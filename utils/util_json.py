from typing import Dict, Any
from dataclasses import asdict
import json
import yaml
import os

from utils.util_flogging import flogger
from utils.util_fmk import glob_files, insure_home_for, write_text
def update_nested_dict(original, updates):
    for key, value in updates.items():
        if isinstance(value, dict):
            original[key] = update_nested_dict(original.get(key, {}), value)
        else:
            original[key] = value
    return original




def clean_dict(obj, warnings: bool = False):
    """Convert dataclass instance to dict, excluding None values."""
    # print("Clean dict, warnings =  ", warnings)
    if isinstance(obj, (str, int, float, bool)):
        return obj
    elif not obj:
        return None
    elif isinstance(obj, list):
        return [clean_dict(item, warnings = warnings) for item in obj if item is not None]
    elif isinstance(obj, dict):
            
        new_dict =  {
            k: clean_dict(v, warnings=warnings)
            for k, v in obj.items()
            if v is not None and not (isinstance(v, (list, dict)) and not v)
        }
        if not new_dict.get("_type", None) and warnings:
            print("CD WARNING2 - dict without _type attribute - ", new_dict)
        return front_key(new_dict, "_type") # make sure that _type - if present - is first entry
    elif hasattr(obj, "__dataclass_fields__"):  # Is a dataclass
        objtype = type(obj).__name__

        if warnings:
            print(f"CD WARNING:  clean_dict found {objtype} dataclass; converting to dict")
        dcvalue = {
            k: clean_dict(v, warnings=warnings)
            for k, v in asdict(obj).items()
            if v is not None and not (isinstance(v, (list, dict)) and not v)
        }
        dcdict = {"_type": objtype}
        # dcdict = {"_type": objtype, "_pytype": type(obj)}
        dcdict.update(dcvalue)
        if warnings:
            print("Converted DC to dict:", objtype)
            print(repr(obj))
            print("became...")
            print(dcdict)
            
        return dcdict
    else:
        objtype = type(obj).__name__

        print(f"clean_dict WARNING: Cannot serialize {objtype} {obj} = \n\t***\t{repr(obj)}")
        return "UnserializablePiece"
    return obj

def make_tidy_yaml(src_yaml_path):
    
    the_dict = read_yaml_file(src_yaml_path)
    tidied = tidy_dict(the_dict, warnings=True)
    tidy_path = src_yaml_path.replace(".yaml", ".tidy.yaml")
    write_yaml(tidied, tidy_path)
    return tidied

def tidy_dict(src_dict, warnings: bool = False):
    """Convert a pure dict to one w/o nulls, "", [] or {}."""
    # print("Clean dict, warnings =  ", warnings)
    
    if isinstance(src_dict, (str, int, float, bool)):
        if src_dict == "":
            return None
        return src_dict

    elif not src_dict:
        return None

    elif isinstance(src_dict, list):
        # Process each item and filter out None results
        items = []
        for item in src_dict:
            cleaned_item = tidy_dict(item, warnings=warnings)
            if cleaned_item is not None:
                items.append(cleaned_item)
        
        if not items:
            return None
        return items
    elif isinstance(src_dict, dict):
        new_dict = {}
        for k, v in src_dict.items():
            cleaned_v = tidy_dict(v, warnings=warnings)
            if cleaned_v is not None:
                new_dict[k] = cleaned_v

        if not new_dict:
            return None
        return new_dict
            
    objtype = type(src_dict).__name__
    if warnings:
        print(f"tidy_dict WARNING: Cannot serialize - type = {objtype}; src_dict = \n\t***\t{repr(src_dict)}")
    return "UnserializablePiece"

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


def as_json(obj, warnings: bool = False):
    # the_dict = clean_dict(obj, warnings)
    the_dict = obj
    return json.dumps(the_dict, indent=2)

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

def read_json_file(json_path: str) -> Dict[str, Any]:
    """
    Read a JSON file and return its contents as a dictionary.

    Args:
        json_path: Path to the YAML file

    Returns:
        Dictionary with file contents, or empty dict if file not found
    """
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception as e:
            flogger.warningf(f"Error reading JSON file {json_path}: {e}")
            return {}
    flogger.warning(f"JSON path not found: {json_path}")
    return {}


def as_yaml(the_dict: Dict, warnings: bool = False) -> str:
    # print("as yaml - warnings = ", warnings)
    
    yaml.emitter.Emitter.prepare_tag = lambda self, tag: ''
    ditems = the_dict.get("dictitems", None)
    if ditems:
        print("AVOIDING dictitems?")
        the_dict = ditems[0]
    return yaml.dump(the_dict,  indent=4, default_flow_style=False, sort_keys=False)

def write_json(the_dict: Dict, file_path: str, warnings: bool = False):

    write_text(file_path, as_json(the_dict, warnings=warnings))
    
