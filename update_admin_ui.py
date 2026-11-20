import glob

html_files = glob.glob("**/*.html", recursive=True)
updated = []

admin_block = """
<!-- Kayan Admin Controls Patch -->
<div id="kayan-admin-tools" style="margin-top:16px;padding:12px;border:1px dashed #f59e0b;border-radius:10px;">
  <div style="font-size:13px;color:#fbbf24;margin-bottom:8px;">أدوات الإدارة السريعة (متوفر / تم البيع - تعديل - حذف - الصور)</div>
  <form method="POST" action="/toggle_status/1" style="display:inline-block;margin:4px;">
    <select name="status" style="padding:6px;border-radius:6px;">
      <option value="متوفر">متوفر</option>
      <option value="تم البيع">تم البيع</option>
    </select>
    <button type="submit" style="padding:6px 10px;border-radius:6px;cursor:pointer;">تحديث الحالة</button>
  </form>
  <form method="POST" action="/delete_product/1" style="display:inline-block;margin:4px;">
    <button type="submit" style="padding:6px 10px;border-radius:6px;cursor:pointer;">حذف منتج</button>
  </form>
</div>
"""

for path in html_files:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    changed = False
    if "لوحة التحكم" in content and "kayan-admin-tools" not in content:
        if "</body>" in content:
            content = content.replace("</body>", admin_block + "\n</body>")
        else:
            content += admin_block
        changed = True
    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        updated.append(path)

print("الملفات المحدثة:", updated if updated else "لم يتم العثور على ملف HTML يحوي لوحة التحكم")
