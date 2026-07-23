'use client';

import React, { useState } from 'react';
import { usePersonaStore } from './persona-context';
import { UserRole } from '@/lib/types';
import { Settings, ShieldCheck, User } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function DeveloperPreviewSwitcher() {
  const router = useRouter();
  const { profile, switchPersona } = usePersonaStore();
  const [isOpen, setIsOpen] = useState(false);

  // Hidden if not logged in (to prevent interference with the login page)
  if (!profile) return null;

  const roles: UserRole[] = [
    'Field Technician',
    'Maintenance Engineer',
    'Project Manager',
    'Regulatory & Compliance Manager',
    'Director / Executive',
  ];

  const handleSwitch = (role: UserRole) => {
    switchPersona(role);
    setIsOpen(false);
    router.push('/dashboard');
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 animate-in slide-in-from-bottom duration-250">
      {/* Floating Toggle Icon */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground hover:bg-primary/95 transition-all shadow-lg cursor-pointer border border-border/20"
        title="Developer Demo Mode"
      >
        <Settings className="h-5 w-5 animate-spin" style={{ animationDuration: '6s' }} />
      </button>

      {/* Switcher Selection drawer */}
      {isOpen && (
        <div className="absolute bottom-12 right-0 w-64 rounded-xl border border-border bg-card p-4 shadow-xl space-y-3 animate-in zoom-in-95 duration-150">
          <div className="border-b border-border pb-2">
            <span className="text-[10px] font-bold text-primary uppercase tracking-wider block flex items-center gap-1">
              <ShieldCheck className="h-3.5 w-3.5" />
              Developer Preview
            </span>
            <p className="text-[10px] text-muted-foreground mt-0.5 leading-normal">
              Hackathon Demo Switcher: Toggle employee personas in-memory to view role-specific dashboards.
            </p>
          </div>

          <div className="space-y-1.5">
            {roles.map((role) => (
              <button
                key={role}
                onClick={() => handleSwitch(role)}
                className="w-full text-left rounded-lg bg-secondary/30 hover:bg-secondary border border-border/40 hover:border-primary/30 px-3 py-2 text-xs font-semibold text-foreground transition-all cursor-pointer flex items-center gap-2"
              >
                <User className="h-3.5 w-3.5 text-muted-foreground" />
                {role}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
