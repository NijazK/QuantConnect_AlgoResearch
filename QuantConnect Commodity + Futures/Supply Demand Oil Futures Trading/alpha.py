#region imports
from AlgorithmImports import *
#endregion

# Algorithm framework model that produces insights
class OilFuturesAlphaModel(AlphaModel):

    def __init__(self, algorithm):
        # Subscribe to the oil production dataset
        self.dataset_symbol = algorithm.AddData(USEnergy, USEnergy.Petroleum.UnitedStates.WeeklyFieldProductionOfCrudeOil).Symbol

        # Warm up the oil production data trend history
        self.roc = RateOfChange(1)
        history = algorithm.History[USEnergy](self.dataset_symbol, timedelta(days=30), Resolution.Daily)
        for data_point in history:
            self.roc.Update(data_point.EndTime, data_point.Value)
        
        self.rebalance = True

    def Update(self, algorithm: QCAlgorithm, data: Slice) -> List[Insight]:
        # Get the latest oil production data
        if data.ContainsKey(self.dataset_symbol):
            data_point = data[self.dataset_symbol]
            self.roc.Update(data_point.EndTime, data_point.Value)
            self.rebalance = True

        # Rebalance when we aren't invested (this occurs when the current contract we're holding expires)
        if not algorithm.Portfolio.Invested:
            self.rebalance = True

        # Rebalance when there is new oil production data and there is Futures data in the current slice
        if not self.rebalance or data.FutureChains.Count == 0:
            return []
        self.rebalance = False

        # Law of supply and demand: increasing supply => decreasing price; decreasing supply => increasing price
        # If supply is increasing, sell futures. Otherwise, buy futures.
        direction = InsightDirection.Down if self.roc.Current.Value > 0 else InsightDirection.Up
        for continuous_contract_symbol, chain in data.FuturesChains.items():
            contract = sorted(chain, key=lambda contract: contract.OpenInterest, reverse=True)[0]
            insight = Insight.Price(contract.Symbol, timedelta(30), direction, None, None, None, 0.01)

        return [insight]
