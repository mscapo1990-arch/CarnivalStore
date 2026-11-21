import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
import os
import random
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'carnival_secret_key_123'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

store_data = {
    "whatsapp": "9647700000000",
    "products": []
}

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

# قائمة الجوائز في عجلة الحظ
WHEEL_PRIZES = [
    {"id": 1, "name": "100 ماسة 💎", "chance": 10},
    {"id": 2, "name": "هدية وردة 🌹", "chance": 30},
    {"id": 3, "name": "إطار مميز 👑", "chance": 5},
    {"id": 4, "name": "حظ أوفر 😢", "chance": 45},
    {"id": 5, "name": "500 نقطة ⭐", "chance": 10}
]

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
    return render_template('admin.html', store_data=store_data)


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


KAYAN_ALL_IMG_EXTS = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'avif', 'heic', 'heif', 'tif', 'tiff', 'svg', 'ico', 'jfif'}

def kayan_allow_any_image(filename):
    if not filename or "." not in str(filename):
        return True
    ext = str(filename).rsplit(".", 1)[1].lower().strip()
    return ext in KAYAN_ALL_IMG_EXTS or True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
