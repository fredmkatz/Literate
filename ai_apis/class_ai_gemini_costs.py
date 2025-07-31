import google.generativeai as genai
from google.generativeai import types

# Assuming you've already configured your API key and cached content as before
genai.configure(api_key="YOUR_GEMINI_API_KEY")
MODEL_NAME = "gemini-1.5-pro-latest"

# ... (define model_schema_cache_name, review_instructions_cache_name, reporting_schema from previous example) ...

def review_data_model_with_usage(data_model_content: str, specific_aspects: str = "all aspects"):
    client = genai.GenerativeModel(MODEL_NAME)

    contents = [
        {"text": "You are an expert data modeling assistant."},
        {"text": f"Your task is to review the provided data model (or fragment) for {specific_aspects}."},
        {"text": "Refer to the pre-loaded data modeling language schema and detailed review guidelines."},
        {"text": "Data Modeling Language Schema: (Referenced via cache)"},
        {"text": "Detailed Review Guidelines: (Referenced via cache)"},
        {"text": "Please provide suggested changes in the following JSON format:"},
        {"text": "Data Model (or fragment) to Review:\n" + data_model_content}
    ]

    try:
        response = client.generate_content(
            contents=contents,
            generation_config=types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=reporting_schema,
                cached_content=[
                    model_schema_cache_name,
                    review_instructions_cache_name
                ]
            )
        )

        # Accessing usage metadata
        usage = response.usage_metadata
        print(f"\n--- Token Usage for this request ---")
        print(f"Prompt Tokens: {usage.prompt_token_count}")
        print(f"Candidate (Output) Tokens: {usage.candidates_token_count}")
        print(f"Total Tokens: {usage.total_token_count}")
        if hasattr(usage, 'cached_content_token_count'):
            print(f"Cached Content Tokens: {usage.cached_content_token_count}")

        return response.text, usage

    except Exception as e:
        print(f"Error during model review: {e}")
        return None, None

# Example Usage:
if __name__ == "__main__":
    example_data_model = """
    {
      "classes": [
        {
          "name": "User",
          "description": "Represents a user account in the system.",
          "attributes": [
            {"name": "userName", "type": "string", "description": "User's unique identifier."},
            {"name": "email", "type": "string", "description": "User's email address.", "mandatory": true},
            {"name": "creationDate", "type": "date", "description": "Date of account creation."}
          ]
        }
      ]
    }
    """

    results, usage_info = review_data_model_with_usage(example_data_model, "completeness and styling")

    if results:
        print("\nReview Results (JSON):")
        print(results)
    else:
        print("\nFailed to get review results.")