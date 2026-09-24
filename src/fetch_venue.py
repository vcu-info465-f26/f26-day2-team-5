import requests
import os
import json

# Function that gets venue data from Ticketmaster
def get_venue():

    # Venue ID taken from an event returned by Endpoint A
    venue_id = "KovZ917Atbr"

    # Ticketmaster Venue Details endpoint
    url = f"https://app.ticketmaster.com/discovery/v2/venues/{venue_id}.json"

    # Parameters sent with the API request
    params = {
        # Reads the Ticketmaster API key from the environment
        "apikey": os.getenv("TICKETMASTER_API_KEY")
    }

    # Sends a GET request to Ticketmaster
    response = requests.get(url, params=params, timeout=10)

    # Converts the JSON response into a Python dictionary
    data = response.json()

    # Saves the response to the data folder
    with open("data/venues_snapshot.json", "w") as f:
        json.dump(data, f, indent=4)

    # Shows the top-level keys in the response
    print(data.keys())

    # Prints the full response so we can inspect the data
    print(data)

    # Returns the venue data
    return data


# Runs the function
get_venue()