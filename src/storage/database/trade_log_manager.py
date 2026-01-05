from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from storage.database.shared.model import TradeLog

# --- Pydantic Models ---
class TradeLogCreate(BaseModel):
    exchange: str = Field(..., description="交易所")
    symbol: str = Field(..., description="交易对")
    action: str = Field(..., description="操作：open/close/stop_loss")
    side: str = Field(..., description="方向：long/short")
    price: float = Field(..., description="成交价格")
    quantity: float = Field(..., description="成交数量")
    pnl: Optional[float] = Field(None, description="盈亏")
    fee: Optional[float] = Field(None, description="手续费")
    order_type: Optional[str] = Field(None, description="订单类型：market/limit")
    order_id: Optional[str] = Field(None, description="订单ID")
    meta: Optional[dict] = Field(None, description="额外元数据")

# --- Manager Class ---
class TradeLogManager:
    """交易日志管理类"""

    def create_trade_log(self, db: Session, log_in: TradeLogCreate) -> TradeLog:
        """创建交易日志"""
        db_log = TradeLog(**log_in.model_dump())
        db.add(db_log)
        try:
            db.commit()
            db.refresh(db_log)
            return db_log
        except Exception:
            db.rollback()
            raise

    def get_trade_logs(self, db: Session, exchange: str = None, symbol: str = None, 
                       action: str = None, limit: int = 100) -> List[TradeLog]:
        """查询交易日志"""
        query = db.query(TradeLog)
        if exchange:
            query = query.filter(TradeLog.exchange == exchange)
        if symbol:
            query = query.filter(TradeLog.symbol == symbol)
        if action:
            query = query.filter(TradeLog.action == action)
        return query.order_by(TradeLog.created_at.desc()).limit(limit).all()

    def get_trade_logs_by_position(self, db: Session, position_id: int, limit: int = 100) -> List[TradeLog]:
        """根据仓位ID查询相关交易日志"""
        return db.query(TradeLog).filter(
            TradeLog.meta['position_id'].astext == str(position_id)
        ).order_by(TradeLog.created_at.desc()).limit(limit).all()

    def get_recent_trades(self, db: Session, limit: int = 100) -> List[TradeLog]:
        """获取最近的交易日志"""
        return db.query(TradeLog).order_by(TradeLog.created_at.desc()).limit(limit).all()

    def get_total_trades(self, db: Session) -> int:
        """获取总交易次数"""
        return db.query(TradeLog).count()

    def get_total_pnl(self, db: Session) -> float:
        """获取总盈亏"""
        result = db.query(func.sum(TradeLog.pnl)).filter(TradeLog.pnl.isnot(None)).scalar()
        return result if result else 0.0

    def get_win_rate(self, db: Session) -> float:
        """获取胜率"""
        total_trades = self.get_total_trades(db)
        if total_trades == 0:
            return 0.0
        winning_trades = db.query(TradeLog).filter(TradeLog.pnl > 0).count()
        return winning_trades / total_trades
