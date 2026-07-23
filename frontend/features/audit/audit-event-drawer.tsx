'use client';

import React from 'react';
import { X, Shield, Calendar, User, Settings, Database, MessageSquare } from 'lucide-react';
import { AuditEvent } from './audit-timeline';
import { useRouter } from 'next/navigation';

interface AuditEventDrawerProps {
  event: AuditEvent | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function AuditEventDrawer({
  event,
  isOpen,
  onClose,
}: AuditEventDrawerProps) {
  const router = useRouter();

  if (!isOpen || !event) return null;

  const handleDocRedirect = () => {
    onClose();
    router.push('/transparency');
  };

  const handleConvRedirect = () => {
    onClose();
    router.push('/history');
  };

  return (
    <div className="w-full lg:w-96 shrink-0 border-l border-border bg-card/40 flex flex-col h-full overflow-hidden animate-in slide-in-from-right duration-250 z-30">
      {/* Title Header */}
      <div className="p-4 border-b border-border flex justify-between items-center bg-card">
        <div className="flex items-center gap-2">
          <Shield className="h-4.5 w-4.5 text-primary shrink-0" />
          <h2 className="text-sm font-bold text-foreground">Audit Log details</h2>
        </div>
        <button
          onClick={onClose}
          className="rounded p-1 hover:bg-secondary text-muted-foreground hover:text-foreground cursor-pointer"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5 text-xs text-muted-foreground leading-normal">
        {/* Basic ID details */}
        <div className="space-y-1 rounded-lg border border-border/80 bg-secondary/15 p-4 text-center">
          <span className="text-[9px] font-bold uppercase tracking-wider block">
            Transaction Event ID
          </span>
          <div className="font-mono text-sm font-bold text-foreground tracking-wide select-all">
            {event.id}
          </div>
        </div>

        {/* Audit Details */}
        <div className="space-y-3 pt-2">
          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block border-b border-border/40 pb-1">
            System Parameters
          </span>
          
          {/* Timestamp */}
          <div className="flex gap-3 items-start">
            <Calendar className="h-4 w-4 text-primary shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <span className="font-bold text-foreground block">Event Timestamp</span>
              <span>{event.timestamp}</span>
            </div>
          </div>

          {/* Action */}
          <div className="flex gap-3 items-start">
            <Shield className="h-4 w-4 text-primary shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <span className="font-bold text-foreground block">Action Type</span>
              <span>{event.action}</span>
            </div>
          </div>

          {/* User */}
          <div className="flex gap-3 items-start">
            <User className="h-4 w-4 text-primary shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <span className="font-bold text-foreground block">Initiator User</span>
              <span className="font-semibold text-foreground">{event.user}</span>
            </div>
          </div>

          {/* Module */}
          <div className="flex gap-3 items-start">
            <Settings className="h-4 w-4 text-primary shrink-0" />
            <div className="space-y-0.5">
              <span className="font-bold text-foreground block">Component Module</span>
              <span className="capitalize">{event.module}</span>
            </div>
          </div>

          {/* Related Document (with module link) */}
          {event.relatedDoc && (
            <div className="flex gap-3 items-start">
              <Database className="h-4 w-4 text-primary shrink-0" />
              <div className="space-y-0.5 flex-1 min-w-0">
                <span className="font-bold text-foreground block">Staged Document</span>
                <button
                  type="button"
                  onClick={handleDocRedirect}
                  className="font-semibold text-primary hover:underline truncate max-w-full text-left"
                >
                  {event.relatedDoc}
                </button>
              </div>
            </div>
          )}

          {/* Related Conversation (with module link) */}
          {event.relatedConvId && (
            <div className="flex gap-3 items-start">
              <MessageSquare className="h-4 w-4 text-primary shrink-0" />
              <div className="space-y-0.5">
                <span className="font-bold text-foreground block">Conversation Reference</span>
                <button
                  type="button"
                  onClick={handleConvRedirect}
                  className="font-semibold text-primary hover:underline"
                >
                  Chat Thread: {event.relatedConvId}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Notes */}
        <div className="space-y-2 pt-2">
          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block border-b border-border/40 pb-1">
            Governance Audit Log Comments
          </span>
          <div className="rounded-lg border border-border bg-secondary/15 p-3 leading-relaxed font-normal">
            {event.notes}
          </div>
        </div>

      </div>
    </div>
  );
}
