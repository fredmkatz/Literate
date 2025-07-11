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

def generate_diagram_code(data: Dict, radius: int) -> str:
    """Generate 100% Mermaid-compatible ER diagram."""
    lines = ["erDiagram"]
    
    all_classes = [cls for cls in data['classes'] if cls.get('_type') in ['Class', 'ValueType']]
    nclasses = len(all_classes)
    all_class_names =  {cls['name'] for cls in all_classes}
    # print("All classes are: ", all_classes)
    # print(all_class_names)
    
    classes = [c for c in all_classes if c['distance'] <= radius]
    nshown = len(classes)
    print(f"Showing {nshown} of {nclasses} classes")
    class_names = {cls['name'] for cls in classes}
    # print(class_names)
    
    # Add relationships - using ONLY the exact syntax from working examples
    for cls in classes:
        class_name = cls['name']
        for edge in cls.get('edges', []):
            relation = edge.get('relation')
            target = edge.get('to')
            if target not in class_names:
                # print(f"Skipping {edge}, {target} out of focus")
                continue
            cardinality = edge.get('cardinality', '1:1')
            
                
            left_card, right_card = convert_cardinality(cardinality)
            
            # Use the EXACT same format as working customer/order example
            lines.append(f"    {class_name} {left_card}--{right_card} {target} : {relation}")
    
    return "\n".join(lines)

import utils.util_all_fmk as fmk
import networkx as nx

def mark_distances(extract: dict, focal_points: list[str] = []) -> dict:
    
    distances = calc_distances(extract, focal_points)
    if not distances:
        return None
    # print("\nShortest distance for each node to any focal point:")
    # for cname, distance in distances.items():
    #     print("\t", cname, "\t", distance)

    for cls in extract["classes"]:
        class_name = cls['name']
        distance = distances.get(class_name, 2000)
        cls["distance"] = distance

    return extract

def calc_distances(extract: dict, focal_points: list[str]= []) -> dict:
    # Example graph
    all_edges = derive_edges_for_extract(extract)
    
    # print("Focus is ", focal_points)
    # print("All edges are: ", all_edges)
    all_nodes = set(e[0] for e in all_edges).union(set(e[1] for e in all_edges))
    # print("All nodes are ", all_nodes)
    if not set(focal_points).issubset(all_nodes):
        print("Focal points not contained in nodes - skipping diagram")
        return None
    G = nx.Graph()
    G.add_edges_from(all_edges)

    # print(G)

    # Calculate shortest path lengths from each focal point
    all_distances = {} # Store the results in a dictionary

    for focus_node in focal_points:
        # Calculate shortest path lengths from the current focus_node
        distances_from_focus = nx.shortest_path_length(G, source=focus_node)
        all_distances[focus_node] = dict(distances_from_focus) # Convert to dictionary for easy access
    # The 'all_distances' dictionary will now hold path lengths from each focal point
    # print("All Distances", all_distances)
    
    # --- New code to find the minimum distance to any focal point ---
    shortest_distance_to_foci = {}
    unreachable_value = 1000 # Define the value for unreachable nodes

    # Iterate through all nodes in the graph
    for node in G.nodes():
        min_dist_for_node = unreachable_value # Initialize with the unreachable value

        # Check distances from each focal point to the current node
        for focus_node in focal_points:
            if node in all_distances[focus_node]:
                # If the node is reachable from this focal point, update min_dist_for_node
                dist = all_distances[focus_node][node]
                min_dist_for_node = min(min_dist_for_node, dist)

        shortest_distance_to_foci[node] = min_dist_for_node

    return(shortest_distance_to_foci)
    

def derive_edges_for_extract(extract: dict) -> list:
    classes = extract["classes"]
    all_edges = []
    for cls in classes:
        cname = cls["name"]
        for edge in cls["edges"]:
            target = edge["to"]
            all_edges.append((cname, target))
    return all_edges

def generate_focused_diagram(full_extract_path: str, focal_points: list[str], radius: int):
    full_extract = load_yaml(full_extract_path)
    marked_extract = mark_distances(full_extract, focal_points=focal_points)
    if(not marked_extract):
        return None
    focuswords = "-".join(focal_points)
    marked_path = full_extract_path.replace(".yaml", f"_{focuswords}.yaml")
    fmk.write_yaml(marked_extract, marked_path)
    # Generate the Mermaid diagram
    diagram_code = generate_diagram_code(marked_extract, radius=radius)
    return diagram_code

def main():
    # Load the YAML file
    
    diagram_code = generate_focused_diagram('trials/extract_diagrams/Literate_15_extract.yaml', ["Class_", "Attribute"], 1)
    # Print or save the result
    print(diagram_code)
    fence = "```"
    with open('trials/extract_diagrams/Literate_15_extract.md', 'w') as f:
        f.write(f"{fence} mermaid\n")
        f.write(diagram_code)
        f.write(f"\n{fence}\n")

if __name__ == '__main__':
    main()