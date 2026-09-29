from datetime import date

from prompts.browser import BROWSER_PROMPT
from prompts.budget import BUDGET_PROMPT
from prompts.files import FILES_PROMPT
from prompts.memory import MEMORY_PROMPT
from prompts.screen import SCREEN_PROMPT
from prompts.shell import SHELL_PROMPT
from prompts.system import CORE_PROMPT
from prompts.web import WEB_PROMPT

SKILL_PROMPTS = [FILES_PROMPT, SHELL_PROMPT, WEB_PROMPT, BROWSER_PROMPT, SCREEN_PROMPT, MEMORY_PROMPT, BUDGET_PROMPT]


def build_system_prompt(memories_text: str) -> str:
    skills = "\n".join(SKILL_PROMPTS)
    today = date.today().strftime("%A, %d %B %Y")
    return f"{CORE_PROMPT}\nToday's date: {today}\n\n{skills}\n## Saved memories (always follow)\n{memories_text}\n"
