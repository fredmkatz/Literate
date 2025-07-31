"""
GraphDB Repository Setup and Data Loading
"""
import requests
import json
from pathlib import Path

class GraphDBManager:
    """Manage GraphDB repositories and data loading"""
    
    def __init__(self, base_url: str = "http://localhost:7200"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def create_repository(self, repo_id: str, repo_title: str = None):
        """Create a new GraphDB repository with RDF-star support"""
        if repo_title is None:
            repo_title = repo_id
        
        config = {
            "@context": {
                "rep": "http://www.openrdf.org/config/repository#",
                "sr": "http://www.openrdf.org/config/repository/sail#",
                "sail": "http://www.openrdf.org/config/sail#",
                "owlim": "http://www.ontotext.com/trree/owlim#"
            },
            "@id": f"rep:{repo_id}",
            "@type": "rep:Repository",
            "rep:repositoryID": repo_id,
            "rdfs:label": repo_title,
            "rep:repositoryImpl": {
                "@id": f"_:{repo_id}-impl",
                "@type": "sr:SailRepository",
                "sr:sailImpl": {
                    "@id": f"_:{repo_id}-sail",
                    "@type": "owlim:Sail",
                    "owlim:base-URL": "http://example.org/owlim#",
                    "owlim:defaultNS": "",
                    "owlim:entity-index-size": "10000000",
                    "owlim:entity-id-size": "32",
                    "owlim:imports": "",
                    "owlim:repository-type": "file-repository",
                    "owlim:ruleset": "rdfs-plus-optimized",
                    "owlim:storage-folder": "storage",
                    "owlim:enable-context-index": "false",
                    "owlim:enablePredicateList": "true",
                    "owlim:in-memory-literal-properties": "true",
                    "owlim:enable-literal-index": "true",
                    "owlim:check-for-inconsistencies": "false",
                    "owlim:disable-sameAs": "true",
                    "owlim:query-timeout": "0",
                    "owlim:query-limit-results": "0",
                    "owlim:throw-QueryEvaluationException-on-timeout": "false",
                    "owlim:read-only": "false",
                    # Enable RDF-star support
                    "owlim:rdf-star-triple-sources": "true"
                }
            }
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = self.session.post(
            f"{self.base_url}/rest/repositories",
            json=config,
            headers=headers
        )
        
        if response.status_code == 201:
            print(f"Repository '{repo_id}' created successfully")
            return True
        else:
            print(f"Failed to create repository: {response.status_code} - {response.text}")
            return False
    
    def list_repositories(self):
        """List all repositories"""
        response = self.session.get(f"{self.base_url}/rest/repositories")
        if response.status_code == 200:
            repos = response.json()
            print("Available repositories:")
            for repo in repos:
                print(f"  - {repo['id']}: {repo['title']}")
            return repos
        else:
            print(f"Failed to list repositories: {response.status_code}")
            return []
    
    def load_data(self, repo_id: str, file_path: str, format: str = "text/turtle"):
        """Load RDF data into a repository using SPARQL UPDATE"""
        # Use the SPARQL endpoint for data loading
        url = f"{self.base_url}/repositories/{repo_id}/statements"
        
        # Read the file and encode as UTF-8 bytes
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read().encode('utf-8')
        
        headers = {
            'Content-Type': f'{format}; charset=utf-8'
        }
        
        response = self.session.post(url, data=data, headers=headers)
        
        if response.status_code in [200, 204]:
            print(f"Data from '{file_path}' uploaded successfully to '{repo_id}'")
            return True
        else:
            print(f"Failed to upload data: {response.status_code} - {response.text}")
            return False
    
    def load_data_alternative(self, repo_id: str, file_path: str):
        """Alternative method using SPARQL INSERT"""
        # Read the turtle file
        with open(file_path, 'r', encoding='utf-8') as f:
            turtle_data = f.read()
        
        # Create a SPARQL INSERT query
        insert_query = f"""
        INSERT DATA {{
            {turtle_data}
        }}
        """
        
        url = f"{self.base_url}/repositories/{repo_id}/statements"
        
        headers = {
            'Content-Type': 'application/sparql-update; charset=utf-8'
        }
        
        response = self.session.post(url, data=insert_query.encode('utf-8'), headers=headers)
        
        if response.status_code in [200, 204]:
            print(f"Data from '{file_path}' inserted successfully to '{repo_id}'")
            return True
        else:
            print(f"Failed to insert data: {response.status_code} - {response.text}")
            return False
    
    def execute_query(self, repo_id: str, query: str, query_type: str = "SELECT"):
        """Execute a SPARQL query"""
        url = f"{self.base_url}/repositories/{repo_id}"
        
        params = {
            'query': query
        }
        
        headers = {
            'Accept': 'application/sparql-results+json' if query_type == "SELECT" else 'text/turtle'
        }
        
        response = self.session.post(url, data=params, headers=headers)
        
        if response.status_code == 200:
            return response.json() if query_type == "SELECT" else response.text
        else:
            print(f"Query failed: {response.status_code} - {response.text}")
            return None

# Example SPARQL queries for your literate model
SAMPLE_QUERIES = {
    "count_triples": """
        SELECT (COUNT(*) as ?count) WHERE {
            ?s ?p ?o .
        }
    """,
    
    "list_classes": """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?class ?label WHERE {
            ?class a rdfs:Class .
            OPTIONAL { ?class rdfs:label ?label }
        }
        ORDER BY ?class
    """,
    
    "temporal_query": """
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?statement ?subject ?predicate ?object ?timestamp ?user WHERE {
            ?statement a rdf:Statement ;
                       rdf:subject ?subject ;
                       rdf:predicate ?predicate ;
                       rdf:object ?object ;
                       prov:generatedAtTime ?timestamp ;
                       prov:wasAttributedTo ?user .
        }
        ORDER BY ?timestamp
    """,
    
    "as_of_query": """
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?subject ?predicate ?object WHERE {
            ?statement a rdf:Statement ;
                       rdf:subject ?subject ;
                       rdf:predicate ?predicate ;
                       rdf:object ?object ;
                       prov:generatedAtTime ?timestamp .
            FILTER(?timestamp <= "2025-07-29T12:00:00"^^xsd:dateTime)
        }
    """
}

def setup_literate_model_repo():
    """Complete setup for literate model repository"""
    gdb = GraphDBManager()
    
    # Use existing repository instead of creating new one
    repo_id = "ldm_repos"  # Use your existing LDM repository
    
    # List repositories to confirm
    print("Available repositories:")
    gdb.list_repositories()
    
    # Load data if file exists
    data_file = "ldm_site/ldm_site_data/literate_model.ttl"
    if Path(data_file).exists():
        print(f"\nLoading data from {data_file}...")
        
        # Try the main method first
        if not gdb.load_data(repo_id, data_file):
            print("Primary method failed, trying alternative...")
            gdb.load_data_alternative(repo_id, data_file)
        
        # Run a test query
        print("\nRunning test query...")
        result = gdb.execute_query(repo_id, SAMPLE_QUERIES["count_triples"])
        if result:
            count = result['results']['bindings'][0]['count']['value']
            print(f"Total triples in repository: {count}")
        
        # Try a temporal query
        print("\nRunning temporal query...")
        result = gdb.execute_query(repo_id, SAMPLE_QUERIES["temporal_query"])
        if result and result['results']['bindings']:
            print(f"Found {len(result['results']['bindings'])} temporal statements")
            # Show first few
            for i, binding in enumerate(result['results']['bindings'][:3]):
                print(f"  {i+1}. {binding.get('subject', {}).get('value', '')} -> {binding.get('timestamp', {}).get('value', '')}")
        else:
            print("No temporal statements found")
            
    else:
        print(f"\nData file {data_file} not found. Run the converter first.")
    
    return gdb

if __name__ == "__main__":
    setup_literate_model_repo()