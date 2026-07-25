'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { MessageSquare, ArrowRight } from 'lucide-react';
import { api } from '@/lib/api-client';

export default function RecentConversations() {
  const [conversations, setConversations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchConversations() {
      try {
        const res = await api.get<any>('/api/v1/history/conversations');
        if (res && res.data) {
          setConversations(res.data);
        }
      } catch (err) {
        console.error('Failed to fetch recent conversations:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchConversations();
  }, []);

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm flex flex-col h-full">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">
        Recent AI Conversations
      </h2>
      <div className="flex-1 space-y-3">
        {loading ? (
          <p className="text-xs text-muted-foreground animate-pulse py-4 text-center">
            Loading conversations...
          </p>
        ) : conversations.length === 0 ? (
          <div className="py-8 text-center space-y-2">
            <MessageSquare className="h-8 w-8 text-muted-foreground/40 mx-auto" />
            <p className="text-xs text-muted-foreground">No recent AI conversations found.</p>
            <Link
              href="/chat"
              className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-primary/10 hover:bg-primary/20 text-primary text-xs font-semibold px-3 py-1.5 transition-all"
            >
              Start New Chat
              <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
        ) : (
          conversations.map((conv, i) => (
            <div
              key={conv.id || i}
              className="flex items-center justify-between border-b border-border/40 pb-3 last:border-0 last:pb-0"
            >
              <div className="space-y-1 min-w-0 pr-2">
                <div className="flex items-center gap-1.5">
                  <MessageSquare className="h-3.5 w-3.5 text-primary shrink-0" />
                  <span className="text-xs font-bold text-foreground line-clamp-1">
                    {conv.title || 'Untitled Conversation'}
                  </span>
                </div>
                <div className="text-[10px] text-muted-foreground">
                  Started {conv.created_at ? new Date(conv.created_at).toLocaleDateString() : 'Recently'}
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
          ))
        )}
      </div>
    </div>
  );
}
