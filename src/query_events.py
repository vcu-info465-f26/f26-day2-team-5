import sqlite3

connection = sqlite3.connect("project.db")

query = """
SELECT e.event_name, e.event_date, v.venue_name, v.city, v.state
FROM events AS e
JOIN venues AS v ON e.venue_id = v.venue_id
WHERE date(e.event_date) >= date('now')
ORDER BY e.event_date, e.event_name
"""

events = connection.execute(query).fetchall()
connection.close()

print("Upcoming Events")

for name, date, venue, city, state in events:
    print(f"{date} | {name}")
    print(f"  {venue} — {city}, {state}")