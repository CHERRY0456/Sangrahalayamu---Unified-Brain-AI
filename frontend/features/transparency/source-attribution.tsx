import React from 'react';
import { Bookmark, Eye, Highlighter } from 'lucide-react';
import { showToast } from '@/lib/toast';

export interface ExplanationCitation {
  fileName: string;
  pages: string;
  sections: string[];
  whyCited?: string;
}

interface SourceAttributionProps {
  citations: ExplanationCitation[];
  interactive?: boolean;
}

export default function SourceAttribution({
  citations,
  interactive = false,
}: SourceAttributionProps) {
  
  const handleViewContext = (fileName: string, pages: string) => {
    showToast('Opening document context viewer...', 'info');
  };

  const handleHighlight = (fileName: string, sections: string[]) => {
    showToast('Reference sections highlighted in document viewer.', 'success');
  };

  return (
    <div className="space-y-3 animate-in fade-in duration-150">
      <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
        Source Attributions
      </span>
      <div className="space-y-3">
        {citations.map((cite, idx) => (
          <div
            key={idx}
            className="rounded-lg border border-border bg-card p-3.5 space-y-3 shadow-sm"
          >
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-foreground truncate max-w-[180px]">
                {cite.fileName}
              </span>
              <span className="text-[10px] bg-secondary border border-border px-1.5 py-0.5 rounded font-mono text-muted-foreground shrink-0">
                Pgs: {cite.pages}
              </span>
            </div>

            {/* Why Cited annotation */}
            {interactive && cite.whyCited && (
              <div className="text-[10px] text-muted-foreground/80 leading-relaxed bg-secondary/15 rounded p-2 border border-border/40">
                <span className="font-bold text-foreground block text-[9px] uppercase tracking-wide mb-0.5">
                  Why Cited
                </span>
                {cite.whyCited}
              </div>
            )}

            {/* Relevant Sections */}
            <div className="space-y-1">
              <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-1">
                <Bookmark className="h-3 w-3 text-primary shrink-0" />
                Target Sections
              </span>
              <div className="flex flex-wrap gap-1 pt-0.5">
                {cite.sections.map((sec, sIdx) => (
                  <span
                    key={sIdx}
                    className="rounded bg-secondary border border-border px-2 py-0.5 text-[9px] font-semibold text-foreground"
                  >
                    {sec}
                  </span>
                ))}
              </div>
            </div>

            {/* Interactive Action Buttons */}
            {interactive && (
              <div className="flex gap-2 pt-1 border-t border-border/40">
                <button
                  type="button"
                  onClick={() => handleViewContext(cite.fileName, cite.pages)}
                  className="flex-1 inline-flex items-center justify-center gap-1 rounded bg-secondary hover:bg-secondary/80 text-[10px] font-semibold text-foreground py-1.5 transition-all cursor-pointer border border-border"
                >
                  <Eye className="h-3.5 w-3.5" />
                  View Context
                </button>
                <button
                  type="button"
                  onClick={() => handleHighlight(cite.fileName, cite.sections)}
                  className="flex-1 inline-flex items-center justify-center gap-1 rounded bg-primary hover:bg-primary/95 text-[10px] font-semibold text-primary-foreground py-1.5 transition-all cursor-pointer shadow-sm"
                >
                  <Highlighter className="h-3.5 w-3.5" />
                  Highlight
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
