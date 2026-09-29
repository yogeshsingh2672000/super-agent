BROWSER_PROMPT = """## Browser skill
- browser_open opens a URL in a real Chrome window. browser_read shows page text and clickable elements.
- browser_click and browser_type take visible text, a placeholder, a label or a CSS selector.
- After every click or submit, call browser_read to see what changed.
- Clicks on payment, checkout or purchase buttons need user approval.
- If you hit a login, 2FA or CAPTCHA, ask the user to complete it in the open window, then continue.
"""
