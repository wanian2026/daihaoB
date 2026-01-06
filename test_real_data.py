"""
测试真实数据模式的扫描功能
"""
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scanner.contract_scanner import ContractScanner

def test_real_data_scan():
    """测试真实数据扫描"""
    print("=" * 60)
    print("测试真实数据模式扫描功能")
    print("=" * 60)

    # 确保使用真实数据模式
    os.environ['USE_MOCK_EXCHANGE'] = 'false'

    # 创建扫描器
    scanner = ContractScanner('binance', timeframe='1h')

    # 扫描前10个合约
    print("\n开始扫描前10个合约...\n")
    signals = scanner.scan_contracts(limit=10)

    # 显示信号
    if signals:
        print(f"\n找到 {len(signals)} 个有效信号：\n")
        for i, signal in enumerate(signals, 1):
            print(f"信号 {i}:")
            print(f"  合约: {signal['symbol']}")
            print(f"  方向: {signal['direction']}")
            print(f"  入场价: {signal['entry_price']:.2f}")
            print(f"  止盈价: {signal['take_profit']:.2f}")
            print(f"  止损价: {signal['stop_loss']:.2f}")
            print(f"  止盈依据: {signal['take_profit_reason']}")
            print(f"  盈亏比: {signal['risk_reward_ratio']:.2f}")
            print(f"  信心度: {signal['confidence']:.1f}%")
            print(f"  原因: {signal['reason']}")
            print()
    else:
        print("\n未找到有效信号")

    # 显示流动性信息（第一个信号）
    if signals:
        signal = signals[0]
        print(f"\n详细流动性信息 ({signal['symbol']}):")
        liquidity_info = signal['liquidity_info']
        print(f"  买单量: {liquidity_info['bid_volume']:.2f}")
        print(f"  卖单量: {liquidity_info['ask_volume']:.2f}")
        print(f"  不平衡比例: {liquidity_info['imbalance_ratio']:.2%}")
        print(f"  流动性评分: {liquidity_info['liquidity_score']:.1f}")
        print(f"  深度比: {liquidity_info['depth_ratio']:.2%}")

        liquidity_zones = signal.get('liquidity_zones', [])
        if liquidity_zones:
            print(f"\n  流动性密集区 (前5个):")
            for zone in liquidity_zones[:5]:
                print(f"    {zone['type']}: 价格={zone['price']:.2f}, 订单量={zone['volume']:.2f}, 距离={zone['distance']:.2f}%")

if __name__ == '__main__':
    test_real_data_scan()
