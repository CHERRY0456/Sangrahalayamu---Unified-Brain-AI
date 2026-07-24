'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { usePersonaStore } from '@/features/persona/persona-context';

interface AuthenticatedSessionGateProps {
  children: React.ReactNode;
}

export default function AuthenticatedSessionGate({ children }: AuthenticatedSessionGateProps) {
  const router = useRouter();
  const { profile, persona, workspaceManifest, isRestoringSession } = usePersonaStore();
  const hasWorkspace = Boolean(profile && persona && workspaceManifest);

  useEffect(() => {
    if (!isRestoringSession && !hasWorkspace) {
      router.replace('/login');
    }
  }, [hasWorkspace, isRestoringSession, router]);

  if (isRestoringSession || !hasWorkspace) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-foreground">
        <div className="flex flex-col items-center gap-4 rounded-2xl border border-border bg-card p-8 text-center shadow-sm">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <div className="space-y-1">
            <p className="text-sm font-bold">
              {isRestoringSession ? 'Restoring workspace session...' : 'Redirecting to login...'}
            </p>
            <p className="text-xs text-muted-foreground">
              Validating your backend session before loading enterprise modules.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
