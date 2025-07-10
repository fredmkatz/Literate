
import yaml
import json
from pathlib import Path
from typing import Union

from deepdiff import DeepDiff

from utils.util_json import tidy_dict, write_yaml, read_yaml_file,  write_json #, read_json
from utils.util_pydantic import TYPE_REGISTRY


def object_from_typed_dict(data: dict):
    """Reconstruct a PydanticMixin-derived object from a _type-tagged dict."""
    if isinstance(data, dict) and "_type" in data:
        cls = TYPE_REGISTRY.get(data["_type"])
        if cls:
            return cls.from_typed_dict(data)
    elif isinstance(data, list):
        return [object_from_typed_dict(item) for item in data]
    return data


class TypedDict(dict):
    """Wraps a _type-tagged dict (usually from a PydanticMixin object).
    Ensures that the dict is:
      - cleaned (no None, [], {}, or "")
      - serializable
      - round-trippable via .to_object()
    """

    def __init__(self, source: Union[dict, 'PydanticMixin', Path, str], tidy=True, warnings=False):
        if isinstance(source, Path) or (isinstance(source, str) and source.endswith(('.yaml', '.yml'))):
            data = read_yaml_file(source)
        elif isinstance(source, str) and source.endswith('.json'):
            data = read_yaml_file(source) # awaiting json reader
        elif hasattr(source, "to_typed_dict"):
            data = source.to_typed_dict()
        elif isinstance(source, dict):
            data = source
        else:
            raise TypeError("Expected a PydanticMixin, dict, or file path")

        if tidy:
            data = tidy_dict(data, warnings=warnings)

        super().__init__(data)

    def save_as(self, filepath: Union[str, Path]):
        """Save to a YAML file."""
        if filepath.endswith(".yaml"):
            write_yaml(dict(self), filepath)
        elif filepath.endswith(".json"):
            write_json(self, filepath)

    def to_object(self):
        """Recreate the object using _type-dispatch."""
        return object_from_typed_dict(self)

    

    def diff(self, other, **kwargs):
        """Return a deep diff between self and another TypedDict or dict."""
        if isinstance(other, TypedDict):
            other = dict(other)
        return DeepDiff(dict(self), other, **kwargs)

    def __str__(self):
        dd = self.diff({})
        return dd.pretty() if hasattr(dd, 'pretty') else super().__str__()

    def __repr__(self):
        return self.to_yaml()


    def to_yaml(self):
        return yaml.dump(dict(self), sort_keys=False)

    def to_json(self, **kwargs):
        return json.dumps(self, indent=2, sort_keys=True, **kwargs)

    def __repr__(self):
        return self.to_yaml()
