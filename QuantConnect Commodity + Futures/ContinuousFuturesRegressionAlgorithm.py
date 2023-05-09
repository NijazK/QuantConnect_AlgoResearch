from AlgorithmImports import *

### <summary>
### Continuous Futures Regression algorithm. Asserting and showcasing the behavior of adding a continuous future
### Lower risk by continuously buying futures contracts (Note: Long positions for calls only)
### </summary>
class ContinuousFuturesRegressionAlgorithm(QCAlgorithm):
    '''Basic template algorithm simply initializes the date range and cash'''

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''

        self.SetStartDate(2013, 7, 1)
        self.SetEndDate(2014, 1, 1)

        self._mappings = []
        self._lastDateLog = -1
        self._continuousContract = self.AddFuture(Futures.Indices.SP500EMini,
                                                  dataNormalizationMode = DataNormalizationMode.BackwardsRatio,
                                                  dataMappingMode = DataMappingMode.LastTradingDay,
                                                  contractDepthOffset= 0)
        self._currentMappedSymbol = self._continuousContract.Symbol

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.

        Arguments:
            data: Slice object keyed by symbol containing the stock data
        '''
        currentlyMappedSecurity = self.Securities[self._continuousContract.Mapped]
        if len(data.Keys) != 1:
            raise ValueError(f"We are getting data for more than one symbols! {','.join(data.Keys)}")

        for changedEvent in data.SymbolChangedEvents.Values:
            if changedEvent.Symbol == self._continuousContract.Symbol:
                self._mappings.append(changedEvent)
                self.Log(f"SymbolChanged event: {changedEvent}")

                if self._currentMappedSymbol == self._continuousContract.Mapped:
                    raise ValueError(f"Continuous contract current symbol did not change! {self._continuousContract.Mapped}")

        if self._lastDateLog != self.Time.month and currentlyMappedSecurity.HasData:
            self._lastDateLog = self.Time.month

            self.Log(f"{self.Time}- {currentlyMappedSecurity.GetLastData()}")
            if self.Portfolio.Invested:
                self.Liquidate()
            else:
                # This works because we set this contract as tradable, even if it's a canonical security
                self.Buy(currentlyMappedSecurity.Symbol, 1)

            if self.Time.month == 1 and self.Time.year == 2013:
                response = self.History( [ self._continuousContract.Symbol ], 60 * 24 * 90)
                if response.empty:
                    raise ValueError("Unexpected empty history response")

        self._currentMappedSymbol = self._continuousContract.Mapped

    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status == OrderStatus.Filled:
            self.Debug("Purchased Stock: {0}".format(orderEvent.Symbol))

    def OnSecuritiesChanged(self, changes):
        self.Debug(f"{self.Time}-{changes}")

    def OnEndOfAlgorithm(self):
        expectedMappingCounts = 2
        if len(self._mappings) != expectedMappingCounts:
            raise ValueError(f"Unexpected symbol changed events: {self._mappings.count()}, was expecting {expectedMappingCounts}")
