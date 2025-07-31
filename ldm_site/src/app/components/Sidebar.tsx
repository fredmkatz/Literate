"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { GraphDBClient } from '@/lib/sparql-client';
import { ChevronDownIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

interface SubjectNode {
  uri: string;
  name: string;
  oneLiner?: string;
  children: SubjectNode[];
}

export default function Sidebar() {
  const [client] = useState(() => new GraphDBClient());
  const [hierarchy, setHierarchy] = useState<SubjectNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  useEffect(() => {
    async function loadHierarchy() {
      try {
        const data = await client.getSubjectHierarchy();
        setHierarchy(data);
        // Expand root by default
        if (data) {
          setExpandedNodes(new Set([data.uri]));
        }
      } catch (error) {
        console.error('Failed to load subject hierarchy:', error);
      } finally {
        setLoading(false);
      }
    }

    loadHierarchy();
  }, [client]);

  const toggleExpanded = (uri: string) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(uri)) {
      newExpanded.delete(uri);
    } else {
      newExpanded.add(uri);
    }
    setExpandedNodes(newExpanded);
  };

  const renderSubjectNode = (node: SubjectNode, level = 0) => {
    const isExpanded = expandedNodes.has(node.uri);
    const hasChildren = node.children && node.children.length > 0;
    const indent = level * 16;

    return (
      <div key={node.uri}>
        <div 
          className="flex items-center py-2 px-2 hover:bg-gray-100 cursor-pointer"
          style={{ paddingLeft: `${8 + indent}px` }}
        >
          {hasChildren && (
            <button
              onClick={(e) => {
                e.preventDefault();
                toggleExpanded(node.uri);
              }}
              className="mr-1 p-1"
            >
              {isExpanded ? (
                <ChevronDownIcon className="h-4 w-4" />
              ) : (
                <ChevronRightIcon className="h-4 w-4" />
              )}
            </button>
          )}
          {!hasChildren && <div className="w-6" />}
          
          <Link 
            href={`/subject/${encodeURIComponent(node.uri)}`}
            className="flex-1 text-sm text-gray-700 hover:text-blue-600"
          >
            {node.name}
          </Link>
        </div>
        
        {isExpanded && hasChildren && (
          <div>
            {node.children.map(child => renderSubjectNode(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="w-80 bg-white border-r border-gray-200 p-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded mb-2"></div>
          <div className="h-4 bg-gray-200 rounded mb-2"></div>
          <div className="h-4 bg-gray-200 rounded mb-2"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-80 bg-white border-r border-gray-200 overflow-y-auto">
      <div className="p-4 border-b border-gray-200">
        <h2 className="font-semibold text-gray-900">Subject Hierarchy</h2>
      </div>
      
      <div className="py-2">
        {hierarchy ? renderSubjectNode(hierarchy) : (
          <div className="p-4 text-gray-500">No subjects found</div>
        )}
      </div>
    </div>
  );
}