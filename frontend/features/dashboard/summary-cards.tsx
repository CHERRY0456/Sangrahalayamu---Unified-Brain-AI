import React from 'react';
import { FileText, MessageSquare, Cpu, Key } from 'lucide-react';

const STATS = [
  { label: 'Documents Ingested', value: '1,429', icon: FileText, change: '+14 this week' },
  { label: 'AI Conversations', value: '84', icon: MessageSquare, change: '12 active today' },
  { label: 'Active Parser Tasks', value: '3', icon: Cpu, change: 'Running OCR...' },
  { label: 'Pending Access Keys', value: '2', icon: Key, change: 'Approval required' },
];

export default function SummaryCards() {
  return (
    <div className="grid gap-4 grid-cols-2 lg:grid-cols-4 w-full">
      {STATS.map((stat, i) => {
        const Icon = stat.icon;
        return (
          <div
            key={i}
            className="rounded-xl border border-border bg-card p-5 shadow-sm hover:shadow-md transition-all duration-200"
          >
            <div className="flex justify-between items-center text-muted-foreground mb-3">
              <span className="text-xs font-semibold tracking-wide uppercase truncate">
                {stat.label}
              </span>
              <Icon className="h-5 w-5 text-primary shrink-0" />
            </div>
            <div className="text-2xl font-bold text-foreground">{stat.value}</div>
            <p className="mt-1 text-[11px] text-muted-foreground font-medium">{stat.change}</p>
          </div>
        );
      })}
    </div>
  );
}
