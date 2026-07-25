'use client';

import React, { useState, useEffect } from 'react';
import AuditDashboard from '@/features/audit/audit-dashboard';
import { AuditEvent } from '@/features/audit/audit-timeline';
import PermissionGuard from '@/features/persona/permission-guard';
import { api } from '@/lib/api-client';

export default function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [summaryStats, setSummaryStats] = useState<any>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const eventsData = await api.get<AuditEvent[]>('/api/v1/audit/events?limit=100');
        setEvents(eventsData);
        
        const statsData = await api.get<any>('/api/v1/audit/summary');
        setSummaryStats(statsData);
      } catch (err) {
        console.error('Failed to fetch audit data:', err);
      }
    }
    fetchData();
  }, []);

  return (
    <PermissionGuard permission="audit">
      <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-300">
      {/* Page Header */}
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Audit Center</h1>
        <p className="text-sm text-muted-foreground">
          Trace security actions, inspect governance timeline logs, and monitor RAG system access permissions.
        </p>
      </div>

      {/* Audit Dashboard Orchestrator */}
      <AuditDashboard events={events} summaryStats={summaryStats} />
      </div>
    </PermissionGuard>
  );
}
