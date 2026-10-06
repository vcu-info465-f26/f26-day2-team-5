"""Venue comparison chart for upcoming event records."""


def display_venue_chart(upcoming_records):
	"""Render counts by venue from the same records shown in the events table.

	Call this with the table's current upcoming records (after applying its
	location filter). Streamlit reruns on filter changes, so the chart stays
	synchronized with the table.
	"""
	import pandas as pd
	import streamlit as st

	if upcoming_records is None:
		records = pd.DataFrame()
	elif isinstance(upcoming_records, pd.DataFrame):
		records = upcoming_records.copy()
	else:
		records = pd.DataFrame(list(upcoming_records))

	st.subheader("Upcoming events by venue")
	st.caption("Compare the number of upcoming events available at each venue.")

	venue_column = next(
		(column for column in records.columns if str(column).casefold() in {"venue", "venue_name"}),
		None,
	)
	if records.empty or venue_column is None:
		st.info("No upcoming events to compare by venue.")
		return

	venues = (
		records[venue_column]
		.fillna("Unknown venue")
		.astype(str)
		.replace("", "Unknown venue")
		.value_counts()
		.rename_axis("Venue")
		.rename("Upcoming events")
		.reset_index()
	)
	st.bar_chart(
		venues,
		x="Venue",
		y="Upcoming events",
		x_label="Venue",
		y_label="Number of upcoming events",
		use_container_width=True,
	)