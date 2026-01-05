"""
策略实时监控和手动干预模块
"""

import asyncio
import time
from typing import Dict, List, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

from exchanges.base_exchange import BaseExchange
from storage.database.db import get_session
from storage.database.position_manager import PositionManager
from storage.database.trade_log_manager import TradeLogManager

console = Console()


class StrategyMonitor:
    """策略监控界面"""

    def __init__(self, exchange: BaseExchange, symbol: str):
        self.exchange = exchange
        self.symbol = symbol
        self.running = False
        self.current_price = 0.0
        self.positions = []
        self.trade_logs = []
        self.total_pnl = 0.0
        
        self.position_mgr = PositionManager()
        self.trade_log_mgr = TradeLogManager()

    def get_current_price(self) -> float:
        """获取当前价格"""
        try:
            ticker = self.exchange.get_ticker(self.symbol)
            self.current_price = ticker.price
            return self.current_price
        except Exception as e:
            console.print(f"[red]获取价格失败: {e}[/red]")
            return self.current_price

    def update_positions(self):
        """更新持仓信息"""
        db = get_session()
        try:
            positions = self.position_mgr.get_open_positions(
                db, 
                self.exchange.get_exchange_name(), 
                self.symbol
            )
            self.positions = positions
        except Exception as e:
            console.print(f"[red]获取持仓失败: {e}[/red]")
        finally:
            db.close()

    def update_trade_logs(self, limit: int = 10):
        """更新交易日志"""
        db = get_session()
        try:
            logs = self.trade_log_mgr.get_trade_logs(
                db,
                exchange=self.exchange.get_exchange_name(),
                symbol=self.symbol,
                limit=limit
            )
            self.trade_logs = logs
            
            # 计算总盈亏
            self.total_pnl = sum([log.pnl for log in logs if log.pnl is not None])
        except Exception as e:
            console.print(f"[red]获取交易日志失败: {e}[/red]")
        finally:
            db.close()

    def create_price_panel(self) -> Panel:
        """创建价格面板"""
        price_color = "green" if self.current_price > 0 else "red"
        price_text = Text()
        price_text.append(f"{self.symbol}\n", style="bold cyan")
        price_text.append(f"${self.current_price:.2f}", style=f"bold {price_color}")
        
        return Panel(
            price_text,
            title="实时价格",
            border_style="cyan"
        )

    def create_positions_panel(self) -> Panel:
        """创建持仓面板"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("方向", width=8)
        table.add_column("开仓价", justify="right")
        table.add_column("当前价", justify="right")
        table.add_column("数量", justify="right")
        table.add_column("未实现盈亏", justify="right")

        for pos in self.positions:
            side_color = "green" if pos.side == "long" else "red"
            side_text = f"[{side_color}]{pos.side.upper()}[/{side_color}]"
            
            # 计算未实现盈亏
            if pos.side == "long":
                unrealized_pnl = (self.current_price - pos.entry_price) * pos.quantity
            else:
                unrealized_pnl = (pos.entry_price - self.current_price) * pos.quantity
            
            pnl_color = "green" if unrealized_pnl >= 0 else "red"
            pnl_text = f"[{pnl_color}]${unrealized_pnl:.2f}[/{pnl_color}]"

            table.add_row(
                side_text,
                f"{pos.entry_price:.2f}",
                f"{self.current_price:.2f}",
                f"{pos.quantity:.6f}",
                pnl_text
            )

        if not self.positions:
            table.add_row("[dim]无持仓[/dim]", "", "", "", "")

        return Panel(
            table,
            title=f"当前持仓 ({len(self.positions)})",
            border_style="magenta"
        )

    def create_summary_panel(self) -> Panel:
        """创建汇总面板"""
        total_positions = len(self.positions)
        long_count = len([p for p in self.positions if p.side == "long"])
        short_count = len([p for p in self.positions if p.side == "short"])
        
        # 计算总未实现盈亏
        total_unrealized_pnl = 0.0
        for pos in self.positions:
            if pos.side == "long":
                total_unrealized_pnl += (self.current_price - pos.entry_price) * pos.quantity
            else:
                total_unrealized_pnl += (pos.entry_price - self.current_price) * pos.quantity
        
        pnl_color = "green" if total_unrealized_pnl >= 0 else "red"
        
        summary_text = f"""
