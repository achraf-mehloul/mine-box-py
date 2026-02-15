import uuid
from datetime import datetime
from .user import User

class Entry:
    """نموذج المدخلة"""
    
    def __init__(self, user_id, file_id, entry_id=None):
        self.id = entry_id or str(uuid.uuid4())
        self.user_id = user_id
        self.file_id = file_id
        self.mood = "😊"
        self.elements = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "file_id": self.file_id,
            "mood": self.mood,
            "elements": self.elements,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def save(self):
        """حفظ المدخلة"""
        data = User.load_data()
        
        if 'entries' not in data:
            data['entries'] = []
        
        entry_exists = False
        for i, e in enumerate(data['entries']):
            if e['id'] == self.id:
                data['entries'][i] = self.to_dict()
                entry_exists = True
                break
        
        if not entry_exists:
            data['entries'].append(self.to_dict())
        
        User.save_data(data)
        return self.id
    
    def delete(self):
        """حذف المدخلة"""
        data = User.load_data()
        data['entries'] = [e for e in data['entries'] if e['id'] != self.id]
        User.save_data(data)
        return True
    
    @staticmethod
    def get_by_id(entry_id):
        """البحث عن مدخلة بالمعرف"""
        data = User.load_data()
        for entry_data in data.get('entries', []):
            if entry_data['id'] == entry_id:
                entry = Entry(entry_data['user_id'], entry_data['file_id'], entry_id)
                entry.__dict__.update(entry_data)
                return entry
        return None
    
    @staticmethod
    def get_user_entries(user_id, file_id=None):
        """الحصول على مدخلات المستخدم"""
        data = User.load_data()
        entries = [e for e in data.get('entries', []) if e['user_id'] == user_id]
        
        if file_id:
            entries = [e for e in entries if e['file_id'] == file_id]
        
        entries.sort(key=lambda x: x['created_at'], reverse=True)
        return entries