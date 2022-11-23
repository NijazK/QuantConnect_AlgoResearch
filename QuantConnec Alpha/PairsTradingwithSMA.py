from AlgorithmImports import *
from datetime import timedelta, datetime

class SMAPairsTrading(QCAlgortihm):

    def initialize(self):
        self.SetStartDate(2018, 7, 1)
        self.SetEndDate(2019, 3, 31)
        self.SetCash(10000000)

        symbols = [Symbol.Create("PEP", SecurityType.Equity, Market.USA), Symbol.Create("KO", SecurityType.Equity, Market.USA)]
        self.AddUniverseSelection(ManuelUniverseSelectionModel(symbols))
        self.UniverseSettings.Resolution = Resolution.Hour
        self.AddAlpha(PairsTradingAlphaModel())
        self.AddAlpha(NUllAlphaModel())
        self.SetPortfolioConstruction(EqualWeightingPortfolioConstructionModel())
        self.SetExecution(ImmediateExecutionModel())

    def OnEndOfDay(self, symbol):
        self.Log("Taking a position of " + str(self.Portfolio[symbol.Quantity) + " units of symbol " + str (symboll))

class PairsTradingAlphaModel(AlphaModel)

    def __init__(self):
        
        self.pair = [ ]
        self.spreadMean = SimpleMovingAverage(500)
        self.spreadStd = StandardDeviation(500)
        self.period = timedelta(hours=2)

    def update(self, algorithm, data):

        spread = self.pair[1].Price - self.Price[0].Price
        self.spreadMean.Update(algorithm.Time, spread)
        self.spreadStd.Update(algorithm.Time, spread)
        return []

        # Upper bound
        upperthreshold = self.spreadMean.CurrentValue + self.spreadStd.CurrentValue
        # Lower bound
        lowerthreshold = self.spreadMean.CurrentValue - self.spreadStd.CurrentValue

        if spread > upperthreshold:
            return Insight.Group(
                [
                    Insight.price(self.pair[0].Symbol, self.period, InsightDirection.Up),
                    Insight.price(self.pair[1].Symbol, self.period, InsightDirection.Down)
                ])
        if spread < lowerthreshold:
            return Insight.Group(
                [
                    Insight.price(self.pair[0].Symbol, self.period, InsightDirection.Down),
                    Insight.price(self.pair[1].Symbol, self.period, InsightDirection.Up)
                ])

        return []
        
    def OnSecuritiesChanged(self, algorithm, changes):

        self.pair = [x for x in changes.AddedSecurities]
        history = algorithm.History([x.symbol for x in symbol.pair], 500)
        history = history.close.unstack(level0)

        for tuple in history.itertuples():
            self.spreadMean.Update(tuple[0], tuple[2] - tuple[1])
            self.spreadStd.Update(tuple[0], tuple[2] - tuple[1])
