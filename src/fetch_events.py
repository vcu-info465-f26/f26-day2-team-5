import requests
import os

# Function that gets event data from Ticketmaster
def get_events():

    # Ticketmaster Events endpoint
    url = "https://app.ticketmaster.com/discovery/v2/events.json"

    # Parameters sent with the API request
    params = {
        # Reads the Ticketmaster API key from the environment
        "apikey": os.getenv("TICKETMASTER_API_KEY"),

        # Limits results to events in the United States
        "countryCode": "US",

        # Limits the response to 5 events
        "size": 5
    }

    # Sends a GET request to Ticketmaster
    response = requests.get(url, params=params)

    # Converts the JSON response into a Python dictionary
    data = response.json()

    # Shows the top-level keys in the response
    print(data.keys())

    # Prints the full response so we can inspect the returned data
    print(data)

    # Returns the event data
    return data


# Runs the function when the file is executed
get_events()