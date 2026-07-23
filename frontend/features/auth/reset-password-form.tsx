'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Eye, EyeOff, CheckCircle2, Loader2, ArrowLeft } from 'lucide-react';
import { useSearchParams } from 'next/navigation';

export default function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const resetToken = searchParams.get('token') || '';
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [strengthScore, setStrengthScore] = useState(0);
  const [strengthLabel, setStrengthLabel] = useState('Very Weak');
  const [errors, setErrors] = useState<{ password?: string; confirmPassword?: string }>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  // Dynamic Password Strength Assessment
  useEffect(() => {
    if (!password) {
      setStrengthScore(0);
      setStrengthLabel('Very Weak');
      return;
    }

    let score = 0;
    if (password.length >= 8) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;

    setStrengthScore(score);

    switch (score) {
      case 0:
      case 1:
        setStrengthLabel('Weak');
        break;
      case 2:
        setStrengthLabel('Fair');
        break;
      case 3:
        setStrengthLabel('Good');
        break;
      case 4:
        setStrengthLabel('Strong');
        break;
    }
  }, [password]);

  const validateForm = () => {
    const newErrors: { password?: string; confirmPassword?: string } = {};

    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsLoading(true);

    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${baseUrl}/api/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: resetToken, new_password: password }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Password reset failed.' }));
        setErrors({ password: err.detail || 'Reset failed.' });
        return;
      }
      setIsSubmitted(true);
    } catch {
      setErrors({ password: 'Network error. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const getStrengthColor = () => {
    switch (strengthScore) {
      case 0:
        return 'bg-muted';
      case 1:
        return 'bg-destructive';
      case 2:
        return 'bg-amber-500';
      case 3:
        return 'bg-primary';
      case 4:
        return 'bg-emerald-500';
      default:
        return 'bg-muted';
    }
  };

  if (isSubmitted) {
    return (
      <div className="text-center space-y-4 animate-in fade-in duration-200">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-500">
          <CheckCircle2 className="h-6 w-6" />
        </div>
        <div className="space-y-2">
          <h3 className="text-md font-semibold text-foreground">Password Reset Successful</h3>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Your login password has been updated securely. You can now use your new password to sign in.
          </p>
        </div>
        <Link
          href="/login"
          className="inline-flex w-full justify-center items-center gap-1.5 rounded-lg bg-primary hover:bg-primary/95 text-primary-foreground py-2 text-sm font-semibold shadow-sm transition-all cursor-pointer"
        >
          Sign In Now
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* New Password Input */}
      <div>
        <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
          New Password
        </label>
        <div className="relative">
          <input
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              if (errors.password) setErrors((prev) => ({ ...prev, password: undefined }));
            }}
            disabled={isLoading}
            placeholder="Min. 8 characters"
            className={`w-full rounded-lg border bg-background pl-3 pr-10 py-2 text-sm text-foreground outline-none transition-all ${
              errors.password ? 'border-destructive focus:ring-1 focus:ring-destructive' : 'border-border focus:border-primary'
            }`}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            disabled={isLoading}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground cursor-pointer"
          >
            {showPassword ? <EyeOff className="h-4.5 w-4.5" /> : <Eye className="h-4.5 w-4.5" />}
          </button>
        </div>
        {/* Strength Meter Gauge */}
        <div className="mt-2 space-y-1">
          <div className="flex justify-between items-center text-[10px] font-semibold text-muted-foreground uppercase">
            <span>Strength: <b className="text-foreground">{strengthLabel}</b></span>
            <span>{strengthScore * 25}%</span>
          </div>
          <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-350 ease-out ${getStrengthColor()}`}
              style={{ width: `${Math.max(5, strengthScore * 25)}%` }}
            />
          </div>
        </div>
        {errors.password && (
          <p className="mt-1 text-xs text-destructive font-medium">{errors.password}</p>
        )}
      </div>

      {/* Confirm Password Input */}
      <div>
        <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
          Confirm Password
        </label>
        <div className="relative">
          <input
            type={showConfirmPassword ? 'text' : 'password'}
            value={confirmPassword}
            onChange={(e) => {
              setConfirmPassword(e.target.value);
              if (errors.confirmPassword) setErrors((prev) => ({ ...prev, confirmPassword: undefined }));
            }}
            disabled={isLoading}
            placeholder="Re-enter password"
            className={`w-full rounded-lg border bg-background pl-3 pr-10 py-2 text-sm text-foreground outline-none transition-all ${
              errors.confirmPassword ? 'border-destructive focus:ring-1 focus:ring-destructive' : 'border-border focus:border-primary'
            }`}
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            disabled={isLoading}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground cursor-pointer"
          >
            {showConfirmPassword ? <EyeOff className="h-4.5 w-4.5" /> : <Eye className="h-4.5 w-4.5" />}
          </button>
        </div>
        {errors.confirmPassword && (
          <p className="mt-1 text-xs text-destructive font-medium">{errors.confirmPassword}</p>
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
            Updating...
          </>
        ) : (
          'Update Password'
        )}
      </button>

      <div className="text-center pt-2">
        <Link
          href="/login"
          className="inline-flex items-center gap-1.5 text-xs text-primary hover:underline font-semibold"
        >
          <ArrowLeft className="h-3 w-3" />
          Cancel & Return to Login
        </Link>
      </div>
    </form>
  );
}
