from flask import Blueprint, request, jsonify
from models.user import User
from models.stats import Stats

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/<user_id>', methods=['GET'])
def get_user_stats(user_id):
    """الحصول على إحصائيات المستخدم"""
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({
            "success": False,
            "error": "المستخدم غير موجود"
        }), 404
    
    stats = Stats(user_id)
    
    return jsonify({
        "success": True,
        "stats": {
            "basic": stats.get_basic_stats(),
            "mood_distribution": stats.get_mood_distribution(),
            "entries_by_type": stats.get_entries_by_type(),
            "productivity_score": stats.get_productivity_score()
        }
    }), 200

@stats_bp.route('/<user_id>/activity', methods=['GET'])
def get_activity(user_id):
    """الحصول على سجل النشاط"""
    days = request.args.get('days', 30, type=int)
    
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({
            "success": False,
            "error": "المستخدم غير موجود"
        }), 404
    
    stats = Stats(user_id)
    activity = stats.get_activity_by_day(days)
    
    return jsonify({
        "success": True,
        "activity": activity,
        "days": days
    }), 200

@stats_bp.route('/<user_id>/achievements', methods=['GET'])
def get_achievements(user_id):
    """الحصول على إنجازات المستخدم"""
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({
            "success": False,
            "error": "المستخدم غير موجود"
        }), 404
    
    stats = Stats(user_id)
    achievements = stats.get_achievements()
    
    return jsonify({
        "success": True,
        "achievements": achievements,
        "count": len(achievements)
    }), 200

@stats_bp.route('/<user_id>/storage', methods=['GET'])
def get_storage_info(user_id):
    """الحصول على معلومات التخزين"""
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({
            "success": False,
            "error": "المستخدم غير موجود"
        }), 404
    
    used_bytes = user.get_storage_usage()
    used_formatted = user.get_formatted_storage()
    
    limit_bytes = 100 * 1024 * 1024
    percentage = (used_bytes / limit_bytes) * 100
    
    return jsonify({
        "success": True,
        "storage": {
            "used_bytes": used_bytes,
            "used_formatted": used_formatted,
            "limit_bytes": limit_bytes,
            "limit_formatted": "100 MB",
            "percentage": round(percentage, 1),
            "remaining_bytes": limit_bytes - used_bytes,
            "remaining_formatted": User.get_formatted_storage_bytes(limit_bytes - used_bytes)
        }
    }), 200

@stats_bp.route('/<user_id>/productivity', methods=['GET'])
def get_productivity(user_id):
    """الحصول على تحليل الإنتاجية"""
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({
            "success": False,
            "error": "المستخدم غير موجود"
        }), 404
    
    stats = Stats(user_id)
    score = stats.get_productivity_score()
    basic = stats.get_basic_stats()
    
    analysis = {
        "score": score,
        "level": "ممتاز" if score >= 80 else "جيد" if score >= 60 else "متوسط" if score >= 40 else "بحاجة للتحسين",
        "strengths": [],
        "weaknesses": []
    }
    
    if basic['completed_tasks'] > 20:
        analysis['strengths'].append("إنجاز المهام")
    if basic['total_entries'] > 30:
        analysis['strengths'].append("الكتابة المنتظمة")
    if len(stats.get_achievements()) > 3:
        analysis['strengths'].append("تنوع الإنجازات")
    
    if basic['task_completion_rate'] < 50:
        analysis['weaknesses'].append("نسبة إنجاز المهام منخفضة")
    if basic['total_entries'] < 10:
        analysis['weaknesses'].append("قلة المدخلات")
    if len(stats.get_entries_by_type()) < 3:
        analysis['weaknesses'].append("قلة تنوع المحتوى")
    
    return jsonify({
        "success": True,
        "productivity": analysis
    }), 200

@staticmethod
def get_formatted_storage_bytes(bytes_size):
    """تنسيق حجم الملف بشكل مقروء"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size/1024:.1f} KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size/(1024*1024):.1f} MB"
    else:
        return f"{bytes_size/(1024*1024*1024):.1f} GB"

User.get_formatted_storage_bytes = staticmethod(get_formatted_storage_bytes)