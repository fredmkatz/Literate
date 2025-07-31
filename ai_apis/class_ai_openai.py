import openai
import os
import json
import time

class LDMReviewSession:
    def __init__(self, api_key=None, docs_dir="trials/ai_docs", ids_file="ldm_ids.json"):
        self.client = openai.OpenAI(api_key=api_key)
        self.docs_dir = docs_dir
        self.cache_path = os.path.join(docs_dir, ids_file)
        self.ids = self._load_ids()

    def _load_ids(self):
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "r") as f:
                return json.load(f)
        else:
            return {}

    def _save_ids(self):
        os.makedirs(self.docs_dir, exist_ok=True)
        with open(self.cache_path, "w") as f:
            json.dump(self.ids, f, indent=2)

    def upload_file(self, filename, label):
        path = os.path.join(self.docs_dir, filename)
        file = self.client.files.create(file=open(path, "rb"), purpose="assistants")
        self.ids[label] = file.id
        self._save_ids()
        print(f"Uploaded '{label}': {file.id}")
        return file.id

    def upload_if_needed(self, filename, label):
        path = os.path.join(self.docs_dir, filename)
        stat = os.stat(path)
        size = stat.st_size
        mtime = stat.st_mtime

        # Check if we already have a valid cached upload
        existing = self.ids.get(label)
        if (
            isinstance(existing, dict)
            and existing.get("filename") == filename
            and existing.get("size") == size
            and abs(existing.get("mtime", 0) - mtime) < 1  # allow slight diff
        ):
            print(f"Upload skipped: '{filename}' already uploaded.")
            return existing["file_id"]

        # Upload required
        file = self.client.files.create(file=open(path, "rb"), purpose="assistants")
        print(f"Uploaded '{filename}' as '{label}': {file.id}")

        self.ids[label] = {
            "file_id": file.id,
            "filename": filename,
            "size": size,
            "mtime": mtime
        }
        self._save_ids()
        return file.id

    def create_assistant(self, name="LDM Reviewer", model="gpt-4o"):
        assistant = self.client.beta.assistants.create(
            name=name,
            instructions="""You are an AI assistant that reviews Literate Data Models (LDMs).
Fix one-liners to be noun phrases.
Add missing Python expressions for constraints and derivations.
Return valid JSON output using the required format from the instructions file.""",
            model=model,
            tools=[{"type": "file_search"}]
        )
        self.ids["assistant_id"] = assistant.id
        self._save_ids()
        print(f"Created assistant: {assistant.id}")
        return assistant.id

    def create_thread(self):
        thread = self.client.beta.threads.create()
        self.ids["thread_id"] = thread.id
        self._save_ids()
        print(f"Created thread: {thread.id}")
        return thread.id

    def submit_prompt(self, prompt="Please review the attached model file and return valid JSON changes."):
        message = self.client.beta.threads.messages.create(
            thread_id=self.ids["thread_id"],
            role="user",
            content=prompt,
            attachments=[
                {
                    "file_id": self.ids["model"]["file_id"],

                    "tools": [{"type": "file_search"}]
                },
                {
                    "file_id": self.ids["instructions"]["file_id"],
                    "tools": [{"type": "file_search"}]
                }
            ]
        )
        print("Submitted prompt to thread.")
        return message

    def run(self):
        run = self.client.beta.threads.runs.create(
            thread_id=self.ids["thread_id"],
            assistant_id=self.ids["assistant_id"]
        )
        print("Running...")
        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=self.ids["thread_id"], run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status in ["failed", "cancelled", "expired"]:
                raise Exception(f"Run failed with status: {run_status.status}")
            time.sleep(1)
        
        print("Run completed.")

        usage = run_status.usage  # May contain prompt_tokens, completion_tokens, total_tokens
        if usage:
            print(f"Tokens used: {usage}")
        else:
            print("No token usage info returned.")

        return run.id, usage

    def get_response(self):
        messages = self.client.beta.threads.messages.list(thread_id=self.ids["thread_id"])
        for msg in messages.data:
            if msg.role == "assistant":
                return msg.content[0].text.value
        return None

def estimate_cost(usage):
    prompt_cost = usage.prompt_tokens * 0.005 / 1000
    completion_cost = usage.completion_tokens * 0.015 / 1000
    return round(prompt_cost + completion_cost, 6)
