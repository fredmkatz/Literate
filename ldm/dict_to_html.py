import json
from pathlib import Path
from utils_pom.util_fmk_pom import write_text
from typing import Dict, List
HEADER_KEYS = ["prefix", "name", "one_liner", "parenthetical"]
HEADED_CLASSES = ["LDM", "Subject", "Class", "AttributeSection", "Attribute"]
USELESS_LIST_KEYS = [
    "attribute_sections",
	 "constraints",
	 "classes",
	 "attributes",
	 "annotations",
	 "subjects",
     "elaboration",
]

CLASS_LIST_KEYS = [
    "based_on",
    "dependent_of",
    "subtype_of",
    "subtypes",
]
def is_headed(class_name: str) -> bool:
    return class_name in HEADED_CLASSES or class_name.startswith("Subject")

def create_dict_html(data, html_path):
    all_dict_keys = all_keys(data)
    print("All keys are: ")
    for x in all_dict_keys:
        print("\t", x)
    
    html = dict_to_html(data)
    write_text(html_path, html)
    css_path = "../Literate.css"
    save_styled_dict(data, css_path, html_path)

def all_keys(data) -> List[str]:
    keys = set()
    if isinstance(data, dict):
        for key, value in data.items():
            keys.add(key)
            keys.update(all_keys(value))
    elif isinstance(data, List):
        for element in data:
            keys.update(all_keys(element))
    return keys
            

    
def dict_to_html(data, indent=0):
    html = []
    indent_str = " " * indent * 4
    
    if isinstance(data, dict):
        
        obj_type = "DICT"
        for key, value in data.items():
            if key == '_type':
                obj_type = value
                break
        
        # Simplify SubjectB, etc
        if obj_type.startswith("Subject"):
            obj_type = "Subject"
        # print("Object type is ", obj_type)
        html.append(f'{indent_str}<div class="{obj_type}">')
        indent += 1
        indent_str = " " * indent * 4
        
        # Gather into header: Prefix, name, oneliner, parenthetical
        if is_headed(obj_type):
            # Start the header
            html.append(f'{indent_str}<div class="{obj_type}_header header">')
            indent += 1
            indent_str = " " * indent * 4

            # add header attributes
            for key, value in data.items():
                if key == '_type':
                    continue
                if key not in HEADER_KEYS:
                    continue
                # print("kv is ", key, value)
                if value.strip() == "":
                    continue
                if key == "name":
                    add_anchor_html(key, value, html, indent)
                else:
                    add_classed_value_html(key, value, html, indent)

            # end the header
            indent -= 1
            indent_str = " " * indent * 4
            html.append(f'{indent_str}</div>')

        for key, value in data.items():
            if key == '_type':
                continue
            if key in HEADER_KEYS:
                continue
            if key in USELESS_LIST_KEYS:
                add_headless_list_html(key, value, html, indent)
                continue
            if key in CLASS_LIST_KEYS:
                add_anchored_class_names(key, value, html, indent + 1)
                continue
            add_key_value_html(key, value, html, indent)
        indent -= 1
        indent_str = " " * indent * 4
        html.append(f'{indent_str}</div>')

    elif isinstance(data, list):
        html.append(f'{indent_str}<div class="list">')
        for item in data:
            html.append(dict_to_html(item, indent+1))
        html.append(f'{indent_str}</div>')
    else:
        return f'{data}'
    
    return "\n".join(html)

def add_anchored_class_names(key, names, html, indent):
    indent_str = " " * indent * 4
    html.append(f'{indent_str}<div class="class_name_list">')
    html.append(f'{indent_str}  <span class="key">{key}:</span>')
    html.append(f'{indent_str}  <div class="class_names">')
    for name in names:
        html.append(f'{indent_str}  <a class="class_name" href="#{name}">{name}</a>')
    html.append(f'{indent_str}</div>')

    html.append(f'{indent_str}</div>')

def add_headless_list_html(key, value, html, indent):
    indent_str = " " * indent * 4
    
    html.append(f'{indent_str}<div class="list {key}">')
    for item in value:
        html.append(dict_to_html(item, indent+1))
    html.append(f'{indent_str}</div>')

    
def add_anchor_html(class_name, value, html, indent):
    indent_str = " " * indent * 4
    # print(f"add anchor called for {class_name}, {value}")
    html.append(f'{indent_str}<a class="{class_name}"  id="{value}">{value}</a>')

def add_key_value_html(key, value, html, indent):
    indent_str = " " * indent * 4

    value_type = getattr(value, '_type', type(value).__name__)
    html.append(f'{indent_str}<div class="{value_type}">')
    html.append(f'{indent_str}  <span class="key">{key}:</span>')
    html.append(f'{indent_str}  <span class="value">{dict_to_html(value, indent+1)}</span>')
    html.append(f'{indent_str}</div>')
    
def add_classed_value_html(key, value, html, indent):
    indent_str = " " * indent * 4

    html.append(f'{indent_str} <span class="value {key}">{dict_to_html(value, indent+1)}</span>')
    

def save_styled_dict(data, css_path="styles.css", output_path="output.md"):
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="{css_path}">
</head>
<body>
{dict_to_html(data)}
</body>
</html>
"""
    
    Path(output_path).write_text(html_content, encoding="utf-8")
    print(f"Saved styled dictionary to {output_path}")


# Example CSS (save this as styles.css)
example_css = """
/* styles.css */
div {
    margin-left: 20px;
    padding: 5px;
    border-left: 1px solid #eee;
}

.key {
    color: #2c3e50;
    font-weight: bold;
    margin-right: 10px;
}

.value {
    color: #3498db;
}

.custom_type {
    background-color: #f8f9fa;
    padding: 8px;
    border-radius: 4px;
}

.list {
    color: #27ae60;
}

.user_profile {
    border: 2px solid #e74c3c;
    padding: 10px;
}
"""

Path("styles.css").write_text(example_css)

if __name__ == "__main__":
    # Example usage
    class CustomType:
        def __init__(self, value):
            self._type = "custom_type"
            self.value = value

    sample_data = {
        "user": {
            "name": "Alice",
            "age": 30,
            "preferences": CustomType(["reading", "hiking"]),
            "_type": "user_profile"
        },
        "system": {
            "version": 2.4,
            "active": True,
            "modules": ["auth", "database"]
        }
    }

    # Save the styled output
    save_styled_dict(sample_data)

