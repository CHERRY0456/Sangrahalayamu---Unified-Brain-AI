'use client';

import React from 'react';
import { HistoryConversation } from './conversation-library';
import PromptTimeline, { TimelineEvent } from './prompt-timeline';
import ConversationMetrics from './conversation-metrics';
import { FileText, Play, Eye, Download, Info } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { showToast } from '@/lib/toast';

export interface InspectionDocument {
  name: string;
  category: string;
  confidence: 'High' | 'Medium' | 'Low';
  usedInResponse: boolean;
}

interface ConversationInspectorProps {
  conversation: HistoryConversation | null;
  events: TimelineEvent[];
  documents: InspectionDocument[];
  // Metrics
  avgConfidence: number;
  explainabilityScore: number;
  responsesGenerated: number;
  transparencyViews: number;
  accessRequests: number;
}

export default function ConversationInspector({
  conversation,
  events,
  documents,
  avgConfidence,
  explainabilityScore,
  responsesGenerated,
  transparencyViews,
  accessRequests,
}: ConversationInspectorProps) {
  const router = useRouter();

  if (!conversation) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-center text-muted-foreground italic h-full p-8 space-y-2">
        <Info className="h-6 w-6 text-muted-foreground/60" />
        <div className="text-xs font-bold text-foreground">No Conversation Selected</div>
        <p className="text-[10px] max-w-[200px] leading-normal">
          Select an explanation session in the left library list to inspect detailed audit trails and prompt progression logs.
        </p>
      </div>
    );
  }

  const handleContinue = () => {
    router.push('/chat');
  };

  const handleAuditRAG = () => {
    router.push('/transparency');
  };

  const handleExport = () => {
    const data = JSON.stringify({ conversation, events, documents }, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `conversation_${conversation.id}_audit.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Conversation audit log exported successfully.', 'success');
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6 h-full animate-in fade-in duration-200">
      
      {/* Title & Top Action bar */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-border/80 pb-4">
        <div>
          <h2 className="text-md font-bold text-foreground">{conversation.title}</h2>
          <p className="text-[11px] text-muted-foreground mt-0.5">
            Ingestion category: <span className="font-semibold text-foreground">{conversation.category}</span> • Session duration: <b>{conversation.duration}</b>
          </p>
        </div>

        {/* Global Module Jumps */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={handleExport}
            className="inline-flex items-center gap-1 rounded bg-secondary hover:bg-secondary/80 text-[10px] font-bold text-foreground px-2.5 py-1.5 transition-colors cursor-pointer border border-border"
          >
            <Download className="h-3.5 w-3.5" />
            Export Log
          </button>
          
          <button
            type="button"
            onClick={handleAuditRAG}
            className="inline-flex items-center gap-1 rounded bg-secondary hover:bg-secondary/80 text-[10px] font-bold text-foreground px-2.5 py-1.5 transition-colors cursor-pointer border border-border"
          >
            <Eye className="h-3.5 w-3.5" />
            Audit RAG
          </button>

          <button
            type="button"
            onClick={handleContinue}
            className="inline-flex items-center gap-1 rounded bg-primary hover:bg-primary/95 text-[10px] font-bold text-primary-foreground px-3 py-1.5 transition-colors cursor-pointer shadow-sm"
          >
            <Play className="h-3.5 w-3.5 fill-current shrink-0" />
            Continue Chat
          </button>
        </div>
      </div>

      {/* Summary KPI stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-secondary/15 rounded-xl border border-border p-4 text-xs">
        <div className="space-y-0.5">
          <span className="text-muted-foreground font-medium">Session State</span>
          <div className="font-bold text-foreground">{conversation.status}</div>
        </div>
        <div className="space-y-0.5">
          <span className="text-muted-foreground font-medium">Retrieval Mode</span>
          <div className="font-bold text-foreground capitalize">{conversation.retrievalMode}</div>
        </div>
        <div className="space-y-0.5">
          <span className="text-muted-foreground font-medium">Total Messages</span>
          <div className="font-bold text-foreground">
            {conversation.promptsCount + conversation.responsesCount} (User: {conversation.promptsCount}, AI: {conversation.responsesCount})
          </div>
        </div>
        <div className="space-y-0.5">
          <span className="text-muted-foreground font-medium">Documents Staged</span>
          <div className="font-bold text-foreground">{conversation.docCount} Files</div>
        </div>
      </div>

      {/* Prompt Timeline progression */}
      <PromptTimeline events={events} />

      <hr className="border-border/60" />

      {/* Attached Documents Table */}
      <div className="space-y-3">
        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
          Attached Document Context
        </span>
        <div className="overflow-x-auto border border-border/60 rounded-lg bg-card shadow-sm">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-border/80 text-[10px] font-bold text-muted-foreground uppercase tracking-wider bg-secondary/30">
                <th className="p-3">File Name</th>
                <th className="p-3">Category</th>
                <th className="p-3">Doc Confidence</th>
                <th className="p-3 text-right">RAG Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40">
              {documents.map((doc, idx) => (
                <tr key={idx} className="hover:bg-secondary/10 transition-colors">
                  <td className="p-3 flex items-center gap-2">
                    <FileText className="h-4 w-4 text-primary shrink-0" />
                    <span className="font-semibold text-foreground truncate max-w-[200px] sm:max-w-xs">
                      {doc.name}
                    </span>
                  </td>
                  <td className="p-3 text-muted-foreground">{doc.category}</td>
                  <td className="p-3">
                    <span className="font-semibold text-foreground">{doc.confidence}</span>
                  </td>
                  <td className="p-3 text-right">
                    {doc.usedInResponse ? (
                      <span className="inline-block rounded-full bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 text-[9px] font-bold uppercase text-emerald-500">
                        Used in Response
                      </span>
                    ) : (
                      <span className="inline-block rounded-full bg-neutral-500/10 border border-neutral-500/20 px-2 py-0.5 text-[9px] font-bold uppercase text-muted-foreground">
                        Not Referenced
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <hr className="border-border/60" />

      {/* Aggregate Governance metrics */}
      <ConversationMetrics
        avgConfidence={avgConfidence}
        explainabilityScore={explainabilityScore}
        responsesGenerated={responsesGenerated}
        transparencyViews={transparencyViews}
        accessRequests={accessRequests}
      />

    </div>
  );
}
