#region imports
from AlgorithmImports import *

from Selection.FutureUniverseSelectionModel import FutureUniverseSelectionModel
#endregion

class FrontMonthFutureUniverseSelectionModel(FutureUniverseSelectionModel):
    def __init__(self,) -> None:
        super().__init__(timedelta(1), self.select_future_chain_symbols)

    def select_future_chain_symbols(self, utcTime: datetime) -> List[Symbol]:
        return [Symbol.Create(Futures.Energies.CrudeOilWTI, SecurityType.Future, Market.NYMEX)]

    def Filter(self, filter: FutureFilterUniverse) -> FutureFilterUniverse:
        return filter.FrontMonth().OnlyApplyFilterAtMarketOpen()
