import React from 'react';
import { Percent, Award, MessageSquare, Eye, Key } from 'lucide-react';

interface ConversationMetricsProps {
  avgConfidence: number;
  explainabilityScore: number;
  responsesGenerated: number;
  transparencyViews: number;
  accessRequests: number;
}

export default function ConversationMetrics({
  avgConfidence,
  explainabilityScore,
  responsesGenerated,
  transparencyViews,
  accessRequests,
}: ConversationMetricsProps) {
  
  const metricItems = [
    { label: 'Avg Confidence', val: `${avgConfidence}%`, icon: Percent, color: 'text-blue-500 bg-blue-500/10' },
    { label: 'Explainability', val: `${explainabilityScore}/100`, icon: Award, color: 'text-emerald-500 bg-emerald-500/10' },
    { label: 'AI Responses', val: responsesGenerated, icon: MessageSquare, color: 'text-primary bg-primary/10' },
    { label: 'RAG Audits', val: transparencyViews, icon: Eye, color: 'text-purple-500 bg-purple-500/10' },
    { label: 'Access Requests', val: accessRequests, icon: Key, color: 'text-amber-500 bg-amber-500/10' },
  ];

  return (
    <div className="space-y-3">
      <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
        Conversation Governance Metrics
      </span>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {metricItems.map((item, idx) => {
          const Icon = item.icon;
          return (
            <div
              key={idx}
              className="rounded-xl border border-border bg-card p-3 space-y-1.5 shadow-sm"
            >
              <div className="flex justify-between items-start">
                <span className="text-[9px] text-muted-foreground font-semibold leading-normal truncate max-w-[80px]">
                  {item.label}
                </span>
                <div className={`rounded p-1 ${item.color} shrink-0`}>
                  <Icon className="h-3.5 w-3.5" />
                </div>
              </div>
              <div className="text-sm font-black text-foreground">
                {item.val}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
