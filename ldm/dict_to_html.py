import json
from pathlib import Path
from utils_pom.util_fmk_pom import write_text
def create_dict_html(data, html_path):
    
    html = dict_to_html(data)
    write_text(html_path, html)
    css_path = "ldm/Literate.css"
    save_styled_dict(data, css_path, html_path)
    
def dict_to_html(data, indent=0):
    html = []
    indent_str = " " * indent * 4
    
    if isinstance(data, dict):
        for key, value in data.items():
            if key == '_type':
                continue
            value_type = getattr(value, '_type', type(value).__name__)
            html.append(f'{indent_str}<div class="{value_type}">')
            html.append(f'{indent_str}  <span class="key">{key}:</span>')
            html.append(f'{indent_str}  <span class="value">{dict_to_html(value, indent+1)}</span>')
            html.append(f'{indent_str}</div>')
    elif isinstance(data, list):
        html.append(f'{indent_str}<div class="list">')
        for item in data:
            html.append(dict_to_html(item, indent+1))
        html.append(f'{indent_str}</div>')
    else:
        return f'{data}'
    
    return "\n".join(html)

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

