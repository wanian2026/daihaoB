import ccxt
from typing import Dict, List
from .base_exchange import BaseExchange, OrderResult, Ticker

class OKXExchange(BaseExchange):
    """欧易交易所实现"""

    def __init__(self, api_key: str, secret: str, passphrase: str = None, sandbox: bool = False):
        super().__init__(api_key, secret, passphrase, sandbox)
        self.exchange = ccxt.okx({
            'apiKey': api_key,
            'secret': secret,
            'password': passphrase,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap'
            }
        })
        if sandbox:
            self.exchange.set_sandbox_mode(True)

    def get_exchange_name(self) -> str:
        return "okx"

    def get_ticker(self, symbol: str) -> Ticker:
        """获取当前价格"""
        ticker = self.exchange.fetch_ticker(symbol)
        return Ticker(
            symbol=symbol,
            price=ticker['last'],
            timestamp=ticker['timestamp']
        )

    def get_balance(self) -> Dict:
        """获取账户余额"""
        balance = self.exchange.fetch_balance()
        return balance

    def create_order(self, symbol: str, side: str, order_type: str, 
                     quantity: float, price: float = None) -> OrderResult:
        """创建订单"""
        if order_type == 'market':
            order = self.exchange.create_market_order(symbol, side, quantity)
        elif order_type == 'limit':
            order = self.exchange.create_limit_order(symbol, side, quantity, price)
        else:
            raise ValueError(f"不支持的订单类型: {order_type}")

        return OrderResult(
            order_id=order['id'],
            price=float(order['price']) if order['price'] else order['average'] or 0,
            quantity=float(order['filled']),
            side=side,
            status=order['status']
        )

    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """取消订单"""
        try:
            self.exchange.cancel_order(order_id, symbol)
            return True
        except Exception as e:
            print(f"取消订单失败: {e}")
            return False

    def get_open_orders(self, symbol: str) -> List[Dict]:
        """获取未成交订单"""
        return self.exchange.fetch_open_orders(symbol)

    def get_position(self, symbol: str) -> Dict:
        """获取持仓信息"""
        try:
            positions = self.exchange.fetch_positions([symbol])
            result = {}
            for pos in positions:
                if float(pos['contracts']) > 0:
                    result[pos['side']] = {
                        'symbol': pos['symbol'],
                        'side': pos['side'],
                        'size': float(pos['contracts']),
                        'entry_price': float(pos['entryPrice']),
                        'unrealized_pnl': float(pos['unrealizedPnl'])
                    }
            return result
        except Exception as e:
            print(f"获取持仓失败: {e}")
            return {}

    def close_position(self, symbol: str, side: str, quantity: float) -> OrderResult:
        """平仓"""
        close_side = 'sell' if side == 'long' else 'buy'
        order = self.exchange.create_market_order(symbol, close_side, quantity)
        return OrderResult(
            order_id=order['id'],
            price=float(order['average']) if order['average'] else 0,
            quantity=float(order['filled']),
            side=close_side,
            status=order['status']
        )
