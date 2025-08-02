from ldm.Literate_01 import ClassName, AttributeName, AttributeReference
from utils.class_casing import UpperCamel, LowerCamel, SnakeCase


cname = "component"
# camelname = UpperCamel(input_string=cname)
camelname = UpperCamel(cname)
print(f"UpperCamel name is {camelname}")
print(f"Upper as json is {camelname.to_json()}")

# class_name = ClassName(input_string = cname)
class_name = ClassName(cname)
print(f"class name is {class_name}")
print(f"Class name as json is {class_name.to_json()}")


attname = "Elaboration"

attribute_name = AttributeName(attname)

attref = AttributeReference(class_name=cname, attribute_name=attname)

print(f"Class name is {class_name}")
print(f"Attribute name is {attribute_name}")
print(f"Attribute name as json is {attribute_name.to_json()}")
print(f"Attribute reference is {attref}")

print(f"Attribute reference as to_dict is {attref.to_dict()}")
print(f"Attribute reference as to_json is {attref.to_json()}")
