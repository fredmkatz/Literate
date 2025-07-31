import os
from ai_apis.class_ai_keys import FMK_Gemini_Key

print("Trying gemini")
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(
    api_key=FMK_Gemini_Key, base_url="https://generativelanguage.googleapis.com/v1beta/"
)
# Make a chat completion request
response = client.chat.completions.create(
    model="gemini-1.5-flash",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain how AI works in simple terms."},
    ],
)
# Print the response
print(response.choices[0].message.content)
