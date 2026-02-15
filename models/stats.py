from datetime import datetime, timedelta
from collections import Counter
from .user import User

class Stats:
    """نموذج الإحصائيات"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.data = User.load_data()
        self.user = User.get_by_id(user_id)
        self.user_entries = [e for e in self.data.get('entries', []) 
                            if e.get('user_id') == user_id]
        self.user_files = [f for f in self.data.get('files', []) 
                          if f.get('user_id') == user_id]
    
    def get_basic_stats(self):
        """إحصائيات أساسية"""
        return {
            "total_entries": len(self.user_entries),
            "total_files": len(self.user_files),
            "total_tasks": self._count_tasks(),
            "completed_tasks": self._count_completed_tasks(),
            "task_completion_rate": self._get_completion_rate(),
            "storage_used": self.user.get_formatted_storage() if self.user else "0 B",
            "account_age": self._get_account_age(),
            "last_active": self._get_last_active()
        }
    
    def _count_tasks(self):
        """عدد المهام في جميع المدخلات"""
        tasks = 0
        for entry in self.user_entries:
            for element in entry.get('elements', []):
                if element.get('type') == 'checklist':
                    tasks += len(element.get('items', []))
        return tasks
    
    def _count_completed_tasks(self):
        """عدد المهام المكتملة"""
        completed = 0
        for entry in self.user_entries:
            for element in entry.get('elements', []):
                if element.get('type') == 'checklist':
                    for item in element.get('items', []):
                        if item.get('checked'):
                            completed += 1
        return completed
    
    def _get_completion_rate(self):
        """نسبة إنجاز المهام"""
        total = self._count_tasks()
        completed = self._count_completed_tasks()
        if total == 0:
            return 0
        return round((completed / total) * 100, 1)
    
    def _get_account_age(self):
        """عمر الحساب بالأيام"""
        if not self.user:
            return 0
        created = datetime.fromisoformat(self.user.created_at)
        days = (datetime.now() - created).days
        return days
    
    def _get_last_active(self):
        """آخر نشاط"""
        if not self.user_entries:
            return "لم يسجل نشاط بعد"
        last_entry = max(self.user_entries, 
                        key=lambda x: x.get('created_at', ''))
        last_date = datetime.fromisoformat(last_entry['created_at'])
        days_ago = (datetime.now() - last_date).days
        
        if days_ago == 0:
            return "اليوم"
        elif days_ago == 1:
            return "أمس"
        else:
            return f"منذ {days_ago} أيام"
    
    def get_mood_distribution(self):
        """توزيع المزاج"""
        moods = [entry.get('mood', '😐') for entry in self.user_entries]
        return dict(Counter(moods))
    
    def get_activity_by_day(self, days=30):
        """النشاط حسب اليوم"""
        activity = {}
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        for entry in self.user_entries:
            entry_date = datetime.fromisoformat(entry['created_at']).date()
            if entry_date >= start_date.date():
                date_str = entry_date.isoformat()
                activity[date_str] = activity.get(date_str, 0) + 1
        
        return activity
    
    def get_entries_by_type(self):
        """المدخلات حسب النوع"""
        types = {
            "text": 0,
            "checklist": 0,
            "highlight": 0,
            "problem": 0,
            "achievement": 0
        }
        
        for entry in self.user_entries:
            for element in entry.get('elements', []):
                element_type = element.get('type')
                if element_type in types:
                    types[element_type] += 1
        
        return types
    
    def get_achievements(self):
        """قائمة الإنجازات المحققة"""
        achievements = []
        basic_stats = self.get_basic_stats()
        
        if basic_stats['total_entries'] >= 10:
            achievements.append({
                "id": "entry_10",
                "name": "الكاتب النشط",
                "description": "أضفت 10 مدخلات",
                "icon": "📝",
                "date": "محقق",
                "color": "#9d4edd"
            })
        
        if basic_stats['total_entries'] >= 50:
            achievements.append({
                "id": "entry_50",
                "name": "الكاتب المحترف",
                "description": "أضفت 50 مدخلة",
                "icon": "✍️",
                "date": "محقق",
                "color": "#c77dff"
            })
        if basic_stats['completed_tasks'] >= 20:
            achievements.append({
                "id": "task_20",
                "name": "منجز المهام",
                "description": "أنجزت 20 مهمة",
                "icon": "✅",
                "date": "محقق",
                "color": "#00b8a9"
            })
        
        problem_count = self.get_entries_by_type().get('problem', 0)
        if problem_count >= 5:
            achievements.append({
                "id": "problem_solver",
                "name": "حلال المشاكل",
                "description": "سجلت 5 مشاكل مع حلولها",
                "icon": "⚠️",
                "date": "محقق",
                "color": "#f85f5f"
            })
        
        achievement_count = self.get_entries_by_type().get('achievement', 0)
        if achievement_count >= 10:
            achievements.append({
                "id": "achiever",
                "name": "صاحب الإنجازات",
                "description": "سجلت 10 إنجازات",
                "icon": "🏆",
                "date": "محقق",
                "color": "#ff9e00"
            })
        
        if len(self.user_files) >= 3:
            achievements.append({
                "id": "organized",
                "name": "منظم محترف",
                "description": "أنشأت 3 ملفات مختلفة",
                "icon": "📁",
                "date": "محقق",
                "color": "#7b2cbf"
            })
        
        return achievements
    
    def get_productivity_score(self):
        """نقاط الإنتاجية (من 100)"""
        score = 0
        basic_stats = self.get_basic_stats()
        
        score += min(30, basic_stats['completed_tasks'] * 3)
        
        activity = self.get_activity_by_day(7)
        active_days = len(activity)
        score += min(20, active_days * 5)
        
        score += min(20, len(self.user_files) * 7)
        
        entry_types = len(self.get_entries_by_type())
        score += min(15, entry_types * 3)
        
        problems = self.get_entries_by_type().get('problem', 0)
        score += min(15, problems * 3)
        
        return min(100, score)