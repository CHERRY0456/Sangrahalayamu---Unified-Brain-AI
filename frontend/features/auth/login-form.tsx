'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Eye, EyeOff, Loader2, AlertTriangle } from 'lucide-react';
import { usePersonaStore } from '@/features/persona/persona-context';

export default function LoginForm() {
  const router = useRouter();
  const { loginUser } = usePersonaStore();
  
  // State variables
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string; general?: string }>({});
  const [isLoading, setIsLoading] = useState(false);

  // Validate form frontend-only
  const validateForm = () => {
    const newErrors: { email?: string; password?: string } = {};
    
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsLoading(true);
    setErrors({});

    try {
      const success = await loginUser(email, password);
      if (success) {
        router.push('/dashboard');
      }
    } catch (err: any) {
      setErrors({ general: err.message || 'Authentication failed. Please check your credentials.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* General error */}
      {errors.general && (
        <div className="flex gap-2 rounded-lg border border-destructive/20 bg-destructive/10 p-3 text-[11px] text-destructive leading-normal">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <span className="font-semibold">{errors.general}</span>
        </div>
      )}

      {/* Email Input */}
      <div>
        <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1">
          Email Address
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            if (errors.email) setErrors((prev) => ({ ...prev, email: undefined }));
          }}
          disabled={isLoading}
          placeholder="name@company.com"
          className={`w-full rounded-lg border bg-background px-3 py-2 text-sm text-foreground outline-none transition-all ${
            errors.email ? 'border-destructive focus:ring-1 focus:ring-destructive' : 'border-border focus:border-primary'
          }`}
        />
        {errors.email && (
          <p className="mt-1 text-xs text-destructive font-medium">{errors.email}</p>
        )}
      </div>

      {/* Password Input */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Password
          </label>
          <Link
            href="/forgot-password"
            className="text-xs text-primary hover:underline font-medium"
          >
            Forgot Password?
          </Link>
        </div>
        <div className="relative">
          <input
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              if (errors.password) setErrors((prev) => ({ ...prev, password: undefined }));
            }}
            disabled={isLoading}
            placeholder="••••••••"
            className={`w-full rounded-lg border bg-background pl-3 pr-10 py-2 text-sm text-foreground outline-none transition-all ${
              errors.password ? 'border-destructive focus:ring-1 focus:ring-destructive' : 'border-border focus:border-primary'
            }`}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            disabled={isLoading}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground cursor-pointer"
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? <EyeOff className="h-4.5 w-4.5" /> : <Eye className="h-4.5 w-4.5" />}
          </button>
        </div>
        {errors.password && (
          <p className="mt-1 text-xs text-destructive font-medium">{errors.password}</p>
        )}
      </div>

      {/* Remember Me Checkbox */}
      <div className="flex items-center">
        <input
          id="remember-me"
          type="checkbox"
          checked={rememberMe}
          onChange={(e) => setRememberMe(e.target.checked)}
          disabled={isLoading}
          className="h-4 w-4 rounded border-border bg-background text-primary accent-primary outline-none cursor-pointer"
        />
        <label
          htmlFor="remember-me"
          className="ml-2 text-sm text-muted-foreground select-none cursor-pointer font-medium"
        >
          Remember this device
        </label>
      </div>

      {/* Action Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-primary hover:bg-primary/95 text-primary-foreground py-2 text-sm font-semibold shadow-sm transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Authenticating...
          </>
        ) : (
          'Sign In to Dashboard'
        )}
      </button>
    </form>
  );
}


