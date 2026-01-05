#!/usr/bin/env python3
"""
测试新功能脚本
测试杠杆、开仓比例和独立止损功能
"""

import sys
import os

# 添加src目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from storage.database.position_manager import PositionManager, PositionCreate, PositionUpdate
from storage.database.strategy_config_manager import StrategyConfigManager, StrategyConfigCreate
from storage.database.db import get_session
from storage.database.shared.model import Position, StrategyConfig
from interactive.market_interactive import MarketInteractive

def test_position_model():
    """测试仓位模型新字段"""
    print("\n=== 测试仓位模型新字段 ===")
    
    db = get_session()
    try:
        position_mgr = PositionManager()
        
        # 创建一个测试仓位
        position_create = PositionCreate(
            exchange='binance',
            symbol='BTC/USDT',
            side='long',
            entry_price=50000.0,
            quantity=0.1,
            leverage=5,  # 杠杆
            stop_loss_price=49000.0,  # 独立止损
            initial_balance=10000.0  # 初始余额
        )
        
        position = position_mgr.create_position(db, position_create)
        print(f"✓ 创建仓位成功，ID: {position.id}")
        print(f"  - 杠杆倍数: {position.leverage}x")
        print(f"  - 独立止损价格: ${position.stop_loss_price}")
        print(f"  - 初始余额: ${position.initial_balance}")
        
        # 测试更新独立止损
        updated_position = position_mgr.set_stop_loss(db, position.id, 48500.0)
        print(f"✓ 更新独立止损成功: ${updated_position.stop_loss_price}")
        
        # 清理测试数据
        db.delete(position)
        db.commit()
        print("✓ 清理测试数据完成")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_strategy_config_model():
    """测试策略配置模型新字段"""
    print("\n=== 测试策略配置模型新字段 ===")
    
    db = get_session()
    try:
        config_mgr = StrategyConfigManager()
        
        # 创建一个固定仓位配置
        config_create = StrategyConfigCreate(
            exchange='binance',
            symbol='BTC/USDT',
            long_threshold=0.02,
            short_threshold=0.02,
            stop_loss_ratio=0.05,
            position_size=1000.0,  # 固定仓位
            position_ratio=None,  # 不使用比例
            leverage=3
        )
        
        config = config_mgr.create_config(db, config_create)
        print(f"✓ 创建固定仓位配置成功，ID: {config.id}")
        print(f"  - 固定仓位大小: ${config.position_size}")
        print(f"  - 开仓比例: {config.position_ratio}")
        print(f"  - 杠杆倍数: {config.leverage}x")
        
        # 清理测试数据
        db.delete(config)
        db.commit()
        
        # 创建一个比例仓位配置
        config_create = StrategyConfigCreate(
            exchange='okx',
            symbol='ETH/USDT',
            long_threshold=0.03,
            short_threshold=0.03,
            stop_loss_ratio=0.08,
            position_size=None,  # 不使用固定仓位
            position_ratio=0.1,  # 使用比例
            leverage=5
        )
        
        config = config_mgr.create_config(db, config_create)
        print(f"✓ 创建比例仓位配置成功，ID: {config.id}")
        print(f"  - 固定仓位大小: {config.position_size}")
        print(f"  - 开仓比例: {config.position_ratio * 100}%")
        print(f"  - 杠杆倍数: {config.leverage}x")
        
        # 清理测试数据
        db.delete(config)
        db.commit()
        print("✓ 清理测试数据完成")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_trading_cost_calculation():
    """测试交易成本计算"""
    print("\n=== 测试交易成本计算 ===")
    
    try:
        current_price = 50000.0
        leverage = 5
        
        # 测试固定仓位模式
        print("\n--- 固定仓位模式 ---")
        cost_fixed = MarketInteractive.calculate_trading_cost(
            price=current_price,
            position_size=1000.0,
            leverage=leverage
        )
        print(f"✓ 固定仓位计算成功")
        print(f"  - 模式: {cost_fixed['mode']}")
        print(f"  - 实际仓位: ${cost_fixed['actual_position_size']:.2f}")
        print(f"  - 持仓数量: {cost_fixed['quantity']:.6f}")
        print(f"  - 开仓手续费: ${cost_fixed['open_fee']:.2f}")
        print(f"  - 保证金: ${cost_fixed['margin']:.2f}")
        print(f"  - 总成本: ${cost_fixed['total_cost']:.2f}")
        
        # 测试比例仓位模式
        print("\n--- 比例仓位模式 ---")
        current_balance = 10000.0
        position_ratio = 0.1
        
        cost_ratio = MarketInteractive.calculate_trading_cost(
            price=current_price,
            position_ratio=position_ratio,
            leverage=leverage,
            current_balance=current_balance
        )
        print(f"✓ 比例仓位计算成功")
        print(f"  - 模式: {cost_ratio['mode']}")
        print(f"  - 当前余额: ${current_balance:.2f}")
        print(f"  - 开仓比例: {position_ratio * 100}%")
        print(f"  - 实际仓位: ${cost_ratio['actual_position_size']:.2f}")
        print(f"  - 持仓数量: {cost_ratio['quantity']:.6f}")
        print(f"  - 开仓手续费: ${cost_ratio['open_fee']:.2f}")
        print(f"  - 保证金: ${cost_ratio['margin']:.2f}")
        print(f"  - 总成本: ${cost_ratio['total_cost']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("新功能测试")
    print("=" * 60)
    
    all_passed = True
    
    # 测试1: 仓位模型
    if not test_position_model():
        all_passed = False
    
    # 测试2: 策略配置模型
    if not test_strategy_config_model():
        all_passed = False
    
    # 测试3: 交易成本计算
    if not test_trading_cost_calculation():
        all_passed = False
    
    # 总结
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有测试通过！")
    else:
        print("✗ 部分测试失败！")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
