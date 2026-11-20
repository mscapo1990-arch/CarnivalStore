import os

app_file = "app.py"
if os.path.exists(app_file):
    with open(app_file, "r", encoding="utf-8") as f:
        code = f.read()

    # ضمان استخدام المسار المطلق لمجلد الصور داخل static/uploads
    if "BASE_DIR = os.path.abspath(os.path.dirname(__file__))" not in code:
        header = (
            "import os\n"
            "BASE_DIR = os.path.abspath(os.path.dirname(__file__))\n"
            "UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')\n"
            "os.makedirs(UPLOAD_FOLDER, exist_ok=True)\n"
        )
        code = header + code

    with open(app_file, "w", encoding="utf-8") as f:
        f.write(code)

os.makedirs("static/uploads", exist_ok=True)
print("تم تحديث المسارات وتجهيز مجلد الصور بنجاح.")
