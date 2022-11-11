from datetime import datetime
from QuantConnect.Data.UniverseSelection import *
from Selection.FundamentalUniverseSelectionModel import FundamentalUniverseSelectionModel

class LiquidValueStocks(QCAlgorithm):

    def initialize(self):
        self.SetStartDate(2016, 10, 1)
        self.SetEndDate(2017, 10, 1)
        self.SetCash(100000)
        self.AddAlpha(NullAlphaModel())

        self.SetUniverseSelection(LiquidValueUniverseSelectionModel())
        self.UniverseSettings.Resolution = Resolution.Hour

        self.setAlpha(LongShortEYAlphaModel())

        self.SetPortfolioConstruction(EqualWeghtingPortfolioConstruct())
        self.SetExecution(ImmediateExecutionModel())

class LiquidValueUniverseSelectionModel(FundamentalUniverseSelectionModel):

    def __init__(self):
        super().__init__(True, None, None)
        self.lastMonth = -1

    def selectCoarse(self, algorithm, coarse):

        if self.lastMonth == algorithm.Time.month:
            return Universe.Unchanged
        self.lastMonth = algorithm.Time.month

        sortedByDollarVolume = sorted([x for x in coarse if x.HasFundamentalData],
                                    key=lambda x: x.DollarVolume, reverse=True)
        return [x.symbol for x in sortedByDollarVolum[:100]]

    def SelectFine(self, algorithm, fine):

        # Sort yields per share
        sortedByYields = sorted(fine, key=lambda f: f.ValuationRatios.EarningYield, reverse=True)


        self.universe = sortedByYields[:10] + sortedByYields[-10:]

        return [f.symbol for f in self.universe]

class LongShortEYAlphaModel(AlphaModel):

    def __init__(self):

        self.lastMonth = -1


    def update(self, algorithm, data):
            insights = []
            
            if self.lastMonth == algorithm.Time.month:
                return insights
            self.lastMonth = algorithm.Time.month
            
            for security in algorithm.ActiveSecurities.Values:
                direction = 1 if security.Fundamentals.ValuationRatios.EarningYield > 0 else -1
                
                insights.append(Insight.Price(security.Symbol, timedelta(28), direction))
                
                return insights
