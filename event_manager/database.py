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


def buy_ticket(user_id, event_id):
    import uuid
    from datetime import datetime
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()
        if event is None:
            return {"success": False, "error": "Event not found."}
        if event["tickets_sold"] >= event["tickets_total"]:
            return {"success": False, "error": "This event is sold out."}
        cursor.execute(
            "SELECT id FROM tickets WHERE user_id = ? AND event_id = ?",
            (user_id, event_id)
        )
        if cursor.fetchone():
            return {"success": False, "error": "You already have a ticket for this event."}
        ticket_code   = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO tickets (user_id, event_id, ticket_code, purchase_date, price_paid)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, event_id, ticket_code, purchase_date, event["price"]))
        cursor.execute(
            "UPDATE events SET tickets_sold = tickets_sold + 1 WHERE id = ?",
            (event_id,)
        )
        conn.commit()
        return {
            "success": True,
            "ticket_code": ticket_code,
            "event": event["title"],
            "location": event["location"],
            "price_paid": event["price"],
            "purchase_date": purchase_date,
        }
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def get_user_tickets(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.ticket_code, t.purchase_date, t.price_paid,
               e.title, e.location, e.organiser_name
        FROM tickets t
        JOIN events e ON t.event_id = e.id
        WHERE t.user_id = ?
        ORDER BY t.purchase_date DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
