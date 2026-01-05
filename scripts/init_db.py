#!/usr/bin/env python3
"""
数据库初始化脚本
创建所有必要的表
"""

from storage.database.db import get_engine
from storage.database.shared.model import Base, Position, TradeLog, StrategyConfig

def init_db():
    """初始化数据库表"""
    engine = get_engine()
    
    print("正在创建数据库表...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    print("✓ 数据库表创建成功！")
    print("  - positions (仓位表)")
    print("  - trade_logs (交易日志表)")
    print("  - strategy_configs (策略配置表)")

if __name__ == "__main__":
    try:
        init_db()
    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
