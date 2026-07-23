import React from 'react';
import { MessageSquare, FileUp, Cpu, Eye, Key, Hammer } from 'lucide-react';

interface AuditSummaryCardsProps {
  totalConversations: number;
  docsUploaded: number;
  aiResponses: number;
  transparencySessions: number;
  accessRequests: number;
  processingJobs: number;
}

export default function AuditSummaryCards({
  totalConversations,
  docsUploaded,
  aiResponses,
  transparencySessions,
  accessRequests,
  processingJobs,
}: AuditSummaryCardsProps) {
  
  const items = [
    { label: 'Audit Conversations', val: totalConversations, icon: MessageSquare, color: 'text-blue-500 bg-blue-500/10' },
    { label: 'Documents Uploaded', val: docsUploaded, icon: FileUp, color: 'text-primary bg-primary/10' },
    { label: 'Responses Generated', val: aiResponses, icon: Cpu, color: 'text-purple-500 bg-purple-500/10' },
    { label: 'RAG Audit Sessions', val: transparencySessions, icon: Eye, color: 'text-emerald-500 bg-emerald-500/10' },
    { label: 'Access Requests', val: accessRequests, icon: Key, color: 'text-amber-500 bg-amber-500/10' },
    { label: 'Processing Jobs', val: processingJobs, icon: Hammer, color: 'text-indigo-500 bg-indigo-500/10' },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {items.map((item, idx) => {
        const Icon = item.icon;
        return (
          <div
            key={idx}
            className="rounded-xl border border-border bg-card p-4 space-y-2 shadow-sm"
          >
            <div className="flex justify-between items-start">
              <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider leading-none">
                {item.label}
              </span>
              <div className={`rounded p-1 ${item.color} shrink-0`}>
                <Icon className="h-4 w-4" />
              </div>
            </div>
            <div className="text-xl font-black text-foreground">
              {item.val}
            </div>
          </div>
        );
      })}
    </div>
  );
}
