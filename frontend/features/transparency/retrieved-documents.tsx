'use client';

import React, { useState } from 'react';
import { FileText, FileSpreadsheet, ChevronDown, ChevronUp } from 'lucide-react';

export interface ExplanationDocument {
  name: string;
  category: string;
  confidence: 'High' | 'Medium' | 'Low';
  relevanceTag: string;
  // Extended fields for dashboard interactive layouts
  whyRetrieved?: string;
  size?: number;
}

interface RetrievedDocumentsProps {
  documents: ExplanationDocument[];
  interactive?: boolean;
}

export default function RetrievedDocuments({
  documents,
  interactive = false,
}: RetrievedDocumentsProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const getDocIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'xlsx' || ext === 'csv') {
      return FileSpreadsheet;
    }
    return FileText;
  };

  const getConfidenceBadgeColor = (conf: 'High' | 'Medium' | 'Low') => {
    switch (conf) {
      case 'High':
        return 'bg-emerald-500/10 border-emerald-500/25 text-emerald-500';
      case 'Medium':
        return 'bg-amber-500/10 border-amber-500/25 text-amber-500';
      case 'Low':
        return 'bg-destructive/10 border-destructive/25 text-destructive';
    }
  };

  const toggleExpand = (idx: number) => {
    if (!interactive) return;
    setExpandedIndex((prev) => (prev === idx ? null : idx));
  };

  return (
    <div className="space-y-3 animate-in fade-in duration-150">
      <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
        Retrieved Documents ({documents.length})
      </span>
      <div className="space-y-2">
        {documents.map((doc, idx) => {
          const Icon = getDocIcon(doc.name);
          const isExpanded = expandedIndex === idx;

          return (
            <div
              key={idx}
              className={`rounded-lg border bg-card transition-all ${
                interactive ? 'cursor-pointer hover:bg-secondary/20' : ''
              } ${isExpanded ? 'border-primary/60 shadow-md' : 'border-border'}`}
              onClick={() => toggleExpand(idx)}
            >
              {/* Header card view */}
              <div className="flex items-center justify-between p-3">
                <div className="flex items-center gap-2.5 min-w-0">
                  <Icon className="h-4.5 w-4.5 text-primary shrink-0" />
                  <div className="min-w-0">
                    <div className="text-xs font-bold text-foreground truncate max-w-[160px] sm:max-w-xs">
                      {doc.name}
                    </div>
                    <div className="text-[10px] text-muted-foreground mt-0.5 capitalize">
                      {doc.category}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 shrink-0">
                  <span
                    className={`rounded border px-1.5 py-0.5 text-[9px] font-extrabold uppercase ${getConfidenceBadgeColor(
                      doc.confidence
                    )}`}
                  >
                    {doc.confidence}
                  </span>
                  
                  <span className="rounded bg-secondary/80 border border-border px-1.5 py-0.5 text-[9px] font-semibold text-muted-foreground">
                    {doc.relevanceTag}
                  </span>

                  {interactive && (
                    <div className="text-muted-foreground/60 ml-1">
                      {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    </div>
                  )}
                </div>
              </div>

              {/* Expandable Meta details */}
              {interactive && isExpanded && (
                <div className="px-3 pb-3 pt-1 border-t border-border/40 text-[10px] space-y-2 text-muted-foreground bg-secondary/10 rounded-b-lg animate-in slide-in-from-top-1 duration-150">
                  <div>
                    <span className="font-bold text-foreground block uppercase tracking-wide text-[8px] text-muted-foreground mb-0.5">
                      Why Retrieved
                    </span>
                    <p className="leading-relaxed">
                      {doc.whyRetrieved || 'Vector matching index scored high semantic relevance match on boiler parameters.'}
                    </p>
                  </div>
                  {doc.size && (
                    <div className="flex justify-between text-[9px] border-t border-border/40 pt-1.5 font-medium">
                      <span>Payload Size:</span>
                      <b className="text-foreground">{(doc.size / 1024).toFixed(1)} KB</b>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
