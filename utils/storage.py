import os
import json
from pathlib import Path

class StorageManager:
    BASE_DIR = Path(__file__).parent.parent
    DATA_FILE = BASE_DIR / 'mindbox_data.json'
    AVATAR_DIR = BASE_DIR / 'public' / 'avatars'
    
    @classmethod
    def ensure_directories(cls):
        cls.AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def load_data(cls):
        if cls.DATA_FILE.exists():
            try:
                with open(cls.DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"users": [], "files": [], "entries": []}
        return {"users": [], "files": [], "entries": []}
    
    @classmethod
    def save_data(cls, data):
        with open(cls.DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def get_user_storage_usage(cls, user_id):
        data = cls.load_data()
        total_size = 0
        user_entries = [e for e in data.get('entries', []) if e.get('user_id') == user_id]
        for entry in user_entries:
            total_size += len(json.dumps(entry)) * 2
        avatar_path = cls.AVATAR_DIR / f"{user_id}.jpg"
        if avatar_path.exists():
            total_size += avatar_path.stat().st_size
        return total_size
    
    @classmethod
    def format_size(cls, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.1f} GB"
    
    @classmethod
    def delete_old_avatar(cls, user_id):
        avatar_path = cls.AVATAR_DIR / f"{user_id}.jpg"
        if avatar_path.exists():
            avatar_path.unlink()
    
    @classmethod
    def save_avatar(cls, user_id, image_data):
        cls.ensure_directories()
        avatar_path = cls.AVATAR_DIR / f"{user_id}.jpg"
        with open(avatar_path, 'wb') as f:
            f.write(image_data)
        return f"/public/avatars/{user_id}.jpg"