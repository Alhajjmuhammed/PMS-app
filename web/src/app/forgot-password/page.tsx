'use client';

import { useState } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Input from '@/components/Input';
import api from '@/lib/api';

export default function ForgotPasswordPage() {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSendCode = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      await api.post('/api/v1/accounts/password-reset/request/', { email });
      alert('Reset code sent to your email!');
      setStep(2);
    } catch (error) {
      alert('Failed to send reset code');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      alert('Passwords do not match');
      return;
    }

    if (newPassword.length < 8) {
      alert('Password must be at least 8 characters');
      return;
    }

    try {
      setLoading(true);
      await api.post('/api/v1/accounts/password-reset/confirm/', {
        email,
        code,
        new_password: newPassword,
      });
      alert('Password reset successfully!');
      window.location.href = '/login';
    } catch (error) {
      alert('Failed to reset password. Please check your code.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">Reset Password</h2>
          <p className="mt-2 text-sm text-gray-600">
            {step === 1 ? 'Enter your email to receive a reset code' : 'Enter the code and your new password'}
          </p>
        </div>

        {step === 1 ? (
          <Card>
            <form onSubmit={handleSendCode} className="space-y-4">
              <Input
                label="Email Address"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />

              <Button type="submit" isLoading={loading} fullWidth>
                Send Reset Code
              </Button>

              <div className="text-center">
                <a href="/login" className="text-sm text-primary-600 hover:text-primary-700">
                  Back to Login
                </a>
              </div>
            </form>
          </Card>
        ) : (
          <Card>
            <form onSubmit={handleResetPassword} className="space-y-4">
              <Input
                label="Reset Code"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="Enter 6-digit code"
                required
              />

              <Input
                label="New Password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                helperText="Must be at least 8 characters"
                required
              />

              <Input
                label="Confirm Password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />

              <Button type="submit" isLoading={loading} fullWidth>
                Reset Password
              </Button>

              <div className="text-center space-y-2">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="text-sm text-primary-600 hover:text-primary-700 block w-full"
                >
                  Didn&apos;t receive code? Try again
                </button>
                <a href="/login" className="text-sm text-gray-600 hover:text-gray-700 block">
                  Back to Login
                </a>
              </div>
            </form>
          </Card>
        )}
      </div>
    </div>
  );
}
