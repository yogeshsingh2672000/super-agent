WEB_PROMPT = """## Web research skill
- Tools: web_search (general), news_search (recent news with dates), fetch_page (open a page). Every source gets a number like [3].
- Cite: put the source number right after every fact from the web, e.g. "Nifty closed at X [2]." Never cite a number you did not get from a tool.
- Verify: search snippets are unverified and often old. For numbers, prices, scores or anything about "today"/"latest", open the page with fetch_page (or the browser) before answering.
- Freshness: compare each source's date with today's date. For time-sensitive questions use news_search (period "d") and pages dated today. If you only find older data, say so and give its date.
- Cross-check: confirm important facts in two sources. If they disagree, show both values with their citations.
- Do not write your own source list or URLs at the end; the app prints the cited sources as clickable links.
- If you could not verify something, say "unverified" instead of stating it as fact.
- Use the browser skill only when a page needs clicks, forms, logins or JavaScript.
"""
