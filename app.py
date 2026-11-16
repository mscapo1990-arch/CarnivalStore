import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

store_data = {
    "whatsapp": "9647700000000",
    "products": []
}

@app.route('/')
def index():
    category = request.args.get('category', 'الكل')
    products = store_data["products"]
    if category != 'الكل':
        products = [p for p in products if p.get('category') == category]
    return render_template('index.html', products=products, whatsapp=store_data["whatsapp"], current_category=category)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
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
