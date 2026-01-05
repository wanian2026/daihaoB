#!/usr/bin/env python3
"""
交互式自动化交易程序主入口
"""

import asyncio
import sys
import os
import questionary
from rich.console import Console

# 添加src目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from exchanges import ExchangeFactory
from strategy import TradingEngine
from storage.database.db import get_session
from storage.database.strategy_config_manager import StrategyConfigManager, StrategyConfigCreate
from interactive.config_interactive import InteractiveConfig
from interactive.market_interactive import select_symbol_interactive, MarketInteractive
from interactive.monitor_interactive import StrategyMonitor

console = Console()


async def interactive_wizard():
    """交互式向导"""
    
    console.print("""
[bold cyan]
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           加密货币自动化交易系统 - 交互式模式              ║
║                                                          ║
║              支持币安 (Binance) 和 欧易 (OKX)             ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
[/bold cyan]
    """)
    
    # 步骤1: 选择交易所
    console.print("\n[bold cyan]步骤 1/5: 选择交易所[/bold cyan]")
    exchange_name = await InteractiveConfig.select_exchange()
    
    # 步骤2: 配置API密钥
    console.print(f"\n[bold cyan]步骤 2/5: 配置 {exchange_name.upper()} API[/bold cyan]")
    credentials = await InteractiveConfig.input_api_credentials(exchange_name)
    
    # 测试连接
    connection_ok = await InteractiveConfig.test_exchange_connection(exchange_name, credentials)
    if not connection_ok:
        console.print("[red]连接失败，请检查API密钥配置[/red]")
        return False
    
    # 创建交易所实例
    exchange = ExchangeFactory.create_exchange(
        exchange_name,
        credentials['api_key'],
        credentials['secret'],
        credentials.get('passphrase'),
        credentials.get('sandbox', False)
    )
    
    # 步骤3: 选择交易对
    console.print("\n[bold cyan]步骤 3/5: 选择交易对[/bold cyan]")
    popular_symbols = [
        'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT',
        'XRP/USDT', 'ADA/USDT', 'DOGE/USDT', 'DOT/USDT'
    ]
    symbol, atr_result = await select_symbol_interactive(exchange, popular_symbols)
    
    if not symbol:
        console.print("[yellow]未选择交易对，程序退出[/yellow]")
        return False
    
    # 获取当前价格
    ticker = exchange.get_ticker(symbol)
    current_price = ticker.price
    console.print(f"\n[green]✓ 当前价格: ${current_price:.2f}[/green]")
    
    # 步骤4: 选择策略和配置参数
    console.print("\n[bold cyan]步骤 4/5: 配置策略[/bold cyan]")
    
    strategy_type = await InteractiveConfig.select_strategy()
    params = await InteractiveConfig.input_strategy_parameters(atr_result)
    
    # 步骤5: 计算交易成本
    console.print("\n[bold cyan]步骤 5/5: 交易成本计算[/bold cyan]")
    
    # 获取当前余额（用于比例模式）
    balance_info = exchange.get_balance()
    current_balance = balance_info.get('USDT', {}).get('free', 0)
    console.print(f"当前账户余额: {current_balance} USDT")
    
    # 计算交易成本
    cost = MarketInteractive.calculate_trading_cost(
        current_price,
        position_size=params.get('position_size'),
        position_ratio=params.get('position_ratio'),
        leverage=params['leverage'],
        current_balance=current_balance if params.get('position_ratio') else None
    )
    
    # 确认交易
    confirmed = await MarketInteractive.confirm_trading(symbol, current_price, cost)
    if not confirmed:
        console.print("[yellow]已取消交易[/yellow]")
        return False
    
    return {
        'exchange': exchange,
        'exchange_name': exchange_name,
        'symbol': symbol,
        'params': params,
        'cost': cost
    }


async def run_strategy_with_monitor(config: dict):
    """运行策略并显示监控界面"""
    
    exchange = config['exchange']
    exchange_name = config['exchange_name']
    symbol = config['symbol']
    params = config['params']
    
    console.print("\n[bold green]正在启动策略...[/bold green]")
    
    # 初始化交易引擎
    engine = TradingEngine(
        exchange=exchange,
        symbol=symbol,
        long_threshold=params['long_threshold'],
        short_threshold=params['short_threshold'],
        stop_loss_ratio=params['stop_loss_ratio'],
        position_size=params.get('position_size'),  # 可能为None
        position_ratio=params.get('position_ratio'),  # 可能为None
        leverage=params['leverage']
    )
    
    # 获取数据库会话
    db = get_session()
    
    try:
        # 初始化策略（开多单和空单）
        console.print("[yellow]正在初始化策略（开多单和空单）...[/yellow]")
        engine.initialize_strategy(db)
        
        console.print("[bold green]✓ 策略初始化完成[/bold green]\n")
        
        # 保存策略配置到数据库
        config_mgr = StrategyConfigManager()
        existing_config = config_mgr.get_config(db, exchange_name, symbol)
        if not existing_config:
            from storage.database.strategy_config_manager import StrategyConfigCreate
            config_mgr.create_config(db, StrategyConfigCreate(
                exchange=exchange_name,
                symbol=symbol,
                long_threshold=params['long_threshold'],
                short_threshold=params['short_threshold'],
                stop_loss_ratio=params['stop_loss_ratio'],
                position_size=params.get('position_size'),  # 可能为None
                position_ratio=params.get('position_ratio'),  # 可能为None
                leverage=params['leverage']
            ))
        
        # 创建监控器
        monitor = StrategyMonitor(exchange, symbol)
        
        # 显示监控界面
        await monitor.show_manual_intervention_menu()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]程序被中断[/yellow]")
    except Exception as e:
        console.print(f"\n[red]策略运行异常: {e}[/red]")
        import traceback
        traceback.print_exc()
    finally:
        engine.stop()
        db.close()
        console.print("[bold yellow]程序已退出[/bold yellow]")


async def main_menu():
    """主菜单"""
    
    while True:
        console.clear()
        console.print("""
[bold cyan]
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           加密货币自动化交易系统 - 主菜单                  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
[/bold cyan]
        """)
        
        choice = await questionary.select(
            "请选择操作",
            choices=[
                questionary.Choice("🚀 启动新策略", "new_strategy"),
                questionary.Choice("📊 查看历史交易", "view_history"),
                questionary.Choice("⚙️  系统设置", "settings"),
                questionary.Choice("❌ 退出", "exit")
            ]
        ).ask_async()
        
        if choice == "new_strategy":
            config = await interactive_wizard()
            if config:
                await run_strategy_with_monitor(config)
        
        elif choice == "view_history":
            console.print("[yellow]历史交易查看功能开发中...[/yellow]")
            await asyncio.sleep(1)
        
        elif choice == "settings":
            console.print("[yellow]系统设置功能开发中...[/yellow]")
            await asyncio.sleep(1)
        
        elif choice == "exit" or choice is None:
            console.print("[yellow]再见！[/yellow]")
            break


async def main():
    """主函数"""
    try:
        import questionary
        await main_menu()
    except KeyboardInterrupt:
        console.print("\n[yellow]程序已退出[/yellow]")
    except Exception as e:
        console.print(f"\n[red]程序异常: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
