"""
实时行情和合约选择模块
"""

from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
import time

from utils.indicators import TechnicalIndicators, ATRResult

console = Console()


class MarketInteractive:
    """实时行情交互"""

    @staticmethod
    def display_market_list(symbols_data: List[Dict[str, any]], page_size: int = 20):
        """
        显示市场列表（分页）
        
        Args:
            symbols_data: 交易对数据列表
            page_size: 每页显示数量
        """
        if not symbols_data:
            console.print("[red]没有可用的交易对数据[/red]")
            return None

        total_pages = (len(symbols_data) + page_size - 1) // page_size
        current_page = 0

        while True:
            # 计算当前页的数据
            start_idx = current_page * page_size
            end_idx = min(start_idx + page_size, len(symbols_data))
            page_data = symbols_data[start_idx:end_idx]

            # 创建表格
            table = Table(title=f"市场行情列表 (第 {current_page + 1}/{total_pages} 页)", show_header=True, header_style="bold magenta")
            table.add_column("序号", style="cyan", width=6)
            table.add_column("交易对", style="green")
            table.add_column("最新价", justify="right", style="yellow")
            table.add_column("24h涨跌", justify="right")
            table.add_column("24h成交量", justify="right")

            for idx, item in enumerate(page_data, start=start_idx + 1):
                price = item.get('price', 'N/A')
                change_24h = item.get('change_24h', 0)
                
                # 涨跌颜色
                if change_24h > 0:
                    change_str = f"[green]+{change_24h:.2f}%[/green]"
                elif change_24h < 0:
                    change_str = f"[red]{change_24h:.2f}%[/red]"
                else:
                    change_str = f"{change_24h:.2f}%"

                table.add_row(
                    str(idx),
                    item['symbol'],
                    f"{price:.2f}",
                    change_str,
                    f"{item.get('volume', 'N/A')}"
                )

            console.print(table)
            console.print("\n[提示] 输入交易对序号进行选择，或输入 'p' 上一页，'n' 下一页，'q' 返回")

            user_input = input("\n请选择: ").strip().lower()

            if user_input == 'q':
                return None
            elif user_input == 'p' and current_page > 0:
                current_page -= 1
            elif user_input == 'n' and current_page < total_pages - 1:
                current_page += 1
            elif user_input.isdigit():
                idx = int(user_input) - 1
                if 0 <= idx < len(symbols_data):
                    selected_symbol = symbols_data[idx]['symbol']
                    console.print(f"\n[green]✓ 已选择交易对: {selected_symbol}[/green]")
                    return selected_symbol
                else:
                    console.print("[red]无效的序号[/red]")
            else:
                console.print("[red]无效的输入[/red]")

    @staticmethod
    def calculate_trading_cost(price: float, position_size: float, leverage: int, 
                                taker_fee: float = 0.0004) -> Dict[str, float]:
        """
        计算交易成本
        
        Args:
            price: 当前价格
            position_size: 仓位大小（USDT）
            leverage: 杠杆倍数
            taker_fee: 手续费率（默认0.04%）
        
        Returns:
            交易成本字典
        """
        # 计算持仓数量
        quantity = position_size / price
        
        # 计算开仓手续费（双边，多单和空单）
        open_fee = position_size * taker_fee * 2
        
        # 计算保证金（考虑杠杆）
        margin = position_size / leverage
        
        # 计算平仓手续费（预估）
        close_fee = position_size * taker_fee * 2
        
        # 总成本
        total_cost = open_fee + close_fee
        
        return {
            'quantity': quantity,
            'open_fee': open_fee,
            'margin': margin,
            'close_fee': close_fee,
            'total_cost': total_cost,
            'taker_fee_rate': taker_fee * 100
        }

    @staticmethod
    def display_atr_panel(atr_result: ATRResult):
        """显示ATR信息面板"""
        # 波动性颜色
        volatility_colors = {
            "低": "green",
            "中": "yellow",
            "高": "red"
        }
        volatility_color = volatility_colors.get(atr_result.volatility, "white")

        atr_text = f"""
[bold cyan]ATR（平均真实波幅）分析[/bold cyan]

当前价格: [yellow]${atr_result.current_price:.2f}[/yellow]
ATR({atr_result.period}): [cyan]${atr_result.atr:.2f}[/cyan]
ATR占比: [cyan]{atr_result.atr_percentage:.2f}%[/cyan]
波动性等级: [{volatility_color}] {atr_result.volatility} [/{volatility_color}]
"""
        
        # 波动性说明
        if atr_result.volatility == "低":
            desc = "[dim]市场波动较小，适合较小阈值策略[/dim]"
        elif atr_result.volatility == "中":
            desc = "[dim]市场波动适中，建议设置中等阈值[/dim]"
        else:
            desc = "[dim]市场波动较大，建议设置较大阈值并提高止损[/dim]"
        
        atr_text += desc

        console.print(Panel(atr_text, border_style="cyan"))

    @staticmethod
    def display_trading_cost(cost: Dict[str, float]):
        """显示交易成本"""
        table = Table(title="交易成本计算", show_header=True, header_style="bold magenta")
        table.add_column("项目", style="cyan")
        table.add_column("金额/数量", justify="right")
        table.add_column("说明", style="dim")

        table.add_row(
            "持仓数量",
            f"{cost['quantity']:.6f}",
            "单边数量"
        )
        table.add_row(
            "开仓手续费",
            f"${cost['open_fee']:.2f}",
            f"双边（多单+空单），费率 {cost['taker_fee_rate']:.4f}%"
        )
        table.add_row(
            "所需保证金",
            f"${cost['margin']:.2f}",
            f"杠杆 1/{cost['margin'] / cost['open_fee']:.0f}x"
        )
        table.add_row(
            "预估平仓手续费",
            f"${cost['close_fee']:.2f}",
            "双边预估"
        )
        table.add_row(
            "总成本",
            f"[yellow]${cost['total_cost']:.2f}[/yellow]",
            "开仓+平仓"
        )
        
        # 成本占仓位比例
        cost_ratio = (cost['total_cost'] / cost['margin']) * 100
        table.add_row(
            "成本占比",
            f"[cyan]{cost_ratio:.2f}%[/cyan]",
            "总成本 / 保证金"
        )

        console.print(table)

    @staticmethod
    async def confirm_trading(symbol: str, price: float, cost: Dict[str, float]) -> bool:
        """确认交易"""
        console.print(f"\n[bold yellow]即将执行交易 - {symbol}[/bold yellow]")
        console.print(f"当前价格: ${price:.2f}")
        MarketInteractive.display_trading_cost(cost)
        
        confirm = input("\n确认执行策略交易？(y/n): ").strip().lower()
        return confirm == 'y'


