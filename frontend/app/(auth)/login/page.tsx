'use client';

import React, { useState } from 'react';
import { usePersonaStore } from '@/features/persona/persona-context';
import { useRouter } from 'next/navigation';
import { ShieldCheck, Loader2, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const { loginUser, isInitializing, initStage, profile, persona } = usePersonaStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email.trim() || !password.trim()) {
      setError('Please enter your email and password.');
      return;
    }

    try {
      const success = await loginUser(email.trim(), password);
      if (success) {
        router.push('/dashboard');
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check your credentials.');
    }
  };

  if (isInitializing) {
    
    return (
      <div className="flex min-h-screen flex-col items-center justify-center p-8 bg-background text-foreground text-center space-y-6 max-w-md mx-auto animate-in fade-in duration-300">
        
        {/* welcome banner header */}
        <div className="space-y-2 border-b border-border/80 pb-4 w-full">
          <span className="text-[10px] font-bold text-primary uppercase tracking-widest block animate-pulse">
            Secure Clearance Verification
          </span>
          <h2 className="text-xl font-black text-foreground">Authenticating</h2>
        </div>

        {/* Checklists stage loaders */}
        <div className="w-full space-y-3.5 text-xs text-left bg-secondary/15 border border-border/80 rounded-xl p-5">
          {/* Stage 1 */}
          <div className="flex justify-between items-center">
            <span className={initStage >= 1 ? 'text-foreground font-semibold' : 'text-muted-foreground'}>
              1. Authenticating...
            </span>
            {initStage > 1 ? (
              <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
            ) : initStage === 1 ? (
              <Loader2 className="h-4 w-4 text-primary animate-spin shrink-0" />
            ) : (
              <span className="text-muted-foreground/30 text-[10px] uppercase font-bold">Pending</span>
            )}
          </div>

          {/* Stage 2 */}
          <div className="flex justify-between items-center">
            <span className={initStage >= 2 ? 'text-foreground font-semibold' : 'text-muted-foreground'}>
              2. Loading Employee Profile...
            </span>
            {initStage > 2 ? (
              <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
            ) : initStage === 2 ? (
              <Loader2 className="h-4 w-4 text-primary animate-spin shrink-0" />
            ) : (
              <span className="text-muted-foreground/30 text-[10px] uppercase font-bold">Pending</span>
            )}
          </div>

          {/* Stage 3 */}
          <div className="flex justify-between items-center">
            <span className={initStage >= 3 ? 'text-foreground font-semibold' : 'text-muted-foreground'}>
              3. Configuring Workspace...
            </span>
            {initStage > 3 ? (
              <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
            ) : initStage === 3 ? (
              <Loader2 className="h-4 w-4 text-primary animate-spin shrink-0" />
            ) : (
              <span className="text-muted-foreground/30 text-[10px] uppercase font-bold">Pending</span>
            )}
          </div>

          {/* Stage 4 */}
          <div className="flex justify-between items-center">
            <span className={initStage >= 4 ? 'text-foreground font-semibold' : 'text-muted-foreground'}>
              4. Loading AI Preferences...
            </span>
            {initStage === 4 ? (
              <Loader2 className="h-4 w-4 text-primary animate-spin shrink-0" />
            ) : (
              <span className="text-muted-foreground/30 text-[10px] uppercase font-bold">Pending</span>
            )}
          </div>
        </div>

        {/* Configuration notification */}
        {profile && (
          <div className="text-[10px] text-muted-foreground/80 leading-normal border border-dashed border-border/80 rounded p-3 bg-card w-full">
            Workspace configuring for: <b>{profile.designation} Operations</b>
          </div>
        )}

      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-6 bg-background text-foreground animate-in fade-in duration-300">
      <div className="w-full max-w-sm space-y-6">
        
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 border border-primary/20 text-primary mb-2 shadow-sm">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-black tracking-tight text-foreground">Log In</h1>
          <p className="text-xs text-muted-foreground">
            Enter your credentials to access the Sangrahalayamu workspace.
          </p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border border-border bg-card p-6 shadow-sm">
          {/* Email */}
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
              Company Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@company.com"
              className="w-full rounded-lg border border-border bg-background px-3.5 py-2 text-xs text-foreground outline-none focus:border-primary placeholder:text-muted-foreground/40"
              required
            />
          </div>

          {/* Name field removed — resolved from backend profile */}

          {/* Password */}
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full rounded-lg border border-border bg-background px-3.5 py-2 text-xs text-foreground outline-none focus:border-primary placeholder:text-muted-foreground/40"
              required
            />
          </div>

          {/* Error */}
          {error && (
            <div className="flex gap-2 rounded-lg border border-destructive/20 bg-destructive/10 p-3 text-[11px] text-destructive leading-normal">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <span className="font-semibold">{error}</span>
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            className="w-full rounded-lg bg-primary hover:bg-primary/95 text-xs font-bold text-primary-foreground py-2.5 transition-all shadow-sm cursor-pointer"
          >
            Access Workspace
          </button>
        </form>

      </div>
    </div>
  );
}
