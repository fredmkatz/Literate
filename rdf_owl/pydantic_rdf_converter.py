"""
Pydantic to RDF-star Converter with Temporal Annotations
Converts Pydantic models to RDF with StarVers-style temporal versioning
"""
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, XSD, OWL
import yaml

# Define our namespaces
LDM = Namespace("http://example.org/ldm/")
PROV = Namespace("http://www.w3.org/ns/prov#")
TIME = Namespace("http://www.w3.org/2006/time#")
TEMP = Namespace("http://example.org/temporal/")

@dataclass
class TemporalMetadata:
    """Metadata for temporal versioning"""
    user_id: str = "system"
    timestamp: datetime = None
    operation: str = "insert"  # insert, update, delete
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class PydanticToRDFConverter:
    """Converts Pydantic model instances to RDF with temporal annotations"""
    
    def __init__(self, base_uri: str = "http://example.org/ldm/"):
        self.graph = Graph()
        self.base_uri = base_uri
        self.ldm = Namespace(base_uri)
        
        # Bind namespaces
        self.graph.bind("ldm", self.ldm)
        self.graph.bind("prov", PROV)
        self.graph.bind("time", TIME)
        self.graph.bind("temp", TEMP)
        
        # Keep track of created resources
        self.resource_cache = {}
        
    def create_uri(self, type_name: str, instance_id: str = None) -> URIRef:
        """Create a URI for a resource"""
        if instance_id is None:
            instance_id = str(uuid.uuid4())
        return URIRef(f"{self.base_uri}{type_name}/{instance_id}")
    
    def add_temporal_triple(self, subject: URIRef, predicate: URIRef, obj: Union[URIRef, Literal], 
                          metadata: TemporalMetadata):
        """Add a triple with RDF-star temporal annotations"""
        # Add the base triple
        self.graph.add((subject, predicate, obj))
        
        # Create quoted triple for RDF-star annotation
        quoted_triple = BNode()
        
        # In real RDF-star, this would be: <<subject predicate object>>
        # For now, we'll use reification-style until GraphDB imports
        self.graph.add((quoted_triple, RDF.type, RDF.Statement))
        self.graph.add((quoted_triple, RDF.subject, subject))
        self.graph.add((quoted_triple, RDF.predicate, predicate))
        self.graph.add((quoted_triple, RDF.object, obj))
        
        # Add temporal metadata
        self.graph.add((quoted_triple, PROV.generatedAtTime, 
                       Literal(metadata.timestamp.isoformat(), datatype=XSD.dateTime)))
        self.graph.add((quoted_triple, PROV.wasAttributedTo, 
                       Literal(metadata.user_id)))
        self.graph.add((quoted_triple, TEMP.operation, 
                       Literal(metadata.operation)))
    
    def convert_pydantic_schema(self, schema_dict: Dict[str, Any]) -> None:
        """Convert Pydantic schema to RDF classes and properties"""
        metadata = TemporalMetadata(operation="schema_definition")
        
        # Process schema definitions
        if '$defs' in schema_dict:
            for class_name, class_def in schema_dict['$defs'].items():
                self._convert_class_definition(class_name, class_def, metadata)
    
    def _convert_class_definition(self, class_name: str, class_def: Dict[str, Any], 
                                metadata: TemporalMetadata):
        """Convert a single class definition"""
        class_uri = self.ldm[class_name]
        
        # Define the class
        self.add_temporal_triple(class_uri, RDF.type, RDFS.Class, metadata)
        
        if 'title' in class_def:
            self.add_temporal_triple(class_uri, RDFS.label, 
                                   Literal(class_def['title']), metadata)
        
        if 'description' in class_def:
            self.add_temporal_triple(class_uri, RDFS.comment, 
                                   Literal(class_def['description']), metadata)
        
        # Process properties
        if 'properties' in class_def:
            for prop_name, prop_def in class_def['properties'].items():
                self._convert_property_definition(class_uri, prop_name, prop_def, metadata)
    
    def _convert_property_definition(self, class_uri: URIRef, prop_name: str, 
                                   prop_def: Dict[str, Any], metadata: TemporalMetadata):
        """Convert a property definition"""
        prop_uri = self.ldm[prop_name]
        
        # Define the property
        self.add_temporal_triple(prop_uri, RDF.type, RDF.Property, metadata)
        self.add_temporal_triple(prop_uri, RDFS.domain, class_uri, metadata)
        
        if 'title' in prop_def:
            self.add_temporal_triple(prop_uri, RDFS.label, 
                                   Literal(prop_def['title']), metadata)
        
        # Handle property types
        if 'type' in prop_def:
            if prop_def['type'] == 'string':
                self.add_temporal_triple(prop_uri, RDFS.range, XSD.string, metadata)
            elif prop_def['type'] == 'boolean':
                self.add_temporal_triple(prop_uri, RDFS.range, XSD.boolean, metadata)
            elif prop_def['type'] == 'array':
                # Handle arrays - could be more sophisticated
                self.add_temporal_triple(prop_uri, RDFS.range, RDFS.Container, metadata)
    
    def convert_instance(self, instance_data: Dict[str, Any], 
                        root_type: str = "LiterateModel") -> URIRef:
        """Convert a Pydantic model instance to RDF"""
        metadata = TemporalMetadata(operation="insert")
        
        # Create main instance
        instance_uri = self.create_uri(root_type)
        class_uri = self.ldm[root_type]
        
        self.add_temporal_triple(instance_uri, RDF.type, class_uri, metadata)
        
        # Convert all properties
        self._convert_instance_properties(instance_uri, instance_data, metadata)
        
        return instance_uri
    
    def _convert_instance_properties(self, subject_uri: URIRef, data: Dict[str, Any], 
                                   metadata: TemporalMetadata):
        """Convert instance properties recursively"""
        for key, value in data.items():
            if key.startswith('_'):  # Skip private fields
                continue
                
            prop_uri = self.ldm[key]
            
            if isinstance(value, dict):
                # Handle nested objects
                if '_type' in value:
                    # This is a typed object
                    nested_uri = self.create_uri(value['_type'])
                    self.add_temporal_triple(subject_uri, prop_uri, nested_uri, metadata)
                    self.add_temporal_triple(nested_uri, RDF.type, 
                                           self.ldm[value['_type']], metadata)
                    self._convert_instance_properties(nested_uri, value, metadata)
                else:
                    # Handle as nested properties
                    self._convert_instance_properties(subject_uri, value, metadata)
            
            elif isinstance(value, list):
                # Handle arrays
                for item in value:
                    if isinstance(item, dict) and '_type' in item:
                        nested_uri = self.create_uri(item['_type'])
                        self.add_temporal_triple(subject_uri, prop_uri, nested_uri, metadata)
                        self.add_temporal_triple(nested_uri, RDF.type, 
                                               self.ldm[item['_type']], metadata)
                        self._convert_instance_properties(nested_uri, item, metadata)
                    else:
                        # Simple list item
                        literal_value = Literal(item)
                        self.add_temporal_triple(subject_uri, prop_uri, literal_value, metadata)
            
            elif value is not None:
                # Handle simple literals
                literal_value = Literal(value)
                self.add_temporal_triple(subject_uri, prop_uri, literal_value, metadata)
    
    def export_turtle_star(self) -> str:
        """Export the graph as Turtle with RDF-star syntax"""
        # For now, export as regular Turtle
        # In production, you'd convert reified triples to RDF-star syntax
        return self.graph.serialize(format='turtle')
    
    def export_for_graphdb(self) -> str:
        """Export in format suitable for GraphDB import"""
        return self.export_turtle_star()

# Example usage
def main():
    # Load the schema and instance
    with open('rdf_owl/LiterateMetaModel_01_PD_schema.yaml', 'r', encoding="utf-8") as f:
        schema = yaml.safe_load(f)
    
    with open('rdf_owl/Literate_PD_04.v_model.json', 'r', encoding="utf-8") as f:
        instance = json.load(f)
    
    # Create converter
    converter = PydanticToRDFConverter()
    
    # Convert schema to RDF classes/properties
    converter.convert_pydantic_schema(schema)
    
    # Convert instance data
    instance_uri = converter.convert_instance(instance)
    
    # Export for GraphDB
    rdf_output = converter.export_for_graphdb()
    
    # Save to file
    with open('ldm_site/ldm_site_data/literate_model.ttl', 'w', encoding="utf-8") as f:
        f.write(rdf_output)
    
    print(f"Converted model to RDF. Instance URI: {instance_uri}")
    print(f"Total triples: {len(converter.graph)}")
    print("Saved to ldm_site/ldm_site_data/literate_model.ttl")

if __name__ == "__main__":
    main()
