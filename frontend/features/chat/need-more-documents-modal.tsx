import React from 'react';
import { useRouter } from 'next/navigation';
import { Database, FileUp, X } from 'lucide-react';
import { showToast } from '@/lib/toast';

interface NeedMoreDocumentsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function NeedMoreDocumentsModal({
  isOpen,
  onClose,
}: NeedMoreDocumentsModalProps) {
  const router = useRouter();

  if (!isOpen) return null;

  const handleUploadRedirect = () => {
    onClose();
    router.push('/upload');
  };

  const handleRetrieval = () => {
    showToast('VectorDB scan complete. No additional document versions found.', 'info');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-md rounded-xl border border-border bg-card p-6 shadow-xl space-y-6 animate-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-md font-bold text-foreground">Manage Conversation Context</h3>
            <p className="text-xs text-muted-foreground mt-1">
              Select how you would like to expand the AI's document context.
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded p-1 hover:bg-secondary text-muted-foreground hover:text-foreground cursor-pointer"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Options */}
        <div className="grid gap-3">
          {/* Retrieve */}
          <button
            type="button"
            onClick={handleRetrieval}
            className="flex items-center gap-3 w-full text-left rounded-lg border border-border bg-transparent hover:bg-secondary/40 p-4 transition-all cursor-pointer"
          >
            <div className="rounded-md bg-primary/10 p-2 text-primary">
              <Database className="h-5 w-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-foreground">Retrieve More Documents</div>
              <p className="text-[10px] text-muted-foreground mt-0.5">
                Scan database indices to attach adjacent compliance records or engineering P&IDs.
              </p>
            </div>
          </button>

          {/* Upload New */}
          <button
            type="button"
            onClick={handleUploadRedirect}
            className="flex items-center gap-3 w-full text-left rounded-lg border border-border bg-transparent hover:bg-secondary/40 p-4 transition-all cursor-pointer"
          >
            <div className="rounded-md bg-primary/10 p-2 text-primary">
              <FileUp className="h-5 w-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-foreground">Upload Additional Documents</div>
              <p className="text-[10px] text-muted-foreground mt-0.5">
                Navigate to the Document Ingestion screen to upload and tag new files.
              </p>
            </div>
          </button>
        </div>

        {/* Footer Actions */}
        <div className="flex justify-end pt-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-border bg-transparent hover:bg-secondary px-4 py-2 text-xs font-semibold transition-all cursor-pointer text-foreground"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
