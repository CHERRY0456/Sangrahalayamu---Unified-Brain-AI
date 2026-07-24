import React from 'react';
import { FileText, Plus, Trash2 } from 'lucide-react';
import { StagedFileMeta } from '@/store/app-context';

interface DocumentsOverviewProps {
  files: StagedFileMeta[];
  onRemoveFile: (index: number) => void;
  onAddPlaceholder: () => void;
  readOnly?: boolean;
}

export default function DocumentsOverview({
  files,
  onRemoveFile,
  onAddPlaceholder,
  readOnly = false,
}: DocumentsOverviewProps) {
  
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const totalSize = files.reduce((acc, f) => acc + f.size, 0);

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-md font-semibold text-foreground">Document Processing Status</h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            Total files: <b>{files.length}</b> • Total batch size: <b>{formatBytes(totalSize)}</b>
          </p>
        </div>
        <button
          type="button"
          onClick={onAddPlaceholder}
          className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-secondary/50 hover:bg-secondary px-3 py-1.5 text-xs font-semibold transition-all cursor-pointer text-foreground"
        >
          <Plus className="h-4 w-4" />
          Add Document
        </button>
      </div>

      <div className="overflow-x-auto border border-border/60 rounded-lg bg-secondary/15">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-border/80 text-[10px] font-bold text-muted-foreground uppercase tracking-wider bg-secondary/40">
              <th className="p-3">File Name</th>
              <th className="p-3">Category</th>
              <th className="p-3">Size</th>
              {!readOnly && <th className="p-3 text-right">Action</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40 text-xs">
            {files.length === 0 ? (
              <tr>
                <td colSpan={readOnly ? 3 : 4} className="p-8 text-center text-muted-foreground italic">
                  No documents uploaded. Upload enterprise documents to start processing.
                </td>
              </tr>
            ) : (
              files.map((file, idx) => (
                <tr key={idx} className="hover:bg-secondary/25 transition-colors">
                  <td className="p-3 flex items-center gap-2">
                    <FileText className="h-4 w-4 text-primary shrink-0" />
                    <span className="font-semibold text-foreground truncate max-w-[200px] sm:max-w-xs">
                      {file.name}
                    </span>
                  </td>
                  <td className="p-3 text-muted-foreground">{file.category}</td>
                  <td className="p-3 text-muted-foreground">{formatBytes(file.size)}</td>
                  {!readOnly && (
                    <td className="p-3 text-right">
                      <button
                        type="button"
                        onClick={() => onRemoveFile(idx)}
                        className="inline-flex items-center justify-center rounded p-1 hover:bg-destructive/10 text-muted-foreground hover:text-destructive cursor-pointer"
                        title="Remove File"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
