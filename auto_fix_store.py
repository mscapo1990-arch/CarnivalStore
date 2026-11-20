import os, glob, sqlite3

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 1. اكتشاف ملف قاعدة البيانات وتأمين وجود عمود status
db_files = glob.glob("*.db") + glob.glob("**/*.db", recursive=True)
db_path = db_files[0] if db_files else "store.db"

conn = sqlite3.connect(db_path)
cur = conn.cursor()
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
for t in tables:
    if "product" in t.lower():
        cols = [c[1] for c in cur.execute(f"PRAGMA table_info({t})").fetchall()]
        if "status" not in cols:
            cur.execute(f"ALTER TABLE {t} ADD COLUMN status TEXT DEFAULT 'متوفر'")
        if "image" not in cols:
            cur.execute(f"ALTER TABLE {t} ADD COLUMN image TEXT DEFAULT ''")
conn.commit()
conn.close()

# 2. تحديث ملف التطبيق الرئيسي لضمان مسار الصور ودعم التعديل والحذف وتبديل الحالة
py_files = [
    f for f in glob.glob("*.py")
    if f not in ("patch_update.py", "add_features.py", "update_admin_ui.py", "fix_routes.py", "fix_images.py", "auto_fix_store.py")
]

for pf in py_files:
    with open(pf, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    if "from flask import" in code and "send_from_directory" not in code:
        code = code.replace("from flask import", "from flask import send_from_directory,", 1)

    upload_route = f"""
@app.route('/static/uploads/<path:filename>')
def serve_static_upload(filename):
    base = os.path.abspath(os.path.dirname(__file__))
    return send_from_directory(os.path.join(base, 'static', 'uploads'), filename)

@app.route('/toggle_status/<int:pid>', methods=['POST'])
def toggle_product_status(pid):
    try:
        c = sqlite3.connect({repr(db_path)})
        c.row_factory = sqlite3.Row
        cur = c.cursor()
        row = cur.execute("SELECT status FROM products WHERE id = ?", (pid,)).fetchone()
        if row:
            curr = row['status'] or 'متوفر'
            nxt = 'تم البيع' if curr == 'متوفر' else 'متوفر'
            cur.execute("UPDATE products SET status = ? WHERE id = ?", (nxt, pid))
        c.commit()
        c.close()
    except Exception as e:
        print("status err:", e)
    return redirect(request.referrer or '/admin')

@app.route('/delete_product/<int:pid>', methods=['POST'])
def delete_product_item(pid):
    try:
        c = sqlite3.connect({repr(db_path)})
        cur = c.cursor()
        cur.execute("DELETE FROM products WHERE id = ?", (pid,))
        c.commit()
        c.close()
    except Exception as e:
        print("delete err:", e)
    return redirect(request.referrer or '/admin')
"""
    if "def serve_static_upload(" not in code and "app =" in code:
        if "if __name__" in code:
            code = code.replace("if __name__", upload_route + "\nif __name__", 1)
        else:
            code += upload_route

    with open(pf, "w", encoding="utf-8") as f:
        f.write(code)

# 3. تحديث قوالب HTML لإظهار الصور بدون إخفائها وإضافة أزرار الحالة والحذف
html_files = glob.glob("**/*.html", recursive=True)
for hf in html_files:
    with open(hf, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    html = html.replace("onerror=\"this.style.display='none'\"", "")
    html = html.replace("onerror='this.style.display=\"none\"'", "")

    if "لوحة التحكم" in html and "kayan-quick-bar" not in html:
        bar = """
<div id="kayan-quick-bar" style="margin-top:14px;padding:10px;border-radius:10px;border:1px solid #334155;background:#1e293b;display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
  <form method="POST" action="/toggle_status/1" style="margin:0;">
    <button type="submit" style="padding:7px 12px;border-radius:8px;border:none;background:#10b981;color:#fff;font-weight:bold;cursor:pointer;">تبديل متوفر / تم البيع</button>
  </form>
  <form method="POST" action="/delete_product/1" style="margin:0;" onsubmit="return confirm('تأكيد الحذف؟');">
    <button type="submit" style="padding:7px 12px;border-radius:8px;border:none;background:#ef4444;color:#fff;font-weight:bold;cursor:pointer;">حذف منتج</button>
  </form>
</div>
"""
        if "</body>" in html:
            html = html.replace("</body>", bar + "\n</body>", 1)
        else:
            html += bar

    with open(hf, "w", encoding="utf-8") as f:
        f.write(html)

print("تم التحديث الشامل بنجاح.")
