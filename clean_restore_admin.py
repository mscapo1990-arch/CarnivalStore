import os, re, ast

# 1. تنظيف app.py من أي دوال مكررة أو متغيرات ناقصة
app_path = "app.py"
if os.path.exists(app_path):
    with open(app_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # إزالة معالج 500 الذي يطبع صفحة خام إذا كان يسبب التباساً، وضمان وجود os و session و secret_key
    lines = code.splitlines()
    if not any(l.strip() == "import os" or l.strip().startswith("import os ") for l in lines):
        code = "import os\n" + code

    if "from flask import" in code:
        m = re.search(r'^from\s+flask\s+import\s+([^\n]+)', code, flags=re.MULTILINE)
        if m and "session" not in m.group(1):
            code = code.replace(m.group(0), m.group(0) + ", session", 1)

    if "app =" in code and "secret_key" not in code:
        code = re.sub(
            r'^(\s*app\s*=\s*Flask\([^\n]*\))',
            r'\1\napp.secret_key = os.environ.get("SECRET_KEY", "carnival-store-secret-2026")',
            code,
            count=1,
            flags=re.MULTILINE
        )

    ast.parse(code)
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(code if code.endswith("\n") else code + "\n")

print("تم ترتيب app.py بنجاح.")
