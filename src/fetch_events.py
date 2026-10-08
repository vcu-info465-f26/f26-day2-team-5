import requests
import os
import json

# Function that gets event data from Ticketmaster
def get_events():

    # Ticketmaster Events endpoint
    url = "https://app.ticketmaster.com/discovery/v2/events.json"

    # Parameters sent with the API request
    params = {
        "apikey": os.getenv("TICKETMASTER_API_KEY"),
        "countryCode": "US",
        "size": 100
    }

    # Sends a GET request to Ticketmaster
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"API request failed: HTTP {response.status_code}")
        return []

    data = response.json()
    events = data.get("_embedded", {}).get("events", [])

    if not events:
        print("No events returned. Check your API key and search parameters.")
        return []

    unique_events = []
    event_names = set()

    for event in events:
        name = event["name"]

        if name not in event_names:
            unique_events.append(event)
            event_names.add(name)

        if len(unique_events) == 250:
            break

        # Save up to 100 unique events
    with open("data/events_snapshot.json", "w") as file:
        json.dump(unique_events, file, indent=4)

    print(f"Saved {len(unique_events)} unique events")
    return unique_events


# Runs the function when the file is executed
get_events()