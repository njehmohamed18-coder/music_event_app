# Music Event Manager

A command-line application for managing music events, built with Python and SQLite.

## Features

- **Organisers** can create, edit, and delete events
- **Users** can browse events, search by artist, buy tickets, and cancel them
- Secure password hashing with bcrypt
- SQLite database with transactional ticket purchasing

## Setup

```bash
# Clone the repo
git clone https://github.com/pypa/mohamednjahsamplepackage
cd mohamednjahsamplepackage

# Install dependencies
pip install -r requirements.txt

# Run the app
python3 main.py
```

## Running Tests

```bash
pytest test_event_manager.py -v
```

## Project Structure

```
event_manager/
├── __init__.py      # Public API exports
├── database.py      # SQLite logic (users, events, tickets)
├── models.py        # MusicEvent, Organizer, Guest classes
main.py              # CLI entry point
test_event_manager.py
requirements.txt
setup.py
```

## License

MIT — see `license` file.
