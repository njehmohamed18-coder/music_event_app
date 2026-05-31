# event_manager/__init__.py
from .database import init_db, get_connection, register_user, login_user
from .database import save_event, load_all_events, search_events_by_artist
from .models import Organizer, Guest, MusicEvent