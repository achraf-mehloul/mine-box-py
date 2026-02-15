import uuid
from datetime import datetime
from .user import User

class File:
    """نموذج الملف (الفولدر)"""
    
    def __init__(self, user_id, file_id=None):
        self.id = file_id or str(uuid.uuid4())
        self.user_id = user_id
        self.name = "ملف جديد"
        self.icon = "📁"
        self.color = "#9d4edd"
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "icon": self.icon,
            "color": self.color,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def save(self):
        """حفظ الملف"""
        data = User.load_data()
        
        if 'files' not in data:
            data['files'] = []
        
        file_exists = False
        for i, f in enumerate(data['files']):
            if f['id'] == self.id:
                data['files'][i] = self.to_dict()
                file_exists = True
                break
        
        if not file_exists:
            data['files'].append(self.to_dict())
        
        User.save_data(data)
        return self.id
    
    def delete(self):
        """حذف الملف وجميع مدخلاته"""
        data = User.load_data()
        
        data['files'] = [f for f in data['files'] if f['id'] != self.id]
        
        data['entries'] = [e for e in data['entries'] if e.get('file_id') != self.id]
        
        User.save_data(data)
        return True
    
    @staticmethod
    def get_by_id(file_id):
        """البحث عن ملف بالمعرف"""
        data = User.load_data()
        for file_data in data.get('files', []):
            if file_data['id'] == file_id:
                file = File(file_data['user_id'], file_id)
                file.__dict__.update(file_data)
                return file
        return None
    
    @staticmethod
    def get_user_files(user_id):
        """الحصول على جميع ملفات المستخدم"""
        data = User.load_data()
        return [f for f in data.get('files', []) if f['user_id'] == user_id]
    
    def get_entries_count(self):
        """عدد المدخلات في هذا الملف"""
        data = User.load_data()
        return len([e for e in data.get('entries', []) 
                   if e.get('file_id') == self.id])