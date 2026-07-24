'use client';

import React from 'react';
import { ExplanationSnapshot } from './response-list';
import { FileText, Percent, ShieldCheck, ArrowRightLeft } from 'lucide-react';

interface ComparisonPanelProps {
  snapA: ExplanationSnapshot;
  snapB: ExplanationSnapshot;
}

export default function ComparisonPanel({ snapA, snapB }: ComparisonPanelProps) {
  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm space-y-6 animate-in zoom-in-95 duration-200">
      
      {/* Title */}
      <div className="flex items-center gap-2 border-b border-border/80 pb-4">
        <div className="rounded-full bg-amber-500/10 p-2 text-amber-500 shrink-0">
          <ArrowRightLeft className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-md font-bold text-foreground">Explanation Snapshot Comparison</h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            Side-by-side analysis of vector inputs, reasoning layers, and trust indicators.
          </p>
        </div>
      </div>

      {/* Grid Comparison Matrix */}
      <div className="grid md:grid-cols-2 gap-6">
        
        {/* Snapshot A Card */}
        <div className="rounded-lg border border-border bg-secondary/10 p-4 space-y-4">
          <div className="border-b border-border/60 pb-2">
            <span className="text-[9px] font-extrabold uppercase text-amber-500 tracking-wider">
              Snapshot A
            </span>
            <h3 className="text-xs font-bold text-foreground truncate mt-1">
              {snapA.question}
            </h3>
            <span className="text-[10px] text-muted-foreground block mt-0.5">
              {snapA.timestamp}
            </span>
          </div>

          {/* Metrics */}
          <div className="grid grid-cols-3 gap-2 text-center text-xs">
            <div className="rounded border border-border bg-card p-2">
              <span className="text-[9px] text-muted-foreground block">Confidence</span>
              <b className="text-foreground">{snapA.confidenceScore}%</b>
            </div>
            <div className="rounded border border-border bg-card p-2">
              <span className="text-[9px] text-muted-foreground block">Explainability</span>
              <b className="text-foreground">{snapA.explainabilityScore}/100</b>
            </div>
            <div className="rounded border border-border bg-card p-2">
              <span className="text-[9px] text-muted-foreground block">Staged Docs</span>
              <b className="text-foreground">{snapA.docCount} files</b>
            </div>
          </div>

          {/* Metadata detail list */}
          <div className="space-y-2 text-xs border-t border-border/40 pt-3">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Retrieval Mode:</span>
              <span className="font-semibold text-foreground capitalize">{snapA.retrievalMode}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Category Group:</span>
              <span className="font-semibold text-foreground">{snapA.category}</span>
            </div>
          </div>
        </div>

        {/* Snapshot B Card */}
        <div className="rounded-lg border border-border bg-secondary/10 p-4 space-y-4">
          <div className="border-b border-border/60 pb-2">
            <span className="text-[9px] font-extrabold uppercase text-amber-500 tracking-wider">
              Snapshot B
            </span>
            <h3 className="text-xs font-bold text-foreground truncate mt-1">
              {snapB.question}
            </h3>
            <span className="text-[10px] text-muted-foreground block mt-0.5">
              {snapB.timestamp}
            </span>
          </div>

          {/* Metrics */}
          <div className="grid grid-cols-3 gap-2 text-center text-xs">
            <div className="rounded border border-border bg-card p-2">
              <span className="text-[9px] text-muted-foreground block">Confidence</span>
              <b className="text-foreground">{snapB.confidenceScore}%</b>
            </div>
            <div className="rounded border border-border bg-card p-2">
              <span className="text-[9px] text-muted-foreground block">Explainability</span>
              <b className="text-foreground">{snapB.explainabilityScore}/100</b>
            </div>
            <div className="rounded border border-border bg-card p-2">
              <span className="text-[9px] text-muted-foreground block">Staged Docs</span>
              <b className="text-foreground">{snapB.docCount} files</b>
            </div>
          </div>

          {/* Metadata detail list */}
          <div className="space-y-2 text-xs border-t border-border/40 pt-3">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Retrieval Mode:</span>
              <span className="font-semibold text-foreground capitalize">{snapB.retrievalMode}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Category Group:</span>
              <span className="font-semibold text-foreground">{snapB.category}</span>
            </div>
          </div>
        </div>

      </div>

      {/* Diff Analysis Summary */}
      <div className="rounded-lg border border-border bg-secondary/15 p-4 space-y-3">
        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block flex items-center gap-1">
          <ShieldCheck className="h-4 w-4 text-primary shrink-0" />
          Explainability Differences Analysis
        </span>
        <div className="text-xs text-muted-foreground/90 leading-relaxed space-y-2 font-normal">
          <p>
            • **Source Overlap**: Determines if the generated responses shared context documents or relied on distinct knowledge bases.
          </p>
          <p>
            • **Pipeline Divergence**: Highlights variations in retrieval modes (e.g. Graph vs Vector) or processing requirements that may have impacted the explainability score (Score A: {snapA.explainabilityScore}, Score B: {snapB.explainabilityScore}).
          </p>
          <p>
            • **Confidence Variance**: Explains the ({Math.abs(snapA.confidenceScore - snapB.confidenceScore)}%) difference in confidence based on semantic similarity weights and context relevance.
          </p>
        </div>
      </div>

    </div>
  );
}
