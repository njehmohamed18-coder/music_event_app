# event_manager/models.py

class User:
    """Base class demonstrating encapsulation and attributes."""
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def display_info(self):
        print(f"User: {self.username} | Email: {self.email}")

class Organizer(User):
    """Inherits from User. Represents the person posting events."""
    def __init__(self, username, email, company_name):
        super().__init__(username, email) # Use super() to call parent constructor
        self.company_name = company_name
        self.hosted_events = []

    def create_event(self, title, location, price, lineup):
        event = MusicEvent(title, location, price, lineup, self.company_name)
        self.hosted_events.append(event)
        return event

class MusicEvent:
    """Class to represent the music event details."""
    def __init__(self, title, location, price, lineup, organizer):
        self.title = title
        self.location = location
        self.price = price
        self.lineup = lineup # List of artists
        self.organizer = organizer

    def get_details(self):
        return f"{self.title} @ {self.location} | Price: {self.price}€ | Lineup: {', '.join(self.lineup)}"