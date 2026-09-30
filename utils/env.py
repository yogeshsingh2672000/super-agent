"""Typed readers for .env values."""
import os


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def env_float(name: str, default: float = 0.0) -> float:
    value = env(name)
    return float(value) if value else default


def env_int(name: str, default: int = 0) -> int:
    value = env(name)
    return int(value) if value else default


def env_bool(name: str, default: bool = False) -> bool:
    value = env(name).lower()
    return value in ("1", "true", "yes") if value else default
