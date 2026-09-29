from datetime import date

import config
from utils.storage import load_json, save_json


class BudgetExceeded(Exception):
    pass


def _today() -> dict:
    ledger = load_json(config.LEDGER_FILE, {})
    return ledger.get(str(date.today()), {"token_cost": 0.0, "search_cost": 0.0, "expenses": [], "income": []})


def _save_today(day: dict) -> None:
    ledger = load_json(config.LEDGER_FILE, {})
    ledger[str(date.today())] = day
    save_json(config.LEDGER_FILE, ledger)


def add_cost(kind: str, amount: float) -> None:
    """kind: 'token_cost' or 'search_cost'."""
    day = _today()
    day[kind] += amount
    _save_today(day)


def add_entry(kind: str, amount: float, note: str) -> None:
    """kind: 'expenses' or 'income'."""
    day = _today()
    day[kind].append({"amount": amount, "note": note})
    _save_today(day)


def summary() -> dict:
    day = _today()
    expenses = sum(e["amount"] for e in day["expenses"])
    income = sum(e["amount"] for e in day["income"])
    total_cost = day["token_cost"] + day["search_cost"] + expenses
    profit = income - total_cost
    margin = (profit / income * 100) if income else 0.0
    return {
        "token_cost": round(day["token_cost"], 4),
        "search_cost": round(day["search_cost"], 4),
        "expenses": round(expenses, 2),
        "total_cost": round(total_cost, 4),
        "income": round(income, 2),
        "profit": round(profit, 4),
        "margin_pct": round(margin, 1),
        "daily_limit": config.MAX_DAILY_SPEND,
    }


def check_limit() -> None:
    if summary()["total_cost"] >= config.MAX_DAILY_SPEND:
        raise BudgetExceeded(f"Daily spend limit ${config.MAX_DAILY_SPEND} reached.")
