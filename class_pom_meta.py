import os
import yaml
import json

from dataclasses import dataclass, field, fields
from typing import Dict, Any, Optional, List
import importlib.resources as pkg_resources
from dataclasses import fields, is_dataclass
from utils_pom.util_flogging import flogger, trace_decorator, trace_method
from utils_pom.util_json_pom import clean_dict, update_nested_dict
from utils_pom.util_fmk_pom import read_yaml_file, write_yaml, write_text
from class_field_type import FieldType

Class_Metas = [
    "header",
    
    "template",
    "is_abstract",
]

Field_Metas = [
    "field_value",
    "str",
    "int",
    "float",
    "bool",
    "list",

    "dict",
    "set",
    "tuple",
    "is_explicit",
    
]


@dataclass
class PomFormat():
    name: str
    _defaults: Dict

    def __init__(self, name: str, _defaults: Dict):
        """
        Initialize the PomFormat object.
        """
        self.name = name
        self._defaults = _defaults
    

dull_dict = {
    "_defaults": {
        # Class formats
        "header": None,
        "template": None,
        "is_abstract": False,

        # Common field formats
        "field_value": "{field_name}: {field_value}",
        
        # suffixes for field types
        "str": "dull_str",
        "int": "dull_int",
        "float": "dull_float",
        "bool": {
            "true": "true",
            "false": "false",
            "is_explicit": True,
        },
        
        "list": "[{element} (, {element})+]",
        "dict": "dull dict",
        "set": "{{element} (, {element})+}",
        "tuple": "[{element} (, {element})+]"
    }
}
DullFormat = PomFormat("dull", dull_dict)
def mf_path(model_name: str, format_name: str, rest: str) -> str:
    """
    Get the path to the model format file.

    Args:
        model_name: Name of the model module
        format_name: Name of the format (json, dull, etc.)

    Returns:
        Path to the model format file
    """
    return f"models/{model_name}/{model_name}_{format_name}{rest}"

NamedFormats = {
    "dull": DullFormat
}   

@dataclass
class PomDict():
    legend: List[str] = field(default_factory=list)

    
    def __init__(self, name: str, the_dict: Dict, legend: List[str] = None):
        self.name = name
        self.the_dict = the_dict
        self.legend = legend or []
        
    def __str__(self):
        full_legend = "\n".join(self.legend) if self.legend else ""
        # print("Full legend", full_legend)
        # print("Self.legend", self.legend)
        yamlstr = yaml.dump(clean_dict(self.the_dict), default_flow_style=False, sort_keys=False)
        return "## PomDict - " + self.name + ": \n" + full_legend + "\n" + yamlstr
       
    def save_to_yaml(self, yaml_path: str):
    
        """
        Save the metadata to a YAML file.

        Args:
            model_name: Name of the model module
            format_name: Name of the format (json, dull, etc.)
        """
        
        full_str = str(self)
        # print("writing to " + yaml_path)
        # print("Text is " + full_str)
        write_text(yaml_path, full_str)
        print(f"Saved metadata to {yaml_path}")
    
    def fill_in_defaults(self, target_meta:Dict , defaults: Dict, tag_filter: Dict) -> Dict:
        for def_key, def_value in defaults.items():
            if not def_key in tag_filter:
                continue
            if not target_meta.get(def_key):
                target_meta[def_key] = def_value
        return target_meta
    
    def fill_in_field_defaults(self, target_meta:Dict , defaults: Dict, field_suffix: str) -> Dict:
        for def_key, def_value in defaults.items():

            if target_meta.get(def_key):
                continue    # no need for a default, it's explicit

            if def_key == "field_value" or def_key ==  field_suffix:
                target_meta[def_key] = def_value
                
        # In any case get rid of the _suffix key
        if "_suffix" in target_meta:
            del target_meta["_suffix"]
        return target_meta

    # @trace_method
    def get_class_metadata(self, class_name: str) -> Dict[str, Any]:
        """
        Get metadata for a specific class.

        Args:
            class_name: Name of the class

        Returns:
            Dictionary of class metadata
        """
        return self.get_keyed_metadata(class_name)

    def get_class_metadata_with_defaults(self, class_name: str) -> Dict[str, Any]:
        """
        Get metadata for a specific class, including defaults.

        Args:
            class_name: Name of the class

        Returns:
            Dictionary of class metadata with defaults
        """
        class_metadata = self.get_class_metadata(class_name)
        defaults = self.get_default_metadata()
        resolved_class_meta = self.fill_in_defaults(class_metadata, defaults, Class_Metas)
        
        return resolved_class_meta

        # #
        # # Now, fill in all defaults
        # defaults = resolved_meta.get("_defaults", None)
        # if defaults:
        #     for class_name in class_names:
        #         resolved_class_meta = resolved_meta[class_name]
        #         resolved_class_meta = self.fill_in_defaults(resolved_class_meta, defaults, Class_Metas)
                
        #         field_metas = resolved_class_meta.get("_fields", None)
        #         if field_metas:
        #             for fname, fmeta in field_metas.items():
        #                 suffix = fmeta.get("_suffix", None)
        #                 resolved_field_meta = self.fill_in_field_defaults(fmeta, defaults, suffix)
        #                 field_metas[fname] = resolved_field_meta
        #         resolved_meta[class_name] = resolved_class_meta

    def get_field_metadata_with_defaults(self, class_name: str, field_name: str, suffix: str) -> Dict[str, Any]:
        """
        Get metadata for a specific field.

        Args:
            class_name: Name of the class
            field_name: Name of the field

        Returns:
            Dictionary of field metadata
        """
        field_metadata =  self.get_keyed_metadata(class_name, "_fields", field_name)
        defaults = self.get_default_metadata()

        resolved_field_meta = self.fill_in_field_defaults(field_metadata, defaults, suffix)
        return resolved_field_meta

    def get_field_metadata(self, class_name: str, field_name: str) -> Dict[str, Any]:
        """
        Get metadata for a specific field.

        Args:
            class_name: Name of the class
            field_name: Name of the field

        Returns:
            Dictionary of field metadata
        """
        field_metadata =  self.get_keyed_metadata(class_name, "_fields", field_name)
        return field_metadata

        
    # @trace_method
    def get_default_metadata(self) -> Any:

        default_metadata = self.get_keyed_metadata("_defaults")
        return default_metadata

    def get_keyed_metadata(self, *keys: str) -> Dict[str, Any]:
        """
        Get metadata for a specific key path.

        Args:
            keys: Sequence of keys to traverse

        Returns:
            Dictionary of metadata, possibly empty but never None
        """
        metadata = self.the_dict
        for key in keys:
            if key in metadata:
                metadata = metadata[key]
            else:
                return {}
        return metadata

    def get_live_metadata(self) -> Dict[str, Any]:
        """
        Get all model metadata.

        Returns:
            Complete metadata dictionary
        """
        return self.the_dict


