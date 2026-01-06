"""
流动性分析模块
分析订单簿深度、买卖不平衡等流动性特征
"""
from typing import Dict, List, Optional
import numpy as np


class LiquidityAnalyzer:
    """流动性分析器"""

    def __init__(self):
        pass

    def analyze_orderbook(self, orderbook: Dict, current_price: float) -> Dict:
        """
        分析订单簿

        Args:
            orderbook: 订单簿数据 {'bids': [[price, amount], ...], 'asks': [[price, amount], ...]}
            current_price: 当前价格

        Returns:
            流动性分析结果
        """
        bids = orderbook.get('bids', [])
        asks = orderbook.get('asks', [])

        if not bids or not asks:
            return {
                'bid_volume': 0,
                'ask_volume': 0,
                'imbalance_ratio': 0,
                'liquidity_score': 0,
                'depth_ratio': 0
            }

        # 计算买卖单总量
        bid_volume = sum([bid[1] for bid in bids])
        ask_volume = sum([ask[1] for ask in asks])

        # 计算不平衡比例
        total_volume = bid_volume + ask_volume
        if total_volume == 0:
            imbalance_ratio = 0
        else:
            imbalance_ratio = (bid_volume - ask_volume) / total_volume

        # 计算深度比（靠近市价的订单量）
        depth_ratio = self._calculate_depth_ratio(bids, asks, current_price)

        # 计算流动性评分
        liquidity_score = self._calculate_liquidity_score(bid_volume, ask_volume, depth_ratio)

        return {
            'bid_volume': bid_volume,
            'ask_volume': ask_volume,
            'imbalance_ratio': imbalance_ratio,  # 正值表示买单多，负值表示卖单多
            'liquidity_score': liquidity_score,
            'depth_ratio': depth_ratio
        }

    def _calculate_depth_ratio(self, bids: List, asks: List, current_price: float) -> float:
        """
        计算深度比（靠近市价的订单量占比）

        Args:
            bids: 买单
            asks: 卖单
            current_price: 当前价格

        Returns:
            深度比
        """
        # 计算前5档的订单量占比
        if not bids or not asks:
            return 0

        top_5_bids = sum([bid[1] for bid in bids[:5]])
        top_5_asks = sum([ask[1] for ask in asks[:5]])

        total_bids = sum([bid[1] for bid in bids])
        total_asks = sum([ask[1] for ask in asks])

        if total_bids == 0 or total_asks == 0:
            return 0

        top_5_ratio = (top_5_bids + top_5_asks) / (total_bids + total_asks)
        return top_5_ratio

    def _calculate_liquidity_score(self, bid_volume: float, ask_volume: float, depth_ratio: float) -> float:
        """
        计算流动性评分（重新修正）

        Args:
            bid_volume: 买单总量
            ask_volume: 卖单总量
            depth_ratio: 深度比

        Returns:
            流动性评分 (0-100)
        """
        # 1. 总订单量评分 (50分) - 流动性基础
        total_volume = bid_volume + ask_volume

        if total_volume > 5000000:  # 500万以上
            volume_score = 50
        elif total_volume > 1000000:  # 100万-500万
            volume_score = 45
        elif total_volume > 500000:   # 50万-100万
            volume_score = 40
        elif total_volume > 100000:   # 10万-50万
            volume_score = 35
        elif total_volume > 50000:    # 5万-10万
            volume_score = 30
        elif total_volume > 10000:    # 1万-5万
            volume_score = 25
        else:
            volume_score = 20

        # 2. 深度评分 (30分) - 市价附近的流动性
        # 深度比越高，说明流动性越集中在市价附近
        depth_score = depth_ratio * 30  # 最多30分

        # 3. 买卖平衡评分 (20分) - 买卖单平衡度
        if total_volume > 0:
            balance = min(bid_volume, ask_volume) / total_volume
            # 平衡度0.5表示完美平衡
            balance_score = balance * 40  # 最多40分，归一化到20分
            balance_score = min(balance_score, 20)
        else:
            balance_score = 0

        total_score = volume_score + depth_score + balance_score
        return min(total_score, 100)

    def find_liquidity_zones(self, orderbook: Dict, current_price: float) -> List[Dict]:
        """
        查找流动性区域（大量挂单的价格区间）

        Args:
            orderbook: 订单簿
            current_price: 当前价格

        Returns:
            流动性区域列表
        """
        bids = orderbook.get('bids', [])
        asks = orderbook.get('asks', [])

        zones = []

        # 分析买单流动性
        if bids:
            # 计算买单的平均量和标准差
            bid_amounts = [bid[1] for bid in bids]
            mean_bid = np.mean(bid_amounts)
            std_bid = np.std(bid_amounts)

            # 查找异常大的买单
            threshold = mean_bid + 2 * std_bid

            for bid in bids:
                if bid[1] > threshold:
                    zones.append({
                        'type': 'buy',
                        'price': bid[0],
                        'volume': bid[1],
                        'distance': (current_price - bid[0]) / current_price * 100  # 距离百分比
                    })

        # 分析卖单流动性
        if asks:
            # 计算卖单的平均量和标准差
            ask_amounts = [ask[1] for ask in asks]
            mean_ask = np.mean(ask_amounts)
            std_ask = np.std(ask_amounts)

            # 查找异常大的卖单
            threshold = mean_ask + 2 * std_ask

            for ask in asks:
                if ask[1] > threshold:
                    zones.append({
                        'type': 'sell',
                        'price': ask[0],
                        'volume': ask[1],
                        'distance': (ask[0] - current_price) / current_price * 100
                    })

        # 按距离排序
        zones.sort(key=lambda x: abs(x['distance']))

        return zones[:5]  # 返回最近的5个流动性区域

    def find_target_liquidity_zone(self, orderbook: Dict, current_price: float,
                                    direction: str) -> Optional[Dict]:
        """
        查找目标方向的流动性密集区（用于止盈）

        做多时：查找上方最近的卖单流动性密集区
        做空时：查找下方最近的买单流动性密集区

        Args:
            orderbook: 订单簿
            current_price: 当前价格
            direction: 方向 'long' 或 'short'

        Returns:
            流动性密集区信息，如果未找到返回 None
        """
        liquidity_zones = self.find_liquidity_zones(orderbook, current_price)

        if not liquidity_zones:
            return None

        # 根据方向筛选流动性区域
        if direction == 'long':
            # 做多：查找上方的卖单流动性密集区
            sell_zones = [z for z in liquidity_zones if z['type'] == 'sell' and z['price'] > current_price]

            if not sell_zones:
                return None

            # 返回最近的卖单流动性密集区
            return min(sell_zones, key=lambda x: x['distance'])

        elif direction == 'short':
            # 做空：查找下方的买单流动性密集区
            buy_zones = [z for z in liquidity_zones if z['type'] == 'buy' and z['price'] < current_price]

            if not buy_zones:
                return None

            # 返回最近的买单流动性密集区
            return min(buy_zones, key=lambda x: abs(x['distance']))

        return None
