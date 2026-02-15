from datetime import datetime, timedelta
from collections import Counter
from .storage import StorageManager

class StatsCalculator:
    def __init__(self, user_id):
        self.user_id = user_id
        self.data = StorageManager.load_data()
        self.user_entries = [e for e in self.data.get('entries', []) if e.get('user_id') == user_id]
        self.user_files = [f for f in self.data.get('files', []) if f.get('user_id') == user_id]
        self.user = next((u for u in self.data.get('users', []) if u.get('id') == user_id), None)
    
    def get_basic_stats(self):
        return {
            "total_entries": len(self.user_entries),
            "total_files": len(self.user_files),
            "total_tasks": self._count_tasks(),
            "completed_tasks": self._count_completed_tasks(),
            "task_completion_rate": self._get_completion_rate(),
            "account_age": self._get_account_age(),
            "last_active": self._get_last_active()
        }
    
    def _count_tasks(self):
        tasks = 0
        for entry in self.user_entries:
            for element in entry.get('elements', []):
                if element.get('type') == 'checklist':
                    tasks += len(element.get('items', []))
        return tasks
    
    def _count_completed_tasks(self):
        completed = 0
        for entry in self.user_entries:
            for element in entry.get('elements', []):
                if element.get('type') == 'checklist':
                    for item in element.get('items', []):
                        if item.get('checked'):
                            completed += 1
        return completed
    
    def _get_completion_rate(self):
        total = self._count_tasks()
        completed = self._count_completed_tasks()
        if total == 0:
            return 0
        return round((completed / total) * 100, 1)
    
    def _get_account_age(self):
        if not self.user:
            return 0
        created = datetime.fromisoformat(self.user.get('created_at', datetime.now().isoformat()))
        days = (datetime.now() - created).days
        return days
    
    def _get_last_active(self):
        if not self.user_entries:
            return "لم يسجل نشاط بعد"
        last_entry = max(self.user_entries, key=lambda x: x.get('created_at', ''))
        last_date = datetime.fromisoformat(last_entry['created_at'])
        days_ago = (datetime.now() - last_date).days
        if days_ago == 0:
            return "اليوم"
        elif days_ago == 1:
            return "أمس"
        else:
            return f"منذ {days_ago} أيام"
    
    def get_mood_distribution(self):
        moods = [entry.get('mood', '😐') for entry in self.user_entries]
        return dict(Counter(moods))
    
    def get_activity_by_day(self, days=30):
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
        types = {"text": 0, "checklist": 0, "highlight": 0, "problem": 0, "achievement": 0}
        for entry in self.user_entries:
            for element in entry.get('elements', []):
                element_type = element.get('type')
                if element_type in types:
                    types[element_type] += 1
        return types
    
    def get_productivity_score(self):
        score = 0
        basic = self.get_basic_stats()
        score += min(30, basic['completed_tasks'] * 3)
        activity = self.get_activity_by_day(7)
        active_days = len(activity)
        score += min(20, active_days * 5)
        score += min(20, len(self.user_files) * 7)
        entry_types = len([t for t in self.get_entries_by_type().values() if t > 0])
        score += min(15, entry_types * 3)
        problems = self.get_entries_by_type().get('problem', 0)
        score += min(15, problems * 3)
        return min(100, score)
    
    def get_weekly_streak(self):
        if not self.user_entries:
            return 0
        dates = sorted([datetime.fromisoformat(e['created_at']).date() for e in self.user_entries])
        streak = 1
        max_streak = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 1
        return max_streak
    
    def get_mood_variety(self):
        moods = set(entry.get('mood', '😐') for entry in self.user_entries)
        return len(moods)