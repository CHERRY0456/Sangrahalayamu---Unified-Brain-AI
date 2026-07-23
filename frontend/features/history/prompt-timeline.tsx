import React from 'react';
import { HelpCircle, MessageSquare, Eye, Key, CheckCircle, Flag } from 'lucide-react';

export interface TimelineEvent {
  type: 'prompt' | 'response' | 'transparency' | 'access_request' | 'system';
  label: string;
  timestamp: string;
}

interface PromptTimelineProps {
  events: TimelineEvent[];
}

export default function PromptTimeline({ events }: PromptTimelineProps) {
  
  const getEventIcon = (type: TimelineEvent['type']) => {
    switch (type) {
      case 'prompt':
        return HelpCircle;
      case 'response':
        return MessageSquare;
      case 'transparency':
        return Eye;
      case 'access_request':
        return Key;
      case 'system':
        return Flag;
    }
  };

  const getEventColors = (type: TimelineEvent['type']) => {
    switch (type) {
      case 'prompt':
        return 'bg-blue-500/10 border-blue-500/30 text-blue-500';
      case 'response':
        return 'bg-primary/10 border-primary/20 text-primary';
      case 'transparency':
        return 'bg-purple-500/10 border-purple-500/30 text-purple-500';
      case 'access_request':
        return 'bg-amber-500/10 border-amber-500/30 text-amber-500';
      case 'system':
        return 'bg-neutral-500/10 border-neutral-500/30 text-muted-foreground';
    }
  };

  return (
    <div className="space-y-4">
      <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
        Conversation Progression Timeline
      </span>

      <div className="relative pl-4 before:absolute before:left-[11px] before:top-2.5 before:bottom-2.5 before:w-0.5 before:bg-border">
        {events.map((event, idx) => {
          const Icon = getEventIcon(event.type);
          const colors = getEventColors(event.type);

          return (
            <div key={idx} className="relative flex gap-3 pb-5 last:pb-0 animate-in fade-in duration-200">
              {/* Event Icon Node */}
              <div
                className={`absolute -left-[18px] top-0.5 flex h-5 w-5 items-center justify-center rounded-full border bg-card z-10 ${colors}`}
              >
                <Icon className="h-3 w-3 shrink-0" />
              </div>

              {/* Event details */}
              <div className="space-y-0.5 min-w-0 flex-1">
                <div className="flex justify-between items-baseline gap-2">
                  <span className="text-[11px] font-bold text-foreground truncate">
                    {event.label}
                  </span>
                  <span className="text-[9px] text-muted-foreground/60 shrink-0 font-medium font-mono">
                    {event.timestamp}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
