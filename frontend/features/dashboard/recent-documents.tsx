'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { FileText, ArrowRight } from 'lucide-react';
import { api } from '@/lib/api-client';

export default function RecentDocuments() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchDocuments() {
      try {
        const res = await api.get<any>('/api/v1/upload');
        if (res && res.documents) {
          setDocuments(res.documents);
        }
      } catch (err) {
        console.error('Failed to fetch recent documents:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchDocuments();
  }, []);

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm flex flex-col h-full">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Recent Documents Ingested
        </h2>
        <Link
          href="/upload"
          className="inline-flex items-center gap-1 text-xs text-primary hover:underline font-semibold"
        >
          View Ingestion Manager
          <ArrowRight className="h-3 w-3" />
        </Link>
      </div>

      <div className="flex-1 overflow-x-auto">
        {loading ? (
          <p className="text-xs text-muted-foreground animate-pulse py-6 text-center">
            Loading document repository...
          </p>
        ) : documents.length === 0 ? (
          <div className="py-8 text-center space-y-2">
            <FileText className="h-8 w-8 text-muted-foreground/40 mx-auto" />
            <p className="text-xs text-muted-foreground">No documents ingested in the repository yet.</p>
            <Link
              href="/upload"
              className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-primary/10 hover:bg-primary/20 text-primary text-xs font-semibold px-3 py-1.5 transition-all"
            >
              Upload First Document
              <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-border/80 text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                <th className="pb-2">Document Details</th>
                <th className="pb-2">Classification</th>
                <th className="pb-2">Uploaded</th>
                <th className="pb-2 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40 text-xs">
              {documents.map((doc, i) => (
                <tr key={doc.id || i} className="hover:bg-secondary/25 transition-colors">
                  <td className="py-3 flex items-center gap-2">
                    <FileText className="h-4 w-4 text-muted-foreground shrink-0" />
                    <span className="font-semibold text-foreground truncate max-w-[180px] sm:max-w-xs">
                      {doc.filename || doc.name || 'Untitled Document'}
                    </span>
                  </td>
                  <td className="py-3 text-muted-foreground">{doc.classification || 'Internal'}</td>
                  <td className="py-3 text-muted-foreground">
                    {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : 'Recently'}
                  </td>
                  <td className="py-3 text-right">
                    <span className={`inline-block rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase ${
                      doc.status === 'COMPLETED' || doc.status === 'PROCESSED'
                        ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
                        : doc.status === 'FAILED'
                        ? 'bg-destructive/10 text-destructive border-destructive/20'
                        : 'bg-amber-500/10 text-amber-500 border-amber-500/20'
                    }`}>
                      {doc.status || 'COMPLETED'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
