'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import PermissionGuard from '@/features/persona/permission-guard';
import DocumentsOverview from '@/features/processing/documents-overview';
import ProcessingOptions from '@/features/processing/processing-options';
import ProcessingSummary from '@/features/processing/processing-summary';
import RetrievalModeSelector from '@/features/processing/retrieval-mode-selector';
import { useAppStore, StagedFileMeta } from '@/store/app-context';
import { uploadService, UploadedDocument } from '@/services/upload-service';
import { Loader2, RefreshCw } from 'lucide-react';

const toFileMeta = (document: UploadedDocument): StagedFileMeta => ({
  name: `${document.name} (${document.status})`,
  size: document.file_size,
  category: document.classification || 'Uploaded Document',
});

export default function ProcessingPage() {
  const router = useRouter();
  const {
    retrievalMode,
    setRetrievalMode,
    processingOptions,
    setProcessingOptions,
  } = useAppStore();

  const [documents, setDocuments] = useState<UploadedDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDocuments = async () => {
    setIsLoading(true);
    setError(null);
    try {
      setDocuments(await uploadService.listDocuments());
    } catch (loadError: any) {
      setError(loadError.message || 'Unable to load backend document status.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const fileRows = documents.map(toFileMeta);
  const categories = Array.from(new Set(fileRows.map((file) => file.category)));
  const processedCount = documents.filter((document) => document.status === 'PROCESSED').length;
  const failedCount = documents.filter((document) => document.status === 'FAILED').length;

  return (
    <PermissionGuard permission="processing">
      <div className="space-y-6 max-w-7xl mx-auto relative animate-in fade-in duration-300">
        <div className="flex flex-col gap-1">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-foreground">AI Processing Studio</h1>
              <p className="text-sm text-muted-foreground">
                Live ingestion status from backend document records.
              </p>
            </div>
            <button
              type="button"
              onClick={loadDocuments}
              disabled={isLoading}
              className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-xs font-bold text-foreground hover:bg-secondary disabled:opacity-60"
            >
              {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
              Refresh
            </button>
          </div>
        </div>

        {error && (
          <div className="rounded-lg border border-destructive/20 bg-destructive/10 p-4 text-xs text-destructive font-semibold">
            {error}
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            {isLoading ? (
              <div className="rounded-xl border border-border bg-card p-8 text-center text-xs text-muted-foreground">
                <Loader2 className="mx-auto mb-3 h-6 w-6 animate-spin text-primary" />
                Loading backend document status...
              </div>
            ) : (
              <DocumentsOverview
                files={fileRows}
                onRemoveFile={() => undefined}
                onAddPlaceholder={() => router.push('/upload')}
                readOnly
              />
            )}
            <RetrievalModeSelector selectedMode={retrievalMode} onSelectMode={setRetrievalMode} />
            <ProcessingOptions options={processingOptions} onChangeOptions={setProcessingOptions} />
          </div>

          <div className="space-y-4">
            <div className="rounded-xl border border-border bg-card p-4 text-xs text-muted-foreground space-y-2">
              <div className="flex justify-between">
                <span>Total documents</span>
                <b className="text-foreground">{documents.length}</b>
              </div>
              <div className="flex justify-between">
                <span>Processed</span>
                <b className="text-emerald-500">{processedCount}</b>
              </div>
              <div className="flex justify-between">
                <span>Failed</span>
                <b className="text-destructive">{failedCount}</b>
              </div>
            </div>
            <ProcessingSummary
              retrievalMode={retrievalMode}
              docCount={processedCount}
              categories={categories}
              options={processingOptions}
              onStartProcessing={() => router.push('/chat')}
              isProcessing={false}
            />
          </div>
        </div>
      </div>
    </PermissionGuard>
  );
}
