'use client';

import React from 'react';
import { usePersonaStore } from './persona-context';
import { WIDGET_REGISTRY } from './widget-registry';
import { Play, Building, UserCheck } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function DynamicDashboardComposer() {
  const router = useRouter();
  const { profile, persona, workspaceManifest, isRestoringSession } = usePersonaStore();

  if (isRestoringSession) {
    return (
      <div className="flex h-[400px] w-full items-center justify-center rounded-xl border border-border bg-card/50">
        <div className="flex flex-col items-center gap-4">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-r-transparent"></div>
          <p className="text-sm font-semibold text-muted-foreground animate-pulse">Restoring workspace session...</p>
        </div>
      </div>
    );
  }

  if (!profile || !persona || !workspaceManifest) return null;

  const handleActionClick = (url: string) => {
    router.push(url);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      
      {/* 1. Welcome Greeting Banner */}
      <div className="rounded-xl border border-border bg-card p-6 shadow-sm relative overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-gradient-to-r from-card via-card/90 to-primary/5">
        <div className="space-y-2">
          <span className="text-[10px] font-bold text-primary uppercase tracking-wider block flex items-center gap-1">
            <UserCheck className="h-3.5 w-3.5" />
            Authenticated Identity System
          </span>
          <h2 className="text-xl font-black text-foreground">
            Welcome Back, {profile.name}
          </h2>
          <div className="text-xs text-muted-foreground space-y-1 font-semibold">
            <p>Designation: <span className="text-foreground">{profile.designation}</span></p>
            <p className="flex items-center gap-1">
              <Building className="h-3.5 w-3.5 text-muted-foreground/60" />
              Department: {profile.department}
            </p>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-secondary/25 px-4 py-2 text-right shrink-0">
          <span className="text-[9px] text-muted-foreground block font-bold uppercase tracking-wider">
            Clearance Profile
          </span>
          <b className="text-xs text-foreground font-black capitalize block mt-0.5">
            {persona.role} Workspace
          </b>
          <span className="text-[9px] text-primary block mt-1 font-semibold">
            Configured for Operations
          </span>
        </div>
      </div>

      {/* 2. Persona Quick Actions section */}
      <div className="space-y-3">
        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
          Role-Aware Quick Operations
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          {workspaceManifest.quickActions.map((act, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleActionClick(act.actionUrl)}
              className="rounded-lg border border-border bg-card hover:bg-secondary/20 p-3.5 text-left transition-all cursor-pointer shadow-sm flex items-center justify-between group hover:border-primary/40"
            >
              <div className="space-y-1.5 min-w-0 pr-2">
                <span className="text-xs font-bold text-foreground group-hover:text-primary transition-colors block truncate">
                  {act.label}
                </span>
                <span className="text-[9px] text-muted-foreground font-medium block">
                  Navigate to module
                </span>
              </div>
              <Play className="h-3 w-3 text-muted-foreground/60 shrink-0 group-hover:text-primary group-hover:translate-x-0.5 transition-all" />
            </button>
          ))}
        </div>
      </div>

      {/* 3. Reusable Dashboard Widgets Grid */}
      <div className="space-y-3">
        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
          Dynamic Metrics Panels
        </span>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {workspaceManifest.dashboard.map((widgetId) => {
            const WidgetComponent = WIDGET_REGISTRY[widgetId];
            if (!WidgetComponent) return null;
            return <WidgetComponent key={widgetId} />;
          })}
        </div>
      </div>

    </div>
  );
}
