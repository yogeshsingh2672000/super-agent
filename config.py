"""Shared agent settings. Provider settings live in providers/<name>.py."""
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from utils.env import env, env_bool, env_float, env_int  # noqa: E402 (needs .env loaded)

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"
MEMORY_FILE = DATA_DIR / "memory.json"
LEDGER_FILE = DATA_DIR / "ledger.json"

# Provider picked by default in the startup menu
DEFAULT_PROVIDER = env("DEFAULT_PROVIDER", "bedrock").lower()
MAX_TOKENS = env_int("MAX_TOKENS", 16000)

# Costs (USD)
SEARCH_COST = env_float("SEARCH_COST", 0.0)
MAX_DAILY_SPEND = env_float("MAX_DAILY_SPEND", 5.0)

# Limits
MAX_STEPS = env_int("MAX_STEPS", 60)
SHELL_TIMEOUT = env_int("SHELL_TIMEOUT", 120)
BROWSER_HEADLESS = env_bool("BROWSER_HEADLESS", False)
MAX_OUTPUT_CHARS = 10000
