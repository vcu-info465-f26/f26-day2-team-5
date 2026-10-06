import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


# Find project.db from the root of the repository.
DB_PATH = Path(__file__).parent / "project.db"


def load_events():
    """Load event and venue information from project.db."""

    if not DB_PATH.exists():
        return None

    connection = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            e.event_name,
            e.event_date,
            v.venue_name,
            v.city,
            v.state
        FROM events AS e
        JOIN venues AS v
            ON e.venue_id = v.venue_id
        ORDER BY e.event_date, e.event_name
    """

    try:
        events = pd.read_sql_query(query, connection)
    except (sqlite3.Error, pd.errors.DatabaseError):
        connection.close()
        return None

    connection.close()

    if events.empty:
        return events

    events["event_date"] = pd.to_datetime(
        events["event_date"],
        errors="coerce"
    )

    events = events.sort_values(
        by=["event_date", "event_name"]
    )

    events["event_date"] = events["event_date"].dt.strftime("%Y-%m-%d")

    return events


st.title("Ticketmaster Event Dashboard")

events = load_events()

if events is None:
    st.error(
        "project.db could not be loaded. "
        "Run `python src/build_db.py` to build the database."
    )

elif events.empty:
    st.warning(
        "The database does not contain any event records."
    )

else:
    st.subheader("Upcoming Events")
    location_labels = (
        events["city"].fillna("Unknown")
        + ", "
        + events["state"].fillna("Unknown")
    )

    location_options = ["All locations"] + sorted(
        location_labels.unique().tolist()
    )

    selected_location = st.selectbox(
        "Filter by location",
        location_options
    )

    if selected_location != "All locations":
        events = events[location_labels == selected_location]

    st.metric(
        "Events in Database",
        len(events)
    )

    st.dataframe(
        events,
        use_container_width=True,
        hide_index=True
    )