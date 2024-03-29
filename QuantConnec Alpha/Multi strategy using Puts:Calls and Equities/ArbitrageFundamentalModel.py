from AlgorithmImports import *
from Selection.FundamentalUniverseSelectionModel import FundamentalUniverseSelectionModel

from math import ceil
from itertools import chain

class FundamentalArbitrageFormulaAlpha(QCAlgorithm):

    def Initialize(self):

        self.SetStartDate(2018, 1, 1)
        self.SetCash(10000000)

        #Set zero transaction fees
        self.SetSecurityInitializer(lambda security: security.SetFeeModel(ConstantFeeModel(0)))

        # select stocks using MagicFormulaUniverseSelectionModel
        self.SetUniverseSelection(FundamentalArbitrageUniverseSelectionModel())

        # Use MagicFormulaAlphaModel to establish insights
        self.SetAlpha(RateOfChangeAlphaModel())

        # Equally weigh securities in portfolio, based on insights
        self.SetPortfolioConstruction(EqualWeightingPortfolioConstructionModel())

        ## Set Immediate Execution Model
        self.SetExecution(ImmediateExecutionModel())

        ## Set Null Risk Management Model
        self.SetRiskManagement(NullRiskManagementModel())

class RateOfChangeAlphaModel(AlphaModel):

    '''Uses Rate of Change (ROC) to create magnitude prediction for insights.'''

    def __init__(self, *args, **kwargs):
        self.lookback = kwargs.get('lookback', 1)
        self.resolution = kwargs.get('resolution', Resolution.Daily)
        self.predictionInterval = Time.Multiply(Extensions.ToTimeSpan(self.resolution), self.lookback)
        self.symbolDataBySymbol = {}

    def Update(self, algorithm, data):
        insights = []
        for symbol, symbolData in self.symbolDataBySymbol.items():
            if symbolData.CanEmit:
                insights.append(Insight.Price(symbol, self.predictionInterval, InsightDirection.Up, symbolData.Return, None))
        return insights

    def OnSecuritiesChanged(self, algorithm, changes):

        # clean up data for removed securities
        for removed in changes.RemovedSecurities:
            symbolData = self.symbolDataBySymbol.pop(removed.Symbol, None)
            if symbolData is not None:
                symbolData.RemoveConsolidators(algorithm)

        # initialize data for added securities
        symbols = [ x.Symbol for x in changes.AddedSecurities
            if x.Symbol not in self.symbolDataBySymbol]

        history = algorithm.History(symbols, self.lookback, self.resolution)
        if history.empty: return

        for symbol in symbols:
            symbolData = SymbolData(algorithm, symbol, self.lookback, self.resolution)
            self.symbolDataBySymbol[symbol] = symbolData
            symbolData.WarmUpIndicators(history.loc[symbol])

class SymbolData:

    '''Contains data specific to a symbol required by this model'''
    def __init__(self, algorithm, symbol, lookback, resolution):
        self.previous = 0
        self.symbol = symbol
        self.ROC = RateOfChange(f'{symbol}.ROC({lookback})', lookback)
        self.consolidator = algorithm.ResolveConsolidator(symbol, resolution)
        algorithm.RegisterIndicator(symbol, self.ROC, self.consolidator)

    def RemoveConsolidators(self, algorithm):
        algorithm.SubscriptionManager.RemoveConsolidator(self.symbol, self.consolidator)

    def WarmUpIndicators(self, history):
        for tuple in history.itertuples():
            self.ROC.Update(tuple.Index, tuple.close)

    @property
    def Return(self):
        return self.ROC.Current.Value

    @property
    def CanEmit(self):
        if self.previous == self.ROC.Samples:
            return False

        self.previous = self.ROC.Samples
        return self.ROC.IsReady

    def __str__(self, **kwargs):
        return f'{self.ROC.Name}: {(1 + self.Return)**252 - 1:.2%}'


