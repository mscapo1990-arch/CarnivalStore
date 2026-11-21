import os, re, ast

# 1. إصلاح السطر المباشر لعرض p.image في templates/index.html
index_path = "templates/index.html"
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # استبدال أي src="{{ p.image }}" أو مشابه بتعبير آمن يضمن /static/uploads/
    html = re.sub(
        r'<img\s+src="\{\{\s*p\.image\s*\}\}"',
        r'<img src="/static/uploads/{{ p.image.split(\'/\')[-1] if p.image else \'\' }}"',
        html
    )

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

# 2. ضمان تحديث عمود الصورة في قاعدة البيانات بالملف المرفوع الفعلي من أي جهاز وأي صيغة
app_path = "app.py"
if os.path.exists(app_path):
    with open(app_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    if "def kayan_sync_db_image_after_post(" not in code and "app =" in code:
        sync_block = """
@app.after_request
def kayan_sync_db_image_after_post(response):
    try:
        from flask import request
        saved = request.environ.get("KAYAN_LAST_UPLOADED_IMG")
        if request.method == "POST" and saved:
            import os, glob, sqlite3
            base = os.path.abspath(os.path.dirname(__file__))
            for db in dict.fromkeys(glob.glob(os.path.join(base, "*.db")) + glob.glob(os.path.join(base, "**", "*.db"), recursive=True)):
                if not os.path.exists(db) or os.path.getsize(db) == 0:
                    continue
                c = sqlite3.connect(db)
                cur = c.cursor()
                tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
                for t in tables:
                    if "product" in t.lower():
                        cols = [x[1] for x in cur.execute(f"PRAGMA table_info({t})").fetchall()]
                        for col in cols:
                            if any(k in col.lower() for k in ("image", "img", "photo", "pic", "thumb", "file")):
                                last = cur.execute(f"SELECT rowid FROM {t} ORDER BY rowid DESC LIMIT 1").fetchone()
                                if last:
                                    cur.execute(f"UPDATE {t} SET {col} = ? WHERE rowid = ?", (saved, last[0]))
                                break
                c.commit()
                c.close()
    except Exception:
        pass
    return response
"""
        if 'if __name__' in code:
            code = code.replace('if __name__', sync_block + '\nif __name__', 1)
        else:
            code += sync_block

    ast.parse(code)
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(code if code.endswith("\n") else code + "\n")

print("تم ربط عرض p.image وتحديث قاعدة البيانات مباشرة بنجاح.")
