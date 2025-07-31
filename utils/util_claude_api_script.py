#!/usr/bin/env python3
"""
LDM AI Assistant - Python script for iterative model improvement using Claude API
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List
import anthropic
from dataclasses import dataclass
import difflib

@dataclass
class ModelUpdate:
    """Represents a change to be applied to the model"""
    path: str
    old_value: Any
    new_value: Any
    reason: str
    change_type: str

class LDMAssistant:
    def __init__(self, api_key: str = None):
        """Initialize Claude API client"""
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        self.model_name = "claude-3-5-sonnet-20241022"  # Latest available
        
    def load_reference_docs(self, docs_dir: Path) -> Dict[str, str]:
        """Load all reference documents for context"""
        docs = {}
        doc_files = [
            "LiterateMetaModel_01_PD_schema.yaml",
            "LDM AI Instructions - July, 2025.md", 
            "Literate_01.py"
        ]
        
        for filename in doc_files:
            file_path = docs_dir / filename
            if file_path.exists():
                docs[filename] = file_path.read_text()
        
        return docs
    
    def load_model(self, model_path: Path) -> Dict[str, Any]:
        """Load the current model JSON/YAML"""
        with open(model_path, 'r') as f:
            if model_path.suffix.lower() in ['.yaml', '.yml']:
                import yaml
                return yaml.safe_load(f)
            else:
                return json.load(f)
    
    def save_model(self, model: Dict[str, Any], output_path: Path):
        """Save updated model"""
        with open(output_path, 'w') as f:
            if output_path.suffix.lower() in ['.yaml', '.yml']:
                import yaml
                yaml.safe_dump(model, f, default_flow_style=False, indent=2)
            else:
                json.dump(model, f, indent=2)
    
    def create_prompt(self, request: str, reference_docs: Dict[str, str], 
                     current_model: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for Claude"""
        
        # Build document context
        doc_context = "\n\n".join([
            f"<document name='{name}'>\n{content}\n</document>"
            for name, content in reference_docs.items()
        ])
        
        # Create the main prompt
        prompt = f"""
I'm working on improving a Literate Data Model (LDM). Please review the reference documents and current model, then respond to this request:

{request}

## Reference Documents:
{doc_context}

## Current Model:
<current_model>
{json.dumps(current_model, indent=2)}
</current_model>

Please provide:
1. An updated version of the complete model as JSON
2. A summary of changes made in this format:
```json
{{
  "changes": [
    {{
      "type": "change_type",
      "path": "json.path.to.changed.element", 
      "old_value": "previous value",
      "new_value": "new value",
      "reason": "explanation of why this change was made"
    }}
  ]
}}
```

Focus on the specific areas mentioned in the request, but feel free to make related improvements you notice.
"""
        return prompt
    
    def call_claude(self, prompt: str) -> str:
        """Make API call to Claude"""
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=4000,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            raise
    
    def extract_json_from_response(self, response: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Extract updated model and changes from Claude's response"""
        # This is a simplified parser - you may want to make it more robust
        import re
        
        # Extract the updated model (assuming it's the first large JSON block)
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        if not matches:
            # Try to find JSON without code blocks
            try:
                # Look for the model JSON (starts with LiterateModel)
                start = response.find('{"_type": "LiterateModel"')
                if start == -1:
                    raise ValueError("Could not find updated model JSON")
                
                # Find the matching closing brace
                brace_count = 0
                end = start
                for i, char in enumerate(response[start:]):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = start + i + 1
                            break
                
                model_json = json.loads(response[start:end])
                
                # Look for changes summary
                changes_start = response.find('"changes": [')
                changes_json = {}
                if changes_start != -1:
                    # Extract changes JSON similarly
                    pass
                
                return model_json, changes_json
                
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Could not parse JSON from response: {e}")
                print("Response snippet:", response[:500])
                raise
        
        try:
            updated_model = json.loads(matches[0])
            changes = json.loads(matches[1]) if len(matches) > 1 else {}
            return updated_model, changes
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            raise
    
    def apply_updates(self, current_model: Dict[str, Any], 
                     updates: List[ModelUpdate]) -> Dict[str, Any]:
        """Apply a list of updates to the model"""
        # For now, we'll rely on Claude returning the complete updated model
        # In the future, you could implement path-based updates using JSONPath
        return current_model
    
    def show_diff(self, old_model: Dict[str, Any], new_model: Dict[str, Any]):
        """Show differences between models"""
        old_json = json.dumps(old_model, indent=2, sort_keys=True)
        new_json = json.dumps(new_model, indent=2, sort_keys=True)
        
        diff = difflib.unified_diff(
            old_json.splitlines(keepends=True),
            new_json.splitlines(keepends=True),
            fromfile="original_model.json",
            tofile="updated_model.json",
            n=3
        )
        
        print("".join(diff))
    
    def process_request(self, request: str, model_path: Path, 
                       docs_dir: Path, output_path: Path = None) -> Dict[str, Any]:
        """Main workflow: process a request and update the model"""
        
        print(f"Loading reference documents from {docs_dir}")
        reference_docs = self.load_reference_docs(docs_dir)
        
        print(f"Loading current model from {model_path}")
        current_model = self.load_model(model_path)
        
        print("Creating prompt for Claude...")
        prompt = self.create_prompt(request, reference_docs, current_model)
        
        print("Calling Claude API...")
        response = self.call_claude(prompt)
        
        print("Parsing response...")
        try:
            updated_model, changes = self.extract_json_from_response(response)
        except Exception as e:
            print(f"Error parsing response: {e}")
            print("Full response:")
            print(response)
            return None
        
        print("\nChanges made:")
        if changes.get('changes'):
            for change in changes['changes']:
                print(f"  - {change['type']}: {change['path']}")
                print(f"    Reason: {change['reason']}")
        
        print("\nModel diff:")
        self.show_diff(current_model, updated_model)
        
        # Save updated model
        if output_path is None:
            output_path = model_path.parent / f"{model_path.stem}_updated{model_path.suffix}"
        
        print(f"\nSaving updated model to {output_path}")
        self.save_model(updated_model, output_path)
        
        return updated_model

def main():
    """Example usage"""
    assistant = LDMAssistant()
    
    # Example paths - adjust to your setup
    model_path = Path("Literate_PD_04.v_model.json")
    docs_dir = Path(".")  # Directory containing reference docs
    
    # Example requests
    requests = [
        "Review and improve the one-liners for all classes in the Preliminaries section",
        "Add missing Python expressions for all constraints and derivations",
        "Add implied inverse attributes where appropriate",
        "Review the Subject class and improve its documentation"
    ]
    
    for i, request in enumerate(requests):
        print(f"\n{'='*60}")
        print(f"Processing request {i+1}: {request}")
        print('='*60)
        
        try:
            updated_model = assistant.process_request(
                request=request,
                model_path=model_path,
                docs_dir=docs_dir,
                output_path=Path(f"model_iteration_{i+1}.json")
            )
            
            # Update model_path for next iteration
            model_path = Path(f"model_iteration_{i+1}.json")
            
            input("Press Enter to continue to next request...")
            
        except Exception as e:
            print(f"Error processing request: {e}")
            break

if __name__ == "__main__":
    main()
