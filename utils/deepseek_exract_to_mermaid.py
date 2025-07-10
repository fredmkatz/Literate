import yaml
from typing import Dict, List

def load_yaml(file_path: str) -> Dict:
    """Load YAML file into a dictionary."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def convert_cardinality(card: str) -> tuple:
    """Convert YAML cardinality to Mermaid's exact ER syntax."""
    if card == 'M:1':
        return ("}o", "||")  # Many-to-one
    elif card == '1:1':
        return ("||", "||")  # One-to-one
    elif card == 'O_O':
        return ("|o", "o|")  # Optional-to-optional
    return ("||", "||")  # Default to one-to-one

def generate_mermaid_er_diagram(data: Dict) -> str:
    """Generate 100% Mermaid-compatible ER diagram."""
    lines = ["erDiagram"]
    
    classes = [cls for cls in data['classes'] if cls.get('_type') in ['Class', 'ValueType']]
    class_names = {cls['name'] for cls in classes}
    
    # Add relationships - using ONLY the exact syntax from working examples
    for cls in classes:
        class_name = cls['name']
        for edge in cls.get('edges', []):
            relation = edge.get('relation')
            target = edge.get('to')
            cardinality = edge.get('cardinality', '1:1')
            
            if target not in class_names:
                continue
                
            left_card, right_card = convert_cardinality(cardinality)
            
            # Use the EXACT same format as working customer/order example
            lines.append(f"    {class_name} {left_card}--{right_card} {target} : {relation}")
    
    return "\n".join(lines)

            
def main():
    # Load the YAML file
    data = load_yaml('trials/extract_diagrams/Literate_15_extract.yaml')
    
    # Generate the Mermaid diagram
    mermaid_diagram = generate_mermaid_er_diagram(data)
    
    # Print or save the result
    print(mermaid_diagram)
    fence = "```"
    with open('trials/extract_diagrams/Literate_15_extract.md', 'w') as f:
        f.write(f"{fence} mermaid\n")
        f.write(mermaid_diagram)
        f.write(f"\n{fence}\n")

if __name__ == '__main__':
    main()