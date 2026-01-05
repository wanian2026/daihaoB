"""
交易所工厂类
"""
from typing import Optional
from .binance import BinanceExchange


class ExchangeFactory:
    """交易所工厂"""

    @staticmethod
    def create_exchange(exchange_name: str, api_key: str = "", secret: str = "",
                       testnet: bool = False, password: Optional[str] = None):
        """
        创建交易所实例

        Args:
            exchange_name: 交易所名称 (binance)
            api_key: API密钥（可选，公开API不需要）
            secret: 密钥（可选，公开API不需要）
            testnet: 是否测试网（已废弃，保留参数兼容性）
            password: 密码（已废弃，保留参数兼容性）

        Returns:
            交易所实例
        """
        exchange_name = exchange_name.lower()

        if exchange_name == 'binance':
            exchange = BinanceExchange(api_key, secret, testnet, password)
        else:
            raise ValueError(f"不支持的交易所: {exchange_name}，仅支持 binance")

        exchange.connect()
        return exchange
