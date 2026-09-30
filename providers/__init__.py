"""Model providers. Each module has NAME, SETTINGS, status(), build(). Model comes from .env."""
from providers import bedrock, lmstudio, ollama, openai
from utils.cost_tracker import CostTracker

PROVIDERS = {
    "bedrock": bedrock,
    "openai": openai,
    "ollama": ollama,
    "lmstudio": lmstudio,
}

# Models known to be text-only even when the provider supports images
TEXT_ONLY_MODELS = ("gpt-oss",)


def is_local(key: str) -> bool:
    return key in ("ollama", "lmstudio")


def model_name(key: str) -> str:
    return PROVIDERS[key].SETTINGS["model"]


def supports_vision(key: str) -> bool:
    if any(hint in model_name(key).lower() for hint in TEXT_ONLY_MODELS):
        return False
    return PROVIDERS[key].SETTINGS["vision"]


def build_model(key: str):
    settings = PROVIDERS[key].SETTINGS
    tracker = CostTracker(settings["input_price"], settings["output_price"])
    return PROVIDERS[key].build([tracker])
