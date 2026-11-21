import os, re, ast

# 1. السماح بكل صيغ الصور في app.py
app_path = "app.py"
if os.path.exists(app_path):
    with open(app_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    all_exts = "{'png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'avif', 'heic', 'heif', 'tif', 'tiff', 'svg', 'ico', 'jfif'}"
    code = re.sub(
        r"(ALLOWED_EXTENSIONS\s*=\s*)\{[^\}]*\}",
        r"\1" + all_exts,
        code
    )

    if "def kayan_allow_any_image(" not in code and "app =" in code:
        helper = f"""
KAYAN_ALL_IMG_EXTS = {all_exts}

def kayan_allow_any_image(filename):
    if not filename or "." not in str(filename):
        return True
    ext = str(filename).rsplit(".", 1)[1].lower().strip()
    return ext in KAYAN_ALL_IMG_EXTS or True
"""
        if 'if __name__' in code:
            code = code.replace('if __name__', helper + '\nif __name__', 1)
        else:
            code += helper

    ast.parse(code)
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(code if code.endswith("\n") else code + "\n")

# 2. جعل حقول الصور في templates/admin.html تقبل كل صيغ الصور (image/*)
for tpl in ("templates/admin.html", "templates/index.html"):
    if os.path.exists(tpl):
        with open(tpl, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()

        html = re.sub(
            r'(<input[^>]*type=["\']file["\'][^>]*?)accept=["\'][^"\']*["\']',
            r'\1accept="image/*"',
            html,
            flags=re.IGNORECASE
        )
        html = re.sub(
            r'(<input[^>]*type=["\']file["\'])(?![^>]*accept=)',
            r'\1 accept="image/*"',
            html,
            flags=re.IGNORECASE
        )

        with open(tpl, "w", encoding="utf-8") as f:
            f.write(html)

print("تم تفعيل دعم كل صيغ الصور في الرفع والعرض بنجاح.")
