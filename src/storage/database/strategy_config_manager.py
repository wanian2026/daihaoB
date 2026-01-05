from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from storage.database.shared.model import StrategyConfig

# --- Pydantic Models ---
class StrategyConfigCreate(BaseModel):
    exchange: str = Field(..., description="交易所")
    symbol: str = Field(..., description="交易对")
    long_threshold: float = Field(..., description="上涨阈值（百分比）")
    short_threshold: float = Field(..., description="下跌阈值（百分比）")
    stop_loss_ratio: float = Field(..., description="止损比例（百分比）")
    position_size: float = Field(..., description="仓位大小（USDT）")
    leverage: int = Field(1, description="杠杆倍数")
    is_active: bool = Field(True, description="是否启用")

class StrategyConfigUpdate(BaseModel):
    long_threshold: Optional[float] = None
    short_threshold: Optional[float] = None
    stop_loss_ratio: Optional[float] = None
    position_size: Optional[float] = None
    leverage: Optional[int] = None
    is_active: Optional[bool] = None

# --- Manager Class ---
class StrategyConfigManager:
    """策略配置管理类"""

    def create_config(self, db: Session, config_in: StrategyConfigCreate) -> StrategyConfig:
        """创建策略配置"""
        db_config = StrategyConfig(**config_in.model_dump())
        db.add(db_config)
        try:
            db.commit()
            db.refresh(db_config)
            return db_config
        except Exception:
            db.rollback()
            raise

    def get_config(self, db: Session, exchange: str, symbol: str) -> Optional[StrategyConfig]:
        """获取指定交易所和交易对的配置"""
        return db.query(StrategyConfig).filter(
            StrategyConfig.exchange == exchange,
            StrategyConfig.symbol == symbol
        ).first()

    def get_active_configs(self, db: Session) -> List[StrategyConfig]:
        """获取所有启用的配置"""
        return db.query(StrategyConfig).filter(StrategyConfig.is_active == True).all()

    def update_config(self, db: Session, exchange: str, symbol: str, 
                      config_in: StrategyConfigUpdate) -> Optional[StrategyConfig]:
        """更新策略配置"""
        db_config = self.get_config(db, exchange, symbol)
        if not db_config:
            return None
        update_data = config_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_config, field):
                setattr(db_config, field, value)
        db.add(db_config)
        try:
            db.commit()
            db.refresh(db_config)
            return db_config
        except Exception:
            db.rollback()
            raise

    def delete_config(self, db: Session, exchange: str, symbol: str) -> bool:
        """删除策略配置"""
        db_config = self.get_config(db, exchange, symbol)
        if not db_config:
            return False
        db.delete(db_config)
        db.commit()
        return True
