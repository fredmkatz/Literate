// src/lib/sparql-client.ts
export interface SPARQLBinding {
  [key: string]: {
    type: 'uri' | 'literal' | 'bnode';
    value: string;
    datatype?: string;
    'xml:lang'?: string;
  };
}

export interface SPARQLResult {
  head: {
    vars: string[];
  };
  results: {
    bindings: SPARQLBinding[];
  };
}

export interface ClassInfo {
  uri: string;
  label?: string;
  comment?: string;
  attributeCount: number;
  lastModified?: string;
}

export interface AttributeInfo {
  uri: string;
  label?: string;
  domain?: string;
  range?: string;
  isOptional?: boolean;
  cardinality?: string;
  lastModified?: string;
}

export interface TemporalTriple {
  subject: string;
  predicate: string;
  object: string;
  timestamp: string;
  user: string;
  operation: string;
}

export class GraphDBClient {
  private repository: string;

  constructor(repository = 'ldm_repos') {
    this.repository = repository;
  }

  async executeQuery(query: string): Promise<SPARQLResult> {
    try {
      console.log('Client: Executing SPARQL query:', query);
      
      const response = await fetch(`/api/graphdb?repo=${this.repository}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ query }),
      });

      console.log('Client: Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.log('Client: Error response:', errorText);
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Client: Response data:', data);
      
      if (data.error) {
        throw new Error(data.error);
      }

      return data;
    } catch (error) {
      console.error('SPARQL query failed:', error);
      throw error;
    }
  }

  async getClasses(): Promise<ClassInfo[]> {
    const query = `
      PREFIX ldm: <http://example.org/ldm/>
      
      SELECT ?class ?nameContent ?oneLinerContent ?modelPath ?plural WHERE {
        ?class a ldm:Class .
        OPTIONAL { ?class ldm:name ?nameObj . ?nameObj ldm:content ?nameContent }
        OPTIONAL { ?class ldm:one_liner ?oneLinerObj . ?oneLinerObj ldm:content ?oneLinerContent }
        OPTIONAL { ?class ldm:model_path ?modelPath }
        OPTIONAL { ?class ldm:plural ?plural }
      }
      ORDER BY ?modelPath ?class
      LIMIT 20
    `;

    const result = await this.executeQuery(query);
    
    return result.results.bindings.map(binding => ({
      uri: binding.class.value,
      label: binding.nameContent?.value || binding.modelPath?.value || binding.plural?.value || 'Unknown Class',
      comment: binding.oneLinerContent?.value,
      attributeCount: 0, // Will show as 0 for now to avoid slow COUNT queries
    }));
  }

  async getStats(): Promise<{
    totalTriples: number;
    totalClasses: number;
    totalProperties: number;
    temporalStatements: number;
  }> {
    // Use hardcoded stats to avoid hanging queries for now
    return {
      totalTriples: 55000,
      totalClasses: 25, // Hardcoded to avoid calling getClasses again
      totalProperties: 100,
      temporalStatements: 0
    };
  }

  async getTemporalHistory(classUri?: string, limit = 50): Promise<TemporalTriple[]> {
    // Mock temporal data while GraphDB issues are resolved
    const allHistory = [
      {
        subject: 'http://example.org/LiterateModel',
        predicate: 'http://www.w3.org/2000/01/rdf-schema#label',
        object: 'Literate Data Model',
        timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
        user: 'alice@example.org',
        operation: 'CREATE'
      },
      {
        subject: 'http://example.org/Class',
        predicate: 'http://www.w3.org/2000/01/rdf-schema#comment',
        object: 'Updated class definition',
        timestamp: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
        user: 'bob@example.org',
        operation: 'UPDATE'
      },
      {
        subject: 'http://example.org/Attribute',
        predicate: 'http://example.org/hasCardinality',
        object: '1..1',
        timestamp: new Date(Date.now() - 10800000).toISOString(), // 3 hours ago
        user: 'alice@example.org',
        operation: 'CREATE'
      }
    ];

    if (classUri) {
      return allHistory.filter(h => h.subject === classUri).slice(0, limit);
    }
    return allHistory.slice(0, limit);
  }

  async getClassDetails(classUri: string): Promise<{
    class: ClassInfo;
    attributes: AttributeInfo[];
    instances: number;
  }> {
    // Get class info
    const classQuery = `
      PREFIX ldm: <http://example.org/ldm/>
      
      SELECT ?class ?nameContent ?oneLinerContent ?modelPath ?plural WHERE {
        ?class a ldm:Class .
        FILTER(?class = <${classUri}>)
        OPTIONAL { ?class ldm:name ?nameObj . ?nameObj ldm:content ?nameContent }  
        OPTIONAL { ?class ldm:one_liner ?oneLinerObj . ?oneLinerObj ldm:content ?oneLinerContent }
        OPTIONAL { ?class ldm:model_path ?modelPath }
        OPTIONAL { ?class ldm:plural ?plural }
      }
    `;

    const classResult = await this.executeQuery(classQuery);
    
    if (classResult.results.bindings.length === 0) {
      throw new Error(`Class not found: ${classUri}`);
    }

    const binding = classResult.results.bindings[0];
    const classInfo: ClassInfo = {
      uri: binding.class.value,
      label: binding.nameContent?.value || binding.modelPath?.value || binding.plural?.value || 'Unknown Class',
      comment: binding.oneLinerContent?.value,
      attributeCount: 0 // Will be updated below
    };

    // Get attributes for this class
    const attrQuery = `
      PREFIX ldm: <http://example.org/ldm/>
      
      SELECT ?attr ?nameContent ?oneLinerContent WHERE {
        <${classUri}> ldm:attributes ?attr .
        OPTIONAL { ?attr ldm:name ?nameObj . ?nameObj ldm:content ?nameContent }
        OPTIONAL { ?attr ldm:one_liner ?oneLinerObj . ?oneLinerObj ldm:content ?oneLinerContent }
      }
    `;

    const attrResult = await this.executeQuery(attrQuery);
    
    const attributes = attrResult.results.bindings.map(binding => ({
      uri: binding.attr.value,
      label: binding.nameContent?.value || 'Unknown Attribute',
      domain: classUri,
      range: 'Unknown',
      lastModified: new Date().toISOString()
    }));

    classInfo.attributeCount = attributes.length;

    return {
      class: classInfo,
      attributes,
      instances: 0 // Placeholder for now
    };
  }

  async getSubjectHierarchy(): Promise<any> {
    // Get all subject relationships in one query
    const query = `
      PREFIX ldm: <http://example.org/ldm/>
      
      SELECT ?parent ?parentName ?child ?childName ?childOneLiner WHERE {
        ?parent ldm:subjects ?child .
        OPTIONAL { ?parent ldm:name ?parentNameObj . ?parentNameObj ldm:content ?parentName }
        OPTIONAL { ?child ldm:name ?childNameObj . ?childNameObj ldm:content ?childName }
        OPTIONAL { ?child ldm:one_liner ?childOneLineObj . ?childOneLineObj ldm:content ?childOneLiner }
      }
      ORDER BY ?parentName ?childName
    `;

    const result = await this.executeQuery(query);
    
    // Build hierarchy from flat results
    const nodeMap = new Map();
    const rootNodes = new Set();

    // First pass: create all nodes
    result.results.bindings.forEach(binding => {
      const parentUri = binding.parent.value;
      const childUri = binding.child.value;
      
      if (!nodeMap.has(parentUri)) {
        nodeMap.set(parentUri, {
          uri: parentUri,
          name: binding.parentName?.value || 'Unknown',
          children: []
        });
      }
      
      if (!nodeMap.has(childUri)) {
        nodeMap.set(childUri, {
          uri: childUri,
          name: binding.childName?.value || 'Unknown',
          oneLiner: binding.childOneLiner?.value,
          children: []
        });
      }
    });

    // Second pass: build relationships
    result.results.bindings.forEach(binding => {
      const parent = nodeMap.get(binding.parent.value);
      const child = nodeMap.get(binding.child.value);
      parent.children.push(child);
    });

    // Find root (LiterateModel)
    const root = Array.from(nodeMap.values()).find(node => 
      node.name.includes('Literate') || node.uri.includes('LiterateModel')
    );

    return root || null;
  }

  async getSubjectDetails(subjectUri: string): Promise<any> {
    // Get subject basic info, classes, and sub-subjects
    const query = `
      PREFIX ldm: <http://example.org/ldm/>
      
      SELECT ?subject ?name ?oneLiner ?elaboration ?class ?className ?classOneLiner ?subSubject ?subSubjectName ?subSubjectOneLiner WHERE {
        VALUES ?subject { <${subjectUri}> }
        
        OPTIONAL { ?subject ldm:name ?nameObj . ?nameObj ldm:content ?name }
        OPTIONAL { ?subject ldm:one_liner ?oneLineObj . ?oneLineObj ldm:content ?oneLiner }
        OPTIONAL { ?subject ldm:elaboration ?elaborationObj . ?elaborationObj ldm:content ?elaboration }
        
        OPTIONAL { 
          ?class ldm:subject ?subject .
          OPTIONAL { ?class ldm:name ?classNameObj . ?classNameObj ldm:content ?className }
          OPTIONAL { ?class ldm:one_liner ?classOneLineObj . ?classOneLineObj ldm:content ?classOneLiner }
        }
        
        OPTIONAL {
          ?subject ldm:subjects ?subSubject .
          OPTIONAL { ?subSubject ldm:name ?subSubjectNameObj . ?subSubjectNameObj ldm:content ?subSubjectName }
          OPTIONAL { ?subSubject ldm:one_liner ?subSubjectOneLineObj . ?subSubjectOneLineObj ldm:content ?subSubjectOneLiner }
        }
      }
    `;

    const result = await this.executeQuery(query);
    
    if (result.results.bindings.length === 0) {
      throw new Error(`Subject not found: ${subjectUri}`);
    }

    const firstBinding = result.results.bindings[0];
    
    // Collect unique classes and sub-subjects
    const classesMap = new Map();
    const subSubjectsMap = new Map();

    result.results.bindings.forEach(binding => {
      if (binding.class?.value) {
        classesMap.set(binding.class.value, {
          uri: binding.class.value,
          name: binding.className?.value || 'Unknown Class',
          oneLiner: binding.classOneLiner?.value
        });
      }
      
      if (binding.subSubject?.value) {
        subSubjectsMap.set(binding.subSubject.value, {
          uri: binding.subSubject.value,
          name: binding.subSubjectName?.value || 'Unknown Subject',
          oneLiner: binding.subSubjectOneLiner?.value
        });
      }
    });

    return {
      uri: subjectUri,
      name: firstBinding.name?.value || 'Unknown Subject',
      oneLiner: firstBinding.oneLiner?.value,
      elaboration: firstBinding.elaboration?.value,
      classes: Array.from(classesMap.values()),
      subSubjects: Array.from(subSubjectsMap.values())
    };
  }

  // Add other methods as needed...
}