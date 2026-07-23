import React from 'react';
import Link from 'next/link';
import { MessageSquare, ArrowRight } from 'lucide-react';

const CONVERSATIONS = [
  {
    title: 'Valve V-402 Operating Limit',
    date: 'July 21, 2026',
    updated: '10 min ago',
  },
  {
    title: 'OSHA High Pressure Steam Boiler Regs',
    date: 'July 20, 2026',
    updated: '1 day ago',
  },
  {
    title: 'Pump P-101A Repair Log Analysis',
    date: 'July 18, 2026',
    updated: '3 days ago',
  },
];

export default function RecentConversations() {
  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm flex flex-col h-full">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">
        Recent AI Conversations
      </h2>
      <div className="flex-1 space-y-3">
        {CONVERSATIONS.map((conv, i) => (
          <div
            key={i}
            className="flex items-center justify-between border-b border-border/40 pb-3 last:border-0 last:pb-0"
          >
            <div className="space-y-1">
              <div className="flex items-center gap-1.5">
                <MessageSquare className="h-3.5 w-3.5 text-primary shrink-0" />
                <span className="text-xs font-bold text-foreground line-clamp-1">
                  {conv.title}
                </span>
              </div>
              <div className="text-[10px] text-muted-foreground">
                Started {conv.date} • Last active {conv.updated}
              </div>
            </div>
            <Link
              href="/chat"
              className="inline-flex items-center gap-1 rounded-lg border border-border bg-secondary/50 hover:bg-secondary px-2.5 py-1 text-[11px] font-semibold transition-all cursor-pointer text-foreground shrink-0"
            >
              Continue
              <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
