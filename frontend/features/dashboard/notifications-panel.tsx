import React from 'react';
import { Cpu, CheckCircle2, FileUp, Bell } from 'lucide-react';

const NOTIFICATIONS = [
  {
    title: 'Processing Completed',
    desc: 'Boiler manual SOP OCR extraction finished with 98.4% parser score.',
    time: '2 mins ago',
    icon: Cpu,
    color: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
  },
  {
    title: 'Access Request Approved',
    desc: 'SRE department has granted your access keys to natural gas pipeline records.',
    time: '45 mins ago',
    icon: CheckCircle2,
    color: 'text-primary bg-primary/10 border-primary/20',
  },
  {
    title: 'New Bulk Upload Ready',
    desc: 'Texas Refinery maintenance file uploads successfully queued for parsing.',
    time: '2 hours ago',
    icon: FileUp,
    color: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
  },
];

export default function NotificationsPanel() {
  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm flex flex-col h-full">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <Bell className="h-4 w-4 text-primary shrink-0" />
          System Alerts
        </h2>
        <span className="rounded bg-primary/10 border border-primary/20 px-1.5 py-0.5 text-[9px] font-extrabold uppercase text-primary">
          3 new
        </span>
      </div>

      <div className="flex-1 space-y-3">
        {NOTIFICATIONS.map((notif, i) => {
          const Icon = notif.icon;
          return (
            <div
              key={i}
              className="flex gap-3 rounded-lg bg-secondary/35 border border-border/60 p-3 hover:bg-secondary/55 transition-all duration-150"
            >
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border ${notif.color}`}
              >
                <Icon className="h-4 w-4 shrink-0" />
              </div>
              <div className="space-y-0.5 flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-bold text-foreground truncate">{notif.title}</span>
                  <span className="text-[9px] text-muted-foreground/60 shrink-0 font-medium">{notif.time}</span>
                </div>
                <p className="text-[10px] text-muted-foreground leading-snug line-clamp-2">
                  {notif.desc}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
