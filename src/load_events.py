import glob
import json
import os
import sqlite3

# Paths are built from this file's location, so the script works
# no matter which folder you run it from.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
DB_PATH = os.path.join(ROOT, "project.db")


def extract_events(data):
    """Handle the different shapes Ticketmaster event data can come in."""
    if isinstance(data, list):          # a plain list of events
        return data
    if "_embedded" in data:             # a search response (/events.json)
        return data["_embedded"].get("events", [])
    if "id" in data:                    # a single event (/events/{id}.json)
        return [data]
    return []


def create_events_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id   TEXT PRIMARY KEY,
            event_name TEXT,
            event_date TEXT,
            venue_id   TEXT
        )
    """)


def load_events(cur):
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*event*.json")))

    if not files:
        print("WARNING: no event files found in data/")
        return

    for path in files:
        with open(path) as f:
            data = json.load(f)

        for event in extract_events(data):
            if not event.get("id"):
                continue

            dates = event.get("dates", {})
            start = dates.get("start", {})

            venue_id = None

            embedded = event.get("_embedded", {})
            venues = embedded.get("venues", [])

            if venues:
                venue_id = venues[0].get("id")

            cur.execute(
                """INSERT OR REPLACE INTO events
                   (event_id, event_name, event_date, venue_id)
                   VALUES (?, ?, ?, ?)""",
                (
                    event["id"],
                    event.get("name"),
                    start.get("localDate"),
                    venue_id,
                ),
            )

    count = cur.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    print(f"events: {count} rows loaded from {len(files)} file(s)")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    create_events_table(cur)
    load_events(cur)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()