import glob
import json
import os
import sqlite3

# Paths are built from this file's location, so the script works
# no matter which folder you run it from.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
DB_PATH = os.path.join(ROOT, "project.db")


def extract_venues(data):
    """Handle the different shapes Ticketmaster venue data can come in."""
    if isinstance(data, list):          # a plain list of venues
        return data
    if "_embedded" in data:             # a search response (/venues.json)
        return data["_embedded"].get("venues", [])
    if "id" in data:                    # a single venue (/venues/{id}.json)
        return [data]
    return []


def create_venues_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS venues (
            venue_id   TEXT PRIMARY KEY,
            venue_name TEXT,
            city       TEXT,
            state      TEXT
        )
    """)


def load_venues(cur):
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*venue*.json")))
    if not files:
        print("WARNING: no venue files found in data/")
        return

    for path in files:
        with open(path) as f:
            data = json.load(f)

        for v in extract_venues(data):
            if not v.get("id"):
                continue
            state = v.get("state", {})
            cur.execute(
                """INSERT OR REPLACE INTO venues (venue_id, venue_name, city, state)
                   VALUES (?, ?, ?, ?)""",
                (
                    v["id"],
                    v.get("name"),
                    v.get("city", {}).get("name"),
                    state.get("stateCode") or state.get("name"),
                ),
            )

    count = cur.execute("SELECT COUNT(*) FROM venues").fetchone()[0]
    print(f"venues: {count} rows loaded from {len(files)} file(s)")


def main():
    # Start fresh every time, so running twice never duplicates rows
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    create_venues_table(cur)
    load_venues(cur)

    # Events table (#30) goes here

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()