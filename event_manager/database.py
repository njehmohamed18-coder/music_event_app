from .models import MusicEvent

import sqlite3

DB_NAME = "music_events.db"

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # existing events table stays as-is ...

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'organiser')),
            company_name TEXT,
            description TEXT
        )
    """)

    conn.commit()
    conn.close()

def register_user(username, email, password, role, company_name=None, description=None):
    """Saves a new user to the database. Returns True on success, False if email/username already exists."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, email, password, role, company_name, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, email, password, role, company_name, description))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # username or email already taken
        return False
    finally:
        conn.close()


def login_user(email, password):
    """Returns the user row as a dict if credentials match, otherwise None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email, password)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


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