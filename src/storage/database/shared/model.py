from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text, func
from typing import Optional

metadata = MetaData()

class Base(DeclarativeBase):
    pass

class Position(Base):
    """仓位表：存储多空持仓信息"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, comment="仓位ID")
    exchange = Column(String(50), nullable=False, index=True, comment="交易所：binance/okx")
    symbol = Column(String(50), nullable=False, index=True, comment="交易对：BTC/USDT")
    side = Column(String(10), nullable=False, index=True, comment="方向：long/short")
    entry_price = Column(Float, nullable=False, comment="开仓价格")
    current_price = Column(Float, nullable=True, comment="当前价格")
    quantity = Column(Float, nullable=False, comment="持仓数量")
    leverage = Column(Integer, nullable=False, default=1, comment="杠杆倍数")
    stop_loss_price = Column(Float, nullable=True, comment="独立止损价格（如果设置，优先使用此价格作为止损）")
    initial_balance = Column(Float, nullable=True, comment="开仓时的账户余额")
    status = Column(String(20), nullable=False, index=True, default="open", comment="状态：open/closed/stopped")
    pnl = Column(Float, nullable=True, comment="已实现盈亏")
    is_stopped = Column(Boolean, default=False, comment="是否已止损")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="开仓时间")
    closed_at = Column(DateTime(timezone=True), nullable=True, comment="平仓时间")
    
    __table_args__ = (
        {'comment': '仓位表'},
    )

class TradeLog(Base):
    """交易日志表：记录所有交易操作"""
    __tablename__ = "trade_logs"

    id = Column(Integer, primary_key=True, comment="日志ID")
    exchange = Column(String(50), nullable=False, index=True, comment="交易所")
    symbol = Column(String(50), nullable=False, index=True, comment="交易对")
    action = Column(String(20), nullable=False, index=True, comment="操作：open/close/stop_loss")
    side = Column(String(10), nullable=False, comment="方向：long/short")
    price = Column(Float, nullable=False, comment="成交价格")
    quantity = Column(Float, nullable=False, comment="成交数量")
    pnl = Column(Float, nullable=True, comment="盈亏")
    fee = Column(Float, nullable=True, comment="手续费")
    order_type = Column(String(20), nullable=True, comment="订单类型：market/limit")
    order_id = Column(String(100), nullable=True, comment="订单ID")
    meta = Column(JSON, nullable=True, comment="额外元数据")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="交易时间")

    __table_args__ = (
        {'comment': '交易日志表'},
    )

class StrategyConfig(Base):
    """策略配置表：存储策略参数"""
    __tablename__ = "strategy_configs"
    
    id = Column(Integer, primary_key=True, comment="配置ID")
    exchange = Column(String(50), nullable=False, unique=True, comment="交易所")
    symbol = Column(String(50), nullable=False, unique=True, comment="交易对")
    long_threshold = Column(Float, nullable=False, comment="上涨阈值（百分比，如0.02表示2%）")
    short_threshold = Column(Float, nullable=False, comment="下跌阈值（百分比）")
    stop_loss_ratio = Column(Float, nullable=False, comment="默认止损比例（百分比），可被仓位独立止损覆盖")
    position_size = Column(Float, nullable=True, comment="固定仓位大小（USDT），为空时使用开仓比例")
    position_ratio = Column(Float, nullable=True, comment="开仓比例（0-1之间，如0.1表示10%），每次开仓根据当前资金动态计算")
    leverage = Column(Integer, nullable=False, default=1, comment="杠杆倍数")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    __table_args__ = (
        {'comment': '策略配置表'},
    )

