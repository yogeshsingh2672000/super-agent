from langchain_core.callbacks import BaseCallbackHandler

import config
from utils import ledger
from utils.logger import log


class CostTracker(BaseCallbackHandler):
    """Adds token cost after every model call and enforces the daily limit."""

    raise_error = True

    def on_chat_model_start(self, serialized, messages, **kwargs):
        ledger.check_limit()

    def on_llm_end(self, response, **kwargs):
        message = response.generations[0][0].message
        usage = getattr(message, "usage_metadata", None) or {}
        cost = (
            usage.get("input_tokens", 0) * config.INPUT_PRICE_PER_M
            + usage.get("output_tokens", 0) * config.OUTPUT_PRICE_PER_M
        ) / 1_000_000
        ledger.add_cost("token_cost", cost)
        total = ledger.summary()["total_cost"]
        log("💰", f"Step cost ${cost:.4f} | today ${total:.4f}", style="dim")
