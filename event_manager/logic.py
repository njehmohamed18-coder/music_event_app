# event_manager/logic.py
from .models import Event

# Global list to store events during the session
all_events = []

def add_event_to_list(event_obj):
    """Adds an Event instance to the central list."""
    all_events.append(event_obj)

def show_all_events():
    """Iterates through and prints all posted events."""
    if not all_events:
        print("\nNo events scheduled yet.")
    else:
        print("\n--- Upcoming Music Events ---")
        for event in all_events:
            print(event)