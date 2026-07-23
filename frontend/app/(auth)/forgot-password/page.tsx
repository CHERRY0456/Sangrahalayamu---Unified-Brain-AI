import React from 'react';
import AuthCard from '@/features/auth/auth-card';
import ForgotPasswordForm from '@/features/auth/forgot-password-form';

export default function ForgotPasswordPage() {
  return (
    <AuthCard
      title="Recover Password"
      subtitle="Input your registered email to request a secure password recovery link."
    >
      <ForgotPasswordForm />
    </AuthCard>
  );
}
