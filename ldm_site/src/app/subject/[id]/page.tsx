"use client";

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { GraphDBClient } from '@/lib/sparql-client';

interface SubjectDetails {
  uri: string;
  name: string;
  oneLiner?: string;
  elaboration?: string;
  classes: Array<{
    uri: string;
    name: string;
    oneLiner?: string;
  }>;
  subSubjects: Array<{
    uri: string;
    name: string;
    oneLiner?: string;
  }>;
}

export default function SubjectPage() {
  const params = useParams();
  const [client] = useState(() => new GraphDBClient());
  const [subject, setSubject] = useState<SubjectDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const subjectUri = decodeURIComponent(params.id as string);

  useEffect(() => {
    async function loadSubjectData() {
      try {
        setLoading(true);
        const data = await client.getSubjectDetails(subjectUri);
        setSubject(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load subject');
        console.error('Failed to load subject data:', err);
      } finally {
        setLoading(false);
      }
    }

    if (subjectUri) {
      loadSubjectData();
    }
  }, [client, subjectUri]);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !subject) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h2 className="text-red-800 font-semibold mb-2">Error Loading Subject</h2>
          <p className="text-red-600">{error || 'Subject not found'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 p-8">
      {/* Breadcrumbs */}
      <nav className="flex items-center space-x-2 text-sm text-gray-500 mb-6">
        <Link href="/" className="hover:text-gray-700">Home</Link>
        <span>›</span>
        <span className="text-gray-900">{subject.name}</span>
      </nav>

      {/* Subject Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{subject.name}</h1>
        {subject.oneLiner && (
          <p className="text-lg text-gray-600 mb-4">{subject.oneLiner}</p>
        )}
        {subject.elaboration && (
          <div className="prose max-w-none">
            <p className="text-gray-700">{subject.elaboration}</p>
          </div>
        )}
      </div>

      {/* Classes Section */}
      {subject.classes.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Classes</h2>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="divide-y divide-gray-200">
              {subject.classes.map((cls) => (
                <Link 
                  key={cls.uri}
                  href={`/class/${encodeURIComponent(cls.uri)}`}
                  className="block p-4 hover:bg-gray-50 transition-colors"
                >
                  <h3 className="font-medium text-blue-600 hover:text-blue-800">
                    {cls.name}
                  </h3>
                  {cls.oneLiner && (
                    <p className="text-sm text-gray-600 mt-1">{cls.oneLiner}</p>
                  )}
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Sub-Subjects Section */}
      {subject.subSubjects.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Sub-Subjects</h2>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="divide-y divide-gray-200">
              {subject.subSubjects.map((subSubject) => (
                <Link 
                  key={subSubject.uri}
                  href={`/subject/${encodeURIComponent(subSubject.uri)}`}
                  className="block p-4 hover:bg-gray-50 transition-colors"
                >
                  <h3 className="font-medium text-blue-600 hover:text-blue-800">
                    {subSubject.name}
                  </h3>
                  {subSubject.oneLiner && (
                    <p className="text-sm text-gray-600 mt-1">{subSubject.oneLiner}</p>
                  )}
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}