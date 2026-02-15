from flask import Blueprint, request, jsonify
from models.user import User
from models.file import File
from models.entry import Entry
from models.stats import Stats

file_bp = Blueprint('files', __name__)

@file_bp.route('', methods=['GET'])
def get_files():
    """الحصول على جميع ملفات المستخدم"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "success": False,
            "error": "معرف المستخدم مطلوب"
        }), 400
    
    files = File.get_user_files(user_id)
    
    for file in files:
        file['entries_count'] = len([e for e in User.load_data().get('entries', []) 
                                    if e.get('file_id') == file['id']])
    
    return jsonify({
        "success": True,
        "files": files
    }), 200

@file_bp.route('/<file_id>', methods=['GET'])
def get_file(file_id):
    """الحصول على ملف محدد"""
    file = File.get_by_id(file_id)
    if not file:
        return jsonify({
            "success": False,
            "error": "الملف غير موجود"
        }), 404
    
    file_data = file.to_dict()
    file_data['entries'] = Entry.get_user_entries(file.user_id, file_id)
    file_data['entries_count'] = len(file_data['entries'])
    
    return jsonify({
        "success": True,
        "file": file_data
    }), 200

@file_bp.route('', methods=['POST'])
def create_file():
    """إنشاء ملف جديد"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        name = data.get('name')
        icon = data.get('icon', '📁')
        color = data.get('color', '#9d4edd')
        
        if not user_id or not name:
            return jsonify({
                "success": False,
                "error": "معرف المستخدم واسم الملف مطلوبان"
            }), 400
        
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({
                "success": False,
                "error": "المستخدم غير موجود"
            }), 404
        
        file = File(user_id)
        file.name = name
        file.icon = icon
        file.color = color
        file.save()
        
        return jsonify({
            "success": True,
            "message": "تم إنشاء الملف بنجاح",
            "file": file.to_dict()
        }), 201
        
    except Exception as e:
        print(f"خطأ في إنشاء الملف: {e}")
        return jsonify({
            "success": False,
            "error": "حدث خطأ أثناء إنشاء الملف"
        }), 500

@file_bp.route('/<file_id>', methods=['PUT'])
def update_file(file_id):
    """تحديث ملف"""
    try:
        file = File.get_by_id(file_id)
        if not file:
            return jsonify({
                "success": False,
                "error": "الملف غير موجود"
            }), 404
        
        data = request.get_json()
        
        if 'name' in data:
            file.name = data['name']
        if 'icon' in data:
            file.icon = data['icon']
        if 'color' in data:
            file.color = data['color']
        
        file.save()
        
        return jsonify({
            "success": True,
            "message": "تم تحديث الملف بنجاح",
            "file": file.to_dict()
        }), 200
        
    except Exception as e:
        print(f"خطأ في تحديث الملف: {e}")
        return jsonify({
            "success": False,
            "error": "حدث خطأ أثناء تحديث الملف"
        }), 500

@file_bp.route('/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """حذف ملف"""
    try:
        file = File.get_by_id(file_id)
        if not file:
            return jsonify({
                "success": False,
                "error": "الملف غير موجود"
            }), 404
        
        file.delete()
        
        return jsonify({
            "success": True,
            "message": "تم حذف الملف بنجاح"
        }), 200
        
    except Exception as e:
        print(f"خطأ في حذف الملف: {e}")
        return jsonify({
            "success": False,
            "error": "حدث خطأ أثناء حذف الملف"
        }), 500