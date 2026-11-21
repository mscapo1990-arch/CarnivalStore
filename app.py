import os, json, time
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "carnival-store-secret-key-2026")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
PERSIST_FILE = os.path.join(BASE_DIR, "carnival_persist.json")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123456"

store_data = {
    "products": [],
    "banner_images": [],
    "whatsapp": "",
    "ad_banner": ""
}

def _save_state():
    try:
        payload = {
            "products": store_data.get("products", []),
            "banner_images": store_data.get("banner_images", []),
            "whatsapp": store_data.get("whatsapp", ""),
            "ad_banner": store_data.get("ad_banner", "")
        }
        with open(PERSIST_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _load_state():
    try:
        if os.path.isfile(PERSIST_FILE):
            with open(PERSIST_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                if isinstance(data.get("products"), list):
                    store_data["products"] = data["products"]
                if isinstance(data.get("banner_images"), list):
                    store_data["banner_images"] = data["banner_images"]
                if "whatsapp" in data and data["whatsapp"] is not None:
                    store_data["whatsapp"] = data["whatsapp"]
                if "ad_banner" in data and data["ad_banner"] is not None:
                    store_data["ad_banner"] = data["ad_banner"]
    except Exception:
        pass

_load_state()

def _save_uploaded_file(file_storage, prefix="img"):
    if not file_storage or not getattr(file_storage, "filename", ""):
        return ""
    safe = secure_filename(file_storage.filename) or f"{prefix}.jpg"
    fname = f"{int(time.time())}_{prefix}_{safe}"
    full_path = os.path.join(UPLOAD_DIR, fname)
    file_storage.save(full_path)
    return f"/static/uploads/{fname}"

def _is_logged_in():
    return bool(session.get("admin_logged_in"))

@app.route("/", methods=['GET', 'POST'])
def index():
    _load_state()
    category = (request.args.get("category") or "").strip()
    all_products = store_data.get("products", [])
    if category and category != "الكل":
        products = [p for p in all_products if p.get("category") == category and p.get("status") != "موقوف"]
    else:
        products = [p for p in all_products if p.get("status") != "موقوف"]
    return render_template(
        "index.html",
        products=products,
        whatsapp=store_data.get("whatsapp", ""),
        banner_images=store_data.get("banner_images", []),
        ad_banner=store_data.get("ad_banner", ""),
        current_category=category or "الكل"
    )

@app.route("/wheel", methods=['GET', 'POST'])
def wheel():
    return render_template("wheel.html")

@app.route("/login", methods=['GET', 'POST'])
@app.route("/admin/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == "POST":
        u = (request.form.get("username") or "").strip()
        p = (request.form.get("password") or "").strip()
        if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect("/admin")
        error = "اسم المستخدم أو كلمة المرور غير صحيحة"
    return render_template("login.html", error=error)

@app.route("/logout", methods=['GET', 'POST'])
@app.route("/admin/logout", methods=['GET', 'POST'])
def logout():
    session.pop("admin_logged_in", None)
    return redirect("/login")

@app.route("/admin", methods=['GET', 'POST'])
def admin():
    if not _is_logged_in():
        return redirect("/login")
    _load_state()

    if request.method == "POST":
        if "whatsapp" in request.form and not request.form.get("name") and not request.form.get("product_name"):
            store_data["whatsapp"] = (request.form.get("whatsapp") or "").strip()
            _save_state()
            return redirect("/admin")

        name = (request.form.get("name") or request.form.get("product_name") or request.form.get("title") or "").strip()
        if name:
            price = (request.form.get("price") or "0$").strip() or "0$"
            category = (request.form.get("category") or "عام").strip() or "عام"
            wa = (request.form.get("whatsapp") or request.form.get("product_whatsapp") or store_data.get("whatsapp") or "").strip()
            f = request.files.get("image") or request.files.get("product_image") or request.files.get("file")
            img_url = _save_uploaded_file(f, "prod")

            prods = store_data.get("products")
            if not isinstance(prods, list):
                prods = []
                store_data["products"] = prods

            next_id = max([int(p.get("id", 0)) for p in prods if isinstance(p, dict)] + [0]) + 1
            prods.append({
                "id": next_id,
                "name": name,
                "price": price,
                "category": category,
                "whatsapp": wa,
                "image": img_url,
                "status": "نشط"
            })
            _save_state()
            return redirect("/admin")

    return render_template("admin.html", store_data=store_data, products=store_data.get("products", []), whatsapp=store_data.get("whatsapp", ""), banner_images=store_data.get("banner_images", []))

@app.route("/admin/add_product", methods=['GET', 'POST'])
def add_product():
    if not _is_logged_in():
        return redirect("/login")
    _load_state()
    name = (request.form.get("name") or request.form.get("product_name") or request.form.get("title") or "").strip()
    if name:
        price = (request.form.get("price") or "0$").strip() or "0$"
        category = (request.form.get("category") or "عام").strip() or "عام"
        wa = (request.form.get("whatsapp") or request.form.get("product_whatsapp") or store_data.get("whatsapp") or "").strip()
        f = request.files.get("image") or request.files.get("product_image") or request.files.get("file")
        img_url = _save_uploaded_file(f, "prod")

        prods = store_data.get("products")
        if not isinstance(prods, list):
            prods = []
            store_data["products"] = prods

        next_id = max([int(p.get("id", 0)) for p in prods if isinstance(p, dict)] + [0]) + 1
        prods.append({
            "id": next_id,
            "name": name,
            "price": price,
            "category": category,
            "whatsapp": wa,
            "image": img_url,
            "status": "نشط"
        })
        _save_state()
    return redirect("/admin")

@app.route("/toggle_status/<int:pid>", methods=['GET', 'POST'])
@app.route("/admin/toggle_status/<int:pid>", methods=['GET', 'POST'])
def toggle_status(pid):
    if not _is_logged_in():
        return redirect("/login")
    _load_state()
    for p in store_data.get("products", []):
        if int(p.get("id", 0)) == pid:
            p["status"] = "موقوف" if p.get("status") == "نشط" else "نشط"
            break
    _save_state()
    return redirect("/admin")

@app.route("/delete_product/<int:pid>", methods=['GET', 'POST'])
@app.route("/admin/delete_product/<int:pid>", methods=['GET', 'POST'])
def delete_product(pid):
    if not _is_logged_in():
        return redirect("/login")
    _load_state()
    store_data["products"] = [p for p in store_data.get("products", []) if int(p.get("id", 0)) != pid]
    _save_state()
    return redirect("/admin")

@app.route("/admin/banner/upload", methods=['GET', 'POST'])
def banner_upload():
    if not _is_logged_in():
        return redirect("/login")
    _load_state()
    files = request.files.getlist("banner_images") or request.files.getlist("images") or request.files.getlist("image")
    imgs = store_data.get("banner_images")
    if not isinstance(imgs, list):
        imgs = []
        store_data["banner_images"] = imgs
    for f in files:
        url = _save_uploaded_file(f, "banner")
        if url:
            imgs.append(url)
    _save_state()
    return redirect("/admin")

@app.route("/admin/banner/delete", methods=['GET', 'POST'])
def banner_delete():
    if not _is_logged_in():
        return redirect("/login")
    _load_state()
    target = (request.form.get("image_url") or request.form.get("url") or "").strip()
    imgs = store_data.get("banner_images", [])
    if target:
        store_data["banner_images"] = [u for u in imgs if u != target]
    elif imgs:
        imgs.pop()
    _save_state()
    return redirect("/admin")

@app.route("/uploads/<path:filename>", methods=['GET', 'POST'])
@app.route("/static/uploads/<path:filename>", methods=['GET', 'POST'])
def serve_upload(filename):
    clean = os.path.basename(filename.split("?")[0])
    if clean and os.path.isfile(os.path.join(UPLOAD_DIR, clean)):
        return send_from_directory(UPLOAD_DIR, clean)
    return store_any_image(clean)

@app.route("/store-image", methods=['GET', 'POST'])
@app.route("/store-image/<path:subpath>", methods=['GET', 'POST'])
def store_any_image(subpath=None):
    if subpath:
        clean = os.path.basename(subpath.split("?")[0])
        if clean and os.path.isfile(os.path.join(UPLOAD_DIR, clean)):
            return send_from_directory(UPLOAD_DIR, clean)
    files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    if files:
        files.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_DIR, x)), reverse=True)
        return send_from_directory(UPLOAD_DIR, files[0])
    return "", 404


