"""
信号生成模块
整合 FVG 和流动性分析，生成交易信号
"""
from typing import Dict, List, Optional
import numpy as np
from .fvg import FVGAnalyzer
from .liquidity import LiquidityAnalyzer


class SignalGenerator:
    """信号生成器"""

    def __init__(self):
        self.fvg_analyzer = FVGAnalyzer()
        self.liquidity_analyzer = LiquidityAnalyzer()

    def _calculate_atr(self, ohlcv: List, period: int = 14) -> Optional[float]:
        """
        计算平均真实波幅（ATR）

        Args:
            ohlcv: K线数据 [[timestamp, open, high, low, close, volume], ...]
            period: ATR周期，默认14

        Returns:
            ATR值
        """
        if len(ohlcv) < period + 1:
            return None

        # 提取高低价
        highs = np.array([candle[2] for candle in ohlcv])
        lows = np.array([candle[3] for candle in ohlcv])
        closes = np.array([candle[4] for candle in ohlcv])

        # 计算真实波幅（TR）
        tr_list = []
        for i in range(1, len(ohlcv)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            tr = max(high_low, high_close, low_close)
            tr_list.append(tr)

        # 计算ATR（使用简单移动平均）
        if len(tr_list) >= period:
            atr = np.mean(tr_list[-period:])
            return atr

        return None

    def generate_signal(self, ohlcv: List, orderbook: Dict, current_price: float,
                       ticker: Dict) -> Dict:
        """
        生成交易信号

        Args:
            ohlcv: K线数据
            orderbook: 订单簿
            current_price: 当前价格
            ticker: 24小时行情数据

        Returns:
            交易信号
        """
        # 检测 FVG
        fvg_list = self.fvg_analyzer.detect_fvg(ohlcv)
        recent_fvg = self.fvg_analyzer.get_recent_fvg(ohlcv, limit=5)

        # 分析流动性
        liquidity = self.liquidity_analyzer.analyze_orderbook(orderbook, current_price)
        liquidity_zones = self.liquidity_analyzer.find_liquidity_zones(orderbook, current_price)

        # 生成信号
        signal = self._generate_trade_signal(
            recent_fvg, liquidity, liquidity_zones, current_price, ticker
        )

        return signal

    def _generate_trade_signal(self, fvg_list: List, liquidity: Dict,
                               liquidity_zones: List, current_price: float,
                               ticker: Dict) -> Dict:
        """
        生成交易信号（入场、止盈、止损）

        Args:
            fvg_list: FVG 列表
            liquidity: 流动性分析
            liquidity_zones: 流动性区域
            current_price: 当前价格
            ticker: 行情数据

        Returns:
            交易信号
        """
        # 基础信号结构
        signal = {
            'has_signal': False,
            'direction': None,  # 'long' or 'short'
            'entry_price': current_price,
            'take_profit': None,
            'take_profit_reason': '',  # 止盈价格依据
            'stop_loss': None,
            'confidence': 0,
            'reason': '',
            'risk_reward_ratio': 0,
            'fvg_info': None,
            'liquidity_info': liquidity,
            'liquidity_zones': liquidity_zones
        }

        # 计算ATR，用于备用止盈方案
        atr = self._calculate_atr(ohlcv)

        # 检查是否有有效的 FVG
        if not fvg_list:
            signal['reason'] = '未发现 FVG 机会'
            return signal

        # 获取最强的 FVG（信心度最高）
        best_fvg = max(fvg_list, key=lambda x: x['confidence'])

        # 检查当前价格是否与FVG相关（在FVG附近）
        fvg_low = best_fvg['gap_low']
        fvg_high = best_fvg['gap_high']
        fvg_size = best_fvg['size']

        # 计算价格与FVG的距离（百分比）
        if best_fvg['type'] == 'bullish':
            # 牛市FVG：价格如果在FVG下方附近或进入FVG区间，考虑做多
            price_distance_low = abs(current_price - fvg_low) / current_price
            price_distance_high = abs(current_price - fvg_high) / current_price

            # 如果价格在FVG区间内，或者在FVG下沿附近2%以内
            if current_price >= fvg_low or price_distance_low <= 0.02:
                signal['direction'] = 'long'

                # 入场价：当前价格
                signal['entry_price'] = current_price

                # 止损价：FVG下沿下方2%
                signal['stop_loss'] = fvg_low * 0.98

                # 止盈价：查找上方的卖单流动性密集区
                target_liquidity = self.liquidity_analyzer.find_target_liquidity_zone(
                    orderbook, current_price, 'long'
                )

                if target_liquidity:
                    # 使用流动性密集区价格作为止盈价
                    signal['take_profit'] = target_liquidity['price']
                    signal['take_profit_reason'] = target_liquidity['reason']
                else:
                    # 备用方案：基于ATR计算止盈价格
                    risk = signal['entry_price'] - signal['stop_loss']
                    if atr and atr > 0:
                        # 使用ATR的2.5倍作为止盈距离，确保止盈目标合理
                        take_profit_distance = atr * 2.5
                        signal['take_profit'] = signal['entry_price'] + take_profit_distance
                        signal['take_profit_reason'] = f"ATR止损法(ATR:{atr:.2f}, 距离:{take_profit_distance:.2f})"
                    else:
                        # 如果没有ATR数据，使用固定的2.5:1盈亏比
                        signal['take_profit'] = signal['entry_price'] + risk * 2.5
                        signal['take_profit_reason'] = "固定盈亏比(2.5:1)"

                # 如果价格已经在FVG上方，可以考虑更激进的入场价（FVG下沿附近）
                if current_price > fvg_high:
                    signal['reason'] = f"价格回踩FVG {fvg_low:.2f}-{fvg_high:.2f} 支撑位，做多机会"
                else:
                    signal['reason'] = f"价格在FVG {fvg_low:.2f}-{fvg_high:.2f} 支撑区，做多机会"

            else:
                signal['reason'] = f'价格距离FVG太远 ({price_distance_low*100:.2f}%)，不宜进场'
                return signal

        elif best_fvg['type'] == 'bearish':
            # 熊市FVG：价格如果在FVG上方附近或进入FVG区间，考虑做空
            price_distance_low = abs(current_price - fvg_low) / current_price
            price_distance_high = abs(current_price - fvg_high) / current_price

            # 如果价格在FVG区间内，或者在FVG上沿附近2%以内
            if current_price <= fvg_high or price_distance_high <= 0.02:
                signal['direction'] = 'short'

                # 入场价：当前价格
                signal['entry_price'] = current_price

                # 止损价：FVG上沿上方2%
                signal['stop_loss'] = fvg_high * 1.02

                # 止盈价：查找下方的买单流动性密集区
                target_liquidity = self.liquidity_analyzer.find_target_liquidity_zone(
                    orderbook, current_price, 'short'
                )

                if target_liquidity:
                    # 使用流动性密集区价格作为止盈价
                    signal['take_profit'] = target_liquidity['price']
                    signal['take_profit_reason'] = target_liquidity['reason']
                else:
                    # 备用方案：基于ATR计算止盈价格
                    risk = signal['stop_loss'] - signal['entry_price']
                    if atr and atr > 0:
                        # 使用ATR的2.5倍作为止盈距离，确保止盈目标合理
                        take_profit_distance = atr * 2.5
                        signal['take_profit'] = signal['entry_price'] - take_profit_distance
                        signal['take_profit_reason'] = f"ATR止损法(ATR:{atr:.2f}, 距离:{take_profit_distance:.2f})"
                    else:
                        # 如果没有ATR数据，使用固定的2.5:1盈亏比
                        signal['take_profit'] = signal['entry_price'] - risk * 2.5
                        signal['take_profit_reason'] = "固定盈亏比(2.5:1)"

                # 如果价格已经在FVG下方，可以考虑更激进的入场价（FVG上沿附近）
                if current_price < fvg_low:
                    signal['reason'] = f"价格反弹FVG {fvg_low:.2f}-{fvg_high:.2f} 阻力位，做空机会"
                else:
                    signal['reason'] = f"价格在FVG {fvg_low:.2f}-{fvg_high:.2f} 阻力区，做空机会"

            else:
                signal['reason'] = f'价格距离FVG太远 ({price_distance_high*100:.2f}%)，不宜进场'
                return signal

        # 计算盈亏比
        if signal['take_profit'] and signal['stop_loss'] and signal['entry_price']:
            if signal['direction'] == 'long':
                risk = signal['entry_price'] - signal['stop_loss']
                reward = signal['take_profit'] - signal['entry_price']
            else:
                risk = signal['stop_loss'] - signal['entry_price']
                reward = signal['entry_price'] - signal['take_profit']

            if risk > 0:
                signal['risk_reward_ratio'] = reward / risk

        # 计算综合信心度
        confidence = self._calculate_total_confidence(
            best_fvg, liquidity, ticker, signal
        )

        if confidence < 40:  # 提高最低信心度阈值
            signal['reason'] = f'信心度不足 ({confidence:.1f}%)'
            return signal

        # 检查流动性是否充足
        if liquidity['liquidity_score'] < 30:
            signal['reason'] = '流动性不足'
            return signal

        # 设置信号状态
        signal['has_signal'] = True
        signal['confidence'] = confidence
        signal['fvg_info'] = best_fvg

        return signal

    def _calculate_total_confidence(self, fvg: Dict, liquidity: Dict,
                                     ticker: Dict, signal: Dict) -> float:
        """
        计算总信心度（重新修正）

        Args:
            fvg: FVG 信息
            liquidity: 流动性分析
            ticker: 行情数据
            signal: 信号信息（包含价格数据）

        Returns:
            总信心度 (0-100)
        """
        # 1. FVG 信心度 (35%) - 基于FVG大小和强度
        fvg_confidence = fvg['confidence'] * 0.35

        # 2. 流动性信心度 (25%) - 基于订单簿深度
        liquidity_confidence = liquidity['liquidity_score'] * 0.25

        # 3. 价格与FVG的匹配度 (20%) - 价格越接近FVG边缘，信心度越高
        fvg_low = fvg['gap_low']
        fvg_high = fvg['gap_high']
        current_price = signal['entry_price']

        if fvg['type'] == 'bullish':
            # 做多：价格在FVG下方或进入FVG区间
            if current_price < fvg_low:
                # 价格在FVG下方，计算距离
                distance = abs(current_price - fvg_low) / current_price
                price_match = max(0, 100 - distance * 5000)  # 距离越近分数越高
            else:
                # 价格在FVG区间内，分数最高
                price_match = 100
        else:
            # 做空：价格在FVG上方或进入FVG区间
            if current_price > fvg_high:
                # 价格在FVG上方，计算距离
                distance = abs(current_price - fvg_high) / current_price
                price_match = max(0, 100 - distance * 5000)
            else:
                # 价格在FVG区间内，分数最高
                price_match = 100

        price_match_confidence = price_match * 0.20

        # 4. 市场波动率 (10%) - 适度波动率有利于交易
        volatility = abs(ticker.get('change', 0))
        # 理想波动率在 2% - 8% 之间
        if 0.02 <= volatility <= 0.08:
            volatility_score = 100
        elif volatility < 0.02:
            volatility_score = 50  # 波动率太低
        else:
            volatility_score = 80  # 波动率稍高，但仍可交易

        volatility_confidence = volatility_score * 0.10

        # 5. 盈亏比 (10%) - 盈亏比越高，信心度越高
        rr_ratio = signal.get('risk_reward_ratio', 0)
        if rr_ratio >= 2.0:
            rr_score = 100
        elif rr_ratio >= 1.5:
            rr_score = 80
        elif rr_ratio >= 1.0:
            rr_score = 60
        else:
            rr_score = 40

        rr_confidence = rr_score * 0.10

        # 计算总信心度
        total_confidence = (
            fvg_confidence +
            liquidity_confidence +
            price_match_confidence +
            volatility_confidence +
            rr_confidence
        )

        return min(total_confidence, 100)
