"""
信号生成模块
整合 FVG 和流动性分析，生成交易信号
"""
from typing import Dict, List, Optional
from .fvg import FVGAnalyzer
from .liquidity import LiquidityAnalyzer


class SignalGenerator:
    """信号生成器"""

    def __init__(self):
        self.fvg_analyzer = FVGAnalyzer()
        self.liquidity_analyzer = LiquidityAnalyzer()

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
            'stop_loss': None,
            'confidence': 0,
            'reason': '',
            'risk_reward_ratio': 0,
            'fvg_info': None,
            'liquidity_info': liquidity,
            'liquidity_zones': liquidity_zones
        }

        # 检查是否有有效的 FVG
        if not fvg_list:
            signal['reason'] = '未发现 FVG 机会'
            return signal

        # 获取最强的 FVG（信心度最高）
        best_fvg = max(fvg_list, key=lambda x: x['confidence'])

        # 计算综合信心度
        confidence = self._calculate_total_confidence(
            best_fvg, liquidity, ticker
        )

        if confidence < 30:  # 最低信心度阈值
            signal['reason'] = f'信心度不足 ({confidence:.1f}%)'
            return signal

        # 根据FVG类型确定交易方向
        if best_fvg['type'] == 'bullish':
            signal['direction'] = 'long'
            # 做多：入场价在 FVG 上沿附近
            signal['entry_price'] = best_fvg['gap_high']

            # 止损：FVG 下沿下方
            signal['stop_loss'] = best_fvg['gap_low'] * 0.995  # 下方0.5%

            # 止盈：根据盈亏比
            risk = signal['entry_price'] - signal['stop_loss']
            signal['take_profit'] = signal['entry_price'] + risk * 2.0  # 2:1盈亏比

        elif best_fvg['type'] == 'bearish':
            signal['direction'] = 'short'
            # 做空：入场价在 FVG 下沿附近
            signal['entry_price'] = best_fvg['gap_low']

            # 止损：FVG 上沿上方
            signal['stop_loss'] = best_fvg['gap_high'] * 1.005  # 上方0.5%

            # 止盈：根据盈亏比
            risk = signal['stop_loss'] - signal['entry_price']
            signal['take_profit'] = signal['entry_price'] - risk * 2.0  # 2:1盈亏比

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

        # 检查流动性是否充足
        if liquidity['liquidity_score'] < 30:
            signal['reason'] = '流动性不足'
            return signal

        # 设置信号状态
        signal['has_signal'] = True
        signal['confidence'] = confidence
        signal['fvg_info'] = best_fvg
        signal['reason'] = f"FVG {best_fvg['type'].upper()} 信号"

        return signal

    def _calculate_total_confidence(self, fvg: Dict, liquidity: Dict, ticker: Dict) -> float:
        """
        计算总信心度

        Args:
            fvg: FVG 信息
            liquidity: 流动性分析
            ticker: 行情数据

        Returns:
            总信心度 (0-100)
        """
        # FVG 信心度 (40%)
        fvg_confidence = fvg['confidence'] * 0.4

        # 流动性信心度 (30%)
        liquidity_confidence = liquidity['liquidity_score'] * 0.3

        # 市场波动率信心度 (15%)
        volatility = abs(ticker.get('change', 0))
        volatility_confidence = min(volatility * 5, 100) * 0.15  # 波动率越大信心度越高（但不超过100）

        # 买卖不平衡信心度 (15%)
        imbalance = abs(liquidity['imbalance_ratio'])
        imbalance_confidence = imbalance * 100 * 0.15

        total_confidence = fvg_confidence + liquidity_confidence + volatility_confidence + imbalance_confidence

        return min(total_confidence, 100)
