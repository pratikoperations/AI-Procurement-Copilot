from pathlib import Path

path = Path("app.py")
text = path.read_text(encoding="utf-8")
old = '"""AI Procurement Copilot — Portfolio Edition v1.0."""'
new = '"""AI Procurement Copilot — Portfolio Edition v1.0.1."""'
if old not in text:
    raise SystemExit("Expected app.py docstring not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Updated app.py release docstring")
