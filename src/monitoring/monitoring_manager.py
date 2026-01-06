"""
监测管理器
管理需要持续监测的合约，定期扫描并生成交易信号
"""
import threading
import time
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict
import asyncio

from exchanges import ExchangeFactory
from analysis import SignalGenerator


class MonitoringManager:
    """监测管理器 - 单例模式"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化监测管理器"""
        if hasattr(self, '_initialized'):
            return

        self._initialized = True

        # 监测合约列表 {symbol: {'exchange': 'binance', 'timeframes': ['5m', '1h', '1d']}}
        self.monitored_symbols: Dict[str, Dict] = {}

        # 最新信号缓存 {symbol: {timeframe: signal}}
        self.latest_signals: Dict[str, Dict[str, Dict]] = defaultdict(dict)

        # 监测状态
        self.is_running = False
        self.monitor_thread = None

        # 扫描间隔（秒）
        self.scan_interval = 30  # 30秒扫描一次

        # 交换机和信号生成器
        self.exchange = None
        self.signal_generator = None

        # 回调函数（用于WebSocket推送）
        self.signal_callbacks = []

    def start(self):
        """启动监测"""
        if self.is_running:
            print("监测已经在运行中")
            return

        print("启动监测管理器...")
        self.is_running = True

        # 初始化交易所和信号生成器
        if self.monitored_symbols:
            exchange_name = list(self.monitored_symbols.values())[0]['exchange']
            self.exchange = ExchangeFactory.create_exchange(exchange_name)
            self.signal_generator = SignalGenerator()

        # 启动监测线程
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        print(f"监测管理器已启动，扫描间隔: {self.scan_interval}秒")

    def stop(self):
        """停止监测"""
        print("停止监测管理器...")
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("监测管理器已停止")

    def add_symbol(self, symbol: str, exchange: str = 'binance',
                   timeframes: Optional[List[str]] = None) -> bool:
        """
        添加监测合约

        Args:
            symbol: 合约符号（如 BTC/USDT）
            exchange: 交易所
            timeframes: 监测的周期列表，默认 ['5m', '1h', '1d']

        Returns:
            是否添加成功
        """
        if timeframes is None:
            timeframes = ['5m', '1h', '1d']

        with self._lock:
            self.monitored_symbols[symbol] = {
                'exchange': exchange,
                'timeframes': timeframes,
                'added_at': datetime.now().isoformat()
            }

            # 重新初始化交易所（如果交易所变化）
            if self.exchange is None or exchange != self.exchange.exchange.name:
                self.exchange = ExchangeFactory.create_exchange(exchange)
                self.signal_generator = SignalGenerator()

        print(f"已添加监测合约: {symbol} ({exchange})")
        print(f"  监测周期: {', '.join(timeframes)}")

        return True

    def remove_symbol(self, symbol: str) -> bool:
        """
        移除监测合约

        Args:
            symbol: 合约符号

        Returns:
            是否移除成功
        """
        with self._lock:
            if symbol in self.monitored_symbols:
                del self.monitored_symbols[symbol]

                # 清理缓存
                if symbol in self.latest_signals:
                    del self.latest_signals[symbol]

                print(f"已移除监测合约: {symbol}")
                return True

        return False

    def get_monitored_symbols(self) -> List[Dict]:
        """
        获取监测合约列表

        Returns:
            监测合约列表
        """
        with self._lock:
            result = []
            for symbol, info in self.monitored_symbols.items():
                result.append({
                    'symbol': symbol,
                    'exchange': info['exchange'],
                    'timeframes': info['timeframes'],
                    'added_at': info['added_at'],
                    'signals_count': len(self.latest_signals.get(symbol, {}))
                })
            return result

    def get_latest_signals(self, symbol: Optional[str] = None) -> Dict:
        """
        获取最新信号

        Args:
            symbol: 合约符号，如果为None则返回所有

        Returns:
            信号字典
        """
        with self._lock:
            if symbol:
                return dict(self.latest_signals.get(symbol, {}))
            else:
                return {
                    sym: dict(signals)
                    for sym, signals in self.latest_signals.items()
                }

    def register_callback(self, callback):
        """
        注册信号回调（用于WebSocket推送）

        Args:
            callback: 回调函数，接收参数: symbol, timeframe, signal
        """
        if callback not in self.signal_callbacks:
            self.signal_callbacks.append(callback)

    def unregister_callback(self, callback):
        """
        注销信号回调

        Args:
            callback: 回调函数
        """
        if callback in self.signal_callbacks:
            self.signal_callbacks.remove(callback)

    def _monitor_loop(self):
        """监测循环"""
        while self.is_running:
            try:
                self._scan_symbols()
            except Exception as e:
                print(f"监测扫描出错: {e}")
                import traceback
                traceback.print_exc()

            # 等待下一次扫描
            time.sleep(self.scan_interval)

    def _scan_symbols(self):
        """扫描所有监测合约"""
        if not self.monitored_symbols:
            return

        print(f"\n{'='*60}")
        print(f"🔍 开始扫描监测合约 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        with self._lock:
            symbols_copy = list(self.monitored_symbols.keys())

        for symbol in symbols_copy:
            with self._lock:
                if symbol not in self.monitored_symbols:
                    continue

                info = self.monitored_symbols[symbol]
                timeframes = info['timeframes']

            print(f"\n📊 扫描合约: {symbol}")

            for timeframe in timeframes:
                try:
                    # 获取数据
                    ohlcv = self.exchange.get_ohlcv(symbol, timeframe=timeframe, limit=100)
                    current_price = self.exchange.get_current_price(symbol)
                    orderbook = self.exchange.get_order_book(symbol, limit=20)
                    ticker = self.exchange.get_24h_ticker(symbol)

                    # 生成信号
                    signal = self.signal_generator.generate_signal(
                        ohlcv, orderbook, current_price, ticker
                    )

                    # 添加额外信息
                    signal['symbol'] = symbol
                    signal['exchange'] = info['exchange']
                    signal['timeframe'] = timeframe
                    signal['timestamp'] = datetime.now().isoformat()

                    # 缓存信号
                    with self._lock:
                        if symbol not in self.latest_signals:
                            self.latest_signals[symbol] = {}
                        self.latest_signals[symbol][timeframe] = signal

                    # 如果有有效信号，通知回调
                    if signal['has_signal']:
                        print(f"  ✅ {timeframe}: 发现信号！方向={signal['direction']}, 信心度={signal['confidence']:.1f}%")

                        # 调用所有回调函数
                        for callback in self.signal_callbacks:
                            try:
                                callback(symbol, timeframe, signal)
                            except Exception as e:
                                print(f"    ⚠️  回调执行失败: {e}")
                    else:
                        print(f"  ⭕ {timeframe}: 无信号 ({signal['reason']})")

                except Exception as e:
                    print(f"  ❌ {timeframe}: 扫描失败 - {e}")
                    continue

        print(f"\n{'='*60}")
        print(f"✅ 扫描完成")
        print(f"{'='*60}\n")
