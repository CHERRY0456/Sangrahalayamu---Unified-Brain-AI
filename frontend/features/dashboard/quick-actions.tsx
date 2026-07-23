import React from 'react';
import Link from 'next/link';
import { Upload, Cpu, MessageSquare, Network, ShieldCheck } from 'lucide-react';

const ACTIONS = [
  { label: 'Upload Documents', href: '/upload', icon: Upload, desc: 'Ingest new manuals or P&IDs' },
  { label: 'Processing Studio', href: '/processing', icon: Cpu, desc: 'OCR & schema parsing logs' },
  { label: 'Start AI Chat', href: '/chat', icon: MessageSquare, desc: 'Multimodal Q&A with citations' },
  { label: 'Transparency Map', href: '/transparency', icon: Network, desc: 'View database knowledge graph' },
  { label: 'Compliance Audit', href: '/audit', icon: ShieldCheck, desc: 'Run safety regulation check' },
];

export default function QuickActions() {
  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">
        Quick Action Command Center
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
        {ACTIONS.map((action, i) => {
          const Icon = action.icon;
          return (
            <Link
              key={i}
              href={action.href}
              className="flex flex-col justify-between rounded-lg border border-border bg-secondary/35 p-4 hover:bg-secondary transition-all group cursor-pointer"
            >
              <div className="rounded-md bg-background p-2 w-fit mb-4 group-hover:bg-primary group-hover:text-primary-foreground transition-colors shadow-sm">
                <Icon className="h-5 w-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-foreground truncate">{action.label}</div>
                <p className="text-[10px] text-muted-foreground mt-1 line-clamp-1">{action.desc}</p>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
