// src/app/api/graphdb/route.ts
import { NextRequest, NextResponse } from 'next/server';

const GRAPHDB_BASE_URL = 'http://localhost:7200';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const endpoint = searchParams.get('endpoint') || 'repositories';
  const repo = searchParams.get('repo');
  const query = searchParams.get('query');

  try {
    let url = `${GRAPHDB_BASE_URL}/${endpoint}`;
    
    if (repo && query) {
      // SPARQL query
      url = `${GRAPHDB_BASE_URL}/repositories/${repo}`;
    }

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: `GraphDB error: ${response.statusText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: `Connection failed: ${error.message}` },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const repo = searchParams.get('repo') || 'ldm_repos';
  
  try {
    const body = await request.text();
    console.log('API: Received SPARQL request for repo:', repo);
    console.log('API: Request body:', body);
    
    const url = `${GRAPHDB_BASE_URL}/repositories/${repo}`;
    console.log('API: Connecting to GraphDB at:', url);
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/sparql-results+json',
      },
      body: body,
    });

    console.log('API: GraphDB response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.log('API: GraphDB error response:', errorText);
      return NextResponse.json(
        { error: `GraphDB error: ${response.statusText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('API: GraphDB success, returning data');
    return NextResponse.json(data);
  } catch (error) {
    console.log('API: Exception occurred:', error);
    return NextResponse.json(
      { error: `Query failed: ${error.message}` },
      { status: 500 }
    );
  }
}