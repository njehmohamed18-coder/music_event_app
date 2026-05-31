from .models import User, Organizer, Guest, MusicEvent
from .database import init_db, save_event, load_all_events, search_events_by_artist