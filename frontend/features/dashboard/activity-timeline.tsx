import React from 'react';
import { Upload, CheckCircle2, MessageSquare, Key } from 'lucide-react';

const ACTIVITIES = [
  {
    title: 'Document Ingested',
    desc: 'SOP_HighPressure_Boiler.docx added to repository',
    time: '12 minutes ago',
    icon: Upload,
    color: 'text-primary bg-primary/10 border-primary/20',
  },
  {
    title: 'AI Processing Completed',
    desc: 'OCR layout parsing completed for P-102A_Schematics_v3.pdf',
    time: '1 hour ago',
    icon: CheckCircle2,
    color: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
  },
  {
    title: 'Chat Session Started',
    desc: 'Q&A session regarding Valve V-402 temperature threshold',
    time: '3 hours ago',
    icon: MessageSquare,
    color: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
  },
  {
    title: 'Access Request Submitted',
    desc: 'Munich Engineering department requested blueprint keys',
    time: '1 day ago',
    icon: Key,
    color: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
  },
];

export default function ActivityTimeline() {
  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm flex flex-col h-full">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">
        Recent Repository Activity
      </h2>
      <div className="flex-1 space-y-6 relative before:absolute before:left-[14px] before:top-3 before:bottom-3 before:w-0.5 before:bg-border">
        {ACTIVITIES.map((act, i) => {
          const Icon = act.icon;
          return (
            <div key={i} className="relative flex items-start animate-in fade-in duration-200">
              {/* Timeline marker */}
              <div
                className={`relative z-10 flex h-7 w-7 items-center justify-center rounded-full border shrink-0 ${act.color}`}
                style={{ backgroundColor: 'hsl(var(--card))' }}
              >
                <Icon className="h-3.5 w-3.5 shrink-0" />
              </div>
              <div 
                className="space-y-0.5 flex-1 min-w-0"
                style={{ marginLeft: '16px' }}
              >
                <div className="text-xs font-bold text-foreground leading-none">{act.title}</div>
                <p className="text-[11px] text-muted-foreground leading-tight mt-0.5">{act.desc}</p>
                <span className="block text-[10px] text-muted-foreground/60 font-medium mt-1">
                  {act.time}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
