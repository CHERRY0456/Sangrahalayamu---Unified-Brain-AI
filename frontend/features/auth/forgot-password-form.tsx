'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Mail, CheckCircle2, Loader2, ArrowLeft } from 'lucide-react';

export default function ForgotPasswordForm() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!email) {
      setError('Email is required');
      return;
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    setError(undefined);
    setIsLoading(true);

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${baseUrl}/api/auth/forgot-password`, { credentials: 'include',
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      // Always show success to prevent email enumeration
      setIsSubmitted(true);
    } catch {
      setIsSubmitted(true); // Still show success to prevent email enumeration
    } finally {
      setIsLoading(false);
    }
  };

  if (isSubmitted) {
    return (
      <div className="text-center space-y-4 animate-in fade-in duration-200">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-500">
          <CheckCircle2 className="h-6 w-6" />
        </div>
        <div className="space-y-2">
          <h3 className="text-md font-semibold text-foreground">Reset Link Transmitted</h3>
          <p className="text-xs text-muted-foreground leading-relaxed">
            If the email address <b>{email}</b> is registered in Sangrahalayamu, you will receive a secure password reset link shortly.
          </p>
        </div>
        <Link
          href="/login"
          className="inline-flex w-full justify-center items-center gap-1.5 rounded-lg border border-border bg-transparent hover:bg-secondary py-2 text-sm font-semibold transition-all cursor-pointer text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Sign In
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
          Registered Email Address
        </label>
        <div className="relative">
          <input
            type="email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              if (error) setError(undefined);
            }}
            disabled={isLoading}
            placeholder="name@company.com"
            className={`w-full rounded-lg border bg-background pl-3 pr-10 py-2 text-sm text-foreground outline-none transition-all ${
              error ? 'border-destructive focus:ring-1 focus:ring-destructive' : 'border-border focus:border-primary'
            }`}
          />
          <Mail className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        </div>
        {error && (
          <p className="mt-1 text-xs text-destructive font-medium">{error}</p>
        )}
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-primary hover:bg-primary/95 text-primary-foreground py-2 text-sm font-semibold shadow-sm transition-all cursor-pointer disabled:opacity-50"
      >
        {isLoading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Transmitting...
          </>
        ) : (
          'Send Password Reset Link'
        )}
      </button>

      <div className="text-center pt-2">
        <Link
          href="/login"
          className="inline-flex items-center gap-1.5 text-xs text-primary hover:underline font-semibold"
        >
          <ArrowLeft className="h-3 w-3" />
          Back to Sign In
        </Link>
      </div>
    </form>
  );
}
