import os
import anthropic
import json

# Replace with your actual API key
from ai_apis.class_ai_keys import FMK_Claude_Key


def make_request(client, request):
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            messages=[{"role": "user", "content": request}],
        )

        print(message.content[0].text)
        print(message)
        rkeys = ["id", "content", "model", "usage"]

        print("id", " => ", message.id)
        print("model", " => ", message.model)
        print("usage", " => ", message.usage)
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    api_key = FMK_Claude_Key

    client = anthropic.Anthropic(api_key=api_key)

    asks = [
        "Show me n factiorial for n in 1..5. Respond with just a json object, please"
    ]

    for k in range(1, 20):
        for req in asks:
            make_request(client, req)


if __name__ == "__main__":
    main()
