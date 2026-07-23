'use client';

import React from 'react';
import TransparencyDashboard from '@/features/transparency/transparency-dashboard';
import { ExplanationSnapshot } from '@/features/transparency/response-list';
import { ExplanationData } from '@/features/transparency/transparency-panel';
import PermissionGuard from '@/features/persona/permission-guard';


export default function TransparencyPage() {
  return (
    <PermissionGuard permission="transparency">
      <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-300">
      {/* Page Title */}
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Explainability Center</h1>
        <p className="text-sm text-muted-foreground">
          Audit, compare, and verify how the AI reached its conclusions across previous explanation snapshots.
        </p>
      </div>

      {/* Orchestrator Dashboard */}
      <TransparencyDashboard
        snapshots={[]}
        explanations={{}}
      />
      </div>
    </PermissionGuard>
  );
}
