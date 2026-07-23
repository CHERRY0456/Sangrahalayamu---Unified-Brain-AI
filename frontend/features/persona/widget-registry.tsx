'use client';

import React from 'react';
import { ShieldAlert, Wrench, Calendar, FileText, LayoutList, CheckCircle2, TrendingDown, RefreshCw, BarChart4, AlertOctagon, HelpCircle, Lock, Check, X } from 'lucide-react';
import { usePersonaStore } from './persona-context';

export const WIDGET_REGISTRY: Record<string, React.ComponentType> = {
  // 1. Field Technician Widgets
  'assigned-equipment': () => (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Assigned Equipment</h3>
      <div className="space-y-1.5 text-xs text-foreground font-semibold">
        <div className="flex justify-between border-b border-border/40 pb-1.5">
          <span>Boiler Cylinder B-3</span>
          <span className="text-emerald-500">Active</span>
        </div>
        <div className="flex justify-between border-b border-border/40 pb-1.5">
          <span>Primary Loop-A Valve</span>
          <span className="text-emerald-500">Active</span>
        </div>
        <div className="flex justify-between">
          <span>Coolant Pump P-2</span>
          <span className="text-amber-500">Inspection Due</span>
        </div>
      </div>
    </div>
  ),
  'recent-repairs': () => (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Recent Repairs</h3>
      <div className="space-y-1.5 text-xs text-muted-foreground">
        <p>• <b>Cylinder B-3</b>: Replaced pressure seals (2 days ago)</p>
        <p>• <b>Coolant Pump P-2</b>: Calibrated flow sensor (5 days ago)</p>
        <p>• <b>Exhaust Line L-4</b>: Cleared soot obstruction (1 week ago)</p>
      </div>
    </div>
  ),
  'safety-alerts': () => (
    <div className="rounded-xl border border-border bg-destructive/10 border-destructive/25 p-4 space-y-2 text-destructive">
      <div className="flex items-center gap-2">
        <ShieldAlert className="h-4 w-4 shrink-0" />
        <h3 className="text-xs font-bold uppercase tracking-wider">Safety Warnings</h3>
      </div>
      <p className="text-xs leading-relaxed font-semibold">
        Boiler 092 is operating near maximum standard pressure. Exceeding 320 PSI triggers shutoff.
      </p>
    </div>
  ),
  'equipment-history': () => (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Equipment History</h3>
      <div className="text-xs space-y-1">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Boiler 092 age:</span>
          <span className="font-bold">4.2 years</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Last overhaul:</span>
          <span className="font-bold">2025-11-12</span>
        </div>
      </div>
    </div>
  ),

  // 2. Maintenance Engineer Widgets
  'failure-trends': () => (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Failure Frequency Trends</h3>
      <div className="flex items-center gap-3">
        <div className="text-2xl font-black text-foreground">-14%</div>
        <div className="text-[10px] text-emerald-500 font-bold bg-emerald-500/10 px-1.5 py-0.5 rounded">
          Better vs Q2
        </div>
      </div>
      <p className="text-[10px] text-muted-foreground">Mean Time To Repair (MTTR) dropped to 1.8 hours.</p>
    </div>
  ),
  'maintenance-schedule': () => (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Upcoming Maintenance</h3>
      <div className="space-y-1 text-xs">
        <p className="font-semibold">• Boiler 092 Pressure Cal (Tomorrow)</p>
        <p className="font-semibold">• Coolant Refill Reactor 5 (July 25)</p>
      </div>
    </div>
  ),
  'uploaded-manuals': () => (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">OEM Manual Index</h3>
      <div className="text-2xl font-black text-foreground">14 Manuals</div>
      <p className="text-[10px] text-muted-foreground">Latest: <i>OSHA_Steam_Regulations_2026.pdf</i></p>
    </div>
  ),
  'processing-queue': () => (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">AI Ingestion Pipeline</h3>
      <div className="flex justify-between items-center text-xs">
        <span className="text-muted-foreground">Queue Status:</span>
        <span className="inline-flex items-center gap-1 text-emerald-500 font-bold">
          <CheckCircle2 className="h-3.5 w-3.5" /> Idle
        </span>
      </div>
    </div>
  ),

  // 3. Project Manager Widgets
  'project-status': () => (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Project Timeline Health</h3>
      <div className="text-2xl font-black text-foreground">94.2%</div>
      <p className="text-[10px] text-muted-foreground">On schedule for Q3 plant upgrades.</p>
    </div>
  ),
  'team-progress': () => (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Active Deliverables</h3>
      <div className="space-y-1 text-xs font-semibold">
        <div className="flex justify-between">
          <span>OCR BLUEPRINT INGESTION</span>
          <span className="text-emerald-500">Done</span>
        </div>
        <div className="flex justify-between">
          <span>SAFETY AUDIT VERIFICATION</span>
          <span className="text-amber-500">In Progress</span>
        </div>
      </div>
    </div>
  ),
  'project-delays': () => (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Reported Blockers</h3>
      <p className="text-xs text-amber-500 font-semibold leading-relaxed">
        • Delay in scheduling physical inspection for Reactor Loop-A.
      </p>
    </div>
  ),
  'resource-allocation': () => (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Resource Allocation</h3>
      <div className="text-xs font-bold text-foreground">7 Technicians / 2 Engineers</div>
      <p className="text-[10px] text-muted-foreground mt-1">Allocation efficiency optimized at 92.5% capacity.</p>
    </div>
  ),

  // 4. Compliance Widgets
  'pending-audits': () => (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Compliance Audits</h3>
      <div className="space-y-1.5 text-xs text-foreground font-semibold">
        <div className="flex justify-between">
          <span>OSHA Steam Standard</span>
          <span className="text-red-500 font-bold">1 Alert</span>
        </div>
        <div className="flex justify-between">
          <span>Reactor Blueprints Audit</span>
          <span className="text-emerald-500">Completed</span>
        </div>
      </div>
    </div>
  ),
  'compliance-status': () => (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Governance Index</h3>
      <div className="text-3xl font-black text-foreground">98.4%</div>
      <p className="text-[10px] text-muted-foreground">Platform complies fully with EPA and OSHA acts.</p>
    </div>
  ),
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
  'transparency-reviews': () => (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">RAG Transparency Reviews</h3>
      <div className="text-xs space-y-1">
        <div className="flex justify-between">
          <span>Total Explainability audits:</span>
          <span className="font-bold">34 sessions</span>
        </div>
      </div>
    </div>
  ),

  // 5. Director/Executive Widgets
  'org-kpis': () => (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Overall Plant KPIs</h3>
      <div className="grid grid-cols-2 gap-2 text-center text-xs pt-1">
        <div className="border border-border/40 rounded p-1 bg-secondary/15">
          <span className="text-[9px] text-muted-foreground block">Safety Rating</span>
          <b className="text-foreground">99.8%</b>
        </div>
        <div className="border border-border/40 rounded p-1 bg-secondary/15">
          <span className="text-[9px] text-muted-foreground block">OEE efficiency</span>
          <b className="text-foreground">84.2%</b>
        </div>
      </div>
    </div>
  ),
  'downtime-trends': () => (
    <div className="rounded-xl border border-border bg-card p-4 space-y-2">
      <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Operational Downtime</h3>
      <div className="text-2xl font-black text-foreground">14.5 Hours</div>
      <p className="text-[10px] text-muted-foreground">Decreased by 2.2 hours since Q2.</p>
    </div>
  ),
  'ai-usage-analytics': () => {
    const [auditCount, setAuditCount] = React.useState<number>(0);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
      const fetchLogs = async () => {
        try {
          const accessToken = localStorage.getItem('ib-access-token');
          const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
          const res = await fetch(`${baseUrl}/api/audit/events`, {
            headers: {
              ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
            }
          });
          if (res.ok) {
            const data = await res.json();
            setAuditCount(data.length || 0);
          }
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
            <span>Compliance Audit Logs:</span>
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
          const accessToken = localStorage.getItem('ib-access-token');
          const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
          const res = await fetch(`${baseUrl}/api/audit/events`, {
            headers: {
              ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
            }
          });
          if (res.ok) {
            const data = await res.json();
            const criticals = data.filter((d: any) => d.severity === 'HIGH' || d.severity === 'CRITICAL');
            setHighRiskCount(criticals.length);
          }
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
          const accessToken = localStorage.getItem('ib-access-token');
          const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
          const res = await fetch(`${baseUrl}/api/upload`, {
            headers: {
              ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
            }
          });
          if (res.ok) {
            const data = await res.json();
            setFiles(data.documents || []);
          }
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
          const accessToken = localStorage.getItem('ib-access-token');
          const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
          const res = await fetch(`${baseUrl}/api/upload`, {
            headers: {
              ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
            }
          });
          if (res.ok) {
            const data = await res.json();
            setFiles(data.documents || []);
          }
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
          <p className="text-[11px] text-muted-foreground italic text-center py-2">No files accessible in your clearance tier.</p>
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
