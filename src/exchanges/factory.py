"""
交易所工厂类
"""
from typing import Optional
from .binance import BinanceExchange
from .okx import OKXExchange


class ExchangeFactory:
    """交易所工厂"""

    @staticmethod
    def create_exchange(exchange_name: str, api_key: str = "", secret: str = "",
                       testnet: bool = False, password: Optional[str] = None):
        """
        创建交易所实例

        Args:
            exchange_name: 交易所名称 (binance, okx)
            api_key: API密钥（可选）
            secret: 密钥（可选）
            testnet: 是否测试网（已废弃，保留参数兼容性）
            password: 密码（OKX需要，但使用公开API时不需要）

        Returns:
            交易所实例
        """
        exchange_name = exchange_name.lower()

        if exchange_name == 'binance':
            exchange = BinanceExchange(api_key, secret, testnet, password)
        elif exchange_name == 'okx':
            exchange = OKXExchange(api_key, secret, testnet, password)
        else:
            raise ValueError(f"不支持的交易所: {exchange_name}")

        exchange.connect()
        return exchange
