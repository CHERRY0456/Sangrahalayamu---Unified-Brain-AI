'use client';

import React, { useRef, useState, useEffect } from 'react';
import { Send, Paperclip } from 'lucide-react';
import { useAppStore } from '@/store/app-context';
import { showToast } from '@/lib/toast';

interface ChatInputProps {
  onSendMessage: (text: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSendMessage, disabled }: ChatInputProps) {
  const { setStagedFiles } = useAppStore();
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const maxChars = 1000;

  // Auto-resize textarea heights
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    
    // Reset height
    textarea.style.height = 'auto';
    // Set to scrollHeight
    textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
  }, [text]);

  const handleSend = () => {
    if (disabled || !text.trim()) return;
    onSendMessage(text.trim());
    setText('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    if (val.length <= maxChars) {
      setText(val);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const fileList = Array.from(files);
    
    // Append context files to global staged store
    setStagedFiles((prev) => [
      ...prev,
      ...fileList.map((f) => ({
        name: f.name,
        size: f.size,
        category: 'Other',
      })),
    ]);

    showToast(`${fileList.length} file(s) attached to conversation context.`, 'success');
  };

  const triggerFileInput = () => {
    if (disabled) return;
    fileInputRef.current?.click();
  };

  return (
    <div className="border-t border-border bg-card p-4 space-y-2">
      <div className="flex items-end gap-2 max-w-4xl mx-auto relative bg-background border border-border rounded-xl px-3 py-2.5 transition-colors focus-within:border-primary">
        
        {/* Hidden Attachment File Input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          disabled={disabled}
          onChange={handleFileChange}
          className="hidden"
          accept=".pdf,.docx,.xlsx,.pptx,.txt,.png,.jpg,.jpeg,.tiff,.bmp,.mp3,.wav,.m4a,.flac,.dwg,.dxf,.svg"
        />

        {/* Attach File Button */}
        <button
          type="button"
          onClick={triggerFileInput}
          disabled={disabled}
          className="flex h-8 w-8 items-center justify-center rounded-lg hover:bg-secondary text-muted-foreground hover:text-foreground cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          title="Attach Document Context"
        >
          <Paperclip className="h-4.5 w-4.5" />
        </button>

        {/* Text Input console */}
        <textarea
          ref={textareaRef}
          value={text}
          onChange={handleTextChange}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? "Please wait for AI response..." : "Ask a question about the repository documents (e.g. valve thresholds)..."}
          disabled={disabled}
          rows={1}
          className="flex-1 max-h-[120px] outline-none text-sm bg-transparent resize-none py-1.5 px-2 text-foreground placeholder:text-muted-foreground/70"
        />

        {/* Action Button */}
        <button
          type="button"
          onClick={handleSend}
          disabled={disabled || !text.trim()}
          className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground hover:bg-primary/95 transition-all shadow-sm cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>

      {/* Character Counter footer */}
      <div className="flex justify-end max-w-4xl mx-auto text-[10px] text-muted-foreground/60 pr-2">
        {text.length} / {maxChars} characters
      </div>
    </div>
  );
}
