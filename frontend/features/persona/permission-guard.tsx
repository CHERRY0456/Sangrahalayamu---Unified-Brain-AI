'use client';

import React, { useState } from 'react';
import { usePersonaStore } from './persona-context';
import { ShieldAlert, ArrowLeft, Key } from 'lucide-react';
import { useRouter } from 'next/navigation';
import RequestAccessModal from '@/features/chat/request-access-modal';
import { hasPermission } from '@/lib/permissions';

interface PermissionGuardProps {
  permission: string;
  children: React.ReactNode;
}

export default function PermissionGuard({
  permission,
  children,
}: PermissionGuardProps) {
  const router = useRouter();
  const { permissions, profile, persona } = usePersonaStore();
  const [isRequestModalOpen, setIsRequestModalOpen] = useState(false);

  // Allow unrestricted access if profile has not loaded yet (prevents layout flashing on load)
  if (!profile) {
    return <>{children}</>;
  }

  const isAuthorized = hasPermission(permissions, permission);

  if (!isAuthorized) {
    return (
      <div className="flex flex-col items-center justify-center text-center p-8 min-h-[70vh] space-y-6 max-w-lg mx-auto animate-in zoom-in-95 duration-250">
        {/* Shield Icon */}
        <div className="rounded-full bg-destructive/10 border border-destructive/20 p-5 text-destructive shadow-sm animate-bounce">
          <ShieldAlert className="h-10 w-10" />
        </div>

        {/* Details Title */}
        <div className="space-y-2">
          <h2 className="text-xl font-bold text-foreground">Access Restricted</h2>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Your enterprise account does not have authorization to view the <b>{permission.toUpperCase()}</b> module. Security policies require strict clearance parameters for this resource.
          </p>
        </div>

        {/* User Identity Info */}
        <div className="w-full rounded-lg border border-border bg-card p-4 text-xs text-left space-y-2.5">
          <div className="flex justify-between border-b border-border/40 pb-2">
            <span className="text-muted-foreground">Current Employee:</span>
            <span className="font-bold text-foreground">{profile.name}</span>
          </div>
          <div className="flex justify-between border-b border-border/40 pb-2">
            <span className="text-muted-foreground">Assigned Role:</span>
            <span className="font-bold text-foreground">{persona?.role}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Required Policy Permission:</span>
            <span className="font-mono bg-secondary border border-border px-1.5 py-0.5 rounded text-[10px] font-bold text-foreground uppercase tracking-wide">
              {permission}
            </span>
          </div>
        </div>

        {/* Action Button Controls */}
        <div className="flex flex-col sm:flex-row gap-3 w-full pt-2">
          <button
            type="button"
            onClick={() => router.push('/dashboard')}
            className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg border border-border hover:bg-secondary text-xs font-bold text-foreground py-2.5 transition-all cursor-pointer"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </button>
          
          <button
            type="button"
            onClick={() => setIsRequestModalOpen(true)}
            className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg bg-primary hover:bg-primary/95 text-xs font-bold text-primary-foreground py-2.5 transition-all cursor-pointer shadow-sm"
          >
            <Key className="h-4 w-4 shrink-0" />
            Request Clearance
          </button>
        </div>

        {/* Request Access Workflow Modal */}
        <RequestAccessModal
          isOpen={isRequestModalOpen}
          onClose={() => setIsRequestModalOpen(false)}
        />
      </div>
    );
  }

  return <>{children}</>;
}
