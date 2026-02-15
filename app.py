from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__, 
            static_folder='static',
            template_folder='.')

DATA_FILE = 'mindbox_data.json'

DEFAULT_DATA = {
    "files": [],
    "entries": []
}

def load_data():
    """تحميل البيانات من ملف JSON المحلي"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return DEFAULT_DATA.copy()
    return DEFAULT_DATA.copy()

def save_data(data):
    """حفظ البيانات إلى ملف JSON المحلي"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(load_data())

@app.route('/api/files', methods=['POST'])
def create_file():
    data = load_data()
    new_file = request.json
    
    file_entry = {
        "id": str(uuid.uuid4()),
        "name": new_file.get('name', 'ملف جديد'),
        "icon": new_file.get('icon', '📁'),
        "color": new_file.get('color', '#9d4edd'),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    data['files'].append(file_entry)
    save_data(data)
    return jsonify(file_entry)

@app.route('/api/files/<file_id>', methods=['PUT'])
def update_file(file_id):
    data = load_data()
    updates = request.json
    
    for file in data['files']:
        if file['id'] == file_id:
            file.update(updates)
            file['updated_at'] = datetime.now().isoformat()
            save_data(data)
            return jsonify(file)
    
    return jsonify({"error": "الملف غير موجود"}), 404

@app.route('/api/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    data = load_data()
    data['files'] = [f for f in data['files'] if f['id'] != file_id]
    data['entries'] = [e for e in data['entries'] if e['file_id'] != file_id]
    save_data(data)
    return jsonify({"success": True})

@app.route('/api/entries', methods=['POST'])
def create_entry():
    data = load_data()
    new_entry = request.json
    
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    
    if hour < 12:
        ampm = "صباحاً"
        if hour == 0:
            hour = 12
    else:
        ampm = "مساءً"
        if hour > 12:
            hour = hour - 12
    
    time_str = f"{hour}:{minute:02d} {ampm}"
    
    entry = {
        "id": str(uuid.uuid4()),
        "file_id": new_entry['file_id'],
        "time": time_str,
        "date": now.isoformat(),
        "mood": new_entry.get('mood', '😊'),
        "elements": new_entry.get('elements', [])
    }
    
    data['entries'].append(entry)
    save_data(data)
    return jsonify(entry)

@app.route('/api/entries/<entry_id>', methods=['PUT'])
def update_entry(entry_id):
    data = load_data()
    updates = request.json
    
    for entry in data['entries']:
        if entry['id'] == entry_id:
            entry.update(updates)
            save_data(data)
            return jsonify(entry)
    
    return jsonify({"error": "المدخلة غير موجودة"}), 404

@app.route('/api/entries/<entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    data = load_data()
    data['entries'] = [e for e in data['entries'] if e['id'] != entry_id]
    save_data(data)
    return jsonify({"success": True})

@app.route('/public/<path:filename>')
def public_files(filename):
    return send_from_directory('public', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)