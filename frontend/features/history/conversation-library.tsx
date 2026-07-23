'use client';

import React, { useState } from 'react';
import { Search, Pin, MessageSquare, ArrowRight, Eye, Download, Star } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { RetrievalMode } from '@/store/app-context';
import { showToast } from '@/lib/toast';

export interface HistoryConversation {
  id: string;
  title: string;
  createdDate: string;
  lastUpdated: string;
  duration: string;
  promptsCount: number;
  responsesCount: number;
  docCount: number;
  retrievalMode: RetrievalMode;
  category: string;
  isFavorite: boolean;
  status: 'Completed' | 'Active';
}

interface ConversationLibraryProps {
  conversations: HistoryConversation[];
  activeId: string;
  onSelect: (id: string) => void;
  onToggleFavorite: (id: string) => void;
}

export default function ConversationLibrary({
  conversations,
  activeId,
  onSelect,
  onToggleFavorite,
}: ConversationLibraryProps) {
  const router = useRouter();
  const [search, setSearch] = useState('');
  const [modeFilter, setModeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortOrder, setSortOrder] = useState<'newest' | 'oldest'>('newest');

  const handleExport = (title: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const conv = conversations.find(c => c.title === title);
    const data = JSON.stringify(conv, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `conversation_export.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast(`"${title}" exported to JSON successfully.`, 'success');
  };

  const handleContinueChat = (e: React.MouseEvent) => {
    e.stopPropagation();
    router.push('/chat');
  };

  const handleOpenTransparency = (e: React.MouseEvent) => {
    e.stopPropagation();
    router.push('/transparency');
  };

  // Filter & Sort
  const filtered = conversations
    .filter((conv) => {
      const matchesSearch =
        conv.title.toLowerCase().includes(search.toLowerCase()) ||
        conv.category.toLowerCase().includes(search.toLowerCase());

      const matchesMode =
        modeFilter === 'all' || conv.retrievalMode === modeFilter;

      const matchesStatus =
        statusFilter === 'all' || conv.status === statusFilter;

      return matchesSearch && matchesMode && matchesStatus;
    })
    .sort((a, b) => {
      // Pinned (Favorite) items always float to the top
      if (a.isFavorite && !b.isFavorite) return -1;
      if (!a.isFavorite && b.isFavorite) return 1;

      // Then apply chronology sort
      return sortOrder === 'newest'
        ? Number(b.id) - Number(a.id)
        : Number(a.id) - Number(b.id);
    });

  return (
    <div className="w-full lg:w-96 shrink-0 border-r border-border bg-card/60 flex flex-col h-full overflow-hidden">
      {/* Search & Sort Panel */}
      <div className="p-4 border-b border-border space-y-3 bg-card">
        <div className="flex justify-between items-center">
          <h2 className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
            Conversation Library
          </h2>
          <select
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value as 'newest' | 'oldest')}
            className="rounded border border-border bg-background px-2 py-0.5 text-[10px] text-foreground font-bold outline-none cursor-pointer"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
          </select>
        </div>

        {/* Search Input */}
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground/60" />
          <input
            type="text"
            placeholder="Search conversations, files..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-border bg-background pl-8 pr-3 py-2 text-xs text-foreground outline-none focus:border-primary placeholder:text-muted-foreground/50"
          />
        </div>
      </div>

      {/* Advanced Filters */}
      <div className="p-3 border-b border-border bg-secondary/15 flex gap-2 text-[10px]">
        {/* Mode filter */}
        <div className="flex-1 space-y-1">
          <label className="text-muted-foreground font-semibold">Mode</label>
          <select
            value={modeFilter}
            onChange={(e) => setModeFilter(e.target.value)}
            className="w-full rounded border border-border bg-background p-1 text-[10px] text-foreground outline-none"
          >
            <option value="all">All Modes</option>
            <option value="automatic">Automatic</option>
            <option value="manual">Manual</option>
          </select>
        </div>

        {/* Status filter */}
        <div className="flex-1 space-y-1">
          <label className="text-muted-foreground font-semibold">Status</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full rounded border border-border bg-background p-1 text-[10px] text-foreground outline-none"
          >
            <option value="all">All Status</option>
            <option value="Active">Active</option>
            <option value="Completed">Completed</option>
          </select>
        </div>
      </div>

      {/* Conversations Cards List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2.5">
        {filtered.length === 0 ? (
          <div className="text-xs text-muted-foreground italic px-3 py-4 text-center">
            No conversations matching filters.
          </div>
        ) : (
          filtered.map((conv) => {
            const isActive = activeId === conv.id;

            return (
              <div
                key={conv.id}
                onClick={() => onSelect(conv.id)}
                className={`relative flex flex-col rounded-xl border p-4 cursor-pointer transition-all ${
                  isActive
                    ? 'border-primary bg-secondary/80 text-foreground'
                    : 'border-border bg-card/45 hover:bg-secondary/20 text-muted-foreground hover:text-foreground'
                }`}
              >
                {/* Header Title Row */}
                <div className="flex justify-between items-start gap-2 border-b border-border/40 pb-2">
                  <div className="min-w-0">
                    <h3 className="text-xs font-bold text-foreground line-clamp-1 leading-relaxed">
                      {conv.title}
                    </h3>
                    <span className="text-[10px] text-muted-foreground/60 block mt-0.5">
                      Last active: {conv.lastUpdated}
                    </span>
                  </div>
                  
                  {/* Pin Toggle */}
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleFavorite(conv.id);
                    }}
                    className={`rounded p-1 hover:bg-secondary cursor-pointer shrink-0 transition-colors ${
                      conv.isFavorite ? 'text-primary font-bold' : 'text-muted-foreground/40 hover:text-foreground'
                    }`}
                  >
                    <Pin className={`h-4 w-4 ${conv.isFavorite ? 'fill-current -rotate-45' : ''}`} />
                  </button>
                </div>

                {/* Info Badges */}
                <div className="flex flex-wrap gap-1.5 pt-3">
                  <span className={`rounded-full px-2 py-0.5 text-[9px] font-bold uppercase leading-none border ${
                    conv.status === 'Active'
                      ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500'
                      : 'bg-neutral-500/10 border-neutral-500/20 text-muted-foreground'
                  }`}>
                    {conv.status}
                  </span>
                  <span className="rounded bg-secondary/85 border border-border px-1.5 py-0.5 text-[9px] font-extrabold text-foreground leading-none capitalize">
                    {conv.retrievalMode}
                  </span>
                  <span className="rounded bg-secondary/85 border border-border px-1.5 py-0.5 text-[9px] font-extrabold text-foreground leading-none">
                    {conv.promptsCount + conv.responsesCount} Messages
                  </span>
                </div>

                {/* Inline Action Buttons (Unified Module Cross-links) */}
                <div className="flex gap-2 mt-3 pt-3 border-t border-border/40 justify-end">
                  <button
                    type="button"
                    onClick={handleOpenTransparency}
                    className="inline-flex items-center gap-1 rounded bg-secondary hover:bg-secondary/80 text-[9px] font-bold text-foreground px-2 py-1 transition-colors cursor-pointer border border-border"
                    title="Audit Transparency Snapshots"
                  >
                    <Eye className="h-3 w-3" />
                    Audit RAG
                  </button>
                  <button
                    type="button"
                    onClick={handleContinueChat}
                    className="inline-flex items-center gap-1 rounded bg-primary hover:bg-primary/95 text-[9px] font-bold text-primary-foreground px-2 py-1 transition-colors cursor-pointer shadow-sm"
                    title="Continue conversation in Chatroom"
                  >
                    <MessageSquare className="h-3 w-3 fill-current" />
                    Continue
                  </button>
                </div>

              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
