"""
交互式配置模块
处理交易所选择、API密钥配置等交互
"""

from typing import Dict, Tuple, Optional
import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from exchanges import ExchangeFactory
from utils.indicators import TechnicalIndicators, ATRResult

console = Console()


class InteractiveConfig:
    """交互式配置管理"""

    @staticmethod
    async def select_exchange() -> str:
        """选择交易所"""
        answer = await questionary.select(
            "请选择交易所",
            choices=[
                questionary.Choice("💎 欧易 (OKX) - 模拟交易配置简单，推荐新手", "okx"),
                questionary.Choice("🔷 币安 (Binance) - 需要单独的测试网API密钥", "binance"),
            ]
        ).ask_async()

        if answer is None:
            raise KeyboardInterrupt("用户取消操作")

        return answer

    @staticmethod
    async def select_trading_mode(exchange_name: str) -> Tuple[str, bool]:
        """
        选择交易模式
        Returns:
            (模式名称, 是否为模拟交易)
        """
        console.print("\n[bold cyan]请选择交易模式:[/bold cyan]")

        if exchange_name == 'binance':
            # 币安的选项
            answer = await questionary.select(
                "选择交易模式",
                choices=[
                    questionary.Choice(
                        "🧪 模拟交易（推荐新手测试，无风险）",
                        ("模拟交易", True)
                    ),
                    questionary.Choice(
                        "💎 正式交易（使用真实资金）",
                        ("正式交易", False)
                    ),
                ]
            ).ask_async()
        else:  # OKX
            # OKX的选项
            answer = await questionary.select(
                "选择交易模式",
                choices=[
                    questionary.Choice(
                        "🧪 模拟交易（推荐新手测试，无风险）",
                        ("模拟交易", True)
                    ),
                    questionary.Choice(
                        "💎 正式交易（使用真实资金）",
                        ("正式交易", False)
                    ),
                ]
            ).ask_async()

        if answer is None:
            raise KeyboardInterrupt("用户取消操作")

        mode_name, is_simulation = answer

        # 显示选择
        console.print(f"[green]✓ 已选择: {mode_name}[/green]")

        if is_simulation:
            if exchange_name == 'binance':
                console.print("\n[yellow]提示:[/yellow]")
                console.print("- 币安模拟交易需要单独的测试网API密钥")
                console.print("- 测试网地址: https://testnet.binancefuture.com/")
                console.print("- 请确保使用测试网API Key，而非正式网API Key")
            else:  # OKX
                console.print("\n[yellow]提示:[/yellow]")
                console.print("- OKX模拟交易需要单独的API密钥")
                console.print("- 请确保使用模拟交易API Key，而非正式网API Key")
        else:
            console.print("\n[red]⚠️  警告:[/red]")
            console.print("- 正式交易将使用真实资金")
            console.print("- 请确保API密钥已设置安全选项（禁用提币、绑定IP等）")
            console.print("- 建议先使用模拟交易熟悉流程")

        return mode_name, is_simulation

    @staticmethod
    async def input_api_credentials(exchange_name: str, is_simulation: bool) -> Dict[str, str]:
        """
        输入API凭证

        Args:
            exchange_name: 交易所名称
            is_simulation: 是否为模拟交易
        """
        credentials = {}

        # 根据交易模式显示不同的提示
        if is_simulation:
            mode_text = "模拟交易 (测试网)"
        else:
            mode_text = "正式交易 (真实资金)"

        console.print(f"\n[cyan]请输入 {exchange_name.upper()} {mode_text} 的 API 凭证:[/cyan]")

        credentials['api_key'] = await questionary.password(
            f"API Key:"
        ).ask_async()

        if not credentials['api_key']:
            raise ValueError("API Key 不能为空")

        credentials['secret'] = await questionary.password(
            f"Secret:"
        ).ask_async()

        if not credentials['secret']:
            raise ValueError("Secret 不能为空")

        # OKX需要passphrase
        if exchange_name == 'okx':
            credentials['passphrase'] = await questionary.password(
                f"Passphrase:"
            ).ask_async()

            if not credentials['passphrase']:
                raise ValueError("Passphrase 不能为空")
        else:
            credentials['passphrase'] = None

        credentials['sandbox'] = is_simulation

        return credentials

    @staticmethod
    async def test_exchange_connection(exchange_name: str, credentials: Dict[str, str]) -> bool:
        """测试交易所连接"""
        print("\n正在测试交易所连接...")
        print(f"交易所: {exchange_name.upper()}")
        mode_text = "模拟交易" if credentials.get('sandbox') else "正式交易"
        print(f"交易模式: {mode_text}")

        try:
            exchange = ExchangeFactory.create_exchange(
                exchange_name,
                credentials['api_key'],
                credentials['secret'],
                credentials.get('passphrase'),
                credentials.get('sandbox', False)
            )

            # 获取账户余额来测试连接
            balance = exchange.get_balance()

            print(f"✓ {exchange_name.upper()} 连接成功！")
            if balance and 'USDT' in balance:
                usdt_balance = balance['USDT'].get('free', 0)
                print(f"  USDT余额: {usdt_balance}")
            return True

        except Exception as e:
            print(f"✗ {exchange_name.upper()} 连接失败: {e}")
            print(f"\n[黄色]提示:[/黄色]")
            if credentials.get('sandbox'):
                print("- 模拟交易需要单独的测试网API密钥")
                if exchange_name == 'binance':
                    print("\n  🔷 币安期货测试网获取步骤:")
                    print("  1. 访问: https://testnet.binancefuture.com/")
                    print("  2. 注册测试网账号（与正式网分开）")
                    print("  3. 进入 API Management")
                    print("  4. 创建API密钥，保存 API Key 和 Secret")
                    print("\n  💡 或者选择OKX模拟交易（更简单）:")
                    print("  1. 访问: https://www.okx.com/")
                    print("  2. 登录后进入'模拟交易'")
                    print("  3. 创建模拟交易API密钥")
                else:  # OKX
                    print("\n  💎 OKX模拟交易获取步骤:")
                    print("  1. 访问: https://www.okx.com/")
                    print("  2. 登录账号")
                    print("  3. 进入'模拟交易'或'Demo Trading'")
                    print("  4. 创建模拟交易API密钥（包含API Key、Secret、Passphrase）")
                print("\n  ❗ 确保使用的是测试网/模拟交易的API密钥，而非正式网API密钥")
            else:
                print("- 请检查API密钥是否正确")
                print("- 确保API密钥有足够的权限")
                print("- 建议使用IP绑定限制提高安全性")
            return False

    @staticmethod
    async def select_strategy() -> str:
        """选择策略类型"""
        answer = await questionary.select(
            "请选择策略类型",
            choices=[
                questionary.Choice("对冲网格策略（推荐）", "hedge_grid"),
                questionary.Choice("更多策略开发中...", "coming_soon"),
            ]
        ).ask_async()
        
        if answer is None or answer == "coming_soon":
            raise ValueError("暂不支持该策略")
        
        return answer

    @staticmethod
    async def input_strategy_parameters(atr_result: Optional[ATRResult] = None) -> Dict[str, float]:
        """
        输入策略参数，支持基于ATR的建议
        
        Args:
            atr_result: ATR计算结果（可选）
        
        Returns:
            策略参数字典
        """
        params = {}

        print("\n" + "=" * 60)
        print("策略参数配置")
        print("=" * 60)

        # 如果有ATR结果，显示基于ATR的建议
        suggested_params = None
        if atr_result:
            suggested_params = TechnicalIndicators.get_suggested_params_from_atr(atr_result)
            console.print("\n[bold cyan]基于ATR的参数建议:[/bold cyan]")
            console.print(f"ATR占比: {atr_result.atr_percentage:.2f}% (波动性: {atr_result.volatility})")
            console.print(f"建议上涨阈值: {suggested_params['long_threshold'] * 100:.2f}%")
            console.print(f"建议下跌阈值: {suggested_params['short_threshold'] * 100:.2f}%")
            console.print(f"建议止损比例: {suggested_params['stop_loss_ratio'] * 100:.2f}%")
            console.print("=" * 60)

        # 上涨阈值
        default_value = ""
        instruction = "输入 0.1-99.9 之间的数字"
        if suggested_params:
            default_value = str(suggested_params['long_threshold'] * 100)
            instruction = f"基于ATR建议: {default_value}%"

        params['long_threshold'] = await questionary.text(
            "上涨阈值（百分比，输入 2 表示 2%）:",
            default=default_value,
            validate=lambda x: x.replace('.', '', 1).isdigit() and float(x) > 0 and float(x) < 100,
            instruction=instruction
        ).ask_async()
        params['long_threshold'] = float(params['long_threshold']) / 100

        # 下跌阈值
        default_value = ""
        instruction = "输入 0.1-99.9 之间的数字"
        if suggested_params:
            default_value = str(suggested_params['short_threshold'] * 100)
            instruction = f"基于ATR建议: {default_value}%"

        params['short_threshold'] = await questionary.text(
            "下跌阈值（百分比，输入 2 表示 2%）:",
            default=default_value,
            validate=lambda x: x.replace('.', '', 1).isdigit() and float(x) > 0 and float(x) < 100,
            instruction=instruction
        ).ask_async()
        params['short_threshold'] = float(params['short_threshold']) / 100

        # 止损比例（默认止损）
        default_value = ""
        instruction = "输入 0.1-99.9 之间的数字，后续可为每个仓位单独设置止损"
        if suggested_params:
            default_value = str(suggested_params['stop_loss_ratio'] * 100)
            instruction = f"基于ATR建议: {default_value}%（此为默认值，可在开仓后为每个仓位单独设置）"

        params['stop_loss_ratio'] = await questionary.text(
            "默认止损比例（百分比，输入 5 表示 5%）:",
            default=default_value,
            validate=lambda x: x.replace('.', '', 1).isdigit() and float(x) > 0 and float(x) < 100,
            instruction=instruction
        ).ask_async()
        params['stop_loss_ratio'] = float(params['stop_loss_ratio']) / 100

        # 选择仓位模式
        position_mode = await questionary.select(
            "请选择仓位模式:",
            choices=[
                questionary.Choice("固定仓位大小（每次开固定USDT金额）", "fixed"),
                questionary.Choice("开仓比例（每次按当前资金比例开仓，更灵活）", "ratio"),
            ]
        ).ask_async()
        
        if position_mode == "fixed":
            # 固定仓位大小
            params['position_size'] = await questionary.text(
                "仓位大小（USDT）:",
                validate=lambda x: x.replace('.', '', 1).isdigit() and float(x) > 0,
                instruction="输入大于 0 的数字"
            ).ask_async()
            params['position_size'] = float(params['position_size'])
            params['position_ratio'] = None
        else:
            # 开仓比例
            params['position_ratio'] = await questionary.text(
                "开仓比例（0-1之间，如0.1表示10%）:",
                default="0.1",
                validate=lambda x: x.replace('.', '', 1).isdigit() and float(x) > 0 and float(x) <= 1,
                instruction="输入 0-1 之间的数字，如 0.1 表示 10%"
            ).ask_async()
            params['position_ratio'] = float(params['position_ratio'])
            params['position_size'] = None

        # 杠杆倍数
        params['leverage'] = await questionary.text(
            "杠杆倍数（1表示无杠杆，最高125）:",
            default="1",
            validate=lambda x: x.isdigit() and int(x) >= 1 and int(x) <= 125,
            instruction="输入 1-125 之间的整数"
        ).ask_async()
        params['leverage'] = int(params['leverage'])

        # 监控间隔
        params['monitor_interval'] = await questionary.text(
            "价格监控间隔（秒）:",
            default="1",
            validate=lambda x: x.isdigit() and int(x) >= 1,
            instruction="输入大于等于 1 的整数"
        ).ask_async()
        params['monitor_interval'] = int(params['monitor_interval'])

        return params

        # 监控间隔
        params['monitor_interval'] = await questionary.text(
            "价格监控间隔（秒）:",
            default="1",
            validate=lambda x: x.isdigit() and int(x) >= 1,
            instruction="输入大于等于 1 的整数"
        ).ask_async()
        params['monitor_interval'] = int(params['monitor_interval'])

        return params

    @staticmethod
    def confirm_parameters(exchange_name: str, symbol: str, params: Dict) -> bool:
        """确认参数配置"""
        print("\n" + "=" * 60)
        print("参数配置确认")
        print("=" * 60)
        print(f"交易所: {exchange_name.upper()}")
        print(f"交易对: {symbol}")
        print(f"上涨阈值: {params['long_threshold'] * 100}%")
        print(f"下跌阈值: {params['short_threshold'] * 100}%")
        print(f"默认止损比例: {params['stop_loss_ratio'] * 100}%")
        
        if params.get('position_size'):
            print(f"仓位模式: 固定仓位")
            print(f"仓位大小: {params['position_size']} USDT")
        else:
            print(f"仓位模式: 按比例开仓")
            print(f"开仓比例: {params['position_ratio'] * 100}% (每次按当前资金动态调整)")
        
        print(f"杠杆倍数: {params['leverage']}x")
        print(f"监控间隔: {params['monitor_interval']}秒")
        print("=" * 60)
        
        print("\n策略说明:")
        print("1. 初始化时同时开一个多单和一个空单")
        print("2. 上涨达到阈值：平多单 + 开新多单")
        print("3. 下跌达到阈值：平空单 + 开新空单")
        print("4. 触发止损：自动平仓（默认使用止损比例，可单独设置每个仓位的止损）")
        print("5. 按比例模式：每次开仓根据当前账户余额动态计算仓位大小")
        print("=" * 60)
        
        confirm = input("\n确认启动策略？(y/n): ").strip().lower()
        return confirm == 'y'
