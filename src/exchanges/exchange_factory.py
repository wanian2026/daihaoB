from typing import Dict
from .base_exchange import BaseExchange
from .binance_exchange import BinanceExchange
from .okx_exchange import OKXExchange

class ExchangeFactory:
    """交易所工厂类"""

    @staticmethod
    def create_exchange(exchange_name: str, api_key: str, secret: str, 
                       passphrase: str = None, sandbox: bool = False) -> BaseExchange:
        """
        创建交易所实例
        :param exchange_name: 交易所名称 (binance/okx)
        :param api_key: API密钥
        :param secret: API密钥
        :param passphrase: OKX需要的passphrase
        :param sandbox: 是否使用沙盒环境
        :return: 交易所实例
        """
        exchange_name = exchange_name.lower()
        
        if exchange_name == 'binance':
            return BinanceExchange(api_key, secret, None, sandbox)
        elif exchange_name == 'okx':
            return OKXExchange(api_key, secret, passphrase, sandbox)
        else:
            raise ValueError(f"不支持的交易所: {exchange_name}")
