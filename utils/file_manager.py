import os
import shutil
from pathlib import Path
from .storage import StorageManager

class FileManager:
    @staticmethod
    def create_user_folder_structure(user_id):
        base_dir = Path(__file__).parent.parent
        folders = [
            base_dir / 'public' / 'avatars',
            base_dir / 'data',
            base_dir / 'static' / 'css',
            base_dir / 'static' / 'js',
            base_dir / 'templates' / 'components'
        ]
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def backup_data():
        base_dir = Path(__file__).parent.parent
        source = base_dir / 'mindbox_data.json'
        if not source.exists():
            return
        backup_dir = base_dir / 'backups'
        backup_dir.mkdir(exist_ok=True)
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        destination = backup_dir / f'mindbox_data_{timestamp}.json'
        shutil.copy2(source, destination)
        backups = sorted(backup_dir.glob('mindbox_data_*.json'))
        if len(backups) > 10:
            for old_backup in backups[:-10]:
                old_backup.unlink()
    
    @staticmethod
    def clean_old_avatars(days=30):
        base_dir = Path(__file__).parent.parent
        avatar_dir = base_dir / 'public' / 'avatars'
        if not avatar_dir.exists():
            return
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=days)
        data = StorageManager.load_data()
        active_users = {u['id'] for u in data.get('users', [])}
        for avatar in avatar_dir.glob('*.jpg'):
            if avatar.stem not in active_users:
                mtime = datetime.fromtimestamp(avatar.stat().st_mtime)
                if mtime < cutoff:
                    avatar.unlink()
    
    @staticmethod
    def get_file_size(filepath):
        path = Path(filepath)
        if path.exists():
            return path.stat().st_size
        return 0
    
    @staticmethod
    def ensure_default_avatar():
        base_dir = Path(__file__).parent.parent
        default_avatar = base_dir / 'public' / 'default-avatar.png'
        if not default_avatar.exists():
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (500, 500), color=(157, 78, 221))
            d = ImageDraw.Draw(img)
            d.text((250, 250), "🧠", fill='white', anchor='mm')
            img.save(default_avatar)