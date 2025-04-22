from utils_pom.util_fmk_pom import as_yaml
from utils_pom.util_json_pom import as_json
from typing import List

from ldm_parse_core import(
    LineType,
    HeadLine,
    # ClauseLine,
    MajorClause,
    MinorClause,
    PartStarter,
    # DocPart,
)




component_clauses = [
    MinorClause(word="abbreviation", is_list=False, is_cum=False, line_label=""),
    MinorClause(word="name"),  # by default: non-cum scalar
    MinorClause(word="plural"),
    MajorClause(word="note", class_started="Annotation", is_cum=True),
    MajorClause(word="issue", class_started="Annotation", is_cum=True),
    MajorClause(word="example", class_started="Annotation", is_cum=True),
    MajorClause(word="see", class_started="Annotation", is_cum=True),

]

section_clauses = component_clauses + [
    HeadLine(starter_pattern="#####", class_started="Section5"),
    HeadLine(starter_pattern="####", class_started="Section4"),
    HeadLine(starter_pattern="###", class_started="Section3"),
    HeadLine(starter_pattern="##", class_started="Section2"),
    HeadLine(starter_pattern="#", class_started="LDM"),
    HeadLine(starter_pattern="```", class_started="CodeBlock"),
    HeadLine(starter_pattern="_", class_started="Class"),

]
class_clauses = component_clauses + [
    HeadLine(starter_pattern="_", class_started="Class"),
    MinorClause(
        word="subtype of", is_list=True, is_cum=True, parse_function="parse_name_list"
    ),
    MinorClause(
        word="subtypes", is_list=True, is_cum=True, parse_function="parse_name_list"
    ),
    MinorClause(
        word="based on", is_list=True, is_cum=True, parse_function="parse_name_list"
    ),
    MinorClause(
        word="dependents", is_list=True, is_cum=True, parse_function="parse_name_list"
    ),
    MajorClause(
        word="Constraint", class_started="Constraint", is_list=False, is_cum=True
    ),
    MinorClause(
        word="dependent of", is_list=True, is_cum=True, parse_function="parse_name_list"
    ),
    MinorClause(word="where"),
    
    MajorClause(word="Constraint", class_started="Constraint"),
    HeadLine(starter_pattern="__", class_started="AttributeSection"),
    HeadLine(starter_pattern="-", class_started="Attribute"),
]
att_section_clauses = component_clauses + [
    HeadLine(starter_pattern="__", class_started="AttributeSection"),
    
    HeadLine(starter_pattern="-", class_started="Attribute"),

]

attribute_clauses = component_clauses + [
    HeadLine(starter_pattern="-", class_started="Attribute"),

    MinorClause(word="data type"),
    MinorClause(word="inverse", parse_function="parse_attribute_reference"),
    MinorClause(word="inverse of", parse_function="parse_attribute_reference"),
    MinorClause(word="overrides", parse_function="parse_attribute_reference"),
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
all_clauses = (section_clauses + att_section_clauses 
               + class_clauses + attribute_clauses + formula_clauses)
nclauses = len(all_clauses)

# print(r"All clauses {nclauses}: \n", as_yaml(all_clauses))
print(f"All clauses: {nclauses}:\n", as_json(all_clauses))

all_clause_specs = {spec.line_label: spec for spec in all_clauses}
nkeys = len(all_clause_specs.keys())
print(f"All clause specs: {nkeys}:\n", as_json(all_clauses))


partsNeeded = set(
    spec.class_started for spec in all_clauses if isinstance(spec, PartStarter)
)

print("parts needed: ", partsNeeded)

section_starts = [
]

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

section_parts = ["Class"]

part_parts = {
    "Document":  ["LDM", "Section2", "Section3", "Section4", "Section5"],
    "LDM": section_parts + ["Section2", "Section3", "Section4", "Section5"],
    "Section2": section_parts +["Section3", "Section4", "Section5"],
    "Section3": section_parts +["Section4", "Section5"],
    "Section4": section_parts +["Section5"],
    "Section5": section_parts +[],
    "Class": ["AttributeSection", "Attribute", "Constraint"],
    "AttributeSection": ["Attribute"],
    "Attribute": ["Derivation", "Default", "Constraint"],
    
    # No parts; only subclauses
    "Derivation": [],
    "Default": [],
    "Constraint": [],
    "CodeBlock": [],
    
}

part_labels = {
    "Document":  labels_for(section_clauses),
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
    "CodeBlock": labels_for(formula_clauses),
}


print("Part Parts:\n", as_json(part_parts))
print("Part Labels:\n", as_json(part_labels))

all_line_types = all_clauses



