import json
from Literate import Class, ClassName, Attribute, AttributeName

# Generate JSON schema


# Example usage
my_class = Class(
    name=ClassName("my lower case class name"),
    attributes=[Attribute(name=AttributeName("myAttr"))],
)

# Serialization
json_data = my_class.model_dump_json()
print("\nJson data - model_dump_json -for serialized class:")
print(json_data)

json_data = my_class.model_dump()
print("\nJson data model_dump - for serialized class:")
print(type(json_data))
print(json_data)
print(json.dumps(json_data, indent=2))

json_string = json.dumps(json_data, indent=2)

print("Generate schema")
class_schema = Class.model_json_schema()
print(json.dumps(class_schema, indent=2))
exit(0)

# Deserialization
print("\nDeserializing...")
loaded = Class.model_validate_json(json_string)
