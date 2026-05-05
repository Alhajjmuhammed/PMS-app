'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Input from '@/components/Input';
import Modal from '@/components/Modal';
import { authService } from '@/lib/auth';

export default function SettingsPage() {
  const { user, refreshUser } = useAuth();
  const [showMFASetup, setShowMFASetup] = useState(false);
  const [mfaMethod, setMfaMethod] = useState<'TOTP' | 'EMAIL' | 'SMS'>('TOTP');
  const [qrCode, setQrCode] = useState('');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [verificationCode, setVerificationCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [mfaEnabled, setMfaEnabled] = useState(false);

  const handleSetupMFA = async () => {
    setLoading(true);
    try {
      const response = await authService.setupMFA(mfaMethod);
      if (response.qr_code) {
        setQrCode(response.qr_code);
      }
      setBackupCodes(response.backup_codes);
      setShowMFASetup(true);
    } catch (error: any) {
      alert(error.response?.data?.error || 'Failed to setup MFA');
    } finally {
      setLoading(false);
    }
  };

  const handleEnableMFA = async () => {
    if (!verificationCode) {
      alert('Please enter the verification code');
      return;
    }

    setLoading(true);
    try {
      await authService.enableMFA(verificationCode, mfaMethod);
      alert('MFA enabled successfully!');
      setMfaEnabled(true);
      setShowMFASetup(false);
      await refreshUser();
    } catch (error: any) {
      alert(error.response?.data?.error || 'Failed to enable MFA');
    } finally {
      setLoading(false);
    }
  };

  const handleDisableMFA = async () => {
    const code = prompt('Enter verification code to disable MFA:');
    if (!code) return;

    try {
      await authService.disableMFA(code);
      alert('MFA disabled successfully');
      setMfaEnabled(false);
      await refreshUser();
    } catch (error: any) {
      alert(error.response?.data?.error || 'Failed to disable MFA');
    }
  };

  return (
    <Layout>
      <div className="max-w-4xl space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>

        {/* Profile Information */}
        <Card title="Profile Information">
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-sm font-medium text-gray-500">Name:</dt>
              <dd className="text-sm text-gray-900">
                {user?.first_name} {user?.last_name}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm font-medium text-gray-500">Email:</dt>
              <dd className="text-sm text-gray-900">{user?.email}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm font-medium text-gray-500">Role:</dt>
              <dd className="text-sm text-gray-900">{user?.role}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm font-medium text-gray-500">Property:</dt>
              <dd className="text-sm text-gray-900">{user?.assigned_property?.name || 'N/A'}</dd>
            </div>
          </dl>
        </Card>

        {/* Security Settings */}
        <Card title="Security">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h4 className="text-sm font-medium text-gray-900">Multi-Factor Authentication</h4>
                <p className="text-sm text-gray-500">
                  {mfaEnabled || user?.mfa_enabled 
                    ? 'MFA is currently enabled' 
                    : 'Add an extra layer of security to your account'}
                </p>
              </div>
              {mfaEnabled || user?.mfa_enabled ? (
                <Button variant="danger" onClick={handleDisableMFA}>
                  Disable MFA
                </Button>
              ) : (
                <Button onClick={handleSetupMFA} isLoading={loading}>
                  Setup MFA
                </Button>
              )}
            </div>

            {!mfaEnabled && !user?.mfa_enabled && (
              <div className="flex gap-2">
                <button
                  onClick={() => setMfaMethod('TOTP')}
                  className={`px-4 py-2 rounded-md text-sm ${
                    mfaMethod === 'TOTP' ? 'bg-primary-600 text-white' : 'bg-gray-100'
                  }`}
                >
                  Authenticator App
                </button>
                <button
                  onClick={() => setMfaMethod('EMAIL')}
                  className={`px-4 py-2 rounded-md text-sm ${
                    mfaMethod === 'EMAIL' ? 'bg-primary-600 text-white' : 'bg-gray-100'
                  }`}
                >
                  Email
                </button>
                <button
                  onClick={() => setMfaMethod('SMS')}
                  className={`px-4 py-2 rounded-md text-sm ${
                    mfaMethod === 'SMS' ? 'bg-primary-600 text-white' : 'bg-gray-100'
                  }`}
                >
                  SMS
                </button>
              </div>
            )}
          </div>
        </Card>

        {/* MFA Setup Modal */}
        <Modal
          isOpen={showMFASetup}
          onClose={() => setShowMFASetup(false)}
          title="Setup Multi-Factor Authentication"
          size="lg"
        >
          <div className="space-y-6">
            {qrCode && mfaMethod === 'TOTP' && (
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-4">
                  Scan this QR code with Google Authenticator or Authy
                </p>
                <img src={qrCode} alt="QR Code" className="mx-auto max-w-xs" />
              </div>
            )}

            {mfaMethod === 'EMAIL' && (
              <p className="text-sm text-gray-600">
                A verification code has been sent to your email
              </p>
            )}

            {mfaMethod === 'SMS' && (
              <p className="text-sm text-gray-600">
                A verification code has been sent to your phone
              </p>
            )}

            <Input
              label="Verification Code"
              placeholder="Enter 6-digit code"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
            />

            {backupCodes.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">
                  Backup Codes (Save these securely):
                </p>
                <div className="bg-gray-50 p-4 rounded-md grid grid-cols-2 gap-2">
                  {backupCodes.map((code, index) => (
                    <code key={index} className="text-sm font-mono">
                      {code}
                    </code>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-end gap-3">
              <Button variant="secondary" onClick={() => setShowMFASetup(false)}>
                Cancel
              </Button>
              <Button onClick={handleEnableMFA} isLoading={loading}>
                Enable MFA
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </Layout>
  );
}
