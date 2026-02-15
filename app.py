from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

CORS(app)  

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
app.config['UPLOAD_FOLDER'] = 'public/avatars'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mindbox-secret-key-2026')

os.makedirs('public/avatars', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('templates/components', exist_ok=True)

from api.auth_routes import auth_bp
from api.file_routes import file_bp
from api.entry_routes import entry_bp
from api.stats_routes import stats_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(file_bp, url_prefix='/api/files')
app.register_blueprint(entry_bp, url_prefix='/api/entries')
app.register_blueprint(stats_bp, url_prefix='/api/stats')

@app.route('/')
def index():
    """الصفحة الرئيسية - التطبيق"""
    return render_template('index.html')

@app.route('/login')
def login():
    """صفحة تسجيل الدخول"""
    return render_template('login.html')

@app.route('/profile')
def profile():
    """صفحة الحساب الشخصي"""
    return render_template('profile.html')

@app.route('/stats')
def stats():
    """صفحة الإحصائيات المفصلة"""
    return render_template('stats.html')

@app.route('/public/<path:filename>')
def public_files(filename):
    return send_from_directory('public', filename)

@app.route('/public/avatars/<path:filename>')
def avatar_files(filename):
    return send_from_directory('public/avatars', filename)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "الصفحة غير موجودة"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "خطأ داخلي في الخادم"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)