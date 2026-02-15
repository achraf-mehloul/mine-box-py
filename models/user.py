import uuid
from datetime import datetime
import json
import os

class User:
    """نموذج المستخدم"""
    
    DATA_FILE = 'mindbox_data.json'
    
    def __init__(self, user_id=None):
        self.id = user_id or str(uuid.uuid4())
        self.first_name = ""
        self.last_name = ""
        self.email = ""
        self.phone = ""
        self.about = ""
        self.avatar = "/public/default-avatar.png"
        self.created_at = datetime.now().isoformat()
        self.last_login = datetime.now().isoformat()
        self.settings = {
            "theme": "dark",
            "notifications": True,
            "language": "ar"
        }
    
    @staticmethod
    def load_data():
        """تحميل البيانات من ملف JSON"""
        if os.path.exists(User.DATA_FILE):
            try:
                with open(User.DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"users": [], "files": [], "entries": []}
        return {"users": [], "files": [], "entries": []}
    
    @staticmethod
    def save_data(data):
        """حفظ البيانات إلى ملف JSON"""
        with open(User.DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save(self):
        """حفظ المستخدم في قاعدة البيانات"""
        data = self.load_data()
        
        user_exists = False
        for i, user in enumerate(data['users']):
            if user['id'] == self.id:
                data['users'][i] = self.to_dict()
                user_exists = True
                break
        
        if not user_exists:
            data['users'].append(self.to_dict())
        
        self.save_data(data)
        return self.id
    
    def to_dict(self):
        """تحويل المستخدم إلى قاموس"""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": f"{self.first_name} {self.last_name}".strip(),
            "email": self.email,
            "phone": self.phone,
            "about": self.about,
            "avatar": self.avatar,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "settings": self.settings
        }
    
    @staticmethod
    def get_by_id(user_id):
        """البحث عن مستخدم بالمعرف"""
        data = User.load_data()
        for user_data in data['users']:
            if user_data['id'] == user_id:
                user = User(user_id)
                user.__dict__.update(user_data)
                return user
        return None
    
    @staticmethod
    def get_by_email(email):
        """البحث عن مستخدم بالبريد الإلكتروني"""
        data = User.load_data()
        for user_data in data['users']:
            if user_data['email'] == email:
                user = User(user_data['id'])
                user.__dict__.update(user_data)
                return user
        return None
    
    def update_last_login(self):
        """تحديث آخر دخول"""
        self.last_login = datetime.now().isoformat()
        self.save()
    
    def get_storage_usage(self):
        """حساب مساحة التخزين المستخدمة"""
        data = self.load_data()
        total_size = 0
        
        user_entries = [e for e in data['entries'] if e.get('user_id') == self.id]
        
        for entry in user_entries:
            total_size += len(json.dumps(entry)) * 2
        
        if self.avatar and self.avatar != "/public/default-avatar.png":
            avatar_path = self.avatar.lstrip('/')
            if os.path.exists(avatar_path):
                total_size += os.path.getsize(avatar_path)
        
        return total_size  
    
    def get_formatted_storage(self):
        """الحصول على حجم التخزين بشكل مقروء"""
        size = self.get_storage_usage()
        
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size/(1024*1024):.1f} MB"
        else:
            return f"{size/(1024*1024*1024):.1f} GB"