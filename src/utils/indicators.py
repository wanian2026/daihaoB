"""
技术指标计算工具
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import numpy as np

from exchanges.base_exchange import BaseExchange


@dataclass
class ATRResult:
    """ATR计算结果"""
    atr: float
    atr_percentage: float  # ATR占当前价格的百分比
    current_price: float
    period: int
    volatility: str  # 低/中/高

    def __str__(self):
        return f"ATR: {self.atr:.2f} ({self.atr_percentage:.2f}%), 波动性: {self.volatility}"


class TechnicalIndicators:
    """技术指标计算类"""

    @staticmethod
    def get_ohlcv(exchange: BaseExchange, symbol: str, timeframe: str = '1h', limit: int = 100) -> List[List[float]]:
        """
        获取K线数据
        
        Args:
            exchange: 交易所实例
            symbol: 交易对
            timeframe: K线周期 (1m, 5m, 15m, 1h, 4h, 1d)
            limit: 获取数量
        
        Returns:
            K线数据列表 [[timestamp, open, high, low, close, volume], ...]
        """
        try:
            ohlcv = exchange.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            raise Exception(f"获取K线数据失败: {e}")

    @staticmethod
    def calculate_atr(ohlcv: List[List[float]], period: int = 14) -> ATRResult:
        """
        计算ATR（平均真实波幅）
        
        Args:
            ohlcv: K线数据 [[timestamp, open, high, low, close, volume], ...]
            period: ATR周期，默认14
        
        Returns:
            ATRResult对象
        """
        if len(ohlcv) < period + 1:
            raise ValueError(f"K线数据不足，至少需要 {period + 1} 条，当前只有 {len(ohlcv)} 条")

        # 提取数据
        highs = np.array([candle[2] for candle in ohlcv])
        lows = np.array([candle[3] for candle in ohlcv])
        closes = np.array([candle[4] for candle in ohlcv])

        # 计算真实波幅（TR）
        # TR = max(high - low, abs(high - previous_close), abs(low - previous_close))
        high_low = highs[1:] - lows[1:]
        high_prev_close = np.abs(highs[1:] - closes[:-1])
        low_prev_close = np.abs(lows[1:] - closes[:-1])
        
        tr = np.maximum(np.maximum(high_low, high_prev_close), low_prev_close)

        # 计算ATR（简单移动平均）
        atr = np.mean(tr[-period:])
        
        # 当前价格
        current_price = closes[-1]
        
        # ATR占价格的百分比
        atr_percentage = (atr / current_price) * 100
        
        # 波动性等级
        if atr_percentage < 0.5:
            volatility = "低"
        elif atr_percentage < 1.5:
            volatility = "中"
        else:
            volatility = "高"

        return ATRResult(
            atr=atr,
            atr_percentage=atr_percentage,
            current_price=current_price,
            period=period,
            volatility=volatility
        )

    @staticmethod
    def get_suggested_params_from_atr(atr_result: ATRResult) -> Dict[str, float]:
        """
        基于ATR生成策略参数建议
        
        Args:
            atr_result: ATR计算结果
        
        Returns:
            建议的参数字典
        """
        # 根据ATR百分比和波动性生成建议
        atr_pct = atr_result.atr_percentage
        
        # 上涨/下跌阈值：建议为ATR的1-2倍
        if atr_result.volatility == "低":
            # 低波动，设置较小阈值
            long_threshold = max(atr_pct * 1.5, 0.5) / 100  # 至少0.5%
            short_threshold = max(atr_pct * 1.5, 0.5) / 100
            stop_loss_ratio = max(atr_pct * 3, 1.0) / 100  # 至少1%
        elif atr_result.volatility == "中":
            # 中等波动
            long_threshold = max(atr_pct * 1.2, 0.8) / 100
            short_threshold = max(atr_pct * 1.2, 0.8) / 100
            stop_loss_ratio = max(atr_pct * 2.5, 1.5) / 100
        else:
            # 高波动，设置较大阈值
            long_threshold = max(atr_pct * 1.0, 1.0) / 100
            short_threshold = max(atr_pct * 1.0, 1.0) / 100
            stop_loss_ratio = max(atr_pct * 2.0, 2.0) / 100

        # 限制阈值范围
        long_threshold = min(max(long_threshold, 0.005), 0.05)  # 0.5% - 5%
        short_threshold = min(max(short_threshold, 0.005), 0.05)
        stop_loss_ratio = min(max(stop_loss_ratio, 0.01), 0.10)  # 1% - 10%

        return {
            'long_threshold': long_threshold,
            'short_threshold': short_threshold,
            'stop_loss_ratio': stop_loss_ratio,
            'atr_based': True,
            'atr_value': atr_result.atr,
            'atr_percentage': atr_result.atr_percentage,
            'volatility': atr_result.volatility
        }

    @staticmethod
    def get_atr_with_timeframe(exchange: BaseExchange, symbol: str, 
                               timeframe: str = '1h', period: int = 14) -> ATRResult:
        """
        获取指定时间周期的ATR
        
        Args:
            exchange: 交易所实例
            symbol: 交易对
            timeframe: K线周期
            period: ATR周期
        
        Returns:
            ATRResult对象
        """
        ohlcv = TechnicalIndicators.get_ohlcv(exchange, symbol, timeframe, period + 10)
        return TechnicalIndicators.calculate_atr(ohlcv, period)

    @staticmethod
    def display_atr_info(atr_result: ATRResult):
        """显示ATR信息"""
        print("\n" + "=" * 60)
        print("市场波动性分析（ATR）")
        print("=" * 60)
        print(f"当前价格: ${atr_result.current_price:.2f}")
        print(f"ATR({atr_result.period}): ${atr_result.atr:.2f}")
        print(f"ATR占比: {atr_result.atr_percentage:.2f}%")
        print(f"波动性等级: {atr_result.volatility}")
        
        # 波动性说明
        if atr_result.volatility == "低":
            volatility_desc = "市场波动较小，适合较小阈值策略"
        elif atr_result.volatility == "中":
            volatility_desc = "市场波动适中，建议设置中等阈值"
        else:
            volatility_desc = "市场波动较大，建议设置较大阈值并提高止损"
        
        print(f"说明: {volatility_desc}")
        print("=" * 60)
