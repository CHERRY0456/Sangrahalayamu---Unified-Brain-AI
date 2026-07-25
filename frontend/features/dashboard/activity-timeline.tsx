'use client';

import React, { useState, useEffect } from 'react';
import { Upload, CheckCircle2, MessageSquare, ShieldAlert } from 'lucide-react';
import { api } from '@/lib/api-client';

export default function ActivityTimeline() {
  const [activities, setActivities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchAuditEvents() {
      try {
        const events = await api.get<any[]>('/api/v1/audit/events?limit=5');
        if (Array.isArray(events)) {
          setActivities(events);
        }
      } catch (err) {
        console.error('Failed to fetch activity timeline events:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchAuditEvents();
  }, []);

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm flex flex-col h-full">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">
        Recent Repository Activity
      </h2>
      {loading ? (
        <p className="text-xs text-muted-foreground animate-pulse py-6 text-center">
          Loading system activity logs...
        </p>
      ) : activities.length === 0 ? (
        <div className="py-8 text-center space-y-1">
          <CheckCircle2 className="h-8 w-8 text-muted-foreground/40 mx-auto" />
          <p className="text-xs text-muted-foreground">No recent system activity recorded.</p>
        </div>
      ) : (
        <div className="flex-1 space-y-6 relative before:absolute before:left-[14px] before:top-3 before:bottom-3 before:w-0.5 before:bg-border">
          {activities.map((act, i) => {
            const isUpload = act.module === 'upload';
            const isChat = act.module === 'chat';
            const Icon = isUpload ? Upload : isChat ? MessageSquare : ShieldAlert;
            const color = isUpload
              ? 'text-primary bg-primary/10 border-primary/20'
              : isChat
              ? 'text-blue-500 bg-blue-500/10 border-blue-500/20'
              : 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';

            return (
              <div key={act.id || i} className="relative flex items-start animate-in fade-in duration-200">
                <div
                  className={`relative z-10 flex h-7 w-7 items-center justify-center rounded-full border shrink-0 ${color}`}
                  style={{ backgroundColor: 'hsl(var(--card))' }}
                >
                  <Icon className="h-3.5 w-3.5 shrink-0" />
                </div>
                <div 
                  className="space-y-0.5 flex-1 min-w-0"
                  style={{ marginLeft: '16px' }}
                >
                  <div className="text-xs font-bold text-foreground leading-none">{act.action || 'System Event'}</div>
                  <p className="text-[11px] text-muted-foreground leading-tight mt-0.5">{act.details?.description || act.resource || 'Action performed'}</p>
                  <span className="block text-[10px] text-muted-foreground/60 font-medium mt-1">
                    {act.timestamp ? new Date(act.timestamp).toLocaleTimeString() : 'Recently'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
