import os, re, ast

# 1. إضافة context_processor في app.py لتمرير ad_banner لجميع القوالب (ومنها index.html)
app_path = "app.py"
if os.path.exists(app_path):
    with open(app_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    if "def kayan_inject_banner(" not in code and "app =" in code:
        ctx_block = """
@app.context_processor
def kayan_inject_banner():
    import os, glob, sqlite3
    txt = ""
    try:
        base = os.path.abspath(os.path.dirname(__file__))
        for db in dict.fromkeys(glob.glob(os.path.join(base, "*.db")) + glob.glob(os.path.join(base, "**", "*.db"), recursive=True)):
            if not os.path.exists(db) or os.path.getsize(db) == 0:
                continue
            c = sqlite3.connect(db)
            cur = c.cursor()
            tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            if "ad_banners" in tables:
                row = cur.execute("SELECT banner_text FROM ad_banners ORDER BY id DESC LIMIT 1").fetchone()
                if row and row[0]:
                    txt = str(row[0]).strip()
                    c.close()
                    break
            c.close()
    except Exception:
        pass
    return {"ad_banner": txt}
"""
        if 'if __name__' in code:
            code = code.replace('if __name__', ctx_block + '\nif __name__', 1)
        else:
            code += ctx_block

    ast.parse(code)
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(code if code.endswith("\n") else code + "\n")

# 2. إضافة شريط بنر الإعلانات في templates/index.html
index_path = "templates/index.html"
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    if 'id="kayan-store-banner"' not in html:
        banner_html = """
{% if ad_banner %}
<div id="kayan-store-banner" style="margin:10px auto;max-width:960px;padding:10px 14px;border-radius:10px;background:linear-gradient(90deg,#1e293b,#0f172a);border:1px solid #f59e0b;color:#fbbf24;text-align:center;font-size:13px;font-weight:bold;box-shadow:0 2px 8px rgba(0,0,0,0.25);">
  {{ ad_banner }}
</div>
{% endif %}
"""
        if "<body" in html:
            b_idx = html.find("<body")
            b_end = html.find(">", b_idx)
            if b_end != -1:
                html = html[:b_end + 1] + "\n" + banner_html + html[b_end + 1:]
            else:
                html = banner_html + "\n" + html
        else:
            html = banner_html + "\n" + html

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html)

print("تم ربط بنر الإعلانات ليظهر في واجهة المتجر بنجاح.")
