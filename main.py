# main.py
import sys
from event_manager import (
    Organizer, Guest, init_db,
    save_event, load_all_events, search_events_by_artist,
    register_user, login_user, buy_ticket, get_user_tickets
)

# ─────────────────────────────────────────
# AUTH FLOWS
# ─────────────────────────────────────────

def sign_up_flow():
    print("\n--- Create your account ---")
    username = input("Username: ").strip()
    email    = input("Email: ").strip()
    password = input("Password: ").strip()

    print("\nJoining as:")
    print(" 1. Normal user   (explore events, buy tickets)")
    print(" 2. Organiser     (post events, manage lineup)")
    role_choice = input("👉 Choose (1-2): ").strip()

    if role_choice == "1":
        role, company_name, description = "user", None, None
    elif role_choice == "2":
        role = "organiser"
        print("\n--- Your collective / company ---")
        company_name = input("Collective or company name: ").strip()
        description  = input("Short description: ").strip()
    else:
        print("❌ Invalid choice.")
        return None

    success = register_user(username, email, password, role, company_name, description)
    if success:
        print(f"\n✅ Account created! Welcome, {username}.")
        return {"username": username, "email": email, "role": role,
                "company_name": company_name, "description": description}
    else:
        print("❌ Username or email already taken. Try logging in.")
        return None


def login_flow():
    print("\n--- Log in ---")
    email    = input("Email: ").strip()
    password = input("Password: ").strip()
    user = login_user(email, password)
    if user:
        print(f"\n✅ Welcome back, {user['username']}!")
        return user
    else:
        print("❌ Wrong email or password.")
        return None


def auth_menu():
    while True:
        print("\n" + "="*50)
        print("   🎵 MUSIC EVENT MANAGER")
        print("="*50)
        print(" 1. Sign up")
        print(" 2. Log in")
        print(" 3. Exit")
        choice = input("\n👉 Choose (1-3): ").strip()

        if choice == "1":
            user = sign_up_flow()
            if user:
                return user
        elif choice == "2":
            user = login_flow()
            if user:
                return user
        elif choice == "3":
            print("\nGoodbye! 👋")
            sys.exit()


# ─────────────────────────────────────────
# ORGANISER PORTAL
# ─────────────────────────────────────────

def run_organizer_portal(current_user):
    organizer = Organizer(
        current_user["username"],
        current_user["email"],
        current_user["company_name"]
    )
    options = organizer.get_menu_options()

    while True:
        print(f"\nWelcome, {organizer.username}! What would you like to do?")
        for idx, opt in enumerate(options, 1):
            print(f" {idx}. {opt}")

        choice = input("\n👉 Select an option: ").strip()

        if choice == "1":
            print("\n--- CREATE A NEW MUSIC EVENT ---")
            title    = input("Event Title: ")
            location = input("Venue / Location: ")
            try:
                price = float(input("Ticket Price (€): "))
            except ValueError:
                print("❌ Invalid price. Setting to 0.0 €")
                price = 0.0
            artists_raw = input("Artists in Lineup (comma-separated): ")
            lineup = [a.strip() for a in artists_raw.split(",") if a.strip()]

            new_event = organizer.create_event(title, location, price, lineup)
            save_event(new_event)
            print(f"\n✅ Event '{new_event.title}' published!")
            input("\nPress Enter to continue...")

        elif choice == "2":
            print(f"\n--- EVENTS BY {organizer.company_name} ---")
            all_events = load_all_events()
            my_events  = [e for e in all_events if e.organizer == organizer.company_name]
            if not my_events:
                print("No events posted yet.")
            for idx, event in enumerate(my_events, 1):
                print(f"\n[Event #{idx}]")
                print(event.get_details())
            input("\nPress Enter to continue...")

        elif choice == "3":
            break


# ─────────────────────────────────────────
# USER PORTAL
# ─────────────────────────────────────────

def run_guest_portal(current_user):
    guest   = Guest(current_user["username"], current_user["email"])
    user_id = current_user.get("id")
    options = guest.get_menu_options()

    while True:
        print(f"\nHello, {guest.username}! What would you like to do?")
        for idx, opt in enumerate(options, 1):
            print(f" {idx}. {opt}")

        choice = input("\n👉 Select an option: ").strip()

        if choice == "1":
            # ── Browse all events ──
            print("\n--- ALL UPCOMING EVENTS ---")
            events = load_all_events()
            if not events:
                print("No events published yet.")
            for idx, event in enumerate(events, 1):
                print(f"\n[EVENT #{idx}]")
                print(event.get_details())
            input("\nPress Enter to continue...")

        elif choice == "2":
            # ── Search by artist ──
            print("\n--- SEARCH BY ARTIST ---")
            artist_search   = input("Enter artist name: ")
            filtered_events = search_events_by_artist(artist_search)
            if not filtered_events:
                print(f"No events found featuring '{artist_search}'.")
            else:
                for idx, event in enumerate(filtered_events, 1):
                    print(f"\n[Result #{idx}]")
                    print(event.get_details())
            input("\nPress Enter to continue...")

        elif choice == "3":
            # ── Buy a ticket ──
            print("\n--- BUY A TICKET ---")
            events = load_all_events()
            if not events:
                print("No events available.")
                input("\nPress Enter to continue...")
                continue

            for idx, event in enumerate(events, 1):
                print(f" {idx}. {event.get_details()}")

            try:
                event_choice = int(input("\nEnter event number to buy: ")) - 1
                if event_choice < 0 or event_choice >= len(events):
                    print("❌ Invalid selection.")
                    input("\nPress Enter to continue...")
                    continue
            except ValueError:
                print("❌ Please enter a number.")
                input("\nPress Enter to continue...")
                continue

            if user_id is None:
                print("❌ Cannot buy ticket — user ID not found. Please log in again.")
                input("\nPress Enter to continue...")
                continue

            result = buy_ticket(user_id, event_choice + 1)
            if result["success"]:
                print(f"\n🎟️  Ticket confirmed!")
                print(f"   Code:   {result['ticket_code']}")
                print(f"   Event:  {result['event']} @ {result['location']}")
                print(f"   Paid:   €{result['price_paid']}")
                print(f"   Date:   {result['purchase_date']}")
            else:
                print(f"\n❌ {result['error']}")
            input("\nPress Enter to continue...")

        elif choice == "4":
            # ── My tickets ──
            print("\n--- MY TICKETS ---")
            if user_id is None:
                print("❌ Cannot load tickets — user ID not found.")
                input("\nPress Enter to continue...")
                continue

            tickets = get_user_tickets(user_id)
            if not tickets:
                print("You haven't bought any tickets yet.")
            for idx, t in enumerate(tickets, 1):
                print(f"\n[Ticket #{idx}]")
                print(f"  Event:    {t['title']} @ {t['location']}")
                print(f"  Code:     {t['ticket_code']}")
                print(f"  Paid:     €{t['price_paid']}")
                print(f"  Bought:   {t['purchase_date']}")
            input("\nPress Enter to continue...")

        elif choice == "5":
            break


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    init_db()
    current_user = auth_menu()

    if current_user["role"] == "organiser":
        run_organizer_portal(current_user)
    else:
        run_guest_portal(current_user)


if __name__ == "__main__":
    main()
