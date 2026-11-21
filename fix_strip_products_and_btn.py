import os, glob, sqlite3

# 1. البحث عن جميع ملفات .db أو .sqlite في المشروع
db_candidates = glob.glob("*.db") + glob.glob("**/*.db", recursive=True) + glob.glob("*.sqlite*", recursive=True)
db_candidates = list(dict.fromkeys(db_candidates))

# 2. تحديث templates/admin.html لعرض المنتجات حتى لو كانت تحت اسم متغير آخر، وجعل زر تعديل عرض يستجيب فوراً
admin_path = "templates/admin.html"
if os.path.exists(admin_path):
    with open(admin_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    # استبدال كتلة الشريط العلوي لضمان استجابة الزر وعرض المنتجات
    start_tok = '<div id="kayan-top-strip"'
    end_tok = '<!-- END KAYAN TOP STRIP -->'
    if start_tok in html and end_tok in html:
        s = html.find(start_tok)
        e = html.find(end_tok, s) + len(end_tok)

        new_block = """
<div id="kayan-top-strip" style="margin:10px auto 14px auto;padding:10px 12px;border-radius:12px;background:#0f172a;border:1px solid #f59e0b;color:#f8fafc;">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:8px;">
    <span id="kayan-strip-title" style="font-size:13px;font-weight:bold;color:#fbbf24;">شريط المنتجات العلوي</span>
    <button type="button" id="kayan-toggle-view-btn" onclick="kayanToggleView()" style="padding:5px 11px;border-radius:7px;border:1px solid #38bdf8;background:#1e293b;color:#38bdf8;font-size:12px;font-weight:bold;cursor:pointer;">تعديل عرض</button>
  </div>

  <div id="kayan-strip-items" style="display:flex;flex-direction:column;gap:8px;">
    {% set list_items = products if (products is defined and products) else (items if (items is defined and items) else []) %}
    {% if list_items %}
      {% for p in list_items %}
        {% set pid = p.id if p.id is defined else (p['id'] if p is mapping and 'id' in p else loop.index) %}
        {% set pname = p.name if p.name is defined else (p['name'] if p is mapping and 'name' in p else (p.title if p.title is defined else 'منتج')) %}
        {% set pimg = p.image if p.image is defined else (p['image'] if p is mapping and 'image' in p else '') %}
        {% set pcode = p.code if p.code is defined else (p['code'] if p is mapping and 'code' in p and p['code'] else (loop.index * 2 - 1)) %}
        {% set pad = p.ad_status if p.ad_status is defined else (p['ad_status'] if p is mapping and 'ad_status' in p and p['ad_status'] else (p.status if p.status is defined else 'متوفر')) %}
        {% set pwa = p.whatsapp if p.whatsapp is defined else (p['whatsapp'] if p is mapping and 'whatsapp' in p and p['whatsapp'] else '') %}
        {% set img_src = pimg if pimg and (pimg.startswith('http') or pimg.startswith('/')) else ('/static/uploads/' ~ pimg if pimg else '') %}

        <div class="kayan-strip-card" style="display:flex;align-items:center;justify-content:space-between;gap:8px;padding:8px 10px;border-radius:10px;background:#1e293b;border:1px solid #334155;min-width:240px;">
          <div style="display:flex;align-items:center;gap:8px;min-width:0;flex:1;">
            {% if img_src %}
              <img src="{{ img_src }}" alt="{{ pname }}" style="width:42px;height:42px;object-fit:cover;border-radius:8px;border:1px solid #475569;flex-shrink:0;">
            {% else %}
              <div style="width:42px;height:42px;border-radius:8px;background:#0f172a;border:1px dashed #475569;display:flex;align-items:center;justify-content:center;font-size:10px;color:#94a3b8;flex-shrink:0;">صورة</div>
            {% endif %}
            <div style="min-width:0;">
              <div style="font-size:13px;font-weight:bold;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{{ pname }}</div>
              <div style="font-size:11px;color:#38bdf8;">المعرف: <span class="kayan-odd-code">{{ pcode }}</span> • {{ pad }}</div>
            </div>
          </div>

          <div style="display:flex;align-items:center;gap:5px;flex-shrink:0;">
            <button type="button"
              data-id="{{ pid }}"
              data-name="{{ pname }}"
              data-code="{{ pcode }}"
              data-ad="{{ pad }}"
              data-wa="{{ pwa }}"
              onclick="openTopEdit(this)"
              title="تعديل"
              style="padding:5px 8px;border-radius:7px;border:1px solid #f59e0b;background:#f59e0b;color:#0f172a;font-weight:bold;cursor:pointer;">✎</button>

            <form method="POST" action="/admin/delete_item/{{ pid }}" style="margin:0;" onsubmit="return confirm('حذف المنتج؟');">
              <button type="submit" title="حذف" style="padding:5px 8px;border-radius:7px;border:1px solid #ef4444;background:#7f1d1d;color:#fecaca;font-size:12px;cursor:pointer;">🗑</button>
            </form>
          </div>
        </div>
      {% endfor %}
    {% else %}
      <div id="kayan-empty-note" style="font-size:12px;color:#94a3b8;">لا توجد منتجات معروضة حالياً في الشريط العلوي.</div>
    {% endif %}
  </div>
</div>

<!-- نافذة التعديل عند الضغط على القلم -->
<div id="kayan-top-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.78);z-index:9999;align-items:center;justify-content:center;padding:14px;">
  <div style="width:100%;max-width:410px;background:#1e293b;border:1px solid #475569;border-radius:14px;padding:15px;color:#f8fafc;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
      <strong style="color:#fbbf24;font-size:14px;">تعديل المنتج</strong>
      <button type="button" onclick="closeTopEdit()" style="background:none;border:none;color:#f87171;font-size:17px;cursor:pointer;">✕</button>
    </div>

    <form id="kayan-top-form" method="POST" action="/admin/update_item/1" enctype="multipart/form-data" style="display:flex;flex-direction:column;gap:9px;">
      <div>
        <label style="display:block;font-size:12px;margin-bottom:3px;color:#cbd5e1;">اسم المنتج</label>
        <input type="text" id="top-edit-name" name="name" required style="width:100%;padding:7px;border-radius:8px;border:1px solid #475569;background:#0f172a;color:#fff;box-sizing:border-box;">
      </div>

      <div>
        <label style="display:block;font-size:12px;margin-bottom:3px;color:#cbd5e1;">الصورة</label>
        <input type="file" name="image" accept="image/*" style="width:100%;padding:5px;border-radius:8px;border:1px solid #475569;background:#0f172a;color:#cbd5e1;box-sizing:border-box;">
      </div>

      <div>
        <label style="display:block;font-size:12px;margin-bottom:3px;color:#cbd5e1;">المعرف (فردي تلقائي: 1، 3، 5...)</label>
        <input type="text" id="top-edit-code" name="code" readonly style="width:100%;padding:7px;border-radius:8px;border:1px solid #475569;background:#0f172a;color:#38bdf8;font-weight:bold;box-sizing:border-box;">
      </div>

      <div>
        <label style="display:block;font-size:12px;margin-bottom:3px;color:#cbd5e1;">خانة الإعلانات</label>
        <select id="top-edit-ad" name="ad_status" style="width:100%;padding:7px;border-radius:8px;border:1px solid #475569;background:#0f172a;color:#fff;box-sizing:border-box;">
          <option value="متوفر">متوفر</option>
          <option value="تم البيع">تم البيع</option>
          <option value="إعلان مميز">إعلان مميز</option>
        </select>
      </div>

      <div>
        <label style="display:block;font-size:12px;margin-bottom:3px;color:#cbd5e1;">رقم واتساب للتواصل</label>
        <input type="text" id="top-edit-wa" name="whatsapp" placeholder="9647700000000" style="width:100%;padding:7px;border-radius:8px;border:1px solid #475569;background:#0f172a;color:#fff;box-sizing:border-box;">
      </div>

      <button type="submit" style="padding:8px;border-radius:8px;border:none;background:#f59e0b;color:#0f172a;font-weight:bold;cursor:pointer;">حفظ</button>
    </form>
  </div>
</div>

<script>
window.kayanMode = 0;
function kayanToggleView() {
  window.kayanMode = (window.kayanMode + 1) % 3;
  const box = document.getElementById('kayan-strip-items');
  const strip = document.getElementById('kayan-top-strip');
  const btn = document.getElementById('kayan-toggle-view-btn');
  const note = document.getElementById('kayan-empty-note');
  if (!box) return;

  if (window.kayanMode === 0) {
    box.style.display = 'flex';
    box.style.flexDirection = 'column';
    box.style.overflowX = 'visible';
    if (strip) strip.style.borderColor = '#f59e0b';
    if (btn) btn.textContent = 'تعديل عرض (قائمة)';
    if (note) note.textContent = 'لا توجد منتجات معروضة حالياً في الشريط العلوي • وضع القائمة.';
  } else if (window.kayanMode === 1) {
    box.style.display = 'flex';
    box.style.flexDirection = 'row';
    box.style.overflowX = 'auto';
    if (strip) strip.style.borderColor = '#38bdf8';
    if (btn) btn.textContent = 'تعديل عرض (أفقي)';
    if (note) note.textContent = 'لا توجد منتجات معروضة حالياً في الشريط العلوي • وضع أفقي.';
  } else {
    box.style.display = 'grid';
    box.style.gridTemplateColumns = '1fr';
    if (strip) strip.style.borderColor = '#10b981';
    if (btn) btn.textContent = 'تعديل عرض (بطاقات)';
    if (note) note.textContent = 'لا توجد منتجات معروضة حالياً في الشريط العلوي • وضع بطاقات.';
  }
}

function nextOddVal() {
  let maxOdd = -1;
  document.querySelectorAll('.kayan-odd-code').forEach(el => {
    const n = parseInt((el.textContent || '').trim(), 10);
    if (!isNaN(n) && n % 2 === 1 && n > maxOdd) maxOdd = n;
  });
  return maxOdd >= 1 ? maxOdd + 2 : 1;
}

function openTopEdit(btn) {
  const pid = btn.getAttribute('data-id') || '1';
  document.getElementById('kayan-top-form').action = '/admin/update_item/' + pid;
  document.getElementById('top-edit-name').value = btn.getAttribute('data-name') || '';
  document.getElementById('top-edit-ad').value = btn.getAttribute('data-ad') || 'متوفر';
  document.getElementById('top-edit-wa').value = btn.getAttribute('data-wa') || '';
  const c = parseInt((btn.getAttribute('data-code') || '').trim(), 10);
  document.getElementById('top-edit-code').value = (!isNaN(c) && c % 2 === 1) ? c : nextOddVal();
  document.getElementById('kayan-top-modal').style.display = 'flex';
}

function closeTopEdit() {
  document.getElementById('kayan-top-modal').style.display = 'none';
}
</script>
<!-- END KAYAN TOP STRIP -->
"""
        html = html[:s] + new_block + html[e:]
        with open(admin_path, "w", encoding="utf-8") as f:
            f.write(html)

# 3. تحديث دالة جلب المنتجات في app.py لتبحث في كل قواعد البيانات والجداول وتمرر products دائماً
py_files = [
    f for f in glob.glob("*.py")
    if f not in (
        "patch_update.py", "add_features.py", "update_admin_ui.py",
        "fix_routes.py", "fix_images.py", "auto_fix_store.py",
        "fix_img_link.py", "fix_index_img.py", "force_upload_fix.py",
        "update_admin_panel.py", "apply_custom_admin.py", "set_odd_id_logic.py",
        "top_admin_bar.py", "fix_top_strip_btn.py", "fix_strip_products_and_btn.py"
    )
]

for pf in py_files:
    with open(pf, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    if "def _load_admin_products(" in code:
        s = code.find("def _load_admin_products(")
        e = code.find("\n@app.route", s + 1)
        if e == -1:
            e = code.find("\nif __name__", s + 1)
        if e == -1:
            e = len(code)

        new_loader = f"""def _load_admin_products():
    import os, glob, sqlite3
    base = os.path.abspath(os.path.dirname(__file__))
    candidates = glob.glob(os.path.join(base, "*.db")) + glob.glob(os.path.join(base, "**", "*.db"), recursive=True)
    for db_file in dict.fromkeys(candidates):
        try:
            c = sqlite3.connect(db_file)
            c.row_factory = sqlite3.Row
            cur = c.cursor()
            tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            for t in tables:
                if any(k in t.lower() for k in ("product", "item", "good")):
                    rows = cur.execute(f"SELECT * FROM {{t}} ORDER BY rowid DESC").fetchall()
                    if rows:
                        c.close()
                        return [dict(r) for r in rows]
            c.close()
        except Exception:
            pass
    return []
"""
        code = code[:s] + new_loader + code[e:]
        with open(pf, "w", encoding="utf-8") as f:
            f.write(code)

print("تم تحديث الشريط العلوي وزر تعديل عرض وجلب المنتجات بنجاح.")
