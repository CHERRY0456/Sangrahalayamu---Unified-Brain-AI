import React, { Suspense } from 'react';
import AuthCard from '@/features/auth/auth-card';
import ResetPasswordForm from '@/features/auth/reset-password-form';

export default function ResetPasswordPage() {
  return (
    <AuthCard
      title="Create New Password"
      subtitle="Establish a strong, compliant security password for your credentials."
    >
      <Suspense fallback={<div className="text-xs text-muted-foreground">Loading...</div>}>
        <ResetPasswordForm />
      </Suspense>
    </AuthCard>
  );
}
