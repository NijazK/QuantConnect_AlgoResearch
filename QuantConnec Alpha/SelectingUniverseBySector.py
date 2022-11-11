from datetime import timedelta
from AlgorithmImports import *
from QuantConnect.Data.UniverseSelection import * 
from Selection.FundamentalUniverseSelectionModel import FundamentalUniverseSelectionModel

class SectorBalancedPortfolioConstruction(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2016, 12, 28) 
        self.SetEndDate(2017, 3, 1) 
        self.SetCash(100000) 

        self.UniverseSettings.Resolution = Resolution.Hour
        #1. Set an instance of MyUniverseSelectionModel using self.SetUniverseSelection
        self.SetUniverseSelection(MyUniverseSelectionModel())
        
        self.SetAlpha(ConstantAlphaModel(InsightType.Price, InsightDirection.Up, timedelta(1), 0.025, None))
        self.SetExecution(ImmediateExecutionModel())

class MyUniverseSelectionModel(FundamentalUniverseSelectionModel):

    def __init__(self):
        super().__init__(True, None)

    def SelectCoarse(self, algorithm, coarse):
        filtered = [x for x in coarse if x.HasFundamentalData > 0 and x.Price > 0]
        sortedByDollarVolume = sorted(filtered, key=lambda x: x.DollarVolume, reverse=True)
        return [x.Symbol for x in sortedByDollarVolume][:100]

    def SelectFine(self, algorithm, fine):
        
        #2. Save the top 3 securities sorted by MarketCap for the Technology sector to the variable self.technology
        filtered = [f for f in fine if x\f.AssetClassification.MorningstarSectorCode == MorningstarSectorCode.technology]
        self.technology = sorted(filtered, key=lambda f: f.MarketCap, reverse=True)[:3]
        
        #3. Save the top 2 securities sorted by MarketCap for the Financial Services sector to the variable self.financialServices
        filtered = [f for f in fine if f.AssetClassification.MorningstarSectorCode == MorningstarSectorCode.financialServices
        self.financialServices = sorted(filtered, key=lambda f: f.MarketCap, reverse=True)[:30]
        
        #4. Save the top 1 securities sorted by MarketCap for the Consumer Goods sector to the variable self.consumerDefensive
        filtered = [f for f in fine if x\f.AssetClassification.MorningstarSectorCode == MorningstarSectorCode.consumerDefensive]
        self.consumerDefensive = sorted(filtered, key=lambda f: f.MarketCap, reverse=True)[:30]
        
    return [x.Symbol for x in self.technology + self.financialServices + self.consumerDefensive]
