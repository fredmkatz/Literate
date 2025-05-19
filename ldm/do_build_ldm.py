from utils_pom.util_fmk_pom import as_yaml
from utils_pom.util_json_pom import as_json
from typing import List

from dull_dsl.dull_parser_classes import (
    LineType,
    HeadLine,
    # ClauseLine,
    MajorClause,
    MinorClause,
    PartStarter,
)
from ldm.ldm_dull_handlers import (
    ParseName,
    ParseNameList, 
    ParseTrivial, 
    ParseAttributeReference, 
    ParseHeader, 
    ParseAnnotation,
    ParseSubtypeOf,

)




handle_name = ParseName()
handle_name_list = ParseNameList()
handle_subtype_of = ParseSubtypeOf()
handle_trivial = ParseTrivial()
handle_att_ref = ParseAttributeReference()
handle_header = ParseHeader()   
handle_annotation = ParseAnnotation()



component_clauses = [
    MinorClause(word="abbreviation", is_list=False, is_cum=False, line_label="", handlers=handle_name),
    MinorClause(word="name", is_list=False, is_cum=False),  # by default: non-cum scalar
    MinorClause(word="plural", is_list=False, is_cum=False),
    MinorClause(word="minerNote",  is_cum=True, is_list=False),
    MajorClause(word="majorNote", class_started="Annotation",  handlers=handle_annotation, is_cum=True, is_list=False),
    MajorClause(word="note", class_started="Annotation",  handlers=handle_annotation, is_cum=True, is_list=False),
    MajorClause(word="issue", class_started="Annotation",  handlers=handle_annotation, is_cum=True, is_list=False),
    MajorClause(word="example", class_started="Annotation",  handlers=handle_annotation, is_cum=True, is_list=False),
    MajorClause(word="see", class_started="Annotation",  handlers=handle_annotation, is_cum=True, is_list=False),
    MajorClause(word="[a-zA-Z ]+:", class_started="Annotation",  handlers=handle_annotation, is_cum=True, is_list=False, priority=-1, line_label="WILD"),
]

