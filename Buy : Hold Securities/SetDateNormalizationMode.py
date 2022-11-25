class BootCampTask(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2017, 6, 1)
        self.SetEndDate(2017, 6, 15)
        
        #1-2. Change the data normalization mode for SPY and set the leverage for the IWM Equity
        self.spy = self.AddEquity("SPY", Resolution.Daily, dataNormalizationMode=DataNormalizationMode.Raw)
        self.iwm = self.AddEquity("IWM", Resolution.Daily, leverage = 1)
        
    def OnData(self, data):
        pass
    
