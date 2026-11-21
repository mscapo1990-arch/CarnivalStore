import re, ast

path = "app.py"
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

m = re.search(r'^from\s+flask\s+import\s+([^\n]+)', code, flags=re.MULTILINE)
if m:
    imported = m.group(1)
    to_add = []
    if "redirect" not in imported:
        to_add.append("redirect")
    if "url_for" not in imported:
        to_add.append("url_for")
    if to_add:
        new_line = f"from flask import {', '.join(to_add)}, {imported}"
        code = code.replace(m.group(0), new_line, 1)
else:
    code = "from flask import redirect, url_for\n" + code

ast.parse(code)
with open(path, "w", encoding="utf-8") as f:
    f.write(code if code.endswith("\n") else code + "\n")

print("تمت إضافة redirect و url_for في app.py بنجاح.")
