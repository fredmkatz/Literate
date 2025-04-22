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
    Tuple,
    Optional,
    Type,
    Union,
    get_type_hints,
    get_origin,
    get_args,
)
from utils_pom.util_flogging import flogger, trace_decorator, trace_method
from utils_pom.util_json_pom import as_json, clean_dict
from class_casing import UpperCamel, LowerCamel, NTCase, TokenCase
from class_field_type import FieldType
from class_field_type import field_terminals, punctuation_terminals, field_name_literals
from class_templates import PomTemplate
from class_pom_token import PresentableToken, PresentableBoolean
from pom_config import PomConfig
from utils_pom.util_fmk_pom import write_yaml

from pom_config import primitive_terminals, pmark_named
from class_abstract_grammar import AbstractGrammar, AbstractSection, AbstractClause, AbstractDisjunction, AbstractRule
from utils_pom.util_fmk_pom import write_text

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
    snake_name = TokenCase(f"{class_name}_Q")
    return str(snake_name)

def terminal_class_name(class_name: str) -> str:
    return str(TokenCase(class_name))

def literal_field_name(field_name: str) -> str:    
    snake_name = TokenCase(f"{field_name}_QF")
    return str(snake_name)
    

the_class_hierarchy = {}

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
        self.class_list = []
        self.class_hierarchy = {}
        self.class_sequence = []
        self.rules = List[Union[str, AbstractRule]]
        self.templates: Dict[str, Union[PomTemplate, str]] = {}
        self.abstract_grammar = AbstractGrammar()
        ag = self.abstract_grammar
        self.abstract_intro = ag.add_section("Intro")
        self.abstract_terminals = ag.add_section("Terminals")
        self.abstract_classes = ag.add_section("Main Class Rules")
        self.abstract_epilogue = ag.add_section("Epilogue")
        self.class_clause_name = {} # maps class name to the name of the class clause rule

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
        self.class_hierarchy.clear()

        # Analyze the model
        classes = self._find_model_classes(model_module)

        self.pom_meta.gather_live_metadata(model_module, model_name, format_name, classes)
        self.class_hierarchy = self._derive_class_hierarchy(classes)
        global the_class_hierarchy
        the_class_hierarchy = self.class_hierarchy

        #   Generate the complete grammar text.
        self._generate_grammar_intro(self.abstract_intro)
        self._generate_grammar_classes(self.abstract_classes)
        
        # Needs to follow class generations, since terminal will be discovered
        self._generate_grammar_terminals(self.abstract_terminals)

        # Store the generated grammar
        self.abstract_grammar.add_chunks()
        abstract_text = self.abstract_grammar.displayed()
        self._lark_grammar = abstract_text


        return abstract_text


    # @trace_method
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

    # @trace_method
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
                "depth": -1
            }

        # Add subtype references
        for name, info in self.class_hierarchy.items():
            for base in info["bases"]:
                if base in self.class_hierarchy:
                    self.class_hierarchy[base]["subtypes"].append(name)

        # calculate depths and paths
        for class_name in self.class_hierarchy.keys():
            self.calc_class_depth(class_name)
        
        print("Class hierarchy is:", self.displayed_hierarchy())
        
        # before returning, get a sorted list of classes (by depth)
        
        # topological order
        path_dict = {name: info["path"] for name, info in self.class_hierarchy.items()}
        print(path_dict)
        classes_by_topol = sorted(self.class_hierarchy.keys(), key = lambda x: self.class_hierarchy[x]["path"])
        print (classes_by_topol)
        self.class_sequence = classes_by_topol

        return self.class_hierarchy

    def displayed_hierarchy(self)-> str:
        display = {}
        for cname, info in self.class_hierarchy.items():
            newinfo = info.copy()
            newinfo['class'] = None
            display[cname] = newinfo
        return as_json(display)
    def calc_class_depth(self, class_name: str) -> int:
        info = self.class_hierarchy[class_name]
        depth = info["depth"]
        if depth >= 0:
            return depth, info["path"]
        max_depth = 0
        class_path = None
        for base in info["bases"]:
            base_depth, base_path = self.calc_class_depth(base)
            if base_depth > max_depth:
                max_depth = base_depth
            if not class_path:
                class_path = base_path + " / " + class_name
            
        if not class_path:
            class_path = class_name
        new_depth = max_depth + 1
        info["depth"] = new_depth
        info['path'] = class_path
        return new_depth, class_path
        
    def _generate_grammar_intro(self, abstract_intro: AbstractSection):
        # Add header
        
        abstract_intro.add_comment("Generated Lark grammar for Presentable Object Model")
        abstract_intro.add_comment(f" Generator: {self.__class__.__name__}")
        abstract_intro.add_comment(f" Model: {self.pom_config.model_name}")
        abstract_intro.add_comment(f" Format: {self.pom_config.format_name}")
        abstract_intro.add_space("")


        # Add start rule
        root_classes = [
            name for name, info in self.class_hierarchy.items() if not info["bases"] and not issubclass(info['class'], PresentableToken)
        ]
        if root_classes:
            root_classes = [str(NTCase(name)) for name in root_classes]

            abstract_intro.add_disjunctive_rule("start", root_classes)
            abstract_intro.add_nt_rule("starter0", "start+\t// For any number of any NT")
            abstract_intro.add_space("")


    def _generate_grammar_terminals(self, abstract_terminals: AbstractSection):
        abstract_terminals.add_comment("===== Terminal definitions =====")

        # Add whitespace handling

        abstract_terminals.add_comment("Whitespace handling")
        abstract_terminals.add_space("%import common.WS_INLINE")
        abstract_terminals.add_space("%ignore WS_INLINE")

            
        abstract_terminals.add_comment("===== Unused Named Punctuation =====")
        for name, value in pmark_named.items():
                if not name in punctuation_terminals:
                    abstract_terminals.add_t_rule(name, f"\"{value}\"")


        abstract_terminals.add_comment("===== Named Punctuation In Use =====")

        for name in  punctuation_terminals:
            value = pmark_named[name]
            abstract_terminals.add_t_rule(name, f"\"{value}\"")


        abstract_terminals.add_comment("===== Tokens =====")
        abstract_terminals.add_comment("===== Field name literals =====")

        case_insensitive = (
            "i" if not self.pom_config.get("case_sensitive", False) else ""
        )
        print(f"case_insensitive is {case_insensitive}!")

        # ToDo.  Not catching all punctuation and terminals used
        # missing neste val
        # ue phrase templates, such as list: element (COMMA element)
        # Add all terminals

        for qf_name in sorted(field_name_literals):
            literal_name = qf_name.replace("_QF", "").lower()
            pattern = literal_name.replace("_", "\\s*")
            abstract_terminals.add_t_rule(f"{qf_name}", f"/{pattern}/{case_insensitive}", priority=9)

        # Field name terminals
        for terminal in sorted(field_terminals):
            if terminal not in pmark_named and terminal not in {
                "STRING",
                "NUMBER",
                "BOOLEAN",
                "INDENT",
                "DEDENT",
            }:
                # Allow for case insensitive keywords
                # Also replace '_" with optional space pattern
                terminal1 = re.sub("_Q$", "", terminal)

                terminal_pattern = terminal1.replace("_", "\\s?").lower()
                
                abstract_terminals.add_t_rule(terminal,  f"\"{terminal_pattern}\"{case_insensitive}", priority = 8)

        self._generate_grammar_class_tokens(abstract_terminals)
        # Standard value types
    
        abstract_terminals.add_comment("===== Primitive types =====")

        for symbol, pattern in primitive_terminals.items():
            abstract_terminals.add_t_rule(symbol, pattern)
        abstract_terminals.add_space("")

        

        print("Field terminals: ", field_terminals)
        print("Punctuation used: ", punctuation_terminals)
    
    def _generate_grammar_class_tokens(self, abstract_terminals):

        abstract_terminals.add_comment("===== Presentable Boolean Tokens =====")
        
        # First, produce the rules for Booleans - or other literal tokens
        for class_name, info in self.class_hierarchy.items():
            cls = info["class"]
            # Check if this is a presentable token
            if issubclass(cls, PresentableBoolean):
                # This is a token class, generate a simple rule
