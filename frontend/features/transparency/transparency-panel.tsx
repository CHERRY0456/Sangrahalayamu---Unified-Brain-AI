'use client';

import React from 'react';
import { X, Eye, ShieldAlert } from 'lucide-react';
import RetrievedDocuments, { ExplanationDocument } from './retrieved-documents';
import ReasoningTimeline, { ExplanationReasoningStep } from './reasoning-timeline';
import ConfidenceCard from './confidence-card';
import SourceAttribution, { ExplanationCitation } from './source-attribution';
import GraphPreview, { ExplanationGraph } from './graph-preview';
import { usePersonaStore } from '@/features/persona/persona-context';

export interface ExplanationData {
  messageId: string;
  overallConfidence: number;
  evidenceStrength: 'High' | 'Medium' | 'Low';
  docCoverage: string;
  documents: ExplanationDocument[];
  reasoningSteps: ExplanationReasoningStep[];
  citations: ExplanationCitation[];
  graph: ExplanationGraph;
}

interface TransparencyPanelProps {
  isOpen: boolean;
  onClose: () => void;
  explanation: ExplanationData | null;
}

export default function TransparencyPanel({
  isOpen,
  onClose,
  explanation,
}: TransparencyPanelProps) {
  const { persona } = usePersonaStore();

  if (!isOpen) return null;

  return (
    <div className="w-full lg:w-96 shrink-0 border-l border-border bg-card/40 flex flex-col h-full overflow-hidden animate-in slide-in-from-right duration-250 z-30">
      
      {/* Title Header */}
      <div className="p-4 border-b border-border flex justify-between items-center bg-card">
        <div className="flex items-center gap-2">
          <Eye className="h-4.5 w-4.5 text-primary shrink-0" />
          <h2 className="text-sm font-bold text-foreground">AI Explainability</h2>
        </div>
        <button
          onClick={onClose}
          className="rounded p-1 hover:bg-secondary text-muted-foreground hover:text-foreground cursor-pointer"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Main scrollable body content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        
        {/* Dynamic Persona-Aware Perspective Banner */}
        {persona && (
          <div className="rounded-lg bg-primary/5 border border-primary/20 p-3 text-[10px] text-primary leading-relaxed font-semibold space-y-1">
            <span className="flex items-center gap-1 uppercase tracking-wider text-[8px] text-primary/70">
              <ShieldAlert className="h-3 w-3 shrink-0" />
              {persona.role} Focus Perspective
            </span>
            <p>{persona.transparencyFocus}</p>
          </div>
        )}

        {!explanation ? (
          <div className="text-center py-12 text-xs text-muted-foreground italic space-y-2">
            <div>Click "Explain Response" below any AI chat message to load diagnostic explainability data.</div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Confidence Metrics */}
            <ConfidenceCard
              overallConfidence={explanation.overallConfidence}
              evidenceStrength={explanation.evidenceStrength}
              docCoverage={explanation.docCoverage}
            />

            <hr className="border-border/60" />

            {/* Retrieved Documents */}
            <RetrievedDocuments documents={explanation.documents} />

            <hr className="border-border/60" />

            {/* Reasoning Timeline */}
            <ReasoningTimeline steps={explanation.reasoningSteps} />

            <hr className="border-border/60" />

            {/* Citations */}
            <SourceAttribution citations={explanation.citations} />

            <hr className="border-border/60" />

            {/* Graph Node previews */}
            <GraphPreview graph={explanation.graph} />
          </div>
        )}
      </div>
    </div>
  );
}
