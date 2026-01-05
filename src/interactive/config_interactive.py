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
                questionary.Choice("币安 (Binance)", "binance"),
                questionary.Choice("欧易 (OKX)", "okx"),
            ]
        ).ask_async()
        
        if answer is None:
            raise KeyboardInterrupt("用户取消操作")
        
        return answer

    @staticmethod
    async def input_api_credentials(exchange_name: str) -> Dict[str, str]:
        """输入API凭证"""
        credentials = {}

        credentials['api_key'] = await questionary.password(
            f"请输入 {exchange_name.upper()} 的 API Key"
        ).ask_async()
        
        if not credentials['api_key']:
            raise ValueError("API Key 不能为空")

        credentials['secret'] = await questionary.password(
            f"请输入 {exchange_name.upper()} 的 Secret"
        ).ask_async()
        
        if not credentials['secret']:
            raise ValueError("Secret 不能为空")

        # OKX需要passphrase
        if exchange_name == 'okx':
            credentials['passphrase'] = await questionary.password(
                f"请输入 {exchange_name.upper()} 的 Passphrase"
            ).ask_async()
            
            if not credentials['passphrase']:
                raise ValueError("Passphrase 不能为空")
        else:
            credentials['passphrase'] = None

        # 是否使用沙盒环境
        use_sandbox = await questionary.confirm(
            "是否使用沙盒环境（测试）？",
            default=False
        ).ask_async()
        
        credentials['sandbox'] = use_sandbox

        return credentials

    @staticmethod
    async def test_exchange_connection(exchange_name: str, credentials: Dict[str, str]) -> bool:
        """测试交易所连接"""
        print("\n正在测试交易所连接...")
        
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
            return True
            
        except Exception as e:
            print(f"✗ {exchange_name.upper()} 连接失败: {e}")
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

        # 止损比例
        default_value = ""
        instruction = "输入 0.1-99.9 之间的数字"
        if suggested_params:
            default_value = str(suggested_params['stop_loss_ratio'] * 100)
            instruction = f"基于ATR建议: {default_value}%"

        params['stop_loss_ratio'] = await questionary.text(
            "止损比例（百分比，输入 5 表示 5%）:",
            default=default_value,
            validate=lambda x: x.replace('.', '', 1).isdigit() and float(x) > 0 and float(x) < 100,
            instruction=instruction
        ).ask_async()
        params['stop_loss_ratio'] = float(params['stop_loss_ratio']) / 100

        # 仓位大小
        params['position_size'] = await questionary.text(
            "仓位大小（USDT）:",
            validate=lambda x: x.replace('.', '', 1).isdigit() and float(x) > 0,
            instruction="输入大于 0 的数字"
        ).ask_async()
        params['position_size'] = float(params['position_size'])

        # 杠杆倍数
        params['leverage'] = await questionary.text(
            "杠杆倍数（1表示无杠杆）:",
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
        print(f"止损比例: {params['stop_loss_ratio'] * 100}%")
        print(f"仓位大小: {params['position_size']} USDT")
        print(f"杠杆倍数: {params['leverage']}x")
        print(f"监控间隔: {params['monitor_interval']}秒")
        print("=" * 60)
        
        print("\n策略说明:")
        print("1. 初始化时同时开一个多单和一个空单")
        print("2. 上涨达到阈值：平多单 + 开新多单")
        print("3. 下跌达到阈值：平空单 + 开新空单")
        print("4. 触发止损：自动平仓")
        print("=" * 60)
        
        confirm = input("\n确认启动策略？(y/n): ").strip().lower()
        return confirm == 'y'
