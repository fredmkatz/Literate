"""
Grammar generator for Presentable Object Models.

This module provides classes for generating Lark grammars from dataclass-based
model definitions, with support for inheritance, templates, and redefined types.
"""

import inspect
import re
import json
import sys
from dataclasses import is_dataclass, fields
import pprint
import inspect

from typing import (
    Dict,
    List,
    Set,
    Any,
    Optional,
    Type,
    Union,
    get_type_hints,
    get_origin,
    get_args,
)
from utils_pom.util_flogging import flogger, trace_decorator, trace_method
from utils_pom.util_json_pom import as_json, clean_dict
from class_casing import UpperCamel, LowerCamel, NTCase, UpperSnake
from class_field_type import FieldType
from class_rules import Rule, DisjunctiveRule, RuleComment
from class_field_type import field_terminals, to_terminal_name
from class_templates import PomTemplate
from class_pom_token import PresentableToken
from pom_config import PomConfig
from utils_pom.util_fmk_pom import write_yaml

from pom_config import primitive_terminals, pmark_named

TerminalCase = UpperSnake
Clause = str
Phrase = str

# Make the generator compatible with the Grammar base class if available
try:
    from class_grammar import Grammar

    grammar_base = Grammar
except ImportError:
    # Fallback to a simple base class
    class Grammar:
        def __init__(self, name="Grammar"):
            self.name = name
            self._lark_grammar = ""

    grammar_base = Grammar


def print_meta_info(x):
    print(x.__module__, x.__args__, x.__origin__)

def terminal_name(class_name :str) ->str:
    snake_name = UpperSnake(f"{class_name}_Q")
    return str(snake_name)


def literal_field_name(field_name: str) -> str:    
    snake_name = UpperSnake(f"{field_name}_QF")
    return str(snake_name)
    

