import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from langchain_core.tools import tool

import config
from utils import ledger, sources
from utils.logger import log
from utils.text import truncate

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SuperAgent/1.0"}


def _source_range(numbers: list[int]) -> str:
    return f"[{numbers[0]}]-[{numbers[-1]}]" if numbers else "none"


@tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web. Returns numbered sources with snippets (snippets are not verified)."""
    ledger.add_cost("search_cost", config.SEARCH_COST)
    try:
        results = DDGS().text(query, max_results=max_results)
    except Exception as e:
        log("🔎", f'Searching "{query}" failed')
        return f"Search failed: {e}"
    lines, numbers = [], []
    for r in results or []:
        n = sources.add(r["href"], r["title"], text=r["body"])
        numbers.append(n)
        lines.append(f"[{n}] {r['title']}\n{r['href']}\nSnippet (unverified, date unknown): {r['body']}")
    log("🔎", f'Searching "{query}" → sources {_source_range(numbers)}')
    return "\n\n".join(lines) or "No results."


@tool
def news_search(query: str, period: str = "w", max_results: int = 5) -> str:
    """Search recent news with publish dates. period: d=day, w=week, m=month. Best for today/latest questions."""
    ledger.add_cost("search_cost", config.SEARCH_COST)
    try:
        results = DDGS().news(query, timelimit=period, max_results=max_results)
    except Exception as e:
        log("📰", f'News search "{query}" failed')
        return f"News search failed: {e}"
    lines, numbers = [], []
    for r in results or []:
        date = sources.short_date(r.get("date", ""))
        n = sources.add(r["url"], f"{r['title']} ({r.get('source', '')})", date, text=r["body"])
        numbers.append(n)
        lines.append(f"[{n}] {r['title']} | {r.get('source', '')} | published {date}\n{r['url']}\nSnippet: {r['body']}")
    log("📰", f'News search "{query}" ({period}) → sources {_source_range(numbers)}')
    return "\n\n".join(lines) or "No recent news found."


@tool
def fetch_page(url: str) -> str:
    """Open a web page and return its text. Use this to verify facts from search snippets."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
    except requests.RequestException as e:
        log("🌐", f"Opening {url} failed")
        return f"Fetch failed: {e}"
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    date = sources.find_page_date(soup, response.headers.get("Last-Modified", ""))
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(soup.get_text(" ").split())
    n = sources.add(url, title, date, opened=True, text=text)
    log("🌐", f"Opening [{n}] {url}")
    return truncate(f"Source [{n}] | {title} | page date: {date or 'unknown'}\n{text}")


TOOLS = [web_search, news_search, fetch_page]
