'use client';

import React, { useState } from 'react';
import { Search, Calendar, Filter, FileText, CheckSquare, Square } from 'lucide-react';
import { RetrievalMode } from '@/store/app-context';

export interface ExplanationSnapshot {
  id: string;
  question: string;
  timestamp: string;
  confidenceScore: number;
  explainabilityScore: number;
  retrievalMode: RetrievalMode;
  docCount: number;
  category: string;
}

interface ResponseListProps {
  snapshots: ExplanationSnapshot[];
  activeId: string;
  onSelect: (id: string) => void;
  compareIds: string[];
  onToggleCompare: (id: string) => void;
  isCompareMode: boolean;
  onToggleCompareMode: () => void;
}

export default function ResponseList({
  snapshots,
  activeId,
  onSelect,
  compareIds,
  onToggleCompare,
  isCompareMode,
  onToggleCompareMode,
}: ResponseListProps) {
  const [search, setSearch] = useState('');
  const [modeFilter, setModeFilter] = useState<string>('all');
  const [confidenceFilter, setConfidenceFilter] = useState<string>('all');

  // Filter Snapshots
  const filteredSnapshots = snapshots.filter((snap) => {
    const matchesSearch =
      snap.question.toLowerCase().includes(search.toLowerCase()) ||
      snap.category.toLowerCase().includes(search.toLowerCase());

    const matchesMode =
      modeFilter === 'all' || snap.retrievalMode === modeFilter;

    const matchesConfidence =
      confidenceFilter === 'all' ||
      (confidenceFilter === 'high' && snap.confidenceScore >= 90) ||
      (confidenceFilter === 'medium' && snap.confidenceScore >= 80 && snap.confidenceScore < 90) ||
      (confidenceFilter === 'low' && snap.confidenceScore < 80);

    return matchesSearch && matchesMode && matchesConfidence;
  });

  return (
    <div className="w-full lg:w-80 shrink-0 border-r border-border bg-card/60 flex flex-col h-full overflow-hidden">
      {/* Search and comparison toggle */}
      <div className="p-4 border-b border-border space-y-3 bg-card">
        <div className="flex justify-between items-center">
          <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
            Explanation Snapshots
          </h2>
          <button
            type="button"
            onClick={onToggleCompareMode}
            className={`rounded px-2.5 py-1 text-[10px] font-bold transition-all cursor-pointer border ${
              isCompareMode
                ? 'bg-primary text-primary-foreground border-primary'
                : 'border-border text-muted-foreground hover:text-foreground'
            }`}
          >
            {isCompareMode ? 'Exit Compare' : 'Compare Snapshots'}
          </button>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground/60" />
          <input
            type="text"
            placeholder="Search questions or topics..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-border bg-background pl-8 pr-3 py-2 text-xs text-foreground outline-none focus:border-primary placeholder:text-muted-foreground/50"
          />
        </div>
      </div>

      {/* Advanced Filters */}
      <div className="p-3 border-b border-border bg-secondary/15 flex gap-2 text-[10px]">
        {/* Mode filter */}
        <div className="flex-1 space-y-1">
          <label className="text-muted-foreground font-semibold">Mode</label>
          <select
            value={modeFilter}
            onChange={(e) => setModeFilter(e.target.value)}
            className="w-full rounded border border-border bg-background p-1 text-[10px] text-foreground outline-none"
          >
            <option value="all">All Modes</option>
            <option value="automatic">Automatic</option>
            <option value="manual">Manual</option>
          </select>
        </div>

        {/* Confidence filter */}
        <div className="flex-1 space-y-1">
          <label className="text-muted-foreground font-semibold">Confidence</label>
          <select
            value={confidenceFilter}
            onChange={(e) => setConfidenceFilter(e.target.value)}
            className="w-full rounded border border-border bg-background p-1 text-[10px] text-foreground outline-none"
          >
            <option value="all">All Confidence</option>
            <option value="high">High (&gt;=90%)</option>
            <option value="medium">Medium (80-89%)</option>
            <option value="low">Low (&lt;80%)</option>
          </select>
        </div>
      </div>

      {/* Snapshots Scroll Area */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {filteredSnapshots.length === 0 ? (
          <div className="text-xs text-muted-foreground italic px-3 py-4 text-center">
            No snapshots match filters.
          </div>
        ) : (
          filteredSnapshots.map((snap) => {
            const isActive = activeId === snap.id && !isCompareMode;
            const isCompareChecked = compareIds.includes(snap.id);

            return (
              <div
                key={snap.id}
                onClick={() => {
                  if (isCompareMode) {
                    onToggleCompare(snap.id);
                  } else {
                    onSelect(snap.id);
                  }
                }}
                className={`relative flex gap-2.5 rounded-lg border p-3 cursor-pointer transition-all select-none ${
                  isActive
                    ? 'border-primary bg-secondary/80 text-foreground'
                    : isCompareChecked && isCompareMode
                    ? 'border-amber-500 bg-amber-500/5 text-foreground shadow-[0_0_10px_rgba(245,158,11,0.08)]'
                    : 'border-border bg-card/40 hover:bg-secondary/30 text-muted-foreground hover:text-foreground'
                }`}
              >
                {/* Checkbox for Compare Mode */}
                {isCompareMode && (
                  <div className="flex items-center shrink-0 text-amber-500 pt-0.5">
                    {isCompareChecked ? (
                      <CheckSquare className="h-4.5 w-4.5" />
                    ) : (
                      <Square className="h-4.5 w-4.5 text-muted-foreground/40" />
                    )}
                  </div>
                )}

                <div className="flex-1 min-w-0 space-y-2">
                  <div className="text-xs font-bold text-foreground line-clamp-2 leading-relaxed">
                    {snap.question}
                  </div>

                  <div className="flex justify-between items-center text-[10px] text-muted-foreground/60 border-t border-border/40 pt-2 font-medium">
                    <span>{snap.timestamp}</span>
                    <span className="capitalize">{snap.retrievalMode} Mode</span>
                  </div>

                  <div className="flex flex-wrap gap-1.5 pt-1">
                    <span className="rounded bg-secondary/85 border border-border px-1.5 py-0.5 text-[9px] font-extrabold text-foreground leading-none">
                      Conf: {snap.confidenceScore}%
                    </span>
                    <span className="rounded bg-secondary/85 border border-border px-1.5 py-0.5 text-[9px] font-extrabold text-foreground leading-none">
                      Expl: {snap.explainabilityScore}/100
                    </span>
                    <span className="rounded bg-primary/10 border border-primary/20 px-1.5 py-0.5 text-[9px] font-bold text-primary leading-none flex items-center gap-0.5">
                      <FileText className="h-2.5 w-2.5 shrink-0" />
                      {snap.docCount} docs
                    </span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
