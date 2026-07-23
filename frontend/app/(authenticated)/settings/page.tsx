'use client';

import React from 'react';
import { useAppStore, ThemePalette, AppearanceMode } from '@/store/app-context';

export default function SettingsPage() {
  const { theme, setTheme, mode, setMode } = useAppStore();

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Settings</h1>
        <p className="text-sm text-muted-foreground">
          Configure platform appearance, theme variations, and user preference details.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Appearance Control Card */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-foreground mb-4">Design Customizer</h2>
          
          <div className="space-y-6">
            {/* Theme Select */}
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Color Palette Theme
              </label>
              <div className="mt-2 grid grid-cols-4 gap-2">
                {(['zinc', 'slate', 'stone', 'gray'] as ThemePalette[]).map((t) => (
                  <button
                    key={t}
                    onClick={() => setTheme(t)}
                    className={`rounded-lg border py-2 text-sm font-medium capitalize transition-all cursor-pointer ${
                      theme === t
                        ? 'border-primary bg-primary text-primary-foreground shadow-sm'
                        : 'border-border bg-transparent hover:bg-secondary text-muted-foreground'
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            {/* Mode Select */}
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Appearance Mode
              </label>
              <div className="mt-2 grid grid-cols-2 gap-2">
                {(['light', 'dark'] as AppearanceMode[]).map((m) => (
                  <button
                    key={m}
                    onClick={() => setMode(m)}
                    className={`rounded-lg border py-2 text-sm font-medium capitalize transition-all cursor-pointer ${
                      mode === m
                        ? 'border-primary bg-primary text-primary-foreground shadow-sm'
                        : 'border-border bg-transparent hover:bg-secondary text-muted-foreground'
                    }`}
                  >
                    {m} Mode
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Info/About Card */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-semibold text-foreground mb-4">About Sangrahalayamu</h2>
            <div className="space-y-3 text-xs text-muted-foreground leading-relaxed">
              <p>
                <b>Sangrahalayamu</b> is an enterprise document intelligence and repository workspace designed for industrial, compliance, and engineering datasets.
              </p>
              <p>
                Equipped with semantic vector-RAG pipelines, optical character recognition (OCR), graph relation schema modeling, and citation traceback panels, it ensures that your operations remain secure and searchable.
              </p>
              <p>
                System Version: <b>v1.0.4</b><br />
                Security Clearance Level: <b>RAG-Tier 3</b>
              </p>
            </div>
          </div>

          <div className="border-t border-border/40 pt-4 mt-6 flex justify-between items-center text-[10px] text-muted-foreground">
            <span>© 2026 economic times</span>
            <span>All rights reserved</span>
          </div>
        </div>
      </div>
    </div>
  );
}
