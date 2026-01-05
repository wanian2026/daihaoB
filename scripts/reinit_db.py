#!/usr/bin/env python3
"""
数据库重新初始化脚本
删除所有表并重新创建（用于开发环境）
"""

import sys
import os

# 添加src目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from storage.database.db import get_engine
from storage.database.shared.model import Base

def reinit_db():
    """重新初始化数据库表"""
    engine = get_engine()
    
    print("警告：这将删除所有现有数据！")
    confirm = input("确认删除并重新创建所有表？(yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("操作已取消")
        return
    
    print("\n正在删除所有表...")
    Base.metadata.drop_all(bind=engine)
    
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    
    print("✓ 数据库表重新创建成功！")
    print("  - positions (仓位表)")
    print("  - trade_logs (交易日志表)")
    print("  - strategy_configs (策略配置表)")

if __name__ == "__main__":
    try:
        reinit_db()
    except Exception as e:
        print(f"✗ 数据库重新初始化失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
