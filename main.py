# main.py
from event_manager.models import Organizer
from event_manager.logic import add_event_to_list, show_all_events

def run_app():
    # 1. Create an Organizer session
    dj_admin = Organizer("Berlin_Techno_Promotions")
    
    # 2. Simulate posting an event
    new_event = dj_admin.post_event(
        "Industrial Night", 
        "Hangar 4", 
        25, 
        ["Artist A", "Artist B"]
    )
    add_event_to_list(new_event)

    # 3. View as a guest
    show_all_events()

if __name__ == "__main__":
 run_app()