import React from 'react';
import AppShell from '@/components/layout/app-shell';
import AuthenticatedSessionGate from '@/components/layout/authenticated-session-gate';

export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthenticatedSessionGate>
      <AppShell>{children}</AppShell>
    </AuthenticatedSessionGate>
  );
}