async def select_symbol_interactive(exchange, popular_symbols: List[str] = None) -> tuple[Optional[str], Optional[ATRResult]]:
    """
    交互式选择交易对
    
    Args:
        exchange: 交易所实例
        popular_symbols: 热门交易对列表（优先显示）
    
    Returns:
        (选中的交易对符号, ATR结果)
    """
    console.print("\n[bold cyan]正在获取市场行情...[/bold cyan]\n")
    
    # 如果提供了热门交易对，优先获取这些
    if popular_symbols:
        console.print(f"[dim]获取 {len(popular_symbols)} 个热门交易对行情...[/dim]")
        symbols_data = []
        
        for symbol in popular_symbols:
            try:
                ticker = exchange.get_ticker(symbol)
                symbols_data.append({
                    'symbol': symbol,
                    'price': ticker.price,
                    'change_24h': 0,  # 简化处理
                    'volume': 'N/A'
                })
            except Exception as e:
                console.print(f"[red]获取 {symbol} 行情失败: {e}[/red]")
    else:
        # 获取所有USDT交易对（简化版）
        console.print("[dim]获取所有交易对行情（可能需要较长时间）...[/dim]")
        console.print("[yellow]提示：推荐选择 BTC/USDT、ETH/USDT 等主流交易对[/yellow]\n")
        
        # 简化处理：返回一些常见交易对
        common_symbols = [
            'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 
            'XRP/USDT', 'ADA/USDT', 'DOGE/USDT', 'DOT/USDT',
            'MATIC/USDT', 'LINK/USDT'
        ]
        
        symbols_data = []
        for symbol in common_symbols:
            try:
                ticker = exchange.get_ticker(symbol)
                symbols_data.append({
                    'symbol': symbol,
                    'price': ticker.price,
                    'change_24h': 0,
                    'volume': 'N/A'
                })
            except:
                pass

    if not symbols_data:
        console.print("[red]未能获取到任何交易对数据[/red]")
        return None, None

    # 显示并选择交易对
    selected_symbol = MarketInteractive.display_market_list(symbols_data)
    
    # 如果选择了交易对，显示ATR信息
    if selected_symbol:
        console.print(f"\n[bold cyan]正在计算ATR（平均真实波幅）...[/bold cyan]")
        try:
            # 计算ATR（使用1小时K线，14周期）
            atr_result = TechnicalIndicators.get_atr_with_timeframe(
                exchange, selected_symbol, timeframe='1h', period=14
            )
            MarketInteractive.display_atr_panel(atr_result)
            
            return selected_symbol, atr_result
            
        except Exception as e:
            console.print(f"[yellow]计算ATR失败: {e}[/yellow]")
            return selected_symbol, None
    
    return None, None
