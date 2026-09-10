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