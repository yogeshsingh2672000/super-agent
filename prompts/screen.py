SCREEN_PROMPT = """## Screen control skill
- Use only for desktop apps the other skills cannot reach. It is slow and costly.
- take_screenshot first. Coordinates you pass to mouse_click must come from the latest screenshot.
- After each click or key press, take a new screenshot to confirm the effect.
- press_keys takes combos like "ctrl+s", "alt+tab", "enter". Launch apps with run_command (Start-Process) when possible.
"""
