with open('main.py', 'w') as f:
    f.write('''# main.py
import sys
from datetime import datetime
from event_manager import (
    Organizer, Guest, init_db,
    save_event, load_all_events, search_events_by_artist,
    get_events_by_organizer, update_event, delete_event,
    register_user, login_user, buy_ticket, get_user_tickets, cancel_ticket
)

def pause():
    input("\\nPress Enter to continue...")

def get_valid_input(prompt, validator=None, error_msg="Invalid input."):
    while True:
        value = input(prompt).strip()
        if not value:
            print("This field is required.")
            continue
        if validator and not validator(value):
            print(error_msg)
            continue
        return value

def get_valid_date(prompt):
    while True:
        date_str = input(prompt).strip()
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            if dt.date() < datetime.now().date():
                print("Event date must be in the future.")
                continue
            return date_str
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD (e.g., 2026-06-15)")

def get_valid_price(prompt):
    while True:
        try:
            price = float(input(prompt).strip())
            if price < 0:
                print("Price cannot be negative.")
                continue
            return price
        except ValueError:
            print("Please enter a valid number.")

def get_valid_int(prompt, min_val=1, max_val=None):
    while True:
        try:
            val = int(input(prompt).strip())
            if val < min_val:
                print(f"Must be at least {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"Must be at most {max_val}.")
                continue
            return val
        except ValueError:
            print("Please enter a valid whole number.")

def select_from_list(items, prompt="Select:", display_fn=str):
    if not items:
        print("No items available.")
        return None
    for idx, item in enumerate(items, 1):
        print(f" {idx}. {display_fn(item)}")
    choice = get_valid_int(f"\\n{prompt} ", 1, len(items))
    return items[choice - 1]

def sign_up_flow():
    print("\\n--- Create your account ---")
    username = get_valid_input("Username: ")
    email = get_valid_input("Email: ", validator=lambda e: "@" in e and "." in e, error_msg="Please enter a valid email.")
    while True:
        password = get_valid_input("Password (min 6 chars): ")
        if len(password) >= 6:
            break
        print("Password must be at least 6 characters.")
    print("\\nJoining as:")
    print(" 1. Normal user   (explore events, buy tickets)")
    print(" 2. Organiser     (post events, manage lineup)")
    role_choice = get_valid_int("Choose (1-2): ", 1, 2)
    if role_choice == 1:
        role, company_name, description = "user", None, None
    else:
        role = "organiser"
        print("\\n--- Your collective / company ---")
        company_name = get_valid_input("Collective or company name: ")
        description = input("Short description: ").strip() or None
    try:
        user = register_user(username, email, password, role, company_name, description)
        print(f"\\nAccount created! Welcome, {username}.")
        return user
    except ValueError as e:
        print(f"\\n{e}")
        return None

def login_flow():
    print("\\n--- Log in ---")
    email = get_valid_input("Email: ")
    password = get_valid_input("Password: ")
    user = login_user(email, password)
    if user:
        print(f"\\nWelcome back, {user['username']}!")
        return user
    else:
        print("\\nWrong email or password.")
        return None

def auth_menu():
    while True:
        print("\\n" + "="*55)
        print("   MUSIC EVENT MANAGER")
        print("="*55)
        print(" 1. Sign up")
        print(" 2. Log in")
        print(" 3. Exit")
        choice = get_valid_int("\\nChoose (1-3): ", 1, 3)
        if choice == 1:
            user = sign_up_flow()
            if user: return user
        elif choice == 2:
            user = login_flow()
            if user: return user
        elif choice == 3:
            print("\\nGoodbye!")
            sys.exit()

def run_organizer_portal(current_user):
    organizer = Organizer(current_user["username"], current_user["email"], current_user.get("company_name", "Unknown"))
    options = organizer.get_menu_options()
    while True:
        print(f"\\nWelcome, {organizer.username}! What would you like to do?")
        for idx, opt in enumerate(options, 1):
            print(f" {idx}. {opt}")
        choice = get_valid_int("\\nSelect an option: ", 1, len(options))
        if choice == 1:
            print("\\n--- CREATE A NEW MUSIC EVENT ---")
            title = get_valid_input("Event Title: ")
            location = get_valid_input("Venue / Location: ")
            price = get_valid_price("Ticket Price (EUR): ")
            event_date = get_valid_date("Event Date (YYYY-MM-DD): ")
            tickets_total = get_valid_int("Total Tickets Available: ", 1)
            artists_raw = get_valid_input("Artists in Lineup (comma-separated): ")
            lineup = [a.strip() for a in artists_raw.split(",") if a.strip()]
            new_event = organizer.create_event(title, location, price, lineup, event_date, tickets_total)
            event_id = save_event(new_event)
            new_event.id = event_id
            print(f"\\nEvent '{new_event.title}' published for {event_date}!")
            pause()
        elif choice == 2:
            print(f"\\n--- EVENTS BY {organizer.company_name} ---")
            my_events = get_events_by_organizer(organizer.company_name)
            if not my_events:
                print("No events posted yet.")
            for idx, event in enumerate(my_events, 1):
                print(f"\\n[Event #{idx}]")
                print(event.get_details())
            pause()
        elif choice == 3:
            print("\\n--- EDIT AN EVENT ---")
            my_events = get_events_by_organizer(organizer.company_name)
            if not my_events:
                print("No events to edit.")
                pause()
                continue
            event = select_from_list(my_events, "Select event to edit:", lambda e: f"{e.title} ({e.event_date})")
            if event is None:
                pause()
                continue
            print("\\nLeave blank to keep current value.")
            new_title = input(f"New Title [{event.title}]: ").strip() or None
            new_location = input(f"New Location [{event.location}]: ").strip() or None
            price_input = input(f"New Price [EUR {event.price}]: ").strip()
            new_price = float(price_input) if price_input else None
            new_date = input(f"New Date [{event.event_date}]: ").strip() or None
            updates = {}
            if new_title: updates["title"] = new_title
            if new_location: updates["location"] = new_location
            if new_price is not None: updates["price"] = new_price
            if new_date: updates["event_date"] = new_date
            if updates:
                if update_event(event.id, **updates):
                    print("\\nEvent updated successfully!")
                else:
                    print("\\nFailed to update event.")
            else:
                print("No changes made.")
            pause()
        elif choice == 4:
            print("\\n--- DELETE AN EVENT ---")
            my_events = get_events_by_organizer(organizer.company_name)
            if not my_events:
                print("No events to delete.")
                pause()
                continue
            event = select_from_list(my_events, "Select event to delete:", lambda e: f"{e.title} ({e.event_date})")
            if event is None:
                pause()
                continue
            confirm = input(f"\\nAre you sure you want to delete '{event.title}'? (yes/no): ").strip().lower()
            if confirm == "yes":
                if delete_event(event.id):
                    print("\\nEvent deleted.")
                else:
                    print("\\nFailed to delete event.")
            else:
                print("Cancelled.")
            pause()
        elif choice == 5:
            break

def run_guest_portal(current_user):
    guest = Guest(current_user["username"], current_user["email"])
    user_id = current_user.get("id")
    options = guest.get_menu_options()
    while True:
        print(f"\\nHello, {guest.username}! What would you like to do?")
        for idx, opt in enumerate(options, 1):
            print(f" {idx}. {opt}")
        choice = get_valid_int("\\nSelect an option: ", 1, len(options))
        if choice == 1:
            print("\\n--- ALL UPCOMING EVENTS ---")
            events = load_all_events()
            upcoming = [e for e in events if e.is_upcoming()]
            if not upcoming:
                print("No upcoming events published yet.")
            for idx, event in enumerate(upcoming, 1):
                print(f"\\n[EVENT #{idx}]")
                print(event.get_details())
            pause()
        elif choice == 2:
            print("\\n--- SEARCH BY ARTIST ---")
            artist_search = input("Enter artist name: ").strip()
            if not artist_search:
                print("Please enter an artist name.")
                pause()
                continue
            filtered_events = search_events_by_artist(artist_search)
            upcoming = [e for e in filtered_events if e.is_upcoming()]
            if not upcoming:
                print(f"No upcoming events found featuring '{artist_search}'.")
            else:
                for idx, event in enumerate(upcoming, 1):
                    print(f"\\n[Result #{idx}]")
                    print(event.get_details())
            pause()
        elif choice == 3:
            print("\\n--- BUY A TICKET ---")
            events = load_all_events()
            upcoming = [e for e in events if e.is_upcoming() and e.tickets_available > 0]
            if not upcoming:
                print("No events with available tickets.")
                pause()
                continue
            event = select_from_list(upcoming, "Select event:", lambda e: f"{e.title} @ {e.location} ({e.event_date})")
            if event is None:
                pause()
                continue
            max_qty = min(event.tickets_available, 10)
            quantity = get_valid_int(f"How many tickets? (1-{max_qty}): ", 1, max_qty)
            result = buy_ticket(user_id, event.id, quantity)
            if result["success"]:
                print(f"\\nTicket confirmed!")
                print(f"   Code:   {result['ticket_code']}")
                print(f"   Event:  {result['event']} @ {result['location']}")
                print(f"   Qty:    {result['quantity']}")
                print(f"   Paid:   EUR {result['price_paid']:.2f}")
                print(f"   Date:   {result['purchase_date']}")
            else:
                print(f"\\n{result['error']}")
            pause()
        elif choice == 4:
            print("\\n--- MY TICKETS ---")
            tickets = get_user_tickets(user_id)
            if not tickets:
                print("You haven't bought any tickets yet.")
            for idx, t in enumerate(tickets, 1):
                print(f"\\n[Ticket #{idx}]")
                print(f"  Event:    {t['title']} @ {t['location']}")
                print(f"  Date:     {t['event_date']}")
                print(f"  Code:     {t['ticket_code']}")
                print(f"  Qty:      {t['quantity']}")
                print(f"  Paid:     EUR {t['price_paid']:.2f}")
                print(f"  Bought:   {t['purchase_date']}")
            pause()
        elif choice == 5:
            print("\\n--- CANCEL A TICKET ---")
            tickets = get_user_tickets(user_id)
            if not tickets:
                print("You have no tickets to cancel.")
                pause()
                continue
            ticket = select_from_list(tickets, "Select ticket to cancel:", lambda t: f"{t['title']} ({t['ticket_code']})")
            if ticket is None:
                pause()
                continue
            confirm = input(f"\\nCancel ticket {ticket['ticket_code']}? (yes/no): ").strip().lower()
            if confirm == "yes":
                result = cancel_ticket(user_id, ticket['ticket_code'])
                if result["success"]:
                    print(f"\\n{result['message']}")
                else:
                    print(f"\\n{result['error']}")
            else:
                print("Cancelled.")
            pause()
        elif choice == 6:
            break

def main():
    init_db()
    current_user = auth_menu()
    if current_user["role"] == "organiser":
        run_organizer_portal(current_user)
    else:
        run_guest_portal(current_user)
    print("\\nThanks for using Music Event Manager!")

if __name__ == "__main__":
    main()
''')
print("main.py updated successfully!")
