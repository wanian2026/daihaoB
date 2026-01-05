import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from exchanges.base_exchange import BaseExchange
from storage.database.db import get_session
from storage.database.position_manager import PositionManager, PositionCreate, PositionUpdate
from storage.database.trade_log_manager import TradeLogManager, TradeLogCreate
from storage.database.strategy_config_manager import StrategyConfigManager, StrategyConfigCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingEngine:
    """交易策略核心引擎"""

    def __init__(self, exchange: BaseExchange, symbol: str, 
                 long_threshold: float, short_threshold: float, 
                 stop_loss_ratio: float, position_size: Optional[float] = None, 
                 position_ratio: Optional[float] = None, leverage: int = 1):
        """
        初始化交易引擎
        :param exchange: 交易所实例
        :param symbol: 交易对
        :param long_threshold: 上涨阈值（百分比）
        :param short_threshold: 下跌阈值（百分比）
        :param stop_loss_ratio: 默认止损比例（百分比）
        :param position_size: 固定仓位大小（USDT），与position_ratio二选一
        :param position_ratio: 开仓比例（0-1），每次开仓根据当前资金动态计算，与position_size二选一
        :param leverage: 杠杆倍数
        """
        self.exchange = exchange
        self.symbol = symbol
        self.long_threshold = long_threshold
        self.short_threshold = short_threshold
        self.stop_loss_ratio = stop_loss_ratio
        self.position_size = position_size
        self.position_ratio = position_ratio
        self.leverage = leverage
        self.running = False

        # 数据库管理器
        self.position_mgr = PositionManager()
        self.trade_log_mgr = TradeLogManager()
        self.strategy_config_mgr = StrategyConfigManager()

    def initialize_strategy(self, db: Session):
        """初始化策略：开一个多单和一个空单"""
        logger.info(f"初始化策略，交易对: {self.symbol}")

        # 获取当前价格
        ticker = self.exchange.get_ticker(self.symbol)
        current_price = ticker.price
        logger.info(f"当前价格: {current_price}")

        # 获取当前余额（用于动态计算）
        balance_info = self.exchange.get_balance()
        current_balance = balance_info.get('USDT', {}).get('free', 0)
        logger.info(f"当前账户余额: {current_balance} USDT")

        # 计算开仓数量
        quantity = self._calculate_quantity(current_price, current_balance)
        logger.info(f"开仓数量: {quantity}")

        # 开多单
        try:
            long_order = self.exchange.create_order(
                self.symbol, 'buy', 'market', quantity
            )
            logger.info(f"开多单成功: 价格={long_order.price}, 数量={long_order.quantity}")

            # 记录到数据库
            db_position = self.position_mgr.create_position(db, PositionCreate(
                exchange=self.exchange.get_exchange_name(),
                symbol=self.symbol,
                side='long',
                entry_price=long_order.price,
                quantity=long_order.quantity
            ))

            # 更新额外字段（杠杆、初始余额）
            db_position.leverage = self.leverage
            db_position.initial_balance = current_balance
            db.commit()

            # 记录交易日志
            self.trade_log_mgr.create_trade_log(db, TradeLogCreate(
                exchange=self.exchange.get_exchange_name(),
                symbol=self.symbol,
                action='open',
                side='long',
                price=long_order.price,
                quantity=long_order.quantity,
                order_id=long_order.order_id,
                meta={'position_id': db_position.id, 'leverage': self.leverage}
            ))

        except Exception as e:
            logger.error(f"开多单失败: {e}")
            raise

        # 开空单
        try:
            short_order = self.exchange.create_order(
                self.symbol, 'sell', 'market', quantity
            )
            logger.info(f"开空单成功: 价格={short_order.price}, 数量={short_order.quantity}")

            # 记录到数据库
            db_position = self.position_mgr.create_position(db, PositionCreate(
                exchange=self.exchange.get_exchange_name(),
                symbol=self.symbol,
                side='short',
                entry_price=short_order.price,
                quantity=short_order.quantity
            ))

            # 更新额外字段（杠杆、初始余额）
            db_position.leverage = self.leverage
            db_position.initial_balance = current_balance
            db.commit()

            # 记录交易日志
            self.trade_log_mgr.create_trade_log(db, TradeLogCreate(
                exchange=self.exchange.get_exchange_name(),
                symbol=self.symbol,
                action='open',
                side='short',
                price=short_order.price,
                quantity=short_order.quantity,
                order_id=short_order.order_id,
                meta={'position_id': db_position.id, 'leverage': self.leverage}
            ))

        except Exception as e:
            logger.error(f"开空单失败: {e}")
            raise

        logger.info("策略初始化完成")

    def _calculate_quantity(self, price: float, current_balance: float = None) -> float:
        """
        计算开仓数量
        :param price: 当前价格
        :param current_balance: 当前账户余额（如果使用比例模式则必填）
        :return: 开仓数量
        """
        if self.position_size:
            # 固定仓位模式
            quantity = self.position_size / price
        else:
            # 比例模式：动态计算
            if current_balance is None:
                balance_info = self.exchange.get_balance()
                current_balance = balance_info.get('USDT', {}).get('free', 0)
            
            quantity = (current_balance * self.position_ratio) / price
            logger.info(f"动态开仓: 当前余额={current_balance} USDT, 比例={self.position_ratio}, 数量={quantity}")
        
        # 应用杠杆
        quantity = quantity * self.leverage
        logger.info(f"应用杠杆 {self.leverage}x 后数量: {quantity}")
        
        return quantity

    def run(self, db: Session, interval: int = 1):
        """
        运行策略主循环
        :param db: 数据库会话
        :param interval: 监控间隔（秒）
        """
        self.running = True
        logger.info(f"开始运行策略，监控间隔: {interval}秒")

        try:
            while self.running:
                # 获取当前价格
                ticker = self.exchange.get_ticker(self.symbol)
                current_price = ticker.price
                logger.info(f"当前价格: {current_price}")

                # 获取所有未平仓的仓位
                positions = self.position_mgr.get_open_positions(
                    db, self.exchange.get_exchange_name(), self.symbol
                )

                # 处理每个仓位
                for position in positions:
                    self._check_position(db, position, current_price)

                # 等待下一次检查
                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("收到停止信号")
        except Exception as e:
            logger.error(f"策略运行异常: {e}")
            raise
        finally:
            self.running = False
            logger.info("策略已停止")

    def _check_position(self, db: Session, position, current_price: float):
        """
        检查仓位状态（上涨触发、下跌触发、止损）
        """
        entry_price = position.entry_price
        side = position.side

        # 更新当前价格
        self.position_mgr.update_position(db, position.id, PositionUpdate(current_price=current_price))

        if side == 'long':
            # 多单逻辑
            self._check_long_position(db, position, current_price, entry_price)
        else:
            # 空单逻辑
            self._check_short_position(db, position, current_price, entry_price)

    def _check_long_position(self, db: Session, position, current_price: float, entry_price: float):
        """检查多单"""
        # 止损检查：优先使用独立止损价格
        if position.stop_loss_price:
            stop_loss_price = position.stop_loss_price
            if current_price <= stop_loss_price:
                logger.warning(f"多单触发独立止损: entry={entry_price}, current={current_price}, stop_loss={stop_loss_price}")
                self._close_position(db, position, current_price, 'stop_loss')
                return
        else:
            # 使用默认止损比例
            stop_loss_price = entry_price * (1 - self.stop_loss_ratio)
            if current_price <= stop_loss_price:
                logger.warning(f"多单触发默认止损: entry={entry_price}, current={current_price}, stop_loss={stop_loss_price}")
                self._close_position(db, position, current_price, 'stop_loss')
                return

        # 上涨触发检查
        trigger_price = entry_price * (1 + self.long_threshold)
        if current_price >= trigger_price:
            logger.info(f"多单触发上涨阈值: entry={entry_price}, current={current_price}, trigger={trigger_price}")
            # 平仓
            self._close_position(db, position, current_price, 'close')
            # 开新多单
            self._open_new_long_position(db, current_price)

    def _check_short_position(self, db: Session, position, current_price: float, entry_price: float):
        """检查空单"""
        # 止损检查：优先使用独立止损价格
        if position.stop_loss_price:
            stop_loss_price = position.stop_loss_price
            if current_price >= stop_loss_price:
                logger.warning(f"空单触发独立止损: entry={entry_price}, current={current_price}, stop_loss={stop_loss_price}")
                self._close_position(db, position, current_price, 'stop_loss')
                return
        else:
            # 使用默认止损比例
            stop_loss_price = entry_price * (1 + self.stop_loss_ratio)
            if current_price >= stop_loss_price:
                logger.warning(f"空单触发默认止损: entry={entry_price}, current={current_price}, stop_loss={stop_loss_price}")
                self._close_position(db, position, current_price, 'stop_loss')
                return

        # 下跌触发检查
        trigger_price = entry_price * (1 - self.short_threshold)
        if current_price <= trigger_price:
            logger.info(f"空单触发下跌阈值: entry={entry_price}, current={current_price}, trigger={trigger_price}")
            # 平仓
            self._close_position(db, position, current_price, 'close')
            # 开新空单
            self._open_new_short_position(db, current_price)

    def _close_position(self, db: Session, position, current_price: float, action: str):
        """
        平仓
        :param db: 数据库会话
        :param position: 仓位对象
        :param current_price: 当前价格
        :param action: 动作 (close/stop_loss)
        """
        logger.info(f"平仓: side={position.side}, entry={position.entry_price}, current={current_price}")

        try:
            # 执行平仓操作
            close_order = self.exchange.close_position(
                self.symbol, position.side, position.quantity
            )

            # 计算盈亏
            if position.side == 'long':
                pnl = (current_price - position.entry_price) * position.quantity
            else:
                pnl = (position.entry_price - current_price) * position.quantity

            # 更新仓位状态
            is_stopped = (action == 'stop_loss')
            self.position_mgr.close_position(db, position.id, pnl, is_stopped)

            # 记录交易日志
            self.trade_log_mgr.create_trade_log(db, TradeLogCreate(
                exchange=self.exchange.get_exchange_name(),
                symbol=self.symbol,
                action=action,
                side=position.side,
                price=current_price,
                quantity=position.quantity,
                pnl=pnl,
                order_id=close_order.order_id,
                meta={'position_id': position.id}
            ))

            logger.info(f"平仓成功: pnl={pnl}, is_stopped={is_stopped}")

        except Exception as e:
            logger.error(f"平仓失败: {e}")
            raise

    def _open_new_long_position(self, db: Session, current_price: float):
        """开新多单"""
        logger.info(f"开新多单: price={current_price}")
        
        # 获取当前余额用于动态计算
        balance_info = self.exchange.get_balance()
        current_balance = balance_info.get('USDT', {}).get('free', 0)
        
        quantity = self._calculate_quantity(current_price, current_balance)

        try:
            order = self.exchange.create_order(self.symbol, 'buy', 'market', quantity)
            logger.info(f"开新多单成功: price={order.price}, quantity={order.quantity}")

            # 记录到数据库
            db_position = self.position_mgr.create_position(db, PositionCreate(
                exchange=self.exchange.get_exchange_name(),
                symbol=self.symbol,
                side='long',
                entry_price=order.price,
                quantity=order.quantity
            ))

            # 更新额外字段（杠杆、初始余额）
            db_position.leverage = self.leverage
            db_position.initial_balance = current_balance
            db.commit()

            # 记录交易日志
            self.trade_log_mgr.create_trade_log(db, TradeLogCreate(
                exchange=self.exchange.get_exchange_name(),
                symbol=self.symbol,
                action='open',
                side='long',
                price=order.price,
                quantity=order.quantity,
                order_id=order.order_id,
                meta={'position_id': db_position.id, 'leverage': self.leverage, 'initial_balance': current_balance}
            ))

        except Exception as e:
            logger.error(f"开新多单失败: {e}")

    def _open_new_short_position(self, db: Session, current_price: float):
        """开新空单"""
        logger.info(f"开新空单: price={current_price}")
        
        # 获取当前余额用于动态计算
        balance_info = self.exchange.get_balance()
        current_balance = balance_info.get('USDT', {}).get('free', 0)
        
        quantity = self._calculate_quantity(current_price, current_balance)

        try:
            order = self.exchange.create_order(self.symbol, 'sell', 'market', quantity)
            logger.info(f"开新空单成功: price={order.price}, quantity={order.quantity}")

            # 记录到数据库
            db_position = self.position_mgr.create_position(db, PositionCreate(
                exchange=self.exchange.get_exchange_name(),
                symbol=self.symbol,
                side='short',
                entry_price=order.price,
                quantity=order.quantity
            ))

            # 更新额外字段（杠杆、初始余额）
            db_position.leverage = self.leverage
            db_position.initial_balance = current_balance
            db.commit()

            # 记录交易日志
            self.trade_log_mgr.create_trade_log(db, TradeLogCreate(
                exchange=self.exchange.get_exchange_name(),
                symbol=self.symbol,
                action='open',
                side='short',
                price=order.price,
                quantity=order.quantity,
                order_id=order.order_id,
                meta={'position_id': db_position.id, 'leverage': self.leverage, 'initial_balance': current_balance}
            ))

        except Exception as e:
            logger.error(f"开新空单失败: {e}")

    def stop(self):
        """停止策略"""
        logger.info("正在停止策略...")
        self.running = False