class PomGrammarGenerator(grammar_base):
    """
    Grammar generator for Presentable Object Models.
    Creates Lark grammar from dataclass definitions.
    """

    def __init__(self, pom_config: PomConfig, name="PresentableGrammar"):
        """
        Initialize the grammar generator.

        Args:
            pom_config: Pom Configuration for grammar generation. Contains all metadata
            name: Name of the grammar
        """
        super().__init__(name)
        self.pom_config = pom_config
        self.pom_meta = pom_config.pom_meta
        
        print("Config is ", json.dumps(clean_dict(pom_config._config_params), indent=2))
        self.processed_classes = set()
        self.class_list = []
        self.class_hierarchy = {}
        self.rules = List[Union[str, Rule]]
        self.terminals = set()
        self.field_name_literals = set()
        self.templates: Dict[str, Union[PomTemplate, str]] = {}

        self.templates2 = {}

    def generate_grammar(self, model_module, model_name, format_name) -> str:
        """
        Generate a complete Lark grammar for the given model module.

        Args:
            model_module: Module containing dataclass definitions

        Returns:
            Complete Lark grammar as a string
        """
        flogger.infof(f"Generating grammar for model module {model_module.__name__}")
        # Reset state
        self.processed_classes.clear()
        self.class_hierarchy.clear()
        # self.rules.clear()
        self.rules = []
        self.terminals.clear()

        # Analyze the model
        classes = self._find_model_classes(model_module)

        self.pom_meta.gather_live_metadata(model_module, model_name, format_name, classes)
        self.class_hierarchy = self._derive_class_hierarchy(classes)
        # Process classes in a suitable order
        self._gen_all_class_rules()

        # Generate grammar components
        grammar_text = self._generate_grammar_text()

        # Store the generated grammar
        self._lark_grammar = grammar_text

        return grammar_text


    @trace_method
    def _find_model_classes(self, model_module) -> Dict:
        """
        Analyze the model to build class hierarchy and identify complex types.

        Args:
            model_module: Module containing dataclass definitions
        """
        # Find all dataclasses in the module

        # Check for model imports
        model_import_names = []
        if hasattr(model_module, "__model_imports__"):
            model_imports = model_module.__model_imports__
            flogger.infof(f"Found model_imports = {model_imports}")
            # Extract the class names from the imports
            model_import_names = [imp.__name__ for imp in model_imports]
            flogger.infof(f"Import class names: {model_import_names}")
        else:
            flogger.infof("No model_imports found")

        # Add classes from the model module itself
        # todo: This is counting on dataclass to determine whether a class should be included
        # but classes imported - or just pres ent - might be dataclasses too
        classes = {}

        # print("vars():")
        varsdict = vars(model_module)

        for name, obj in varsdict.items():
            if inspect.isclass(obj) and is_dataclass(obj):
                # Include if it's defined in the model module itself
                if obj.__module__ == model_module.__name__:
                    classes[name] = obj
                    self.class_list.append(name)
                # Or if its name matches an imported class name
                elif name in model_import_names:
                    classes[name] = obj
                    self.class_list.append(name)
                else:
                    pass
            else:
                pass
                # flogger.infof(f"Inspected: Ignoring non-class {name}")

        # print(f"All classes: {len(classes)}\n {classes.keys()}")
        return classes

    @trace_method
    def _derive_class_hierarchy(self, classes: Dict) -> Dict:

        # Build class hierarchy
        for name, cls in classes.items():
            # Get direct base classes
            bases = [
                base.__name__
                for base in cls.__bases__
                if base.__name__ in classes and base.__name__ != "object"
            ]

            # Create entry for this class
            self.class_hierarchy[name] = {
                "class": cls,
                "bases": bases,
                "subtypes": [],
                "attributes": {},
            }

        # Add subtype references
        for name, info in self.class_hierarchy.items():
            for base in info["bases"]:
                if base in self.class_hierarchy:
                    self.class_hierarchy[base]["subtypes"].append(name)

        return self.class_hierarchy

    def _gen_all_class_rules(self):
        """
        Process classes in an order that respects dependencies.
        Generate rules for each class.
        """
        # Process base classes first
        print("Starting class rules")
        print(self.pom_meta.resolved)


        for class_name, info in self.class_hierarchy.items():

            self._gen_rules_for_class(class_name, info["class"])

    def _generate_grammar_text(self):
        """Generate the complete grammar text."""
        grammar_parts = []

        # Add header
        grammar_parts.append("// Generated Lark grammar for Presentable Object Model")
        grammar_parts.append(f"// Generator: {self.__class__.__name__}")
        grammar_parts.append(f"// Model: {self.pom_config.model_name}")
        grammar_parts.append(f"// Format: {self.pom_config.format_name}")
        grammar_parts.append("")

        # Add start rule
        root_classes = [
            name for name, info in self.class_hierarchy.items() if not info["bases"]
        ]
        if root_classes:
            root_classes = [str(NTCase(name)) for name in root_classes]
            starter_rule = DisjunctiveRule("start", root_classes)
            grammar_parts.append(str(starter_rule))

            start_rule2 = Rule("starter0", "start+\t// For any number of any NT")
            grammar_parts.append(str(start_rule2))
            grammar_parts.append("")

        # Add all rules
        rule_strings = [str(r) for r in self.rules]
        grammar_parts.extend(rule_strings)
        grammar_parts.append("")

        # Add all terminals
        grammar_parts.append("// ===== Terminal definitions =====")
        grammar_parts.append("// ===== Field name literals =====")
        for qf_name in sorted(self.field_name_literals):
            literal_name = qf_name.replace("_QF", "").lower()
            grammar_parts.append(f"{qf_name}: \"{literal_name}\"")

        grammar_parts.append("")
        grammar_parts.append("// ===== Named Punctuation =====")
        for name, value in pmark_named.items():
            # flogger.infof(f"Pmark named: {name} = {value}")
            # if name in self.terminals or name in field_terminals or name == "NEWLINE":
            #     # flogger.infof(f"Pmark named: {name} = {value} is in terminals")

                grammar_parts.append(f"{name}: \"{value}\"")

        grammar_parts.append("")
        grammar_parts.append("// ===== Tokens =====")
        # Field name terminals
        case_insensitive = (
            "i" if not self.pom_config.get("case_sensitive", False) else ""
        )
        for terminal in sorted(self.terminals.union(field_terminals)):
            if terminal not in pmark_named and terminal not in {
                "STRING",
                "NUMBER",
                "BOOLEAN",
                "NEWLINE",
                "INDENT",
                "DEDENT",
            }:
                # Allow for case insensitive keywords
                # Also replace '_" with optional space pattern
                terminal1 = re.sub("_Q$", "", terminal)

                terminal_pattern = terminal1.replace("_", "\\s?").lower()
                
                grammar_parts.append(
                    f'{terminal}: "{terminal_pattern}"{case_insensitive}'
                )

        # Standard value types
        grammar_parts.append("")
        grammar_parts.append("// ===== Value types =====")
        for symbol, pattern in primitive_terminals.items():
            grammar_parts.append(f"{symbol}: {pattern}")
        grammar_parts.append("")

        # Add whitespace handling

        grammar_parts.append("// Whitespace handling")
        grammar_parts.append("WHITESPACE: /[ \\t\\n\\r]+/")
        grammar_parts.append('COMMENT: "//" /[^\\n]*/ "\\n"')
        grammar_parts.append("%ignore WHITESPACE")
        grammar_parts.append("%ignore COMMENT")

        print("Field terminals: ", field_terminals)
        print("Self terminals: ", self.terminals)
        return "\n".join(grammar_parts)

    @trace_method
    def _gen_rules_for_class(self, class_name, cls):
        """
        Generate grammar rules for a specific class.

        Args:
            class_name: Name of the class
            cls: Class object
        """
        # todo: is this check necessary??
        if class_name in self.processed_classes:
            print(f"Skipping processed class: {class_name}")
            return

        self.processed_classes.add(class_name)

        self.rules.append("")

        self.rules.append(f"//          ========== {UpperCamel(class_name)} ==========")

        # Get class metadata (from both in-code Meta and external config)
        class_meta = self.pom_meta.resolved.get_class_metadata_with_defaults(class_name)

        # Check if this is a presentable token
        if issubclass(cls, PresentableToken):
            # This is a token class, generate a simple rule

            # Generate a simple token rule
            rule_name = str(NTCase(class_name))
            token_pattern = cls.token_pattern()  # gets message? shown
            # token_pattern = cls.token_pattern_str # Works. gets the pattern from the class
            flogger.infof(f"Token pattern: {token_pattern}")
            self.rules.append(Rule(rule_name, token_pattern))
            return

        full_template_clause = None
        header_clause = None
        hierarchy_clause = None
        field_clauses_name = None
        clause_rule = None
        fields_needing_rules = set()

        # Generate the type hierarchy rule
        hierarchy_clause = self._generate_type_hierarchy_clause(class_name)

        # Check if this is an abstract class that shouldn't generate direct rules
        if _is_abstract_class(cls, class_name):
            flogger.infof(f"Class {class_name} is abstract, skipping rule generation")
            # Only generate type hierarchy rule
        else:
            
            flogger.infof(
                f"Class {class_name} is not abstract, generating own rule with clauses"
            )

            fields_needing_rules = set()


            # if the class has a template, just use that
            full_template = class_meta.get("template")
            if full_template:
                pom_full_template = PomTemplate(full_template)
                flogger.infof(f"Full template is {full_template}")
                full_template_clause = self._gen_full_class_by_template(class_name, pom_full_template)
                fields_needing_rules = pom_full_template.find_fields()

            else:

                # Generate the header rule if template exists
                header_clause = ""
                header_template = class_meta.get("header")
                if header_template:
                    # flogger.infof(f"Header template is {header_template}")
                    header_clause = self._gen_class_header(
                        class_name, PomTemplate(header_template)
                    )
                    # flogger.infof(f"Header clause is {header_clause}")

                    # Fields in the header have non terminal ClassName.FieldName_value
                    # and need corresponding rules.  So get a list of those fields to
                    # pass to gen_field_clauses()
                    fields_needing_rules = PomTemplate(header_template).find_fields()
                    # flogger.infof("header fields are: {haeder_fields}")

                # Generate field clause rules
                (field_clauses, field_value_rules) = self._gen_field_clauses(
                    class_name, cls, fields_needing_rules
                )
                body_clauses = "\n\t|\t".join(field_clauses)
                field_clauses_name = str(NTCase(class_name)) + "_clause"
                clause_rule = Rule(field_clauses_name, body_clauses)
                self.rules.append(clause_rule)
        
        # So. might have:
        # - a header_clause
        # - hierarchy_clause
        # - full_template_clause
        # - field_clauses_name for needed clauses
        
        disjuncts = []
        if hierarchy_clause:
            disjuncts.append(hierarchy_clause)
        if full_template_clause:
            disjuncts.append(full_template_clause)
        
        if header_clause and field_clauses_name:
            disjuncts.append(header_clause + "  " + "(" + field_clauses_name + ")+" )    
        elif header_clause:
            disjuncts.append(header_clause)
        elif field_clauses_name:
            disjuncts.append("( " + field_clauses_name + " )+")
        
            
        rule_body = "\n\t|\t".join(disjuncts)
              
        full_class_rule = Rule(str(NTCase(class_name)), rule_body)
        self.rules.append(full_class_rule)

        if fields_needing_rules:
            self.rules.append("")
            self.rules.append(f"//  ... value rules for {NTCase(class_name)}  ...")
            ## add the value rules
            (field_clauses, field_value_rules) = self._gen_field_clauses(
                class_name, cls, fields_needing_rules
            )

            for v in field_value_rules:
                self.rules.append(v)
                # self.rule_names.add(rule_name) # for now, this is done on generation

            # Add empty line for readability
            self.rules.append("")

    # @trace_method
    def _gen_class_header(self, class_name, template: PomTemplate) -> Clause:
        """
        Generate a header rule for a class based on a template.

        Args:
            class_name: Name of the class
            cls: Class object
            template: Header template
        """
        # Convert template to grammar rule
        rule_parts = template.to_grammar_parts(class_name)
        flogger.infof(f"rule parts are: {rule_parts}")
        # Create the header clause
        header_clause = " ".join(rule_parts)
        return header_clause

    @trace_method
    def _gen_full_class_by_template(self, class_name, template: PomTemplate) -> Rule:
        """
        Generate a header rule for a class based on a template.

        Args:
            class_name: Name of the class
            template: full template for class
        """
        # Convert template to grammar rule
        rule_parts = template.to_grammar_parts(class_name)
        flogger.infof(f"rule parts are: {rule_parts}")
        # Create the header clause
        full_rhs = " ".join(rule_parts)
        return full_rhs

    @trace_method
    def _gen_field_clauses(
        self, class_name, cls, header_fields: Set[str]
    ) -> tuple[List[str], List[Rule]]:
        """
        Generate field clause rules for a class, handling inheritance and specialization.

        Args:
            class_name: Name of the class
            cls: Class object
        """
        # Get redefined fields (fields redefined in this class)

        # Note: even though these are all found in fields(cls), this might be useful
        # for cheching Metadata for presentable attributes. So saving the call
        # redefined_fields = self._get_redefined_fields(cls)

        # Track processed fields to avoid duplicates
        processed_fields = set()
        field_clauses = []
        value_rules = []

        # Process fields defined for this class.
        # note: this will include inherited fields, whether they are redefined for the class or not
        # If a field is redefined, it will appear in fields() with the redefined type

        for field_obj in fields(cls):
            # Skip private fields
            if field_obj.name.startswith("_"):
                continue

            # Generate field clause and value rules
            # flogger.infof(
            #     f"... direct field of {class_name} - {field_obj.name},  {field_obj.type}"
            # )
            # flogger.infof(f"...   Field object: {field_obj}")
            (field_clause, value_rule) = self._generate_field_rules(
                class_name, field_obj.name, field_obj
            )
            field_clauses.append(field_clause)
            if field_obj.name in header_fields:
                value_rules.append(value_rule)
            processed_fields.add(field_obj.name)

        return (field_clauses, value_rules)

    @trace_method
    def _get_redefined_fields(self, cls):
        """
        Get fields that are redefined  in this class.
        Specifically, fields that are redefined in this class with a different type.

        Args:
            cls: Class to analyze

        Returns:
            Set of field names that are redefined
        """
        redefined = set()

        # Get base classes
        bases = [
            base
            for base in cls.__bases__
            if is_dataclass(base) and base.__name__ in self.class_hierarchy
        ]

        # Get fields in this class
        cls_fields = {f.name: f.type for f in fields(cls)}

        # Check each base class
        for base in bases:
            base_fields = {f.name: f.type for f in fields(base)}

            # Find fields with the same name but different types
            for name, type_hint in cls_fields.items():
                if name in base_fields and type_hint != base_fields[name]:
                    redefined.add(name)

        return redefined

    # @trace_method
    def _generate_field_rules(
        self, class_name, field_name, field_obj
    ) -> tuple[str, str]:
        """
        Generate rules for a field clause and value.

        Args:
            class_name: Name of the class
            field_name: Name of the field
            field_obj: Field object
        """

        # Get field type and metadata
        field_type = field_obj.type

        fieldType = FieldType.create(field_type)
        # flogger.infof(
        #     f"Field name: {field_name}, type(FieldType): {type(fieldType)}, field type: {fieldType}"
        # )

        # Generate field clause rule
        field_clause_rule = self._generate_field_clause(
            class_name, field_name, field_obj, fieldType
        )

        # Generate field value rule based on type
        field_value_rule = self._generate_field_value_rule(
            class_name, field_name, field_obj, fieldType
        )
        return (field_clause_rule, field_value_rule)

    @trace_method
    def _generate_field_clause(
        self, class_name, field_name, field_obj, fieldType
    ) -> str:
        """
        Generate a rule for a field clause.

        Args:
            class_name: Name of the class
            field_name: Name of the field
            field_obj: Field object
        """

        # flogger.infof(f"Field name: {field_name}")
        # Get the field clause template
        
        field_meta = self.pom_meta.resolved.get_field_metadata_with_defaults(class_name, field_name, fieldType.suffix())
        flogger.infof(f"Field meta  for {class_name}.{field_name} is: {field_meta}")  
        field_clause_template = field_meta.get("field_value", "{field_name}: {field_value}")

        # flogger.infof(f"fs template found is: {field_clause_template}")

        # Get field metadata

        field_name_literal = literal_field_name(field_name)
        # Replace placeholders with actual values
        suffix = fieldType.suffix()
        rule_text = field_clause_template.replace("{field_name}", field_name_literal)

        # Note: for field level templates, they will still have just one field value, so aliasing can be used
        # for headers and other full spelling templates, we will need to create Rules like: CLASS_FIELD_VALUE : Datatype
        value_phrase = fieldType.value_phrase(field_meta)  #  Might be List[ClassName]
        node_name = f"{NTCase(class_name)}__{NTCase(field_name)}__{suffix}"
        rule_text = rule_text.replace("{field_value}", value_phrase)
        rule_text += f"\t-> {node_name}"  # alias the field value to the node name

        # Add the field name to terminals
        self.field_name_literals.add(field_name_literal)

        return rule_text

    # @trace_method
    def _generate_field_value_rule(
        self, class_name, field_name, field_obj, fieldType
    ) -> Rule:
        """
        Generate a rule for a field value based on its type.

        Args:
            class_name: Name of the class
            field_name: Name of the field
            field_obj: Field object
        """

        metadata = self.pom_meta.resolved.get_field_metadata_with_defaults(class_name, field_name, fieldType.suffix())
        # Rule name
        # flogger.infof(f"Field name: {field_name}, type(FieldType): {type(fieldType)}")
        rule_name = f"{class_name}__{LowerCamel(field_name)}__{fieldType.suffix()}"
        rule_name = f"{NTCase(class_name)}__{NTCase(field_name)}__value"

        value_phrase = fieldType.value_phrase(metadata)
        # flogger.infof(
        #     f"Field name: {field_name}, rule name: {rule_name}, value phrase: {value_phrase}"
        # )
        return Rule(rule_name, value_phrase)

    @trace_method
    def _generate_type_hierarchy_clause(self, class_name):
        """
        Generate a rule for type hierarchy (parent class with subtypes).

        Args:
            class_name: Name of the class
        """
        # Get subtypes of this class
        subtypes = self.class_hierarchy[class_name].get("subtypes", [])
        flogger.infof(f"subtypes of {class_name} are {subtypes}")
        if not subtypes:
            # No subtypes, just return
            return None

        # Convert class name to upper camel for rule naming
        rule_name = str(NTCase(class_name))

        # Create a rule that maps to any subtype (joined with |)
        subtypes_clause = " | ".join(str(NTCase(st)) for st in subtypes)
        return subtypes_clause



    def get_templates(self):
        """
        Get the templates used for rendering.

        Returns:
            Dictionary of templates, keyed by class name
        """

        # Collect header templates
        for class_name in self.class_hierarchy.keys():
            class_meta = self.pom_meta.resolved.get_class_metadata_with_defaults(class_name)

            # Add header template if available
            if "header" in class_meta and class_meta["header"]:
                header_template = PomTemplate(class_meta["header"])
                self.templates[f"{class_name}_header"] = header_template

                # convert to handlebars format
                # Note: this is a simple conversion, not a full handlebars template

                hb_template = header_template.as_handlebars()
                self.templates[f"{class_name}_header_hb"] = hb_template
                
                rule = header_template.as_rule(class_name)
                self.templates[f"{class_name}_header_rule"] = rule
                # Add the header template to the templates dictionary
                self.templates[f"{class_name}_header_z"] = "" 

            # Add full template if available
            if "template" in class_meta and class_meta["template"]:
                full_template = PomTemplate(class_meta["template"])
                self.templates[f"{class_name}_template"] = full_template
                # convert to handlebars format
                # Note: this is a simple conversion, not a full handlebars template
                self.templates[f"{class_name}_template_hb"] = (
                    full_template.as_handlebars()
                )
                self.templates[f"{class_name}_template_z"] = "" 
            # Add field templates if available
            if "field_value" in class_meta and class_meta["field_value"]:
                field_template = PomTemplate(class_meta["field_value"])
                self.templates[f"{class_name}_field"] = field_template
                # convert to handlebars format
                # Note: this is a simple conversion, not a full handlebars template
                self.templates[f"{class_name}_field_hb"] = (
                    field_template.as_handlebars()
                )
                self.templates[f"{class_name}_field_z"] = ""
           

        # Add default templates
        self.templates["default_header"] = (
            "{{name}}{{#if one_liner}} - {{one_liner}}{{/if}}"
        )
        self.templates["default_field"] = "{{name}}: {{value}}"

        return self.templates


def _is_abstract_class(cls, class_name):
    """
    Determine if a class is abstract based on its Meta definition.
    This only checks the direct Meta attribute, not inherited ones.

    Args:
        cls: The class to check
        class_name: The name of the class (for logging)

    Returns:
        bool: True if the class is marked as abstract
    """
    # Check for Meta class with is_abstract attribute
    if hasattr(cls, "Meta"):
        # Check if is_abstract is directly defined on this Meta class
        if hasattr(cls.Meta, "is_abstract"):
            return cls.Meta.is_abstract

    # Not explicitly marked as abstract
    return False
