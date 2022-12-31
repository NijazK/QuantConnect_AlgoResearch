from AlgorithmImports import *

### <summary>
### Universe Selection regression algorithm simulates for Blackrock Advisors, LLC. 
### </summary>
### <meta name="tag" content="regression test" />
class UniverseSelectionRegressionAlgorithm(QCAlgorithm):
    
    def Initialize(self):
        
        self.SetStartDate(2017,3,1)   #Set Start Date
        self.SetEndDate(2022,11,27)      #Set End Date
        self.SetCash(1000000)           #Set Strategy Cash
        # Find more symbols here: http://quantconnect.com/data
        # security that exists with no mappings
        self.AddEquity("IVV", Resolution.Daily)
        # security that doesn't exist until half way in backtest (comes in as IEFA)
        self.AddEquity("IEFA", Resolution.Daily)

        self.UniverseSettings.Resolution = Resolution.Daily
        self.AddUniverse(self.CoarseSelectionFunction)
        
        self.changedSymbols = []
        self.changes = None


    def CoarseSelectionFunction(self, coarse):
        return [ c.Symbol for c in coarse if c.Symbol.Value == "IEFA" or c.Symbol.Value == "IJR" or c.Symbol.Value == "IJH" or c.Symbol.Value == "IEMG" ]


    def OnData(self, data):
        if self.Transactions.OrdersCount == 0:
            self.MarketOrder("IVV", 70)
            self.MarketOrder("IEFA", 30)

        for kvp in data.Delistings:
            self.changedSymbols.append(kvp.Key)
        
        if self.changes is None:
            return

        if not all(data.Bars.ContainsKey(x.Symbol) for x in self.changes.AddedSecurities):
            return 
        
        for security in self.changes.AddedSecurities:
            self.Log("{0}: Added Security: {1}".format(self.Time, security.Symbol))
            self.MarketOnOpenOrder(security.Symbol, 100)

        for security in self.changes.RemovedSecurities:
            self.Log("{0}: Removed Security: {1}".format(self.Time, security.Symbol))
            if security.Symbol not in self.changedSymbols:
                self.Log("Not in delisted: {0}:".format(security.Symbol))
                self.MarketOnOpenOrder(security.Symbol, -100)

        self.changes = None 


    def OnSecuritiesChanged(self, changes):
        self.changes = changes


    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status == OrderStatus.Submitted:
            self.Log("{0}: Submitted: {1}".format(self.Time, self.Transactions.GetOrderById(orderEvent.OrderId)))
        if orderEvent.Status == OrderStatus.Filled:
            self.Log("{0}: Filled: {1}".format(self.Time, self.Transactions.GetOrderById(orderEvent.OrderId)))
