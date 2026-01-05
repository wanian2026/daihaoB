"""
合约扫描系统 API（使用公开API）
"""
from fastapi import FastAPI, HTTPException, Query
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
    description="基于 FVG 和流动性分析的智能交易信号系统（公开API版）",
    version="2.0.0"
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

class ExchangeConfig(BaseModel):
    exchange: str

# ========== 主页路由 ==========

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回主页"""
    with open("web/index.html", "r", encoding="utf-8") as f:
        return f.read()

# ========== 交易所接口 ==========

@app.get("/api/available-exchanges")
async def get_available_exchanges():
    """获取可用交易所列表"""
    return {
        "success": True,
        "exchanges": [
            {"name": "binance", "display": "币安 (Binance)"},
            {"name": "okx", "display": "欧易 (OKX)"}
        ]
    }

@app.post("/api/test-connection")
async def test_connection(config: ExchangeConfig):
    """测试交易所连接"""
    try:
        exchange = ExchangeFactory.create_exchange(config.exchange)

        # 获取一个交易对测试
        symbols = exchange.get_futures_symbols()
        if symbols:
            price = exchange.get_current_price(symbols[0])
            return {
                "success": True,
                "message": f"连接成功！获取到 {len(symbols)} 个合约",
                "symbols_count": len(symbols),
                "sample_symbol": symbols[0],
                "sample_price": price
            }
        else:
            return {"success": False, "message": "未找到合约"}

    except Exception as e:
        return {"success": False, "message": str(e)}

# ========== 扫描接口 ==========

@app.post("/api/scan")
async def scan_contracts(config: ExchangeConfig, limit: int = Query(50, description="扫描数量限制")):
    """
    扫描合约，生成交易信号

    Args:
        config: 交易所配置
        limit: 扫描数量限制

    Returns:
        扫描结果
    """
    try:
        # 创建扫描器
        scanner = ContractScanner(config.exchange)

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
