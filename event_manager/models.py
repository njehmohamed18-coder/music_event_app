# event_manager/models.py
from datetime import datetime


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
        return [
            "Post a New Music Event",
            "View My Hosted Events",
            "Edit an Event",
            "Delete an Event",
            "Return to Main Menu"
        ]

    def create_event(self, title, location, price, lineup, event_date, tickets_total=100):
        return MusicEvent(title, location, price, lineup, self.company_name, event_date, tickets_total)


class Guest(User):
    """Inherits from User. Represents a customer browsing the database."""
    def __init__(self, username, email):
        super().__init__(username, email)

    def get_menu_options(self):
        return [
            "Browse All Active Music Events",
            "Search Events by Artist/Lineup",
            "Buy a Ticket",
            "View My Tickets",
            "Cancel a Ticket",
            "Return to Main Menu"
        ]


class MusicEvent:
    """Class to represent the structured music event details."""
    def __init__(self, title, location, price, lineup, organizer, event_date, tickets_total=100):
        self.id = None
        self.title = title
        self.location = location
        self.price = price
        self.lineup = lineup
        self.organizer = organizer
        self.event_date = event_date
        self.tickets_total = tickets_total
        self.tickets_sold = 0

    @property
    def tickets_available(self):
        return self.tickets_total - self.tickets_sold

    def is_upcoming(self):
        try:
            event_dt = datetime.strptime(self.event_date, "%Y-%m-%d")
            return event_dt >= datetime.now()
        except (ValueError, TypeError):
            return True

    def get_details(self):
        status = "SOLD OUT" if self.tickets_available <= 0 else f"{self.tickets_available} left"
        artists = " | ".join(self.lineup)
        return (f"** {self.title.upper()} **\n"
                f"Venue     : {self.location}\n"
                f"Date      : {self.event_date}\n"
                f"Price     : EUR {self.price:.2f}\n"
                f"Lineup    : {artists}\n"
                f"Agency    : {self.organizer}\n"
                f"Tickets   : {status}\n"
                f"{'-'*50}")
