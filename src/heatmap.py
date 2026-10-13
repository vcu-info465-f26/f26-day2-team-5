"""
U.S. heatmap of events by venue location (issue #52).

Takes the same filtered events dataframe the dashboard table uses,
counts events at each venue location, and draws a heatmap with pydeck.
"""

import pandas as pd
import pydeck as pdk
import streamlit as st

CAPTION = (
    "This map uses our saved Ticketmaster event snapshot. "
    "Brighter areas have more events."
)

# Starting view: centered on the continental United States.
US_VIEW = pdk.ViewState(latitude=39.5, longitude=-98.35, zoom=3)


def count_events_by_location(events):
    """
    Count events at each location that has valid coordinates.
    Returns the counts and how many events were skipped for missing coordinates.
    """
    located = events.copy()
    located["latitude"] = pd.to_numeric(located["latitude"], errors="coerce")
    located["longitude"] = pd.to_numeric(located["longitude"], errors="coerce")

    total = len(located)
    located = located.dropna(subset=["latitude", "longitude"])
    skipped = total - len(located)

    counts = (
        located.groupby(["venue_name", "city", "state", "latitude", "longitude"], dropna=False)
        .size()
        .reset_index(name="event_count")
        .sort_values("event_count", ascending=False)
    )
    return counts, skipped


def display_event_heatmap(events):
    """Show the heatmap, a city/state/count table, and a caption."""
    st.subheader("Where events are concentrated")

    if events.empty:
        st.info("No events match this filter, so there is nothing to map.")
        return

    counts, skipped = count_events_by_location(events)

    if counts.empty:
        st.info("None of these events have map coordinates, so the map can't be drawn.")
        return

    layer = pdk.Layer(
        "HeatmapLayer",
        data=counts,
        get_position="[longitude, latitude]",
        get_weight="event_count",
        radius_pixels=60,
    )

    st.pydeck_chart(
        pdk.Deck(map_style=None, initial_view_state=US_VIEW, layers=[layer])
    )

    if skipped:
        st.caption(f"{skipped} event(s) had no coordinates and are not shown on the map.")

    st.dataframe(
        counts[["venue_name", "city", "state", "event_count"]],
        use_container_width=True,
        hide_index=True,
    )

    st.caption(CAPTION)