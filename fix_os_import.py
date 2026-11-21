import ast

path = "app.py"
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

lines = code.splitlines()
has_import_os = any(l.strip() == "import os" or l.strip().startswith("import os ") for l in lines)

if not has_import_os:
    code = "import os\n" + code

ast.parse(code)
with open(path, "w", encoding="utf-8") as f:
    f.write(code if code.endswith("\n") else code + "\n")

print("تمت إضافة import os في بداية app.py بنجاح.")
