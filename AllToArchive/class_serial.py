import json

class JSONSerializable:
    def to_dict(self):
        # Default implementation
        return {"_type": getattr(self, "_type", self.__class__.__name__)}
        
    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)
        
    @classmethod
    def from_json(cls, json_string):
        data = json.loads(json_string)
        return cls.from_dict(data)