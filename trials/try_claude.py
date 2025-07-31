from pathlib import Path
import json
import os

from typing import List, Dict, Any
from ai_apis.class_ai_claude import LDMAssistant, ClaudeLDMAssistant
from ai_apis.class_ai_keys import FMK_Claude_Key
import utils.util_all_fmk as fmk

claude_dir = "trials/claude_docs"
claude_results = "trials/claude_results"
model_path = Path(f"{claude_dir}/Literate_sample.json")
model_path = Path(f"{claude_dir}/Literate_tiny.json")
# model_path = Path(f"{claude_dir}/Literate_PD_03.model.yaml")

# Start with your model


# Process each request
####


# Example usage
def main():
    """Example of simplified workflow"""
    assistant = ClaudeLDMAssistant(api_key=FMK_Claude_Key)

    current_model = _load_model(model_path)
    # Initialize session once
    assistant.initialize_session(docs_dir=Path(claude_dir))

    # Now you can make multiple requests with memory
    requests0 = [
        # "Improve the AnnotationType class documentation",
        # "Add any missing implied inverse attributes"
    ]

    all_requests = ["\n AND ".join(requests0)]
    print("All requests are: ", "\n", all_requests, "\n")
    for i, request in enumerate(all_requests):
        print(f"\n{'='*60}")
        print(f"Request {i+1}: {request}")
        print("=" * 60)

        try:
            # Get changes only (faster)
            (result, stats) = assistant.make_request(current_model, request)

            print(f"Changes made: {len(result.get('changes', []))}")
            print(f"Summary: {result.get('summary', 'No summary')}")

            # Show changes
            changes = result.get("changes", [])
            for change in result.get("changes", []):
                print(f"  - {change['change_type']}: {change['path']}")
                print(f"    {change['reason']}")

            print("Stats are: ", json.dumps(stats, indent=2))
            # Apply changes to current model
            # current_model = _apply_changes(current_model, result["changes"])

            # Save after each request
            # save_current_model(current_model, Path(f"{claude_results}/model_after_request_{i+1}.json"))
            fmk.write_json(changes, f"{claude_results}/changes_{i+1}.json")

        except Exception as e:
            print(f"Error: {e}")
            break

    # Final model
    print(f"\nFinal model saved. Session summary:")
    print(json.dumps(assistant.get_conversation_summary(), indent=2))


def _load_model(model_path: Path) -> Dict[str, Any]:
    """Load model from file"""
    with open(model_path, "r", encoding="utf-8") as f:
        if model_path.suffix.lower() in [".yaml", ".yml"]:
            import yaml

            model = yaml.safe_load(f)
        else:
            model = json.load(f)
        model_size_bytes = os.path.getsize(model_path)

        print("Size of model is ", model_size_bytes, " - ", model_path)
        return model


def save_current_model(model, output_path: Path):
    """Save the current model state"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(model, f, indent=2)


def _apply_changes(
    model: Dict[str, Any], changes: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Apply path-based changes to model"""
    # Import the JSONPathUpdater from our utility
    from utils.util_json_path_update import ModelPatcher

    patcher = ModelPatcher(model)
    patcher.apply_changes(changes)
    return patcher.get_updated_model()


if __name__ == "__main__":

    main()
