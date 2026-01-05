"""
合约扫描器
扫描所有合约，识别交易机会
"""
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from exchanges import ExchangeFactory
from analysis import SignalGenerator


class ContractScanner:
    """合约扫描器"""

    def __init__(self, exchange_name: str, api_key: str, secret: str,
                 testnet: bool = True, password: Optional[str] = None):
        """
        初始化扫描器

        Args:
            exchange_name: 交易所名称
            api_key: API密钥
            secret: 密钥
            testnet: 是否测试网
            password: 密码（OKX需要）
        """
        self.exchange_name = exchange_name
        self.exchange = ExchangeFactory.create_exchange(
            exchange_name, api_key, secret, testnet, password
        )
        self.signal_generator = SignalGenerator()

    async def scan_contracts(self, limit: int = 50) -> List[Dict]:
        """
        扫描所有合约，寻找交易机会

        Args:
            limit: 扫描数量限制

        Returns:
            信号列表（按信心度排序）
        """
        print(f"开始扫描 {self.exchange_name} 合约...")

        # 获取所有合约交易对
        symbols = self.exchange.get_futures_symbols()
        print(f"共找到 {len(symbols)} 个合约")

        # 限制扫描数量
        symbols = symbols[:limit]

        signals = []
        scanned_count = 0

        for symbol in symbols:
            try:
                # 获取K线数据
                ohlcv = self.exchange.get_ohlcv(symbol, timeframe='1h', limit=100)

                # 获取当前价格
                current_price = self.exchange.get_current_price(symbol)

                # 获取订单簿
                orderbook = self.exchange.get_order_book(symbol, limit=20)

                # 获取24小时行情
                ticker = self.exchange.get_24h_ticker(symbol)

                # 生成信号
                signal = self.signal_generator.generate_signal(
                    ohlcv, orderbook, current_price, ticker
                )

                # 添加额外信息
                signal['symbol'] = symbol
                signal['exchange'] = self.exchange_name
                signal['timestamp'] = datetime.now().isoformat()

                # 只保存有效信号
                if signal['has_signal']:
                    signals.append(signal)

                scanned_count += 1

                # 显示进度
                if scanned_count % 10 == 0:
                    print(f"已扫描 {scanned_count}/{len(symbols)} 个合约")

            except Exception as e:
                print(f"扫描 {symbol} 失败: {e}")
                continue

        # 按信心度排序
        signals.sort(key=lambda x: x['confidence'], reverse=True)

        print(f"扫描完成！共扫描 {scanned_count} 个合约，找到 {len(signals)} 个信号")

        return signals

    def scan_contracts_sync(self, limit: int = 50) -> List[Dict]:
        """
        同步扫描所有合约

        Args:
            limit: 扫描数量限制

        Returns:
            信号列表
        """
        return asyncio.run(self.scan_contracts(limit))
