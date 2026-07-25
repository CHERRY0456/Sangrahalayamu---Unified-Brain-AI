'use client';

import React, { useState } from 'react';
import { Bell } from 'lucide-react';

export default function NotificationsPanel() {
  const [notifications] = useState<any[]>([]);

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm flex flex-col h-full">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <Bell className="h-4 w-4 text-primary shrink-0" />
          System Alerts
        </h2>
        <span className="rounded bg-secondary border border-border px-1.5 py-0.5 text-[9px] font-extrabold uppercase text-muted-foreground">
          {notifications.length} new
        </span>
      </div>

      <div className="flex-1 space-y-3">
        {notifications.length === 0 ? (
          <div className="py-8 text-center space-y-1">
            <Bell className="h-8 w-8 text-muted-foreground/30 mx-auto" />
            <p className="text-xs text-muted-foreground">No unread notifications</p>
          </div>
        ) : (
          notifications.map((notif, i) => (
            <div
              key={i}
              className="flex gap-3 rounded-lg bg-secondary/35 border border-border/60 p-3 hover:bg-secondary/55 transition-all duration-150"
            >
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
          ))
        )}
      </div>
    </div>
  );
}
