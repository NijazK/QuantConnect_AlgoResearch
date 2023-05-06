#region imports
from AlgorithmImports import *
#endregion

class NewsSentimentAlphaModel(AlphaModel):

    symbol_data_by_symbol  = {}
    
    # Assign sentiment values to words
    word_scores = {'acceptable': 1, 'approved': 1, 'accepted': 1, 'valid': 1,
                   'rejected': -1, 'incomplete': -1, 'failed': -1, 'postponed': -1}

    def Update(self, algorithm: QCAlgorithm, data: Slice) -> List[Insight]:
        insights = []

        for symbol, symbol_data in self.symbol_data_by_symbol.items():
            if not symbol_data.hours.IsOpen(algorithm.Time + timedelta(minutes=1), extendedMarket=False):
                continue
            if not data.ContainsKey(symbol_data.dataset_symbol):
                continue
            article = data[symbol_data.dataset_symbol]

            # Assign a sentiment score to the article
            title_words = article.Description.lower()
            score = 0
            for word, word_score in self.word_scores.items():
                if word in title_words:
                    score += word_score
                    
            # Only trade when there is positive news
            if score > 0:
                direction = InsightDirection.Up
            elif score < 0:
                direction = InsightDirection.Flat
            else: 
                continue

            # Create insights
            expiry = symbol_data.hours.GetNextMarketClose(algorithm.Time, extendedMarket=False) - timedelta(minutes=1, seconds=1)
            insights.append(Insight.Price(symbol, expiry, direction, None, None, None, 1/len(self.symbol_data_by_symbol)))

        return insights

    def OnSecuritiesChanged(self, algorithm: QCAlgorithm, changes: SecurityChanges) -> None:
        for security in changes.AddedSecurities:
            # Create SymbolData objects for each security in the universe
            self.symbol_data_by_symbol[security.Symbol] = SymbolData(algorithm, security)

        for security in changes.RemovedSecurities:
            # Delete the corresponding SymbolData object when a security leaves the universe
            if security.Symbol in self.symbol_data_by_symbol:
                symbol_data = self.symbol_data_by_symbol.pop(security.Symbol, None)
                if symbol_data:
                    symbol_data.dispose()

class SymbolData:
    def __init__(self, algorithm, security):
        self.algorithm = algorithm
        self.hours = security.Exchange.Hours
        # Subscribe to the Tiingo News Feed for this security
        self.dataset_symbol = algorithm.AddData(TiingoNews, security.Symbol).Symbol
    
    def dispose(self):
        # Unsubscribe from the Tiingo News Feed for this security
        self.RemoveSecurity(self.dataset_symbol)
