

import json
from dataclasses import dataclass
from typing import List, Optional

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL

def try_rdf():
    print("Hi from rdf")
    
    n3_data_string = """
        @prefix : <http://example.org/> .
        :subject :predicate :object .
        """
    g = Graph()
    g.parse(data=n3_data_string, format="n3")
    print(g)
    

if __name__ == "__main__":
    try_rdf()


# poetry add --group dev $(cat rdf_owl/requirements.txt)
