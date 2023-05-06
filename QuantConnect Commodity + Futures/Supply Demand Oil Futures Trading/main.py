# region imports
from AlgorithmImports import *

from universe import FrontMonthFutureUniverseSelectionModel
from alpha import OilFuturesAlphaModel
# endregion

class CreativeOrangeBull(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2019, 1, 1)
        self.SetCash(1_000_0000)
        
        self.UniverseSettings.ExtendedMarketHours = True

        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)

        self.AddUniverseSelection(FrontMonthFutureUniverseSelectionModel())

        self.AddAlpha(OilFuturesAlphaModel(self))

        self.Settings.RebalancePortfolioOnSecurityChanges = False
        self.SetPortfolioConstruction(InsightWeightingPortfolioConstructionModel(lambda time: None))

        self.AddRiskManagement(NullRiskManagementModel())

        self.SetExecution(ImmediateExecutionModel()) 
