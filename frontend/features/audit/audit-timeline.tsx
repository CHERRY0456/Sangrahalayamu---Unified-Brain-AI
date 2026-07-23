'use client';

import React from 'react';
import { AlertTriangle, Info, ShieldAlert, CheckCircle, Database } from 'lucide-react';
import { useRouter } from 'next/navigation';

export interface AuditEvent {
  id: string;
  action: string;
  timestamp: string;
  user: string;
  status: 'Success' | 'Pending' | 'Warning' | 'Failed';
  severity: 'Info' | 'Medium' | 'High' | 'Critical';
  relatedDoc?: string;
  relatedConvId?: string;
  module: string;
  notes: string;
}

interface AuditTimelineProps {
  events: AuditEvent[];
  selectedId: string;
  onSelectEvent: (event: AuditEvent) => void;
}

export default function AuditTimeline({
  events,
  selectedId,
  onSelectEvent,
}: AuditTimelineProps) {
  const router = useRouter();

  const getStatusColor = (status: AuditEvent['status']) => {
    switch (status) {
      case 'Success':
        return 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500';
      case 'Pending':
        return 'bg-blue-500/10 border-blue-500/20 text-blue-500';
      case 'Warning':
        return 'bg-amber-500/10 border-amber-500/20 text-amber-500';
      case 'Failed':
        return 'bg-destructive/10 border-destructive/20 text-destructive';
    }
  };

  const getSeverityColor = (sev: AuditEvent['severity']) => {
    switch (sev) {
      case 'Info':
        return 'bg-secondary text-muted-foreground border-border';
      case 'Medium':
        return 'bg-blue-500/10 border-blue-500/20 text-blue-500';
      case 'High':
        return 'bg-amber-500/10 border-amber-500/20 text-amber-500';
      case 'Critical':
        return 'bg-destructive/15 border-destructive/30 text-destructive font-bold animate-pulse';
    }
  };

  const handleDocClick = (e: React.MouseEvent, docName: string) => {
    e.stopPropagation();
    // Cross-link: Route to transparency snapshot overview
    router.push('/transparency');
  };

  const handleConvClick = (e: React.MouseEvent, convId: string) => {
    e.stopPropagation();
    // Cross-link: Route to conversation history inspector
    router.push('/history');
  };

  return (
    <div className="rounded-xl border border-border bg-card shadow-sm overflow-hidden animate-in fade-in duration-200">
      <div className="p-4 border-b border-border bg-card">
        <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
          Enterprise Audit Trace Logs
        </h2>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-border/80 text-[10px] font-bold text-muted-foreground uppercase tracking-wider bg-secondary/35">
              <th className="p-3.5">Action Event</th>
              <th className="p-3.5">Timestamp</th>
              <th className="p-3.5">User</th>
              <th className="p-3.5">Status</th>
              <th className="p-3.5">Severity</th>
              <th className="p-3.5">Related Object</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40">
            {events.map((event) => {
              const isSelected = selectedId === event.id;

              return (
                <tr
                  key={event.id}
                  onClick={() => onSelectEvent(event)}
                  className={`hover:bg-secondary/15 transition-colors cursor-pointer ${
                    isSelected ? 'bg-secondary/25' : ''
                  }`}
                >
                  {/* Action */}
                  <td className="p-3.5 font-bold text-foreground">
                    {event.action}
                  </td>
                  
                  {/* Timestamp */}
                  <td className="p-3.5 text-muted-foreground font-mono">
                    {event.timestamp}
                  </td>
                  
                  {/* User */}
                  <td className="p-3.5 text-foreground font-semibold">
                    {event.user}
                  </td>
                  
                  {/* Status */}
                  <td className="p-3.5">
                    <span className={`rounded-full border px-2 py-0.5 text-[9px] font-bold uppercase ${getStatusColor(event.status)}`}>
                      {event.status}
                    </span>
                  </td>

                  {/* Severity */}
                  <td className="p-3.5">
                    <span className={`rounded border px-1.5 py-0.5 text-[9px] font-bold uppercase ${getSeverityColor(event.severity)}`}>
                      {event.severity}
                    </span>
                  </td>

                  {/* Cross-linked Document/Conversation */}
                  <td className="p-3.5">
                    {event.relatedDoc ? (
                      <button
                        type="button"
                        onClick={(e) => handleDocClick(e, event.relatedDoc!)}
                        className="inline-flex items-center gap-1 text-[10px] font-semibold text-primary hover:underline"
                        title="Audit Document RAG metadata"
                      >
                        <Database className="h-3 w-3" />
                        {event.relatedDoc}
                      </button>
                    ) : event.relatedConvId ? (
                      <button
                        type="button"
                        onClick={(e) => handleConvClick(e, event.relatedConvId!)}
                        className="inline-flex items-center gap-1 text-[10px] font-semibold text-primary hover:underline"
                        title="View conversation timeline"
                      >
                        Chat ID: {event.relatedConvId}
                      </button>
                    ) : (
                      <span className="text-muted-foreground/45 italic">—</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
