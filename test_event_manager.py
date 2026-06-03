import pytest
import os
import sys
import bcrypt
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ["DB_PATH"] = "test_events.db"

import event_manager.database as db_module
db_module.DB_PATH = "test_events.db"

from event_manager.database import (
    init_db, get_connection, register_user, login_user,
    save_event, load_all_events, search_events_by_artist,
    get_events_by_organizer, update_event, delete_event,
    buy_ticket, get_user_tickets, cancel_ticket,
    validate_email, validate_required, validate_price
)
from event_manager.models import Organizer, Guest, MusicEvent


@pytest.fixture(autouse=True)
def setup_db():
    if os.path.exists("test_events.db"):
        os.remove("test_events.db")
    init_db()
    yield
    if os.path.exists("test_events.db"):
        os.remove("test_events.db")


@pytest.fixture
def sample_organizer():
    return register_user("dj_mike", "mike@beats.com", "password123", "organiser",
                         "Beat Collective", "Underground music events")


@pytest.fixture
def sample_user():
    return register_user("alice", "alice@music.com", "password123", "user")


@pytest.fixture
def sample_event(sample_organizer):
    event = MusicEvent("Summer Vibes", "Berlin Arena", 25.0,
                       ["DJ Shadow", "Four Tet"], "Beat Collective", "2026-08-15", tickets_total=50)
    event_id = save_event(event)
    event.id = event_id
    return event


def test_validate_email_valid():
    assert validate_email("test@example.com") is True


def test_validate_email_invalid():
    assert validate_email("notanemail") is False


def test_validate_required():
    validate_required("hello", "field")
    with pytest.raises(ValueError):
        validate_required("", "field")


def test_validate_price():
    assert validate_price("10.5") == 10.5
    with pytest.raises(ValueError):
        validate_price("-5")


def test_register_user_success(sample_organizer):
    assert sample_organizer["username"] == "dj_mike"
    assert sample_organizer["role"] == "organiser"


def test_login_user_success(sample_organizer):
    user = login_user("mike@beats.com", "password123")
    assert user is not None
    assert user["username"] == "dj_mike"


def test_login_user_wrong_password(sample_organizer):
    user = login_user("mike@beats.com", "wrongpassword")
    assert user is None


def test_password_is_hashed(sample_organizer):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE id = ?", (sample_organizer["id"],))
    row = cursor.fetchone()
    conn.close()
    stored_hash = row["password_hash"]
    assert stored_hash != "password123"
    assert bcrypt.checkpw(b"password123", stored_hash.encode('utf-8'))


def test_save_event(sample_organizer):
    event = MusicEvent("Test", "Venue", 15.0, ["Artist"], "Beat Collective", "2026-09-01", 100)
    event_id = save_event(event)
    assert event_id is not None


def test_load_all_events(sample_event):
    events = load_all_events()
    assert len(events) == 1
    assert events[0].title == "Summer Vibes"


def test_search_events_by_artist(sample_event):
    results = search_events_by_artist("DJ Shadow")
    assert len(results) == 1


def test_buy_ticket_success(sample_event, sample_user):
    result = buy_ticket(sample_user["id"], sample_event.id, quantity=2)
    assert result["success"] is True
    assert result["quantity"] == 2


def test_buy_ticket_sold_out(sample_event, sample_user):
    buy_ticket(sample_user["id"], sample_event.id, quantity=50)
    user2 = register_user("bob", "bob@test.com", "password123", "user")
    result = buy_ticket(user2["id"], sample_event.id, quantity=1)
    assert result["success"] is False


def test_cancel_ticket(sample_event, sample_user):
    result = buy_ticket(sample_user["id"], sample_event.id, quantity=2)
    ticket_code = result["ticket_code"]
    cancel_result = cancel_ticket(sample_user["id"], ticket_code)
    assert cancel_result["success"] is True


def test_update_event_owner(sample_event):
    # Owner can update their own event
    updated = update_event(sample_event.id, organiser_name="Beat Collective", title="New Title")
    assert updated is True


def test_update_event_wrong_owner(sample_event):
    # A different organiser cannot update someone else's event
    updated = update_event(sample_event.id, organiser_name="Fake Org", title="Hacked Title")
    assert updated is False


def test_delete_event_owner(sample_event):
    deleted = delete_event(sample_event.id, organiser_name="Beat Collective")
    assert deleted is True


def test_delete_event_wrong_owner(sample_event):
    deleted = delete_event(sample_event.id, organiser_name="Fake Org")
    assert deleted is False


def test_music_event_creation():
    event = MusicEvent("Test", "Venue", 10.0, ["Artist"], "Org", "2026-06-01")
    assert event.title == "Test"


def test_organizer_menu():
    org = Organizer("dj", "dj@test.com", "My Company")
    options = org.get_menu_options()
    assert len(options) == 5


def test_guest_menu():
    guest = Guest("alice", "alice@test.com")
    options = guest.get_menu_options()
    assert len(options) == 6
