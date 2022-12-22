from AlgorithmImports import *

### <summary>
### This example demonstrates how to add options for a given underlying equity security.
### It also shows how you can prefilter contracts easily based on strikes and expirations, and how you
### can inspect the option chain to pick a specific option contract to trade.
### </summary>
### <meta name="tag" content="using data" />
### <meta name="tag" content="options" />
### <meta name="tag" content="filter selection" />
class BasicTemplateOptionsAlgorithm(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2015, 12, 24)
        self.SetEndDate(2015, 12, 24)
        self.SetCash(1000000)

        # Add equity
        equity = self.AddEquity("MSFT", Resolution.Minute)

        # Add option
        option = self.AddOption("MSFT")
        self.option_symbol = option.Symbol

        # set our strike/expiry filter for this option chain
        option.SetFilter(-3, +3, 0, 31)

        # use the underlying equity as the benchmark
        self.SetBenchmark(equity.Symbol)

    def OnData(self,slice):
        if self.Portfolio.Invested or not self.IsMarketOpen(self.option_symbol): return

        chain = slice.OptionChains.GetValue(self.option_symbol)
        if chain is None:
            return

        # we sort the contracts to find at the money (ATM) contract with farthest expiration
        contracts = sorted(sorted(sorted(chain, \
            key = lambda x: abs(chain.Underlying.Price - x.Strike)), \
            key = lambda x: x.Expiry, reverse=True), \
            key = lambda x: x.Right, reverse=True)

        # if found, trade it
        if len(contracts) == 0: return
        symbol = contracts[0].Symbol
        self.MarketOrder(symbol, 1)
        self.MarketOnCloseOrder(symbol, -1)

    def OnOrderEvent(self, orderEvent):
        self.Log(str(orderEvent))
