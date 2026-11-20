import os, sqlite3, glob

# البحث التلقائي عن ملف قاعدة البيانات (.db أو .sqlite) وعن ملف app.py
db_files = glob.glob("*.db") + glob.glob("**/*.db", recursive=True)
db_name = db_files[0] if db_files else "store.db"

app_candidates = [f for f in glob.glob("*.py") if f not in ("patch_update.py", "add_features.py", "update_admin_ui.py", "fix_routes.py")]
app_file = app_candidates[0] if app_candidates else "app.py"

def safe_conn():
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

if os.path.exists(app_file):
    with open(app_file, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # إزالة الدوال السابقة إذا كانت مكررة لتفادي التعارض
    for fn in ["def toggle_status(", "def delete_product(", "def edit_product_route("]:
        if fn in code:
            idx = code.find(fn)
            next_def = code.find("\n@app.route", idx + 1)
            next_main = code.find("\nif __name__", idx + 1)
            ends = [x for x in (next_def, next_main) if x != -1]
            end_idx = min(ends) if ends else len(code)
            code = code[:idx] + code[end_idx:]

    clean_routes = f"""
@app.route('/toggle_status/<int:pid>', methods=['POST'])
def toggle_status(pid):
    try:
        conn = sqlite3.connect({repr(db_name)})
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cols = [c[1] for c in cur.execute("PRAGMA table_info(products)").fetchall()]
        if 'status' not in cols:
            cur.execute("ALTER TABLE products ADD COLUMN status TEXT DEFAULT 'متوفر'")
        row = cur.execute("SELECT status FROM products WHERE id = ?", (pid,)).fetchone()
        if row:
            curr = row['status'] or 'متوفر'
            nxt = 'تم البيع' if curr == 'متوفر' else 'متوفر'
            cur.execute("UPDATE products SET status = ? WHERE id = ?", (nxt, pid))
        conn.commit()
        conn.close()
    except Exception as e:
        print("toggle_status error:", e)
    return redirect(request.referrer or '/admin')

@app.route('/delete_product/<int:pid>', methods=['POST'])
def delete_product(pid):
    try:
        conn = sqlite3.connect({repr(db_name)})
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE id = ?", (pid,))
        conn.commit()
        conn.close()
    except Exception as e:
        print("delete_product error:", e)
    return redirect(request.referrer or '/admin')
"""
    if "if __name__ ==" in code:
        code = code.replace("if __name__ ==", clean_routes + "\nif __name__ ==")
    else:
        code += clean_routes

    with open(app_file, "w", encoding="utf-8") as f:
        f.write(code)

print(f"تم تحديث {app_file} بنجاح باستخدام قاعدة البيانات: {db_name}")
