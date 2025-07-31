#!/usr/bin/env python3
"""
Simplified LDM AI Assistant with JSON-only responses and conversation memory
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import anthropic
from dataclasses import dataclass

class LDMAssistant:
    def __init__(self, api_key: str = None):
        """Initialize Claude API client"""
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        self.model_name = "claude-3-5-sonnet-20241022"
        
        # Conversation state
        self.conversation_history = []
        self.reference_docs = {}
        self.current_model = None
        self.system_prompt = None
        
    def initialize_session(self, docs_dir: Path, model_path: Path):
        """Set up the session with reference docs and initial model"""
        print("Initializing session...")
        
        # Load reference documents once
        self.reference_docs = self._load_reference_docs(docs_dir)
        
        # Load initial model
        self.current_model = self._load_model(model_path)
        
        # Create system prompt that will persist
        self.system_prompt = self._create_system_prompt()
        
        print(f"Session initialized with {len(self.reference_docs)} reference docs")
        print(f"Model loaded: {self.current_model.get('name', {}).get('content', 'Unknown')}")
    
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
                size =  len(docs[filename])
                print("Loading doc: ", filename, ". Length is ", size)
                total_size += size
        print("Total size in bytes is: ", total_size, " = about ", total_size/4, " tokens")
        return docs
    
    def _load_model(self, model_path: Path) -> Dict[str, Any]:
        """Load model from file"""
        with open(model_path, 'r', encoding="utf-8") as f:
            if model_path.suffix.lower() in ['.yaml', '.yml']:
                import yaml
                model =  yaml.safe_load(f)
            else:
                model = json.load(f)
            model_size_bytes = os.path.getsize(model_path)

            print("Size of model is ", model_size_bytes, " - ", model_path)
            return model
    
    def _create_system_prompt(self) -> str:
        """Create the persistent system prompt"""
        doc_context = "\n\n".join([
            f"<document name='{name}'>\n{content}\n</document>"
            for name, content in self.reference_docs.items()
        ])
        
        return f"""You are an AI assistant specialized in improving Literate Data Models (LDMs). 

## Reference Documents:
{doc_context}
"""

    def make_request(self, request: str, return_full_model: bool = False) -> Dict[str, Any]:
        """Make a request to Claude with conversation memory"""
        
        if not self.current_model:
            raise ValueError("Session not initialized. Call initialize_session() first.")
        
        # Create user message
        user_message = f"""Current model:
{json.dumps(self.current_model, indent=2)}

Request: {request}

Please respond with {"complete updated model" if return_full_model else "changes only"} in the specified JSON format."""

        try:
            self.conversation_history = []  # Reset completely

            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=4000,
                temperature=0,
                system=self.system_prompt,  # Persistent context
                messages=self.conversation_history + [
                    {"role": "user", "content": user_message}
                ]
            )
            print(response)
            # json.dumps(response, indent=2)
            
            print("incidentals...")
            print("\tid", " => ", response.id)
            print("\tmodel", " => ", response.model)
            print("\tusage", " => ", response.usage)

            response_text = response.content[0].text.strip()
            
            # Parse JSON response
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {e}")
                print(f"Response was: {response_text[:500]}...")
                raise
            print("\nfull result is...")
            print(result)
            print("====================")

            # Update conversation history (keep it manageable)
            self.conversation_history.append({"role": "user", "content": request})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            # Keep conversation history from getting too long
            if len(self.conversation_history) > 10:  # Keep last 5 exchanges
                self.conversation_history = self.conversation_history[-10:]
            
            # Update current model if full model was returned
            if result.get("response_type") == "full_model":
                self.current_model = result["model"]
            elif result.get("response_type") == "changes":
                changes = result["changes"]
                print("\tand changes are")
                print(json.dumps(changes, indent=2))
                # Apply changes to current model
                return result
                # self.current_model = self._apply_changes(self.current_model, result["changes"])
            
            return result
            
        except Exception as e:
            print(f"Error making request: {e}")
            raise
    
    def _apply_changes(self, model: Dict[str, Any], changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply path-based changes to model"""
        # Import the JSONPathUpdater from our utility
        from json_updater import ModelPatcher
        
        patcher = ModelPatcher(model)
        patcher.apply_changes(changes)
        return patcher.get_updated_model()
    
    def save_current_model(self, output_path: Path):
        """Save the current model state"""
        with open(output_path, 'w') as f:
            json.dump(self.current_model, f, indent=2)
    
    def get_current_model(self) -> Dict[str, Any]:
        """Get current model state"""
        return self.current_model
    
    def reset_conversation(self):
        """Clear conversation history but keep docs and model"""
        self.conversation_history = []
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        return {
            "conversation_length": len(self.conversation_history),
            "reference_docs_loaded": list(self.reference_docs.keys()),
            "model_name": self.current_model.get('name', {}).get('content', 'Unknown') if self.current_model else None,
            "session_initialized": self.current_model is not None
        }


