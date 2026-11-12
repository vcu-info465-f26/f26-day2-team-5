# Ticketmaster API Project

# Sprint 1

## API Choice

Our team selected the Ticketmaster Discovery API.

Ticketmaster meets the project requirements because it provides API access with a free default quota, uses a simple API key for authentication, does not require OAuth, provides stable public event data, returns manageable JSON responses, and provides related resources such as events and venues. Ticketmaster's default quota is 5,000 API calls per day. 

## Selected Endpoints

Endpoint A: Ticketmaster Events  
`/discovery/v2/events.json`

Endpoint B: Ticketmaster Venue Details  
`/discovery/v2/venues/{venue_id}.json`

## Endpoint Connection

Both endpoints use the Ticketmaster venue ID, allowing events to be matched with the venue where they occur.

# Sprint 2: Event Dashboard

## Dashboard Overview

The dashboard displays upcoming Ticketmaster events from our saved
data snapshot. Visitors can filter by location and compare event
counts by venue and scheduled date.

The dashboard uses saved data, not live Ticketmaster availability.

## Installation

From the repository root, install the required packages:

pip install -r requirements.txt

## Build the Database

Run these commands from the repository root, in order:

python src/load_venues.py
python src/load_events.py
python src/build_db.py

These commands use the committed JSON snapshots in data/.
No Ticketmaster API key is required to build the database.

The generated project.db file is excluded from Git by the
existing *.db rule in .gitignore.

The dashboard automatically creates project.db from the committed JSON
snapshots in data/ when the database is missing. No Ticketmaster API key
or manual database setup is required to start the dashboard.

To rebuild the database manually, run:

```bash
python src/build_db.py
```

The generated project.db remains excluded from Git by the existing
*.db rule in .gitignore.

## Verify the Database

Run:

python src/query_events.py

Confirm that the script displays event records without errors.

## Start the Dashboard

Run:

streamlit run app.py

In Codespaces, open the forwarded dashboard port when prompted.

Choose a location to update the table and both charts.

# Sprint 3: AI Summary and Chat

## Event Overview

The dashboard displays a short overview of the saved Ticketmaster event data.
It includes the event count, venue count, event date range, and where events
are concentrated. The overview covers all locations, even when a visitor
filters the table and charts to one city.

The summary script builds the database from the saved JSON snapshots and
calculates statistics in SQLite. It uses Groq to help write the overview and
saves the result and its generation date in `data/summary.md`. Streamlit reads
that file when displaying the overview.

To regenerate the summary from the repository root, configure `GROQ_API_KEY`
in Codespaces and run:

```bash
python src/summarize.py
```

## Dashboard Chat

Use **Ask about these events** to ask questions about the events currently
shown in the dashboard. For example, select a city and ask, “Which venue has
the most events?”

The chatbot sends Groq a compact summary of the currently filtered data and
includes recent messages so visitors can ask follow-up questions. It can
answer questions about event counts, venues, locations, and dates. Ticket
prices and attendance are outside the saved dataset, and detailed questions
about individual events may be limited by the rows included in the chat
context. If the model call fails, the app displays an unavailable message.

The summary and chat share the `openai/gpt-oss-120b` model configured in
`src/ai_config.py`.

## Daily Data and Summary Refresh

The **Daily data and summary refresh** workflow is scheduled for 12:00 UTC
every day and can also be started manually from GitHub Actions. It fetches
updated Ticketmaster event and venue snapshots, runs the summary script, and
pushes changed data files to `main`.

If summary generation fails, the workflow keeps the previous `data/summary.md`
and still attempts to push any updated snapshots. The dashboard can therefore
show newer event data alongside an older overview. Check the overview’s
generation date to see when it was last written.

## Required Secrets

| Environment | Secret names | Used for |
| --- | --- | --- |
| GitHub Codespaces | `GROQ_API_KEY` | Regenerating the summary and testing chat locally |
| Streamlit Community Cloud | `GROQ_API_KEY` | Chat on the public dashboard |
| GitHub Actions | `TICKETMASTER_API_KEY`, `GROQ_API_KEY` | Fetching snapshots and generating the scheduled summary |

The saved overview can be displayed without a Groq key. Store API keys in the
appropriate secrets settings and keep their values out of the repository.

## Public Dashboard

Public URL: https://f26team5.streamlit.app

The public dashboard runs from the main branch.