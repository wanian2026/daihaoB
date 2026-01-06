"""
测试改进后的流动性密集区查找和止盈计算逻辑
"""
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from analysis.liquidity import LiquidityAnalyzer
from analysis.signal import SignalGenerator

def test_liquidity_zones():
    """测试流动性密集区查找"""
    print("=" * 60)
    print("测试流动性密集区查找算法")
    print("=" * 60)

    analyzer = LiquidityAnalyzer()

    # 创建模拟订单簿数据
    # 当前价格 100
    current_price = 100.0

    # 买单（下方）- 创建几个密集区
    bids = [
        [99.5, 100],   # 密集区1的开始
        [99.4, 150],
        [99.3, 200],
        [99.2, 250],
        [99.1, 300],   # 密集区1结束，总订单量 1000
        [99.0, 50],
        [98.9, 40],
        [98.8, 30],
        [98.7, 20],
        [98.6, 10],
        [98.5, 80],
        [98.4, 90],
        [98.3, 100],
        [98.2, 110],
        [98.1, 120],   # 密集区2，总订单量 500
        [98.0, 20],
    ]

    # 卖单（上方）- 创建几个密集区
    asks = [
        [100.1, 30],
        [100.2, 40],
        [100.3, 50],
        [100.4, 60],
        [100.5, 70],
        [100.6, 100],
        [100.7, 150],
        [100.8, 200],
        [100.9, 250],
        [101.0, 300],   # 密集区1，总订单量 1000
        [101.1, 40],
        [101.2, 30],
        [101.3, 20],
        [101.4, 60],
        [101.5, 80],
        [101.6, 100],
        [101.7, 120],
        [101.8, 140],
        [101.9, 160],
        [102.0, 180],   # 密集区2，总订单量 840
        [102.1, 20],
    ]

    orderbook = {
        'bids': bids,
        'asks': asks
    }

    # 查找流动性密集区
    liquidity_zones = analyzer.find_liquidity_zones(orderbook, current_price)

    print(f"\n找到 {len(liquidity_zones)} 个流动性密集区：\n")

    for i, zone in enumerate(liquidity_zones, 1):
        print(f"区域 {i}:")
        print(f"  类型: {zone['type']}")
        print(f"  价格: {zone['price']:.2f}")
        print(f"  订单量: {zone['volume']:.2f}")
        print(f"  距离: {zone['distance']:.2f}%")
        print()

    # 测试做多时的止盈选择
    print("=" * 60)
    print("测试做多时的止盈选择")
    print("=" * 60)

    target_zone_long = analyzer.find_target_liquidity_zone(orderbook, current_price, 'long')

    if target_zone_long:
        print(f"\n做多止盈目标：")
        print(f"  价格: {target_zone_long['price']:.2f}")
        print(f"  距离: {target_zone_long['distance']:.2f}%")
        print(f"  订单量: {target_zone_long['volume']:.2f}")
        print(f"  得分: {target_zone_long['score']:.2f}")
        print(f"  原因: {target_zone_long['reason']}\n")
    else:
        print("\n未找到合适的做多止盈目标\n")

    # 测试做空时的止盈选择
    print("=" * 60)
    print("测试做空时的止盈选择")
    print("=" * 60)

    target_zone_short = analyzer.find_target_liquidity_zone(orderbook, current_price, 'short')

    if target_zone_short:
        print(f"\n做空止盈目标：")
        print(f"  价格: {target_zone_short['price']:.2f}")
        print(f"  距离: {target_zone_short['distance']:.2f}%")
        print(f"  订单量: {target_zone_short['volume']:.2f}")
        print(f"  得分: {target_zone_short['score']:.2f}")
        print(f"  原因: {target_zone_short['reason']}\n")
    else:
        print("\n未找到合适的做空止盈目标\n")

def test_atr_calculation():
    """测试ATR计算"""
    print("=" * 60)
    print("测试ATR计算")
    print("=" * 60)

    generator = SignalGenerator()

    # 创建模拟K线数据
    # [timestamp, open, high, low, close, volume]
    ohlcv = [
        [1700000000000, 100, 102, 99, 101, 1000],
        [1700000036000, 101, 104, 100, 103, 1100],
        [1700000072000, 103, 105, 101, 104, 1200],
        [1700000108000, 104, 107, 103, 106, 1300],
        [1700000144000, 106, 108, 105, 107, 1400],
        [1700000180000, 107, 110, 106, 109, 1500],
        [1700000216000, 109, 112, 108, 111, 1600],
        [1700000252000, 111, 114, 110, 113, 1700],
        [1700000288000, 113, 115, 112, 114, 1800],
        [1700000324000, 114, 117, 113, 116, 1900],
        [1700000360000, 116, 118, 115, 117, 2000],
        [1700000396000, 117, 120, 116, 119, 2100],
        [1700000432000, 119, 122, 118, 121, 2200],
        [1700000468000, 121, 124, 120, 123, 2300],
        [1700000504000, 123, 125, 122, 124, 2400],
        [1700000540000, 124, 127, 123, 126, 2500],
        [1700000576000, 126, 128, 125, 127, 2600],
        [1700000612000, 127, 130, 126, 129, 2700],
        [1700000648000, 129, 132, 128, 131, 2800],
        [1700000684000, 131, 133, 130, 132, 2900],
    ]

    atr = generator._calculate_atr(ohlcv, period=14)

    print(f"\nATR值（14周期）: {atr:.4f}\n")

    # 说明如何使用ATR
    if atr:
        entry_price = 100.0
        stop_loss = 99.0
        risk = entry_price - stop_loss

        take_profit_atr = entry_price + atr * 2.5
        take_profit_ratio = entry_price + risk * 2.5

        print(f"入场价: {entry_price:.2f}")
        print(f"止损价: {stop_loss:.2f}")
        print(f"风险: {risk:.2f}")
        print(f"\n止盈方案对比：")
        print(f"  基于ATR (2.5倍): {take_profit_atr:.2f} (距离 {take_profit_atr - entry_price:.2f})")
        print(f"  基于盈亏比 (2.5:1): {take_profit_ratio:.2f} (距离 {take_profit_ratio - entry_price:.2f})")
        print()

if __name__ == '__main__':
    test_liquidity_zones()
    test_atr_calculation()
