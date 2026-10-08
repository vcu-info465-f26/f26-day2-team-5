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

## Verify the Database

Run:

python src/query_events.py

Confirm that the script displays event records without errors.

## Start the Dashboard

Run:

streamlit run app.py

In Codespaces, open the forwarded dashboard port when prompted.

Choose a location to update the table and both charts.

## Public Dashboard

The public URL will be added after deployment from main.