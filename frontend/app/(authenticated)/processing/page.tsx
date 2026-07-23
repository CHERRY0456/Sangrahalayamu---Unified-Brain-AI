'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAppStore, StagedFileMeta } from '@/store/app-context';
import DocumentsOverview from '@/features/processing/documents-overview';
import RetrievalModeSelector from '@/features/processing/retrieval-mode-selector';
import ProcessingOptions from '@/features/processing/processing-options';
import ProcessingSummary from '@/features/processing/processing-summary';
import { Loader2 } from 'lucide-react';
import PermissionGuard from '@/features/persona/permission-guard';



export default function ProcessingPage() {
  const router = useRouter();
  
  // Bind global store
  const {
    stagedFiles,
    setStagedFiles,
    category,
    retrievalMode,
    setRetrievalMode,
    processingOptions,
    setProcessingOptions,
  } = useAppStore();



  const handleRemoveFile = (index: number) => {
    setStagedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleStartProcessing = () => {
    router.push('/chat');
  };

  const getUniqueCategories = () => {
    const cats = stagedFiles.map((f) => f.category);
    return Array.from(new Set(cats));
  };



  return (
    <PermissionGuard permission="processing">
      <div className="space-y-6 max-w-7xl mx-auto relative animate-in fade-in duration-300">
      {/* Title Header */}
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">AI Processing Studio</h1>
        <p className="text-sm text-muted-foreground">
          Configure model parameters, select RAG context constraints, and index document batches.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Configuration panels */}
        <div className="lg:col-span-2 space-y-6">
          <DocumentsOverview
            files={stagedFiles}
            onRemoveFile={handleRemoveFile}
            onAddPlaceholder={() => router.push('/upload')}
          />
          <RetrievalModeSelector
            selectedMode={retrievalMode}
            onSelectMode={setRetrievalMode}
          />
          <ProcessingOptions
            options={processingOptions}
            onChangeOptions={setProcessingOptions}
          />
        </div>

        {/* Sidebar Summary Review card */}
        <div>
          <ProcessingSummary
            retrievalMode={retrievalMode}
            docCount={stagedFiles.length}
            categories={getUniqueCategories()}
            options={processingOptions}
            onStartProcessing={handleStartProcessing}
            isProcessing={false}
          />
        </div>
      </div>


      </div>
    </PermissionGuard>
  );
}
