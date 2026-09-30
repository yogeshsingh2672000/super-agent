from langchain_core.callbacks import BaseCallbackHandler

from utils import ledger
from utils.logger import log


class CostTracker(BaseCallbackHandler):
    """Adds token cost after every model call and enforces the daily limit."""

    raise_error = True

    def __init__(self, input_price_per_m: float, output_price_per_m: float):
        self.input_price = input_price_per_m
        self.output_price = output_price_per_m

    def on_chat_model_start(self, serialized, messages, **kwargs):
        ledger.check_limit()

    def on_llm_end(self, response, **kwargs):
        message = response.generations[0][0].message
        usage = getattr(message, "usage_metadata", None) or {}
        cost = (
            usage.get("input_tokens", 0) * self.input_price
            + usage.get("output_tokens", 0) * self.output_price
        ) / 1_000_000
        ledger.add_cost("token_cost", cost)
        total = ledger.summary()["total_cost"]
        log("💰", f"Step cost ${cost:.4f} | today ${total:.4f}", style="dim")
