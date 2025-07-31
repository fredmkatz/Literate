// src/app/class/[id]/page.tsx
"use client";

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { GraphDBClient, ClassInfo, AttributeInfo, TemporalTriple } from '@/lib/sparql-client';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';

interface ClassDetails {
  class: ClassInfo;
  attributes: AttributeInfo[];
  instances: number;
}

export default function ClassDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [client] = useState(() => new GraphDBClient());
  const [details, setDetails] = useState<ClassDetails | null>(null);
  const [history, setHistory] = useState<TemporalTriple[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'history'>('overview');

  const classUri = decodeURIComponent(params.id as string);

  useEffect(() => {
    async function loadClassData() {
      try {
        setLoading(true);
        const [classDetails, classHistory] = await Promise.all([
          client.getClassDetails(classUri),
          client.getTemporalHistory(classUri, 20)
        ]);
        setDetails(classDetails);
        setHistory(classHistory);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load class data');
        console.error('Failed to load class data:', err);
      } finally {
        setLoading(false);
      }
    }

    if (classUri) {
      loadClassData();
    }
  }, [client, classUri]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !details) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h2 className="text-red-800 font-semibold mb-2">Error Loading Class</h2>
          <p className="text-red-600">{error || 'Class not found'}</p>
          <button
            onClick={() => router.back()}
            className="mt-4 text-blue-600 hover:text-blue-800"
          >
            ← Go Back
          </button>
        </div>
      </div>
    );
  }

  const displayName = details.class.label || classUri.split('/').pop() || classUri;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
                <Link href="/" className="hover:text-gray-700">
                  Dashboard
                </Link>
                <span>›</span>
                <span>Class Detail</span>
              </div>
              <h1 className="text-3xl font-bold text-gray-900">{displayName}</h1>
              {details.class.comment && (
                <p className="text-gray-600 mt-1">{details.class.comment}</p>
              )}
            </div>
            <div className="flex space-x-4">
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                Edit Class
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="text-2xl font-bold text-gray-900">{details.attributes.length}</div>
            <div className="text-sm text-gray-600">Attributes</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="text-2xl font-bold text-gray-900">{details.instances}</div>
            <div className="text-sm text-gray-600">Instances</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="text-2xl font-bold text-gray-900">{history.length}</div>
            <div className="text-sm text-gray-600">Recent Changes</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('overview')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'overview'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'history'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                History
              </button>
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'overview' && (
              <AttributesView attributes={details.attributes} />
            )}
            {activeTab === 'history' && (
              <HistoryView history={history} />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

function AttributesView({ attributes }: { attributes: AttributeInfo[] }) {
  if (attributes.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No attributes defined for this class.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Attributes</h3>
      
      <div className="space-y-3">
        {attributes.map((attr) => (
          <AttributeCard key={attr.uri} attribute={attr} />
        ))}
      </div>
    </div>
  );
}

function AttributeCard({ attribute }: { attribute: AttributeInfo }) {
  const displayName = attribute.label || attribute.uri.split('/').pop() || attribute.uri;
  const rangeDisplay = attribute.range ? attribute.range.split('/').pop() : 'Any';

  return (
    <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h4 className="font-medium text-gray-900">{displayName}</h4>
          <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
            <span>Type: {rangeDisplay}</span>
            {attribute.isOptional && <span className="text-blue-600">Optional</span>}
            {attribute.cardinality && <span>Cardinality: {attribute.cardinality}</span>}
          </div>
        </div>
        {attribute.lastModified && (
          <span className="text-xs text-gray-400">
            {formatDistanceToNow(new Date(attribute.lastModified), { addSuffix: true })}
          </span>
        )}
      </div>
    </div>
  );
}

function HistoryView({ history }: { history: TemporalTriple[] }) {
  if (history.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No history available for this class.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Changes</h3>
      
      <div className="space-y-3">
        {history.map((change, index) => (
          <HistoryCard key={index} change={change} />
        ))}
      </div>
    </div>
  );
}

function HistoryCard({ change }: { change: TemporalTriple }) {
  const predicateDisplay = change.predicate.split('/').pop() || change.predicate;
  const objectDisplay = change.object.length > 50 
    ? change.object.substring(0, 50) + '...' 
    : change.object;

  return (
    <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="font-medium text-gray-900">
            {predicateDisplay}
          </div>
          <div className="text-sm text-gray-600 mt-1">
            {objectDisplay}
          </div>
          <div className="flex items-center space-x-4 text-xs text-gray-500 mt-2">
            <span>By: {change.user}</span>
            <span className={`px-2 py-1 rounded ${
              change.operation === 'insert' ? 'bg-green-100 text-green-800' :
              change.operation === 'update' ? 'bg-blue-100 text-blue-800' :
              'bg-red-100 text-red-800'
            }`}>
              {change.operation}
            </span>
          </div>
        </div>
        <span className="text-xs text-gray-400">
          {formatDistanceToNow(new Date(change.timestamp), { addSuffix: true })}
        </span>
      </div>
    </div>
  );
}