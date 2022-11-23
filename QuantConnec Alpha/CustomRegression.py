from AlgorithmImports import *

class CustomAddRemoveRegressionAlgorithm(QCAlgorithm):
    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''
        
        # Set starting date, cash and ending date of the backtest.
        # Set the date to a 5 week interval.
        self.SetStartDate(2020, 10, 7)
        self.SetEndDate(2020, 10, 12)
        self.SetCash(1000000)

        self.SetSecurityInitializer(lambda security: security.SetMarketPrice(self.GetLastKnownPrice(security)))
        
        # Subscribe to data of the selected stocks
        self.symbols = [self.AddEquity(ticker, Resolution.Daily).Symbol for ticker in ["SPY", "SQ", "CRM", "PLTR", "INTC", "AMD", "ASML"]]
        self._lastAction = None
    
    def OnData(self, data):
        if self._lastAction is not None and self._lastAction.date() == self.Time.date():
            return
        
        if not self.Portfolio.Invested:
            self.SetHoldings("SPY", .5)
            self._lastAction = self.Time
        
        if self.Time.weekday() == 1:
            self.AddEquity("SQ")
            self.AddEquity("CRM")
            self.AddEquity("PLTR")
            self._lastAction = self.Time 

        if self.Time.weekday() == 2:
            self.SetHoldings("SQ", .10)
            self.SetHoldings("CRM", .10)
            self.SetHoldings("PLTR", .10)
            self._lastAction = self.Time 
        
        if self.Time.weekday() == 3:
            self.AddEquity("INTC")
            self.AddEquity("AMD")
            self.AddEquity("ASML")
            self._lastAction = self.Time 
        
        if self.Time.weekday() == 4:
            self.SetHoldings("SQ", .10)
            self.SetHoldings("CRM", .10)
            self.SetHoldings("PLTR", .10)
            self._lastAction = self.Time 

        if self.Time.weekday() == 5:
            self.RemoveSecurity("SQ")
            self.RemoveSecurity("CRM")
            self.RemoveSecurity("PLTR")
            self.RemoveSecurity("INTC")
            self.RemoveSecurity("AMD")
            self.RemoveSecurity("ASML")
            self._lastAction = self.Time
        

    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status == OrderStatus.Submitted:
            self.Debug("{0}: Submitted: {1}".format(self.Time, self.Transactions.GetOrderById(orderEvent.OrderId)))
        if orderEvent.Status == OrderStatus.Filled:
            self.Debug("{0}: Filled: {1}".format(self.Time, self.Transactions.GetOrderById(orderEvent.OrderId)))
