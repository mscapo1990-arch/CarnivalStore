import os, re, ast

path = "app.py"
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

# 1. إضافة session إلى استيراد flask
if "from flask import" in code:
    m = re.search(r'^from\s+flask\s+import\s+([^\n]+)', code, flags=re.MULTILINE)
    if m and "session" not in m.group(1):
        old_line = m.group(0)
        new_line = old_line + ", session"
        code = code.replace(old_line, new_line, 1)
else:
    code = "from flask import session\n" + code

# 2. ضمان وجود app.secret_key بعد تعريف app
if "app =" in code and "secret_key" not in code:
    code = re.sub(
        r'^(\s*app\s*=\s*Flask\([^\n]*\))',
        r'\1\napp.secret_key = os.environ.get("SECRET_KEY", "carnival-store-secret-2026")',
        code,
        count=1,
        flags=re.MULTILINE
    )

ast.parse(code)
with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("تم إصلاح استيراد session و secret_key في app.py بنجاح.")
