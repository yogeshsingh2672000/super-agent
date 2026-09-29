"""Sources seen during the current task, numbered for citations."""
import html
import re

from bs4 import BeautifulSoup

_sources: list[dict] = []

DATE_META_KEYS = [
    "article:published_time",
    "article:modified_time",
    "og:updated_time",
    "datePublished",
    "dateModified",
    "pubdate",
    "publish-date",
    "date",
    "last-modified",
]
CITATION = re.compile(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\]")  # [2], [1, 3], [1-4]
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


def reset() -> None:
    _sources.clear()


def add(url: str, title: str = "", date: str = "", opened: bool = False, text: str = "") -> int:
    """Register a source and return its number. Same URL keeps its number."""
    title = html.unescape(title or "").strip()
    for number, source in enumerate(_sources, 1):
        if source["url"] == url:
            source["title"] = source["title"] or title
            source["date"] = source["date"] or date
            if opened:
                source["opened"], source["text"] = True, text
            return number
    _sources.append({"url": url, "title": title, "date": date, "opened": opened, "text": text})
    return len(_sources)


def all_sources() -> list[tuple[int, dict]]:
    return list(enumerate(_sources, 1))


def _citation_numbers(text: str) -> set[int]:
    numbers = set()
    for group in CITATION.findall(text):
        for part in re.split(r"\s*,\s*", group):
            if re.search(r"[–-]", part):
                start, end = (int(x) for x in re.split(r"\s*[–-]\s*", part))
                numbers.update(range(start, end + 1))
            else:
                numbers.add(int(part))
    return numbers


def cited(text: str) -> list[tuple[int, dict]]:
    """Sources referenced as [n] in the text."""
    numbers = _citation_numbers(text)
    return [(n, s) for n, s in all_sources() if n in numbers]


def _key_numbers(sentence: str) -> list[str]:
    """Numbers worth checking: skip citations, years and small integers."""
    sentence = CITATION.sub("", sentence)
    result = []
    for value in NUMBER.findall(sentence):
        plain = value.replace(",", "")
        is_year = plain.isdigit() and len(plain) == 4 and plain.startswith(("19", "20"))
        if is_year or (plain.isdigit() and len(plain) < 3):
            continue
        result.append(value)
    return result


def _not_in(numbers: list[str], text: str) -> list[str]:
    plain = text.replace(",", "")
    return [v for v in numbers if v.replace(",", "") not in plain]


def check_numbers(answer: str) -> dict[int, list[str]]:
    """Numbers NOT found in their cited source. Key 0 = uncited numbers found in no source."""
    missing: dict[int, list[str]] = {}
    all_text = " ".join(s["text"] for s in _sources)
    for sentence in re.split(r"(?<=[.!?])\s+|\n", answer):
        numbers = _key_numbers(sentence)
        if not numbers:
            continue
        cited_here = [n for n in _citation_numbers(sentence) if 1 <= n <= len(_sources)]
        checks = [(n, _sources[n - 1]["text"]) for n in cited_here] or [(0, all_text)]
        for n, text in checks:
            for value in _not_in(numbers, text):
                if value not in missing.setdefault(n, []):
                    missing[n].append(value)
    return missing


def short_date(value: str) -> str:
    value = (value or "").strip()
    if re.match(r"\d{4}-\d{2}-\d{2}", value):
        return value[:10]
    return value[:30]


def find_page_date(soup: BeautifulSoup, last_modified: str = "") -> str:
    """Publish/update date from page meta tags, <time>, or Last-Modified header."""
    for key in DATE_META_KEYS:
        tag = soup.find("meta", attrs={"property": key}) or soup.find("meta", attrs={"name": key}) \
            or soup.find("meta", attrs={"itemprop": key})
        if tag and tag.get("content"):
            return short_date(tag["content"])
    time_tag = soup.find("time", attrs={"datetime": True})
    if time_tag:
        return short_date(time_tag["datetime"])
    return short_date(last_modified)
