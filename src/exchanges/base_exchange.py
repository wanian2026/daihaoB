from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class OrderResult:
    """订单结果"""
    order_id: str
    price: float
    quantity: float
    side: str
    status: str

@dataclass
class Ticker:
    """行情信息"""
    symbol: str
    price: float
    timestamp: int

class BaseExchange(ABC):
    """交易所基础接口抽象类"""

    def __init__(self, api_key: str, secret: str, passphrase: str = None, sandbox: bool = False):
        """
        初始化交易所
        :param api_key: API密钥
        :param secret: API密钥
        :param passphrase: OKX需要的passphrase
        :param sandbox: 是否使用沙盒环境
        """
        self.api_key = api_key
        self.secret = secret
        self.passphrase = passphrase
        self.sandbox = sandbox

    @abstractmethod
    def get_exchange_name(self) -> str:
        """获取交易所名称"""
        pass

    @abstractmethod
    def get_ticker(self, symbol: str) -> Ticker:
        """获取当前价格"""
        pass

    @abstractmethod
    def get_balance(self) -> Dict:
        """获取账户余额"""
        pass

    @abstractmethod
    def create_order(self, symbol: str, side: str, order_type: str, 
                     quantity: float, price: float = None) -> OrderResult:
        """
        创建订单
        :param symbol: 交易对
        :param side: 买卖方向 (buy/sell)
        :param order_type: 订单类型 (market/limit)
        :param quantity: 数量
        :param price: 价格（限价单必填）
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """取消订单"""
        pass

    @abstractmethod
    def get_open_orders(self, symbol: str) -> List[Dict]:
        """获取未成交订单"""
        pass

    @abstractmethod
    def get_position(self, symbol: str) -> Dict:
        """获取持仓信息"""
        pass

    @abstractmethod
    def close_position(self, symbol: str, side: str, quantity: float) -> OrderResult:
        """平仓"""
        pass
