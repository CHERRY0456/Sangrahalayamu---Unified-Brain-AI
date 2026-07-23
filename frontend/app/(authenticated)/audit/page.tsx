'use client';

import React, { useState, useEffect } from 'react';
import AuditDashboard from '@/features/audit/audit-dashboard';
import { AuditEvent } from '@/features/audit/audit-timeline';
import PermissionGuard from '@/features/persona/permission-guard';

export default function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);

  useEffect(() => {
    async function fetchEvents() {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const token = localStorage.getItem('ib-access-token');
        const res = await fetch(`${baseUrl}/api/audit/events?limit=100`, {
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
          }
        });
        if (res.ok) {
          const data = await res.json();
          setEvents(data);
        }
      } catch (err) {
        console.error('Failed to fetch audit events:', err);
      }
    }
    fetchEvents();
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
      <AuditDashboard events={events} />
      </div>
    </PermissionGuard>
  );
}
