import React from 'react';
import { useAppStore } from '@/store/app-context';
import { Percent, ShieldCheck } from 'lucide-react';

interface ConfidenceCardProps {
  overallConfidence: number;
  evidenceStrength: 'High' | 'Medium' | 'Low';
  docCoverage: string;
}

export default function ConfidenceCard({
  overallConfidence,
  evidenceStrength,
  docCoverage,
}: ConfidenceCardProps) {
  const { retrievalMode } = useAppStore();

  const getStrengthColor = (str: 'High' | 'Medium' | 'Low') => {
    switch (str) {
      case 'High':
        return 'text-emerald-500 font-bold';
      case 'Medium':
        return 'text-amber-500 font-bold';
      case 'Low':
        return 'text-destructive font-bold';
    }
  };

  return (
    <div className="rounded-xl border border-border bg-secondary/15 p-4 space-y-3.5">
      <div className="flex items-center gap-2">
        <ShieldCheck className="h-4.5 w-4.5 text-primary" />
        <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
          Confidence Metrics
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Overall Confidence */}
        <div className="space-y-1 bg-card rounded-lg border border-border/60 p-3 text-center flex flex-col justify-center items-center">
          <span className="text-[10px] text-muted-foreground font-semibold">Overall Rating</span>
          <div className="text-xl font-black text-foreground flex items-center justify-center gap-0.5 mt-1">
            {overallConfidence}
            <Percent className="h-4.5 w-4.5 text-primary shrink-0" />
          </div>
        </div>

        {/* Evidence & Coverage */}
        <div className="space-y-2 text-xs flex flex-col justify-center">
          <div className="space-y-0.5">
            <span className="text-[10px] text-muted-foreground font-semibold">Evidence Strength</span>
            <div className={`text-xs ${getStrengthColor(evidenceStrength)}`}>{evidenceStrength}</div>
          </div>
          
          <div className="space-y-0.5">
            <span className="text-[10px] text-muted-foreground font-semibold">Doc Coverage</span>
            <div className="font-bold text-foreground">{docCoverage}</div>
          </div>
        </div>
      </div>

      <div className="border-t border-border/80 pt-2 text-[10px] text-muted-foreground flex justify-between">
        <span>Active Retrieval Mode:</span>
        <b className="capitalize text-foreground font-bold">{retrievalMode}</b>
      </div>
    </div>
  );
}
