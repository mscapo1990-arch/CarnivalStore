import os, re

path = "app.py"
if not os.path.exists(path):
    print("لم يتم العثور على app.py")
    raise SystemExit(1)

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

# إذا كان هناك تعريف لـ app في مكان متأخر، نضمن وجود تعريف مبكر أو نقل سطر app = Flask(...) للأعلى
app_assign_match = re.search(r'^(\s*app\s*=\s*Flask\([^\n]*\))', code, flags=re.MULTILINE)
first_route_match = re.search(r'^\s*@app\.route\b', code, flags=re.MULTILINE)

if app_assign_match and first_route_match and app_assign_match.start() > first_route_match.start():
    app_line = app_assign_match.group(1)
    code_without_line = code[:app_assign_match.start()] + code[app_assign_match.end():]
    # إزالة الأسطر الفارغة الزائدة الناتجة
    code_without_line = re.sub(r'\n{3,}', '\n\n', code_without_line)
    # وضع تعريف app مباشرة بعد استيراد Flask أو بعد أول سطر import
    imp_match = re.search(r'(?:^|\n)(?:from\s+flask\s+import[^\n]*|import\s+flask[^\n]*)', code_without_line)
    if imp_match:
        ins_pos = imp_match.end()
        code = code_without_line[:ins_pos] + "\n" + app_line + code_without_line[ins_pos:]
    else:
        code = app_line + "\n" + code_without_line
elif not app_assign_match and first_route_match:
    fallback = "\nfrom flask import Flask\napp = Flask(__name__)\n"
    imp_match = re.search(r'(?:^|\n)(?:from\s+flask\s+import[^\n]*|import\s+flask[^\n]*)', code)
    if imp_match:
        ins_pos = imp_match.end()
        code = code[:ins_pos] + "\napp = Flask(__name__)" + code[ins_pos:]
    else:
        code = fallback + code

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

# فحص الصياغة والتأكد من عدم وجود NameError مبدئي
import ast
ast.parse(code)
print("تم إصلاح تعريف app في app.py بنجاح.")
