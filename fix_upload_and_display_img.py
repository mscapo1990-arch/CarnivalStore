import os, re, ast, glob

# 1. التأكد من وجود مجلد static/uploads
os.makedirs(os.path.join("static", "uploads"), exist_ok=True)

# 2. إضافة دالة مساعدة موحدة لحفظ الصور في app.py وتمريرها للمنتجات في index.html
app_path = "app.py"
if os.path.exists(app_path):
    with open(app_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    if "def kayan_save_upload_file(" not in code and "app =" in code:
        saver_block = """
def kayan_save_upload_file(file_obj):
    if not file_obj or not getattr(file_obj, "filename", ""):
        return ""
    import os, time, sqlite3, glob
    from werkzeug.utils import secure_filename
    base = os.path.abspath(os.path.dirname(__file__))
    upload_dir = os.path.join(base, "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    raw_name = os.path.basename(file_obj.filename)
    safe_name = secure_filename(raw_name)
    if not safe_name or "." not in safe_name:
        ext = raw_name.rsplit(".", 1)[1].lower() if "." in raw_name else "jpg"
        safe_name = f"img_{int(time.time()*1000)}.{ext}"
    else:
        name_part, ext_part = safe_name.rsplit(".", 1)
        safe_name = f"{name_part}_{int(time.time())}.{ext_part.lower()}"
    full_path = os.path.join(upload_dir, safe_name)
    file_obj.save(full_path)
    return safe_name

@app.route('/static/uploads/<path:filename>')
def kayan_static_uploads(filename):
    import os
    from flask import send_from_directory
    base = os.path.abspath(os.path.dirname(__file__))
    clean = os.path.basename(filename)
    for folder in [
        os.path.join(base, "static", "uploads"),
        os.path.join(base, "uploads"),
        os.path.join(base, "static")
    ]:
        target = os.path.join(folder, clean)
        if os.path.isfile(target):
            return send_from_directory(folder, clean)
    return "", 404
"""
        if 'if __name__' in code:
            code = code.replace('if __name__', saver_block + '\nif __name__', 1)
        else:
            code += saver_block

    ast.parse(code)
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(code if code.endswith("\n") else code + "\n")

# 3. تحديث عرض الصور داخل templates/index.html ليقرأ من /static/uploads/ تلقائياً إذا كان اسم ملف فقط
index_path = "templates/index.html"
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    if "kayanNormalizeAllImages" not in html:
        fix_script = """
<script>
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('img').forEach(function(img) {
    var src = (img.getAttribute('src') || '').trim();
    if (src && !src.startsWith('http') && !src.startsWith('/') && !src.startsWith('data:')) {
      img.setAttribute('src', '/static/uploads/' + src);
    }
  });
});
</script>
"""
        if "</body>" in html:
            html = html.replace("</body>", fix_script + "\n</body>", 1)
        else:
            html += fix_script

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html)

print("تم تطبيق إصلاح حفظ وعرض الصور بنجاح.")
