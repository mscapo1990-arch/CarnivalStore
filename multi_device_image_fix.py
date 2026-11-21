import os, ast

app_path = "app.py"
if os.path.exists(app_path):
    with open(app_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    if "def kayan_multi_ip_img_handler(" not in code and "app =" in code:
        block = """
def kayan_multi_ip_img_handler():
    try:
        from flask import request
        if request.method != "POST" or not getattr(request, "files", None):
            return
        import os, time, uuid
        from werkzeug.utils import secure_filename
        base = os.path.abspath(os.path.dirname(__file__))
        up_dir = os.path.join(base, "static", "uploads")
        os.makedirs(up_dir, exist_ok=True)
        for _, fobj in request.files.items():
            if fobj and getattr(fobj, "filename", ""):
                raw = os.path.basename(fobj.filename)
                safe = secure_filename(raw)
                ext = ""
                if "." in raw:
                    ext = raw.rsplit(".", 1)[1].lower().strip()
                if not ext and safe and "." in safe:
                    ext = safe.rsplit(".", 1)[1].lower().strip()
                if not ext:
                    ext = "jpg"
                uniq = f"img_{int(time.time())}_{uuid.uuid4().hex[:6]}.{ext}"
                full_path = os.path.join(up_dir, uniq)
                fobj.save(full_path)
                try:
                    fobj.stream.seek(0)
                except Exception:
                    pass
                request.environ["KAYAN_LAST_UPLOADED_IMG"] = uniq
                break
    except Exception:
        pass

@app.before_request
def kayan_before_any_ip_post():
    kayan_multi_ip_img_handler()
"""
        if 'if __name__' in code:
            code = code.replace('if __name__', block + '\nif __name__', 1)
        else:
            code += block

    ast.parse(code)
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(code if code.endswith("\n") else code + "\n")

print("تم تثبيت نظام حفظ الصور لأي IP وجهاز بأي صيغة بنجاح.")
