from AlgorithmImports import *
from QuantConnect.DataSource import *

class BlockchainBitcoinMetadataAlgorithm(QCAlgorithm):
    
    def Initialize(self) -> None:
        self.SetStartDate(2023, 1, 1)   # Set Start Date
        self.SetCash(10000000)

        self.btcusd = self.AddCrypto("BTCUSD", Resolution.Minute).Symbol
        ### Requesting data
        self.bitcoin_metadata_symbol = self.AddData(BitcoinMetadata, self.btcusd).Symbol

        ### Historical data
        history = self.History(BitcoinMetadata, self.bitcoin_metadata_symbol, 60, Resolution.Daily)
        self.Debug(f"We got {len(history)} items from our history request for {self.btcusd} Blockchain Bitcoin Metadata")

        self.last_demand_supply = None

    def OnData(self, slice: Slice) -> None:
        ### Retrieving data
        data = slice.Get(BitcoinMetadata)
        
        if self.bitcoin_metadata_symbol in data and data[self.bitcoin_metadata_symbol] != None:
            current_demand_supply = data[self.bitcoin_metadata_symbol].NumberofTransactions / data[self.bitcoin_metadata_symbol].HashRate

            # comparing the average transaction-to-hash-rate ratio changes, we will buy bitcoin or hold cash
            if self.last_demand_supply != None and current_demand_supply > self.last_demand_supply:
                self.SetHoldings(self.btcusd, 1)
            else:
                self.SetHoldings(self.btcusd, 0)

            self.last_demand_supply = current_demand_supply
