"""
欧易交易所实现（使用公开API）
"""
from typing import List, Dict, Optional
import ccxt
from .base import BaseExchange


class OKXExchange(BaseExchange):
    """欧易交易所"""

    def __init__(self, api_key: str = "", secret: str = "", testnet: bool = False, password: Optional[str] = None):
        super().__init__(api_key, secret, testnet, password)

    def connect(self):
        """连接欧易（使用公开API）"""
        # 欧易公开API，不需要API密钥
        self.exchange = ccxt.okx({
            'enableRateLimit': True,
        })

        # 加载市场数据
        self.exchange.load_markets()

    def get_futures_symbols(self) -> List[str]:
        """获取欧易合约交易对"""
        symbols = []
        for symbol, market in self.exchange.markets.items():
            if market.get('type') == 'swap' and market.get('quote') == 'USDT':
                # 排除某些交易对
                if not any(x in symbol for x in ['BULL', 'BEAR', 'UP', 'DOWN']):
                    symbols.append(symbol)
        return sorted(symbols)

    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> List:
        """获取K线数据"""
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        return ohlcv

    def get_current_price(self, symbol: str) -> float:
        """获取当前价格"""
        ticker = self.exchange.fetch_ticker(symbol)
        return ticker['last']

    def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """获取订单簿"""
        orderbook = self.exchange.fetch_order_book(symbol, limit=limit)
        return orderbook

    def get_24h_ticker(self, symbol: str) -> Dict:
        """获取24小时行情"""
        ticker = self.exchange.fetch_ticker(symbol)
        return {
            'volume': ticker.get('quoteVolume', 0),
            'change': ticker.get('percentage', 0),
            'high': ticker.get('high', 0),
            'low': ticker.get('low', 0),
        }