class FundamentalArbitrageUniverseSelectionModel(FundamentalUniverseSelectionModel):
    
    def __init__(self,
                 filterFineData = True,
                 universeSettings = None):
        '''Initializes a new default instance of the MagicFormulaUniverseSelectionModel'''
        super().__init__(filterFineData, universeSettings)

        # Number of stocks in Coarse Universe
        self.NumberOfSymbolsCoarse = 1000
        # Number of sorted stocks in the fine selection subset using the valuation ratio, EV to EBITDA (EV/EBITDA)
        self.NumberOfSymbolsFine = 200
        # Final number of stocks in security list, after sorted by the valuation ratio, Return on Assets (ROA)
        # WARNING: Higher number of symbols for portfolio will increase Maximum Drawdown.
        self.NumberOfSymbolsInPortfolio = 100

        self.lastMonth = -1
        self.dollarVolumeBySymbol = {}
    
    def SelectCoarse(self, algorithm, coarse):
        '''Performs coarse selection for constituents.
        The stocks must have fundamental data'''
        month = algorithm.Time.month
        if month == self.lastMonth:
            return Universe.Unchanged
        self.lastMonth = month

        # sort the stocks by dollar volume and take the top 1000
        top = sorted([x for x in coarse if x.HasFundamentalData],
                    key=lambda x: x.DollarVolume, reverse=True)[:self.NumberOfSymbolsCoarse]

        self.dollarVolumeBySymbol = { i.Symbol: i.DollarVolume for i in top }

        return list(self.dollarVolumeBySymbol.keys())
    
    def SelectFine(self, algorithm, fine):

        '''Arbitrage Fundamentals: Rank stocks by Enterprise Value to EBITDA (EV/EBITDA)
        Rank subset of previously ranked stocks (EV/EBITDA), using the valuation ratio Return on Assets (ROA)'''

        # QC500:
        ## The company's headquarter must in the U.S.
        ## The stock must be traded on either the NYSE or NASDAQ
        ## At least half a year since its initial public offering
        ## The stock's market cap must be greater than 500 million
        filteredFine = [x for x in fine if x.CompanyReference.CountryId == "USA"
                                        and (x.CompanyReference.PrimaryExchangeID == "NYS" or x.CompanyReference.PrimaryExchangeID == "NAS")
                                        and (algorithm.Time - x.SecurityReference.IPODate).days > 180
                                        and x.EarningReports.BasicAverageShares.ThreeMonths * x.EarningReports.BasicEPS.TwelveMonths * x.ValuationRatios.PERatio > 5e8]
        count = len(filteredFine)
        if count == 0: return []

        myDict = dict()
        percent = self.NumberOfSymbolsFine / count

        # select stocks with top dollar volume in every single sector
        for key in ["N", "M", "U", "T", "B", "I"]:
            value = [x for x in filteredFine if x.CompanyReference.IndustryTemplateCode == key]
            value = sorted(value, key=lambda x: self.dollarVolumeBySymbol[x.Symbol], reverse = True)
            myDict[key] = value[:ceil(len(value) * percent)]

        # stocks in QC500 universe
        topFine = chain.from_iterable(myDict.values())

        ## Rank stocks by Enterprise Value to EBITDA (EV/EBITDA)
        ## Rank subset of previously ranked stocks (EV/EBITDA), using the valuation ratio Return on Assets (ROA)
        # sort stocks in the security universe of QC500 based on Enterprise Value to EBITDA valuation ratio
        sortedByEVToEBITDA = sorted(topFine, key=lambda x: x.ValuationRatios.EVToEBITDA , reverse=True)

        # sort subset of stocks that have been sorted by Enterprise Value to EBITDA, based on the valuation ratio Return on Assets (ROA)
        sortedByROA = sorted(sortedByEVToEBITDA[:self.NumberOfSymbolsFine], key=lambda x: x.ValuationRatios.ForwardROA, reverse=False)

        # retrieve list of securites in portfolio
        return [f.Symbol for f in sortedByROA[:self.NumberOfSymbolsInPortfolio]]