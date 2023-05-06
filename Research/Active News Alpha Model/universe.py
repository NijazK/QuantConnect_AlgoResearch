#region imports
from AlgorithmImports import *
#endregion

class FaangUniverseSelectionModel(ManualUniverseSelectionModel):
    def __init__(self):
        tickers = ["NVS", "AAPL", "BMU", "PFE", "ABBV"]
        self.Count = len(tickers)
        symbols = [Symbol.Create(ticker, SecurityType.Equity, Market.USA) for ticker in tickers]
        super().__init__(symbols)
