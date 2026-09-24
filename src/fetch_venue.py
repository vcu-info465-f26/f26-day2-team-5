import requests
import os
import json

# Function that gets venue data from Ticketmaster
def get_venues():

    with open("data/events_snapshot.json", "r") as file:
        data = json.load(file)

    # Handles both the old Ticketmaster response and the new event list
    if isinstance(data, dict):
        events = data.get("_embedded", {}).get("events", [])
    else:
        events = data

    venue_ids = set()

    for event in events:
        venues = event.get("_embedded", {}).get("venues", [])

        if venues:
            venue_ids.add(venues[0]["id"])

    venue_data = []

    for venue_id in venue_ids:

        url = f"https://app.ticketmaster.com/discovery/v2/venues/{venue_id}.json"

        params = {
            "apikey": os.getenv("TICKETMASTER_API_KEY")
        }

        response = requests.get(url, params=params, timeout=10)

        venue_data.append(response.json())

    with open("data/venues_snapshot.json", "w") as file:
        json.dump(venue_data, file, indent=4)

    print(f"Saved {len(venue_data)} unique venues")

    return venue_data


get_venues()