import os

from flask import Flask, session
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "carnival-store-secret-2026")

def _load_admin_products():
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
                    rows = cur.execute(f"SELECT * FROM {t} ORDER BY rowid DESC").fetchall()
                    if rows:
                        c.close()
                        return [dict(r) for r in rows]
            c.close()
        except Exception:
            pass
    return []

@app.route('/')
def index():
    category = request.args.get('category', 'الكل')
    products = store_data["products"]
    if category != 'الكل':
        products = [p for p in products if p.get('category') == category]
    return render_template('index.html', products=products, whatsapp=store_data["whatsapp"], current_category=category)

@app.route('/wheel')
def wheel_page():
    return render_template('wheel.html')

@app.route('/api/spin-wheel', methods=['POST'])
def spin_wheel():
    prizes_pool = []
    for prize in WHEEL_PRIZES:
        prizes_pool.extend([prize] * prize['chance'])
    
    won_prize = random.choice(prizes_pool)
    return {
        "status": "success",
        "prize": won_prize,
        "message": f"مبروك يا أبو سليم! لقد ربحت: {won_prize['name']}"
    }

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('username') == ADMIN_USER and request.form.get('password') == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = 'اسم المستخدم أو كلمة المرور غير صحيحة!'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_whatsapp':
            store_data["whatsapp"] = request.form.get('whatsapp')
        elif action == 'add_product':
            name = request.form.get('name')
            price = request.form.get('price')
            category = request.form.get('category', 'منتجات أخرى')
            desc = request.form.get('desc', '')
            image_url = "https://via.placeholder.com/300"
            file = request.files.get('image')
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = url_for('static', filename=f'uploads/{filename}')
            store_data["products"].append({
                "id": len(store_data["products"]) + 1,
                "name": name,
                "price": price,
                "category": category,
                "image": image_url,
                "desc": desc
            })
    return render_template('admin.html', products=_load_admin_products(), store_data=store_data)


@app.route('/toggle_status/<int:pid>', methods=['POST'])

@app.route('/delete_product/<int:pid>', methods=['POST'])

@app.route('/edit_product/<int:pid>', methods=['POST'])


@app.route('/toggle_status/<int:pid>', methods=['POST'])
def toggle_status(pid):
    try:
        conn = sqlite3.connect('store.db')
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
        conn = sqlite3.connect('store.db')
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE id = ?", (pid,))
        conn.commit()
        conn.close()
    except Exception as e:
        print("delete_product error:", e)
    return redirect(request.referrer or '/admin')


@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    from flask import send_from_directory
    import os
    base = os.path.abspath(os.path.dirname(__file__))
    return send_from_directory(os.path.join(base, 'static', 'uploads'), filename)


@app.route('/static/uploads/<path:filename>')
def serve_static_upload(filename):
    base = os.path.abspath(os.path.dirname(__file__))
    return send_from_directory(os.path.join(base, 'static', 'uploads'), filename)

@app.route('/toggle_status/<int:pid>', methods=['POST'])
def toggle_product_status(pid):
    try:
        c = sqlite3.connect('store.db')
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
        c = sqlite3.connect('store.db')
        cur = c.cursor()
        cur.execute("DELETE FROM products WHERE id = ?", (pid,))
        c.commit()
        c.close()
    except Exception as e:
        print("delete err:", e)
    return redirect(request.referrer or '/admin')


@app.errorhandler(500)
def handle_500_err(e):
    return f"<h3>تنبيه في التطبيق</h3><pre>{e}</pre>", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
