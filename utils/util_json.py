from typing import Dict, Any
from dataclasses import asdict
import json
import yaml

def update_nested_dict(original, updates):
    for key, value in updates.items():
        if isinstance(value, dict):
            original[key] = update_nested_dict(original.get(key, {}), value)
        else:
            original[key] = value
    return original




def clean_dict(obj):
    """Convert dataclass instance to dict, excluding None values."""
    if isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, list):
        return [clean_dict(item) for item in obj if item is not None]
    elif isinstance(obj, dict):
        # diagnostics = obj.get("diagnostics", None)
        # if diagnostics:
        #     print("Seeing diagnostics in dict: ", diagnostics)
            
        new_dict =  {
            k: clean_dict(v)
            for k, v in obj.items()
            if v is not None and not (isinstance(v, (list, dict)) and not v)
        }
        return front_key(new_dict, "_type") # make sure that _type - if present - is first entry
    elif hasattr(obj, "__dataclass_fields__"):  # Is a dataclass
        return {
            k: clean_dict(v)
            for k, v in asdict(obj).items()
            if v is not None and not (isinstance(v, (list, dict)) and not v)
        }
    else:
        return "UnserializablePiece"
    return obj

def front_key(d: Dict, key) -> Dict:
    if not d.get(key, None):
        return d
    return {**plop(d, key), **d}
    
# get a one item dict with just the specified key
def plop(d, key):
    return {key: d.pop(key)}

# d = {'a': 1, 'b': 2, 'c': 3}  # original dict
# d = {**plop(d, 'b'), **d}  # new order
# print(d)
# # {'b': 2, 'a': 1, 'c': 3}


def as_json(obj):
    return json.dumps(clean_dict(obj), indent=2)

def read_yaml_file(yaml_path: str) -> Dict[str, Any]:
    """
    Read a YAML file and return its contents as a dictionary.

    Args:
        yaml_path: Path to the YAML file

    Returns:
        Dictionary with file contents, or empty dict if file not found
    """
    if os.path.exists(yaml_path):
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            flogger.warningf(f"Error reading YAML file {yaml_path}: {e}")
            return {}
    return {}


def as_yaml(the_dict: Dict) -> str:
    return yaml.dump(
        clean_dict(the_dict), indent=4, default_flow_style=False, sort_keys=False
    )

def write_json(the_dict: Dict, file_path: str):
    import utils.util_all_fmk as fmk

    fmk.write_text(file_path, as_json(the_dict))
def write_yaml(the_dict: Dict, file_path: str):
    """
    Write a dictionary to a YAML file.

    Args:
        the_dict: Dictionary to write
        file_path: Path to write the YAML file
    """
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(clean_dict(the_dict), f, default_flow_style=False, sort_keys=False)


def json_census(json_object):
    """Counts the occurrences of keys in a JSON object and returns two dictionaries.

    This function recursively traverses a JSON object (represented as a Python
    dictionary or list) and counts the number of times each key appears.

    Args:
        json_object: The JSON object to analyze. Can be a dictionary or a list.

    Returns:
        A tuple of two dictionaries:
        - The first dictionary where each key is a tag and its value is the count of occurrences.
        - The second dictionary where each key is a count and its value is a list of tags with that count.

    Examples:
        >>> json_census({"a": 1, "b": [1, 2, {"c": 3}]})
        ({'a': 1, 'b': 3, 'c': 1}, {1: ['a', 'c'], 3: ['b']})
        >>> json_census([{"a": 1}, {"b": 2}])
        ({'a': 1, 'b': 1}, {1: ['a', 'b']})
        >>> json_census({"a": [1, 2], "b": {"a": 1}})
        ({'a': 3, 'b': 1}, {1: ['b'], 3: ['a']})
    """

    def count_tags(obj, counts):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key not in counts:
                    counts[key] = 0
                if isinstance(value, (str, int, float, bool, type(None))):
                    counts[key] += 1
                elif isinstance(value, list):
                    counts[key] += len(value)
                    for item in value:
                        count_tags(item, counts)
                elif isinstance(value, dict):
                    counts[key] += 1
                    count_tags(value, counts)
        elif isinstance(obj, list):
            for item in obj:
                count_tags(item, counts)

    counts = {}
    count_tags(json_object, counts)

    by_count = {}
    for tag, count in counts.items():
        if count not in by_count:
            by_count[count] = []
        by_count[count].append(tag)

    for count in by_count:
        by_count[count].sort()

    return counts, by_count


if __name__ == "__main__":
    print(json_census({"a": 1, "b": [1, 2, {"c": 3}]}))
    print(json_census([{"a": 1}, {"b": 2}]))
    print(json_census({"a": [1, 2], "b": {"a": 1}}))
