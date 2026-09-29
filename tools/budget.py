import json

from langchain_core.tools import tool

from utils import ledger
from utils.logger import log


@tool
def record_expense(amount: float, note: str) -> str:
    """Record real money spent today (USD)."""
    ledger.add_entry("expenses", amount, note)
    log("💸", f"Expense ${amount:.2f}: {note}", style="yellow")
    return "Expense recorded."


@tool
def record_income(amount: float, note: str) -> str:
    """Record real money earned today (USD). Only confirmed income."""
    ledger.add_entry("income", amount, note)
    log("💵", f"Income ${amount:.2f}: {note}", style="green")
    return "Income recorded."


@tool
def budget_status() -> str:
    """Today's costs (tokens, searches, expenses), income, profit and margin."""
    log("📊", "Checking budget")
    return json.dumps(ledger.summary(), indent=2)


TOOLS = [record_expense, record_income, budget_status]
