import os, glob, sqlite3

# 1. تحديث زر تعديل عرض ووظيفته داخل templates/admin.html
admin_path = "templates/admin.html"
if os.path.exists(admin_path):
    with open(admin_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    old_fn = """function toggleStripView() {
  stripCompact = !stripCompact;
  const box = document.getElementById('kayan-strip-items');
  if (!box) return;
  if (stripCompact) {
    box.style.flexDirection = 'row';
    box.style.overflowX = 'auto';
  } else {
    box.style.flexDirection = 'column';
    box.style.overflowX = 'visible';
  }
}"""

    new_fn = """function toggleStripView() {
  stripCompact = !stripCompact;
  const box = document.getElementById('kayan-strip-items');
  const strip = document.getElementById('kayan-top-strip');
  if (!box) return;
  if (stripCompact) {
    box.style.flexDirection = 'row';
    box.style.overflowX = 'auto';
    box.style.gap = '10px';
    if (strip) strip.style.borderColor = '#38bdf8';
  } else {
    box.style.flexDirection = 'column';
    box.style.overflowX = 'visible';
    box.style.gap = '8px';
    if (strip) strip.style.borderColor = '#f59e0b';
  }
}"""

    if old_fn in html:
        html = html.replace(old_fn, new_fn)

    with open(admin_path, "w", encoding="utf-8") as f:
        f.write(html)

# 2. التأكد من تمرير المنتجات من قاعدة البيانات إلى admin.html في حال لم تكن ممررة
db_files = glob.glob("*.db") + glob.glob("**/*.db", recursive=True)
db_path = db_files[0] if db_files else "store.db"

py_files = [
    f for f in glob.glob("*.py")
    if f not in (
        "patch_update.py", "add_features.py", "update_admin_ui.py",
        "fix_routes.py", "fix_images.py", "auto_fix_store.py",
        "fix_img_link.py", "fix_index_img.py", "force_upload_fix.py",
        "update_admin_panel.py", "apply_custom_admin.py", "set_odd_id_logic.py",
        "top_admin_bar.py", "fix_top_strip_btn.py"
    )
]

for pf in py_files:
    with open(pf, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    if "@app.route('/admin'" in code and "def _load_admin_products(" not in code:
        loader = f"""
def _load_admin_products():
    try:
        import sqlite3
        c = sqlite3.connect({repr(db_path)})
        c.row_factory = sqlite3.Row
        cur = c.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        for t in tables:
            if "product" in t.lower():
                rows = cur.execute(f"SELECT * FROM {{t}} ORDER BY id DESC").fetchall()
                c.close()
                return [dict(r) for r in rows]
        c.close()
    except Exception:
        pass
    return []
"""
        code = loader + "\n" + code
        code = code.replace(
            "render_template('admin.html'",
            "render_template('admin.html', products=_load_admin_products()"
        ).replace(
            'render_template("admin.html"',
            'render_template("admin.html", products=_load_admin_products()'
        )
        with open(pf, "w", encoding="utf-8") as f:
            f.write(code)

print("تم تحديث زر تعديل عرض وربط جلب المنتجات بنجاح.")
