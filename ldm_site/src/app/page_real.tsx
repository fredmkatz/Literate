// src/app/page.tsx
"use client";

import { useState, useEffect } from 'react';
import { GraphDBClient, ClassInfo } from '@/lib/sparql-client';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';

interface Stats {
  totalTriples: number;
  totalClasses: number;
  totalProperties: number;
  temporalStatements: number;
}

export default function Dashboard() {
  const [client] = useState(() => new GraphDBClient());
  const [stats, setStats] = useState<Stats | null>(null);
  const [classes, setClasses] = useState<ClassInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [statsData, classesData] = await Promise.all([
          client.getStats(),
          client.getClasses()
        ]);
        setStats(statsData);
        setClasses(classesData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [client]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h2 className="text-red-800 font-semibold mb-2">Connection Error</h2>
          <p className="text-red-600">{error}</p>
          <p className="text-sm text-red-500 mt-2">
            Make sure GraphDB is running on localhost:7200
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Literate Data Model Editor
              </h1>
              <p className="text-gray-600 mt-1">
                Collaborative ontology editing with temporal versioning
              </p>
            </div>
            <div className="flex space-x-4">
              <Link
                href="/temporal"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Temporal View
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <StatCard
              title="Total Triples"
              value={stats.totalTriples.toLocaleString()}
              icon="🔗"
              description="RDF statements in the database"
            />
            <StatCard
              title="Classes"
              value={stats.totalClasses.toString()}
              icon="📝"
              description="Ontology classes defined"
            />
            <StatCard
              title="Properties"
              value={stats.totalProperties.toString()}
              icon="🏷️"
              description="Attributes and relationships"
            />
            <StatCard
              title="Temporal Statements"
              value={stats.temporalStatements.toLocaleString()}
              icon="⏰"
              description="Versioned with timestamps"
            />
          </div>
        )}

        {/* Classes Grid */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              Ontology Classes
            </h2>
            <p className="text-gray-600 mt-1">
              Click on a class to view its detailed structure
            </p>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {classes.map((cls) => (
                <ClassCard key={cls.uri} classInfo={cls} />
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function StatCard({ 
  title, 
  value, 
  icon, 
  description 
}: { 
  title: string; 
  value: string; 
  icon: string; 
  description: string;
}) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center">
        <div className="text-2xl mr-3">{icon}</div>
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
      </div>
      <p className="text-xs text-gray-500 mt-2">{description}</p>
    </div>
  );
}

function ClassCard({ classInfo }: { classInfo: ClassInfo }) {
  const displayName = classInfo.label || classInfo.uri.split('/').pop() || classInfo.uri;
  const classId = encodeURIComponent(classInfo.uri);
  
  return (
    <Link href={`/class/${classId}`}>
      <div className="bg-gray-50 rounded-lg border border-gray-200 p-4 hover:bg-gray-100 hover:border-gray-300 transition-all cursor-pointer">
        <h3 className="font-semibold text-gray-900 mb-2">{displayName}</h3>
        
        {classInfo.comment && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-2">
            {classInfo.comment}
          </p>
        )}
        
        <div className="flex justify-between items-center text-xs text-gray-500">
          <span>{classInfo.attributeCount} attributes</span>
          {classInfo.lastModified && (
            <span title={classInfo.lastModified}>
              {formatDistanceToNow(new Date(classInfo.lastModified), { addSuffix: true })}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}