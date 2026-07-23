import React from 'react';
import { FileText, Tag, AlignLeft, CheckCircle2 } from 'lucide-react';
import { StagedFileMeta } from '@/store/app-context';

interface ReviewUploadProps {
  files: StagedFileMeta[];
  category: string;
  description: string;
  onEditFiles: () => void;
  onEditMetadata: () => void;
}

export default function ReviewUpload({
  files,
  category,
  description,
  onEditFiles,
  onEditMetadata,
}: ReviewUploadProps) {
  
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const totalSize = files.reduce((acc, file) => acc + file.size, 0);

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">
          Review Ingestion Details
        </h2>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Files Summary Box */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide flex items-center gap-1.5">
                <FileText className="h-4 w-4 text-primary" />
                Staged Files ({files.length})
              </span>
              <button
                type="button"
                onClick={onEditFiles}
                className="text-xs font-semibold text-primary hover:underline cursor-pointer"
              >
                Edit
              </button>
            </div>
            <div className="rounded-lg border border-border bg-secondary/20 p-4 max-h-48 overflow-y-auto space-y-2">
              {files.map((file, idx) => (
                <div key={idx} className="flex justify-between items-center text-xs">
                  <span className="font-medium text-foreground truncate max-w-[200px]">
                    {file.name}
                  </span>
                  <span className="text-muted-foreground">{formatBytes(file.size)}</span>
                </div>
              ))}
              <div className="border-t border-border/80 pt-2 flex justify-between items-center text-xs font-bold text-foreground">
                <span>Total Payload Size</span>
                <span>{formatBytes(totalSize)}</span>
              </div>
            </div>
          </div>

          {/* Metadata Summary Box */}
          <div className="space-y-4">
            {/* Category */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide flex items-center gap-1.5">
                  <Tag className="h-4 w-4 text-primary" />
                  Category Classification
                </span>
                <button
                  type="button"
                  onClick={onEditMetadata}
                  className="text-xs font-semibold text-primary hover:underline cursor-pointer"
                >
                  Edit
                </button>
              </div>
              <div className="rounded-lg border border-border bg-secondary/20 px-4 py-2.5 text-xs font-bold text-foreground">
                {category}
              </div>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide flex items-center gap-1.5">
                <AlignLeft className="h-4 w-4 text-primary" />
                Description
              </span>
              <div className="rounded-lg border border-border bg-secondary/20 p-3 text-xs text-foreground min-h-[60px] leading-relaxed max-h-24 overflow-y-auto">
                {description ? description : <span className="italic text-muted-foreground">No description provided.</span>}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Info Badge */}
      <div className="flex items-center gap-2 rounded-lg border border-primary/20 bg-primary/5 p-4 text-xs leading-normal text-muted-foreground">
        <CheckCircle2 className="h-5 w-5 text-primary shrink-0 animate-pulse" />
        <div>
          <h4 className="font-bold text-foreground">Ready for AI Ingestion Pipeline</h4>
          <p className="mt-0.5">Proceeding will initiate layout-aware parsing (OCR), entity extraction, and knowledge graph mapping in the AI Processing Studio.</p>
        </div>
      </div>
    </div>
  );
}
