import React from 'react';

interface AuthCardProps {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}

export default function AuthCard({ title, subtitle, children }: AuthCardProps) {
  return (
    <div className="rounded-xl border border-border bg-card p-8 shadow-lg transition-all duration-200">
      {/* Brand & Title */}
      <div className="mb-6 text-center">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-2xl">
          ⚙️
        </div>
        <h1 className="mt-4 text-2xl font-bold tracking-tight text-foreground">
          Sangrahalayamu
        </h1>
        <h2 className="mt-2 text-lg font-semibold text-foreground">{title}</h2>
        <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>
      </div>

      {/* Card Content */}
      <div>{children}</div>
    </div>
  );
}
