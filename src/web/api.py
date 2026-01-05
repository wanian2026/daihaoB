"""
合约扫描系统 API
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import os
from datetime import datetime

from exchanges import ExchangeFactory
from scanner import ContractScanner

# 创建FastAPI应用
app = FastAPI(
    title="合约信号扫描系统",
    description="基于 FVG 和流动性分析的智能交易信号系统",
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

# ========== 数据模型 ==========

class APIConfig(BaseModel):
    exchange: str
    testnet: bool
    api_key: str
    secret: str
    password: Optional[str] = None

# ========== 主页路由 ==========

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回主页"""
    with open("web/index.html", "r", encoding="utf-8") as f:
        return f.read()

# ========== API 配置接口 ==========

@app.get("/api/config")
async def get_config():
    """获取API配置"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), "../../config/api_keys.json")

        if not os.path.exists(config_path):
            return {"success": True, "config": None}

        with open(config_path, 'r', encoding='utf-8') as f:
            api_keys = json.load(f)

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

        return {"success": True, "config": None}
    except Exception as e:
        return {"success": False, "message": f"加载配置失败: {str(e)}"}

@app.post("/api/config")
async def save_config(config: APIConfig):
    """保存API配置"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), "../../config/api_keys.json")

        existing_config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)

        if 'exchanges' not in existing_config:
            existing_config['exchanges'] = {}

        existing_config['exchanges'][config.exchange] = {
            'api_key': config.api_key,
            'secret': config.secret,
            'testnet': config.testnet
        }

        if config.exchange == 'okx' and config.password:
            existing_config['exchanges']['okx']['password'] = config.password

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, indent=2, ensure_ascii=False)

        return {"success": True, "message": "API配置保存成功"}
    except Exception as e:
        return {"success": False, "message": f"保存失败: {str(e)}"}

@app.post("/api/test")
async def test_connection(config: APIConfig):
    """测试API连接"""
    try:
        exchange = ExchangeFactory.create_exchange(
            config.exchange,
            config.api_key,
            config.secret,
            config.testnet,
            config.password
        )

        # 获取一个交易对测试
        symbols = exchange.get_futures_symbols()
        if symbols:
            price = exchange.get_current_price(symbols[0])
            return {
                "success": True,
                "message": f"连接成功！获取到 {len(symbols)} 个合约",
                "symbols_count": len(symbols)
            }
        else:
            return {"success": False, "message": "未找到合约"}

    except Exception as e:
        return {"success": False, "message": str(e)}

# ========== 扫描接口 ==========

@app.post("/api/scan")
async def scan_contracts(config: APIConfig, limit: int = 50):
    """
    扫描合约，生成交易信号

    Args:
        config: API配置
        limit: 扫描数量限制

    Returns:
        扫描结果
    """
    try:
        # 创建扫描器
        scanner = ContractScanner(
            config.exchange,
            config.api_key,
            config.secret,
            config.testnet,
            config.password
        )

        # 执行扫描
        signals = scanner.scan_contracts_sync(limit=limit)

        # 计算统计信息
        max_confidence = 0
        if signals:
            max_confidence = max(s['confidence'] for s in signals)

        # 转换信号格式（处理时间戳等）
        for signal in signals:
            if signal.get('fvg_info') and signal['fvg_info'].get('timestamp'):
                signal['fvg_info']['timestamp'] = datetime.fromtimestamp(
                    signal['fvg_info']['timestamp'] / 1000
                ).strftime('%Y-%m-%d %H:%M:%S')

        return {
            "success": True,
            "signals": signals,
            "stats": {
                "scanned": limit,
                "found": len(signals),
                "max_confidence": max_confidence,
                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return {
            "success": False,
            "message": str(e),
            "detail": error_detail
        }
