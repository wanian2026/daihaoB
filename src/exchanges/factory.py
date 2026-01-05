"""
交易所工厂类
"""
from typing import Optional
from .binance import BinanceExchange
from .okx import OKXExchange


class ExchangeFactory:
    """交易所工厂"""

    @staticmethod
    def create_exchange(exchange_name: str, api_key: str, secret: str,
                       testnet: bool = True, password: Optional[str] = None):
        """
        创建交易所实例

        Args:
            exchange_name: 交易所名称 (binance, okx)
            api_key: API密钥
            secret: 密钥
            testnet: 是否测试网
            password: 密码（OKX需要）

        Returns:
            交易所实例
        """
        exchange_name = exchange_name.lower()

        if exchange_name == 'binance':
            exchange = BinanceExchange(api_key, secret, testnet, password)
        elif exchange_name == 'okx':
            if not password:
                raise ValueError("OKX 需要提供 password")
            exchange = OKXExchange(api_key, secret, testnet, password)
        else:
            raise ValueError(f"不支持的交易所: {exchange_name}")

        exchange.connect()
        return exchange
