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


def kayan_save_upload_file(file_obj):
    if not file_obj or not getattr(file_obj, "filename", ""):
        return ""
    import os, time, sqlite3, glob
    from werkzeug.utils import secure_filename
    base = os.path.abspath(os.path.dirname(__file__))
    upload_dir = os.path.join(base, "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    raw_name = os.path.basename(file_obj.filename)
    safe_name = secure_filename(raw_name)
    if not safe_name or "." not in safe_name:
        ext = raw_name.rsplit(".", 1)[1].lower() if "." in raw_name else "jpg"
        safe_name = f"img_{int(time.time()*1000)}.{ext}"
    else:
        name_part, ext_part = safe_name.rsplit(".", 1)
        safe_name = f"{name_part}_{int(time.time())}.{ext_part.lower()}"
    full_path = os.path.join(upload_dir, safe_name)
    file_obj.save(full_path)
    return safe_name

@app.route('/static/uploads/<path:filename>')
def kayan_static_uploads(filename):
    import os
    from flask import send_from_directory
    base = os.path.abspath(os.path.dirname(__file__))
    clean = os.path.basename(filename)
    for folder in [
        os.path.join(base, "static", "uploads"),
        os.path.join(base, "uploads"),
        os.path.join(base, "static")
    ]:
        target = os.path.join(folder, clean)
        if os.path.isfile(target):
            return send_from_directory(folder, clean)
    return "", 404


def kayan_multi_ip_img_handler():
    try:
        from flask import request
        if request.method != "POST" or not getattr(request, "files", None):
            return
        import os, time, uuid
        from werkzeug.utils import secure_filename
        base = os.path.abspath(os.path.dirname(__file__))
        up_dir = os.path.join(base, "static", "uploads")
        os.makedirs(up_dir, exist_ok=True)
        for _, fobj in request.files.items():
            if fobj and getattr(fobj, "filename", ""):
                raw = os.path.basename(fobj.filename)
                safe = secure_filename(raw)
                ext = ""
                if "." in raw:
                    ext = raw.rsplit(".", 1)[1].lower().strip()
                if not ext and safe and "." in safe:
                    ext = safe.rsplit(".", 1)[1].lower().strip()
                if not ext:
                    ext = "jpg"
                uniq = f"img_{int(time.time())}_{uuid.uuid4().hex[:6]}.{ext}"
                full_path = os.path.join(up_dir, uniq)
                fobj.save(full_path)
                try:
                    fobj.stream.seek(0)
                except Exception:
                    pass
                request.environ["KAYAN_LAST_UPLOADED_IMG"] = uniq
                break
    except Exception:
        pass

@app.before_request
def kayan_before_any_ip_post():
    kayan_multi_ip_img_handler()


@app.after_request
def kayan_sync_db_image_after_post(response):
    try:
        from flask import request
        saved = request.environ.get("KAYAN_LAST_UPLOADED_IMG")
        if request.method == "POST" and saved:
            import os, glob, sqlite3
            base = os.path.abspath(os.path.dirname(__file__))
            for db in dict.fromkeys(glob.glob(os.path.join(base, "*.db")) + glob.glob(os.path.join(base, "**", "*.db"), recursive=True)):
                if not os.path.exists(db) or os.path.getsize(db) == 0:
                    continue
                c = sqlite3.connect(db)
                cur = c.cursor()
                tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
                for t in tables:
                    if "product" in t.lower():
                        cols = [x[1] for x in cur.execute(f"PRAGMA table_info({t})").fetchall()]
                        for col in cols:
                            if any(k in col.lower() for k in ("image", "img", "photo", "pic", "thumb", "file")):
                                last = cur.execute(f"SELECT rowid FROM {t} ORDER BY rowid DESC LIMIT 1").fetchone()
                                if last:
                                    cur.execute(f"UPDATE {t} SET {col} = ? WHERE rowid = ?", (saved, last[0]))
                                break
                c.commit()
                c.close()
    except Exception:
        pass
    return response


from functools import wraps
from flask import session, render_template_string

app.secret_key = os.environ.get("CARNIVAL_SECRET_KEY", "carnival_store_secret_key_2026")
ADMIN_USERNAME = os.environ.get("CARNIVAL_ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("CARNIVAL_ADMIN_PASS", "Carnival@2026")

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>دخول الإدارة | كرنفال</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-white min-h-screen flex items-center justify-center p-4">
  <div class="w-full max-w-sm bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl">
    <div class="text-center mb-6">
      <h1 class="text-2xl font-bold text-amber-400">CARNIVAL | كرنفال</h1>
      <p class="text-xs text-slate-400 mt-1">تسجيل الدخول إلى لوحة التحكم</p>
    </div>
    {% if error %}
      <div class="bg-red-500/15 border border-red-500/40 text-red-300 text-xs rounded-xl p-3 mb-4 text-center">{{ error }}</div>
    {% endif %}
    <form method="POST" class="space-y-4">
      <div>
        <label class="block text-xs text-slate-300 mb-1">اسم المستخدم</label>
        <input type="text" name="username" required class="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-amber-400">
      </div>
      <div>
        <label class="block text-xs text-slate-300 mb-1">كلمة المرور</label>
        <input type="password" name="password" required class="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-amber-400">
      </div>
      <button type="submit" class="w-full bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold py-2.5 rounded-xl text-sm transition">دخول اللوحة</button>
    </form>
    <div class="mt-5 text-center">
      <a href="/" class="text-xs text-slate-400 hover:text-amber-400">العودة إلى المتجر</a>
    </div>
  </div>
</body>
</html>
'''

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        u = (request.form.get('username') or '').strip()
        p = (request.form.get('password') or '').strip()
        if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
            session['is_admin'] = True
            session['admin_user'] = u
            return redirect('/admin')
        error = "اسم المستخدم أو كلمة المرور غير صحيحة"
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect('/admin/login')

def _ensure_product_ids():
    prods = store_data.get("products", [])
    for idx, item in enumerate(prods):
        if not item.get("id"):
            item["id"] = idx + 1
    return prods

def _save_upload_file(file_obj):
    import time, uuid
    up_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static", "uploads")
    os.makedirs(up_dir, exist_ok=True)
    ext = os.path.splitext(file_obj.filename)[1].lower() or ".jpg"
    fname = f"img_{int(time.time())}_{uuid.uuid4().hex[:6]}{ext}"
    file_obj.save(os.path.join(up_dir, fname))
    return "/static/uploads/" + fname

@app.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin_dashboard():
    prods = _ensure_product_ids()
    if request.method == 'POST':
        action_type = (request.form.get('action_type') or 'add_product').strip()
        if action_type == 'update_settings':
            banner = (request.form.get('ad_banner') or '').strip()
            wa = (request.form.get('whatsapp') or '').strip()
            if banner:
                store_data['ad_banner'] = banner
            if wa:
                store_data['whatsapp'] = wa
            return redirect('/admin')
        else:
            name_val = (request.form.get('name') or '').strip()
            price_val = (request.form.get('price') or '').strip()
            cat_val = (request.form.get('category') or 'رجالي').strip()
            img_url = "/store-image"
            f = request.files.get('image') or request.files.get('photo') or request.files.get('file')
            if f and getattr(f, 'filename', ''):
                img_url = _save_upload_file(f)
            next_id = max([int(x.get('id', i + 1)) for i, x in enumerate(prods)] + [0]) + 1
            if name_val:
                prods.append({
                    "id": next_id,
                    "name": name_val,
                    "price": price_val or "0$",
                    "category": cat_val,
                    "image": img_url
                })
                store_data["products"] = prods
            return redirect('/admin')
    return render_template(
        "admin.html",
        products=prods,
        ad_banner=store_data.get("ad_banner", ""),
        whatsapp=store_data.get("whatsapp", ""),
        admin_user=session.get("admin_user", ADMIN_USERNAME)
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
