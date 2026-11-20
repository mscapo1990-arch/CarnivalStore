import os

path = "templates/index.html"
if os.path.exists(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    old_tag = '<img src="{{ p.image }}"'
    new_tag = '<img src="{{ p.image if p.image and (p.image.startswith(\'http\') or p.image.startswith(\'/\')) else \'/static/uploads/\' ~ (p.image or \'\') }}"'

    if old_tag in html:
        html = html.replace(old_tag, new_tag)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("تم تحديث وسم الصورة في templates/index.html بنجاح.")
    else:
        print("لم يطابق النص الحرفي في templates/index.html، يرجى مراجعة السطر 30.")
else:
    print("الملف templates/index.html غير موجود.")
