"""
Build one SQLite database containing both Ticketmaster tables.

The venues and events tables connect through venue_id.
"""

import os
import sqlite3

from build_venue_db import create_venues_table, load_venues
from build_events_db import create_events_table, load_events


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "project.db")


def main():
    # Rebuild the database from scratch each time.
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create and load both related tables.
    create_venues_table(cur)
    load_venues(cur)

    create_events_table(cur)
    load_events(cur)

    conn.commit()

    # Check how many events match a venue through venue_id.
    joined_rows = cur.execute(
        """
        SELECT COUNT(*)
        FROM events
        JOIN venues
          ON events.venue_id = venues.venue_id
        """
    ).fetchone()[0]

    print(f"joined event and venue rows: {joined_rows}")

    conn.close()


if __name__ == "__main__":
    main()