import React from 'react';
import { ProcessingOptionsState } from '@/store/app-context';
import { AlignLeft, Box, Network, CalendarDays, Lightbulb, ShieldAlert } from 'lucide-react';

interface ProcessingOptionsProps {
  options: ProcessingOptionsState;
  onChangeOptions: React.Dispatch<React.SetStateAction<ProcessingOptionsState>>;
}

const OPTION_METADATA = [
  {
    key: 'summarization' as keyof ProcessingOptionsState,
    label: 'Document Summarization',
    icon: AlignLeft,
    desc: 'Synthesizes long files into concise, multi-level executive summaries.',
  },
  {
    key: 'entityExtraction' as keyof ProcessingOptionsState,
    label: 'Entity Extraction',
    icon: Box,
    desc: 'Extracts physical components (valves, pumps, gauges) and details.',
  },
  {
    key: 'relationshipDiscovery' as keyof ProcessingOptionsState,
    label: 'Relationship Discovery',
    icon: Network,
    desc: 'Extracts connectivity mapping (e.g. "this valve belongs to this pump").',
  },
  {
    key: 'timelineExtraction' as keyof ProcessingOptionsState,
    label: 'Timeline Extraction',
    icon: CalendarDays,
    desc: 'Assembles chronological logs of maintenance histories or safety logs.',
  },
  {
    key: 'keyInsights' as keyof ProcessingOptionsState,
    label: 'Key Insights',
    icon: Lightbulb,
    desc: 'Distills major operational metrics, thresholds, and performance ranges.',
  },
  {
    key: 'complianceAnalysis' as keyof ProcessingOptionsState,
    label: 'Compliance Analysis',
    icon: ShieldAlert,
    desc: 'Evaluates procedures against regulatory standards (OSHA/ISO).',
  },
];

export default function ProcessingOptions({
  options,
  onChangeOptions,
}: ProcessingOptionsProps) {
  
  const handleToggle = (key: keyof ProcessingOptionsState) => {
    onChangeOptions((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm space-y-4">
      <div>
        <h2 className="text-md font-semibold text-foreground">AI Processing Capabilities</h2>
        <p className="text-xs text-muted-foreground mt-0.5">
          Select which data extraction models should run during batch ingestion.
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        {OPTION_METADATA.map((opt) => {
          const Icon = opt.icon;
          const isEnabled = options[opt.key];

          return (
            <div
              key={opt.key}
              onClick={() => handleToggle(opt.key)}
              className={`flex items-start rounded-lg border p-4 cursor-pointer transition-all select-none ${
                isEnabled
                  ? 'border-primary/80 bg-primary/5 shadow-sm'
                  : 'border-border bg-secondary/10 hover:bg-secondary/35 text-muted-foreground'
              }`}
            >
              <div
                className={`rounded-md p-2 mr-3 shrink-0 ${
                  isEnabled ? 'bg-primary text-primary-foreground' : 'bg-background text-muted-foreground'
                }`}
              >
                <Icon className="h-4.5 w-4.5" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-foreground truncate">{opt.label}</span>
                  {/* Mock Toggle Switch */}
                  <div
                    className={`relative inline-flex h-5.5 w-10 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out ${
                      isEnabled ? 'bg-emerald-600 dark:bg-emerald-500' : 'bg-neutral-300 dark:bg-neutral-800'
                    }`}
                  >
                    <span
                      className="pointer-events-none inline-block h-4.5 w-4.5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                      style={{ transform: isEnabled ? 'translateX(18px)' : 'translateX(0)' }}
                    />
                  </div>
                </div>
                <p className="text-[10px] text-muted-foreground mt-1.5 leading-normal leading-relaxed">
                  {opt.desc}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
