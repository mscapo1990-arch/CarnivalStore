import os, glob

# 1. تنظيف أي تعبيرات Jinja قد تسبب خطأ إذا كان الكائن dict أو tuple أو None في admin.html
admin_path = "templates/admin.html"
if os.path.exists(admin_path):
    with open(admin_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # استبدال الوصول المباشر للخصائص غير الآمنة داخل الشريط العلوي بتعبيرات آمنة
    html = html.replace("p is mapping", "p is defined and p is mapping")
    html = html.replace("p.id is defined", "p is defined and p.id is defined")
    html = html.replace("p.name is defined", "p is defined and p.name is defined")
    html = html.replace("p.image is defined", "p is defined and p.image is defined")
    html = html.replace("p.code is defined", "p is defined and p.code is defined")
    html = html.replace("p.ad_status is defined", "p is defined and p.ad_status is defined")
    html = html.replace("p.status is defined", "p is defined and p.status is defined")
    html = html.replace("p.whatsapp is defined", "p is defined and p.whatsapp is defined")

    with open(admin_path, "w", encoding="utf-8") as f:
        f.write(html)

# 2. إضافة معالج أخطاء واضح في app.py لمنع توقف المسارات عند استثناءات بسيطة
py_files = [
    f for f in glob.glob("*.py")
    if f not in (
        "patch_update.py", "add_features.py", "update_admin_ui.py",
        "fix_routes.py", "fix_images.py", "auto_fix_store.py",
        "fix_img_link.py", "fix_index_img.py", "force_upload_fix.py",
        "update_admin_panel.py", "apply_custom_admin.py", "set_odd_id_logic.py",
        "top_admin_bar.py", "fix_top_strip_btn.py", "fix_strip_products_and_btn.py",
        "repair_app_syntax.py", "fix_app_defined.py", "fix_internal_500.py"
    )
]

for pf in py_files:
    with open(pf, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    if "app =" in code and "@app.errorhandler(500)" not in code:
        handler = """
@app.errorhandler(500)
def handle_500_err(e):
    return f"<h3>تنبيه في التطبيق</h3><pre>{e}</pre>", 500
"""
        if 'if __name__' in code:
            code = code.replace('if __name__', handler + '\nif __name__', 1)
        else:
            code += handler

        with open(pf, "w", encoding="utf-8") as f:
            f.write(code)

print("تم تطبيق معالجة أخطاء 500 وتأمين قوالب العرض بنجاح.")
