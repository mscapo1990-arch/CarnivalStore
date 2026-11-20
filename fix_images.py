import os, glob

os.makedirs("static/uploads", exist_ok=True)

# 1. إضافة مسار صريح لخدمة الصور من static/uploads في ملف التطبيق الرئيسي
py_files = [f for f in glob.glob("*.py") if f not in ("patch_update.py", "add_features.py", "update_admin_ui.py", "fix_routes.py", "fix_images.py")]
for pf in py_files:
    with open(pf, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()
    if "def serve_upload(" not in code and "app =" in code:
        route_code = """
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    from flask import send_from_directory
    import os
    base = os.path.abspath(os.path.dirname(__file__))
    return send_from_directory(os.path.join(base, 'static', 'uploads'), filename)
"""
        if "if __name__" in code:
            code = code.replace("if __name__", route_code + "\nif __name__")
        else:
            code += route_code
        with open(pf, "w", encoding="utf-8") as f:
            f.write(code)

# 2. ضبط عرض الصور في قوالب HTML بحيث تتعامل مع اسم الملف أو الرابط المباشر بأمان
html_files = glob.glob("**/*.html", recursive=True)
for hf in html_files:
    with open(hf, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
    if "<img" in html and "onerror=" not in html:
        html = html.replace("<img ", "<img onerror=\"this.style.display='none'\" ")
        with open(hf, "w", encoding="utf-8") as f:
            f.write(html)

print("تم تحديث مسارات الصور في الملفات بنجاح.")
