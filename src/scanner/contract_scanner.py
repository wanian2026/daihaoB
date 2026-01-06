"""
合约扫描器
扫描所有合约，识别交易机会（使用公开API）
"""
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from exchanges import ExchangeFactory
from analysis import SignalGenerator


class ContractScanner:
    """合约扫描器"""

    def __init__(self, exchange_name: str, timeframe: str = "1h"):
        """
        初始化扫描器

        Args:
            exchange_name: 交易所名称
            timeframe: K线周期（默认1小时）
        """
        self.exchange_name = exchange_name
        self.timeframe = timeframe
        self.exchange = ExchangeFactory.create_exchange(exchange_name)
        self.signal_generator = SignalGenerator()

    def scan_contracts(self, limit: int = 50) -> List[Dict]:
        """
        扫描所有合约，寻找交易机会（同步方法）

        Args:
            limit: 扫描数量限制

        Returns:
            信号列表（按信心度排序）
        """
        print(f"=" * 60)
        print(f"🔍 开始扫描 {self.exchange_name} 合约")
        print(f"📊 K线周期: {self.timeframe}")
        print(f"⏱️  时间戳范围: 前{100}根{self.timeframe}K线")
        print(f"=" * 60)

        # 获取所有合约交易对
        symbols = self.exchange.get_futures_symbols()
        print(f"共找到 {len(symbols)} 个合约")

        # 限制扫描数量
        symbols = symbols[:limit]

        signals = []
        scanned_count = 0

        for symbol in symbols:
            try:
                # 获取K线数据（使用配置的K线周期）
                ohlcv = self.exchange.get_ohlcv(symbol, timeframe=self.timeframe, limit=100)

                # 验证获取的K线数据
                if ohlcv and len(ohlcv) > 1:
                    time_span = (ohlcv[-1][0] - ohlcv[0][0]) / 1000  # 转换为秒
                    if scanned_count == 0:  # 只在第一个合约打印验证信息
                        print(f"\n📌 验证K线周期 ({symbol}):")
                        print(f"   - 获取K线数量: {len(ohlcv)} 根")
                        print(f"   - 第一根K线时间: {datetime.fromtimestamp(ohlcv[0][0]/1000).strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"   - 最后一根K线时间: {datetime.fromtimestamp(ohlcv[-1][0]/1000).strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"   - 时间跨度: {time_span/60:.1f} 分钟")

                        # 验证周期是否正确
                        expected_seconds = {
                            '5m': 5 * 60,
                            '15m': 15 * 60,
                            '30m': 30 * 60,
                            '1h': 60 * 60,
                            '4h': 4 * 60 * 60,
                            '1d': 24 * 60 * 60,
                            '1w': 7 * 24 * 60 * 60
                        }

                        expected = expected_seconds.get(self.timeframe)
                        if expected:
                            avg_interval = time_span / (len(ohlcv) - 1)
                            print(f"   - 期望周期间隔: {expected} 秒")
                            print(f"   - 实际平均间隔: {avg_interval:.1f} 秒")
                            print(f"   - 周期验证: {'✅ 正确' if abs(avg_interval - expected) < 60 else '❌ 异常'}")
                        print()

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
                signal['timeframe'] = self.timeframe
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
