'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Input from '@/components/Input';
import Modal from '@/components/Modal';
import { authService } from '@/lib/auth';
import {
  HomeIcon, ChevronRightIcon, Cog6ToothIcon,
} from '@heroicons/react/24/outline';

export default function SettingsPage() {
  const { user, refreshUser } = useAuth();
  const [showMFASetup, setShowMFASetup] = useState(false);
  const [mfaMethod, setMfaMethod] = useState<'TOTP' | 'EMAIL' | 'SMS'>('TOTP');
  const [qrCode, setQrCode] = useState('');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [verificationCode, setVerificationCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [mfaEnabled, setMfaEnabled] = useState(false);
  const [mfaMessage, setMfaMessage] = useState<{ text: string; ok: boolean } | null>(null);
  const [showDisableMFA, setShowDisableMFA] = useState(false);
  const [disableCode, setDisableCode] = useState('');

  const showMfaMsg = (text: string, ok = true) => {
    setMfaMessage({ text, ok });
    setTimeout(() => setMfaMessage(null), 3500);
  };

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
      showMfaMsg(error.response?.data?.error || 'Failed to setup MFA', false);
    } finally {
      setLoading(false);
    }
  };

  const handleEnableMFA = async () => {
    if (!verificationCode) {
      showMfaMsg('Please enter the verification code', false);
      return;
    }

    setLoading(true);
    try {
      await authService.enableMFA(verificationCode, mfaMethod);
      showMfaMsg('MFA enabled successfully!');
      setMfaEnabled(true);
      setShowMFASetup(false);
      await refreshUser();
    } catch (error: any) {
      showMfaMsg(error.response?.data?.error || 'Failed to enable MFA', false);
    } finally {
      setLoading(false);
    }
  };

  const handleDisableMFA = async () => {
    if (!disableCode) {
      showMfaMsg('Please enter the verification code', false);
      return;
    }
    try {
      await authService.disableMFA(disableCode);
      showMfaMsg('MFA disabled successfully');
      setMfaEnabled(false);
      setShowDisableMFA(false);
      setDisableCode('');
      await refreshUser();
    } catch (error: any) {
      showMfaMsg(error.response?.data?.error || 'Failed to disable MFA', false);
    }
  };

  return (
    <Layout>
      <div className="p-5 lg:p-6 space-y-5">
        {mfaMessage && (
          <div className={`px-4 py-3 rounded-lg text-sm font-medium border ${mfaMessage.ok ? 'bg-green-50 text-green-800 border-green-200' : 'bg-red-50 text-red-800 border-red-200'}`}>{mfaMessage.text}</div>
        )}
        {/* Breadcrumb */}
        <nav className="flex items-center gap-1.5 text-sm text-slate-400">
          <HomeIcon className="w-4 h-4" />
          <span>Home</span>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <span className="text-slate-700 font-medium">Settings</span>
        </nav>

        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center flex-shrink-0">
              <Cog6ToothIcon className="w-5 h-5 text-slate-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
            </div>
          </div>
        </div>

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
              <dd className="text-sm text-gray-900">
                {user?.is_superuser ? (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-800">
                    ★ Super Admin
                  </span>
                ) : (
                  user?.role?.replace('_', ' ')
                )}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm font-medium text-gray-500">Property:</dt>
              <dd className="text-sm text-gray-900">
                {user?.is_superuser
                  ? <span className="text-purple-700 font-medium">All Properties (Platform)</span>
                  : user?.assigned_property?.name || 'N/A'}
              </dd>
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
                <Button variant="danger" onClick={() => setShowDisableMFA(true)}>
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

        {/* Disable MFA Modal */}
        <Modal
          isOpen={showDisableMFA}
          onClose={() => { setShowDisableMFA(false); setDisableCode(''); }}
          title="Disable MFA"
        >
          <div className="space-y-4">
            <p className="text-sm text-gray-600">Enter your verification code to disable multi-factor authentication.</p>
            <input
              type="text"
              value={disableCode}
              onChange={(e) => setDisableCode(e.target.value)}
              placeholder="Verification code"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <div className="flex gap-2 justify-end">
              <Button variant="secondary" onClick={() => { setShowDisableMFA(false); setDisableCode(''); }}>Cancel</Button>
              <Button variant="danger" onClick={handleDisableMFA} isLoading={loading}>Disable MFA</Button>
            </div>
          </div>
        </Modal>
      </div>
    </Layout>
  );
}
