import React from 'react';
import { RetrievalMode, ProcessingOptionsState } from '@/store/app-context';
import { FileText, Sparkles, MousePointerClick, Database, ShieldAlert, Settings2 } from 'lucide-react';

interface ConversationContextBarProps {
  retrievalMode: RetrievalMode;
  onSelectMode: (mode: RetrievalMode) => void;
  docCount: number;
  options: ProcessingOptionsState;
  onOpenManageContext: () => void;
  onOpenRequestAccess: () => void;
}

export default function ConversationContextBar({
  retrievalMode,
  onSelectMode,
  docCount,
  options,
  onOpenManageContext,
  onOpenRequestAccess,
}: ConversationContextBarProps) {
  
  // Format active pipeline capabilities
  const getActiveOptionsText = () => {
    const list: string[] = [];
    if (options.summarization) list.push('Summary');
    if (options.entityExtraction) list.push('Entities');
    if (options.relationshipDiscovery) list.push('Relations');
    if (options.timelineExtraction) list.push('Timelines');
    if (options.keyInsights) list.push('Insights');
    if (options.complianceAnalysis) list.push('Compliance');
    
    if (list.length === 0) return 'No active models';
    return list.slice(0, 3).join(', ') + (list.length > 3 ? ` +${list.length - 3}` : '');
  };

  return (
    <div className="flex flex-wrap items-center justify-between border-b border-border bg-card/45 px-4 py-2 text-xs text-muted-foreground gap-3">
      {/* Active Pipeline Metadata */}
      <div className="flex flex-wrap items-center gap-4">
        {/* Documents Count */}
        <div className="flex items-center gap-1.5">
          <FileText className="h-4 w-4 text-primary shrink-0" />
          <span>Staged Payload: <b>{docCount} Files</b></span>
        </div>

        <span className="hidden md:inline h-3 w-px bg-border" />

        {/* Retrieval Mode Toggle */}
        <div className="flex items-center gap-2">
          <span className="text-muted-foreground">Mode:</span>
          <div className="flex items-center bg-secondary/50 rounded-lg p-0.5 border border-border">
            <button
              type="button"
              onClick={() => onSelectMode('automatic')}
              className={`px-2 py-0.5 rounded text-[10px] font-bold transition-all cursor-pointer ${
                retrievalMode === 'automatic'
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Automatic
            </button>
            <button
              type="button"
              onClick={() => onSelectMode('manual')}
              className={`px-2 py-0.5 rounded text-[10px] font-bold transition-all cursor-pointer ${
                retrievalMode === 'manual'
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Manual
            </button>
          </div>
        </div>

        <span className="hidden md:inline h-3 w-px bg-border" />

        {/* Enabled Options */}
        <div className="flex items-center gap-1.5">
          <Settings2 className="h-4 w-4 text-primary shrink-0" />
          <span>Active Models: <b>{getActiveOptionsText()}</b></span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onOpenManageContext}
          className="inline-flex items-center gap-1 rounded border border-border bg-secondary/50 hover:bg-secondary px-2.5 py-1 text-[11px] font-semibold text-foreground transition-all cursor-pointer"
        >
          <Database className="h-3.5 w-3.5" />
          Manage Context
        </button>

        <button
          type="button"
          onClick={onOpenRequestAccess}
          className="inline-flex items-center gap-1 rounded border border-border bg-secondary/50 hover:bg-secondary px-2.5 py-1 text-[11px] font-semibold text-foreground transition-all cursor-pointer"
        >
          <ShieldAlert className="h-3.5 w-3.5 text-amber-500" />
          Access Clearance
        </button>
      </div>
    </div>
  );
}
