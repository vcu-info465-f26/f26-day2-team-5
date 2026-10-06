"""
Plot upcoming events over time (issue #43).

Counts how many upcoming events are scheduled on each date, using the
data in project.db. Can be narrowed to one city. The dashboard (#41) will
call these functions; you can also run this file by itself to test it.
"""

import os
import sqlite3
from datetime import date

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator

DB_PATH = "project.db"

# Text the dashboard should show under the chart (last checkbox on #43).
NOTE = (
    "This chart shows how many events are scheduled on each upcoming date "
    "in our saved data snapshot. It is not a history of when events were "
    "collected, because we only have one snapshot."
)


def load_events(db_path=DB_PATH):
    """Read every event along with its venue's city and state."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(
            f"{db_path} not found. Run build_db.py first to create it."
        )

    # LEFT JOIN keeps events even if their venue isn't in the venues table.
    query = """
        SELECT e.event_id, e.event_date, v.city, v.state
        FROM events AS e
        LEFT JOIN venues AS v ON e.venue_id = v.venue_id
    """
    conn = sqlite3.connect(db_path)
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


def count_upcoming_by_date(events, city=None, today=None):
    """
    Return the number of events on each date from today onward,
    sorted in date order. Invalid or missing dates are skipped.
    """
    if today is None:
        today = pd.Timestamp(date.today())

    events = events.copy()

    # Keep only the YYYY-MM-DD part, turn it into a real date,
    # and mark anything that isn't a valid date as missing.
    events["event_date"] = pd.to_datetime(
        events["event_date"].astype(str).str[:10],
        format="%Y-%m-%d",
        errors="coerce",
    )
    events = events.dropna(subset=["event_date"])

    # Upcoming only: today or later.
    events = events[events["event_date"] >= today]

    # Optional location filter.
    if city:
        events = events[events["city"] == city]

    counts = events.groupby("event_date").size().sort_index()
    counts.name = "event_count"
    return counts


def plot_upcoming(counts):
    """Draw a bar chart of event counts by date. Empty data gives an empty chart."""
    fig, ax = plt.subplots(figsize=(10, 4))

    if counts.empty:
        ax.text(
            0.5, 0.5, "No upcoming events to show",
            ha="center", va="center", transform=ax.transAxes,
        )
        ax.set_xticks([])
        ax.set_yticks([])
    else:
        ax.bar(counts.index, counts.values, width=0.8)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        fig.autofmt_xdate()

    ax.set_title("Upcoming events by scheduled date")
    ax.set_xlabel("Scheduled date")
    ax.set_ylabel("Number of events")
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    events = load_events()

    counts = count_upcoming_by_date(events)
    print(counts)
    print(f"Total upcoming events: {counts.sum()}")
    plot_upcoming(counts).savefig("upcoming_events.png")
    print("Saved upcoming_events.png (do NOT commit this file)")

    # Test the empty case: a city that doesn't exist should give an empty chart, not a crash.
    empty = count_upcoming_by_date(events, city="NoSuchCity")
    plot_upcoming(empty).savefig("upcoming_events_empty.png")
    print("Saved upcoming_events_empty.png (do NOT commit this file)")