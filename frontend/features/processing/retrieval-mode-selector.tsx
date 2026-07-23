import React from 'react';
import { RetrievalMode } from '@/store/app-context';
import { Sparkles, MousePointerClick } from 'lucide-react';

interface RetrievalModeSelectorProps {
  selectedMode: RetrievalMode;
  onSelectMode: (mode: RetrievalMode) => void;
}

export default function RetrievalModeSelector({
  selectedMode,
  onSelectMode,
}: RetrievalModeSelectorProps) {
  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm space-y-4">
      <div>
        <h2 className="text-md font-semibold text-foreground">Select Retrieval Mode</h2>
        <p className="text-xs text-muted-foreground mt-0.5">
          Determine how the AI coordinates context search queries across your database.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Automatic Retrieval */}
        <button
          type="button"
          onClick={() => onSelectMode('automatic')}
          className={`flex items-start text-left rounded-xl border p-4 transition-all cursor-pointer ${
            selectedMode === 'automatic'
              ? 'border-primary bg-primary/5 shadow-sm'
              : 'border-border bg-transparent hover:bg-secondary/40'
          }`}
        >
          <div className="rounded-lg bg-primary/10 p-2.5 text-primary shrink-0 mr-3.5 mt-0.5">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <div className="text-sm font-bold text-foreground flex items-center gap-1.5">
              Automatic Retrieval
              {selectedMode === 'automatic' && (
                <span className="rounded bg-primary/20 border border-primary/30 px-1.5 py-0.5 text-[9px] font-extrabold uppercase text-primary leading-none">
                  Active
                </span>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1 leading-normal">
              System parses search queries and dynamically pulls matching context chunks from all documents automatically using vector index semantic ranks.
            </p>
          </div>
        </button>

        {/* Manual Document Selection */}
        <button
          type="button"
          onClick={() => onSelectMode('manual')}
          className={`flex items-start text-left rounded-xl border p-4 transition-all cursor-pointer ${
            selectedMode === 'manual'
              ? 'border-primary bg-primary/5 shadow-sm'
              : 'border-border bg-transparent hover:bg-secondary/40'
          }`}
        >
          <div className="rounded-lg bg-primary/10 p-2.5 text-primary shrink-0 mr-3.5 mt-0.5">
            <MousePointerClick className="h-5 w-5" />
          </div>
          <div>
            <div className="text-sm font-bold text-foreground flex items-center gap-1.5">
              Manual Document Selection
              {selectedMode === 'manual' && (
                <span className="rounded bg-primary/20 border border-primary/30 px-1.5 py-0.5 text-[9px] font-extrabold uppercase text-primary leading-none">
                  Active
                </span>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1 leading-normal">
              Lock query search constraints exclusively to folders or specific files. Queries are evaluated only within the manually designated scopes.
            </p>
          </div>
        </button>
      </div>
    </div>
  );
}