subject_clauses = component_clauses + [
    HeadLine(starter_pattern="#####", class_started="SubjectE", priority=10, handlers=handle_header),
    HeadLine(starter_pattern="####", class_started="SubjectD", priority=9, handlers=handle_header),
    HeadLine(starter_pattern="###", class_started="SubjectC", priority=8, handlers=handle_header),
    HeadLine(starter_pattern="##", class_started="SubjectB", priority=7, handlers=handle_header),
    HeadLine(starter_pattern="#", class_started="LiterateModel", priority=1, handlers=handle_header),
    # HeadLine(starter_pattern="```", class_started="CodeBlock", handlers=handle_header),
    HeadLine(starter_pattern="_", class_started="Class", handlers=handle_header),
    HeadLine(starter_pattern="Class", class_started="Class", handlers=handle_header),
    HeadLine(starter_pattern="Value Type:", class_started="ValueType", handlers=handle_header),
    HeadLine(starter_pattern="Code Type:", class_started="CodeType", handlers=handle_header),
]
class_clauses = component_clauses + [
    HeadLine(starter_pattern="_", class_started="Class", handlers=handle_header),
    HeadLine(starter_pattern="_ Value Type:", class_started="ValueType", handlers=handle_header),
    HeadLine(starter_pattern="_ Code Type:", class_started="CodeType", handlers=handle_header),

    MinorClause(
        word="subtype of", is_list=True, is_cum=True, handlers=handle_subtype_of
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
        word="constraint", class_started="Constraint", is_list=False, is_cum=True, plural="constraintes"
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
    MajorClause(word="Derivation", class_started="Derivation", attribute_name="one_liner"),
    MajorClause(word="Default", class_started="Default", attribute_name="one_liner"),
    MajorClause(word="Constraint", class_started="Constraint", is_list=False, is_cum=True, attribute_name="one_liner", plural="constraints"),
]

formula_clauses = [
    MinorClause(word="code"),
    MinorClause(word="english"),
    MinorClause(word="message"),
    MinorClause(word="severity"),
]
all_clauses = (
    subject_clauses
    + att_section_clauses
    + class_clauses
    + attribute_clauses
    + formula_clauses
)
nclauses = len(all_clauses)
all_clauses_by_priority = sorted(
    all_clauses, key=lambda clause: clause.priority, reverse=True
)
# print("BY PRI")
# for x in all_clauses_by_priority:
    # print(f"{x.line_label} -- {x.priority}")

# print(r"All clauses {nclauses}: \n", as_yaml(all_clauses))
# print(f"All clauses: {nclauses}:\n", as_json(all_clauses))

# print(f"All clauses by Priority: {nclauses}:\n", as_json(all_clauses_by_priority))

all_clause_specs = {spec.line_label: spec for spec in all_clauses_by_priority}
nkeys = len(all_clause_specs.keys())
# print(f"All clause specs: {nkeys}:\n", as_json(all_clause_specs))


partsNeeded = set(
    spec.class_started for spec in all_clauses if isinstance(spec, PartStarter)
)

# print("parts needed: ", partsNeeded)

# section_starts = []



def labels_for(clauses: List[LineType]) -> List[str]:
    return [c.line_label for c in clauses]


component_clause_labels = labels_for(component_clauses)
attribute_clause_labels = labels_for(attribute_clauses)
formula_clause_labels = labels_for(formula_clauses)

component_parts = ["Annotation"]

subject_parts = component_parts + ["Class", "CodeType", "ValueType"]
part_parts = {
    "Document": component_parts
    + ["LiterateModel", "Class", "CodeType", "ValueType", "SubjectB", "SubjectC", "SubjectD", "SubjectE"],
    "LiterateModel": subject_parts + ["SubjectB", "SubjectC", "SubjectD", "SubjectE"],
    "SubjectB": subject_parts + ["SubjectC", "SubjectD", "SubjectE"],
    "SubjectC": subject_parts + ["SubjectD", "SubjectE"],
    "SubjectD": subject_parts + ["SubjectE"],
    "SubjectE": subject_parts + [],
    "Class": component_parts + ["AttributeSection", "Attribute", "Constraint"],
    "CodeType": component_parts + ["AttributeSection", "Attribute", "Constraint"],
    "ValueType": component_parts + ["AttributeSection", "Attribute", "Constraint"],
    "AttributeSection": component_parts + ["Attribute"],
    "Attribute": component_parts + ["Derivation", "Default", "Constraint"],
    # No parts; only subclauses
    "Derivation": [],
    "Default": [],
    "Constraint": [],
}

part_labels = {
    "Document": labels_for(subject_clauses),
    "LiterateModel": labels_for(subject_clauses),
    "SubjectB": labels_for(subject_clauses),
    "SubjectC": labels_for(subject_clauses),
    "SubjectD": labels_for(subject_clauses),
    "SubjectE": labels_for(subject_clauses),
    "Class": labels_for(class_clauses),
    "ValueType": labels_for(class_clauses),
    "CodeType": labels_for(class_clauses),
    "AttributeSection": labels_for(att_section_clauses),
    "Attribute": labels_for(attribute_clauses),
    # No parts; only subclauses
    "Derivation": labels_for(formula_clauses),
    "Default": labels_for(formula_clauses),
    "Constraint": labels_for(formula_clauses),
}

part_plurals = {
    "Constraint": "constraintConditions",
    "Annotation": "annotationNotes",
    "Default": "defaultDefinitions",
    "Attribute": "FieldNames",
    "AttributeSection": "FieldGroups",
}
part_plurals = {
    "Class": "Classes",
}

# print("Part Parts:\n", as_json(part_parts))
# print("Part Labels:\n", as_json(part_labels))

majors = set(x.class_started for x in all_clauses if isinstance(x, MajorClause))
# print("Majors")
# print(majors)
parts_to_list = set(
    spec.class_started for spec in all_clauses if isinstance(spec, MajorClause) and 
        (spec.is_list or spec.is_cum)
    ) 

headed_parts = set(spec.class_started for spec in all_clauses if isinstance(spec, HeadLine))
# print("Headed parts")
# print(headed_parts)

# print("Parts to list", "\n", parts_to_list)
listed_parts = headed_parts | parts_to_list
# print("Listed parts", "\n", listed_parts)


all_line_types = all_clauses

models_dir = "ldm/ldm_models"
ldm_dull_specs = {
    "part_parts": part_parts,
    "part_plurals": part_plurals,
    "all_clauses_by_priority": all_clauses_by_priority,
    "listed_parts": listed_parts,
    "dirpath": models_dir,
    "model_doc": "Literate.md",
    "model_module": "Literate01.py",

}
if __name__ == "__main__":
    from dull_dsl.dull_build import build_dull_dsl
    
    model_doc = "Literate.md"
    model_doc = "LiterateTester.md"


    model_doc = "Literate.md"
    model_doc = "LiterateTester.md"



    ldm_dull_specs["model_doc"] = model_doc
    build_dull_dsl(ldm_dull_specs)

