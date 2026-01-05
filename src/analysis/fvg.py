"""
FVG (Fair Value Gap) 算法实现
FVG 是价格行为分析中的一个重要概念，表示市场中未被填补的价格缺口
"""
from typing import List, Dict, Tuple, Optional
import numpy as np


class FVGAnalyzer:
    """FVG 分析器"""

    def __init__(self, min_fvg_ratio: float = 0.1):
        """
        初始化 FVG 分析器

        Args:
            min_fvg_ratio: 最小 FVG 比例（相对于K线实体的比例）
        """
        self.min_fvg_ratio = min_fvg_ratio

    def detect_fvg(self, ohlcv: List[List]) -> List[Dict]:
        """
        检测 FVG

        Args:
            ohlcv: K线数据 [[timestamp, open, high, low, close, volume], ...]

        Returns:
            FVG 列表
        """
        fvg_list = []

        if len(ohlcv) < 3:
            return fvg_list

        # 遍历K线，寻找FVG模式
        for i in range(1, len(ohlcv) - 1):
            prev_candle = ohlcv[i - 1]
            curr_candle = ohlcv[i]
            next_candle = ohlcv[i + 1]

            _, prev_open, prev_high, prev_low, prev_close, _ = prev_candle
            _, curr_open, curr_high, curr_low, curr_close, _ = curr_candle
            _, next_open, next_high, next_low, next_close, _ = next_candle

            # 牛市 FVG (Bullish FVG)
            # 上一根K线的最低价 > 下一根K线的最高价
            # 中间是强势上涨的K线
            if prev_low > next_high:
                fvg_size = prev_low - next_high
                candle_range = curr_high - curr_low

                if fvg_size > 0 and candle_range > 0:
                    fvg_ratio = fvg_size / candle_range

                    if fvg_ratio >= self.min_fvg_ratio:
                        fvg_list.append({
                            'type': 'bullish',
                            'gap_high': prev_low,
                            'gap_low': next_high,
                            'size': fvg_size,
                            'ratio': fvg_ratio,
                            'timestamp': curr_candle[0],
                            'confidence': self._calculate_confidence(fvg_ratio, 'bullish')
                        })

            # 熊市 FVG (Bearish FVG)
            # 上一根K线的最高价 < 下一根K线的最低价
            elif prev_high < next_low:
                fvg_size = next_low - prev_high
                candle_range = curr_high - curr_low

                if fvg_size > 0 and candle_range > 0:
                    fvg_ratio = fvg_size / candle_range

                    if fvg_ratio >= self.min_fvg_ratio:
                        fvg_list.append({
                            'type': 'bearish',
                            'gap_high': next_low,
                            'gap_low': prev_high,
                            'size': fvg_size,
                            'ratio': fvg_ratio,
                            'timestamp': curr_candle[0],
                            'confidence': self._calculate_confidence(fvg_ratio, 'bearish')
                        })

        return fvg_list

    def _calculate_confidence(self, fvg_ratio: float, fvg_type: str) -> float:
        """
        计算 FVG 信心度（重新修正）

        Args:
            fvg_ratio: FVG 比例
            fvg_type: FVG 类型

        Returns:
            信心度 (0-100)
        """
        # 基础信心度：基于FVG大小
        # FVG比例越大，信心度越高，但有上限
        if fvg_ratio >= 0.5:
            # 非常大的FVG（50%以上）
            base_confidence = 90
        elif fvg_ratio >= 0.3:
            # 大FVG（30%-50%）
            base_confidence = 80
        elif fvg_ratio >= 0.2:
            # 中等FVG（20%-30%）
            base_confidence = 70
        elif fvg_ratio >= 0.1:
            # 小FVG（10%-20%）
            base_confidence = 60
        elif fvg_ratio >= 0.05:
            # 很小FVG（5%-10%）
            base_confidence = 50
        else:
            # 极小FVG（小于5%）
            base_confidence = 40

        # 额外加分：FVG类型
        # 牛市FVG和熊市FVG同等权重
        if fvg_type in ['bullish', 'bearish']:
            base_confidence += 5

        # 确保不超过100
        return min(base_confidence, 100)

    def find_fvg_at_price(self, fvg_list: List[Dict], price: float, tolerance: float = 0.001) -> Optional[Dict]:
        """
        查找价格附近的 FVG

        Args:
            fvg_list: FVG 列表
            price: 当前价格
            tolerance: 容差比例

        Returns:
            匹配的 FVG
        """
        for fvg in fvg_list:
            gap_low = fvg['gap_low']
            gap_high = fvg['gap_high']

            # 检查价格是否在 FVG 范围内
            if gap_low * (1 - tolerance) <= price <= gap_high * (1 + tolerance):
                return fvg

        return None

    def get_recent_fvg(self, ohlcv: List[List], limit: int = 10) -> List[Dict]:
        """
        获取最近的 FVG

        Args:
            ohlcv: K线数据
            limit: 返回数量

        Returns:
            最近的 FVG 列表
        """
        fvg_list = self.detect_fvg(ohlcv)
        # 按时间戳排序，返回最近的
        fvg_list.sort(key=lambda x: x['timestamp'], reverse=True)
        return fvg_list[:limit]
