import React from 'react';
import { Cpu } from 'lucide-react';

export default function TypingIndicator() {
  return (
    <div className="flex gap-3 w-full animate-in fade-in duration-200 justify-start">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 border border-primary/20 text-primary animate-pulse">
        <Cpu className="h-4.5 w-4.5" />
      </div>

      <div className="flex flex-col space-y-1">
        <div className="text-[9px] font-bold text-primary uppercase tracking-wider pl-1 animate-pulse">
          AI Ingesting Context...
        </div>
        <div className="rounded-xl px-4 py-3 bg-card border border-border text-foreground rounded-tl-none flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:-0.3s]" />
          <span className="h-2 w-2 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:-0.15s]" />
          <span className="h-2 w-2 rounded-full bg-muted-foreground/60 animate-bounce" />
        </div>
      </div>
    </div>
  );
}
