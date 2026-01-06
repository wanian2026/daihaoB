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
        查找流动性区域（使用分段累积订单量方法）

        将订单簿分成多个价格区间，计算每个区间的累积订单量，
        找到订单量最大的几个区间作为流动性密集区。

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
            # 将买单分成多个区间（每5档一个区间）
            bid_zones = self._analyze_liquidity_by_zones(bids, current_price, 'buy')
            zones.extend(bid_zones)

        # 分析卖单流动性
        if asks:
            # 将卖单分成多个区间（每5档一个区间）
            ask_zones = self._analyze_liquidity_by_zones(asks, current_price, 'sell')
            zones.extend(ask_zones)

        # 按订单量排序（优先选择订单量大的）
        zones.sort(key=lambda x: x['volume'], reverse=True)

        return zones[:10]  # 返回订单量最大的10个流动性区域

    def _analyze_liquidity_by_zones(self, orders: List, current_price: float,
                                     order_type: str) -> List[Dict]:
        """
        将订单分成多个区间，分析每个区间的累积订单量

        Args:
            orders: 订单列表 [[price, amount], ...]
            current_price: 当前价格
            order_type: 订单类型 'buy' 或 'sell'

        Returns:
            流动性区域列表
        """
        if not orders:
            return []

        # 每个区间包含5档订单
        zone_size = 5
        zones = []

        # 将订单分成多个区间
        for i in range(0, len(orders), zone_size):
            zone_orders = orders[i:i + zone_size]

            if not zone_orders:
                continue

            # 计算该区间的累积订单量
            total_volume = sum([order[1] for order in zone_orders])

            # 计算该区间的平均价格（使用成交量加权平均）
            total_value = sum([order[0] * order[1] for order in zone_orders])
            avg_price = total_value / total_volume if total_volume > 0 else zone_orders[0][0]

            # 计算距离
            if order_type == 'buy':
                distance = (current_price - avg_price) / current_price * 100
            else:
                distance = (avg_price - current_price) / current_price * 100

            zones.append({
                'type': order_type,
                'price': avg_price,
                'volume': total_volume,
                'distance': distance,
                'order_count': len(zone_orders)
            })

        # 只保留订单量较大的区间（超过平均值的1.5倍）
        if zones:
            avg_volume = np.mean([z['volume'] for z in zones])
            zones = [z for z in zones if z['volume'] > avg_volume * 1.5]

        return zones

    def find_target_liquidity_zone(self, orderbook: Dict, current_price: float,
                                    direction: str) -> Optional[Dict]:
        """
        查找目标方向的流动性密集区（用于止盈）

        策略：
        1. 在止盈方向查找多个流动性密集区
        2. 综合考虑距离和订单量，选择最佳的止盈位置
        3. 优先选择订单量大且距离合理的区域

        做多时：查找上方的卖单流动性密集区
        做空时：查找下方的买单流动性密集区

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
            target_zones = [z for z in liquidity_zones if z['type'] == 'sell' and z['price'] > current_price]

            if not target_zones:
                return None

            # 计算每个区域的得分（综合考虑订单量和距离）
            # 订单量越大越好，但太近或太远都不好
            scored_zones = []
            for zone in target_zones:
                distance = zone['distance']
                volume = zone['volume']

                # 距离得分：最佳距离是 0.5% - 3%
                if 0.5 <= distance <= 3.0:
                    distance_score = 1.0
                elif 0.3 <= distance <= 5.0:
                    distance_score = 0.7
                else:
                    distance_score = 0.4

                # 归一化订单量得分
                max_volume = max([z['volume'] for z in target_zones])
                volume_score = volume / max_volume if max_volume > 0 else 0

                # 综合得分（距离权重60%，订单量权重40%）
                total_score = distance_score * 0.6 + volume_score * 0.4

                scored_zones.append({
                    **zone,
                    'score': total_score
                })

            # 返回得分最高的区域
            if scored_zones:
                best_zone = max(scored_zones, key=lambda x: x['score'])
                return {
                    'price': best_zone['price'],
                    'distance': best_zone['distance'],
                    'volume': best_zone['volume'],
                    'score': best_zone['score'],
                    'reason': f'流动性密集区（订单量:{best_zone["volume"]:.0f}, 距离:{best_zone["distance"]:.2f}%, 得分:{best_zone["score"]:.2f}）'
                }

        elif direction == 'short':
            # 做空：查找下方的买单流动性密集区
            target_zones = [z for z in liquidity_zones if z['type'] == 'buy' and z['price'] < current_price]

            if not target_zones:
                return None

            # 计算每个区域的得分
            scored_zones = []
            for zone in target_zones:
                distance = abs(zone['distance'])
                volume = zone['volume']

                # 距离得分：最佳距离是 0.5% - 3%
                if 0.5 <= distance <= 3.0:
                    distance_score = 1.0
                elif 0.3 <= distance <= 5.0:
                    distance_score = 0.7
                else:
                    distance_score = 0.4

                # 归一化订单量得分
                max_volume = max([z['volume'] for z in target_zones])
                volume_score = volume / max_volume if max_volume > 0 else 0

                # 综合得分
                total_score = distance_score * 0.6 + volume_score * 0.4

                scored_zones.append({
                    **zone,
                    'score': total_score
                })

            # 返回得分最高的区域
            if scored_zones:
                best_zone = max(scored_zones, key=lambda x: x['score'])
                return {
                    'price': best_zone['price'],
                    'distance': abs(best_zone['distance']),
                    'volume': best_zone['volume'],
                    'score': best_zone['score'],
                    'reason': f'流动性密集区（订单量:{best_zone["volume"]:.0f}, 距离:{abs(best_zone["distance"]):.2f}%, 得分:{best_zone["score"]:.2f}）'
                }

        return None
