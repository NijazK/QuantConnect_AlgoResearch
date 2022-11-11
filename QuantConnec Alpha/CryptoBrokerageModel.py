class MyBrokerageModel(DefaultBrokerageModel):
    DefaultMarkets = {}
    RequiredFreeBuyingPowerPercent = 0

    def __init__(self, accountType = AccountType.Margin: AccountType):
        self.AccountType = accountType
        self.ShortableProvider = NullShortableProvider()
    
    def CanSubmitOrder(self, security: Security, order: Order,
         message: BrokerageMessageEvent) -> bool:
        return super().CanSubmitOrder(security, order, message)

    def CanUpdateOrder(self, security: Security, order: Order,
         request: UpdateOrderRequest, message: BrokerageMessageEvent) -> bool:
        return super().CanUpdateOrder(security, order, message)

    def CanExecuteOrder(self, security: Security, order: Order) -> bool:
        return super().CanExecuteOrder(security, order)

    def ApplySplit(self, tickets: list[OrderTicket], split: Split) -> None:
        super().ApplySplit(tickets, split)

    def GetLeverage(self, security: Security) -> float:
        return super().GetLeverage(security)

    def GetBenchmark(self, securities: SecurityManager) -> IBenchmark:
        return super().GetBenchmark(securities)

    def GetFillModel(self, security: Security) -> IFillModel:
        return super().GetFillModel(security)

    def GetFeeModel(self, security: Security) -> IFeeModel:
        return super().GetFeeModel(security)

    def GetSlippageModel(self, security: Security) -> ISlippageModel:
        return super().GetSlippageModel(security)

    def GetSettlementModel(self, security: Security) -> ISettlementModel:
        return super().GetSettlementModel(security)

    def GetBuyingPowerModel(self, security: Security) -> IBuyingPowerModel:
        return super().GetBuyingPowerModel(security)

    def GetShortableProvider(self) -> IShortableProvider:
        return self.ShortableProvider
