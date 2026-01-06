"""
模拟交易所（用于测试和演示）
"""
from typing import List, Dict, Optional
import random
from .base import BaseExchange


class MockExchange(BaseExchange):
    """模拟交易所 - 返回测试数据"""

    def __init__(self, api_key: str = "", secret: str = "", testnet: bool = False, password: Optional[str] = None):
        super().__init__(api_key, secret, testnet, password)
        self.exchange = None  # 不使用真实的ccxt交易所

    def connect(self):
        """连接（不需要真实连接）"""
        pass

    def get_futures_symbols(self) -> List[str]:
        """获取模拟交易对列表"""
        return [
            'BTC/USDT',
            'ETH/USDT',
            'BNB/USDT',
            'SOL/USDT',
            'XRP/USDT',
            'ADA/USDT',
            'DOGE/USDT',
            'MATIC/USDT',
            'DOT/USDT',
            'LTC/USDT',
            'AVAX/USDT',
            'LINK/USDT',
            'ATOM/USDT',
            'UNI/USDT',
        ]

    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> List:
        """获取模拟K线数据"""
        import time

        # 生成模拟K线数据
        ohlcv = []
        base_price = self._get_base_price(symbol)
        current_time = int(time.time() * 1000)
        time_interval = self._get_timeframe_ms(timeframe)

        # 生成limit个K线
        for i in range(limit):
            timestamp = current_time - (limit - i - 1) * time_interval
            close = base_price + random.uniform(-0.05, 0.05) * base_price
            high = close + random.uniform(0, 0.02) * close
            low = close - random.uniform(0, 0.02) * close
            open_ = low + random.uniform(0, 1) * (high - low)
            volume = random.uniform(100, 10000)

            ohlcv.append([timestamp, open_, high, low, close, volume])

        return ohlcv

    def get_current_price(self, symbol: str) -> float:
        """获取模拟当前价格"""
        return self._get_base_price(symbol) + random.uniform(-0.01, 0.01) * self._get_base_price(symbol)

    def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """获取模拟订单簿"""
        base_price = self._get_base_price(symbol)

        # 生成模拟买单
        bids = []
        for i in range(limit):
            price = base_price * (1 - 0.001 * (i + 1))
            size = random.uniform(10, 1000)
            bids.append([price, size])

        # 生成模拟卖单
        asks = []
        for i in range(limit):
            price = base_price * (1 + 0.001 * (i + 1))
            size = random.uniform(10, 1000)
            asks.append([price, size])

        return {
            'bids': bids,
            'asks': asks,
            'timestamp': int(__import__('time').time() * 1000)
        }

    def get_24h_ticker(self, symbol: str) -> Dict:
        """获取模拟24小时行情"""
        base_price = self._get_base_price(symbol)
        change = random.uniform(-5, 5)

        return {
            'volume': random.uniform(1000000, 10000000),
            'change': change,
            'high': base_price * (1 + abs(change) / 100),
            'low': base_price * (1 - abs(change) / 100),
        }

    def _get_base_price(self, symbol: str) -> float:
        """获取基础价格"""
        prices = {
            'BTC/USDT': 95000,
            'ETH/USDT': 3500,
            'BNB/USDT': 650,
            'SOL/USDT': 180,
            'XRP/USDT': 2.3,
            'ADA/USDT': 1.1,
            'DOGE/USDT': 0.35,
            'MATIC/USDT': 0.9,
            'DOT/USDT': 7.5,
            'LTC/USDT': 85,
            'AVAX/USDT': 42,
            'LINK/USDT': 18,
            'ATOM/USDT': 9.5,
            'UNI/USDT': 14,
        }
        return prices.get(symbol, 100)

    def _get_timeframe_ms(self, timeframe: str) -> int:
        """获取时间间隔（毫秒）"""
        timeframe_map = {
            '1m': 60 * 1000,
            '5m': 5 * 60 * 1000,
            '15m': 15 * 60 * 1000,
            '30m': 30 * 60 * 1000,
            '1h': 60 * 60 * 1000,
            '4h': 4 * 60 * 60 * 1000,
            '1d': 24 * 60 * 60 * 1000,
            '1w': 7 * 24 * 60 * 60 * 1000,
        }
        return timeframe_map.get(timeframe, 60 * 60 * 1000)
