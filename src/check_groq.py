import os
from openai import OpenAI

# Allow this file to work as a module or a directly run script.
if __package__:
    from .ai_config import MODEL
else:
    from ai_config import MODEL


def main():
    # Read the key from the Codespace environment.
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise SystemExit("GROQ_API_KEY is missing. Check your Codespaces secret.")

    # Connect to Groq using the OpenAI Python package.
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
    )

    # Send a short request to confirm the connection works.
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": "Say hello in five words."}
        ],
        reasoning_effort="low",
    )

    # Display the answer without exposing the key.
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()