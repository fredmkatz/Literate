from ai_apis.class_ai_openai import LDMReviewSession, estimate_cost
from ai_apis.class_ai_keys import FMK_OPENAI_KEY

# Step 1: Create session
session = LDMReviewSession(api_key=FMK_OPENAI_KEY)


# Step 1: Upload files (once)
# session.upload_file("Literate_sample.json", "model")
# session.upload_file("ResponseInstructions.txt", "instructions")

session.upload_if_needed("Literate_sample.json", "model")
session.upload_if_needed("ResponseInstructions.txt", "instructions")

# Step 2: Create assistant and thread (once)
session.create_assistant()
session.create_thread()

# Step 3: Submit user request
session.submit_prompt()

# Step 4: Run and print response
_, usage = session.run()
if usage:
    cost = estimate_cost(usage)
    print(f"Cost estimate (gpt-4o): {cost}")
    print(f"  Prompt tokens:     {usage.prompt_tokens}")
    print(f"  Completion tokens: {usage.completion_tokens}")
    print(f"  Total tokens:      {usage.total_tokens}")
    # You could multiply by rate here (see below)
print(session.get_response())
