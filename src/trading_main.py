#!/usr/bin/env python3
"""
加密货币自动化交易程序入口
支持币安和欧易平台的对冲网格策略
"""

import os
import sys
import json
import signal
import logging
from pathlib import Path

from exchanges import ExchangeFactory
from strategy import TradingEngine
from storage.database.db import get_session
from storage.database.strategy_config_manager import StrategyConfigManager, StrategyConfigCreate

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config(config_file: str) -> dict:
    """加载配置文件"""
    config_path = Path(config_file)
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_file}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_api_keys(api_keys_file: str) -> dict:
    """加载API密钥"""
    api_keys_path = Path(api_keys_file)
    if not api_keys_path.exists():
        raise FileNotFoundError(f"API密钥文件不存在: {api_keys_file}")

    with open(api_keys_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("加密货币自动化交易程序启动")
    logger.info("=" * 60)

    try:
        # 加载配置文件
        strategy_config = load_config('config/strategy_config.json')
        api_keys_config = load_api_keys('config/api_keys.json')

        # 获取策略参数
        exchange_name = strategy_config['strategy']['exchange']
        symbol = strategy_config['strategy']['symbol']
        long_threshold = strategy_config['strategy']['long_threshold']
        short_threshold = strategy_config['strategy']['short_threshold']
        stop_loss_ratio = strategy_config['strategy']['stop_loss_ratio']
        position_size = strategy_config['strategy']['position_size']
        leverage = strategy_config['strategy'].get('leverage', 1)
        monitor_interval = strategy_config['strategy'].get('monitor_interval', 1)

        logger.info(f"交易所: {exchange_name}")
        logger.info(f"交易对: {symbol}")
        logger.info(f"上涨阈值: {long_threshold * 100}%")
        logger.info(f"下跌阈值: {short_threshold * 100}%")
        logger.info(f"止损比例: {stop_loss_ratio * 100}%")
        logger.info(f"仓位大小: {position_size} USDT")
        logger.info(f"杠杆倍数: {leverage}x")
        logger.info(f"监控间隔: {monitor_interval}秒")

        # 获取API密钥
        if exchange_name not in api_keys_config['exchanges']:
            raise ValueError(f"未找到交易所 {exchange_name} 的API密钥配置")

        exchange_config = api_keys_config['exchanges'][exchange_name]
        api_key = exchange_config['api_key']
        secret = exchange_config['secret']
        passphrase = exchange_config.get('passphrase')
        sandbox = exchange_config.get('sandbox', False)

        # 检查API密钥是否已配置
        if api_key == 'YOUR_BINANCE_API_KEY' or api_key == 'YOUR_OKX_API_KEY':
            raise ValueError("请先配置API密钥！请编辑 config/api_keys.json 文件")

        # 创建交易所实例
        logger.info(f"正在连接 {exchange_name} 交易所...")
        exchange = ExchangeFactory.create_exchange(
            exchange_name, api_key, secret, passphrase, sandbox
        )
        logger.info(f"交易所连接成功！")

        # 获取数据库会话
        db = get_session()

        # 保存策略配置到数据库
        config_mgr = StrategyConfigManager()
        existing_config = config_mgr.get_config(db, exchange_name, symbol)
        if not existing_config:
            config_mgr.create_config(db, StrategyConfigCreate(
                exchange=exchange_name,
                symbol=symbol,
                long_threshold=long_threshold,
                short_threshold=short_threshold,
                stop_loss_ratio=stop_loss_ratio,
                position_size=position_size,
                leverage=leverage
            ))
            logger.info("策略配置已保存到数据库")

        # 创建交易引擎
        logger.info("正在初始化交易引擎...")
        engine = TradingEngine(
            exchange=exchange,
            symbol=symbol,
            long_threshold=long_threshold,
            short_threshold=short_threshold,
            stop_loss_ratio=stop_loss_ratio,
            position_size=position_size,
            leverage=leverage
        )

        # 注册信号处理（优雅退出）
        def signal_handler(signum, frame):
            logger.info(f"收到信号 {signum}，正在停止交易...")
            engine.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # 初始化策略（开多单和空单）
        logger.info("正在初始化策略...")
        engine.initialize_strategy(db)

        # 运行策略
        logger.info("开始运行策略...")
        logger.info("按 Ctrl+C 停止程序")
        engine.run(db, interval=monitor_interval)

    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except FileNotFoundError as e:
        logger.error(f"配置文件错误: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"配置错误: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序运行异常: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("=" * 60)
        logger.info("程序已退出")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()
