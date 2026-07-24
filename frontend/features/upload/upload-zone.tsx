'use client';

import React, { useRef, useState } from 'react';
import { UploadCloud, FileWarning } from 'lucide-react';

interface UploadZoneProps {
  onFilesAdded: (files: File[]) => void;
  disabled?: boolean;
}

export default function UploadZone({ onFilesAdded, disabled }: UploadZoneProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (disabled) return;

    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const validateAndAddFiles = (fileList: FileList | null) => {
    if (!fileList) return;
    setValidationError(null);

    const allowedExtensions = [
      '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
      '.csv', '.tsv', '.txt', '.md', '.markdown', '.rtf', '.html',
      '.htm', '.xml', '.json', '.png', '.jpg', '.jpeg', '.webp',
      '.tiff', '.tif', '.eml', '.msg', '.log', '.err', '.out',
      '.py', '.js', '.ts', '.go', '.c', '.cpp', '.h', '.rs',
      '.java', '.sql', '.sh', '.cfg', '.conf', '.ini', '.svg',
      '.dwg', '.dxf'
    ];
    const maxSizeBytes = 100 * 1024 * 1024; // 100MB
    const validFiles: File[] = [];

    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      const extension = '.' + file.name.split('.').pop()?.toLowerCase();

      // Check type
      if (!allowedExtensions.includes(extension)) {
        setValidationError(`Format "${extension}" is not supported by the parser registry.`);
        return;
      }

      // Check size
      if (file.size > maxSizeBytes) {
        setValidationError(`File "${file.name}" exceeds the 100MB size limit.`);
        return;
      }

      validFiles.push(file);
    }

    if (validFiles.length > 0) {
      onFilesAdded(validFiles);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (disabled) return;

    validateAndAddFiles(e.dataTransfer.files);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    validateAndAddFiles(e.target.files);
  };

  const triggerFileInput = () => {
    if (disabled) return;
    fileInputRef.current?.click();
  };

  return (
    <div className="space-y-4">
      {/* Drop Zone Box */}
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={triggerFileInput}
        className={`relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-10 text-center cursor-pointer transition-all ${
          disabled
            ? 'border-border bg-secondary/10 cursor-not-allowed opacity-60'
            : isDragActive
            ? 'border-primary bg-primary/5 shadow-inner scale-[0.99]'
            : 'border-border hover:border-primary/55 bg-card/50 hover:bg-secondary/20'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          disabled={disabled}
          onChange={handleFileChange}
          className="hidden"
          accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.csv,.tsv,.txt,.md,.markdown,.rtf,.html,.htm,.xml,.json,.png,.jpg,.jpeg,.webp,.tiff,.tif,.eml,.msg,.log,.err,.out,.py,.js,.ts,.go,.c,.cpp,.h,.rs,.java,.sql,.sh,.cfg,.conf,.ini,.svg,.dwg,.dxf"
        />

        <div className="rounded-full bg-primary/10 p-4 text-primary mb-4 shadow-sm">
          <UploadCloud className="h-8 w-8 animate-bounce" />
        </div>

        <h3 className="text-sm font-bold text-foreground">
          Drag and drop files here, or <span className="text-primary hover:underline">browse</span>
        </h3>
        <p className="mt-1 text-[11px] text-muted-foreground leading-normal max-w-xs">
          Supports multi-file selection of documents, spreadsheets, logs, images, source files, and supported engineering exports.
        </p>
      </div>

      {/* Validation Error Message */}
      {validationError && (
        <div className="flex gap-2 rounded-lg border border-destructive/20 bg-destructive/10 p-3 text-xs text-destructive animate-in fade-in duration-200">
          <FileWarning className="h-4.5 w-4.5 shrink-0" />
          <span className="font-semibold">{validationError}</span>
        </div>
      )}
    </div>
  );
}
