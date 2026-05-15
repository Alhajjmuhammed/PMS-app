'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Input from '@/components/Input';
import api from '@/lib/api';

export default function PasswordChangePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ text: string; ok: boolean } | null>(null);
  const [formData, setFormData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.new_password !== formData.confirm_password) {
      setMessage({ text: 'New passwords do not match', ok: false });
      return;
    }

    if (formData.new_password.length < 8) {
      setMessage({ text: 'Password must be at least 8 characters long', ok: false });
      return;
    }

    try {
      setLoading(true);
      await api.post('/api/v1/auth/change-password/', {
        old_password: formData.current_password,
        new_password: formData.new_password,
        confirm_password: formData.confirm_password,
      });
      setMessage({ text: 'Password changed successfully!', ok: true });
      setFormData({ current_password: '', new_password: '', confirm_password: '' });
      setTimeout(() => router.push('/settings'), 1000);
    } catch (error: any) {
      setMessage({ text: error.response?.data?.detail || 'Failed to change password', ok: false });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-2xl mx-auto space-y-6">
        {message && (
          <div className={`px-4 py-3 rounded-lg text-sm font-medium border ${message.ok ? 'bg-green-50 text-green-800 border-green-200' : 'bg-red-50 text-red-800 border-red-200'}`}>{message.text}</div>
        )}
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Change Password</h1>
          <Button variant="secondary" onClick={() => router.push('/settings')}>
            Back to Settings
          </Button>
        </div>

        <Card>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Current Password"
              type="password"
              value={formData.current_password}
              onChange={(e) => setFormData({ ...formData, current_password: e.target.value })}
              required
            />

            <Input
              label="New Password"
              type="password"
              value={formData.new_password}
              onChange={(e) => setFormData({ ...formData, new_password: e.target.value })}
              helperText="Must be at least 8 characters long"
              required
            />

            <Input
              label="Confirm New Password"
              type="password"
              value={formData.confirm_password}
              onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
              required
            />

            <div className="pt-4">
              <Button type="submit" isLoading={loading} fullWidth>
                Change Password
              </Button>
            </div>
          </form>
        </Card>

        <Card title="Password Requirements">
          <ul className="space-y-2 text-sm text-gray-600">
            <li>• Minimum 8 characters</li>
            <li>• Mix of uppercase and lowercase letters recommended</li>
            <li>• Include numbers and special characters for better security</li>
            <li>• Avoid using common words or personal information</li>
          </ul>
        </Card>
      </div>
    </Layout>
  );
}
