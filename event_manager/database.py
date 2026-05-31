import sqlite3
import bcrypt

DB_PATH = "events.db"


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
            price REAL NOT NULL CHECK(price >= 0),
            lineup TEXT NOT NULL,
            organiser_name TEXT NOT NULL,
            tickets_total INTEGER DEFAULT 100 CHECK(tickets_total > 0),
            tickets_sold INTEGER DEFAULT 0 CHECK(tickets_sold >= 0),
            event_date TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
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
            quantity INTEGER DEFAULT 1 CHECK(quantity > 0),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    """)
    conn.commit()
    conn.close()


def validate_email(email):
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def validate_required(value, field_name):
    if not value or not value.strip():
        raise ValueError(f"{field_name} is required")


def validate_price(price):
    try:
        p = float(price)
        if p < 0:
            raise ValueError("Price cannot be negative")
        return p
    except (ValueError, TypeError):
        raise ValueError("Price must be a valid non-negative number")


def register_user(username, email, password, role, company_name=None, description=None):
    validate_required(username, "Username")
    validate_required(email, "Email")
    validate_required(password, "Password")
    if not validate_email(email):
        raise ValueError("Invalid email format")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters")
    
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, company_name, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username.strip(), email.strip().lower(), password_hash, role, 
              company_name.strip() if company_name else None, 
              description.strip() if description else None))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE id = last_insert_rowid()")
        row = cursor.fetchone()
        return dict(row)
    except sqlite3.IntegrityError as e:
        if "username" in str(e).lower():
            raise ValueError("Username already taken")
        elif "email" in str(e).lower():
            raise ValueError("Email already registered")
        raise ValueError("Username or email already exists")
    finally:
        conn.close()


def login_user(email, password):
    validate_required(email, "Email")
    validate_required(password, "Password")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email.strip().lower(),)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return None
    
    stored_hash = row["password_hash"].encode('utf-8')
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        return dict(row)
    return None


def save_event(event):
    conn = get_connection()
    cursor = conn.cursor()
    lineup_string = ", ".join(event.lineup)
    cursor.execute("""
        INSERT INTO events (title, location, price, lineup, organiser_name, event_date, tickets_total)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (event.title.strip(), event.location.strip(), event.price, 
          lineup_string, event.organizer.strip(), event.event_date, event.tickets_total))
    conn.commit()
    event_id = cursor.lastrowid
    conn.close()
    return event_id


def _row_to_event(row):
    from .models import MusicEvent
    lineup = [a.strip() for a in row["lineup"].split(",") if a.strip()]
    event = MusicEvent(
        row["title"], row["location"], row["price"], 
        lineup, row["organiser_name"], row["event_date"]
    )
    event.id = row["id"]
    event.tickets_total = row["tickets_total"]
    event.tickets_sold = row["tickets_sold"]
    return event


def load_all_events():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_event(row) for row in rows]


def search_events_by_artist(artist_name):
    if not artist_name or not artist_name.strip():
        return []
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM events WHERE lineup LIKE ? ORDER BY event_date ASC",
        (f"%{artist_name.strip()}%",)
    )
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_event(row) for row in rows]


def get_events_by_organizer(organizer_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM events WHERE organiser_name = ? ORDER BY event_date ASC",
        (organizer_name,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [_row_to_event(row) for row in rows]


def update_event(event_id, **kwargs):
    allowed = {"title", "location", "price", "lineup", "event_date", "tickets_total"}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return False
    
    if "lineup" in updates and isinstance(updates["lineup"], list):
        updates["lineup"] = ", ".join(updates["lineup"])
    
    conn = get_connection()
    cursor = conn.cursor()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [event_id]
    cursor.execute(f"UPDATE events SET {set_clause} WHERE id = ?", values)
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def delete_event(event_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def buy_ticket(user_id, event_id, quantity=1):
    import uuid
    from datetime import datetime
    
    if quantity < 1:
        return {"success": False, "error": "Quantity must be at least 1"}
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN IMMEDIATE")
        
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        event = cursor.fetchone()
        if event is None:
            return {"success": False, "error": "Event not found."}
        
        available = event["tickets_total"] - event["tickets_sold"]
        if available < quantity:
            return {"success": False, "error": f"Only {available} ticket(s) remaining."}
        
        cursor.execute(
            "SELECT SUM(quantity) as total FROM tickets WHERE user_id = ? AND event_id = ?",
            (user_id, event_id)
        )
        existing = cursor.fetchone()["total"] or 0
        if existing > 0:
            return {"success": False, "error": "You already have ticket(s) for this event."}
        
        ticket_code = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_price = event["price"] * quantity
        
        cursor.execute("""
            INSERT INTO tickets (user_id, event_id, ticket_code, purchase_date, price_paid, quantity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, event_id, ticket_code, purchase_date, total_price, quantity))
        
        cursor.execute(
            "UPDATE events SET tickets_sold = tickets_sold + ? WHERE id = ?",
            (quantity, event_id)
        )
        
        conn.commit()
        return {
            "success": True,
            "ticket_code": ticket_code,
            "event": event["title"],
            "location": event["location"],
            "price_paid": total_price,
            "purchase_date": purchase_date,
            "quantity": quantity,
        }
    except sqlite3.Error as e:
        conn.rollback()
        return {"success": False, "error": f"Database error: {e}"}
    finally:
        conn.close()


def get_user_tickets(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.ticket_code, t.purchase_date, t.price_paid, t.quantity,
               e.title, e.location, e.organiser_name, e.event_date
        FROM tickets t
        JOIN events e ON t.event_id = e.id
        WHERE t.user_id = ?
        ORDER BY t.purchase_date DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def cancel_ticket(user_id, ticket_code):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            "SELECT * FROM tickets WHERE ticket_code = ? AND user_id = ?",
            (ticket_code, user_id)
        )
        ticket = cursor.fetchone()
        if ticket is None:
            return {"success": False, "error": "Ticket not found."}
        
        cursor.execute(
            "UPDATE events SET tickets_sold = tickets_sold - ? WHERE id = ?",
            (ticket["quantity"], ticket["event_id"])
        )
        cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket["id"],))
        conn.commit()
        return {"success": True, "message": "Ticket cancelled successfully."}
    except sqlite3.Error as e:
        conn.rollback()
        return {"success": False, "error": f"Database error: {e}"}
    finally:
        conn.close()
