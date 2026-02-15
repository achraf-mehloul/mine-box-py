from flask import Blueprint, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import io
from models.user import User

auth_bp = Blueprint('auth', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_IMAGE_SIZE = (500, 500)  

def allowed_file(filename):
    """التحقق من صيغة الملف المسموح بها"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def optimize_image(image_file):
    """تحسين الصورة وتغيير حجمها"""
    try:
        img = Image.open(image_file)
        
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
        
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        return output
    except Exception as e:
        print(f"خطأ في تحسين الصورة: {e}")
        return None

@auth_bp.route('/register', methods=['POST'])
def register():
    """تسجيل مستخدم جديد"""
    try:
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        about = request.form.get('about', '')
        
        if not all([first_name, last_name, email, phone]):
            return jsonify({
                "success": False,
                "error": "الرجاء ملء جميع الحقول المطلوبة"
            }), 400
        
        existing_user = User.get_by_email(email)
        if existing_user:
            return jsonify({
                "success": False,
                "error": "البريد الإلكتروني مستخدم مسبقاً"
            }), 400
        
        user = User()
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone = phone
        user.about = about
        
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename and allowed_file(file.filename):
                optimized = optimize_image(file)
                if optimized:
                    filename = f"{user.id}.jpg"
                    filepath = os.path.join('public/avatars', filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(optimized.getvalue())
                    
                    user.avatar = f"/public/avatars/{filename}"
        
        user.save()
        
        return jsonify({
            "success": True,
            "message": "تم التسجيل بنجاح",
            "user": user.to_dict()
        }), 201
        
    except Exception as e:
        print(f"خطأ في التسجيل: {e}")
        return jsonify({
            "success": False,
            "error": "حدث خطأ أثناء التسجيل"
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """تسجيل الدخول"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({
                "success": False,
                "error": "الرجاء إدخال البريد الإلكتروني"
            }), 400
        
        user = User.get_by_email(email)
        
        if not user:
            return jsonify({
                "success": False,
                "error": "المستخدم غير موجود"
            }), 404
        
        user.update_last_login()
        
        return jsonify({
            "success": True,
            "message": "تم تسجيل الدخول بنجاح",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"خطأ في تسجيل الدخول: {e}")
        return jsonify({
            "success": False,
            "error": "حدث خطأ أثناء تسجيل الدخول"
        }), 500

@auth_bp.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    """الحصول على بيانات المستخدم"""
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({
            "success": False,
            "error": "المستخدم غير موجود"
        }), 404
    
    return jsonify({
        "success": True,
        "user": user.to_dict()
    }), 200

@auth_bp.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    """تحديث بيانات المستخدم"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({
                "success": False,
                "error": "المستخدم غير موجود"
            }), 404
        
        data = request.get_json()
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'about' in data:
            user.about = data['about']
        if 'settings' in data:
            user.settings.update(data['settings'])
        
        user.save()
        
        return jsonify({
            "success": True,
            "message": "تم تحديث البيانات بنجاح",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"خطأ في تحديث المستخدم: {e}")
        return jsonify({
            "success": False,
            "error": "حدث خطأ أثناء تحديث البيانات"
        }), 500

@auth_bp.route('/user/<user_id>/avatar', methods=['POST'])
def update_avatar(user_id):
    """تحديث الصورة الشخصية"""
    try:
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({
                "success": False,
                "error": "المستخدم غير موجود"
            }), 404
        
        if 'avatar' not in request.files:
            return jsonify({
                "success": False,
                "error": "الرجاء اختيار صورة"
            }), 400
        
        file = request.files['avatar']
        if not file or not file.filename:
            return jsonify({
                "success": False,
                "error": "الملف غير صالح"
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": "صيغة الملف غير مدعومة. استخدم: PNG, JPG, JPEG, GIF, WEBP"
            }), 400
        
        optimized = optimize_image(file)
        if not optimized:
            return jsonify({
                "success": False,
                "error": "فشل في معالجة الصورة"
            }), 500
        
        if user.avatar and user.avatar != "/public/default-avatar.png":
            old_path = user.avatar.lstrip('/')
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except:
                    pass
        
        filename = f"{user.id}.jpg"
        filepath = os.path.join('public/avatars', filename)
        
        with open(filepath, 'wb') as f:
            f.write(optimized.getvalue())
        
        user.avatar = f"/public/avatars/{filename}"
        user.save()
        
        return jsonify({
            "success": True,
            "message": "تم تحديث الصورة بنجاح",
            "avatar": user.avatar
        }), 200
        
    except Exception as e:
        print(f"خطأ في تحديث الصورة: {e}")
        return jsonify({
            "success": False,
            "error": "حدث خطأ أثناء تحديث الصورة"
        }), 500