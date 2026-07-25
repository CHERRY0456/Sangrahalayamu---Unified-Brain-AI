'use client';

import React, { useState, useEffect } from 'react';
import { FileText, MessageSquare, Cpu, ShieldCheck } from 'lucide-react';
import { api } from '@/lib/api-client';

export default function SummaryCards() {
  const [stats, setStats] = useState({
    documents: 0,
    conversations: 0,
    activeTasks: 0,
    audits: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const data = await api.get<any>('/api/v1/dashboard/summary');
        if (data && data.data) {
          setStats({
            documents: data.data.total_documents || 0,
            conversations: data.data.total_conversations || 0,
            activeTasks: data.data.active_parser_tasks || 0,
            audits: data.data.total_audit_events || 0,
          });
        }
      } catch (err) {
        console.error('Failed to load dashboard summary stats:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, []);

  const items = [
    { label: 'Documents Ingested', value: loading ? '...' : stats.documents, icon: FileText, change: 'Ingested into Vector/Graph' },
    { label: 'AI Conversations', value: loading ? '...' : stats.conversations, icon: MessageSquare, change: 'Total Q&A sessions' },
    { label: 'Active Parser Tasks', value: loading ? '...' : stats.activeTasks, icon: Cpu, change: 'Docling OCR queue' },
    { label: 'Audit Records', value: loading ? '...' : stats.audits, icon: ShieldCheck, change: 'Logged system events' },
  ];

  return (
    <div className="grid gap-4 grid-cols-2 lg:grid-cols-4 w-full">
      {items.map((stat, i) => {
        const Icon = stat.icon;
        return (
          <div
            key={i}
            className="rounded-xl border border-border bg-card p-5 shadow-sm hover:shadow-md transition-all duration-200"
          >
            <div className="flex justify-between items-center text-muted-foreground mb-3">
              <span className="text-xs font-semibold tracking-wide uppercase truncate">
                {stat.label}
              </span>
              <Icon className="h-5 w-5 text-primary shrink-0" />
            </div>
            <div className="text-2xl font-bold text-foreground">{stat.value}</div>
            <p className="mt-1 text-[11px] text-muted-foreground font-medium">{stat.change}</p>
          </div>
        );
      })}
    </div>
  );
}
