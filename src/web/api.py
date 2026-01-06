"""
合约扫描系统 API（使用公开API）
"""
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
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

# 获取项目根目录
# 优先使用环境变量 COZE_WORKSPACE_PATH，否则使用当前文件的父目录的父目录的父目录
WORKSPACE_PATH = os.getenv('COZE_WORKSPACE_PATH')
if WORKSPACE_PATH:
    BASE_DIR = WORKSPACE_PATH
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

web_dir = os.path.join(BASE_DIR, 'web')

# 挂载web目录为静态文件（如果目录存在）
if os.path.exists(web_dir):
    try:
        app.mount("/static", StaticFiles(directory=web_dir), name="static")
    except Exception as e:
        print(f"警告: 挂载静态文件失败: {e}")
else:
    print(f"警告: web目录不存在: {web_dir}")

# ========== 数据模型 ==========

class ExchangeConfig(BaseModel):
    exchange: str
    timeframe: str = "1h"  # K线周期

# ========== 扫描接口 ==========

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """返回主页"""
    html_path = os.path.join(web_dir, "index.html")

    if not os.path.exists(html_path):
        return """
        <html>
        <head><title>404 Not Found</title></head>
        <body>
            <h1>404 Not Found</h1>
            <p>index.html 不存在: {html_path}</p>
            <p>项目目录: {BASE_DIR}</p>
            <p>Web目录: {web_dir}</p>
        </body>
        </html>
        """.format(html_path=html_path, BASE_DIR=BASE_DIR, web_dir=web_dir)

    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/index.html", response_class=HTMLResponse)
async def read_index():
    """返回主页（兼容/index.html路径）"""
    return await read_root()

# ========== 交易所接口 ==========

@app.get("/api/available-exchanges")
async def get_available_exchanges():
    """获取可用交易所列表"""
    return {
        "success": True,
        "exchanges": [
            {"name": "binance", "display": "币安 (Binance)"}
        ]
    }

@app.get("/api/available-timeframes")
async def get_available_timeframes():
    """获取可用K线周期列表"""
    return {
        "success": True,
        "timeframes": [
            {"value": "5m", "display": "5分钟"},
            {"value": "15m", "display": "15分钟"},
            {"value": "30m", "display": "30分钟"},
            {"value": "1h", "display": "1小时"},
            {"value": "4h", "display": "4小时"},
            {"value": "1d", "display": "1天"},
            {"value": "1w", "display": "1周"}
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
                "message": f"连接成功！获取到 {len(symbols)} 个合约，{symbols[0]} 当前价格 {price:.6f}",
                "symbols_count": len(symbols),
                "sample_symbol": symbols[0],
                "sample_price": round(price, 6)
            }
        else:
            return {"success": False, "message": "未找到合约"}

    except Exception as e:
        return {"success": False, "message": str(e)}

# ========== 扫描接口 ==========

@app.post("/api/scan")
async def scan_contracts(config: ExchangeConfig, limit: int = Query(500, description="扫描数量限制")):
    """
    扫描合约，生成交易信号

    Args:
        config: 交易所配置
        limit: 扫描数量限制

    Returns:
        扫描结果
    """
    try:
        # 创建扫描器（传入K线周期）
        scanner = ContractScanner(config.exchange, config.timeframe)

        # 执行扫描
        signals = scanner.scan_contracts(limit=limit)

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
                "timeframe": config.timeframe,
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
