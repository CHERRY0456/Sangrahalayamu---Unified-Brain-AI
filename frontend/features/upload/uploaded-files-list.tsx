import React from 'react';
import { FileText, Trash2, Eye, FileSpreadsheet, FileImage, FileAudio, FileCode } from 'lucide-react';
import { StagedFileMeta } from '@/store/app-context';
import { showToast } from '@/lib/toast';

interface UploadedFilesListProps {
  files: StagedFileMeta[];
  onRemoveFile: (index: number) => void;
}

export default function UploadedFilesList({ files, onRemoveFile }: UploadedFilesListProps) {
  
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    if (ext === 'xlsx' || ext === 'csv') return FileSpreadsheet;
    if (['png', 'jpg', 'jpeg', 'tiff', 'bmp'].includes(ext || '')) return FileImage;
    if (['mp3', 'wav', 'm4a', 'flac'].includes(ext || '')) return FileAudio;
    if (['dwg', 'dxf', 'svg'].includes(ext || '')) return FileCode;
    return FileText;
  };

  if (files.length === 0) return null;

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4">
        Staged Ingestion Queue ({files.length} {files.length === 1 ? 'file' : 'files'})
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-border/80 text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
              <th className="pb-2">File Name</th>
              <th className="pb-2">Size</th>
              <th className="pb-2">Status</th>
              <th className="pb-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40 text-xs">
            {files.map((file, idx) => {
              const Icon = getFileIcon(file.name);
              return (
                <tr key={idx} className="hover:bg-secondary/20 transition-colors">
                  <td className="py-3 flex items-center gap-2">
                    <Icon className="h-4.5 w-4.5 text-primary shrink-0" />
                    <span className="font-semibold text-foreground truncate max-w-[200px] sm:max-w-xs">
                      {file.name}
                    </span>
                  </td>
                  <td className="py-3 text-muted-foreground">{formatBytes(file.size)}</td>
                  <td className="py-3">
                    <span className="inline-block rounded-full border border-primary/20 bg-primary/10 px-2 py-0.5 text-[9px] font-bold uppercase text-primary">
                      Ready
                    </span>
                  </td>
                  <td className="py-3 text-right space-x-1">
                    {/* Preview Placeholder */}
                    <button
                      type="button"
                      onClick={() => showToast(`Document preview for "${file.name}" is not available yet.`, 'info')}
                      className="inline-flex items-center justify-center rounded p-1 hover:bg-secondary text-muted-foreground hover:text-foreground cursor-pointer"
                      title="Preview Document"
                    >
                      <Eye className="h-4.5 w-4.5" />
                    </button>
                    {/* Remove Trigger */}
                    <button
                      type="button"
                      onClick={() => onRemoveFile(idx)}
                      className="inline-flex items-center justify-center rounded p-1 hover:bg-destructive/10 text-muted-foreground hover:text-destructive cursor-pointer"
                      title="Remove File"
                    >
                      <Trash2 className="h-4.5 w-4.5" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
