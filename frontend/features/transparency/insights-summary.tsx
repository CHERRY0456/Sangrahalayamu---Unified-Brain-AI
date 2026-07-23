'use client';

import React from 'react';
import { ExplanationData } from './transparency-panel';
import { ShieldCheck, HelpCircle, AlertCircle, Sparkles, Percent } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface InsightsSummaryProps {
  explanation: ExplanationData | null;
  explainabilityScore: number;
}

export default function InsightsSummary({
  explanation,
  explainabilityScore,
}: InsightsSummaryProps) {
  const router = useRouter();

  if (!explanation) return null;

  // Mock static values for explanation properties if missing
  const activeMode = explanation.docCoverage.includes('documents') ? 'Vector-RAG' : 'Schema-constrained';
  const pipelineTasks = ['Summarization', 'Entities Ingress', 'Key Insights'];

  const getStrengthBarWidth = (str: 'High' | 'Medium' | 'Low') => {
    switch (str) {
      case 'High': return 'w-full bg-emerald-500';
      case 'Medium': return 'w-2/3 bg-amber-500';
      case 'Low': return 'w-1/3 bg-destructive';
    }
  };

  const getExplainabilityRating = (score: number) => {
    if (score >= 90) return 'Excellent';
    if (score >= 80) return 'Good';
    return 'Fair';
  };

  return (
    <div className="w-full lg:w-80 shrink-0 border-l border-border bg-card/60 flex flex-col h-full overflow-y-auto p-4 space-y-6">
      
      {/* 1. Explainability Score Card (Enterprise Metric) */}
      <div className="rounded-xl border border-border bg-primary/5 p-4 space-y-2 shadow-sm text-center">
        <span className="text-[10px] font-bold text-primary uppercase tracking-wider block">
          Explainability Index
        </span>
        <div className="text-3xl font-black text-foreground">
          {explainabilityScore} <span className="text-xs text-muted-foreground">/ 100</span>
        </div>
        <span className="inline-block rounded-full bg-primary/20 border border-primary/30 px-3 py-0.5 text-[10px] font-bold uppercase text-primary tracking-wide">
          {getExplainabilityRating(explainabilityScore)}
        </span>
      </div>

      {/* 2. Visual Confidence Gauges */}
      <div className="space-y-4 rounded-xl border border-border bg-card p-4 shadow-sm">
        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
          Confidence Metrics Visualizer
        </span>

        {/* SVG Circular Progress */}
        <div className="flex flex-col items-center py-2 space-y-2">
          <div className="relative h-20 w-20 flex items-center justify-center">
            {/* SVG Track */}
            <svg className="absolute inset-0 transform -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-secondary"
                strokeWidth="3"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className="text-primary transition-all duration-1000 ease-out"
                strokeWidth="3.2"
                strokeDasharray={`${explanation.overallConfidence}, 100`}
                strokeLinecap="round"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <div className="text-base font-black text-foreground flex items-center gap-0.5">
              {explanation.overallConfidence}
              <Percent className="h-3.5 w-3.5 text-primary shrink-0" />
            </div>
          </div>
          <span className="text-[9px] text-muted-foreground font-semibold uppercase tracking-wide">
            Vector Score Rank
          </span>
        </div>

        {/* Evidence Strength Horizontal Gauge */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-[10px] font-semibold">
            <span className="text-muted-foreground">Evidence Strength:</span>
            <span className="text-foreground">{explanation.evidenceStrength}</span>
          </div>
          <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
            <div className={`h-full rounded-full transition-all duration-1000 ease-out ${getStrengthBarWidth(explanation.evidenceStrength)}`} />
          </div>
        </div>

        {/* Document Coverage */}
        <div className="flex justify-between text-[10px] border-t border-border/40 pt-3">
          <span className="text-muted-foreground font-medium">Staged Document Ratio:</span>
          <b className="text-foreground">{explanation.docCoverage}</b>
        </div>
      </div>

      {/* 3. AI Decision Summary */}
      <div className="space-y-4">
        {/* Why Generated */}
        <div className="rounded-xl border border-border bg-card p-4 space-y-2 shadow-sm">
          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block flex items-center gap-1">
            <ShieldCheck className="h-4 w-4 text-emerald-500 shrink-0" />
            AI Decision Summary
          </span>
          <p className="text-xs text-muted-foreground/90 leading-relaxed font-normal">
            This answer was formulated because the queried engineering valve parameter (<b>V-402</b>) matches threshold tables on <b>Page 3</b> of the blueprint specs. Conflicting logs were resolved using active vector context weighting.
          </p>
        </div>

        {/* Potential Limitations */}
        <div className="rounded-xl border border-border bg-card p-4 space-y-2 shadow-sm">
          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block flex items-center gap-1">
            <AlertCircle className="h-4 w-4 text-amber-500 shrink-0" />
            Potential Limitations
          </span>
          <div className="text-xs text-muted-foreground/80 leading-relaxed space-y-1 font-normal">
            <div className="flex gap-1 items-start">
              <span className="text-amber-500 font-bold">•</span>
              <span>Vector chunks do not parse non-tabular drawing layers.</span>
            </div>
            <div className="flex gap-1 items-start">
              <span className="text-amber-500 font-bold">•</span>
              <span>Maintenance history excludes Reactor Unit 4 records.</span>
            </div>
          </div>
        </div>

        {/* Suggested Follow-up Questions */}
        <div className="rounded-xl border border-border bg-card p-4 space-y-2.5 shadow-sm">
          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block flex items-center gap-1">
            <HelpCircle className="h-4 w-4 text-primary shrink-0" />
            Suggested Follow-up
          </span>
          <div className="grid gap-1.5">
            {[
              'Inspect SV-901 valve settings',
              'Check Reactor Unit 5 safety logs',
              'View flow calibration guidelines',
            ].map((q, idx) => (
              <button
                key={idx}
                onClick={() => router.push('/chat')}
                className="w-full rounded border border-border bg-secondary/15 hover:bg-secondary text-left px-2.5 py-1.5 text-[10px] font-medium text-foreground transition-all cursor-pointer truncate"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>
      
    </div>
  );
}
