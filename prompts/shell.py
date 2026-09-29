SHELL_PROMPT = """## Shell skill
- run_command runs Windows PowerShell. Use PowerShell syntax (Get-ChildItem, Select-String, $env:VAR).
- Prefer read-only commands to inspect first. Run one clear command at a time.
- Destructive or install commands need user approval; system-damaging ones are blocked.
- Long-running programs: use Start-Process so the command returns.
"""