@app.route('/admin/save_banner', methods=['GET', 'POST'])
@app.route('/admin/banner/upload', methods=['GET', 'POST'])
def _mna_banner_upload():
    if not _is_logged_in():
        return redirect('/login')
    _load_state()
    files = request.files.getlist('banner_images') or request.files.getlist('images') or request.files.getlist('image') or request.files.getlist('file')
    imgs = store_data.get('banner_images')
    if not isinstance(imgs, list):
        imgs = []
        store_data['banner_images'] = imgs
    for f in files:
        url = _save_uploaded_file(f, 'banner')
        if url:
            imgs.append(url)
    _save_state()
    return redirect('/admin')

@app.route('/admin/banner/delete', methods=['GET', 'POST'])
def _mna_banner_delete():
    if not _is_logged_in():
        return redirect('/login')
    _load_state()
    target = (request.form.get('image_url') or request.args.get('image_url') or request.form.get('url') or '').strip()
    imgs = store_data.get('banner_images', [])
    if target:
        store_data['banner_images'] = [u for u in imgs if u != target]
    elif imgs:
        imgs.pop()
    _save_state()
    return redirect('/admin')

@app.route('/admin/whatsapp', methods=['GET', 'POST'])
def _mna_whatsapp():
    if not _is_logged_in():
        return redirect('/login')
    _load_state()
    wa = (request.form.get('whatsapp') or request.args.get('whatsapp') or '').strip()
    if wa:
        store_data['whatsapp'] = wa
        _save_state()
    return redirect('/admin')

if __name__ == "__main__":
    app.run(debug=True)
