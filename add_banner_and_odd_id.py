import os, re, ast, sqlite3, glob

# 1. تجهيز جدول/عمود بنر الإعلانات والمعرفات الفردية في قاعدة البيانات إن وجدت
db_files = glob.glob("*.db") + glob.glob("**/*.db", recursive=True)
for db in dict.fromkeys(db_files):
    try:
        if not os.path.exists(db) or os.path.getsize(db) == 0:
            continue
        c = sqlite3.connect(db)
        cur = c.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS ad_banners (id INTEGER PRIMARY KEY AUTOINCREMENT, banner_text TEXT DEFAULT '', updated_at TEXT DEFAULT CURRENT_TIMESTAMP)")
        row = cur.execute("SELECT id FROM ad_banners LIMIT 1").fetchone()
        if not row:
            cur.execute("INSERT INTO ad_banners (banner_text) VALUES (?)", ("أهلاً بكم في متجر كرنفال — عروض وتشكيلات مميزة",))
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        for t in tables:
            if "product" in t.lower():
                cols = [x[1] for x in cur.execute(f"PRAGMA table_info({t})").fetchall()]
                if "code" not in cols:
                    cur.execute(f"ALTER TABLE {t} ADD COLUMN code TEXT DEFAULT ''")
                rows = cur.execute(f"SELECT rowid, code FROM {t} ORDER BY rowid ASC").fetchall()
                odd = 1
                for rid, code_val in rows:
                    val = str(code_val or "").strip()
                    if not val.isdigit() or int(val) % 2 == 0:
                        cur.execute(f"UPDATE {t} SET code = ? WHERE rowid = ?", (str(odd), rid))
                    odd += 2
        c.commit()
        c.close()
    except Exception:
        pass

# 2. إضافة مسار حفظ بنر الإعلانات وتوليد المعرف الفردي التلقائي في app.py بأمان
app_path = "app.py"
if os.path.exists(app_path):
    with open(app_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    if "def kayan_next_odd_id(" not in code and "app =" in code:
        addition = """
def kayan_next_odd_id():
    import os, glob, sqlite3
    base = os.path.abspath(os.path.dirname(__file__))
    for db in dict.fromkeys(glob.glob(os.path.join(base, "*.db")) + glob.glob(os.path.join(base, "**", "*.db"), recursive=True)):
        try:
            if not os.path.exists(db) or os.path.getsize(db) == 0:
                continue
            c = sqlite3.connect(db)
            cur = c.cursor()
            tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            max_odd = -1
            for t in tables:
                if "product" in t.lower():
                    cols = [x[1] for x in cur.execute(f"PRAGMA table_info({t})").fetchall()]
                    if "code" in cols:
                        for (val,) in cur.execute(f"SELECT code FROM {t}").fetchall():
                            s = str(val or "").strip()
                            if s.isdigit():
                                n = int(s)
                                if n % 2 == 1 and n > max_odd:
                                    max_odd = n
            c.close()
            return str(max_odd + 2 if max_odd >= 1 else 1)
        except Exception:
            continue
    return "1"

@app.route('/admin/save_banner', methods=['POST'])
def kayan_save_banner():
    import os, glob, sqlite3
    banner_text = (request.form.get('banner_text') or '').strip()
    base = os.path.abspath(os.path.dirname(__file__))
    for db in dict.fromkeys(glob.glob(os.path.join(base, "*.db")) + glob.glob(os.path.join(base, "**", "*.db"), recursive=True)):
        try:
            if not os.path.exists(db):
                continue
            c = sqlite3.connect(db)
            cur = c.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS ad_banners (id INTEGER PRIMARY KEY AUTOINCREMENT, banner_text TEXT DEFAULT '')")
            existing = cur.execute("SELECT id FROM ad_banners LIMIT 1").fetchone()
            if existing:
                cur.execute("UPDATE ad_banners SET banner_text = ? WHERE id = ?", (banner_text, existing[0]))
            else:
                cur.execute("INSERT INTO ad_banners (banner_text) VALUES (?)", (banner_text,))
            c.commit()
            c.close()
        except Exception:
            pass
    return redirect(request.referrer or '/admin')
"""
        if 'if __name__' in code:
            code = code.replace('if __name__', addition + '\nif __name__', 1)
        else:
            code += addition

    ast.parse(code)
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(code if code.endswith("\n") else code + "\n")

# 3. إضافة خانة بنر الإعلانات والمعرف الفردي التلقائي داخل templates/admin.html
admin_path = "templates/admin.html"
if os.path.exists(admin_path):
    with open(admin_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    if 'id="kayan-banner-odd-box"' not in html:
        box_html = """
<div id="kayan-banner-odd-box" style="margin:12px auto;padding:12px;border-radius:12px;background:#111827;border:1px solid #f59e0b;color:#f8fafc;">
  <form method="POST" action="/admin/save_banner" style="display:flex;flex-direction:column;gap:8px;margin-bottom:10px;">
    <label style="font-size:13px;font-weight:bold;color:#fbbf24;">خانة بنر إعلانات</label>
    <div style="display:flex;gap:8px;flex-wrap:wrap;">
      <input type="text" name="banner_text" placeholder="اكتب نص بنر الإعلانات هنا..." style="flex:1;min-width:180px;padding:8px 10px;border-radius:8px;border:1px solid #334155;background:#1e293b;color:#fff;">
      <button type="submit" style="padding:8px 14px;border-radius:8px;border:none;background:#f59e0b;color:#0f172a;font-weight:bold;cursor:pointer;">حفظ البنر</button>
    </div>
  </form>

  <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;padding-top:8px;border-top:1px solid #1e293b;">
    <span style="font-size:12px;color:#cbd5e1;">المعرف التلقائي (أرقام فردية):</span>
    <div style="display:flex;align-items:center;gap:6px;">
      <input type="text" id="kayan-auto-odd-input" name="code" readonly value="1" style="width:74px;padding:6px 8px;text-align:center;border-radius:8px;border:1px solid #38bdf8;background:#0f172a;color:#38bdf8;font-weight:bold;">
      <button type="button" onclick="kayanGenOdd()" style="padding:6px 10px;border-radius:8px;border:1px solid #10b981;background:#065f46;color:#ecfdf5;font-size:12px;font-weight:bold;cursor:pointer;">فردي جديد</button>
    </div>
  </div>
</div>

<script>
function kayanGenOdd() {
  const inp = document.getElementById('kayan-auto-odd-input');
  if (!inp) return;
  let cur = parseInt((inp.value || '1').trim(), 10);
  if (isNaN(cur) || cur < 1) {
    inp.value = '1';
    return;
  }
  inp.value = String(cur % 2 === 1 ? cur + 2 : cur + 1);
}
</script>
"""
        if "<body" in html:
            b_idx = html.find("<body")
            b_end = html.find(">", b_idx)
            if b_end != -1:
                html = html[:b_end + 1] + "\n" + box_html + html[b_end + 1:]
            else:
                html = box_html + "\n" + html
        else:
            html = box_html + "\n" + html

        with open(admin_path, "w", encoding="utf-8") as f:
            f.write(html)

print("تمت إضافة خانة بنر الإعلانات والمعرف الفردي التلقائي بنجاح.")
