#!/usr/bin/env python3
"""
Simplified LDM AI Assistant with JSON-only responses and conversation memory
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import utils.util_json_path_update as json_updater
import anthropic
from dataclasses import dataclass
from ai_apis.class_ai_claude_json_parser import handle_claude_api_call


class LDMAssistant:
    def __init__(self, api_key: str = None):
        """Initialize in Agent specific classes"""
        self.client = None
        self.model_name = None

        # Conversation state
        self.n_conversations = 0
        self.bytes_sent = 0
        self.reference_docs = None
        self.system_prompt = None

    def initialize_session(self, docs_dir: Path):
        """Set up the session with reference docs and initial model"""
        print("Initializing session...")

        # Load reference documents once
        self.reference_docs = self._load_reference_docs(docs_dir)

        # Create system prompt that will persist
        self.system_prompt = self._create_system_prompt()

        print(f"Session initialized with {len(self.reference_docs)} reference docs")

    def _load_reference_docs(self, docs_dir: Path) -> Dict[str, str]:
        """Load all reference documents"""
        docs = {}
        doc_files = [
            # "LiterateMetaModel_01_PD_schema.yaml",
            # "LDM AI Instructions - July, 2025.md",
            # "Literate_01.py",
            "ResponseInstructions.txt",
        ]
        total_size = 0
        for filename in doc_files:
            file_path = docs_dir / filename
            if file_path.exists():
                docs[filename] = file_path.read_text()
                size = len(docs[filename])
                print("Loading doc: ", filename, ". Length is ", size)
                total_size += size
        print(
            "Total size in bytes is: ",
            total_size,
            " = about ",
            total_size / 4,
            " tokens",
        )
        return docs

    def _create_system_prompt(self) -> str:
        """Create the persistent system prompt"""
        doc_context = "\n\n".join(
            [
                f"<document name='{name}'>\n{content}\n</document>"
                for name, content in self.reference_docs.items()
            ]
        )

        return f"""You are an AI assistant specialized in improving Literate Data Models (LDMs). 

## Reference Documents:
{doc_context}
"""

    def make_request(self, current_model, request: str) -> Dict[str, Any]:
        """Make a request to Claude with conversation memory"""

        if not self.reference_docs:
            raise ValueError(
                "Session not initialized. Call initialize_session() first."
            )

        # Create user message
        user_message = f"""Current model:
{json.dumps(current_model, indent=2)}

Request: {request}

Please respond with changes only in the specified JSON format."""

        try:
            print("Sending message with user_message = ")
            print(len(user_message), " bytes")
            print("... end of user message")
            full_response = self.handle_api_call(
                persistent_context=self.system_prompt, message=user_message
            )
            self.n_conversations += 1
            self.bytes_sent += len(self.system_prompt) + len(user_message)

            print("FULL RESPONSE IN JSON")
            # print(json.dumps(full_response, indent=2))
            print("END OF FULL RESPONSE")

            result = full_response.get("content_blocks", [{}])[0].get("parsed_json", {})
            print("RESULT FROM FIRST CONTENT BLOCK")
            # print(json.dumps(result, indent = 2))
            print("END OF RESULT FROM FIRST CONTENT BLOCK")

            # Update current model if full model was returned
            if result.get("response_type") == "changes":
                changes = result["changes"]
                print("\tand changes are")
                print(json.dumps(changes, indent=2))
            else:
                print("unrecognized response tyep: ", result.get("response_type"))
            stats = {
                "id": full_response.get("id", "??"),
                "model": full_response.get("model", "??"),
                "total_bytes_sent": self.bytes_sent,
                "sent_docs_size": len(self.system_prompt),
                "query_size": len(user_message),
                "usage": full_response.get("usage", "??"),
            }
            return (result, stats)

        except Exception as e:
            print(f"Error making request: {e}")
            raise

    def handle_api_call(self, persistent_context, message):
        return {}

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        return {
            "conversation_length": self.n_conversations,
            "reference_docs_loaded": list(self.reference_docs.keys()),
            "session_initialized": self.reference_docs is not None,
        }


class ClaudeLDMAssistant(LDMAssistant):
    def __init__(self, api_key: str = None):
        super().__init__(api_key)

        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        self.model_name = "claude-3-5-sonnet-20241022"

    def handle_api_call(self, persistent_context, message):

        full_response = handle_claude_api_call(
            self.client,
            model=self.model_name,
            max_tokens=4000,
            temperature=0,
            system=persistent_context,  # Persistent context
            messages=[{"role": "user", "content": message}],
        )
        return full_response
