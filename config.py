import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"
MEMORY_FILE = DATA_DIR / "memory.json"
LEDGER_FILE = DATA_DIR / "ledger.json"

# Model
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-opus-5")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "16000"))

# Pricing (USD)
INPUT_PRICE_PER_M = float(os.getenv("INPUT_PRICE_PER_M", "5"))
OUTPUT_PRICE_PER_M = float(os.getenv("OUTPUT_PRICE_PER_M", "25"))
SEARCH_COST = float(os.getenv("SEARCH_COST", "0"))
MAX_DAILY_SPEND = float(os.getenv("MAX_DAILY_SPEND", "5"))

# Limits
MAX_STEPS = int(os.getenv("MAX_STEPS", "60"))
SHELL_TIMEOUT = int(os.getenv("SHELL_TIMEOUT", "120"))
BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"
MAX_OUTPUT_CHARS = 10000
