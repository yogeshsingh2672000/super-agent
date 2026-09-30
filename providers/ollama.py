"""Ollama (local, free)."""
import requests

import config
from utils.env import env, env_bool, env_int

NAME = "Ollama (local)"
SETTINGS = {
    "base_url": env("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
    "model": env("OLLAMA_MODEL"),
    "num_ctx": env_int("OLLAMA_NUM_CTX", 16384),  # Ollama's default is too small for the agent prompt
    "input_price": 0.0,
    "output_price": 0.0,
    "vision": env_bool("OLLAMA_VISION", False),
}


def _installed() -> list[str]:
    response = requests.get(f"{SETTINGS['base_url']}/api/tags", timeout=2)
    response.raise_for_status()
    return [m["name"] for m in response.json().get("models", [])]


def status() -> tuple[bool, str]:
    model = SETTINGS["model"]
    if not model:
        return False, "OLLAMA_MODEL missing in .env"
    try:
        installed = _installed()
    except requests.RequestException:
        return False, f"server not running at {SETTINGS['base_url']} (start the Ollama app)"
    if model not in installed and f"{model}:latest" not in installed:
        return False, f"{model} not installed (run: ollama pull {model})"
    return True, "server running, model installed"


def build(callbacks: list):
    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=SETTINGS["model"],
        base_url=SETTINGS["base_url"],
        num_ctx=SETTINGS["num_ctx"],
        num_predict=config.MAX_TOKENS,
        callbacks=callbacks,
    )
