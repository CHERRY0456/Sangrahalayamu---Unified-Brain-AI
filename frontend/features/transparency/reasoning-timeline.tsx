'use client';

import React, { useState } from 'react';
import { Check, Loader2, ChevronDown, ChevronUp } from 'lucide-react';

export interface ExplanationReasoningStep {
  label: string;
  description: string;
  status: 'completed' | 'pending';
  // Extended array for dashboard expandable steps
  subLogs?: string[];
}

interface ReasoningTimelineProps {
  steps: ExplanationReasoningStep[];
  interactive?: boolean;
}

export default function ReasoningTimeline({
  steps,
  interactive = false,
}: ReasoningTimelineProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const toggleExpand = (idx: number) => {
    if (!interactive) return;
    setExpandedIndex((prev) => (prev === idx ? null : idx));
  };

  return (
    <div className="space-y-4 animate-in fade-in duration-150">
      <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
        AI Reasoning Pipeline Flow
      </span>
      <div className="relative pl-4 before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-0.5 before:bg-border">
        {steps.map((step, idx) => {
          const isCompleted = step.status === 'completed';
          const isExpanded = expandedIndex === idx;

          return (
            <div key={idx} className="relative flex flex-col pb-4 last:pb-0">
              
              {/* Timeline row */}
              <div 
                className={`relative flex gap-3 items-start ${interactive ? 'cursor-pointer select-none group' : ''}`}
                onClick={() => toggleExpand(idx)}
              >
                {/* Step Icon Node */}
                <div
                  className={`absolute -left-[18px] top-0.5 flex h-5 w-5 items-center justify-center rounded-full border bg-card z-10 ${
                    isCompleted
                      ? 'border-emerald-500/30 text-emerald-500 shadow-sm'
                      : 'border-primary text-primary animate-pulse'
                  }`}
                >
                  {isCompleted ? (
                    <Check className="h-3 w-3" />
                  ) : (
                    <Loader2 className="h-3 w-3 animate-spin text-primary" />
                  )}
                </div>

                {/* Step Text details */}
                <div className="space-y-0.5 min-w-0 flex-1">
                  <div className="text-[11px] font-bold text-foreground leading-none group-hover:text-primary transition-colors flex items-center justify-between">
                    <span>{step.label}</span>
                    {interactive && step.subLogs && (
                      <div className="text-muted-foreground/60">
                        {isExpanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
                      </div>
                    )}
                  </div>
                  <p className="text-[10px] text-muted-foreground/85 leading-normal mt-0.5">
                    {step.description}
                  </p>
                </div>
              </div>

              {/* Sub-logs expansion */}
              {interactive && isExpanded && step.subLogs && (
                <div className="pl-3 mt-2 space-y-1 text-[9px] text-muted-foreground/75 leading-relaxed bg-secondary/10 border border-border/40 rounded-lg p-2.5 ml-1 animate-in slide-in-from-top-1 duration-150">
                  {step.subLogs.map((log, lIdx) => (
                    <div key={lIdx} className="flex gap-1.5 items-start">
                      <span className="text-primary font-bold">•</span>
                      <span>{log}</span>
                    </div>
                  ))}
                </div>
              )}

            </div>
          );
        })}
      </div>
    </div>
  );
}
