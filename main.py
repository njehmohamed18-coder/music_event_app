#main
import sys
from event_manager import Organizer, Guest, init_db, save_event, load_all_events, search_events_by_artist

def run_organizer_portal():
    print("\n" + "-"*60)
    print("🔑 ORGANIZER PORTAL: Initialize Session")
    print("-"*60)
    username = input("Enter your Username: ")
    email = input("Enter your Email: ")
    company = input("Enter your Company/Agency Name: ")
    
    # OOP Instantiate
    organizer = Organizer(username, email, company)
    options = organizer.get_menu_options() # Polymorphism at work
    
    while True:
        print(f"\nWelcome back, {organizer.username}! What would you like to do?")
        for idx, opt in enumerate(options, 1):
            print(f" {idx}. {opt}")
            
        choice = input("\n👉 Select an option (1-3): ")
        
        if choice == "1":
            print("\n" + "-"*60)
            print("📝 CREATE A NEW MUSIC EVENT")
            print("-"*60)
            title = input("Enter Event Title: ")
            location = input("Enter Venue / Location: ")
            
            try:
                price = float(input("Enter Ticket Price (€): "))
            except ValueError:
                print("❌ Invalid price format. Setting to 0.0 €")
                price = 0.0
                
            artists_raw = input("Enter Artists in Lineup (separate by commas): ")
            lineup = [a.strip() for a in artists_raw.split(",") if a.strip()]
            
            # Use Organizer method to instantiate MusicEvent
            new_event = organizer.create_event(title, location, price, lineup)
            
            print("\n[System] Instantiating 'MusicEvent' object matching your schema...")
            print("[Database] Serializing lineup list to string stream...")
            save_event(new_event)
            print(f"\n✅ Event '{new_event.title}' has been successfully published!")
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            print("\n" + "-"*60)
            print(f"📋 ALL EVENTS HOSTED BY: {organizer.company_name}")
            print("-"*60)
            all_events = load_all_events()
            my_events = [e for e in all_events if e.organizer == organizer.company_name]
            
            if not my_events:
                print("You haven't posted any events yet.")
            for idx, event in enumerate(my_events, 1):
                print(f"\n[Hosted Event #{idx}]")
                print(event.get_details())
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            break

def run_guest_portal():
    print("\n" + "-"*60)
    print("🔍 GUEST PORTAL: Welcome Music Enthusiast")
    print("-"*60)
    username = input("Enter a temporary username to browse: ")
    
    guest = Guest(username, email=f"{username}@example.com")
    options = guest.get_menu_options() # Polymorphism at work
    
    while True:
        print(f"\nGuest Mode ({guest.username}) Menu:")
        for idx, opt in enumerate(options, 1):
            print(f" {idx}. {opt}")
            
        choice = input("\n👉 Select an option (1-3): ")
        
        if choice == "1":
            print("\n" + "-"*60)
            print("🔍 BROWSE ALL ACTIVE MUSIC EVENTS")
            print("-"*60)
            events = load_all_events()
            if not events:
                print("No music events have been published yet.")
            for idx, event in enumerate(events, 1):
                print(f"\n[EVENT #{idx}]")
                print(event.get_details())
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            print("\n" + "-"*60)
            print("🎧 SEARCH LINEUPS BY ARTIST")
            print("-"*60)
            artist_search = input("Enter artist name to look up: ")
            filtered_events = search_events_by_artist(artist_search)
            
            if not filtered_events:
                print(f"No upcoming events found featuring '{artist_search}'.")
            else:
                print(f"\nFound {len(filtered_events)} event(s) matching your search:")
                for idx, event in enumerate(filtered_events, 1):
                    print(f"\n[Result #{idx}]")
                    print(event.get_details())
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            break

def main():
    init_db() # Ensures SQLite setup runs seamlessly
    
    while True:
        print("\n" + "="*60)
        print("   🎵  WELCOME TO THE MUSIC EVENT MANAGER APPLICATION  🎵")
        print("="*60)
        print("[System] Running safely inside Virtual Environment (venv).")
        print("[System] Data Persistence Mode: Active (Records persist inside SQLite).")
        print("\nPlease choose your role to continue:")
        print(" 1. Enter as an Event Organizer (Post & Manage Events)")
        print(" 2. Enter as a Guest User (Browse & Explore Lineups)")
        print(" 3. Exit Application")
        
        main_choice = input("\n👉 Select an option (1-3): ")
        
        if main_choice == "1":
            run_organizer_portal()
        elif main_choice == "2":
            run_guest_portal()
        elif main_choice == "3":
            print("\nThank you for using Music Event Manager. Goodbye! 👋")
            sys.exit()
        else:
            print("❌ Invalid option choice. Please choose 1, 2, or 3.")

if __name__ == "__main__":
    main()