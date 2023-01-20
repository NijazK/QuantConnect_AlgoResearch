from AlgorithmImports import *

### <summary>
### This algorithm demonstrates the runtime addition and removal of equities with a quarterly time frame.
### This strategy is implemented with the thought of cyclicals that will mean revert above standard deviation.
### With LEAN it is possible to add and remove securities after the initialization.
### </summary>
### <meta name="tag" content="using data" />
### <meta name="tag" content="assets" />
### <meta name="tag" content="regression test" />
class AddRemoveSecurityRegressionAlgorithm(QCAlgorithm):

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''

        self.SetStartDate(2021,11,1)   #Set Start Date
        self.SetEndDate(2022,1,1)    #Set End Date
        self.SetCash(100000)           #Set Strategy Cash
        # Find more symbols here: http://quantconnect.com/data
        self.AddEquity("NVO")
        self.AddEquity("MSFT")
        self.AddEquity("ABNB")
        self.AddEquity("HSY")

        self._lastAction = None


    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.'''
        if self._lastAction is not None and self._lastAction.date() == self.Time.date():
            return

        if not self.Portfolio.Invested:
            self.SetHoldings("NVO", .02)
            self.SetHoldings("MSFT", .01)
            self.SetHoldings("ABNB", .05)
            self.SetHoldings("HSY", .09)
            self._lastAction = self.Time

        if self.Time.weekday() == 1:
            self.AddEquity("NVO")
            self.AddEquity("MSFT")
            self.AddEquity("ABNB")
            self.AddEquity("HSY")
            self._lastAction = self.Time

        if self.Time.weekday() == 2:
            self.AddEquity("NVO")
            self.AddEquity("MSFT")
            self.AddEquity("ABNB")
            self.AddEquity("HSY")
            self._lastAction = self.Time

        if self.Time.weekday() == 3:
            self.AddEquity("NVO")
            self.AddEquity("MSFT")
            self.AddEquity("ABNB")
            self.AddEquity("HSY")
            self._lastAction = self.Time
        
        if self.Time.weekday() == 12:
            self.RemoveSecurity("NVO")
            self.RemoveSecurity("MSFT")
            self.RemoveSecurity("ABNB")
            self.RemoveSecurity("HSY")
            self._lastAction = self.Time

    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status == OrderStatus.Submitted:
            self.Debug("{0}: Submitted: {1}".format(self.Time, self.Transactions.GetOrderById(orderEvent.OrderId)))
        if orderEvent.Status == OrderStatus.Filled:
            self.Debug("{0}: Filled: {1}".format(self.Time, self.Transactions.GetOrderById(orderEvent.OrderId)))
