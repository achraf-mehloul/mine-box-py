from flask import Blueprint, request, jsonify
from models.user import User
from models.file import File
from models.entry import Entry
from datetime import datetime

entry_bp = Blueprint('entries', __name__)

@entry_bp.route('', methods=['GET'])
def get_entries():
    """الحصول على مدخلات المستخدم"""
    user_id = request.args.get('user_id')
    file_id = request.args.get('file_id')
    
    if not user_id:
        return jsonify({
            "success": False,
            "error": "معرف المستخدم مطلوب"
        }), 400
    
    entries = Entry.get_user_entries(user_id, file_id)
    
    return jsonify({
        "success": True,
        "entries": entries
    }), 200

@entry_bp.route('/<entry_id>', methods=['GET'])
def get_entry(entry_id):
    """الحصول على مدخلة محددة"""
    entry = Entry.get_by_id(entry_id)
    if not entry:
        return jsonify({
            "success": False,
            "error": "المدخلة غير موجودة"
        }), 404
    
    return jsonify({
        "success": True,
        "entry": entry.to_dict()
    }), 200

@entry_bp.route('', methods=['POST'])
def create_entry():
    """إنشاء مدخلة جديدة"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        file_id = data.get('file_id')
        mood = data.get('mood', '😊')
        elements = data.get('elements', [])
        
        if not user_id or not file_id:
            return jsonify({
                "success": False,
                "error": "معرف المستخدم والملف مطلوبان"
            }), 400
        
        if not elements:
            return jsonify({
                "success": False,
                "error": "يجب إضافة عنصر واحد على الأقل"
            }), 400
        
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({
                "success": False,
                "error": "المستخدم غير موجود"
            }), 404
        
        file = File.get_by_id(file_id)
        if not file:
            return jsonify({
                "success": False,
                "error": "الملف غير موجود"
            }), 404
        
        entry = Entry(user_id, file_id)
        entry.mood = mood
        entry.elements = elements
        entry.save()
        
        return jsonify({
            "success": True,
            "message": "تم إنشاء المدخلة بنجاح",
            "entry": entry.to_dict()
        }), 201
        
    except Exception as e:
        print(f"خطأ في إنشاء المدخلة: {e}")
        return jsonify({
            "success": False,
            "error": "حدث خطأ أثناء إنشاء المدخلة"
        }), 500

@entry_bp.route('/<entry_id>', methods=['PUT'])
def update_entry(entry_id):
    """تحديث مدخلة"""
    try:
        entry = Entry.get_by_id(entry_id)
        if not entry:
            return jsonify({
                "success": False,
                "error": "المدخلة غير موجودة"
            }), 404
        
        data = request.get_json()
        
        if 'mood' in data:
            entry.mood = data['mood']
        if 'elements' in data:
            entry.elements = data['elements']
        
        entry.updated_at = datetime.now().isoformat()
        entry.save()
        
        return jsonify({
            "success": True,
            "message": "تم تحديث المدخلة بنجاح",
            "entry": entry.to_dict()
        }), 200
        
    except Exception as e:
        print(f"خطأ في تحديث المدخلة: {e}")
        return jsonify({
            "success": False,
            "error": "حدث خطأ أثناء تحديث المدخلة"
        }), 500

@entry_bp.route('/<entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    """حذف مدخلة"""
    try:
        entry = Entry.get_by_id(entry_id)
        if not entry:
            return jsonify({
                "success": False,
                "error": "المدخلة غير موجودة"
            }), 404
        
        entry.delete()
        
        return jsonify({
            "success": True,
            "message": "تم حذف المدخلة بنجاح"
        }), 200
        
    except Exception as e:
        print(f"خطأ في حذف المدخلة: {e}")
        return jsonify({
            "success": False,
            "error": "حدث خطأ أثناء حذف المدخلة"
        }), 500

@entry_bp.route('/file/<file_id>/recent', methods=['GET'])
def get_recent_entries(file_id):
    """الحصول على آخر 10 مدخلات في ملف"""
    file = File.get_by_id(file_id)
    if not file:
        return jsonify({
            "success": False,
            "error": "الملف غير موجود"
        }), 404
    
    entries = Entry.get_user_entries(file.user_id, file_id)
    recent = entries[:10] 
    
    return jsonify({
        "success": True,
        "entries": recent
    }), 200