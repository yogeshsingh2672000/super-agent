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


NO_SCREEN_NOTE = "## Screen control\n- Not available with this model (no image input). Use shell, files, web and browser tools instead.\n"


def build_system_prompt(memories_text: str, vision: bool = True) -> str:
    prompts = SKILL_PROMPTS if vision else [NO_SCREEN_NOTE if p is SCREEN_PROMPT else p for p in SKILL_PROMPTS]
    skills = "\n".join(prompts)
    today = date.today().strftime("%A, %d %B %Y")
    return f"{CORE_PROMPT}\nToday's date: {today}\n\n{skills}\n## Saved memories (always follow)\n{memories_text}\n"