\
                # Generate a simple token rule
                token_pattern = cls.token_pattern()  # gets message? shown
                # token_pattern = cls.token_pattern_str # Works. gets the pattern from the class
                flogger.infof(f"Token pattern: {token_pattern}")
                
                abstract_terminals.add_t_rule(class_name,token_pattern )

        abstract_terminals.add_comment("===== Presentable Pattern Tokens =====")
        # Then, do the pattern tokens
        for class_name, info in self.class_hierarchy.items():
            cls = info["class"]
            # Check if this is a presentable token
            if not issubclass(cls, PresentableToken):
                continue
            if issubclass(cls, PresentableBoolean):
                continue
            
            # This is a token class, generate a simple rule
\
            # Generate a simple token rule
            token_pattern = cls.token_pattern()  # gets message? shown
            # token_pattern = cls.token_pattern_str # Works. gets the pattern from the class
            # flogger.infof(f"Token pattern: {token_pattern}")
            
            # For pattern tokens:
            # - If this class inherits from another - and has the same pattern,
            #  - then just use the rule THIS_TOKEN: PARENT_TOKEN, instead of
            #       repeating the pattern
            bases = info.get("bases", None)
            # flogger.infof(f"Bases of Presentable token {class_name} are {bases}")
            if len(bases) == 1:
                base_cls = self.class_hierarchy[bases[0]]['class']
                base_name = bases[0]
                # flogger.infof(f".. and base cls is {base_cls}")
                base_pattern = base_cls.token_pattern()
                # flogger.infof(f".. and base pattern is {base_pattern}")
                if base_pattern  == token_pattern:
                    abstract_terminals.add_t_rule(class_name, terminal_class_name(base_name) )
                    continue
            # if it gets difficult, use the class's own token pattern
            abstract_terminals.add_t_rule(class_name,token_pattern )



        
    def _generate_grammar_classes(self, abstract_classes: AbstractSection):
        """
        Process classes in an order that respects dependencies.
        Generate rules for each class.
        """
        # Process base classes first
        print("Starting class rules")
        print(self.pom_meta.resolved)

        for class_name in self.class_sequence:
            info = self.class_hierarchy[class_name]

        # for class_name, info in self.class_hierarchy.items():

            self._gen_rules_for_class(abstract_classes, class_name, info["class"])


    # @trace_method
    def _gen_rules_for_class(self, abstract_classes: AbstractSection,  class_name, cls):
        """
        Generate grammar rules for a specific class.

        Args:
            class_name: Name of the class
            cls: Class object
        """


        # Check if this is a presentable token. These are in the Terminals section
        if issubclass(cls, PresentableToken):
            return

        # Get class metadata (from both in-code Meta and external config)
        class_meta = self.pom_meta.resolved.get_class_metadata_with_defaults(class_name)
        abstract_classes.add_comment(f"          ========== {UpperCamel(class_name)} ==========")

        full_template_clause = None
        header_clause = None
        hierarchy_clause = None
        class_clauses_name = None
        clause_rule = None
        fields_needing_rules = set()

        # Generate the type hierarchy rule
        hierarchy_clause = self._generate_type_hierarchy_clause(class_name)
        depth = the_class_hierarchy[class_name].get("depth", -1)

        # Note. generate headers and field clauses for abstract classes - to be "inherited"
        # by the comcrete classes
            
        flogger.infof(
            f"Class {class_name} is not abstract, generating own rule with clauses"
        )

        fields_needing_rules = set()
        # Get redefined fields (fields redefined in this class)

        # Note: even though these are all found in fields(cls), this might be useful
        # for cheching Metadata for presentable attributes. So saving the call
        (newfields, redefined_fields, inherited, inherits_from) = self._assess_fields(cls)


        # if the class has a template, just use that
        full_template = class_meta.get("template")
        if full_template:
            pom_full_template = PomTemplate(full_template)
            flogger.infof(f"Full template is {full_template}")
            full_template_clause = self._gen_full_class_by_template(class_name, pom_full_template)
            fields_needing_rules = pom_full_template.find_fields()

        else:

            # Generate the header rule if template exists
            header_rule = ""
            header_clause = ""
            header_template = class_meta.get("header")
            if header_template:
                flogger.infof(f"Header template is {header_template}")
                header_clause = self._gen_class_header(
                    class_name, PomTemplate(header_template)
                )
                flogger.infof(f"Header clause is {header_clause}")

                # Fields in the header have non terminal ClassName.FieldName_value
                # and need corresponding rules.  So get a list of those fields to
                # pass to gen_field_clauses()
                fields_needing_rules = PomTemplate(header_template).find_fields()
                # flogger.infof("header fields are: {haeder_fields}")
                header_clause_name = str(NTCase(class_name)) + "_header"
                header_rule = abstract_classes.add_nt_rule2(header_clause_name, header_clause)
                flogger.infof(f"Header clause is: {header_clause}")
                flogger.infof(f"Header rule is: {header_rule}")
                header_clause = header_clause_name
            
            
            # inherited class clauses
            ancestor_clauses = list(AbstractClause(self.class_clause_name[base]) for base in inherits_from)
            if ancestor_clauses:
                flogger.infof(f"Ancestor clauses for {class_name} are {ancestor_clauses}")
            # Generate field clause rules
            field_clauses = self._gen_field_clauses(class_name, cls, inherited)
            if field_clauses:
                flogger.infof(f"Field clauses for {class_name} are {field_clauses}")

            class_clauses_name = None

            # The class only needs a CLASS_clause rule if it has uninherited fields
            # or more than one parent
            if field_clauses or len(ancestor_clauses) > 1:
                class_clauses = ancestor_clauses + field_clauses
                
                body_clause = AbstractDisjunction(class_clauses)
                print("body_clause is ", repr(body_clause))
                class_clauses_name = str(NTCase(class_name)) + "_clause"
                abstract_classes.add_nt_rule2(class_clauses_name, body_clause)
            elif ancestor_clauses:
                class_clauses_name = str(ancestor_clauses[0])
                
            
            self.class_clause_name[class_name] = class_clauses_name
        
        # So. might have:
        # - a header_clause
        # - hierarchy_clause
        # - full_template_clause
        # - class_clauses_name for needed clauses
        
        disjuncts = []
        if hierarchy_clause:
            disjuncts.append(hierarchy_clause)
        if full_template_clause:
            disjuncts.append(full_template_clause)
        
        if header_clause and class_clauses_name:
            disjuncts.append(AbstractClause(str(header_clause) + "  " + "(" + class_clauses_name + ")*") )    
        elif header_clause:
            disjuncts.append(header_clause)
        elif class_clauses_name:
            disjuncts.append("( " + class_clauses_name + " )+")
        
            
              
        abstract_classes.add_nt_rule2(class_name, AbstractDisjunction(disjuncts), priority=depth + 1)

        if fields_needing_rules:
            abstract_classes.add_comment(f"  ... value rules for {NTCase(class_name)}  ...")
            ## add the value rules
            field_value_rules = self._gen_field_value_rules(
                class_name, cls, fields_needing_rules
            )

            for v in field_value_rules:
                print(f"Value rule is: {v}")
                abstract_classes.add_rule2(v)
                print(f"... added as {v}")

            # Add empty line for readability
            abstract_classes.add_space("")


    # @trace_method
    def _gen_class_header(self, class_name, template: PomTemplate) -> AbstractClause:
        """
        Generate a header rule for a class based on a template.

        Args:
            class_name: Name of the class
            cls: Class object
            template: Header template
        """
        # Convert template to grammar rule
        
        header_clause = template.to_fragment(class_name)
        return AbstractClause(header_clause)

    # @trace_method
    def _gen_full_class_by_template(self, class_name, template: PomTemplate) -> AbstractClause:
        """
        Generate a header rule for a class based on a template.

        Args:
            class_name: Name of the class
            template: full template for class
        """
        # Convert template to grammar rule
        
        full_rhs = template.to_fragment(class_name)
        return AbstractClause(full_rhs)

    # @trace_method
    def _gen_field_clauses(
        self, class_name, cls, inherited: List[str]) -> List[AbstractClause]:
        """
        Generate field clause rules for a class, handling inheritance and specialization.

        Args:
            class_name: Name of the class
            cls: Class object
            inherited: names of fields that are inherited w/o redefinition of type or template
        """

        field_clauses = []

        # Process fields defined for this class.
        # note: this will include inherited fields, whether they are redefined for the class or not
        # If a field is redefined, it will appear in fields() with the redefined type

        for field_obj in fields(cls):
            # Skip private fields
            if field_obj.name.startswith("_"):
                continue
            
            # Fields inherited (and not redefined) need not be repeated.
            # Cloauses for those fields are included by  including PARENT_clauses
            if field_obj.name in inherited:
                continue
            # Generate field clause and value rules
            # flogger.infof(
            #     f"... direct field of {class_name} - {field_obj.name},  {field_obj.type}"
            # )
            # flogger.infof(f"...   Field object: {field_obj}")
            field_clause = self._generate_field_clause(
                class_name, field_obj.name, field_obj
            )
            field_clauses.append(field_clause)
            

        return field_clauses
    # @trace_method
    def _gen_field_value_rules(
        self, class_name, cls, header_fields: Set[str]) -> List[AbstractRule]:
        """
        Generate field clause rules for a class, handling inheritance and specialization.

        Args:
            class_name: Name of the class
            cls: Class object
        """    

        value_rules = []

        # Process fields defined for this class.
        # note: this will include inherited fields, whether they are redefined for the class or not
        # If a field is redefined, it will appear in fields() with the redefined type

        for field_obj in fields(cls):
            # Skip private fields
            if field_obj.name.startswith("_"):
                continue
            
            if not field_obj.name in header_fields:
                continue

            # Generate field  value rule
            # flogger.infof(
            #     f"... direct field of {class_name} - {field_obj.name},  {field_obj.type}"
            # )
            # flogger.infof(f"...   Field object: {field_obj}")

            value_rule = self._generate_field_value_rule(
                class_name, field_obj.name, field_obj
            )
            value_rules.append(value_rule)

        return value_rules

    # @trace_method
    def _assess_fields(self, cls) -> Tuple[Set[str], Set[str], Set[str], Set[str]]:
        """
        Get fields that are redefined  in this class.
        Specifically, fields that are redefined in this class with a different type.

        Args:
            cls: Class to analyze

        Returns:
            [New Fields, Redefined Fields, InheritedFields. Inherits from]
        """
        redefined = set()
        newfields = set()
        inherited = set()
        inherits_from = set()

        # Get base classes
        bases = [
            base
            for base in cls.__bases__
            if is_dataclass(base) and base.__name__ in self.class_hierarchy
        ]

        # Get fields in this class
        cls_fields = {f.name: f.type for f in fields(cls)}
        
        for fname, ftype in cls_fields.items():
    
            # Check each base class
            resolved = False
            for base in bases:
                base_fields = {f.name: f.type for f in fields(base)}
                for basename, basetype in base_fields.items():
                    if fname == basename:   # either inherited or redefined
                        if ftype == basetype:
                            inherited.add(fname)
                            inherits_from.add(base.__name__)
                        else:
                            redefined.add(fname)
                        resolved = True
                        break   # no need to check other fields in this base
                if resolved: # ie found a redefined or inherited field
                    break   # no need to check other bases
            #
            # Gone through all bases, all fields.
            if not resolved:
                newfields.add(fname)
        
        # flogger.infof(f"Assessed: {cls}...")
        # flogger.infof(f"... New fields for {cls} are {newfields}")
        # flogger.infof(f"... Redefined fields for {cls} are {redefined}")
        # flogger.infof(f"... Inherited fields for {cls} are {inherited}")
        # flogger.infof(f"... Inherits from for {cls} are {inherits_from}")
        return (newfields, redefined, inherited, inherits_from)

    # @trace_method
    def _generate_field_clause(
        self, class_name, field_name, field_obj) -> AbstractClause:
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


        # flogger.infof(f"Field name: {field_name}")
        # Get the field clause template
        
        field_meta = self.pom_meta.resolved.get_field_metadata_with_defaults(class_name, field_name, fieldType.suffix())
        # flogger.infof(f"Field meta  for {class_name}.{field_name} is: {field_meta}")  
        field_clause_template = field_meta.get("field_value", "{field_name}: {field_value}")

        # flogger.infof(f"fs template found is: {field_clause_template}")

        # Get field metadata

        field_name_literal = literal_field_name(field_name)
        # Replace placeholders with actual values
        suffix = fieldType.suffix()
        # rule_text = field_clause_template.replace("{field_name}", field_name_literal)

        # Note: for field level templates, they will still have just one field value, so aliasing can be used
        # for headers and other full spelling templates, we will need to create Rules like: CLASS_FIELD_VALUE : Datatype
        value_phrase = fieldType.value_phrase(field_meta)  #  Might be List[ClassName]
        node_name = f"{NTCase(class_name)}__{NTCase(field_name)}__{suffix}"
        rule_text2 = field_clause_template.replace("{field_name}",  field_name_literal )
        rule_text2 = rule_text2.replace("{field_value}", "FIELDVALUE") 
       
        # value_fragment = PomTemplate(value_phrase).to_fragment(None)
        # flogger.infof(f"vphrase is {value_phrase}; vfragment is {value_fragment}")
        rule_fragment = PomTemplate(rule_text2).to_fragment(class_name)
        repaired_fragment = rule_fragment.replace("FIELDVALUE_Q", value_phrase)
        # flogger.infof(f"repaired fragment = {repaired_fragment}")
        field_clause = AbstractClause(repaired_fragment, node_name)


        return field_clause


    def _generate_field_value_rule(
        self, class_name, field_name, field_obj
    ) -> AbstractRule:
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


        # Generate field value rule based on type

        metadata = self.pom_meta.resolved.get_field_metadata_with_defaults(class_name, field_name, fieldType.suffix())
        # Rule name
        # flogger.infof(f"Field name: {field_name}, type(FieldType): {type(fieldType)}")
        rule_name = f"{NTCase(class_name)}__{NTCase(field_name)}__value"

        value_phrase = fieldType.value_phrase(metadata)
        # flogger.infof(
        #     f"Field name: {field_name}, rule name: {rule_name}, value phrase: {value_phrase}"
        # )
        return AbstractRule(rule_name, value_phrase)





    @trace_method
    def _generate_type_hierarchy_clause(self, class_name) -> Optional[AbstractClause]:
        """
        Generate a rule for type hierarchy (parent class with subtypes).

        Args:
            class_name: Name of the class
        """
        # Get subtypes of this class
        subtypes = self.class_hierarchy[class_name].get("subtypes", [])
        # flogger.infof(f"subtypes of {class_name} are {subtypes}")
        if not subtypes:
            # No subtypes, just return
            return None


        # Create a rule that maps to any subtype (joined with |)
        subtypes_clause = " | ".join(str(NTCase(st)) for st in subtypes)
        return AbstractClause(subtypes_clause)



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
