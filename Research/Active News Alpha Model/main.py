# region imports
from AlgorithmImports import *

from universe import FaangUniverseSelectionModel
from alpha import NewsSentimentAlphaModel
from portfolio import PartitionedPortfolioConstructionModel
# endregion

class BreakingNewsEventsAlgorithm(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2019, 1, 1)
        self.SetEndDate(2023, 3, 1)
        self.SetCash(1_000_000)
        
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)

        universe = FaangUniverseSelectionModel()
        self.AddUniverseSelection(universe)

        self.AddAlpha(NewsSentimentAlphaModel())

        # We use 5 partitions because the FAANG universe has 5 members.
        # If we change the universe to have, say, 100 securities, then 100 paritions means
        #  that each trade gets a 1% (1/100) allocation instead of a 20% (1/5) allocation.
        self.SetPortfolioConstruction(PartitionedPortfolioConstructionModel(self, universe.Count))

        self.AddRiskManagement(NullRiskManagementModel())

        self.SetExecution(ImmediateExecutionModel()) 
