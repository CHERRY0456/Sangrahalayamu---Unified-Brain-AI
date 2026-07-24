'use client';

import React, { useState, useEffect } from 'react';
import ConversationLibrary, { HistoryConversation } from '@/features/history/conversation-library';
import ConversationInspector, { InspectionDocument } from '@/features/history/conversation-inspector';
import { TimelineEvent } from '@/features/history/prompt-timeline';
import PermissionGuard from '@/features/persona/permission-guard';

export default function HistoryPage() {
  const [conversations, setConversations] = useState<HistoryConversation[]>([]);
  const [activeId, setActiveId] = useState('');
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [docs, setDocs] = useState<InspectionDocument[]>([]);

  // Fetch all conversations
  useEffect(() => {
    async function fetchConversations() {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const token = localStorage.getItem('ib-access-token');
        const res = await fetch(`${baseUrl}/api/chat/conversations`, { credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
          }
        });
        if (res.ok) {
          const data = await res.json();
          // Map backend conversations to HistoryConversation shape
          const mapped: HistoryConversation[] = data.map((c: any) => ({
            id: c.id,
            title: c.title,
            createdDate: c.updatedAt ? new Date(c.updatedAt).toLocaleDateString() : 'Unknown',
            lastUpdated: c.updatedAt ? new Date(c.updatedAt).toLocaleTimeString() : 'Just now',
            duration: '2m',
            promptsCount: Math.max(1, Math.ceil(c.responsesCount / 2)),
            responsesCount: Math.max(1, Math.floor(c.responsesCount / 2)),
            docCount: 1,
            retrievalMode: 'automatic',
            category: 'Compliance',
            isFavorite: false,
            status: 'Completed'
          }));
          setConversations(mapped);
          if (mapped.length > 0 && !activeId) {
            setActiveId(mapped[0].id);
          }
        }
      } catch (err) {
        console.error('Failed to fetch conversations:', err);
      }
    }
    fetchConversations();
  }, [activeId]);

  // Fetch messages for the selected conversation
  useEffect(() => {
    if (!activeId) return;

    async function fetchMessages() {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const token = localStorage.getItem('ib-access-token');
        const res = await fetch(`${baseUrl}/api/chat/conversations/${activeId}/messages`, { credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
          }
        });
        if (res.ok) {
          const messages = await res.json();
          
          // Generate timeline events from message history
          const timeline: TimelineEvent[] = messages.map((m: any) => ({
            time: m.timestamp || '',
            label: m.sender === 'user' ? 'User Query Submitted' : 'AI Response Rendered',
            description: m.text.substring(0, 80) + (m.text.length > 80 ? '...' : ''),
            status: 'completed'
          }));
          setEvents(timeline);

          // Extract documents from message metadata
          const documentsMap = new Map<string, InspectionDocument>();
          messages.forEach((m: any) => {
            if (m.sender === 'ai' && m.metadata) {
              const sources = m.metadata.sources || [];
              const citations = m.metadata.citations || [];
              
              sources.forEach((src: any) => {
                const name = src.document_name || `Doc ${src.document_id}`;
                documentsMap.set(name, {
                  name,
                  category: 'Reference Doc',
                  confidence: 'High',
                  usedInResponse: true
                });
              });

              citations.forEach((c: any) => {
                const name = c.document_name || `Doc ${c.document_id}`;
                if (!documentsMap.has(name)) {
                  documentsMap.set(name, {
                    name,
                    category: 'Reference Doc',
                    confidence: 'High',
                    usedInResponse: true
                  });
                }
              });
            }
          });
          setDocs(Array.from(documentsMap.values()));
        }
      } catch (err) {
        console.error('Failed to fetch conversation messages:', err);
      }
    }
    fetchMessages();
  }, [activeId]);

  const handleSelect = (id: string) => {
    setActiveId(id);
  };

  const handleToggleFavorite = (id: string) => {
    setConversations((prev) =>
      prev.map((c) => (c.id === id ? { ...c, isFavorite: !c.isFavorite } : c))
    );
  };

  const activeConv = conversations.find((c) => c.id === activeId) || null;

  return (
    <PermissionGuard permission="history">
      <div className="space-y-6 max-w-7xl mx-auto animate-in fade-in duration-300">
      {/* Page Header */}
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Conversation Library</h1>
        <p className="text-sm text-muted-foreground">
          Audit previous chat sessions, inspect prompt timelines, and track document references.
        </p>
      </div>

      {/* Main Split Layout */}
      <div className="flex flex-col lg:flex-row h-[calc(100vh-8rem)] rounded-xl border border-border bg-card/25 overflow-hidden shadow-sm">
        
        {/* Left Side Library listing */}
        <ConversationLibrary
          conversations={conversations}
          activeId={activeId}
          onSelect={handleSelect}
          onToggleFavorite={handleToggleFavorite}
        />

        {/* Right Side detailed Inspector */}
        <ConversationInspector
          conversation={activeConv}
          events={events}
          documents={docs}
          avgConfidence={activeConv?.id === '1' ? 92 : activeConv?.id === '2' ? 88 : 95}
          explainabilityScore={activeConv?.id === '1' ? 94 : activeConv?.id === '2' ? 89 : 96}
          responsesGenerated={activeConv?.responsesCount || 0}
          transparencyViews={activeConv?.id === '1' ? 2 : activeConv?.id === '2' ? 1 : 0}
          accessRequests={activeConv?.id === '3' ? 1 : 0}
        />

      </div>
      </div>
    </PermissionGuard>
  );
}
