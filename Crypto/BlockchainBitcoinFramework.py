from AlgorithmImports import *
from QuantConnect.DataSource import *

class BlockchainBitcoinMetadataFrameworkAlgorithm(QCAlgorithm):
    
    def Initialize(self) -> None:
        self.SetStartDate(2023, 1, 1)   # Set Start Date
        self.SetCash(10000000)

        self.AddUniverseSelection(
            ManualUniverseSelectionModel(
            Symbol.Create("BTCUSD", SecurityType.Crypto, Market.Bitfinex)
        ))

        self.AddAlpha(BlockchainBitcoinMetadataAlphaModel())
        
        self.SetPortfolioConstruction(EqualWeightingPortfolioConstructionModel())
        
        self.AddRiskManagement(NullRiskManagementModel())
        
        self.SetExecution(ImmediateExecutionModel())
        
class BlockchainBitcoinMetadataAlphaModel(AlphaModel):
    
    def __init__(self) -> None:
        self.bitcoin_metadata_symbol_by_symbol = {}
        self.last_demand_supply = {}

    def Update(self, algorithm:QCAlgorithm, slice: Slice) -> List[Insight]:
        insights = []
        
        ### Retrieving data
        data = slice.Get(BitcoinMetadata)
        
        for symbol, bitcoin_metadata_symbol in self.bitcoin_metadata_symbol_by_symbol.items():
            if data.ContainsKey(bitcoin_metadata_symbol) and data[bitcoin_metadata_symbol] != None:
                current_demand_supply = data[bitcoin_metadata_symbol].NumberofTransactions / data[bitcoin_metadata_symbol].HashRate

                # comparing the transaction-to-hash-rate ratio changes, we will buy bitcoin or hold cash
                if symbol in self.last_demand_supply and current_demand_supply > self.last_demand_supply[symbol]:
                    insights.append(Insight.Price(symbol, timedelta(1), InsightDirection.Up))

                self.last_demand_supply[symbol] = current_demand_supply
                
        return insights

    def OnSecuritiesChanged(self, algorithm: QCAlgorithm, changes: SecurityChanges) -> None:
        for security in changes.AddedSecurities:
            symbol = security.Symbol
            
            ### Requesting data
            bitcoin_metadata_symbol = algorithm.AddData(BitcoinMetadata, symbol).Symbol

            self.bitcoin_metadata_symbol_by_symbol[symbol] = bitcoin_metadata_symbol

            ### Historical data
            history = algorithm.History(BitcoinMetadata, bitcoin_metadata_symbol, 60, Resolution.Daily)
            algorithm.Debug(f"We got {len(history)} items from our history request for {symbol} Blockchain Bitcoin Metadata")
