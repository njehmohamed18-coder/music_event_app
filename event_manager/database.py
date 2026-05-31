from .models import MusicEvent

import sqlite3

DB_NAME = "music_events.db"

def init_db():
    """Initializes the SQLite database and creates the events table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            location TEXT NOT NULL,
            price REAL NOT NULL,
            lineup TEXT NOT NULL,
            organizer TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def save_event(event):
    """Takes a MusicEvent object, serializes the lineup list to a string, and saves it."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    lineup_string = ", ".join(event.lineup)
    
    cursor.execute('''
        INSERT INTO events (title, location, price, lineup, organizer)
        VALUES (?, ?, ?, ?, ?)
    ''', (event.title, event.location, event.price, lineup_string, event.organizer))
    
    conn.commit()
    conn.close()

def load_all_events():
    """Fetches all events from the database and converts them back into MusicEvent objects."""
    # Move the import inside this function to break the circular dependency loop!
    from .models import MusicEvent
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT title, location, price, lineup, organizer FROM events')
    rows = cursor.fetchall()
    
    events_list = []
    for row in rows:
        title, location, price, lineup_str, organizer = row
        lineup = [artist.strip() for artist in lineup_str.split(",")]
        
        event_obj = MusicEvent(title, location, price, lineup, organizer)
        events_list.append(event_obj)
        
    conn.close()
    return events_list

def search_events_by_artist(artist_name):
    """Filters and returns events where the requested artist is part of the lineup string."""
    # Move the import inside this function to break the circular dependency loop!
    from .models import MusicEvent
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = 'SELECT title, location, price, lineup, organizer FROM events WHERE lineup LIKE ?'
    cursor.execute(query, (f"%{artist_name}%",))
    rows = cursor.fetchall()
    
    events_list = []
    for row in rows:
        title, location, price, lineup_str, organizer = row
        lineup = [artist.strip() for artist in lineup_str.split(",")]
        event_obj = MusicEvent(title, location, price, lineup, organizer)
        events_list.append(event_obj)
        
    conn.close()
    return events_list