def get_meta_attributes_with_values(cls):
    import inspect
    if hasattr(cls, "Meta"):
        # Get the attributes and their values
        meta_vars = vars(cls.Meta)
        # print(f"Meta vars for {cls.__name__} are {meta_vars}")
        goodvars =  {key: value for key, value in meta_vars.items() if  not key.startswith("__")}
        goodvars = {key: value for key, value in goodvars.items() if key != "fields" }
        return goodvars
    return {}



class PomMeta():
    def __init__(self):
        self.external = PomDict("External Meta", the_dict = {})
        self.live = PomDict("Live Meta", the_dict={})
        self.resolved = PomDict("Resolved Meta", the_dict={})

    def load_model_formats(self, model_name: str, format_name: str = None):
        """
        Load templates for a specific model and format.

        If format is specified, load from:
        - Presentable/settings/{format_name}_format.yaml
        - Presentable/models/{model_name}/{model_name}_{format_name}_format.yaml

        If format is not specified, load from:
        - Presentable/settings/default_format.yaml
        - Presentable/models/{model_name}/{model_name}_format.yaml

        Args:
            model_name: Name of the model module
            format_name: Name of the format (json, dull, etc.)
        """

        # Reset metadata before loading
        external_meta = {}
        legend = ["# From YAML files:"]

        # start with named builin formats
        if format_name in NamedFormats:
            external_meta = NamedFormats[format_name]._defaults
            legend.append(f"##\tUsing built-in format: {format_name}")

        # Determine paths to check
        paths = [
            "settings/default_format.yaml",
            f"models/{model_name}/{model_name}_format.yaml",
        ]

        if format_name:
            paths = [
                f"settings/{format_name}_format.yaml",
                f"models/{model_name}/{model_name}_{format_name}_format.yaml",
            ]

        flogger.infof(f"Loading format files from paths: {paths}")
        
        for path in paths:
            if os.path.exists(path):
                legend.append(f"## \tUsing: {path}")
            else:
                legend.append(f"## \tnot found: {path}")



        # Try to load from each path
        for yaml_path in paths:
            if os.path.exists(yaml_path):
                flogger.infof(f"Found format file: {yaml_path}")
                update_nested_dict(external_meta, read_yaml_file(yaml_path))
                flogger.infof(f"Updated metadata: {clean_dict(external_meta)}")
            else:
                flogger.infof(f"Format file not found: {yaml_path}")
        self.external = PomDict("External", external_meta, legend)
        path = mf_path(model_name, format_name, "_y_external.yaml")
        self.external.save_to_yaml(path)
        # Save the external metadata to a YAML file

        print(self.external)
    
    
    def resolve_metas(self, live_meta: PomDict, external_meta: PomDict) -> PomDict:
        live_dict = live_meta.the_dict
        external_dict = external_meta.the_dict
        
        resolved_meta = {}
        # Let live_dict drive the process since that should
        # have a complete list of classes and fields
        
        # Note a. With nested dict update, this covers all fields as well as all
        # classes
        # Note b. This first pass, just combines live and external. 
        # it does not account for default values
        # Though it does produces a resolved set of default values
        
        class_names = live_dict.keys()
        for class_name in class_names:
            live_class_meta = live_dict[class_name]
            external_class_meta = external_dict.get(class_name, {})
            resolved_class_meta = update_nested_dict(live_class_meta, external_class_meta)
            
            resolved_meta[class_name] = resolved_class_meta
        
                

        legend = []
        legend.append(f"## Resolved metadata from {live_meta.name} and {external_meta.name}")
        legend.extend(self.live.legend)

        legend.extend(self.external.legend)
        return  PomDict("Resolved", resolved_meta, legend)

        
    
    def gather_live_metadata(self, model_module, model_name, format_name, classes):
        live_meta = self.gather_live_metas(classes)
        # self.pom_config._model_metadata = live_meta
        self.live = PomDict("Live", live_meta,  legend = [f"# extracted from the {model_name} model"])
        
        path = mf_path(model_name, format_name, "_y_live.yaml")
        self.live.save_to_yaml(path)
        
        
        self.resolved  = self.resolve_metas(self.live, self.external)
        path = mf_path(model_name, format_name, "_y_resolved.yaml")
        self.resolved.save_to_yaml(path)
        print(self.resolved)
       
        

    def gather_live_metas(self, classes):
        live_meta = {}
        live_meta["_defaults"] = {}
        defaults = live_meta["_defaults"]
        defaults["header"] = "Header:  "
        defaults["field_value"] = "{name}: {value}"
        for class_name, cls in classes.items():
            class_meta = self._get_live_class_metadata(cls)

            # print(f"class meta for {class_name} is {class_meta}")

            field_metas = {}
            for field_obj in fields(cls):
                # Skip private fields
                if field_obj.name.startswith("_"):
                    continue
                field_name = field_obj.name
                field_metadata = self._get_live_field_metadata(field_obj)
                # print(f"field meta for {field_name} = {field_metadata}")
                if field_metadata.keys():
                    field_metas[field_name] = field_metadata
            if field_metas.keys():
                class_meta['_fields'] = field_metas
            if class_meta.keys():
                live_meta[class_name] = class_meta

        return live_meta
   
    # @trace_method
    def _get_live_class_metadata(self, cls):
        """
        Get metadata for a class, combining in-code Meta with external config.

        Args:
            cls: Class object
            class_name: Name of the class

        Returns:
            Dictionary of metadata
        """
        # Start with defaults
        # flogger.infof(f"Class name: {class_name}")

        metadata = {}
        class_meta = get_meta_attributes_with_values(cls)
        # print(f"\nClass meta for {cls.__name__} is {class_meta}")
        for key, value in class_meta.items():
            
            # pom_ and presentable_ are permitted in model, but discarded
            trimmed_key = key.replace("pom_", "").replace("presentable_", "")
            # print(f"Trimmed key: {trimmed_key}")
            if trimmed_key in Class_Metas:
                metadata[trimmed_key] = value
            
        metadata = clean_dict(metadata)
        return metadata

    # @trace_method
    def _get_live_field_metadata(self, field_obj):
        """
        Get metadata for a field, combining field metadata with external config.

        Args:
            field_obj: Field object
            class_name: Name of the class
            field_name: Name of the field

        Returns:
            Dictionary of metadata
        """
        
        field_type = field_obj.type

        fieldType = FieldType.create(field_type)
        

        # Start with defaults
        metadata = {
            # "_fieldType": fieldType,
            # "_field_type": field_type,
            # "_suffix": fieldType.suffix()
        }

        field_meta = field_obj.metadata if field_obj.metadata else {}
        # print(f"\nDirect Field meta for {field_obj.name} is {field_meta}")
        for key, value in field_meta.items():

            # pom_ and presentable_ are permitted in model, but discarded
            trimmed_key = key.replace("pom_", "").replace("presentable_", "")
            # print(f"Trimmed field key: {trimmed_key}")
            if trimmed_key in Field_Metas:
                # print(f"Found Trimmed key: {trimmed_key}")
                metadata[trimmed_key] = value
                

        metadata = clean_dict(metadata)
        return metadata


