'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAppStore } from '@/store/app-context';
import { usePersonaStore } from '@/features/persona/persona-context';
import PermissionGuard from '@/features/persona/permission-guard';
import ChatSidebar from '@/features/chat/chat-sidebar';
import ConversationContextBar from '@/features/chat/conversation-context-bar';
import MessageBubble from '@/features/chat/message-bubble';
import TypingIndicator from '@/features/chat/typing-indicator';
import ChatInput from '@/features/chat/chat-input';
import NeedMoreDocumentsModal from '@/features/chat/need-more-documents-modal';
import RequestAccessModal from '@/features/chat/request-access-modal';
import TransparencyPanel, { ExplanationData } from '@/features/transparency/transparency-panel';

interface Conversation {
  id: string;
  title: string;
  updatedAt: string;
}

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: string;
}



export default function ChatPage() {
  const { stagedFiles, retrievalMode, setRetrievalMode, processingOptions } = useAppStore();
  const { persona, workspaceManifest } = usePersonaStore();

  const [conversations, setConversations] = useState<Conversation[]>([]);

  const [activeId, setActiveId] = useState<string>('');
  const [messagesMap, setMessagesMap] = useState<Record<string, Message[]>>({});

  const [explanations, setExplanations] = useState<Record<string, ExplanationData>>({});

  // Split-screen explainability sidebar states
  const [selectedExplanation, setSelectedExplanation] = useState<ExplanationData | null>(null);
  const [isTransparencyOpen, setIsTransparencyOpen] = useState(false);

  // Modals overlays state
  const [isManageContextOpen, setIsManageContextOpen] = useState(false);
  const [isRequestAccessOpen, setIsRequestAccessOpen] = useState(false);
  const [restrictedDocsForModal, setRestrictedDocsForModal] = useState<any[] | undefined>(undefined);

  // Typing & Stream loading states
  const [isTyping, setIsTyping] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);

  // Helper to parse potential JSON string answers from the backend
  const parseAiMessageText = (text: string): string => {
    try {
      if (text.trim().startsWith('{')) {
        const parsed = JSON.parse(text);
        if (parsed && typeof parsed.answer === 'string') {
          return parsed.answer;
        }
      }
    } catch (e) {
      // Ignore
    }
    return text;
  };

  // 1. Fetch conversations list on mount
  useEffect(() => {
    async function loadConversations() {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const accessToken = localStorage.getItem('ib-access-token');
        const res = await fetch(`${baseUrl}/api/chat/conversations`, {
          headers: {
            'Content-Type': 'application/json',
            ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
          }
        });
        if (res.ok) {
          const list = await res.json();
          const formatted = list.map((c: any) => ({
            id: c.id,
            title: c.title,
            updatedAt: c.updatedAt ? new Date(c.updatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Just now',
          }));
          setConversations(formatted);
          if (formatted.length > 0) {
            setActiveId(formatted[0].id);
          } else {
            // Auto-create a session if library is empty
            handleNewChatInline();
          }
        }
      } catch (err) {
        console.error('Failed to load conversations:', err);
      }
    }
    loadConversations();
  }, []);

  // Inline fallback helper to create conversation during initial mount
  const handleNewChatInline = () => {
    const newId = crypto.randomUUID();
    const newConv: Conversation = {
      id: newId,
      title: `New Query Session`,
      updatedAt: 'Just now',
    };
    setConversations([newConv]);
    setMessagesMap(prev => ({
      ...prev,
      [newId]: [
        {
          id: `init-${newId}`,
          sender: 'ai',
          text: `Session initialized. I am ready to process questions using retrieval mode **${retrievalMode}**.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
      ]
    }));
    setActiveId(newId);
  };

  // 2. Fetch messages when activeId changes
  useEffect(() => {
    if (!activeId) return;
    if (messagesMap[activeId] && messagesMap[activeId].length > 1) return;

    async function loadMessages() {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const accessToken = localStorage.getItem('ib-access-token');
        const res = await fetch(`${baseUrl}/api/chat/conversations/${activeId}/messages`, {
          headers: {
            'Content-Type': 'application/json',
            ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
          }
        });
        if (res.ok) {
          const data = await res.json();
          if (data.length > 0) {
            const msgs: Message[] = data.map((m: any) => ({
              id: m.id,
              sender: m.sender,
              text: m.sender === 'ai' ? parseAiMessageText(m.text) : m.text,
              timestamp: m.timestamp || '00:00 AM'
            }));
            setMessagesMap(prev => ({ ...prev, [activeId]: msgs }));
          } else {
            setMessagesMap(prev => ({
              ...prev,
              [activeId]: [
                {
                  id: `init-${activeId}`,
                  sender: 'ai',
                  text: `Session initialized. I am ready to process questions using retrieval mode **${retrievalMode}**.`,
                  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                }
              ]
            }));
          }
        }
      } catch (err) {
        console.error('Failed to load messages:', err);
      }
    }
    loadMessages();
  }, [activeId]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messagesMap, activeId, isTyping, isStreaming]);

  const activeMessages = messagesMap[activeId] || [];

  const handleSelectConversation = (id: string) => {
    if (isStreaming || isTyping) return;
    setActiveId(id);
    setSelectedExplanation(null);
    setIsTransparencyOpen(false);
  };

  const handleNewChat = () => {
    if (isStreaming || isTyping) return;
    const newId = crypto.randomUUID();
    const newConv: Conversation = {
      id: newId,
      title: `New Query Session`,
      updatedAt: 'Just now',
    };
    setConversations((prev) => [newConv, ...prev]);
    setMessagesMap((prev) => ({
      ...prev,
      [newId]: [
        {
          id: `init-${newId}`,
          sender: 'ai',
          text: `Session initialized. I am ready to process questions using retrieval mode **${retrievalMode}**.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ],
    }));
    setActiveId(newId);
    setSelectedExplanation(null);
    setIsTransparencyOpen(false);
  };

  const handleDeleteConversation = async (id: string) => {
    if (isStreaming || isTyping) return;
    setConversations((prev) => prev.filter((c) => c.id !== id));
    
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const accessToken = localStorage.getItem('ib-access-token');
      await fetch(`${baseUrl}/api/chat/conversations/${id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
        }
      });
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }

    if (activeId === id) {
      setActiveId('');
    }
  };

  const handleSendMessage = async (text: string) => {
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMsg: Message = {
      id: Math.random().toString(),
      sender: 'user',
      text,
      timestamp: timeStr,
    };

    // 1. Add user message
    setMessagesMap((prev) => ({
      ...prev,
      [activeId]: [...(prev[activeId] || []), userMsg],
    }));

    // 2. Trigger typing indicator
    setIsTyping(true);

    const newMsgId = Math.random().toString();
    const aiMsg: Message = {
      id: newMsgId,
      sender: 'ai',
      text: '',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const accessToken = typeof window !== 'undefined' ? localStorage.getItem('ib-access-token') : null;
      const response = await fetch(`${baseUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
        },
        body: JSON.stringify({
          query: text,
          workspace_id: 'default',
          conversation_id: activeId,
          stream: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }

      setIsTyping(false);
      setIsStreaming(true);

      // Register initial empty AI message bubble
      setMessagesMap((prev) => ({
        ...prev,
        [activeId]: [...(prev[activeId] || []), aiMsg],
      }));

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let currentText = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.replace('data: ', '').trim();
              if (dataStr === '[DONE]') continue;
              
              try {
                const data = JSON.parse(dataStr);
                if (data.type === 'token' || data.content) {
                   // Handle both {type: 'token', content: '...'} and generic strings
                   const token = typeof data === 'string' ? data : (data.content || '');
                   currentText += token;

                   setMessagesMap((prev) => {
                     const list = prev[activeId] || [];
                     if (list.length > 0) {
                       const updatedList = [...list];
                       updatedList[updatedList.length - 1] = {
                         ...updatedList[updatedList.length - 1],
                         text: currentText,
                       };
                       return { ...prev, [activeId]: updatedList };
                     }
                     return prev;
                   });
                } else if (data.type === 'metadata') {
                  // Capture final metadata/citations and map them to our ExplanationData structure
                  const meta = data.metadata || data.content || data;
                  const dynamicExp: ExplanationData = {
                    messageId: newMsgId,
                    overallConfidence: meta.confidence_score || 95,
                    evidenceStrength: 'High',
                    docCoverage: meta.citations?.length ? `${meta.citations.length} documents` : 'Global Index',
                    documents: meta.citations?.map((c: any) => ({
                      name: c.document_id,
                      category: 'Extracted Content',
                      confidence: 'High',
                      relevanceTag: 'Primary'
                    })) || [],
                    reasoningSteps: meta.reasoning_steps?.map((step: string) => ({
                      label: 'Reasoning Step',
                      description: step,
                      status: 'completed'
                    })) || [
                      { label: 'Semantic Matching', description: 'Matched via Vector Database', status: 'completed' }
                    ],
                    citations: meta.citations?.map((c: any) => ({
                      fileName: c.document_id,
                      pages: '1',
                      sections: [c.snippet.substring(0, 30) + '...']
                    })) || [],
                    graph: {
                      nodes: [
                        { id: 'n1', label: 'Semantic Matching', type: 'compliance' },
                      ],
                      links: [],
                    }
                  };
                  
                  setExplanations(prev => ({ ...prev, [newMsgId]: dynamicExp }));
                }
              } catch (e) {
                // Ignore parse errors on partial chunks
              }
            }
          }
        }
      }
    } catch (e) {
      console.error('Chat API Error:', e);
      const errorText = 'Sorry, there was an error communicating with the backend. Please ensure the backend server is running.';
      setMessagesMap((prev) => {
        const list = prev[activeId] || [];
        const updatedList = [...list];
        // If we hadn't added the bubble yet, add it
        if (updatedList[updatedList.length - 1]?.id !== newMsgId) {
            updatedList.push({ ...aiMsg, text: errorText });
        } else {
            updatedList[updatedList.length - 1].text = errorText;
        }
        return { ...prev, [activeId]: updatedList };
      });
    } finally {
      setIsTyping(false);
      setIsStreaming(false);
    }
  };

  const handleExplainResponse = async (msgId: string) => {
    if (explanations[msgId]) {
      setSelectedExplanation(explanations[msgId]);
      setIsTransparencyOpen(true);
      return;
    }

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const accessToken = localStorage.getItem('ib-access-token');
      const res = await fetch(`${baseUrl}/api/chat/explain/${msgId}`, {
        headers: {
          'Content-Type': 'application/json',
          ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
        }
      });
      if (res.ok) {
        const expData = await res.json();
        setExplanations(prev => ({ ...prev, [msgId]: expData }));
        setSelectedExplanation(expData);
        setIsTransparencyOpen(true);
      }
    } catch (err) {
      console.error('Failed to fetch explanation from backend:', err);
    }
  };

  const handleTriggerRequestAccess = (msgId?: string) => {
    if (msgId) {
      const msg = activeMessages.find((m) => m.id === msgId);
      const text = msg?.text.toLowerCase() || '';
      
      if (text.includes('boiler') || text.includes('cylinder')) {
        setRestrictedDocsForModal([
          {
            name: 'Boiler_Calibration_SOP.docx',
            category: 'Compliance',
            relevanceScore: 94,
            sectionsAvailable: ['Complete Document', 'Section 2.3: Cylinder Limits', 'Section 4.1: Relief Valving'],
          },
          {
            name: 'P-102A_Schematics_v3.pdf',
            category: 'P&ID Blueprint',
            relevanceScore: 89,
            sectionsAvailable: ['Complete Document', 'Section 4.1: Flow Diagrams', 'Section 5.2: Electrical Calibrations'],
          }
        ]);
      } else if (text.includes('pressure') || text.includes('osha')) {
        setRestrictedDocsForModal([
          {
            name: 'OSHA_Steam_Regulations_2026.pdf',
            category: 'Compliance',
            relevanceScore: 91,
            sectionsAvailable: ['Complete Document', 'Section 2.1: Steam Ventilation', 'Section 3.4: Pressure Release SOPs'],
          },
          {
            name: 'Maintenance_Log_2026_07.xlsx',
            category: 'Energy Reports',
            relevanceScore: 85,
            sectionsAvailable: ['Complete Document', 'Section 1.2: General Specifications', 'Section 2.3: Cylinder Limits'],
          }
        ]);
      } else {
        setRestrictedDocsForModal(undefined);
      }
    } else {
      setRestrictedDocsForModal(undefined);
    }
    setIsRequestAccessOpen(true);
  };

  return (
    <PermissionGuard permission="chat">
      <div className="flex h-[calc(100vh-8rem)] rounded-xl border border-border bg-card/25 overflow-hidden shadow-sm animate-in fade-in duration-300">
        
        {/* Sidebar Conversation List */}
        <ChatSidebar
          conversations={conversations}
          activeId={activeId}
          onSelectConversation={handleSelectConversation}
          onNewChat={handleNewChat}
          onDeleteConversation={handleDeleteConversation}
        />

        {/* Main Split Screen Area */}
        <div className="flex-1 flex overflow-hidden">
          
          {/* Main chat window container */}
          <div className="flex-1 flex flex-col justify-between bg-background/45 h-full relative border-r border-border/40">
            {/* Top Context Bar */}
            <ConversationContextBar
              retrievalMode={retrievalMode}
              onSelectMode={setRetrievalMode}
              docCount={stagedFiles.length}
              options={processingOptions}
              onOpenManageContext={() => setIsManageContextOpen(true)}
              onOpenRequestAccess={() => handleTriggerRequestAccess()}
            />

            {/* Message Feeds Scroll Container */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {activeMessages.map((msg) => (
                <MessageBubble 
                  key={msg.id} 
                  message={msg} 
                  onTriggerRequestAccess={() => handleTriggerRequestAccess(msg.id)}
                  onExplainResponse={() => handleExplainResponse(msg.id)}
                />
              ))}

              {/* Typing Indicator */}
              {isTyping && <TypingIndicator />}

              {/* Dummy element for scroll anchors */}
              <div ref={scrollRef} />
            </div>

            {/* Persona Chat Starters Suggestions */}
            {activeMessages.length <= 1 && workspaceManifest && (
              <div className="px-4 pb-2 space-y-2">
                <span className="text-[9px] font-bold text-muted-foreground/60 uppercase tracking-wider block">
                  Suggested Queries for {persona?.role || 'User'}
                </span>
                <div className="flex flex-wrap gap-2">
                  {workspaceManifest.chatSuggestions.map((starter, sIdx) => (
                    <button
                      key={sIdx}
                      onClick={() => handleSendMessage(starter)}
                      className="rounded-full bg-secondary/60 hover:bg-secondary border border-border px-3 py-1.5 text-[10px] text-foreground font-semibold hover:border-primary/30 transition-all cursor-pointer text-left"
                    >
                      {starter}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Console Inputs */}
            <ChatInput onSendMessage={handleSendMessage} disabled={isTyping || isStreaming} />
          </div>

          {/* Reusable, Data-driven collapsible side explainability panel */}
          <TransparencyPanel
            isOpen={isTransparencyOpen}
            onClose={() => setIsTransparencyOpen(false)}
            explanation={selectedExplanation}
          />
        </div>

        {/* Modals Overlay */}
        <NeedMoreDocumentsModal
          isOpen={isManageContextOpen}
          onClose={() => setIsManageContextOpen(false)}
        />
        <RequestAccessModal
          isOpen={isRequestAccessOpen}
          onClose={() => setIsRequestAccessOpen(false)}
          matchingRestrictedDocs={restrictedDocsForModal}
        />
      </div>
    </PermissionGuard>
  );
}
