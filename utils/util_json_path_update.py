#!/usr/bin/env python3
"""
Utility for applying path-based updates to JSON models
"""

import json
from typing import Any, Dict, List, Union
from pathlib import Path
import copy

class JSONPathUpdater:
    """Utility for updating JSON using path-based operations"""
    
    @staticmethod
    def get_by_path(data: Dict[str, Any], path: str) -> Any:
        """Get value at JSON path (e.g., 'subjects[0].classes[1].name')"""
        keys = JSONPathUpdater._parse_path(path)
        current = data
        
        for key in keys:
            if isinstance(key, int):
                current = current[key]
            else:
                current = current[key]
        
        return current
    
    @staticmethod
    def set_by_path(data: Dict[str, Any], path: str, value: Any) -> Dict[str, Any]:
        """Set value at JSON path, returning updated copy"""
        result = copy.deepcopy(data)
        keys = JSONPathUpdater._parse_path(path)
        current = result
        
        # Navigate to parent of target
        for key in keys[:-1]:
            if isinstance(key, int):
                current = current[key]
            else:
                current = current[key]
        
        # Set the final value
        final_key = keys[-1]
        if isinstance(final_key, int):
            current[final_key] = value
        else:
            current[final_key] = value
            
        return result
    
    @staticmethod
    def _parse_path(path: str) -> List[Union[str, int]]:
        """Parse path string into list of keys/indices"""
        # Simple parser for paths like 'subjects[0].classes[1].name'
        parts = []
        current = ""
        i = 0
        
        while i < len(path):
            char = path[i]
            
            if char == '.':
                if current:
                    parts.append(current)
                    current = ""
            elif char == '[':
                if current:
                    parts.append(current)
                    current = ""
                # Find closing bracket
                j = i + 1
                while j < len(path) and path[j] != ']':
                    j += 1
                index_str = path[i+1:j]
                parts.append(int(index_str))
                i = j  # Skip the ']'
            else:
                current += char
            
            i += 1
        
        if current:
            parts.append(current)
            
        return parts

class ModelPatcher:
    """Apply structured changes to LDM models"""
    
    def __init__(self, model: Dict[str, Any]):
        self.original_model = model
        self.current_model = copy.deepcopy(model)
        self.changes_applied = []
    
    def apply_change(self, change: Dict[str, Any]) -> bool:
        """Apply a single change to the model"""
        try:
            path = change['path']
            new_value = change['new_value']
            change_type = change.get('type', 'update')
            
            # Verify old value matches if provided
            if 'old_value' in change:
                current_value = JSONPathUpdater.get_by_path(self.current_model, path)
                if current_value != change['old_value']:
                    print(f"Warning: Expected '{change['old_value']}' at {path}, found '{current_value}'")
            
            # Apply the change
            self.current_model = JSONPathUpdater.set_by_path(
                self.current_model, path, new_value
            )
            
            self.changes_applied.append({
                **change,
                'status': 'applied'
            })
            
            return True
            
        except Exception as e:
            print(f"Error applying change to {change.get('path', 'unknown')}: {e}")
            self.changes_applied.append({
                **change,
                'status': 'failed',
                'error': str(e)
            })
            return False
    
    def apply_changes(self, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply multiple changes and return statistics"""
        successful = 0
        failed = 0
        
        for change in changes:
            if self.apply_change(change):
                successful += 1
            else:
                failed += 1
        
        return {
            'total': len(changes),
            'successful': successful,
            'failed': failed,
            'changes_applied': self.changes_applied
        }
    
    def get_updated_model(self) -> Dict[str, Any]:
        """Get the current state of the model"""
        return self.current_model
    
    def save_model(self, output_path: Path):
        """Save the updated model"""
        with open(output_path, 'w') as f:
            json.dump(self.current_model, f, indent=2)
    
    def create_patch_file(self, output_path: Path):
        """Create a patch file showing all changes"""
        patch_data = {
            'original_model_info': {
                'name': self.original_model.get('name', {}).get('content', 'Unknown'),
                'classes_count': len(self._count_classes(self.original_model)),
            },
            'changes_summary': {
                'total_changes': len(self.changes_applied),
                'successful': len([c for c in self.changes_applied if c['status'] == 'applied']),
                'failed': len([c for c in self.changes_applied if c['status'] == 'failed'])
            },
            'changes': self.changes_applied
        }
        
        with open(output_path, 'w') as f:
            json.dump(patch_data, f, indent=2)
    
    def _count_classes(self, model: Dict[str, Any]) -> int:
        """Count total classes in model"""
        count = 0
        
        def count_in_subject(subject):
            nonlocal count
            count += len(subject.get('classes', []))
            for sub_subject in subject.get('subjects', []):
                count_in_subject(sub_subject)
        
        count += len(model.get('classes', []))
        for subject in model.get('subjects', []):
            count_in_subject(subject)
            
        return count

# Example usage and testing
def test_json_path_updater():
    """Test the JSONPathUpdater"""
    sample_data = {
        "subjects": [
            {
                "name": {"content": "Test Subject"},
                "classes": [
                    {"name": {"content": "TestClass"}, "attributes": []}
                ]
            }
        ]
    }
    
    # Test getting values
    name = JSONPathUpdater.get_by_path(sample_data, "subjects[0].name.content")
    print(f"Got name: {name}")
    
    # Test setting values  
    updated = JSONPathUpdater.set_by_path(
        sample_data, 
        "subjects[0].classes[0].name.content", 
        "UpdatedClass"
    )
    
    new_name = JSONPathUpdater.get_by_path(updated, "subjects[0].classes[0].name.content")
    print(f"Updated name: {new_name}")

def example_model_update():
    """Example of updating a model with changes"""
    # Load your model
    model_path = Path("Literate_PD_04.v_model.json")
    if not model_path.exists():
        print(f"Model file {model_path} not found")
        return
        
    with open(model_path, 'r') as f:
        model = json.load(f)
    
    # Create patcher
    patcher = ModelPatcher(model)
    
    # Example changes (these would come from Claude's response)
    changes = [
        {
            "type": "one_liner_improvement",
            "path": "subjects[0].classes[0].one_liner.content",
            "old_value": "An element or building block of the literate data model",
            "new_value": "fundamental building block of the literate data model",
            "reason": "Made more concise and precise as noun phrase"
        },
        {
            "type": "python_expression_added",
            "path": "subjects[0].classes[0].attributes[3].default.python",
            "new_value": "generate_abbreviation(x.name)",
            "reason": "Added proper Python expression for default value calculation"
        }
    ]
    
    # Apply changes
    result = patcher.apply_changes(changes)
    print(f"Applied {result['successful']}/{result['total']} changes")
    
    # Save updated model
    output_path = Path("updated_model.json")
    patcher.save_model(output_path)
    print(f"Saved updated model to {output_path}")
    
    # Create patch file
    patch_path = Path("model_changes.json")
    patcher.create_patch_file(patch_path)
    print(f"Saved change log to {patch_path}")

if __name__ == "__main__":
    test_json_path_updater()
    # example_model_update()
