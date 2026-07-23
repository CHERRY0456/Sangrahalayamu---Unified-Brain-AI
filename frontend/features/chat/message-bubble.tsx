import React from 'react';
import { Cpu, User, Lock } from 'lucide-react';
import { usePersonaStore } from '@/features/persona/persona-context';

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: string;
}

interface MessageBubbleProps {
  message: Message;
  onTriggerRequestAccess?: () => void;
  onExplainResponse?: () => void;
}

export default function MessageBubble({
  message,
  onTriggerRequestAccess,
  onExplainResponse,
}: MessageBubbleProps) {
  const isAI = message.sender === 'ai';
  const { profile } = usePersonaStore();

  const getInitials = () => {
    if (!profile) return 'U';
    return profile.name
      .split(' ')
      .map((n) => n[0] || '')
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  // Light-weight regex parser to format markdown (bold, bullet points, code blocks)
  const formatMessageText = (text: string) => {
    // 1. Check if the message contains our special [Request Access] action button hook
    if (text.includes('[Request Access]')) {
      const parts = text.split('[Request Access]');
      return (
        <div className="space-y-2">
          <div className="space-y-1 text-sm leading-relaxed font-normal">
            <span dangerouslySetInnerHTML={{ __html: parts[0].replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
          </div>
          <button
            type="button"
            onClick={onTriggerRequestAccess}
            className="inline-flex items-center gap-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-white font-bold text-xs py-1.5 px-3.5 shadow-sm transition-all cursor-pointer"
          >
            <Lock className="h-3.5 w-3.5" />
            Request Access Clearance
          </button>
          {parts[1] && (
            <div className="space-y-1 text-sm leading-relaxed font-normal mt-2">
              <span dangerouslySetInnerHTML={{ __html: parts[1].replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
            </div>
          )}
        </div>
      );
    }

    // 2. Escape basic HTML elements
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // 3. Parse Code Blocks ```code```
    const codeBlockRegex = /```([\s\S]*?)```/g;
    html = html.replace(codeBlockRegex, (_, code) => {
      return `<pre class="bg-secondary/90 border border-border rounded-lg p-3 my-3 font-mono text-xs overflow-x-auto text-foreground whitespace-pre"><code>${code.trim()}</code></pre>`;
    });

    // 4. Parse Bold **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // 5. Parse Bullet Points "- item"
    const lines = html.split('\n');
    const formattedLines = lines.map((line) => {
      if (line.trim().startsWith('- ')) {
        return `<li class="ml-4 list-disc my-1">${line.trim().substring(2)}</li>`;
      }
      return line;
    });
    html = formattedLines.join('<br />');

    return (
      <div 
        dangerouslySetInnerHTML={{ __html: html }} 
        className="space-y-1 text-sm leading-relaxed font-normal" 
      />
    );
  };

  return (
    <div
      className={`flex gap-3 w-full animate-in fade-in duration-150 ${
        isAI ? 'justify-start' : 'justify-end'
      }`}
    >
      {/* Icon Avatar */}
      {isAI && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 border border-primary/20 text-primary">
          <Cpu className="h-4.5 w-4.5" />
        </div>
      )}

      {/* Message Box */}
      <div className="flex flex-col max-w-[85%] space-y-1">


        <div
          className={`rounded-xl px-4 py-3 shadow-sm border transition-all ${
            isAI
              ? 'bg-card border-border text-foreground rounded-tl-none'
              : 'bg-primary border-primary text-primary-foreground rounded-tr-none'
          }`}
        >
          {formatMessageText(message.text)}
        </div>

        {/* Timestamp / Actions Footer */}
        <div
          className={`flex items-center gap-1.5 text-[9px] text-muted-foreground/60 px-1 font-medium ${
            isAI ? 'justify-start' : 'justify-end'
          }`}
        >
          <span>{message.timestamp}</span>
          {isAI && onExplainResponse && (
            <>
              <span>•</span>
              <button
                type="button"
                onClick={onExplainResponse}
                className="hover:text-primary hover:underline cursor-pointer font-bold"
              >
                Explain Response
              </button>
            </>
          )}
        </div>
      </div>

      {/* User Avatar */}
      {!isAI && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs font-semibold shadow-sm select-none">
          {getInitials()}
        </div>
      )}
    </div>
  );
}
