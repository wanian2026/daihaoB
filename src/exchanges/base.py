"""
交易所基础类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import ccxt


class BaseExchange(ABC):
    """交易所基础接口"""

    def __init__(self, api_key: str, secret: str, testnet: bool = True, password: Optional[str] = None):
        self.api_key = api_key
        self.secret = secret
        self.testnet = testnet
        self.password = password
        self.exchange = None

    @abstractmethod
    def connect(self):
        """连接交易所"""
        pass

    @abstractmethod
    def get_futures_symbols(self) -> List[str]:
        """获取所有合约交易对"""
        pass

    @abstractmethod
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> List:
        """获取K线数据"""
        pass

    @abstractmethod
    def get_current_price(self, symbol: str) -> float:
        """获取当前价格"""
        pass

    @abstractmethod
    def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """获取订单簿"""
        pass

    @abstractmethod
    def get_24h_ticker(self, symbol: str) -> Dict:
        """获取24小时行情"""
        pass

    def fetch_all_contracts(self) -> List[Dict]:
        """获取所有合约信息"""
        symbols = self.get_futures_symbols()
        contracts = []

        for symbol in symbols:
            try:
                ticker = self.get_24h_ticker(symbol)
                price = self.get_current_price(symbol)
                orderbook = self.get_order_book(symbol, limit=20)

                contracts.append({
                    'symbol': symbol,
                    'price': price,
                    'volume_24h': ticker.get('volume', 0),
                    'change_24h': ticker.get('change', 0),
                    'orderbook': orderbook
                })
            except Exception as e:
                print(f"获取 {symbol} 数据失败: {e}")
                continue

        return contracts
