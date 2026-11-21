import os

admin_path = "templates/admin.html"
if not os.path.exists(admin_path):
    print("لم يتم العثور على templates/admin.html")
    raise SystemExit(1)

with open(admin_path, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

# إزالة أي شريط قديم أضفناه سابقاً لتفادي التكرار
for marker in ['id="kayan-quick-bar"', 'id="kayan-admin-panel-bar"', 'id="kayan-custom-admin-section"']:
    if marker in html:
        s = html.find(f'<div {marker}')
        if s != -1:
            e = html.find('<!-- END KAYAN CUSTOM ADMIN -->')
            if e != -1:
                html = html[:s] + html[e + len('<!-- END KAYAN CUSTOM ADMIN -->'):]

custom_section = """
<div id="kayan-custom-admin-section" style="margin-top:20px;padding:14px;border-radius:14px;border:1px solid #334155;background:#111827;color:#f8fafc;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
    <h3 style="margin:0;font-size:16px;color:#fbbf24;">إدارة المنتجات والاعلانات</h3>
    <button type="button" onclick="openEditModal(null)" style="padding:7px 12px;border-radius:8px;border:1px solid #f59e0b;background:#f59e0b;color:#0f172a;font-weight:bold;cursor:pointer;">✎ معرف فردي جديد</button>
  </div>

  <div id="kayan-products-list" style="display:flex;flex-direction:column;gap:10px;">
    {% if products is defined and products %}
      {% for p in products %}
        {% set pid = p.id if p.id is defined else (p['id'] if p is mapping and 'id' in p else loop.index) %}
        {% set pname = p.name if p.name is defined else (p['name'] if p is mapping and 'name' in p else 'منتج') %}
        {% set pimg = p.image if p.image is defined else (p['image'] if p is mapping and 'image' in p else '') %}
        {% set pcode = p.code if p.code is defined else (p['code'] if p is mapping and 'code' in p and p['code'] else (loop.index * 2 - 1)) %}
        {% set pad = p.ad_status if p.ad_status is defined else (p['ad_status'] if p is mapping and 'ad_status' in p and p['ad_status'] else (p.status if p.status is defined else 'متوفر')) %}
        {% set pwa = p.whatsapp if p.whatsapp is defined else (p['whatsapp'] if p is mapping and 'whatsapp' in p and p['whatsapp'] else '') %}
        {% set img_src = pimg if pimg and (pimg.startswith('http') or pimg.startswith('/')) else ('/static/uploads/' ~ pimg if pimg else '') %}

        <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px;padding:10px;border-radius:10px;background:#1e293b;border:1px solid #334155;">
          <div style="display:flex;align-items:center;gap:10px;min-width:180px;">
            {% if img_src %}
              <img src="{{ img_src }}" alt="{{ pname }}" style="width:48px;height:48px;object-fit:cover;border-radius:8px;border:1px solid #475569;">
            {% else %}
              <div style="width:48px;height:48px;border-radius:8px;background:#0f172a;border:1px dashed #475569;display:flex;align-items:center;justify-content:center;font-size:11px;color:#94a3b8;">بدون صورة</div>
            {% endif %}
            <div>
              <div style="font-weight:bold;font-size:14px;color:#f8fafc;">{{ pname }}</div>
              <div style="font-size:12px;color:#38bdf8;">المعرف: <span id="code-text-{{ pid }}">{{ pcode }}</span></div>
            </div>
          </div>

          <div style="display:flex;flex-wrap:wrap;align-items:center;gap:6px;">
            <span style="padding:5px 9px;border-radius:7px;font-size:12px;background:#0f172a;color:#fbbf24;border:1px solid #475569;">إعلان: {{ pad }}</span>

            <button type="button"
              data-id="{{ pid }}"
              data-name="{{ pname }}"
              data-code="{{ pcode }}"
              data-ad="{{ pad }}"
              data-wa="{{ pwa }}"
              onclick="openEditModalFromBtn(this)"
              title="قلم التعديل"
              style="padding:6px 10px;border-radius:7px;border:1px solid #f59e0b;background:#f59e0b;color:#0f172a;font-weight:bold;cursor:pointer;">✎</button>

            <button type="button"
              data-id="{{ pid }}"
              data-name="{{ pname }}"
              data-code="{{ pcode }}"
              data-ad="{{ pad }}"
              data-wa="{{ pwa }}"
              onclick="openEditModalFromBtn(this)"
              style="padding:6px 10px;border-radius:7px;border:1px solid #3b82f6;background:#1d4ed8;color:#fff;font-size:12px;cursor:pointer;">تعديل</button>

            <form method="POST" action="/admin/delete_item/{{ pid }}" style="margin:0;" onsubmit="return confirm('هل تريد حذف هذا المنتج؟');">
              <button type="submit" title="سلة حذف" style="padding:6px 10px;border-radius:7px;border:1px solid #ef4444;background:#7f1d1d;color:#fecaca;font-size:12px;cursor:pointer;">🗑 حذف</button>
            </form>
          </div>
        </div>
      {% endfor %}
    {% else %}
      <div style="font-size:13px;color:#94a3b8;">قائمة المنتجات جاهزة للعرض عند توفر منتجات في القاعدة.</div>
    {% endif %}
  </div>
</div>

<!-- نافذة التعديل عند الضغط على القلم -->
<div id="kayan-edit-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.75);z-index:9999;align-items:center;justify-content:center;padding:14px;">
  <div style="width:100%;max-width:420px;background:#1e293b;border:1px solid #475569;border-radius:14px;padding:16px;color:#f8fafc;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
      <h4 style="margin:0;color:#fbbf24;font-size:15px;">تعديل بيانات المنتج</h4>
      <button type="button" onclick="closeEditModal()" style="background:none;border:none;color:#f87171;font-size:18px;cursor:pointer;">✕</button>
    </div>

    <form id="kayan-edit-form" method="POST" action="/admin/update_item/1" enctype="multipart/form-data" style="display:flex;flex-direction:column;gap:10px;">
      <div>
        <label style="display:block;font-size:12px;margin-bottom:4px;color:#cbd5e1;">اسم المنتج</label>
        <input type="text" id="edit-name" name="name" required style="width:100%;padding:8px;border-radius:8px;border:1px solid #475569;background:#0f172a;color:#fff;box-sizing:border-box;">
      </div>

      <div>
        <label style="display:block;font-size:12px;margin-bottom:4px;color:#cbd5e1;">الصورة</label>
        <input type="file" id="edit-image" name="image" accept="image/*" style="width:100%;padding:6px;border-radius:8px;border:1px solid #475569;background:#0f172a;color:#cbd5e1;box-sizing:border-box;">
      </div>

      <div>
        <label style="display:block;font-size:12px;margin-bottom:4px;color:#cbd5e1;">المعرف (تلقائي فردي: 1، 3، 5...)</label>
        <div style="display:flex;gap:6px;">
          <input type="text" id="edit-code" name="code" readonly style="flex:1;padding:8px;border-radius:8px;border:1px solid #475569;background:#0f172a;color:#38bdf8;font-weight:bold;">
          <button type="button" onclick="setNextOddCode()" style="padding:8px 10px;border-radius:8px;border:1px solid #10b981;background:#065f46;color:#d1fae5;font-size:12px;cursor:pointer;">فردي جديد</button>
        </div>
      </div>

      <div>
        <label style="display:block;font-size:12px;margin-bottom:4px;color:#cbd5e1;">خانة الإعلانات / الحالة</label>
        <select id="edit-ad" name="ad_status" style="width:100%;padding:8px;border-radius:8px;border:1px solid #475569;background:#0f172a;color:#fff;box-sizing:border-box;">
          <option value="متوفر">متوفر</option>
          <option value="تم البيع">تم البيع</option>
          <option value="إعلان مميز">إعلان مميز</option>
        </select>
      </div>

      <div>
        <label style="display:block;font-size:12px;margin-bottom:4px;color:#cbd5e1;">إضافة رقم واتساب للتواصل</label>
        <input type="text" id="edit-wa" name="whatsapp" placeholder="9647700000000" style="width:100%;padding:8px;border-radius:8px;border:1px solid #475569;background:#0f172a;color:#fff;box-sizing:border-box;">
      </div>

      <div style="display:flex;gap:8px;margin-top:6px;">
        <button type="submit" style="flex:1;padding:9px;border-radius:8px;border:none;background:#f59e0b;color:#0f172a;font-weight:bold;cursor:pointer;">حفظ</button>
        <button type="button" onclick="closeEditModal()" style="padding:9px 14px;border-radius:8px;border:1px solid #475569;background:#334155;color:#fff;cursor:pointer;">إلغاء</button>
      </div>
    </form>
  </div>
</div>

<script>
function getNextOddNumber() {
  let maxOdd = -1;
  document.querySelectorAll('[id^="code-text-"]').forEach(el => {
    const num = parseInt((el.textContent || '').trim(), 10);
    if (!isNaN(num) && num % 2 === 1 && num > maxOdd) {
      maxOdd = num;
    }
  });
  return maxOdd >= 1 ? maxOdd + 2 : 1;
}

function setNextOddCode() {
  document.getElementById('edit-code').value = getNextOddNumber();
}

function openEditModalFromBtn(btn) {
  const pid = btn.getAttribute('data-id');
  const name = btn.getAttribute('data-name') || '';
  const code = btn.getAttribute('data-code') || '';
  const ad = btn.getAttribute('data-ad') || 'متوفر';
  const wa = btn.getAttribute('data-wa') || '';

  const form = document.getElementById('kayan-edit-form');
  form.action = '/admin/update_item/' + pid;
  document.getElementById('edit-name').value = name;
  document.getElementById('edit-ad').value = ad;
  document.getElementById('edit-wa').value = wa;

  const parsed = parseInt(String(code).trim(), 10);
  if (!isNaN(parsed) && parsed % 2 === 1) {
    document.getElementById('edit-code').value = parsed;
  } else {
    setNextOddCode();
  }

  document.getElementById('kayan-edit-modal').style.display = 'flex';
}

function openEditModal(pid) {
  const form = document.getElementById('kayan-edit-form');
  form.action = '/admin/update_item/' + (pid || 1);
  document.getElementById('edit-name').value = '';
  document.getElementById('edit-ad').value = 'متوفر';
  document.getElementById('edit-wa').value = '';
  setNextOddCode();
  document.getElementById('kayan-edit-modal').style.display = 'flex';
}

function closeEditModal() {
  document.getElementById('kayan-edit-modal').style.display = 'none';
}
</script>
<!-- END KAYAN CUSTOM ADMIN -->
"""

if "</body>" in html:
    html = html.replace("</body>", custom_section + "\n</body>", 1)
else:
    html += custom_section

with open(admin_path, "w", encoding="utf-8") as f:
    f.write(html)

print("تم تحديث templates/admin.html بالشكل المطلوب بنجاح.")
