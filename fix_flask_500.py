import os, ast, glob

# 1. فحص صياغة جميع ملفات بايثون في المشروع
for py in sorted(glob.glob("*.py")):
    try:
        with open(py, "r", encoding="utf-8", errors="ignore") as f:
            src = f.read()
        ast.parse(src)
    except SyntaxError as e:
        print(f"خطأ صياغة في {py} السطر {e.lineno}: {e.msg}")

# 2. التأكد من أن app.py لا يحتوي على تعبيرات Jinja خاطئة أو استدعاءات ترفع 500
app_path = "app.py"
if os.path.exists(app_path):
    with open(app_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # التأكد من أن دالة معالجة خطأ 500 تطبع التفاصيل بوضوح إذا حدث خطأ داخل بايثون
    if "@app.errorhandler(500)" not in code and "app =" in code:
        err_block = """
@app.errorhandler(500)
def internal_error(error):
    import traceback
    return f"<h3>خطأ في تطبيق بايثون</h3><pre>{traceback.format_exc()}</pre>", 500
"""
        if 'if __name__' in code:
            code = code.replace('if __name__', err_block + '\nif __name__', 1)
        else:
            code += err_block

        with open(app_path, "w", encoding="utf-8") as f:
            f.write(code)

# 3. تنظيف أي كود Jinja غير مدعوم داخل templates/admin.html
admin_path = "templates/admin.html"
if os.path.exists(admin_path):
    with open(admin_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    html = html.replace("p is defined and p is defined and p is mapping", "p is defined and p is mapping")
    with open(admin_path, "w", encoding="utf-8") as f:
        f.write(html)

print("تم فحص كود بايثون ورفع التعديلات الجاهزة.")
