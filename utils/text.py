import config


def truncate(text: str, limit: int = config.MAX_OUTPUT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... [truncated {len(text) - limit} chars]"


def message_text(message) -> str:
    """Plain text from a LangChain message (string or content blocks)."""
    content = message.content
    if isinstance(content, str):
        return content
    parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
    return "\n".join(p for p in parts if p)
