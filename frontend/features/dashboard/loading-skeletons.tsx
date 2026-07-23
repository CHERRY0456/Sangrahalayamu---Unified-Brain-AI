import React from 'react';

export function SummaryCardsSkeleton() {
  return (
    <div className="grid gap-4 grid-cols-2 lg:grid-cols-4 w-full animate-pulse">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="h-28 rounded-xl border border-border bg-card p-5 space-y-3">
          <div className="flex justify-between items-center">
            <div className="h-4 w-24 bg-muted rounded" />
            <div className="h-5 w-5 bg-muted rounded-full" />
          </div>
          <div className="h-7 w-12 bg-muted rounded" />
          <div className="h-3 w-16 bg-muted rounded" />
        </div>
      ))}
    </div>
  );
}

export function QuickActionsSkeleton() {
  return (
    <div className="rounded-xl border border-border bg-card p-6 space-y-4 animate-pulse">
      <div className="h-6 w-32 bg-muted rounded" />
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-20 rounded-lg bg-secondary p-3 flex flex-col justify-between">
            <div className="h-5 w-5 bg-muted rounded" />
            <div className="h-3 w-16 bg-muted rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function RecentDocumentsSkeleton() {
  return (
    <div className="rounded-xl border border-border bg-card p-6 space-y-4 animate-pulse">
      <div className="flex justify-between items-center">
        <div className="h-6 w-36 bg-muted rounded" />
        <div className="h-4 w-12 bg-muted rounded" />
      </div>
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="flex justify-between items-center border-b border-border/40 pb-3 last:border-0 last:pb-0">
            <div className="space-y-2">
              <div className="h-4.5 w-48 bg-muted rounded" />
              <div className="h-3.5 w-24 bg-muted rounded" />
            </div>
            <div className="h-5.5 w-16 bg-muted rounded-full" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function RecentConversationsSkeleton() {
  return (
    <div className="rounded-xl border border-border bg-card p-6 space-y-4 animate-pulse">
      <div className="h-6 w-44 bg-muted rounded" />
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="flex justify-between items-center border-b border-border/40 pb-3 last:border-0 last:pb-0">
            <div className="space-y-2">
              <div className="h-4.5 w-36 bg-muted rounded" />
              <div className="h-3 w-20 bg-muted rounded" />
            </div>
            <div className="h-8 w-16 bg-muted rounded-lg" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function ActivityTimelineSkeleton() {
  return (
    <div className="rounded-xl border border-border bg-card p-6 space-y-4 animate-pulse">
      <div className="h-6 w-32 bg-muted rounded" />
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="flex items-start">
            <div className="h-4.5 w-4.5 bg-muted rounded-full shrink-0" />
            <div className="space-y-2 flex-1" style={{ marginLeft: '16px' }}>
              <div className="h-4 w-3/4 bg-muted rounded" />
              <div className="h-3 w-16 bg-muted rounded" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function NotificationsPanelSkeleton() {
  return (
    <div className="rounded-xl border border-border bg-card p-6 space-y-4 animate-pulse">
      <div className="h-6 w-36 bg-muted rounded" />
      <div className="space-y-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-14 rounded-lg bg-secondary p-3 flex gap-2">
            <div className="h-4 w-4 bg-muted rounded-full shrink-0" />
            <div className="space-y-1.5 flex-1">
              <div className="h-3 w-5/6 bg-muted rounded" />
              <div className="h-2 w-12 bg-muted rounded" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