[bold]汇总信息[/bold]
总持仓数: {total_positions}
多单数量: {long_count}
空单数量: {short_count}

总已实现盈亏: [cyan]${self.total_pnl:.2f}[/cyan]
总未实现盈亏: [{pnl_color}]${total_unrealized_pnl:.2f}[/{pnl_color}]
总盈亏: [{pnl_color}]${self.total_pnl + total_unrealized_pnl:.2f}[/{pnl_color}]
"""
        
        return Panel(
            summary_text,
            title="汇总",
            border_style="green"
        )

    def create_logs_panel(self) -> Panel:
        """创建交易日志面板"""
        table = Table(show_header=True, header_style="bold yellow")
        table.add_column("时间", width=19)
        table.add_column("操作", width=10)
        table.add_column("方向", width=8)
        table.add_column("价格", justify="right")
        table.add_column("盈亏", justify="right")

        for log in self.trade_logs:
            action_color = {
                "open": "green",
                "close": "yellow",
                "stop_loss": "red"
            }.get(log.action, "white")
            
            side_color = "green" if log.side == "long" else "red"
            
            pnl_text = f"${log.pnl:.2f}" if log.pnl is not None else "N/A"
            pnl_color = "green" if (log.pnl and log.pnl >= 0) else "red"
            
            table.add_row(
                log.created_at.strftime("%H:%M:%S"),
                f"[{action_color}]{log.action}[/{action_color}]",
                f"[{side_color}]{log.side}[/{side_color}]",
                f"{log.price:.2f}",
                f"[{pnl_color}]{pnl_text}[/{pnl_color}]"
            )

        if not self.trade_logs:
            table.add_row("[dim]暂无交易记录[/dim]", "", "", "", "")

        return Panel(
            table,
            title=f"最近交易 (最近{len(self.trade_logs)}条)",
            border_style="yellow"
        )

    def create_menu_panel(self) -> Panel:
        """创建操作菜单面板"""
        menu_text = """
[bold cyan]操作菜单[/bold cyan]
  [1] 查看详细持仓
  [2] 查看完整交易日志
  [3] 手动平仓（指定仓位）
  [4] 停止策略
  [5] 刷新数据
  [0] 退出监控
