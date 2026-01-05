"""
Web管理界面API
提供交易系统的完整Web接口
"""

import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from exchanges import ExchangeFactory
from strategy import TradingEngine
from storage.database.db import get_session
from storage.database.strategy_config_manager import StrategyConfigManager
from storage.database.trade_log_manager import TradeLogManager
from storage.database.position_manager import PositionManager
from utils.indicators import TechnicalIndicators

# 创建FastAPI应用
app = FastAPI(
    title="加密货币交易系统API",
    description="提供完整的交易系统管理接口",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# 全局交易引擎实例
trading_engine: Optional[TradingEngine] = None

# ========== 数据模型 ==========

class ExchangeConfig(BaseModel):
    exchange: str
    testnet: bool
    api_key: str
    secret: str
    password: Optional[str] = None

class StrategyConfig(BaseModel):
    exchange: str
    symbol: str
    long_threshold: float
    short_threshold: float
    stop_loss_ratio: float
    position_size: Optional[float] = None
    position_ratio: Optional[float] = None
    leverage: int = 1

class TradingControl(BaseModel):
    action: str  # start, stop, pause, resume

# ========== 主页路由 ==========

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回主页"""
    with open("web/index.html", "r", encoding="utf-8") as f:
        return f.read()

# ========== 交易所接口 ==========

@app.post("/api/exchange/test")
async def test_exchange_connection(config: ExchangeConfig):
    """测试交易所连接"""
    try:
        exchange = ExchangeFactory.create_exchange(
            config.exchange,
            config.api_key,
            config.secret,
            config.password,
            config.testnet
        )
        balance = exchange.get_balance()
        return {
            "success": True,
            "message": "连接成功",
            "balance": balance.get('USDT', {}).get('free', 0)
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.get("/api/exchange/api-config")
async def get_api_config():
    """获取API配置"""
    try:
        import os
        config_path = os.path.join(os.path.dirname(__file__), "../../config/api_keys.json")

        # 检查文件是否存在
        if not os.path.exists(config_path):
            return {
                "success": True,
                "config": None
            }

        with open(config_path, 'r', encoding='utf-8') as f:
            api_keys = json.load(f)

        # 返回第一个配置（OKX优先）
        if 'exchanges' in api_keys and api_keys['exchanges']:
            for exchange_name in ['okx', 'binance']:
                if exchange_name in api_keys['exchanges']:
                    exchange_data = api_keys['exchanges'][exchange_name]
                    return {
                        "success": True,
                        "config": {
                            "exchange": exchange_name,
                            "testnet": exchange_data.get('testnet', True),
                            "api_key": exchange_data.get('api_key', ''),
                            "secret": '',
                            "password": ''
                        }
                    }

        return {
            "success": True,
            "config": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.post("/api/exchange/api-config")
async def save_api_config(config: ExchangeConfig):
    """保存API配置"""
    try:
        import os
        config_path = os.path.join(os.path.dirname(__file__), "../../config/api_keys.json")

        # 读取现有配置
        existing_config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)

        # 更新配置
        if 'exchanges' not in existing_config:
            existing_config['exchanges'] = {}

        existing_config['exchanges'][config.exchange] = {
            'api_key': config.api_key,
            'secret': config.secret,
            'testnet': config.testnet
        }

        # OKX需要password
        if config.exchange == 'okx' and config.password:
            existing_config['exchanges']['okx']['password'] = config.password

        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, indent=2, ensure_ascii=False)

        return {
            "success": True,
            "message": "API配置保存成功"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.get("/api/exchange/ticker/{exchange_name}/{symbol}")
async def get_ticker(exchange_name: str, symbol: str):
    """获取当前价格"""
    try:
        # 从配置中获取API密钥
        db = get_session()
        config_mgr = StrategyConfigManager()
        configs = config_mgr.list_configs(db)
        api_key = None
        secret = None
        passphrase = None
        sandbox = True

        for cfg in configs:
            if cfg.exchange == exchange_name:
                # 从配置文件读取API密钥
                import os
                config_path = os.path.join(os.path.dirname(__file__), "../../config/api_keys.json")
                with open(config_path, 'r', encoding='utf-8') as f:
                    api_keys = json.load(f)
                    if exchange_name in api_keys.get('exchanges', {}):
                        exchange_data = api_keys['exchanges'][exchange_name]
                        api_key = exchange_data.get('api_key')
                        secret = exchange_data.get('secret')
                        passphrase = exchange_data.get('password')
                        sandbox = exchange_data.get('testnet', True)
                break

        if not api_key:
            # 如果没有配置，返回模拟数据
            import random
            base_prices = {
                'BTC/USDT': 95000,
                'ETH/USDT': 3300,
                'BNB/USDT': 680,
                'SOL/USDT': 210
            }
            base_price = base_prices.get(symbol, 100)
            change = random.uniform(-500, 500)
            change_percent = (change / base_price) * 100

            return {
                "success": True,
                "price": base_price + change,
                "change": change,
                "percentage": change_percent,
                "volume": random.uniform(1000000, 50000000),
                "timestamp": datetime.now().isoformat(),
                "ticker": {
                    "last": base_price + change,
                    "change": change,
                    "percentage": change_percent,
                    "volume": random.uniform(1000000, 50000000)
                }
            }

        exchange = ExchangeFactory.create_exchange(
            exchange_name, api_key, secret, passphrase, sandbox
        )
        ticker = exchange.get_ticker(symbol)
        return {
            "success": True,
            "price": ticker.price,
            "change": ticker.change,
            "percentage": ticker.change_percent,
            "volume": ticker.volume,
            "timestamp": ticker.timestamp,
            "ticker": {
                "last": ticker.price,
                "change": ticker.change,
                "percentage": ticker.change_percent,
                "volume": ticker.volume
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.get("/api/exchange/balance/{exchange_name}")
async def get_balance(exchange_name: str):
    """获取账户余额"""
    try:
        db = get_session()
        config_mgr = StrategyConfigManager()
        configs = config_mgr.list_configs(db)
        api_key = None
        secret = None
        passphrase = None
        sandbox = True

        for cfg in configs:
            if cfg.exchange == exchange_name:
                import os
                config_path = os.path.join(os.path.dirname(__file__), "../../config/api_keys.json")
                with open(config_path, 'r') as f:
                    api_keys = json.load(f)
                    if exchange_name in api_keys['exchanges']:
                        api_key = api_keys['exchanges'][exchange_name]['api_key']
                        secret = api_keys['exchanges'][exchange_name]['secret']
                        passphrase = api_keys['exchanges'][exchange_name].get('passphrase')
                        sandbox = api_keys['exchanges'][exchange_name].get('sandbox', True)
                break

        if not api_key:
            raise HTTPException(status_code=404, detail="未找到交易所配置")

        exchange = ExchangeFactory.create_exchange(
            exchange_name, api_key, secret, passphrase, sandbox
        )
        balance = exchange.get_balance()
        return {
            "success": True,
            "balance": balance
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

# ========== 策略配置接口 ==========

@app.get("/api/strategy/configs")
async def list_strategy_configs():
    """获取所有策略配置"""
    try:
        db = get_session()
        config_mgr = StrategyConfigManager()
        configs = config_mgr.list_configs(db)
        return {
            "success": True,
            "configs": [
                {
                    "id": cfg.id,
                    "exchange": cfg.exchange,
                    "symbol": cfg.symbol,
                    "long_threshold": cfg.long_threshold,
                    "short_threshold": cfg.short_threshold,
                    "stop_loss_ratio": cfg.stop_loss_ratio,
                    "position_size": cfg.position_size,
                    "position_ratio": cfg.position_ratio,
                    "leverage": cfg.leverage,
                    "created_at": cfg.created_at.isoformat() if cfg.created_at else None
                }
                for cfg in configs
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.post("/api/strategy/config")
async def create_strategy_config(config: StrategyConfig):
    """创建策略配置"""
    try:
        db = get_session()
        config_mgr = StrategyConfigManager()

        from storage.database.strategy_config_manager import StrategyConfigCreate
        config_mgr.create_config(db, StrategyConfigCreate(
            exchange=config.exchange,
            symbol=config.symbol,
            long_threshold=config.long_threshold,
            short_threshold=config.short_threshold,
            stop_loss_ratio=config.stop_loss_ratio,
            position_size=config.position_size,
            position_ratio=config.position_ratio,
            leverage=config.leverage
        ))

        return {
            "success": True,
            "message": "配置保存成功"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.delete("/api/strategy/config/{config_id}")
async def delete_strategy_config(config_id: int):
    """删除策略配置"""
    try:
        db = get_session()
        config_mgr = StrategyConfigManager()
        config_mgr.delete_config(db, config_id)
        return {
            "success": True,
            "message": "配置删除成功"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

# ========== 交易控制接口 ==========

@app.post("/api/trading/control")
async def trading_control(control: TradingControl):
    """控制交易（启动/停止/暂停/恢复）"""
    global trading_engine

    try:
        if control.action == "start":
            # 从数据库获取最新配置启动交易
            db = get_session()
            config_mgr = StrategyConfigManager()
            configs = config_mgr.list_configs(db)

            if not configs:
                return {
                    "success": False,
                    "message": "未找到策略配置，请先配置"
                }

            cfg = configs[0]

            # 获取交易所
            import os
            config_path = os.path.join(os.path.dirname(__file__), "../../config/api_keys.json")
            with open(config_path, 'r') as f:
                api_keys = json.load(f)
                exchange_config = api_keys['exchanges'][cfg.exchange]
                exchange = ExchangeFactory.create_exchange(
                    cfg.exchange,
                    exchange_config['api_key'],
                    exchange_config['secret'],
                    exchange_config.get('passphrase'),
                    exchange_config.get('sandbox', True)
                )

            # 创建交易引擎
            trading_engine = TradingEngine(
                exchange=exchange,
                symbol=cfg.symbol,
                long_threshold=cfg.long_threshold,
                short_threshold=cfg.short_threshold,
                stop_loss_ratio=cfg.stop_loss_ratio,
                position_size=cfg.position_size,
                position_ratio=cfg.position_ratio,
                leverage=cfg.leverage
            )

            # 初始化并启动
            trading_engine.initialize_strategy(db)

            # 在后台运行
            asyncio.create_task(run_trading(trading_engine, db))

            return {
                "success": True,
                "message": "交易已启动"
            }

        elif control.action == "stop":
            if trading_engine:
                trading_engine.stop()
                trading_engine = None
                return {
                    "success": True,
                    "message": "交易已停止"
                }
            else:
                return {
                    "success": False,
                    "message": "没有运行中的交易"
                }

        elif control.action == "pause":
            if trading_engine:
                trading_engine.pause()
                return {
                    "success": True,
                    "message": "交易已暂停"
                }
            else:
                return {
                    "success": False,
                    "message": "没有运行中的交易"
                }

        elif control.action == "resume":
            if trading_engine:
                trading_engine.resume()
                return {
                    "success": True,
                    "message": "交易已恢复"
                }
            else:
                return {
                    "success": False,
                    "message": "没有运行中的交易"
                }

        else:
            return {
                "success": False,
                "message": "无效的操作"
            }

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

async def run_trading(engine: TradingEngine, db):
    """后台运行交易"""
    try:
        await engine.run_async(db, interval=1)
    except Exception as e:
        print(f"交易运行错误: {e}")

@app.get("/api/trading/status")
async def get_trading_status():
    """获取交易状态"""
    global trading_engine

    if trading_engine:
        return {
            "success": True,
            "status": "running",
            "is_paused": trading_engine.is_paused
        }
    else:
        return {
            "success": True,
            "status": "stopped",
            "is_paused": False
        }

# ========== 持仓和交易历史接口 ==========

@app.get("/api/positions")
async def get_positions():
    """获取当前持仓"""
    try:
        db = get_session()
        position_mgr = PositionManager()
        positions = position_mgr.get_all_positions(db)
        return {
            "success": True,
            "positions": [
                {
                    "id": pos.id,
                    "symbol": pos.symbol,
                    "side": pos.side,
                    "size": pos.size,
                    "entry_price": pos.entry_price,
                    "current_price": pos.current_price,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "unrealized_pnl_pct": pos.unrealized_pnl_pct if pos.unrealized_pnl_pct else 0,
                    "stop_loss": pos.stop_loss,
                    "created_at": pos.created_at.isoformat() if pos.created_at else None
                }
                for pos in positions
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.post("/api/positions/{position_id}/close")
async def close_position(position_id: int):
    """平仓"""
    try:
        db = get_session()
        position_mgr = PositionManager()
        position = position_mgr.get_position(db, position_id)

        if not position:
            return {
                "success": False,
                "message": "未找到持仓"
            }

        # 获取交易所连接
        import os
        config_path = os.path.join(os.path.dirname(__file__), "../../config/api_keys.json")
        with open(config_path, 'r', encoding='utf-8') as f:
            api_keys = json.load(f)
            if position.exchange not in api_keys['exchanges']:
                raise HTTPException(status_code=404, detail="未找到交易所配置")

            exchange_config = api_keys['exchanges'][position.exchange]
            exchange = ExchangeFactory.create_exchange(
                position.exchange,
                exchange_config['api_key'],
                exchange_config['secret'],
                exchange_config.get('password'),
                exchange_config.get('testnet', True)
            )

        # 执行平仓
        # TODO: 实现实际的平仓逻辑
        # 这里只是将持仓标记为已关闭
        position_mgr.close_position(db, position_id)

        return {
            "success": True,
            "message": "平仓成功"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.get("/api/trades")
async def get_trades(limit: int = 100):
    """获取交易历史"""
    try:
        db = get_session()
        trade_mgr = TradeLogManager()
        trades = trade_mgr.get_recent_trades(db, limit)
        return {
            "success": True,
            "trades": [
                {
                    "id": trade.id,
                    "symbol": trade.symbol,
                    "side": trade.side,
                    "order_type": trade.order_type,
                    "price": trade.price,
                    "quantity": trade.quantity,
                    "status": trade.status,
                    "pnl": trade.pnl,
                    "created_at": trade.created_at.isoformat() if trade.created_at else None
                }
                for trade in trades
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.get("/api/performance")
async def get_performance():
    """获取性能统计"""
    try:
        db = get_session()
        trade_mgr = TradeLogManager()

        total_trades = trade_mgr.get_total_trades(db)
        total_pnl = trade_mgr.get_total_pnl(db)
        win_rate = trade_mgr.get_win_rate(db)

        return {
            "success": True,
            "performance": {
                "total_trades": total_trades,
                "total_pnl": total_pnl,
                "win_rate": win_rate
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

# ========== WebSocket实时推送 ==========

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时数据推送"""
    await manager.connect(websocket)
    try:
        while True:
            # 发送实时数据
            data = {
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_json(data)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ========== ATR分析接口 ==========

@app.get("/api/indicators/atr/{exchange_name}/{symbol}")
async def get_atr_analysis(exchange_name: str, symbol: str, period: int = 14):
    """获取ATR分析"""
    try:
        import os
        config_path = os.path.join(os.path.dirname(__file__), "../../config/api_keys.json")
        with open(config_path, 'r') as f:
            api_keys = json.load(f)
            if exchange_name not in api_keys['exchanges']:
                raise HTTPException(status_code=404, detail="未找到交易所配置")

            exchange_config = api_keys['exchanges'][exchange_name]
            exchange = ExchangeFactory.create_exchange(
                exchange_name,
                exchange_config['api_key'],
                exchange_config['secret'],
                exchange_config.get('passphrase'),
                exchange_config.get('sandbox', True)
            )

        # 获取K线数据
        ohlcv = exchange.exchange.fetch_ohlcv(symbol, timeframe='1h', limit=period + 1)

        # 计算ATR
        indicators = TechnicalIndicators()
        atr_result = indicators.calculate_atr(ohlcv, period)

        return {
            "success": True,
            "atr": atr_result.to_dict()
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
