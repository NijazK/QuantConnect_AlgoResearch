class BootCampTask(QCAlgorithm):

    def Initialize(self):

        self.SetCash(100000)
        self.SetStartDate(2017, 5, 1)
        self.SetEndDate(2017, 5, 31) 
        self.forex = self.AddForex("EURUSD", Resolution.Hour, Market.Oanda)
        
        #1. Request the OANDA brokerage model
        brokerage = self.SetBrokerageModel(BrokerageName.OandaBrokerage)
        
    def OnData(self, data):
        pass

