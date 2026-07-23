import React from 'react';
import { HelpCircle, FileText, Database, Network, MessageSquare, ArrowRight } from 'lucide-react';

const PATH_STEPS = [
  { label: 'Question', icon: HelpCircle },
  { label: 'Retrieved Docs', icon: FileText },
  { label: 'Extraction', icon: Database },
  { label: 'Graph Links', icon: Network },
  { label: 'Answer Out', icon: MessageSquare },
];

export default function DecisionPath() {
  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-sm space-y-3">
      <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
        Decision Path Pipeline
      </span>

      <div className="flex items-center justify-between max-w-2xl mx-auto py-1">
        {PATH_STEPS.map((step, idx) => {
          const Icon = step.icon;
          return (
            <React.Fragment key={idx}>
              <div className="flex flex-col items-center gap-1.5 flex-1 text-center">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 border border-primary/20 text-primary shadow-sm">
                  <Icon className="h-4.5 w-4.5 shrink-0" />
                </div>
                <span className="text-[9px] font-bold text-foreground">
                  {step.label}
                </span>
              </div>
              {idx < PATH_STEPS.length - 1 && (
                <div className="text-muted-foreground/40 -translate-y-2">
                  <ArrowRight className="h-4 w-4 shrink-0" />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
