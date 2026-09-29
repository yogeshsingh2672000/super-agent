# Super Agent

Autonomous terminal agent (LangChain + Claude on AWS Bedrock). It plans, uses your PC, browses the web, controls the screen, remembers what you tell it, and tracks its own cost.

## Setup
```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m playwright install chromium
Copy-Item .env.example .env   # then edit if needed
```
AWS credentials come from `aws configure` (~/.aws) unless set in `.env`.

## Run
```powershell
.venv\Scripts\python main.py
```
Commands: `/budget`, `/memory`, `/new` (fresh chat, memories kept), `/exit`. `Ctrl+C` stops the current task.

## Skills
| Skill | Tools |
|---|---|
| Files | list_directory, read_file, write_file, delete_path |
| Shell | run_command (PowerShell) |
| Web | web_search, fetch_page |
| Browser | browser_open, browser_read, browser_click, browser_type, browser_press_key |
| Screen | take_screenshot, mouse_click, type_text, press_keys, scroll |
| Memory | remember, recall, forget |
| Budget | record_expense, record_income, budget_status |

## Safety
- **Blocked**: formatting drives, deleting system folders, drive roots or the home folder, registry deletes, shutdown.
- **Asks y/n**: deleting anything, installing or uninstalling software, sending mail, payment or checkout clicks.
- **Screen**: move the mouse to a screen corner to abort screen control.
- **Spend cap**: `MAX_DAILY_SPEND` in `.env` stops the agent when today's cost reaches it.

## Costs
- Token cost uses `INPUT_PRICE_PER_M` / `OUTPUT_PRICE_PER_M` from `.env`. Check your Bedrock pricing and update them.
- Real money the agent spends or earns is recorded by the agent itself.
- Daily totals are saved in `data/ledger.json`.

## Layout
```
main.py            terminal chat
config.py          settings from .env
agent/builder.py   model + tools + prompt
prompts/           one prompt per skill
tools/             one file per skill
utils/             logger, safety, ledger, memory, cost tracker, helpers
data/  logs/       memory, ledger, daily activity logs
```
