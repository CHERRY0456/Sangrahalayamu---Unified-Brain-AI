import React from 'react';
import { MessageSquare, Plus, Trash2 } from 'lucide-react';

interface Conversation {
  id: string;
  title: string;
  updatedAt: string;
}

interface ChatSidebarProps {
  conversations: Conversation[];
  activeId: string;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  onDeleteConversation: (id: string) => void;
}

export default function ChatSidebar({
  conversations,
  activeId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
}: ChatSidebarProps) {
  return (
    <div className="hidden lg:flex w-64 shrink-0 flex-col border-r border-border bg-card/60 h-[calc(100vh-8rem)]">
      {/* New Chat Button */}
      <div className="p-4 border-b border-border">
        <button
          onClick={onNewChat}
          className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-primary hover:bg-primary/95 text-primary-foreground py-2 text-sm font-semibold shadow-sm transition-all cursor-pointer"
        >
          <Plus className="h-4 w-4 shrink-0" />
          New Chat
        </button>
      </div>

      {/* History List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1">
        <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider px-3 mb-2">
          Chat History
        </div>

        {conversations.length === 0 ? (
          <div className="text-xs text-muted-foreground italic px-3 py-2">
            No active threads.
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = activeId === conv.id;
            return (
              <div
                key={conv.id}
                className={`group flex items-center justify-between rounded-lg px-3 py-2 text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-secondary text-foreground'
                    : 'text-muted-foreground hover:bg-secondary/40 hover:text-foreground'
                }`}
              >
                <button
                  type="button"
                  onClick={() => onSelectConversation(conv.id)}
                  className="flex-1 text-left truncate flex items-center gap-2 pr-2 cursor-pointer"
                >
                  <MessageSquare className="h-4 w-4 text-primary shrink-0" />
                  <span className="truncate">{conv.title}</span>
                </button>

                {/* Delete Trigger */}
                <button
                  type="button"
                  onClick={() => onDeleteConversation(conv.id)}
                  className="opacity-0 group-hover:opacity-100 rounded p-1 hover:bg-destructive/10 text-muted-foreground hover:text-destructive cursor-pointer transition-opacity shrink-0"
                  title="Delete Thread"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
