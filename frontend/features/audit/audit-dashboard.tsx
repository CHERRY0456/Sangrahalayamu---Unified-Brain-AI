'use client';

import React, { useState } from 'react';
import AuditSummaryCards from './audit-summary-cards';
import AuditTimeline, { AuditEvent } from './audit-timeline';
import AuditEventDrawer from './audit-event-drawer';
import { Search } from 'lucide-react';

interface AuditDashboardProps {
  events: AuditEvent[];
}

export default function AuditDashboard({ events }: AuditDashboardProps) {
  const [selectedEvent, setSelectedEvent] = useState<AuditEvent | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  
  // Filters & Search states
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [moduleFilter, setModuleFilter] = useState('all');

  const handleSelectEvent = (event: AuditEvent) => {
    setSelectedEvent(event);
    setIsDrawerOpen(true);
  };

  // KPI Calculations
  const totalConversations = 6;
  const docsUploaded = 14;
  const aiResponses = 88;
  const transparencySessions = 34;
  const accessRequests = 5;
  const processingJobs = 21;

  // Filter Event Logs
  const filteredEvents = events.filter((ev) => {
    const matchesSearch =
      ev.id.toLowerCase().includes(search.toLowerCase()) ||
      ev.action.toLowerCase().includes(search.toLowerCase()) ||
      ev.user.toLowerCase().includes(search.toLowerCase()) ||
      (ev.relatedDoc && ev.relatedDoc.toLowerCase().includes(search.toLowerCase())) ||
      (ev.relatedConvId && ev.relatedConvId.toLowerCase().includes(search.toLowerCase()));

    const matchesStatus = statusFilter === 'all' || ev.status === statusFilter;
    const matchesSeverity = severityFilter === 'all' || ev.severity === severityFilter;
    const matchesModule = moduleFilter === 'all' || ev.module === moduleFilter;

    return matchesSearch && matchesStatus && matchesSeverity && matchesModule;
  });

  return (
    <div className="space-y-6">
      
      {/* 1. Summary KPI Metrics */}
      <AuditSummaryCards
        totalConversations={totalConversations}
        docsUploaded={docsUploaded}
        aiResponses={aiResponses}
        transparencySessions={transparencySessions}
        accessRequests={accessRequests}
        processingJobs={processingJobs}
      />

      {/* 2. Advanced Search & Filters Console */}
      <div className="rounded-xl border border-border bg-card p-4 shadow-sm grid gap-4 md:grid-cols-4 items-end">
        {/* Search */}
        <div className="space-y-1.5 md:col-span-1">
          <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
            Search Audit Trails
          </label>
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground/60" />
            <input
              type="text"
              placeholder="Search Event ID, users, docs..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-lg border border-border bg-background pl-8 pr-3 py-2 text-xs text-foreground outline-none focus:border-primary placeholder:text-muted-foreground/50"
            />
          </div>
        </div>

        {/* Status */}
        <div className="space-y-1.5">
          <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
            Status
          </label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full rounded-lg border border-border bg-background p-2 text-xs text-foreground outline-none cursor-pointer"
          >
            <option value="all">All Statuses</option>
            <option value="Success">Success</option>
            <option value="Pending">Pending</option>
            <option value="Warning">Warning</option>
            <option value="Failed">Failed</option>
          </select>
        </div>

        {/* Severity */}
        <div className="space-y-1.5">
          <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
            Severity
          </label>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="w-full rounded-lg border border-border bg-background p-2 text-xs text-foreground outline-none cursor-pointer"
          >
            <option value="all">All Severities</option>
            <option value="Info">Info</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
            <option value="Critical">Critical</option>
          </select>
        </div>

        {/* Module */}
        <div className="space-y-1.5">
          <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
            System Module
          </label>
          <select
            value={moduleFilter}
            onChange={(e) => setModuleFilter(e.target.value)}
            className="w-full rounded-lg border border-border bg-background p-2 text-xs text-foreground outline-none cursor-pointer"
          >
            <option value="all">All Modules</option>
            <option value="upload">Upload</option>
            <option value="processing">Processing</option>
            <option value="chat">Chat</option>
            <option value="transparency">Explainability</option>
            <option value="auth">Auth</option>
          </select>
        </div>
      </div>

      {/* 3. Timeline Audit Listing & Detail Drawer Split Layout */}
      <div className="flex flex-col lg:flex-row overflow-hidden gap-6 items-start">
        
        {/* Table listing */}
        <div className="flex-1 w-full min-w-0">
          <AuditTimeline
            events={filteredEvents}
            selectedId={selectedEvent?.id || ''}
            onSelectEvent={handleSelectEvent}
          />
        </div>

        {/* Collapsible details inspector drawer */}
        <AuditEventDrawer
          event={selectedEvent}
          isOpen={isDrawerOpen}
          onClose={() => setIsDrawerOpen(false)}
        />
      </div>

    </div>
  );
}
