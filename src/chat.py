"""
Chat about the selected dashboard data (issue #62).

The dashboard passes in the currently filtered events. This module
calculates a short summary of those events and sends it to Groq along
with the last few chat messages, so answers always match the filter.
Uses the same model and client setup as summarize.py.
"""

import os

import pandas as pd
import streamlit as st
from openai import OpenAI, OpenAIError

from src.ai_config import MODEL

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MAX_HISTORY = 6   # how many recent messages are sent with each question
TOP_N = 10        # how many venues/locations to list in the summary
MAX_ROWS = 25     # how many individual events to include in the summary

SYSTEM_PROMPT = (
    "You answer questions about Ticketmaster events shown on a dashboard. "
    "Use only the data summary below. If the answer is not in the summary "
    "(for example ticket prices, which this data does not include), say that "
    "the data does not contain that information. Keep answers short. "
    "The summary always reflects the user's current filter. If earlier "
    "messages mention different numbers, trust this summary."
)

UNAVAILABLE = "The chat assistant is unavailable right now. Please try again later."


def get_api_key():
    """Read the Groq key from Streamlit secrets (deployed) or the environment (Codespace)."""
    try:
        key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        key = None
    return key or os.environ.get("GROQ_API_KEY")


def build_context(events, location):
    """Turn the filtered events into a compact text summary for Groq."""
    lines = [f"Location filter: {location}", f"Total events: {len(events)}"]

    if events.empty:
        lines.append("No events match this filter.")
        return "\n".join(lines)

    if "venue_name" in events.columns:
        venues = events["venue_name"].fillna("Unknown").value_counts().head(TOP_N)
        lines.append("Events per venue (most first):")
        lines += [f"- {name}: {count}" for name, count in venues.items()]

    if "city" in events.columns and "state" in events.columns:
        places = (
            events["city"].fillna("Unknown") + ", " + events["state"].fillna("Unknown")
        ).value_counts().head(TOP_N)
        lines.append("Events per location (most first):")
        lines += [f"- {place}: {count}" for place, count in places.items()]

    if "event_date" in events.columns:
        dates = pd.to_datetime(events["event_date"], errors="coerce").dropna()
        if not dates.empty:
            lines.append(f"Date range: {dates.min():%Y-%m-%d} to {dates.max():%Y-%m-%d}")
            busiest = dates.dt.date.value_counts()
            lines.append(f"Busiest date: {busiest.index[0]} with {busiest.iloc[0]} events")

    columns = [c for c in ["event_name", "event_date", "venue_name", "city", "state"] if c in events.columns]
    if columns:
        lines.append(f"Events (first {min(MAX_ROWS, len(events))} of {len(events)}):")
        for _, row in events[columns].head(MAX_ROWS).iterrows():
            lines.append("- " + " | ".join(str(row[c]) for c in columns))

    lines.append("Data does not include ticket prices or attendance.")
    return "\n".join(lines)


def ask_groq(messages):
    """Send messages to Groq. Returns the reply text, or None if anything fails."""
    key = get_api_key()
    if not key:
        return None
    try:
        client = OpenAI(api_key=key, base_url=GROQ_BASE_URL, timeout=30)
        response = client.chat.completions.create(model=MODEL, messages=messages)
        return response.choices[0].message.content
    except (OpenAIError, IndexError, AttributeError):
        return None


def display_chat(events, location):
    """Show the chat box and conversation history on the dashboard."""
    st.subheader("Ask about these events")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a question about the selected events")
    if not question:
        return

    st.session_state.chat_history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    system = {
        "role": "system",
        "content": SYSTEM_PROMPT + "\n\n" + build_context(events, location),
    }
    recent = st.session_state.chat_history[-MAX_HISTORY:]

    with st.spinner("Thinking..."):
        answer = ask_groq([system] + recent)

    if answer is None:
        answer = UNAVAILABLE

    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)