'use client';

import React from 'react';
import DynamicDashboardComposer from '@/features/persona/dynamic-dashboard-composer';

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Operational Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Real-time metrics, system status widgets, and role-based action triggers.
        </p>
      </div>

      {/* Dynamic Persona-Aware Composer */}
      <DynamicDashboardComposer />
    </div>
  );
}
