'use client';

import React, { useState } from 'react';
import ResponseList, { ExplanationSnapshot } from './response-list';
import DecisionPath from './decision-path';
import RetrievedDocuments from './retrieved-documents';
import ReasoningTimeline from './reasoning-timeline';
import SourceAttribution from './source-attribution';
import GraphPreview from './graph-preview';
import InsightsSummary from './insights-summary';
import ComparisonPanel from './comparison-panel';
import { ExplanationData } from './transparency-panel';
import { Network, HelpCircle } from 'lucide-react';

interface TransparencyDashboardProps {
  snapshots: ExplanationSnapshot[];
  explanations: Record<string, ExplanationData>;
}

export default function TransparencyDashboard({
  snapshots,
  explanations,
}: TransparencyDashboardProps) {
  const [activeId, setActiveId] = useState<string>('1');
  const [compareIds, setCompareIds] = useState<string[]>([]);
  const [isCompareMode, setIsCompareMode] = useState(false);

  const handleSelectSnapshot = (id: string) => {
    setActiveId(id);
  };

  const handleToggleCompare = (id: string) => {
    setCompareIds((prev) => {
      if (prev.includes(id)) {
        return prev.filter((itemId) => itemId !== id);
      }
      if (prev.length >= 2) {
        // Limit to max 2 items, swap the oldest
        return [prev[1], id];
      }
      return [...prev, id];
    });
  };

  const handleToggleCompareMode = () => {
    setIsCompareMode((prev) => {
      const next = !prev;
      if (!next) {
        setCompareIds([]);
      }
      return next;
    });
  };

  const currentExplanation = explanations[activeId] || null;
  const currentSnapshot = snapshots.find((s) => s.id === activeId) || null;

  // Find snap objects for comparison
  const snapA = snapshots.find((s) => s.id === compareIds[0]) || null;
  const snapB = snapshots.find((s) => s.id === compareIds[1]) || null;

  return (
    <div className="flex flex-col lg:flex-row h-[calc(100vh-8rem)] rounded-xl border border-border bg-card/25 overflow-hidden shadow-sm animate-in fade-in duration-300">
      
      {/* 1. Left Panel - Searchable Snapshot List */}
      <ResponseList
        snapshots={snapshots}
        activeId={activeId}
        onSelect={handleSelectSnapshot}
        compareIds={compareIds}
        onToggleCompare={handleToggleCompare}
        isCompareMode={isCompareMode}
        onToggleCompareMode={handleToggleCompareMode}
      />

      {/* 2. Center Workspace Column */}
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 overflow-y-auto p-6 space-y-6 border-r border-border/40 h-full">
          {isCompareMode ? (
            /* Comparison Mode View */
            snapA && snapB ? (
              <ComparisonPanel snapA={snapA} snapB={snapB} />
            ) : (
              <div className="flex flex-col items-center justify-center text-center text-muted-foreground italic h-64 space-y-3 p-8 border border-dashed border-border rounded-xl">
                <Network className="h-8 w-8 text-muted-foreground/60 animate-pulse" />
                <div className="text-xs font-bold text-foreground">Select Snapshots to Compare</div>
                <p className="text-[10px] max-w-xs leading-normal">
                  Check exactly 2 snapshots in the left column list to perform side-by-side RAG trace diff analysis.
                </p>
              </div>
            )
          ) : (
            /* Inspect Mode View */
            currentExplanation && (
              <div className="space-y-6">
                {/* Decision Path Pipeline */}
                <DecisionPath />

                {/* Retrieved Documents (Interactive) */}
                <RetrievedDocuments documents={currentExplanation.documents} interactive={true} />

                <hr className="border-border/40" />

                {/* Reasoning Timeline (Interactive) */}
                <ReasoningTimeline steps={currentExplanation.reasoningSteps} interactive={true} />

                <hr className="border-border/40" />

                {/* Source Attribution (Interactive) */}
                <SourceAttribution citations={currentExplanation.citations} interactive={true} />

                <hr className="border-border/40" />

                {/* Knowledge Graph Preview (Interactive) */}
                <GraphPreview graph={currentExplanation.graph} interactive={true} />
              </div>
            )
          )}
        </div>

        {/* 3. Right Column Panel - Insights & Enterprise Score */}
        {!isCompareMode && currentExplanation && currentSnapshot && (
          <InsightsSummary
            explanation={currentExplanation}
            explainabilityScore={currentSnapshot.explainabilityScore}
          />
        )}
      </div>

    </div>
  );
}
