 from utils.class_casing import *
from trials.Literate import *

import json

from pydantic.dataclasses import dataclass, Field


# Test without ABC
@dataclass
class TestTokenNoABC(PydanticMixin):
    content: str = Field(default="")


@dataclass
class TestCasingNoABC(TestTokenNoABC):
    content: str = Field(default="")


# Test this
# Note. Casing is a normal dataclass, which inherits for PresentableToken
test_no_abc = TestTokenNoABC("test content")
print(f"No ABC Token - Content: '{test_no_abc.content}'")

test_no_abc = TestCasingNoABC("test content")
print(f"No ABC Casing - Content: '{test_no_abc.content}'")

testtoken = PresentableToken("presentable token")
print("Test token: ", testtoken)
testtoken2 = PresentableToken(content="presentable token")
print("Test token: with content= ", testtoken2)

print("model_dump test token")
print(testtoken2.model_dump())

testcasing = Casing("preentable casing")
print("testcasing: ", testcasing)
print("model_dump testcasing")
print(testcasing.model_dump())

upper_camel = UpperCamel(content="test upper camel")
print(f"Upper camel Content: '{upper_camel.content}'")
print("model_dump upper_camel")
print(upper_camel.model_dump())

exit(0)


@dataclass
class SimpleTest:
    content: str


# Test this
simple = SimpleTest("test content")
print(f"Simple test content: {simple.content}")


@dataclass
class SimpleTestWithMixin(PydanticMixin):
    content: str


simple_mixin = SimpleTestWithMixin("test with mixin")
print(f"Simple with mixin: {simple_mixin.content}")


from pydantic import Field


@dataclass
class SimpleTestWithField:
    content: str = Field(default="")


simple_field = SimpleTestWithField("test with field")
print(f"Simple with field: {simple_field.content}")


@dataclass
class SimpleTestWithParent(UpperCamel):
    content: str = Field(default="")


simple_parent = SimpleTestWithParent("test with parent")
print(f"Simple with parent: {simple_parent.content}")


exit(0)
# Test with explicit keyword argument
test_instance = UpperCamel(content="test content")
print(f"Test with keyword: {test_instance.content}")


# Test with positional (what you're doing now)
test_instance2 = UpperCamel("test content")
print(f"Test with positional: {test_instance2.content}")
exit(0)
samples = [
    UpperCamel("upper camel"),
    SnakeCase("snake case"),
]

for sample in samples:
    print("Sample: ", sample)
    # print(sample.asdict())


att1 = Attribute(name=LowerCamel("desired flavor"))
att2 = Attribute(LowerCamel("settled flavor"))
class1 = Class(UpperCamel("sample class"), [att1, att2])

print('\natt1 - att1 = Attribute(name = LowerCamel("desired flavor")) ')
print(att1)
print(att1.name)

print('\nclass1 =  Class(UpperCamel("sample class"), [att1, att2])')
print(class1.model_dump())
print(class1.name)
print(class1.name)
exit(0)
class_schema = class1.model_json_schema()
print(json.dumps(class_schema, indent=2))

json_data = class1.model_dump_json(indent=2)
print(json_data)
