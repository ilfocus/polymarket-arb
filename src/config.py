import os
from dataclasses import dataclass
import string

from dotenv import load_dotenv

# 如果存在，从项目根目录加载 .env 文件；覆盖现有环境变量以优先使用 .env 编辑
load_dotenv(override=True)


@dataclass
class Settings:
    api_key: str = os.getenv("POLYMARKET_API_KEY", "")
    api_secret: str = os.getenv("POLYMARKET_API_SECRET", "")
    api_passphrase: str = os.getenv("POLYMARKET_API_PASSPHRASE", "")
    private_key: str = os.getenv("POLYMARKET_PRIVATE_KEY", "")
    signature_type: int = int(os.getenv("POLYMARKET_SIGNATURE_TYPE", "1"))
    funder: str = os.getenv("POLYMARKET_FUNDER", "")
    market_slug: str = os.getenv("POLYMARKET_MARKET_SLUG", "")
    market_id: str = os.getenv("POLYMARKET_MARKET_ID", "")
    yes_token_id: str = os.getenv("POLYMARKET_YES_TOKEN_ID", "")
    no_token_id: str = os.getenv("POLYMARKET_NO_TOKEN_ID", "")
    ws_url: str = os.getenv(
        "POLYMARKET_WS_URL", "wss://ws-subscriptions-clob.polymarket.com"
    )
    target_pair_cost: float = float(os.getenv("TARGET_PAIR_COST", "0.99"))
    balance_slack: float = float(os.getenv("BALANCE_SLACK", "0.15"))
    balance_refresh_seconds: float = float(
        os.getenv("BALANCE_REFRESH_SECONDS", "5")
    )
    order_size: float = float(os.getenv("ORDER_SIZE", "50"))
    yes_buy_threshold: float = float(os.getenv("YES_BUY_THRESHOLD", "0.45"))
    no_buy_threshold: float = float(os.getenv("NO_BUY_THRESHOLD", "0.45"))
    verbose: bool = os.getenv("VERBOSE", "false").lower() == "true"
    dry_run: bool = os.getenv("DRY_RUN", "false").lower() == "true"
    cooldown_seconds: float = float(os.getenv("COOLDOWN_SECONDS", "10"))
    sim_balance: float = float(os.getenv("SIM_BALANCE", "0"))
    max_trades_per_market: int = int(os.getenv("MAX_TRADES_PER_MARKET", "0"))
    min_time_remaining_minutes: int = int(os.getenv("MIN_TIME_REMAINING_MINUTES", "0"))

    def __post_init__(self) -> None:
        self.private_key = normalize_private_key(self.private_key)
        self.funder = self.funder.strip()


def normalize_private_key(value: str) -> str:
    value = (value or "").strip().strip('"').strip("'")
    if not value:
        return ""

    hex_value = value[2:] if value.lower().startswith("0x") else value
    if len(hex_value) != 64 or any(char not in string.hexdigits for char in hex_value):
        raise ValueError(
            "POLYMARKET_PRIVATE_KEY 必须是 64 位十六进制 EVM 私钥（可带 0x 前缀）；当前值看起来像 UUID/API Key，而不是钱包私钥"
        )

    return f"0x{hex_value.lower()}"


def load_settings() -> Settings:
    return Settings()
