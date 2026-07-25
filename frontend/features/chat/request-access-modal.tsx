'use client';

import React, { useState, useEffect } from 'react';
import { ShieldAlert, Lock, X, CheckCircle, Loader2, ChevronDown } from 'lucide-react';
import { usePersonaStore } from '@/features/persona/persona-context';
import { apiClient } from '@/lib/api-client';
import { showToast } from '@/lib/toast';

export interface RestrictedDoc {
  name: string;
  category: string;
  relevanceScore: number;
  sectionsAvailable: string[];
}

interface RequestAccessModalProps {
  isOpen: boolean;
  onClose: () => void;
  matchingRestrictedDocs?: RestrictedDoc[];
}

const DEFAULT_RESTRICTED_RESOURCES: RestrictedDoc[] = [];

export default function RequestAccessModal({
  isOpen,
  onClose,
  matchingRestrictedDocs = DEFAULT_RESTRICTED_RESOURCES,
}: RequestAccessModalProps) {
  const { submitAccessRequest } = usePersonaStore();

  const [selectedDocs, setSelectedDocs] = useState<Record<string, boolean>>({});
  const [docSections, setDocSections] = useState<Record<string, string>>({});
  const [reason, setReason] = useState('');
  const [priority, setPriority] = useState<'Normal' | 'High'>('Normal');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [requestId, setRequestId] = useState('');
  const maxChars = 300;

  // Reset state when modal is opened/closed
  useEffect(() => {
    if (isOpen) {
      // Pre-select the first document by default
      const initialSelections: Record<string, boolean> = {};
      const initialSections: Record<string, string> = {};
      
      matchingRestrictedDocs.forEach((doc, idx) => {
        initialSelections[doc.name] = idx === 0;
        initialSections[doc.name] = doc.sectionsAvailable[0] || 'Complete Document';
      });

      setSelectedDocs(initialSelections);
      setDocSections(initialSections);
      setReason('');
      setPriority('Normal');
      setIsSubmitting(false);
      setIsSubmitted(false);
      setRequestId('');
    }
  }, [isOpen, matchingRestrictedDocs]);

  if (!isOpen) return null;

  const handleToggleDoc = (name: string) => {
    setSelectedDocs((prev) => ({
      ...prev,
      [name]: !prev[name],
    }));
  };

  const handleSectionChange = (name: string, section: string) => {
    setDocSections((prev) => ({
      ...prev,
      [name]: section,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Check if at least one document is selected
    const activeSelected = Object.keys(selectedDocs).filter((k) => selectedDocs[k]);
    if (activeSelected.length === 0) {
      showToast('Please select at least one document to request access.', 'warning');
      return;
    }

    setIsSubmitting(true);

    try {
      for (const docName of activeSelected) {
        const targetSection = docSections[docName] || 'Complete Document';
        const docId = parseInt(docName, 10) || 1;
        await apiClient.post('/api/access/request', {
          document_id: docId,
          requested_sections: [targetSection],
          justification: reason
        });
      }
      setIsSubmitting(false);
      setIsSubmitted(true);
    } catch (error) {
      console.error('Access request failed:', error);
      setIsSubmitting(false);
      showToast('Failed to request access. Please try again.', 'error');
    }
  };

  const selectedCount = Object.values(selectedDocs).filter(Boolean).length;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg rounded-xl border border-border bg-card p-6 shadow-xl space-y-5 animate-in zoom-in-95 duration-200">
        
        {/* Success Confirmation State */}
        {isSubmitted ? (
          <div className="text-center py-6 space-y-5 animate-in fade-in duration-200">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-500">
              <CheckCircle className="h-8 w-8" />
            </div>

            <div className="space-y-2">
              <h3 className="text-lg font-bold text-foreground">✓ Request Submitted Successfully</h3>
              <p className="text-xs text-muted-foreground">
                Your access request for {selectedCount} document{selectedCount > 1 ? 's' : ''} has been recorded in the Compliance queue.
              </p>
            </div>

            {/* Reference Card */}
            <div className="rounded-lg border border-border bg-secondary/25 p-4 max-w-xs mx-auto space-y-1">
              <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                Status
              </span>
              <div className="font-mono text-sm font-bold text-primary tracking-wide">
                Pending Approval
              </div>
            </div>

            <div className="pt-2">
              <button
                type="button"
                onClick={onClose}
                className="w-full sm:w-auto inline-flex justify-center rounded-lg bg-primary hover:bg-primary/95 text-primary-foreground px-6 py-2 text-xs font-semibold transition-all shadow-sm cursor-pointer"
              >
                Close Window
              </button>
            </div>
          </div>
        ) : (
          /* Input Form State */
          <form onSubmit={handleSubmit} className="space-y-4">
            
            {/* Header */}
            <div className="flex justify-between items-start">
              <div className="flex items-start gap-2.5">
                <div className="rounded-lg bg-amber-500/10 p-2 text-amber-500 shrink-0 mt-0.5">
                  <Lock className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-md font-bold text-foreground">Request Document Access</h3>
                  <p className="text-[11px] text-muted-foreground mt-0.5 leading-normal">
                    Select the matching documents and specify which sections you need access to.
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={onClose}
                disabled={isSubmitting}
                className="rounded p-1 hover:bg-secondary text-muted-foreground hover:text-foreground cursor-pointer disabled:opacity-50"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Requested Resources Section */}
            <div className="space-y-2">
              <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
                Matching Restricted Documents
              </span>
              <div className="max-h-48 overflow-y-auto space-y-2 pr-1">
                {matchingRestrictedDocs.map((doc) => {
                  const isChecked = !!selectedDocs[doc.name];
                  return (
                    <div
                      key={doc.name}
                      className={`flex flex-col gap-2 rounded-lg border p-3 text-xs transition-all ${
                        isChecked 
                          ? 'border-primary/40 bg-primary/5 text-foreground' 
                          : 'border-border bg-secondary/10 text-muted-foreground'
                      }`}
                    >
                      <div className="flex items-start gap-2.5">
                        <input
                          type="checkbox"
                          id={`check-${doc.name}`}
                          checked={isChecked}
                          onChange={() => handleToggleDoc(doc.name)}
                          className="mt-0.5 h-3.5 w-3.5 rounded border-border text-primary outline-none focus:ring-0 focus:ring-offset-0 cursor-pointer"
                        />
                        <div className="flex-1 min-w-0">
                          <label htmlFor={`check-${doc.name}`} className="font-bold block truncate text-foreground cursor-pointer">
                            {doc.name}
                          </label>
                          <div className="flex items-center gap-2 text-[10px] text-muted-foreground/80 font-semibold mt-0.5">
                            <span>Category: {doc.category}</span>
                            <span>•</span>
                            <span className="text-amber-500 font-bold">Match score: {doc.relevanceScore}%</span>
                          </div>
                        </div>
                      </div>

                      {/* Dropdown for Document section */}
                      {isChecked && (
                        <div className="mt-1 flex items-center gap-2 pl-6 animate-in slide-in-from-top-1 duration-150">
                          <span className="text-[10px] font-bold text-muted-foreground/80 shrink-0">Section:</span>
                          <div className="relative flex-1 max-w-[240px]">
                            <select
                              value={docSections[doc.name] || 'Complete Document'}
                              onChange={(e) => handleSectionChange(doc.name, e.target.value)}
                              className="w-full appearance-none rounded-md border border-border/80 bg-background pl-2.5 pr-8 py-1 text-[10px] font-semibold text-foreground outline-none focus:border-primary cursor-pointer"
                            >
                              {doc.sectionsAvailable.map((sect) => (
                                <option key={sect} value={sect}>{sect}</option>
                              ))}
                            </select>
                            <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground/60 pointer-events-none" />
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Reason Textarea */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                  Reason for Override Clearance Request
                </label>
                <span className="text-[9px] text-muted-foreground/60 font-semibold">
                  {reason.length} / {maxChars}
                </span>
              </div>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value.substring(0, maxChars))}
                placeholder="Ex. Conducting safety inspection validation on Boiler 092 Cylinder B-3."
                required
                disabled={isSubmitting}
                rows={3}
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-xs text-foreground outline-none transition-all focus:border-primary placeholder:text-muted-foreground/60 resize-none disabled:opacity-60"
              />
            </div>

            {/* Priority Selector */}
            <div className="space-y-1.5">
              <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
                Priority Level
              </span>
              <div className="flex gap-2">
                {(['Normal', 'High'] as const).map((p) => (
                  <button
                    key={p}
                    type="button"
                    disabled={isSubmitting}
                    onClick={() => setPriority(p)}
                    className={`flex-1 rounded-lg border py-2 px-3 text-xs font-semibold text-center cursor-pointer transition-all disabled:opacity-60 ${
                      priority === p
                        ? 'border-primary bg-primary text-primary-foreground shadow-sm'
                        : 'border-border bg-transparent hover:bg-secondary text-muted-foreground'
                    }`}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>

            {/* Information Notice */}
            <div className="rounded-lg border border-primary/20 bg-primary/5 p-3 text-[10px] text-muted-foreground leading-normal">
              Your request will be submitted to compliance audits queue. A manager (e.g. Neha Iyer) must verify and approve it before the retrieval keys are unlocked.
            </div>

            {/* Footer Actions */}
            <div className="flex justify-end gap-2 pt-2 border-t border-border">
              <button
                type="button"
                onClick={onClose}
                disabled={isSubmitting}
                className="rounded-lg border border-border bg-transparent hover:bg-secondary px-4 py-2 text-xs font-semibold transition-all cursor-pointer text-foreground disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting || !reason.trim() || selectedCount === 0}
                className="rounded-lg bg-primary hover:bg-primary/95 text-primary-foreground px-5 py-2 text-xs font-semibold transition-all shadow-sm cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  `Submit Request (${selectedCount})`
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
