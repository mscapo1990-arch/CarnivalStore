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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
