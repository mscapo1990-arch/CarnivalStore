import os

# التأكد من وجود مجلد الصور داخل static
os.makedirs("static/uploads", exist_ok=True)

# 1. تحديث app.py لإضافة مسارات التعديل والحذف وتبديل الحالة (متوفر / تم البيع) وإصلاح مسار الصور
if os.path.exists("app.py"):
    with open("app.py", "r", encoding="utf-8") as f:
        code = f.read()

    extra_routes = """
@app.route('/toggle_status/<int:pid>', methods=['POST'])
def toggle_status(pid):
    conn = get_db()
    row = conn.execute("SELECT status FROM products WHERE id = ?", (pid,)).fetchone()
    if row:
        current = row['status'] if 'status' in row.keys() else 'متوفر'
        new_status = 'تم البيع' if current == 'متوفر' else 'متوفر'
        conn.execute("UPDATE products SET status = ? WHERE id = ?", (new_status, pid))
        conn.commit()
    conn.close()
    return redirect(request.referrer or '/admin')

@app.route('/delete_product/<int:pid>', methods=['POST'])
def delete_product(pid):
    conn = get_db()
    conn.execute("DELETE FROM products WHERE id = ?", (pid,))
    conn.commit()
    conn.close()
    return redirect(request.referrer or '/admin')

@app.route('/edit_product/<int:pid>', methods=['POST'])
def edit_product_route(pid):
    name = request.form.get('name', '').strip()
    price = request.form.get('price', '').strip()
    category = request.form.get('category', '').strip()
    status = request.form.get('status', 'متوفر').strip()
    details = request.form.get('details', '').strip()
    conn = get_db()
    if name and price:
        conn.execute(
            "UPDATE products SET name=?, price=?, category=?, status=?, details=? WHERE id=?",
            (name, price, category, status, details, pid)
        )
        conn.commit()
    conn.close()
    return redirect(request.referrer or '/admin')
"""
    if "def toggle_status(" not in code:
        if "if __name__ ==" in code:
            code = code.replace("if __name__ ==", extra_routes + "\nif __name__ ==")
        else:
            code += extra_routes

    with open("app.py", "w", encoding="utf-8") as f:
        f.write(code)

print("تمت إضافة مسارات التعديل والحذف وحالة متوفر/تم البيع بنجاح.")
