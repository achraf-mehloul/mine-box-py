from .auth_routes import auth_bp
from .file_routes import file_bp
from .entry_routes import entry_bp
from .stats_routes import stats_bp

__all__ = ['auth_bp', 'file_bp', 'entry_bp', 'stats_bp']