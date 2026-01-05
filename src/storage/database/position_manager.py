from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from storage.database.shared.model import Position

# --- Pydantic Models ---
class PositionCreate(BaseModel):
    exchange: str = Field(..., description="交易所")
    symbol: str = Field(..., description="交易对")
    side: str = Field(..., description="方向：long/short")
    entry_price: float = Field(..., description="开仓价格")
    quantity: float = Field(..., description="持仓数量")

class PositionUpdate(BaseModel):
    current_price: Optional[float] = None
    status: Optional[str] = None
    pnl: Optional[float] = None
    is_stopped: Optional[bool] = None

# --- Manager Class ---
class PositionManager:
    """仓位管理类"""

    def create_position(self, db: Session, position_in: PositionCreate) -> Position:
        """创建新仓位"""
        db_position = Position(**position_in.model_dump())
        db.add(db_position)
        try:
            db.commit()
            db.refresh(db_position)
            return db_position
        except Exception:
            db.rollback()
            raise

    def get_open_positions(self, db: Session, exchange: str = None, symbol: str = None) -> List[Position]:
        """获取所有未平仓仓位"""
        query = db.query(Position).filter(Position.status == "open")
        if exchange:
            query = query.filter(Position.exchange == exchange)
        if symbol:
            query = query.filter(Position.symbol == symbol)
        return query.all()

    def get_position_by_id(self, db: Session, position_id: int) -> Optional[Position]:
        """根据ID获取仓位"""
        return db.query(Position).filter(Position.id == position_id).first()

    def update_position(self, db: Session, position_id: int, position_in: PositionUpdate) -> Optional[Position]:
        """更新仓位信息"""
        db_position = self.get_position_by_id(db, position_id)
        if not db_position:
            return None
        update_data = position_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_position, field):
                setattr(db_position, field, value)
        db.add(db_position)
        try:
            db.commit()
            db.refresh(db_position)
            return db_position
        except Exception:
            db.rollback()
            raise

    def close_position(self, db: Session, position_id: int, pnl: float = None, is_stopped: bool = False) -> Optional[Position]:
        """平仓"""
        db_position = self.get_position_by_id(db, position_id)
        if not db_position:
            return None
        db_position.status = "closed"
        db_position.pnl = pnl
        db_position.is_stopped = is_stopped
        from datetime import datetime
        db_position.closed_at = datetime.utcnow()
        db.add(db_position)
        try:
            db.commit()
            db.refresh(db_position)
            return db_position
        except Exception:
            db.rollback()
            raise

    def get_long_positions(self, db: Session, exchange: str, symbol: str) -> List[Position]:
        """获取多单仓位"""
        return db.query(Position).filter(
            Position.exchange == exchange,
            Position.symbol == symbol,
            Position.side == "long",
            Position.status == "open"
        ).all()

    def get_short_positions(self, db: Session, exchange: str, symbol: str) -> List[Position]:
        """获取空单仓位"""
        return db.query(Position).filter(
            Position.exchange == exchange,
            Position.symbol == symbol,
            Position.side == "short",
            Position.status == "open"
        ).all()
