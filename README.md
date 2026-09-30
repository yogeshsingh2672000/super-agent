# Super Agent

Autonomous terminal agent built on LangChain. It runs on AWS Bedrock, OpenAI, Ollama or LM Studio. It plans, uses your PC, browses the web, controls the screen, remembers what you tell it, and tracks its own cost.

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
.venv\Scripts\python main.py                      # startup menu: pick a provider
.venv\Scripts\python main.py --provider ollama    # skip the menu
```

## Providers
You pick only the provider at startup. The model comes from that provider's section in `.env` (`# bedrock`, `# openai`, `# ollama`, `# lmstudio`). Each section holds its own credentials, model, prices and options, so they never mix. `DEFAULT_PROVIDER` picks the default row.

The menu shows each provider's model, price, and whether it's ready. It refuses a provider whose credentials or model are missing, or whose local model isn't installed or loaded, and tells you what to fix.

| Provider | Needs | Cost |
|---|---|---|
| AWS Bedrock | AWS keys in `.env` or `aws configure` | `BEDROCK_*_PRICE_PER_M` |
| OpenAI | `OPENAI_API_KEY`, `OPENAI_MODEL` | `OPENAI_*_PRICE_PER_M` |
| Ollama | Ollama app running, a model pulled (`ollama pull qwen3:8b`) | free |
| LM Studio | a model loaded, Developer > Start Server | free |

- **Local models must support tool calling** (e.g. qwen3, llama3.1), or the agent can't use tools. In LM Studio, set the context length to at least 16k when loading the model.
- **Screen control:** `*_VISION=false` removes it, for models that can't read images. gpt-oss models are always treated as text-only.
Commands: `/budget`, `/memory`, `/stats`, `/new` (fresh chat, memories kept), `/exit`. `Ctrl+C` stops the current task.

While a task runs, a live line shows CPU, system RAM, and the RAM used by the agent and its browser/shell processes. It updates every second.

## Skills
| Skill | Tools |
|---|---|
| Files | list_directory, read_file, write_file, delete_path |
| Shell | run_command (PowerShell) |
| Web | web_search, news_search, fetch_page |
| Browser | browser_open, browser_read, browser_click, browser_type, browser_press_key |
| Screen | take_screenshot, mouse_click, type_text, press_keys, scroll |
| Memory | remember, recall, forget |
| Budget | record_expense, record_income, budget_status |

## Sources
- Every web result gets a number `[n]`. The agent cites them in its answer.
- After the answer, a compact **📚 Sources** panel lists the cited sources as clickable links. Ctrl+click them in Windows Terminal.
- Press **F2** at the `You:` prompt to expand it: you get dates, full URLs and a "Read more" excerpt from each page. Press F2 again to collapse.
- `/sources` expands all sources; `/sources 2` shows a longer excerpt of source [2]. Use these where F2 isn't supported, such as Git Bash.
- Each source is marked ✅ opened or ⚠️ snippet only, with its date.
- Every number in the answer is checked against the text of its cited source. Numbers that aren't found are flagged ❌ in red.

## Safety
- **Blocked**: formatting drives, deleting system folders, drive roots or the home folder, registry deletes, shutdown.
- **Asks y/n**: deleting anything, installing or uninstalling software, sending mail, payment or checkout clicks.
- **Screen**: move the mouse to a screen corner to abort screen control.
- **Spend cap**: `MAX_DAILY_SPEND` in `.env` stops the agent when today's cost reaches it.

## Costs
- Token cost uses the chosen provider's `*_INPUT_PRICE_PER_M` / `*_OUTPUT_PRICE_PER_M` from `.env`. Local models cost $0.
- Real money the agent spends or earns is recorded by the agent itself.
- Daily totals are saved in `data/ledger.json`.

## Layout
```
main.py            terminal chat
config.py          shared settings from .env
providers/         one file per model provider (bedrock, openai, ollama, lmstudio)
agent/builder.py   model + tools + prompt
prompts/           one prompt per skill
tools/             one file per skill
utils/             logger, safety, ledger, memory, cost tracker, helpers
data/  logs/       memory, ledger, daily activity logs
```
