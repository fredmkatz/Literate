// src/app/temporal/page.tsx
"use client";

import { useState, useEffect } from 'react';
import { GraphDBClient, TemporalTriple, SPARQLBinding } from '@/lib/sparql-client';
import Link from 'next/link';
import { format, parseISO } from 'date-fns';

export default function TemporalPage() {
  const [client] = useState(() => new GraphDBClient());
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().slice(0, 16) // Current datetime for input
  );
  const [currentState, setCurrentState] = useState<SPARQLBinding[]>([]);
  const [recentChanges, setRecentChanges] = useState<TemporalTriple[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'current' | 'asof'>('current');

  useEffect(() => {
    loadRecentChanges();
  }, []);

  async function loadRecentChanges() {
    try {
      const changes = await client.getTemporalHistory(undefined, 100);
      setRecentChanges(changes);
    } catch (err) {
      console.error('Failed to load recent changes:', err);
    }
  }

  async function loadAsOfState() {
    if (!selectedDate) return;
    
    try {
      setLoading(true);
      setError(null);
      const state = await client.getAsOfState(selectedDate);
      setCurrentState(state);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load state');
      console.error('Failed to load as-of state:', err);
    } finally {
      setLoading(false);
    }
  }

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
                <span>Temporal View</span>
              </div>
              <h1 className="text-3xl font-bold text-gray-900">Time Travel</h1>
              <p className="text-gray-600 mt-1">
                Explore how your ontology evolved over time
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Controls */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            <div className="flex items-center space-x-4">
              <label className="text-sm font-medium text-gray-700">
                View Mode:
              </label>
              <select
                value={viewMode}
                onChange={(e) => setViewMode(e.target.value as 'current' | 'asof')}
                className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="current">Recent Changes</option>
                <option value="asof">As-of Date</option>
              </select>
            </div>

            {viewMode === 'asof' && (
              <div className="flex items-center space-x-4">
                <label className="text-sm font-medium text-gray-700">
                  Select Date & Time:
                </label>
                <input
                  type="datetime-local"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                <button
                  onClick={loadAsOfState}
                  disabled={loading}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {loading ? 'Loading...' : 'Load State'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Current View */}
          <div className="space-y-6">
            {viewMode === 'current' ? (
              <RecentChangesView changes={recentChanges} />
            ) : (
              <AsOfStateView state={currentState} selectedDate={selectedDate} />
            )}
          </div>

          {/* Right Column - Timeline */}
          <div className="space-y-6">
            <TimelineView changes={recentChanges.slice(0, 20)} />
          </div>
        </div>
      </main>
    </div>
  );
}

function RecentChangesView({ changes }: { changes: TemporalTriple[] }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">Recent Changes</h2>
        <p className="text-gray-600 mt-1">Latest modifications to the ontology</p>
      </div>
      
      <div className="p-6">
        {changes.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No recent changes found</p>
        ) : (
          <div className="space-y-4">
            {changes.slice(0, 10).map((change, index) => (
              <ChangeCard key={index} change={change} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function AsOfStateView({ 
  state, 
  selectedDate 
}: { 
  state: SPARQLBinding[]; 
  selectedDate: string;
}) {
  const groupedState = groupBySubject(state);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">
          State as of {format(parseISO(selectedDate), 'PPpp')}
        </h2>
        <p className="text-gray-600 mt-1">
          {state.length} triples were active at this time
        </p>
      </div>
      
      <div className="p-6">
        {Object.keys(groupedState).length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            No data found for the selected date
          </p>
        ) : (
          <div className="space-y-4">
            {Object.entries(groupedState).slice(0, 10).map(([subject, triples]) => (
              <SubjectCard key={subject} subject={subject} triples={triples} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function TimelineView({ changes }: { changes: TemporalTriple[] }) {
  // Group changes by date
  const groupedByDate = changes.reduce((acc, change) => {
    const date = format(parseISO(change.timestamp), 'yyyy-MM-dd');
    if (!acc[date]) acc[date] = [];
    acc[date].push(change);
    return acc;
  }, {} as Record<string, TemporalTriple[]>);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">Timeline</h2>
        <p className="text-gray-600 mt-1">Changes grouped by date</p>
      </div>
      
      <div className="p-6">
        <div className="space-y-6">
          {Object.entries(groupedByDate)
            .sort(([a], [b]) => b.localeCompare(a))
            .map(([date, dayChanges]) => (
              <div key={date}>
                <h3 className="font-medium text-gray-900 mb-3">
                  {format(parseISO(date), 'EEEE, MMMM d, yyyy')}
                </h3>
                <div className="space-y-2">
                  {dayChanges.slice(0, 5).map((change, index) => (
                    <div key={index} className="flex items-center space-x-3 text-sm">
                      <div className={`w-2 h-2 rounded-full ${
                        change.operation === 'insert' ? 'bg-green-500' :
                        change.operation === 'update' ? 'bg-blue-500' :
                        'bg-red-500'
                      }`} />
                      <span className="text-gray-600">
                        {format(parseISO(change.timestamp), 'HH:mm')}
                      </span>
                      <span className="text-gray-900 truncate flex-1">
                        {change.predicate.split('/').pop()}
                      </span>
                    </div>
                  ))}
                  {dayChanges.length > 5 && (
                    <div className="text-xs text-gray-500 ml-5">
                      +{dayChanges.length - 5} more changes
                    </div>
                  )}
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}

function ChangeCard({ change }: { change: TemporalTriple }) {
  const predicateDisplay = change.predicate.split('/').pop() || change.predicate;
  const subjectDisplay = change.subject.split('/').pop() || change.subject;
  const objectDisplay = change.object.length > 100 
    ? change.object.substring(0, 100) + '...' 
    : change.object;

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1">
          <div className="font-medium text-gray-900">
            {subjectDisplay} → {predicateDisplay}
          </div>
          <div className="text-sm text-gray-600 mt-1">
            {objectDisplay}
          </div>
        </div>
        <span className={`px-2 py-1 rounded text-xs ${
          change.operation === 'insert' ? 'bg-green-100 text-green-800' :
          change.operation === 'update' ? 'bg-blue-100 text-blue-800' :
          'bg-red-100 text-red-800'
        }`}>
          {change.operation}
        </span>
      </div>
      <div className="flex justify-between items-center text-xs text-gray-500">
        <span>By: {change.user}</span>
        <span>{format(parseISO(change.timestamp), 'MMM d, yyyy HH:mm')}</span>
      </div>
    </div>
  );
}

function SubjectCard({ 
  subject, 
  triples 
}: { 
  subject: string; 
  triples: SPARQLBinding[];
}) {
  const subjectDisplay = subject.split('/').pop() || subject;

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <h4 className="font-medium text-gray-900 mb-3">{subjectDisplay}</h4>
      <div className="space-y-2">
        {triples.slice(0, 5).map((triple, index) => (
          <div key={index} className="flex justify-between text-sm">
            <span className="text-gray-600">
              {triple.predicate.value.split('/').pop()}
            </span>
            <span className="text-gray-900 truncate ml-4">
              {triple.object.value.length > 50 
                ? triple.object.value.substring(0, 50) + '...'
                : triple.object.value
              }
            </span>
          </div>
        ))}
        {triples.length > 5 && (
          <div className="text-xs text-gray-500">
            +{triples.length - 5} more properties
          </div>
        )}
      </div>
    </div>
  );
}

function groupBySubject(state: SPARQLBinding[]): Record<string, SPARQLBinding[]> {
  return state.reduce((acc, triple) => {
    const subject = triple.subject.value;
    if (!acc[subject]) acc[subject] = [];
    acc[subject].push(triple);
    return acc;
  }, {} as Record<string, SPARQLBinding[]>);
}