def write_yaml(the_dict: Dict, file_path: str, warnings: bool = False):
    """
    Write a dictionary to a YAML file.

    Args:
        the_dict: Dictionary to write
        file_path: Path to write the YAML file
    """
    insure_home_for(file_path)
    write_text(file_path, as_yaml(the_dict, warnings=warnings))


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

from collections import defaultdict

def count_key_paths(data, path=None, counts=None):
    if path is None:
        path = ""
    if counts is None:
        counts = defaultdict(int)

    if isinstance(data, dict):
        dtype = data.get("_type", None)
        if dtype : 
            path = dtype
        for key, value in data.items():
            current_path = path + "." + key
            counts[current_path] += 1
            count_key_paths(value, current_path, counts)
    elif isinstance(data, list):
        for item in data:
            count_key_paths(item, path, counts)

    counts = dict(sorted(counts.items()))
    return counts

from typing import Dict

def merge_counts(pieces: Dict[str, dict]) -> Dict:
    """compare and combine count dictionaries

    Args:
        pieces (Dict[str, dict]): Each piece has a name and a dictionary of (str -> int)

    Returns:
        Dict: The result is a dictionary from the keys found in any of the pieces to
        a "merged result".  The merged result itself is a dictionary from piece name to
        count (for each piece which had a count for that key)
        The exception: If all pieces had a value - and the same value for a key, then the 
        merged result should just be {"All": common value}
    """
    if not pieces:
        return {}
    
    # Collect all possible keys across all pieces
    all_keys = set()
    for piece_dict in pieces.values():
        all_keys.update(piece_dict.keys())
    
    result = {}
    
    for key in all_keys:
        # Collect values for this key from each piece that has it
        key_values = {}
        for piece_name, piece_dict in pieces.items():
            if key in piece_dict:
                key_values[piece_name] = piece_dict[key]
        
        # Check if all pieces have this key and they all have the same value
        if len(key_values) == len(pieces):  # All pieces have this key
            unique_values = set(key_values.values())
            if len(unique_values) == 1:  # All values are the same
                result[key] = {"All": list(unique_values)[0]}
            else:
                result[key] = key_values
        else:
            # Not all pieces have this key, so just store the pieces that do
            result[key] = key_values
    
    return result
def show_census(fd, caption, census):
    print("\nCensus: ", caption, file = fd)
    print(as_yaml(census), file = fd)


COMBO_PAIRS = [
    ["PD", "DC"],
    ["02.dict", "03.model"],
    ["03.model", "04.v_model"],
    ["04.v_model", "05.r_model"],
    
]
def find_combos(dict_names):
    combos = []
    for name1 in dict_names:
        for name2 in dict_names:
            if name1 == name2:
                continue
            for cpair in COMBO_PAIRS:
                word1 = cpair[0]
                word2 = cpair[1]
                if not word1 in name1:
                    continue
                if name1.replace(word1, word2) == name2:
                    combos.append([name1, name2])
                if name1.replace(".tidy", "") == name2:
                    combos.append([name1, name2])
    return combos


def compare_dicts(base_path, model_name, result_suffix ="90_census.txt"):
    output_path = f"{base_path}/{model_name}_{result_suffix}.txt"
    fd = open(output_path, mode="w", encoding="utf-8")
    dict_paths = glob_files(f"{base_path}/*dict*.yaml", f"{base_path}/*model*.yaml")
    dict_paths = list(set(dict_paths))
    dict_paths.sort()
    print(dict_paths,file = fd)
    
    dict_names = [os.path.basename(p) for p in dict_paths]
    print("Dict names are: ", dict_names)
    
    combos = find_combos(dict_names)
    print("All combos are:")
    for combo in combos:
        print(combo)
    for combo in combos:
        print(f"Combo is: {combo}")
    
        # short_pieces = {}
        pieces = {}
        for dict_name in combo:
            dict_path = f"{base_path}/{dict_name}"
            print("Including: ", dict_name)
            print("Including: ", dict_name, file = fd)
            the_dict = read_yaml_file(dict_path)
            
            path_counts = count_key_paths(the_dict)
            pieces[dict_name] = path_counts
            # show_census(fd, dict_name + " PATHS", path_counts)

        merger = merge_counts(pieces)
        # show_census(fd, f"Merged results for {pieces.keys()}", merger)
        
        merger = dict(sorted(merger.items()))

        trimmed_merger = {}
        for k, v in merger.items():
            if v.get("All", None):
                continue
            trimmed_merger[k] = v
        show_census(fd, f"Trimmed Merged  for {pieces.keys()}- 'All' cells deleted", trimmed_merger)

    
    fd.close()



if __name__ == "__main__":
    model_name = "Literate"
    
    # compare .dict.yaml to .model.yaml
    results_path  = f"ldm/ldm_models/{model_name}/{model_name}_results"
    

    compare_dicts(results_path, model_name)

    