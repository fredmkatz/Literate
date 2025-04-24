from utils_pom.util_fmk_pom import as_yaml
from utils_pom.util_json_pom import as_json
from typing import List

from ldm_parse_core import (
    LineType,
    HeadLine,
    # ClauseLine,
    MajorClause,
    MinorClause,
    PartStarter,
    ParseHandler,
)
from ldm_parse_bits import (  # to do. Not really core
    parse_trivial,
    parse_name,
    parse_name_list,
    parse_att_ref,
    parse_header,
    
    validate_trivial,
    validate_name,
    validate_name_list,
    validate_att_ref,
    validate_header,

    render_trivial,
    render_name,
    render_name_list,
    render_att_ref,
    render_header,

)




handle_name = ParseHandler(parse_name, render_name, validate_name)
handle_name_list = ParseHandler(parse_name_list, render_name_list, validate_name_list)
handle_trivial = ParseHandler(parse_trivial, render_trivial, validate_trivial)
handle_att_ref = ParseHandler(
    parse_att_ref, render_att_ref, validate_att_ref
)
handle_header = ParseHandler(parse_header, render_header, validate_header)


component_clauses = [
    MinorClause(word="abbreviation", is_list=False, is_cum=False, line_label="", handlers=handle_name),
    MinorClause(word="name", is_list=False, is_cum=False),  # by default: non-cum scalar
    MinorClause(word="plural", is_list=False, is_cum=False),
    MajorClause(word="note", class_started="Annotation", is_cum=True, is_list=False),
    MajorClause(word="issue", class_started="Annotation", is_cum=True, is_list=False),
    MajorClause(word="example", class_started="Annotation", is_cum=True, is_list=False),
    MajorClause(word="see", class_started="Annotation", is_cum=True, is_list=False),
]

section_clauses = component_clauses + [
    HeadLine(starter_pattern="#####", class_started="Section5", priority=10, handlers=handle_header),
    HeadLine(starter_pattern="####", class_started="Section4", priority=9, handlers=handle_header),
    HeadLine(starter_pattern="###", class_started="Section3", priority=8, handlers=handle_header),
    HeadLine(starter_pattern="##", class_started="Section2", priority=7, handlers=handle_header),
    HeadLine(starter_pattern="#", class_started="LDM", priority=1, handlers=handle_header),
    # HeadLine(starter_pattern="```", class_started="CodeBlock", handlers=handle_header),
    HeadLine(starter_pattern="_", class_started="Class", handlers=handle_header),
]
class_clauses = component_clauses + [
    HeadLine(starter_pattern="_", class_started="Class", handlers=handle_header),
    MinorClause(
        word="subtype of", is_list=True, is_cum=True, handlers=handle_name_list
    ),
    MinorClause(
        word="subtypes", is_list=True, is_cum=True, handlers=handle_name_list
    ),
    MinorClause(
        word="based on", is_list=True, is_cum=True, handlers=handle_name_list
    ),
    MinorClause(
        word="dependents", is_list=True, is_cum=True, handlers=handle_name_list
    ),
    MajorClause(
        word="Constraint", class_started="Constraint", is_list=True, is_cum=True
    ),
    MinorClause(
        word="dependent of", is_list=True, is_cum=True, handlers=handle_name_list
    ),
    MinorClause(word="where", is_list=False, is_cum=False),
    HeadLine(starter_pattern="__", class_started="AttributeSection", priority=2, handlers=handle_header),
    HeadLine(starter_pattern="-", class_started="Attribute", handlers=handle_header),
]
att_section_clauses = component_clauses + [
    HeadLine(starter_pattern="__", class_started="AttributeSection", handlers=handle_header),
    HeadLine(starter_pattern="-", class_started="Attribute", handlers=handle_header),
]

attribute_clauses = component_clauses + [
    HeadLine(starter_pattern="-", class_started="Attribute", handlers=handle_header),
    MinorClause(word="data type"),
    MinorClause(word="inverse", handlers=handle_att_ref),
    MinorClause(word="inverse of", handlers=handle_att_ref),
    MinorClause(word="overrides", handlers=handle_att_ref),
    MajorClause(word="Derivation", class_started="Derivation"),
    MajorClause(word="Default", class_started="Default"),
    MajorClause(word="Constraint", class_started="Constraint"),
]

formula_clauses = [
    MinorClause(word="code"),
    MinorClause(word="english"),
    MinorClause(word="message"),
    MinorClause(word="severity"),
]
all_clauses = (
    section_clauses
    + att_section_clauses
    + class_clauses
    + attribute_clauses
    + formula_clauses
)
nclauses = len(all_clauses)
all_clauses_by_priority = sorted(
    all_clauses, key=lambda clause: clause.priority, reverse=True
)
print("BY PRI")
for x in all_clauses_by_priority:
    print(f"{x.line_label} -- {x.priority}")

# print(r"All clauses {nclauses}: \n", as_yaml(all_clauses))
print(f"All clauses: {nclauses}:\n", as_json(all_clauses))

print(f"All clauses by Priority: {nclauses}:\n", as_json(all_clauses_by_priority))

all_clause_specs = {spec.line_label: spec for spec in all_clauses_by_priority}
nkeys = len(all_clause_specs.keys())
print(f"All clause specs: {nkeys}:\n", as_json(all_clause_specs))


partsNeeded = set(
    spec.class_started for spec in all_clauses if isinstance(spec, PartStarter)
)

print("parts needed: ", partsNeeded)

section_starts = []

clause_types = [
    # for Components
    # for Classes
    # For Attributes
    # for Formulas
    # TBD
    MajorClause(word="value type", class_started="Class"),
    MajorClause(word="Annotation", class_started="Annotation"),
]


def labels_for(clauses: List[LineType]) -> List[str]:
    return [c.line_label for c in clauses]


component_clause_labels = labels_for(component_clauses)
attribute_clause_labels = labels_for(attribute_clauses)
formula_clause_labels = labels_for(formula_clauses)

component_parts = ["Annotation"]

section_parts = component_parts + ["Class"]
part_parts = {
    "Document": component_parts
    + ["LDM", "Class", "Section2", "Section3", "Section4", "Section5"],
    "LDM": section_parts + ["Section2", "Section3", "Section4", "Section5"],
    "Section2": section_parts + ["Section3", "Section4", "Section5"],
    "Section3": section_parts + ["Section4", "Section5"],
    "Section4": section_parts + ["Section5"],
    "Section5": section_parts + [],
    "Class": component_parts + ["AttributeSection", "Attribute", "Constraint"],
    "AttributeSection": component_parts + ["Attribute"],
    "Attribute": component_parts + ["Derivation", "Default", "Constraint"],
    # No parts; only subclauses
    "Derivation": [],
    "Default": [],
    "Constraint": [],
}

part_labels = {
    "Document": labels_for(section_clauses),
    "LDM": labels_for(section_clauses),
    "Section2": labels_for(section_clauses),
    "Section3": labels_for(section_clauses),
    "Section4": labels_for(section_clauses),
    "Section5": labels_for(section_clauses),
    "Class": labels_for(class_clauses),
    "AttributeSection": labels_for(att_section_clauses),
    "Attribute": labels_for(attribute_clauses),
    # No parts; only subclauses
    "Derivation": labels_for(formula_clauses),
    "Default": labels_for(formula_clauses),
    "Constraint": labels_for(formula_clauses),
}


print("Part Parts:\n", as_json(part_parts))
print("Part Labels:\n", as_json(part_labels))

all_line_types = all_clauses
