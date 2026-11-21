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
	import numpy as np
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
	st.caption("Bar colors rank venues from least used (red) to most used (green).")

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
	positions = np.linspace(0, 1, len(values))
	color_gradient = LinearSegmentedColormap.from_list(
		"venue_event_rank", ["#d73027", "#fee08b", "#1a9850"]
	)

	fig, ax = plt.subplots(figsize=(10, 4))
	ax.bar(
		venues["Venue"],
		values,
		color=color_gradient(positions),
		width=0.82,
		edgecolor="#202124",
		linewidth=0.6,
	)
	ax.set_xlabel("Venue")
	ax.set_ylabel("Number of upcoming events")
	ax.yaxis.set_major_locator(MaxNLocator(integer=True))
	ax.tick_params(axis="x", labelrotation=45)
	for label in ax.get_xticklabels():
		label.set_ha("right")
	color_scale = ScalarMappable(
		norm=Normalize(vmin=0, vmax=max(len(values) - 1, 1)),
		cmap=color_gradient,
	)
	colorbar = fig.colorbar(color_scale, ax=ax)
	colorbar.set_ticks([0, max(len(values) - 1, 1)])
	colorbar.set_ticklabels(["Least used", "Most used"])
	colorbar.set_label("Venue usage rank")
	fig.tight_layout()
	st.pyplot(fig, use_container_width=True)
	plt.close(fig)
