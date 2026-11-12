"""
Build the saved event database and create a short Groq summary.
"""

import os
import sqlite3
import tempfile
from datetime import date

from openai import OpenAI

# Support both direct execution and importing as a module.
if __package__:
    from . import build_db
    from .ai_config import MODEL
else:
    import build_db
    from ai_config import MODEL


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUMMARY_PATH = os.path.join(ROOT, "data", "summary.md")


def get_statistics():
    # Open the database created from the saved JSON files.
    with sqlite3.connect(build_db.DB_PATH) as conn:
        cur = conn.cursor()

                # Match the dashboard's All locations view.
        event_count, venue_count, first_date, last_date = cur.execute(
            """
            SELECT
                COUNT(*),
                COUNT(DISTINCT v.venue_id),
                MIN(NULLIF(e.event_date, '')),
                MAX(NULLIF(e.event_date, ''))
            FROM events AS e
            JOIN venues AS v ON e.venue_id = v.venue_id
            """
        ).fetchone()

        # Count events by city and state using matching venue records.
        top_cities = cur.execute(
            """
            SELECT venues.city, venues.state, COUNT(*) AS event_count
            FROM events
            JOIN venues ON events.venue_id = venues.venue_id
            WHERE venues.city IS NOT NULL AND TRIM(venues.city) != ''
            GROUP BY venues.city, venues.state
            ORDER BY event_count DESC, venues.city, venues.state
            LIMIT 5
            """
        ).fetchall()

    return event_count, venue_count, first_date, last_date, top_cities


def save_summary(content):
    # Write to a temporary file first so an unsuccessful write does not
    # replace an existing summary with an incomplete file.
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=os.path.dirname(SUMMARY_PATH),
            delete=False,
        ) as temp_file:
            temp_path = temp_file.name
            temp_file.write(content)

        os.replace(temp_path, SUMMARY_PATH)

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def main():
    # Make sure the Groq key is available before doing any work.
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise SystemExit(
            "GROQ_API_KEY is missing. Check your Codespaces secret."
        )

    # Rebuild project.db from the committed JSON snapshots.
    build_db.main()

    # Calculate the facts that will be sent to Groq.
    event_count, venue_count, first_date, last_date, top_cities = (
        get_statistics()
    )

    if event_count == 0:
        raise SystemExit("No events were found. The summary was not changed.")

    if not first_date or not last_date:
        raise SystemExit(
            "No event date range was found. The summary was not changed."
        )

    if top_cities:
        city_lines = []
        for city, state, count in top_cities:
            location = f"{city}, {state}" if state else city
            city_lines.append(f"- {location}: {count} events")

        city_text = "\n".join(city_lines)
    else:
        city_text = "No city information is available."

    # Print the facts so they can be checked against the database.
    facts = (
        f"Event count: {event_count}\n"
        f"Venue count: {venue_count}\n"
        f"Event date range: {first_date} to {last_date}\n"
        f"Cities with the most events:\n{city_text}"
    )

    print("\nDashboard Statistics:")
    print(facts)

    # Connect to Groq using the same model as the rest of the project.
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Write one short sentence identifying the city or cities "
                        "with the most events. Use only the supplied city rankings. "
                        "Mention at most two cities. Use plain text and leave out "
                        "counts, dates, headings, and bullets."
                    ),
                },
                {
                    "role": "user",
                    "content": city_text,
                },
            ],
        )

        summary = response.choices[0].message.content

        if not summary or not summary.strip():
            raise ValueError("Groq returned an empty summary.")

    except Exception as error:
        raise SystemExit(
            f"Could not create summary: {error}\n"
            "The existing summary was not changed."
        )

    # Add the source date range separately so it is always present.
    start = date.fromisoformat(first_date).strftime("%B %d, %Y")
    end = date.fromisoformat(last_date).strftime("%B %d, %Y")

    content = (
        "## Event Overview\n\n"
        f"Across all locations, the dashboard shows {event_count} events "
        f"at {venue_count} venues, with dates ranging from {start} to {end}. "
        f"{summary.strip()}\n\n"
        f"*Generated {date.today().isoformat()}.*\n"
    )

    save_summary(content)
    print(f"\nSummary saved to {SUMMARY_PATH}")


if __name__ == "__main__":
    main()