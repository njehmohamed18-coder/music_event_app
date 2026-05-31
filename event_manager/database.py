import sqlite3

DB_PATH = "events.db"
DB_NAME = DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            location TEXT NOT NULL,
            price REAL NOT NULL,
            lineup TEXT NOT NULL,
            organiser_name TEXT NOT NULL,
            tickets_total INTEGER DEFAULT 100,
            tickets_sold INTEGER DEFAULT 0,
            event_date TEXT
        )
    """)
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_id INTEGER NOT NULL,
            ticket_code TEXT UNIQUE NOT NULL,
            purchase_date TEXT NOT NULL,
            price_paid REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    """)
    conn.commit()
    conn.close()


def register_user(username, email, password, role, company_name=None, description=None):
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
        return False
    finally:
        conn.close()


def login_user(email, password):
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
    conn = get_connection()
    cursor = conn.cursor()
    lineup_string = ", ".join(event.lineup)
    cursor.execute("""
        INSERT INTO events (title, location, price, lineup, organiser_name)
        VALUES (?, ?, ?, ?, ?)
    """, (event.title, event.location, event.price, lineup_string, event.organizer))
    conn.commit()
    conn.close()


def load_all_events():
    from .models import MusicEvent
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, location, price, lineup, organiser_name FROM events")
    rows = cursor.fetchall()
    conn.close()
    events_list = []
    for row in rows:
        lineup = [a.strip() for a in row["lineup"].split(",")]
        event_obj = MusicEvent(row["title"], row["location"], row["price"], lineup, row["organiser_name"])
        events_list.append(event_obj)
    return events_list


def search_events_by_artist(artist_name):
    from .models import MusicEvent
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT title, location, price, lineup, organiser_name FROM events WHERE lineup LIKE ?",
        (f"%{artist_name}%",)
    )
    rows = cursor.fetchall()
    conn.close()
    events_list = []
    for row in rows:
        lineup = [a.strip() for a in row["lineup"].split(",")]
        event_obj = MusicEvent(row["title"], row["location"], row["price"], lineup, row["organiser_name"])
        events_list.append(event_obj)
    return events_list
