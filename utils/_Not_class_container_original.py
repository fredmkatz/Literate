# from utils.util_pydantic import PydanticMixin,  dataclass, field
from dataclasses import dataclass, field
from typing import Any, List

@dataclass
class Container():
    # container_atts = None # :list = [] # field(init=False, default_factory=list)
    container_atts: List[str] = field(init=False, default_factory=list)

    _container: "Container" = field(init=False, default=None)
    
    def set_contents(self, container: "Container"):
        self._container = container
        
        
        print(f"Container set: {container} containts {self}")
        print("\tand atts are ", self.container_atts)
        if not self.container_atts:
            self.container_atts = ["subjects", "classes", "attribute_sections", "attributes", "data_type_clause", "data_type"]
        for att_name in self.container_atts:
            att_value = getattr(self, att_name, None)
            if not att_value:
                continue
            if isinstance(att_value, list):
                for child in att_value:
                    if not isinstance(child, Container):
                        print(f"Container issue: {att_name} contains  a non-Container")
                        continue
                    child.set_contents(self)
            else:
                if not isinstance(att_value, Container):
                        print(f"Container issue: {att_name} refers to a non-Container")
                        continue
                att_value.set_contents(self)
    
    def nearest(self, cls: Any) -> "Container":
        if isinstance(self, cls):
            return self
        if not self._container:
            return None
        return self._container.nearest(cls)
        