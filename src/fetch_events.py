import requests
import os
import json
import time


# Get up to 100 events with unique names from Ticketmaster.
def get_events():

    url = "https://app.ticketmaster.com/discovery/v2/events.json"

    # Read the API key from the environment.
    api_key = os.getenv("TICKETMASTER_API_KEY")

    if not api_key:
        print("Set TICKETMASTER_API_KEY before running this script.")
        return []

    params = {
        "apikey": api_key,
        "countryCode": "US",
        "size": 100,
        "page": 0
    }

    unique_events = []
    event_names = set()

    # Check up to 10 pages, staying within the API's paging limit.
    while len(unique_events) < 100 and params["page"] < 10:

        # Request the current page without waiting indefinitely.
        try:
            response = requests.get(url, params=params, timeout=10)
        except requests.RequestException:
            print("Request failed. The existing snapshot was not changed.")
            return []

        if response.status_code != 200:
            print(f"API request failed: HTTP {response.status_code}")
            return []

        data = response.json()
        events = data.get("_embedded", {}).get("events", [])

        # Stop if there are no more events.
        if not events:
            break

        # Keep only the first event with each name.
        for event in events:
            name = event["name"]

            if name not in event_names:
                unique_events.append(event)
                event_names.add(name)

            if len(unique_events) == 100:
                break

        # Stop if we have reached the last available page.
        total_pages = data.get("page", {}).get("totalPages", 0)

        if params["page"] + 1 >= total_pages:
            break

        # Move to the next page and pause between requests.
        params["page"] += 1
        time.sleep(0.25)

    if not unique_events:
        print("No events returned. The existing snapshot was not changed.")
        return []

    # Save the collected events in the existing snapshot format.
    os.makedirs("data", exist_ok=True)

    with open("data/events_snapshot.json", "w") as file:
        json.dump(unique_events, file, indent=4)

    print(f"Saved {len(unique_events)} unique events")

    if len(unique_events) < 100:
        print("Reached the available results or paging limit before finding 100.")

    return unique_events


# Run the function when this file is executed directly.
if __name__ == "__main__":
    get_events()