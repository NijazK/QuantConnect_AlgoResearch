from AlgorithmImports import *
from Portfolio.MeanVarianceOptimizationPortfolioConstructionModel import *

### <summary>
### Mean Variance Optimization algorithm
### Uses the HistoricalReturnsAlphaModel and the MeanVarianceOptimizationPortfolioConstructionModel
### to create an algorithm that rebalances the portfolio according to modern portfolio theory
### </summary>
### <meta name="tag" content="using data" />
### <meta name="tag" content="using quantconnect" />
### <meta name="tag" content="trading and orders" />
class MeanVarianceOptimizationFrameworkAlgorithm(QCAlgorithm):
    '''Mean Variance Optimization algorithm.'''

    def Initialize(self):

        # Set requested data resolution
        self.UniverseSettings.Resolution = Resolution.Minute

        self.Settings.RebalancePortfolioOnInsightChanges = False

        self.SetStartDate(2020,1,1)   #Set Start Date
        self.SetEndDate(2020,2, 20)    #Set End Date
        self.SetCash(10000000)        #Set Strategy Cash

        # set algorithm framework models
        self.SetUniverseSelection(FineFundamentalUniverseSelectionModel(self.SelectCoarse, self.SelectFine))
        self.SetAlpha(HistoricalReturnsAlphaModel(resolution = Resolution.Daily))
        self.SetPortfolioConstruction(MeanVarianceOptimizationPortfolioConstructionModel())
        self.SetExecution(ImmediateExecutionModel())
        self.SetRiskManagement(NullRiskManagementModel())


    def OnOrderEvent(self,  orderEvent):
        if orderEvent.Status == OrderStatus.Filled:
            self.Log(str(orderEvent))

    def SelectCoarse(self, coarse):
        # Template for basket of stocks. if no fundamental analysis available, buy SPY
        tickers = ["GOOGL", "MSTR", "IBM"] if self.Time.date() < date(2020, 2, 15) else ["SPY"]
        return [Symbol.Create(x, SecurityType.Equity, Market.USA) for x in tickers]

    def SelectFine(self, fine):
        return [f.Symbol for f in fine]