"""
        return Panel(
            menu_text,
            title="操作",
            border_style="cyan"
        )

    def display_dashboard(self):
        """显示仪表板"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        
        layout["left"].split_column(
            Layout(name="price", size=5),
            Layout(name="positions", size=12),
            Layout(name="summary", size=8),
            Layout(name="logs", size=12)
        )
        
        layout["right"].split_column(
            Layout(name="menu", size=12),
            Layout(name="info", ratio=1)
        )
        
        # 更新内容
        layout["header"].update(Panel(
            f"[bold cyan]策略实时监控 - {self.exchange.get_exchange_name().upper()} - {self.symbol}[/bold cyan]",
            style="on blue"
        ))
        
        layout["price"].update(self.create_price_panel())
        layout["positions"].update(self.create_positions_panel())
        layout["summary"].update(self.create_summary_panel())
        layout["logs"].update(self.create_logs_panel())
        layout["menu"].update(self.create_menu_panel())
        
        info_text = f"""
[dim]更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]
[dim]监控状态: {'[green]运行中[/green]' if self.running else '[red]已停止[/red]' }[/dim]
"""
        layout["info"].update(Panel(info_text, title="状态"))
        
        return layout

    async def run_monitor(self):
        """运行监控界面"""
        self.running = True
        console.clear()
        console.print("[bold green]策略监控已启动[/bold green]")
        console.print("[yellow]提示: 按 'q' 查看操作菜单\n[/yellow]")
        
        # 初始数据更新
        self.get_current_price()
        self.update_positions()
        self.update_trade_logs()
        
        # 创建布局和Live显示
        with Live(self.display_dashboard(), refresh_per_second=1) as live:
            try:
                while self.running:
                    # 定期更新数据
                    self.get_current_price()
                    self.update_positions()
                    self.update_trade_logs()
                    
                    # 更新显示
                    live.update(self.display_dashboard())
                    
                    await asyncio.sleep(1)
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]监控已停止[/yellow]")
                self.running = False

    async def show_manual_intervention_menu(self):
        """显示手动干预菜单"""
        while self.running:
            # 更新数据
            self.get_current_price()
            self.update_positions()
            self.update_trade_logs()
            
            # 显示仪表板
            console.clear()
            self.display_dashboard()
            
            # 显示操作选项
            console.print("\n[bold cyan]请选择操作:[/bold cyan]")
            console.print("  [1] 查看详细持仓信息")
            console.print("  [2] 查看完整交易日志")
            console.print("  [3] 手动平仓指定仓位")
            console.print("  [4] 手动平仓所有仓位")
            console.print("  [5] 停止策略并退出")
            console.print("  [6] 返回监控")
            console.print("  [0] 退出程序")
            
            choice = input("\n请输入选项 (0-6): ").strip()
            
            if choice == '0':
                self.running = False
                console.print("[yellow]退出监控程序[/yellow]")
                return False
            elif choice == '1':
                self.show_positions_detail()
            elif choice == '2':
                self.show_full_trade_logs()
            elif choice == '3':
                await self.manual_close_position()
            elif choice == '4':
                await self.manual_close_all_positions()
            elif choice == '5':
                self.running = False
                console.print("[yellow]策略已停止[/yellow]")
                return True
            elif choice == '6':
                # 返回实时监控
                return True
            else:
                console.print("[red]无效的选项[/red]")
                time.sleep(1)
        
        return False

    def show_positions_detail(self):
        """显示详细持仓信息"""
        db = get_session()
        try:
            positions = self.position_mgr.get_open_positions(
                db,
                self.exchange.get_exchange_name(),
                self.symbol
            )
            
            if not positions:
                console.print("[yellow]当前没有持仓[/yellow]")
                input("\n按回车继续...")
                return
            
            for pos in positions:
                console.print(f"\n{'='*60}")
                console.print(f"[bold]仓位ID:[/bold] {pos.id}")
                console.print(f"[bold]方向:[/bold] {pos.side}")
                console.print(f"[bold]开仓价格:[/bold] ${pos.entry_price:.2f}")
                console.print(f"[bold]当前价格:[/bold] ${pos.current_price:.2f}")
                console.print(f"[bold]持仓数量:[/bold] {pos.quantity:.6f}")
                console.print(f"[bold]状态:[/bold] {pos.status}")
                console.print(f"[bold]开仓时间:[/bold] {pos.created_at}")
                console.print(f"{'='*60}")
            
            input("\n按回车继续...")
            
        finally:
            db.close()

    def show_full_trade_logs(self, limit: int = 50):
        """显示完整交易日志"""
        db = get_session()
        try:
            logs = self.trade_log_mgr.get_trade_logs(
                db,
                exchange=self.exchange.get_exchange_name(),
                symbol=self.symbol,
                limit=limit
            )
            
            if not logs:
                console.print("[yellow]暂无交易日志[/yellow]")
                input("\n按回车继续...")
                return
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("ID", width=6)
            table.add_column("时间", width=20)
            table.add_column("操作", width=10)
            table.add_column("方向", width=8)
            table.add_column("价格", justify="right")
            table.add_column("数量", justify="right")
            table.add_column("盈亏", justify="right")
            table.add_column("订单ID", width=15)
            
            for log in logs:
                table.add_row(
                    str(log.id),
                    log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    log.action,
                    log.side,
                    f"{log.price:.2f}",
                    f"{log.quantity:.6f}",
                    f"${log.pnl:.2f}" if log.pnl else "N/A",
                    log.order_id or "N/A"
                )
            
            console.print(table)
            input("\n按回车继续...")
            
        finally:
            db.close()

    async def manual_close_position(self):
        """手动平仓指定仓位"""
        db = get_session()
        try:
            positions = self.position_mgr.get_open_positions(
                db,
                self.exchange.get_exchange_name(),
                self.symbol
            )
            
            if not positions:
                console.print("[yellow]当前没有持仓[/yellow]")
                return
            
            # 显示持仓列表
            console.print("\n[bold]当前持仓列表:[/bold]")
            for i, pos in enumerate(positions, 1):
                console.print(f"  [{i}] {pos.side.upper()} - 开仓价: ${pos.entry_price:.2f}, 数量: {pos.quantity:.6f}")
            
            try:
                choice = int(input("\n请输入要平仓的仓位编号: ")) - 1
                if choice < 0 or choice >= len(positions):
                    console.print("[red]无效的编号[/red]")
                    return
                
                pos = positions[choice]
                
                # 确认
                confirm = input(f"\n确认平仓 {pos.side.upper()} (ID: {pos.id})? (y/n): ").strip().lower()
                if confirm != 'y':
                    console.print("[yellow]已取消[/yellow]")
                    return
                
                # 执行平仓
                close_order = self.exchange.close_position(self.symbol, pos.side, pos.quantity)
                
                # 计算盈亏
                current_price = self.get_current_price()
                if pos.side == 'long':
                    pnl = (current_price - pos.entry_price) * pos.quantity
                else:
                    pnl = (pos.entry_price - current_price) * pos.quantity
                
                # 更新数据库
                self.position_mgr.close_position(db, pos.id, pnl, is_stopped=False)
                
                console.print(f"[green]✓ 平仓成功: 订单ID={close_order.order_id}, 盈亏=${pnl:.2f}[/green]")
                
            except ValueError:
                console.print("[red]无效的输入[/red]")
                
        except Exception as e:
            console.print(f"[red]平仓失败: {e}[/red]")
        finally:
            db.close()

    async def manual_close_all_positions(self):
        """手动平仓所有仓位"""
        db = get_session()
        try:
            positions = self.position_mgr.get_open_positions(
                db,
                self.exchange.get_exchange_name(),
                self.symbol
            )
            
            if not positions:
                console.print("[yellow]当前没有持仓[/yellow]")
                return
            
            confirm = input(f"\n确认平仓所有 {len(positions)} 个仓位? (y/n): ").strip().lower()
            if confirm != 'y':
                console.print("[yellow]已取消[/yellow]")
                return
            
            total_pnl = 0.0
            success_count = 0
            
            for pos in positions:
                try:
                    # 执行平仓
                    close_order = self.exchange.close_position(self.symbol, pos.side, pos.quantity)
                    
                    # 计算盈亏
                    current_price = self.get_current_price()
                    if pos.side == 'long':
                        pnl = (current_price - pos.entry_price) * pos.quantity
                    else:
                        pnl = (pos.entry_price - current_price) * pos.quantity
                    
                    # 更新数据库
                    self.position_mgr.close_position(db, pos.id, pnl, is_stopped=False)
                    
                    total_pnl += pnl
                    success_count += 1
                    
                    console.print(f"[green]✓ 平仓成功: {pos.side.upper()}, 盈亏=${pnl:.2f}[/green]")
                    
                except Exception as e:
                    console.print(f"[red]✗ 平仓失败: {pos.side.upper()}, 错误={e}[/red]")
            
            console.print(f"\n[bold]平仓完成:[/bold] 成功 {success_count}/{len(positions)}, 总盈亏=${total_pnl:.2f}")
            
        except Exception as e:
            console.print(f"[red]平仓失败: {e}[/red]")
        finally:
            db.close()
