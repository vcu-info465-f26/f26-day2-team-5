import re
import sqlite3
from pathlib import Path
from src.venue_compare import display_venue_chart
from src.heatmap import display_event_heatmap
from src.chat import display_chat
from src.build_db import main as build_database
from src.snapshot_fingerprint import snapshot_fingerprint
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Ticketmaster Dashboard",
    layout="wide"
)

# Find project.db from the root of the repository.
DB_PATH = Path(__file__).parent / "project.db"
SUMMARY_PATH = Path(__file__).parent / "data" / "summary.md"


def display_saved_summary():
    """Display the summary for the full saved dataset."""
    try:
        summary = SUMMARY_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        st.info("The saved event summary is not available yet.")
        return

    marker = re.match(
        r"<!-- snapshot-fingerprint: ([0-9a-f]{64}) -->\n\n", 
        summary
    )
    is_outdated = False

    if marker:
        summary = summary[marker.end():]
        try:
            is_outdated = marker.group(1) != snapshot_fingerprint()
        except OSError:
            # If a snapshot is unavailable, we can't verify freshness.
            pass

    with st.container(border=True):
        st.markdown(summary)
        if is_outdated:
            st.warning("The event data has been updated since this summary was written.")


def load_events():
    """Load event and venue information from project.db."""

        # Create the database from the saved JSON files when it is missing.
    # Refresh the database using the committed JSON snapshots.
        # Rebuild when the database is missing or a snapshot has changed.
    snapshot_paths = [
        DB_PATH.parent / "data" / "events_snapshot.json",
        DB_PATH.parent / "data" / "venues_snapshot.json",
    ]

    if (
        not DB_PATH.exists()
        or any(
            snapshot.stat().st_mtime > DB_PATH.stat().st_mtime
            for snapshot in snapshot_paths
        )
    ):
        build_database()

    connection = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            e.event_name,
            e.event_date,
            v.venue_name,
            v.city,
               v.state,
               v.latitude,
               v.longitude        
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

@st.dialog("AI Event Chat", width="large")
def open_chat(events, location):
    # Chat uses the currently selected dashboard location.
    st.caption(f"Current filter: {location}")
    display_chat(events, location)

# Dashboard title and chat button.
title_col, chat_col = st.columns([5, 1])

with title_col:
    st.title("Ticketmaster Event Dashboard")

with chat_col:
    if st.button("Open Chat", use_container_width=True):
        st.session_state.open_chat = True

events = load_events()

if events is None:
    st.error("The event database could not be loaded.")

elif events.empty:
    st.warning("The database does not contain any events.")

else:
    # Location filter.
    location_labels = (
        events["city"].fillna("Unknown")
        + ", "
        + events["state"].fillna("Unknown")
    )

    locations = ["All locations"] + sorted(
        location_labels.unique().tolist()
    )

    selected_location = st.selectbox(
        "Filter by location",
        locations
    )

    if selected_location != "All locations":
        events = events[location_labels == selected_location]

    # Summary metrics.
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Events", len(events))

    with col2:
        st.metric("Venues", events["venue_name"].nunique())

    with col3:
        st.metric("Locations", len(
            events[["city", "state"]].drop_duplicates()
        ))

    # Brief summary stays near the top.
    st.subheader("Event Summary")

    with st.expander("View full AI-generated summary"):
        display_saved_summary()

    # Charts and event records no longer stack vertically.
    venue_tab, map_tab, data_tab = st.tabs([
        "Venue Chart",
        "Event Heatmap",
        "Event Data"
    ])

    with venue_tab:
        display_venue_chart(events)

    with map_tab:
        display_event_heatmap(events)

    with data_tab:
        st.dataframe(
            events,
            use_container_width=True,
            hide_index=True
        )

    # Open the chatbot without leaving the dashboard.
    if st.session_state.get("open_chat", False):
        st.session_state.open_chat = False
        open_chat(events, selected_location)