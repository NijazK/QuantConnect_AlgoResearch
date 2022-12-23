from AlgorithmImports import *

### <summary>
### This example demonstrates how to add futures with daily resolution.
### </summary>
### <meta name="tag" content="using data" />
### <meta name="tag" content="benchmarks" />
### <meta name="tag" content="futures" />
class BasicTemplateFuturesDailyAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2015, 10, 8)
        self.SetEndDate(2022, 10, 10)
        self.SetCash(10000000)

        resolution = self.GetResolution()
        extendedMarketHours = self.GetExtendedMarketHours()

        # Subscribe and set our expiry filter for the futures chain
        self.futureSP500 = self.AddFuture(Futures.Indices.SP500EMini, resolution, extendedMarketHours=extendedMarketHours)
        self.futureGold = self.AddFuture(Futures.Metals.Gold, resolution, extendedMarketHours=extendedMarketHours)
        self.futureSilver = self.AddFuture(Futures.Metals.Silver, resolution, extendedMarketHours=extendedMarketHours)

        # set our expiry filter for this futures chain
        # SetFilter method accepts timedelta objects or integer for days.
        # The following statements yield the same filtering criteria
        self.futureSP500.SetFilter(timedelta(0), timedelta(182))
        self.futureGold.SetFilter(timedelta(0), timedelta(182))
        self.futureSilver.SetFilter(timedelta(0), timedelta(182))

    def OnData(self,slice):
        if not self.Portfolio.Invested:
            for chain in slice.FutureChains:
                 
                # Get contracts expiring no earlier than in 90 days
                contracts = list(filter(lambda x: x.Expiry > self.Time + timedelta(90), chain.Value))

                # if there is any contract, trade the front contract
                if len(contracts) == 0: continue
                contract = sorted(contracts, key = lambda x: x.Expiry)[0]

                # if found, trade it.
                # Also check if exchange is open for regular or extended hours. Since daily data comes at 8PM, this allows us prevent the
                # algorithm from trading on friday when there is not after-market.
                if self.Securities[contract.Symbol].Exchange.Hours.IsOpen(self.Time, True):
                    self.MarketOrder(contract.Symbol, 1)
        
        # Same as above, check for cases like trading on a friday night.
        elif all(x.Exchange.Hours.IsOpen(self.Time, True) for x in self.Securities.Values if x.Invested):
            self.Liquidate()

    def GetResolution(self):
        return Resolution.Daily

    def GetExtendedMarketHours(self):
        return False
