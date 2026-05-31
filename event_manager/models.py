# event_manager/models.py

class User:
    """Base class demonstrating encapsulation and core user attributes."""
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def get_menu_options(self):
        """Polymorphic method to be overridden by child classes."""
        raise NotImplementedError("Subclasses must implement this method")


class Organizer(User):
    """Inherits from User. Represents an event manager with publishing privileges."""
    def __init__(self, username, email, company_name):
        super().__init__(username, email)
        self.company_name = company_name

    def get_menu_options(self):
        # Polymorphic response specific to Organizers
        return [
            "Post a New Music Event",
            "View My Hosted Events",
            "Return to Main Menu"
        ]

    def create_event(self, title, location, price, lineup):
        # Imports are placed inside methods if needed to break cyclic dependencies
        return MusicEvent(title, location, price, lineup, self.company_name)


class Guest(User):
    """Inherits from User. Represents a customer browsing the database."""
    def __init__(self, username, email):
        super().__init__(username, email)

    def get_menu_options(self):
        # Polymorphic response specific to Guests
        return [
            "Browse All Active Music Events",
            "Search Events by Artist/Lineup",
            "Return to Main Menu"
        ]


class MusicEvent:
    """Class to represent the structured music event details."""
    def __init__(self, title, location, price, lineup, organizer):
        self.title = title
        self.location = location
        self.price = price
        self.lineup = lineup  # Expects a list of strings
        self.organizer = organizer

    def get_details(self):
        artists = " | ".join(self.lineup)
        return (f"✨ {self.title.upper()} ✨\n"
                f"📍 Venue  : {self.location}\n"
                f"🎟️ Price  : {self.price:.2f} €\n"
                f"🎧 Lineup : {artists}\n"
                f"🏢 Agency : {self.organizer}\n"
                f"{'-'*45}")