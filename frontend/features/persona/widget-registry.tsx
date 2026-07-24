'use client';

import React from 'react';
import { ShieldAlert, Wrench, Calendar, FileText, LayoutList, CheckCircle2, TrendingDown, RefreshCw, BarChart4, AlertOctagon, HelpCircle, Lock, Check, X } from 'lucide-react';
import { usePersonaStore } from './persona-context';
import { api } from '@/lib/api-client';

export const WIDGET_REGISTRY: Record<string, React.ComponentType> = {
  'processing-queue': () => {
    const [queueCount, setQueueCount] = React.useState<number>(0);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
      const checkQueue = async () => {
        try {
          const data = await api.get<any>('/api/upload'); // using /api/upload since status might not exist
          const processing = (data.documents || []).filter((d: any) => d.status === 'PROCESSING');
          setQueueCount(processing.length);
        } catch (e) {
          console.error(e);
        } finally {
          setLoading(false);
        }
      };
      checkQueue();
      const interval = setInterval(checkQueue, 10000);
      return () => clearInterval(interval);
    }, []);

    return (
      <div className="rounded-xl border border-border bg-card p-4 space-y-2">
        <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">AI Ingestion Pipeline</h3>
        <div className="flex justify-between items-center text-xs">
          <span className="text-muted-foreground">Queue Status:</span>
          {loading ? (
            <span className="text-muted-foreground animate-pulse">Checking...</span>
          ) : queueCount > 0 ? (
            <span className="inline-flex items-center gap-1 text-amber-500 font-bold">
              <RefreshCw className="h-3.5 w-3.5 animate-spin" /> {queueCount} Processing
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-emerald-500 font-bold">
              <CheckCircle2 className="h-3.5 w-3.5" /> Idle
            </span>
          )}
        </div>
      </div>
    );
  },

  'access-requests': () => {
    const { accessRequests, approveAccessRequest, rejectAccessRequest } = usePersonaStore();
    const pendingRequests = accessRequests.filter((r) => r.status === 'Pending');

    return (
      <div className="rounded-xl border border-border bg-card p-4 space-y-3 col-span-1 md:col-span-2">
        <div className="flex justify-between items-center border-b border-border/40 pb-2">
          <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
            <Lock className="h-3.5 w-3.5 text-amber-500 shrink-0" />
            Access Clearance Queue
          </h3>
          <span className="text-[10px] font-bold bg-secondary px-2 py-0.5 rounded text-foreground font-mono">
            {pendingRequests.length} Pending
          </span>
        </div>

        {accessRequests.length === 0 ? (
          <p className="text-[11px] text-muted-foreground italic text-center py-4">No access tickets registered.</p>
        ) : (
          <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
            {accessRequests.map((req) => (
              <div
                key={req.id}
                className="rounded-lg border border-border/60 bg-secondary/10 p-2.5 space-y-2 text-xs"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <span className="font-extrabold text-foreground truncate block max-w-[180px]">{req.documentName}</span>
                    <span className="text-[9px] text-muted-foreground block font-semibold mt-0.5">
                      User: <b>{req.employeeName} ({req.employeeId})</b>
                    </span>
                  </div>
                  <span className={`rounded px-1.5 py-0.5 text-[8px] font-black uppercase tracking-wider ${
                    req.status === 'Approved'
                      ? 'bg-emerald-500/15 text-emerald-500 border border-emerald-500/25'
                      : req.status === 'Rejected'
                      ? 'bg-destructive/15 text-destructive border border-destructive/25'
                      : 'bg-amber-500/15 text-amber-500 border border-amber-500/25'
                  }`}>
                    {req.status}
                  </span>
                </div>

                <div className="text-[10px] space-y-0.5 text-muted-foreground/80">
                  <p>Target Section: <span className="font-semibold text-foreground">{req.section}</span></p>
                  <p>Match Relevance: <span className="font-bold text-amber-500">{req.relevanceScore}%</span></p>
                  <p className="italic text-[9px] border-l-2 border-border/80 pl-2 mt-1.5 leading-normal text-muted-foreground">
                    Reason: "{req.reason}"
                  </p>
                </div>

                {req.status === 'Pending' && (
                  <div className="flex justify-end gap-1.5 pt-1.5 border-t border-border/40">
                    <button
                      type="button"
                      onClick={() => rejectAccessRequest(req.id)}
                      className="inline-flex items-center gap-1 rounded bg-destructive hover:bg-destructive/90 text-white font-bold text-[9px] px-2 py-1 shadow-sm transition-all cursor-pointer"
                    >
                      <X className="h-2.5 w-2.5" />
                      Reject
                    </button>
                    <button
                      type="button"
                      onClick={() => approveAccessRequest(req.id)}
                      className="inline-flex items-center gap-1 rounded bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-[9px] px-2 py-1 shadow-sm transition-all cursor-pointer"
                    >
                      <Check className="h-2.5 w-2.5" />
                      Approve
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  },

  'ai-usage-analytics': () => {
    const [auditCount, setAuditCount] = React.useState<number>(0);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
      const fetchLogs = async () => {
        try {
          const data = await api.get<any[]>('/api/audit/events');
          setAuditCount(data.length || 0);
        } catch (e) {
          console.error(e);
        } finally {
          setLoading(false);
        }
      };
      fetchLogs();
    }, []);

    return (
      <div className="rounded-xl border border-border bg-card p-4 space-y-2">
        <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">AI Platform Usage</h3>
        <div className="text-xs space-y-1">
          <div className="flex justify-between">
            <span>Platform Audit Logs:</span>
            <span className="font-bold">{loading ? '...' : auditCount} event{auditCount === 1 ? '' : 's'}</span>
          </div>
          <div className="flex justify-between">
            <span>System Status:</span>
            <span className="font-bold text-emerald-500">Operational</span>
          </div>
        </div>
      </div>
    );
  },

  'risk-heatmap': () => {
    const [highRiskCount, setHighRiskCount] = React.useState<number>(0);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
      const fetchLogs = async () => {
        try {
          const data = await api.get<any[]>('/api/audit/events');
          const criticals = data.filter((d: any) => d.severity === 'HIGH' || d.severity === 'CRITICAL');
          setHighRiskCount(criticals.length);
        } catch (e) {
          console.error(e);
        } finally {
          setLoading(false);
        }
      };
      fetchLogs();
    }, []);

    return (
      <div className="rounded-xl border border-border bg-card p-4 space-y-2">
        <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Operational Risk Map</h3>
        <div className="flex justify-between items-center text-xs pt-1">
          <span>Active High-Risk Items:</span>
          {loading ? (
            <span className="text-muted-foreground">...</span>
          ) : highRiskCount > 0 ? (
            <span className="rounded bg-destructive/10 text-destructive border border-destructive/25 px-2 py-0.5 font-bold uppercase text-[9px]">
              {highRiskCount} Critical Alert{highRiskCount === 1 ? '' : 's'}
            </span>
          ) : (
            <span className="rounded bg-emerald-500/10 text-emerald-500 border border-emerald-500/25 px-2 py-0.5 font-bold uppercase text-[9px]">
              0 Alerts
            </span>
          )}
        </div>
      </div>
    );
  },

  'knowledge-coverage': () => {
    const [files, setFiles] = React.useState<any[]>([]);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
      const fetchFiles = async () => {
        try {
          const data = await api.get<any>('/api/upload');
          setFiles(data.documents || []);
        } catch (e) {
          console.error(e);
        } finally {
          setLoading(false);
        }
      };
      fetchFiles();
    }, []);

    const totalSizeBytes = files.reduce((acc, f) => acc + (f.file_size || 0), 0);
    const totalSizeFormatted = totalSizeBytes > 1024 * 1024
      ? `${(totalSizeBytes / (1024 * 1024)).toFixed(1)} MB`
      : `${(totalSizeBytes / 1024).toFixed(1)} KB`;

    const uniqueClassifications = Array.from(new Set(files.map(f => f.classification))).filter(Boolean);

    return (
      <div className="rounded-xl border border-border bg-card p-4 space-y-2 col-span-1">
        <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider font-semibold">Staged Knowledge Base</h3>
        {loading ? (
          <div className="text-xs font-bold text-muted-foreground animate-pulse">Loading size...</div>
        ) : files.length === 0 ? (
          <div className="text-[11px] text-muted-foreground italic py-1">No knowledge ingested. Database is empty.</div>
        ) : (
          <>
            <div className="text-xs font-bold text-foreground">
              {totalSizeFormatted} / {files.length} Ingested Document{files.length === 1 ? '' : 's'}
            </div>
            <p className="text-[10px] text-muted-foreground mt-1">
              Clearance Levels: {uniqueClassifications.join(', ') || 'None'}
            </p>
          </>
        )}
      </div>
    );
  },

  'recent-uploads': () => {
    const { persona, isDocumentAccessible } = usePersonaStore();
    const [files, setFiles] = React.useState<any[]>([]);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
      const fetchFiles = async () => {
        try {
          const data = await api.get<any>('/api/upload');
          setFiles(data.documents || []);
        } catch (e) {
          console.error(e);
        } finally {
          setLoading(false);
        }
      };
      fetchFiles();
    }, []);

    // Filter files based on user clearance role:
    const filteredFiles = files.filter((file) => {
      return isDocumentAccessible(file.name);
    });

    return (
      <div className="rounded-xl border border-border bg-card p-4 space-y-3 col-span-1 md:col-span-2">
        <div className="flex justify-between items-center border-b border-border/40 pb-2">
          <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
            <FileText className="h-3.5 w-3.5 text-primary shrink-0" />
            Clearance-Filtered Ingested Files
          </h3>
          <span className="text-[9px] font-bold text-emerald-500 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
            Clearance Checked
          </span>
        </div>

        {loading ? (
          <p className="text-[11px] text-muted-foreground italic text-center py-2 animate-pulse">Loading documents...</p>
        ) : filteredFiles.length === 0 ? (
          <p className="text-[11px] text-muted-foreground italic text-center py-4">No documents available in your clearance tier. The database is empty.</p>
        ) : (
          <div className="grid gap-2">
            {filteredFiles.map((file) => (
              <div 
                key={file.id || file.name} 
                className="flex items-center justify-between rounded-lg border border-border/50 bg-secondary/15 p-2 text-xs"
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className="rounded p-1.5 bg-primary/10 text-primary shrink-0">
                    <FileText className="h-4 w-4" />
                  </div>
                  <div className="min-w-0">
                    <span className="font-bold text-foreground block truncate max-w-[200px]">{file.name}</span>
                    <span className="text-[9px] text-muted-foreground block truncate">
                      Classification: {file.classification} • Ingested: {new Date(file.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                <div className="text-[9px] font-bold bg-primary/10 text-primary px-1.5 py-0.5 rounded shrink-0">
                  {file.required_clearance}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  },

  'my-requests': () => {
    const { profile, accessRequests } = usePersonaStore();
    
    // Filter requests submitted by the active profile
    const myRequests = accessRequests.filter((r) => r.employeeId === profile?.employeeId);

    return (
      <div className="rounded-xl border border-border bg-card p-4 space-y-3 col-span-1 md:col-span-2">
        <div className="flex justify-between items-center border-b border-border/40 pb-2">
          <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
            <Lock className="h-3.5 w-3.5 text-primary shrink-0" />
            My Clearance Requests
          </h3>
          <span className="text-[10px] font-bold bg-secondary px-2 py-0.5 rounded text-foreground font-mono">
            {myRequests.length} Total
          </span>
        </div>

        {myRequests.length === 0 ? (
          <p className="text-[11px] text-muted-foreground italic text-center py-4">No override requests submitted yet.</p>
        ) : (
          <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
            {myRequests.map((req) => (
              <div
                key={req.id}
                className="rounded-lg border border-border/60 bg-secondary/15 p-2.5 space-y-1.5 text-xs"
              >
                <div className="flex justify-between items-start gap-2">
                  <div>
                    <span className="font-extrabold text-foreground truncate block max-w-[170px]">{req.documentName}</span>
                    <span className="text-[9px] text-muted-foreground block font-medium mt-0.5">
                      Requested: {req.section}
                    </span>
                  </div>
                  <span className={`rounded px-1.5 py-0.5 text-[8px] font-black uppercase tracking-wider ${
                    req.status === 'Approved'
                      ? 'bg-emerald-500/15 text-emerald-500 border border-emerald-500/25 font-bold'
                      : req.status === 'Rejected'
                      ? 'bg-destructive/15 text-destructive border border-destructive/25 font-bold'
                      : 'bg-amber-500/15 text-amber-500 border border-amber-500/25 font-bold'
                  }`}>
                    {req.status === 'Approved' ? 'Approved ✓' : req.status === 'Rejected' ? 'Rejected ✗' : 'Pending ⏳'}
                  </span>
                </div>
                
                {req.status === 'Approved' && (
                  <p className="text-[9px] text-emerald-500 font-bold bg-emerald-500/5 px-2 py-1 rounded border border-emerald-500/10">
                    Access Granted! This resource is now searchable and visible in your dashboard feeds.
                  </p>
                )}
                {req.status === 'Rejected' && (
                  <p className="text-[9px] text-red-400 font-semibold bg-destructive/5 px-2 py-1 rounded border border-destructive/10">
                    Clearance Denied. Contact corporate safety compliance admin.
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  },
};
