import sys
import json
import jsonpickle


from deepdiff import DeepDiff
from utils.util_antlr import path_for


def deep_dive(path1, path2, diffpath):
    """
    Perform a deep dive comparison of two JSON files.
    """

    print(f"DeepDiffing {path1} and {path2}...")
    with open(path1, "r", encoding="utf-8") as f:
        json1 = json.load(f)
    with open(path2, "r", encoding="utf-8") as f:

        json2 = json.load(f)

    difference = DeepDiff(json1, json2, ignore_order=True)

    # json_pickle_output = difference.to_json_pickle()
    serialized = jsonpickle.encode(difference)
    #  print(json.dumps(json.loads(serialized), indent=2))
    with open(diffpath, "w", encoding="utf-8") as f:
        json.dump(json.loads(serialized), f, indent=2, ensure_ascii=False)

    print(f"-- Deep diff written to {diffpath}")


if __name__ == "__main__":
    grammar_name = "Markdown"
    document = "Markdown_Example"

    path1 = path_for("A", grammar_name, "outputs", document, "_04.json")
    path2 = path_for("B", grammar_name, "outputs", document, "_04.json")
    diffpath = path_for("B", grammar_name, "outputs", document, "_04b.deep_diff.txt")
    deep_dive(path1, path2, diffpath)
