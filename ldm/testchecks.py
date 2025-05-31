from typing import List, Optional
from ldm.Literate_01.py import (
    Diagnostic,
    Annotation,
    DataType,
    BaseDataType,
    DataTypeClause,
    ClassName,
    AttributeName,
    AttributeSectionName,
    SubjectName,
    IsOptional,
)
from utils.class_casing import UpperCamel, Casing, SnakeCase, LowerCamel
from class_pom_token import IsOptional, IsExclusive, IsExhaustive, AsValue
from ldm.ldm_validators import check_type
from utils.util_json import as_json


def testdiag():
    d = Diagnostic(
        severity="Error", message="HELLO", object_type="Gopher", object_name="Gogo"
    )
    diagnostics = [d]
    diagnostics2 = []

    diagnostics2.append(d)
    expected_type = Optional[List[Diagnostic]]
    # expected_type2 = Optional[List[Annotation]]
    print()
    print("Testing diagnostics = [Diagnostic[d]]")
    print(check_type(diagnostics, expected_type))
    print()
    print("Testing diagnostics2 = [],append(d)")

    print(check_type(diagnostics2, expected_type))


def testcase(casing, result):
    print()
    print(f"Testing: {casing}")
    # print("input: ", result.input_string)
    print(f"\tasjson: {as_json(result)}")
    # print(f"\ttoJSON: {result.toJSON()}")
    print(f"\tas_str: {result}")
    print("REPR: ", repr(result))
    # print(f"\tas_dict: {as_dict(result)}")


bdt = BaseDataType(class_name="Component", as_value_type=AsValue(True))

print("\n print(bdt)")
print(bdt)

print("\n print(as_json(bdt))")

print(as_json(bdt))

dtclause = DataTypeClause(data_type=bdt, is_optional_lit=IsOptional(False))

tests = [
    ["UpperCamel", UpperCamel("value type")],
    ["LowerCamel", LowerCamel("was required")],
    ["SnakeCase", SnakeCase("subtype of")],
    ["ClassName", ClassName("value type")],
    ["SubjectName", SubjectName("For Machinery")],
    ["AttributeName", AttributeName("was required")],
    ["IsOptional - true", IsOptional(True)],
    ["IsOptional - false", IsOptional(False)],
    ["IsExclusive - true", IsExclusive(True)],
    ["IsExclusive - false", IsExclusive(False)],
    ["IsExhaustive - true", IsExhaustive(True)],
    ["IsExhaustive - false", IsExhaustive(False)],
    ["AsValue - true", AsValue(True)],
    ["AsValue - false", AsValue(False)],
    ["BasicDataType", bdt],
    ["DTClause", dtclause],
    ["IsOptional(required)", IsOptional("required")],
    ["IsOptional(false)", IsOptional(False)],
    ["IsOptional(true)", IsOptional(True)],
]
for test in tests:
    testcase(test[0], test[1])


exit(0)
import dataclasses

print("using dataclasses.asdict() -> ", dataclasses.asdict(bdt))


print("type(bdt) = ", type(bdt))

cname = ClassName("Attribute")
print(as_json(cname))
print("using dataclasses.asdict() -> ", dataclasses.asdict(cname))


sname = SubjectName("Introduduction")
print("Subject name ", as_json(sname))

aname = AttributeName("was rquired")
print("Atribute name ", as_json(aname))
asname = AttributeSectionName("For Machinery")
print("AttSection name ", as_json(asname))
