"""Venue comparison chart for upcoming event records."""


def display_venue_chart(upcoming_records):
	"""Render counts by venue from the same records shown in the events table.

	Call this with the table's current upcoming records (after applying its
	location filter). Streamlit reruns on filter changes, so the chart stays
	synchronized with the table.
	"""
	import matplotlib.pyplot as plt
	from matplotlib.colors import LinearSegmentedColormap, Normalize
	from matplotlib.cm import ScalarMappable
	from matplotlib.ticker import MaxNLocator
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
	st.caption("Bars progress from least to most used (red to green).")

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
		.sort_values(
			["Upcoming events", "Venue"],
			ascending=[True, True],
			kind="stable",
		)
		.reset_index(drop=True)
	)

	values = venues["Upcoming events"].to_numpy()
	value_range = values.max() - values.min()
	positions = (
		(values - values.min()) / value_range
		if value_range
		else values * 0 + 0.5
	)
	color_gradient = LinearSegmentedColormap.from_list(
		"venue_event_counts", ["#e53935", "#ffeb3b", "#43a047"]
	)

	fig, ax = plt.subplots(figsize=(10, 4))
	ax.bar(
		venues["Venue"],
		values,
		color=color_gradient(positions),
		width=0.8,
		edgecolor="#263238",
		linewidth=0.35,
	)
	ax.set_xlabel("Venue")
	ax.set_ylabel("Number of upcoming events")
	ax.yaxis.set_major_locator(MaxNLocator(integer=True))
	ax.tick_params(axis="x", labelrotation=45)
	for label in ax.get_xticklabels():
		label.set_ha("right")
	if value_range:
		color_scale = ScalarMappable(
			norm=Normalize(vmin=values.min(), vmax=values.max()),
			cmap=color_gradient,
		)
		fig.colorbar(color_scale, ax=ax, label="Upcoming events")
	fig.tight_layout()
	st.pyplot(fig, use_container_width=True)
	plt.close(fig)
