import React from 'react';
import Link from 'next/link';
import { RetrievalMode, ProcessingOptionsState } from '@/store/app-context';
import { ArrowLeft, MessageSquare, ShieldAlert } from 'lucide-react';

interface ProcessingSummaryProps {
  retrievalMode: RetrievalMode;
  docCount: number;
  categories: string[];
  options: ProcessingOptionsState;
  onStartProcessing: () => void;
  isProcessing: boolean;
}

export default function ProcessingSummary({
  retrievalMode,
  docCount,
  categories,
  options,
  onStartProcessing,
  isProcessing,
}: ProcessingSummaryProps) {
  
  // Compile active task labels
  const getActiveTasks = () => {
    const tasks: string[] = [];
    if (options.summarization) tasks.push('Summarization');
    if (options.entityExtraction) tasks.push('Entities Ingress');
    if (options.relationshipDiscovery) tasks.push('Relation Mapping');
    if (options.timelineExtraction) tasks.push('Timeline Logs');
    if (options.keyInsights) tasks.push('Key Insights');
    if (options.complianceAnalysis) tasks.push('Compliance Scan');
    return tasks;
  };

  const activeTasks = getActiveTasks();

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm flex flex-col justify-between h-full space-y-6">
      <div className="space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Configuration Summary
        </h2>

        {/* Overview Stats */}
        <div className="grid grid-cols-2 gap-3 text-xs border-b border-border/80 pb-4">
          <div className="space-y-0.5">
            <span className="text-muted-foreground font-medium">Retrieval Mode</span>
            <div className="font-bold text-foreground capitalize">{retrievalMode}</div>
          </div>
          <div className="space-y-0.5">
            <span className="text-muted-foreground font-medium">Attached Docs</span>
            <div className="font-bold text-foreground">{docCount} Files</div>
          </div>
        </div>

        {/* Categories list */}
        <div className="text-xs space-y-1">
          <span className="text-muted-foreground font-medium">Classified Categories</span>
          <div className="flex flex-wrap gap-1.5 pt-1">
            {categories.length === 0 ? (
              <span className="text-muted-foreground italic">None staged</span>
            ) : (
              categories.map((cat, i) => (
                <span
                  key={i}
                  className="rounded-full bg-secondary border border-border px-2 py-0.5 text-[10px] font-semibold text-foreground"
                >
                  {cat}
                </span>
              ))
            )}
          </div>
        </div>

        {/* Enabled Tasks */}
        <div className="text-xs space-y-1.5 pt-2">
          <span className="text-muted-foreground font-medium">Enabled AI Pipelines ({activeTasks.length})</span>
          <div className="rounded-lg border border-border bg-secondary/15 p-3 space-y-1.5 max-h-40 overflow-y-auto">
            {activeTasks.length === 0 ? (
              <div className="text-destructive font-semibold flex items-center gap-1.5">
                <ShieldAlert className="h-4 w-4 shrink-0 animate-pulse" />
                No models selected!
              </div>
            ) : (
              activeTasks.map((task, i) => (
                <div key={i} className="flex items-center gap-1.5 font-bold text-foreground">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                  {task}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="space-y-2 pt-4 border-t border-border">
        <button
          type="button"
          onClick={onStartProcessing}
          disabled={docCount === 0 || activeTasks.length === 0 || isProcessing}
          className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-primary hover:bg-primary/95 text-primary-foreground py-2.5 text-sm font-semibold shadow-sm transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <MessageSquare className="h-4 w-4 fill-current shrink-0" />
          {isProcessing ? 'Processing Pipeline...' : 'Continue to AI Chat'}
        </button>

        <Link
          href="/upload"
          className="w-full inline-flex items-center justify-center gap-2 rounded-lg border border-border bg-transparent hover:bg-secondary py-2 text-xs font-semibold transition-all cursor-pointer text-foreground"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to Ingestion
        </Link>
      </div>
    </div>
  );
}
