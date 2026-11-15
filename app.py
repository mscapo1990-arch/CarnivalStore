import os
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DATA_FILE = 'data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "whatsapp": "9647700000000",
            "products": []
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as df:
            json.dump(default_data, df, ensure_ascii=False, indent=4)
    with open(DATA_FILE, 'r', encoding='utf-8') as df:
        return json.load(df)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as df:
        json.dump(data, df, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', data=data)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    data = load_data()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_whatsapp':
            data['whatsapp'] = request.form.get('whatsapp')
            save_data(data)
        elif action == 'add_product':
            new_prod = {
                "id": len(data['products']) + 1,
                "name": request.form.get('name'),
                "price": request.form.get('price'),
                "type": request.form.get('type'),
                "image": request.form.get('image') or 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500'
            }
            data['products'].append(new_prod)
            save_data(data)
        elif action == 'delete_product':
            prod_id = int(request.form.get('id'))
            data['products'] = [p for p in data['products'] if p['id'] != prod_id]
            save_data(data)
        return redirect(url_for('admin'))
    return render_template('admin.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
