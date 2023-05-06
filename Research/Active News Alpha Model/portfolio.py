#region imports
from AlgorithmImports import *
#endregion


class PartitionedPortfolioConstructionModel(PortfolioConstructionModel):
    
    def __init__(self, algorithm, num_partitions):
        self.algorithm = algorithm
        self.NUM_PARTITIONS = num_partitions

    # REQUIRED: Will determine the target percent for each insight
    def DetermineTargetPercent(self, activeInsights: List[Insight]) -> Dict[Insight, float]:        
        target_pct_by_insight = {}
        
        # Sort insights by time they were emmited
        insights_sorted_by_time = sorted(activeInsights, key=lambda x: x.GeneratedTimeUtc)

        # Find target securities and group insights by Symbol
        target_symbols = []
        insight_by_symbol = {}
        for insight in insights_sorted_by_time:
            insight_by_symbol[insight.Symbol] = insight
            if len(target_symbols) < self.NUM_PARTITIONS:
                target_symbols.append(insight.Symbol)

        occupied_portfolio_value = 0
        occupied_partitions = 0
        # Get last insight emmited for each target Symbol
        for symbol, insight in insight_by_symbol.items():
            # Only invest in Symbols in `target_symbols`
            if symbol not in target_symbols:
                target_pct_by_insight[insight] = 0
            else:
                security_holding = self.algorithm.Portfolio[symbol]
                # If we're invested in the security in the proper direction, do nothing
                if security_holding.IsShort and insight.Direction == InsightDirection.Down \
                    or security_holding.IsLong and insight.Direction == InsightDirection.Up:
                    occupied_portfolio_value += security_holding.AbsoluteHoldingsValue
                    occupied_partitions += 1
                    continue

                # If currently invested and there but the insight direction has changed, 
                #  change portfolio weight of security and reset set partition size
                if security_holding.IsShort and insight.Direction == InsightDirection.Up \
                    or security_holding.IsLong and insight.Direction == InsightDirection.Down:
                    target_pct_by_insight[insight] = int(insight.Direction)

                # If not currently invested, set portfolio weight of security with partition size
                if not security_holding.Invested:
                    target_pct_by_insight[insight] = int(insight.Direction)

        # Scale down target percentages to respect partitions (account for liquidations from insight expiry + universe removals)
        total_portfolio_value = self.algorithm.Portfolio.TotalPortfolioValue
        free_portfolio_pct = (total_portfolio_value - occupied_portfolio_value) / total_portfolio_value
        vacant_partitions = self.NUM_PARTITIONS - occupied_partitions
        scaling_factor = free_portfolio_pct / vacant_partitions if vacant_partitions != 0 else 0
        for insight, target_pct in target_pct_by_insight.items():
            target_pct_by_insight[insight] = target_pct * scaling_factor

        return target_pct_by_insight

    # Determines if the portfolio should be rebalanced base on the provided rebalancing func
    def IsRebalanceDue(self, insights: List[Insight], algorithmUtc: datetime) -> bool:
        # Rebalance when any of the following cases are true:
        #  Case 1: A security we're invested in was removed from the universe
        #  Case 2: The latest insight for a Symbol we're invested in has expired
        #  Case 3: The insight direction for a security we're invested in has changed
        #  Case 4: There is an insight for a security we're not currently invested in AND there is an available parition in the portfolio

        last_active_insights = self.GetTargetInsights() # Warning: This assumes that all insights have the same duration
        insight_symbols = [insight.Symbol for insight in last_active_insights]
        num_investments = 0
        for symbol, security_holding in self.algorithm.Portfolio.items():
            if not security_holding.Invested:
                continue
            num_investments += 1
            #  Case 1: A security we're invested in was removed from the universe
            #  Case 2: The latest insight for a Symbol we're invested in has expired
            if symbol not in insight_symbols:
                return True
        
        for insight in last_active_insights:
            security_holding = self.algorithm.Portfolio[insight.Symbol]
            #  Case 3: The insight direction for a security we're invested in has changed
            if security_holding.IsShort and insight.Direction == InsightDirection.Up \
                or security_holding.IsLong and insight.Direction == InsightDirection.Down:
                return True

            #  Case 4: There is an insight for a security we're not currently invested in AND there is an available parition in the portfolio
            if not security_holding.Invested and num_investments < self.NUM_PARTITIONS:
                return True

        return False
