'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import UploadStepper from '@/features/upload/upload-stepper';
import UploadZone from '@/features/upload/upload-zone';
import UploadedFilesList from '@/features/upload/uploaded-files-list';
import CategorySelector from '@/features/upload/category-selector';
import DescriptionForm from '@/features/upload/description-form';
import ReviewUpload from '@/features/upload/review-upload';
import { useAppStore } from '@/store/app-context';
import { AlertTriangle, ArrowLeft, ArrowRight, Loader2, Play } from 'lucide-react';
import PermissionGuard from '@/features/persona/permission-guard';
import { uploadService } from '@/services/upload-service';

export default function UploadPage() {
  const router = useRouter();
  
  // Use global app store
  const {
    stagedFiles,
    setStagedFiles,
    fileBinaries,
    setFileBinaries,
    category,
    setCategory,
    description,
    setDescription,
    resetBatch,
  } = useAppStore();

  const [currentStep, setCurrentStep] = useState(1);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFilesAdded = (newFiles: File[]) => {
    const metaList = newFiles.map((f) => ({
      name: f.name,
      size: f.size,
      category: category,
    }));
    setStagedFiles((prev) => [...prev, ...metaList]);
    setFileBinaries((prev) => [...prev, ...newFiles]);
  };

  const handleRemoveFile = (index: number) => {
    setStagedFiles((prev) => prev.filter((_, i) => i !== index));
    setFileBinaries((prev) => prev.filter((_, i) => i !== index));
  };

  const handleNextStep = () => {
    if (currentStep < 3) {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handlePrevStep = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  const handleFinalizeUpload = async () => {
    if (fileBinaries.length === 0 || isUploading) return;

    setUploadError(null);
    setIsUploading(true);

    try {
      const success = await uploadService.uploadDocuments(fileBinaries, category, description);
      if (!success) {
        setUploadError('One or more documents failed to upload or process. Review the processing page for backend status.');
        return;
      }

      resetBatch();
      router.push('/processing');
    } catch (error) {
      console.error('Upload failed:', error);
      setUploadError('Upload failed. Verify backend availability and your authenticated session.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <PermissionGuard permission="upload">
      <div className="space-y-6 max-w-4xl mx-auto animate-in fade-in duration-300">
      {/* Title Header */}
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Document Ingestion</h1>
        <p className="text-sm text-muted-foreground">
          Queue and catalogue documents for Layout-aware OCR parsing and Graph ingestion.
        </p>
      </div>

      {/* Stepper progress indicator */}
      <UploadStepper currentStep={currentStep} />

      {/* STEP 1: INGEST FILES */}
      {currentStep === 1 && (
        <div className="space-y-6">
          <UploadZone onFilesAdded={handleFilesAdded} />
          <UploadedFilesList files={stagedFiles} onRemoveFile={handleRemoveFile} />
          
          {/* Step 1 Actions */}
          {stagedFiles.length > 0 && (
            <div className="flex justify-end pt-4 animate-in fade-in duration-200">
              <button
                type="button"
                onClick={handleNextStep}
                className="inline-flex items-center gap-2 rounded-lg bg-primary hover:bg-primary/95 text-primary-foreground px-5 py-2.5 text-sm font-semibold shadow-sm transition-all cursor-pointer"
              >
                Continue to Metadata
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      )}

      {/* STEP 2: ADD METADATA */}
      {currentStep === 2 && (
        <div className="space-y-6 rounded-xl border border-border bg-card p-6 shadow-sm">
          <CategorySelector
            selectedCategory={category}
            onSelectCategory={setCategory}
          />
          
          <hr className="border-border/60" />

          <DescriptionForm
            description={description}
            onChangeDescription={setDescription}
          />

          {/* Step 2 Actions */}
          <div className="flex justify-between pt-4 border-t border-border">
            <button
              type="button"
              onClick={handlePrevStep}
              className="inline-flex items-center gap-2 rounded-lg border border-border bg-transparent hover:bg-secondary px-4 py-2.5 text-sm font-semibold transition-all cursor-pointer text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Ingestion
            </button>
            <button
              type="button"
              onClick={handleNextStep}
              className="inline-flex items-center gap-2 rounded-lg bg-primary hover:bg-primary/95 text-primary-foreground px-5 py-2.5 text-sm font-semibold shadow-sm transition-all cursor-pointer"
            >
              Continue to Review
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: REVIEW DETAILS */}
      {currentStep === 3 && (
        <div className="space-y-6">
          <ReviewUpload
            files={stagedFiles}
            category={category}
            description={description}
            onEditFiles={() => setCurrentStep(1)}
            onEditMetadata={() => setCurrentStep(2)}
          />

          {uploadError && (
            <div className="flex gap-2 rounded-lg border border-destructive/20 bg-destructive/10 p-3 text-xs text-destructive">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <span className="font-semibold">{uploadError}</span>
            </div>
          )}

          {/* Step 3 Actions */}
          <div className="flex justify-between pt-4">
            <button
              type="button"
              onClick={handlePrevStep}
              className="inline-flex items-center gap-2 rounded-lg border border-border bg-transparent hover:bg-secondary px-4 py-2.5 text-sm font-semibold transition-all cursor-pointer text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Metadata
            </button>
            <button
              type="button"
              onClick={handleFinalizeUpload}
              disabled={isUploading || fileBinaries.length === 0}
              className="inline-flex items-center gap-2 rounded-lg bg-primary hover:bg-primary/95 text-primary-foreground px-5 py-2.5 text-sm font-semibold shadow-sm transition-all cursor-pointer disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isUploading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin shrink-0" />
                  Uploading & Processing...
                </>
              ) : (
                <>
                  Upload to AI Processing
                  <Play className="h-4 w-4 fill-current shrink-0" />
                </>
              )}
            </button>
          </div>
        </div>
      )}
      </div>
    </PermissionGuard>
  );
}
