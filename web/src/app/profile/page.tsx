'use client';

import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import clsx from 'clsx';
import {
  UserCircleIcon,
  PencilSquareIcon,
  LockClosedIcon,
  CheckCircleIcon,
  XMarkIcon,
  BuildingOfficeIcon,
  EnvelopeIcon,
  PhoneIcon,
  ShieldCheckIcon,
  CalendarDaysIcon,
} from '@heroicons/react/24/outline';

const ROLE_COLORS: Record<string, string> = {
  ADMIN:        'bg-purple-100 text-purple-700',
  MANAGER:      'bg-blue-100 text-blue-700',
  FRONT_DESK:   'bg-emerald-100 text-emerald-700',
  HOUSEKEEPING: 'bg-amber-100 text-amber-700',
  MAINTENANCE:  'bg-orange-100 text-orange-700',
  ACCOUNTANT:   'bg-teal-100 text-teal-700',
  POS_STAFF:    'bg-pink-100 text-pink-700',
  GUEST:        'bg-slate-100 text-slate-600',
};

const AVATAR_COLORS = [
  'from-blue-500 to-blue-600',
  'from-violet-500 to-violet-600',
  'from-emerald-500 to-emerald-600',
  'from-amber-500 to-amber-600',
  'from-pink-500 to-pink-600',
  'from-teal-500 to-teal-600',
];

function formatDate(str?: string | null) {
  if (!str) return '—';
  return new Date(str).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

export default function ProfilePage() {
  const { user, refreshUser } = useAuth();

  // profile form state
  const [editMode, setEditMode] = useState(false);
  const [profileForm, setProfileForm] = useState({ first_name: '', last_name: '', phone: '' });
  const [savingProfile, setSavingProfile] = useState(false);

  // password form state
  const [pwForm, setPwForm] = useState({ old_password: '', new_password: '', confirm_password: '' });
  const [savingPw, setSavingPw] = useState(false);
  const [showPwSection, setShowPwSection] = useState(false);

  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  };

  useEffect(() => {
    if (user) {
      setProfileForm({
        first_name: user.first_name ?? '',
        last_name: user.last_name ?? '',
        phone: (user as any).phone ?? '',
      });
    }
  }, [user]);

  const avatarColor = AVATAR_COLORS[(user?.id ?? 0) % AVATAR_COLORS.length];
  const initials = `${user?.first_name?.[0] ?? ''}${user?.last_name?.[0] ?? ''}`.toUpperCase() || '?';
  const roleLabel = user?.is_superuser ? 'SUPERADMIN' : (user?.role ?? '');
  const roleColor = user?.is_superuser
    ? 'bg-amber-100 text-amber-800'
    : (ROLE_COLORS[user?.role ?? ''] ?? 'bg-slate-100 text-slate-600');

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingProfile(true);
    try {
      await api.patch('/api/v1/auth/me/', profileForm);
      await refreshUser();
      setEditMode(false);
      showToast('Profile updated successfully');
    } catch {
      showToast('Failed to update profile', false);
    } finally {
      setSavingProfile(false);
    }
  };

  const handlePasswordSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pwForm.new_password !== pwForm.confirm_password) {
      showToast('New passwords do not match', false);
      return;
    }
    if (pwForm.new_password.length < 8) {
      showToast('Password must be at least 8 characters', false);
      return;
    }
    setSavingPw(true);
    try {
      await api.post('/api/v1/auth/change-password/', {
        old_password: pwForm.old_password,
        new_password: pwForm.new_password,
        confirm_password: pwForm.confirm_password,
      });
      setPwForm({ old_password: '', new_password: '', confirm_password: '' });
      setShowPwSection(false);
      showToast('Password changed successfully. Please log in again.');
    } catch (err: any) {
      const detail = err?.response?.data;
      const msg =
        typeof detail === 'string'
          ? detail
          : typeof detail === 'object'
          ? Object.values(detail).flat().join(' ')
          : 'Failed to change password';
      showToast(msg as string, false);
    } finally {
      setSavingPw(false);
    }
  };

  return (
    <Layout>
      <div className="p-5 lg:p-6 max-w-2xl mx-auto space-y-5">
        {/* Toast */}
        {toast && (
          <div
            className={clsx(
              'fixed top-5 right-5 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium',
              toast.ok ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white',
            )}
          >
            <CheckCircleIcon className="w-5 h-5 flex-shrink-0" />
            {toast.msg}
          </div>
        )}

        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-slate-900">My Profile</h1>
          <p className="text-slate-500 text-sm mt-0.5">Manage your account information and password</p>
        </div>

        {/* Profile Card */}
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
          {/* Avatar bar */}
          <div className="bg-gradient-to-r from-slate-800 to-slate-900 px-6 py-8 flex items-center gap-5">
            <div
              className={clsx(
                'w-20 h-20 rounded-2xl bg-gradient-to-br flex items-center justify-center text-white text-2xl font-bold shadow-lg flex-shrink-0',
                avatarColor,
              )}
            >
              {initials}
            </div>
            <div className="min-w-0">
              <h2 className="text-white text-xl font-bold leading-tight">
                {user?.first_name} {user?.last_name}
              </h2>
              <p className="text-slate-400 text-sm mt-0.5">{user?.email}</p>
              <span
                className={clsx(
                  'inline-block mt-2 px-2.5 py-0.5 rounded-full text-xs font-semibold',
                  roleColor,
                )}
              >
                {roleLabel.replace('_', ' ')}
              </span>
            </div>
          </div>

          {/* Info / Edit */}
          <div className="p-6">
            {!editMode ? (
              <>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-slate-700">Account Details</h3>
                  <button
                    onClick={() => setEditMode(true)}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:text-blue-700 px-3 py-1.5 rounded-lg hover:bg-blue-50 transition-colors"
                  >
                    <PencilSquareIcon className="w-4 h-4" />
                    Edit
                  </button>
                </div>
                <dl className="space-y-3">
                  <Row icon={<UserCircleIcon className="w-4 h-4" />} label="Full Name">
                    {user?.first_name} {user?.last_name}
                  </Row>
                  <Row icon={<EnvelopeIcon className="w-4 h-4" />} label="Email">
                    {user?.email}
                  </Row>
                  <Row icon={<PhoneIcon className="w-4 h-4" />} label="Phone">
                    {(user as any)?.phone || <span className="text-slate-400 italic">Not set</span>}
                  </Row>
                  <Row icon={<ShieldCheckIcon className="w-4 h-4" />} label="Role">
                    <span className={clsx('px-2 py-0.5 rounded-full text-xs font-semibold', roleColor)}>
                      {roleLabel.replace('_', ' ')}
                    </span>
                  </Row>
                  {user?.assigned_property && (
                    <Row icon={<BuildingOfficeIcon className="w-4 h-4" />} label="Property">
                      {user.assigned_property.name}
                    </Row>
                  )}
                  <Row icon={<CalendarDaysIcon className="w-4 h-4" />} label="Member since">
                    {formatDate((user as any)?.date_joined)}
                  </Row>
                </dl>
              </>
            ) : (
              <form onSubmit={handleProfileSave} className="space-y-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-semibold text-slate-700">Edit Profile</h3>
                  <button
                    type="button"
                    onClick={() => setEditMode(false)}
                    className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 transition-colors"
                  >
                    <XMarkIcon className="w-4 h-4" />
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">First Name</label>
                    <input
                      value={profileForm.first_name}
                      onChange={(e) => setProfileForm((p) => ({ ...p, first_name: e.target.value }))}
                      className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Last Name</label>
                    <input
                      value={profileForm.last_name}
                      onChange={(e) => setProfileForm((p) => ({ ...p, last_name: e.target.value }))}
                      className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Phone</label>
                  <input
                    type="tel"
                    placeholder="+1-555-000-0000"
                    value={profileForm.phone}
                    onChange={(e) => setProfileForm((p) => ({ ...p, phone: e.target.value }))}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300"
                  />
                </div>
                <div className="pt-1 flex gap-2">
                  <button
                    type="submit"
                    disabled={savingProfile}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors"
                  >
                    {savingProfile ? 'Saving…' : 'Save Changes'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditMode(false)}
                    className="px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-600 hover:bg-slate-50 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>

        {/* Change Password */}
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
          <button
            onClick={() => setShowPwSection((v) => !v)}
            className="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-slate-50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center">
                <LockClosedIcon className="w-5 h-5 text-slate-600" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800">Change Password</p>
                <p className="text-xs text-slate-500">Update your account password</p>
              </div>
            </div>
            <span className="text-xs font-semibold text-blue-600">
              {showPwSection ? 'Cancel' : 'Change'}
            </span>
          </button>

          {showPwSection && (
            <form onSubmit={handlePasswordSave} className="px-6 pb-6 space-y-3 border-t border-slate-50">
              <div className="pt-4 space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Current Password</label>
                  <input
                    type="password"
                    required
                    value={pwForm.old_password}
                    onChange={(e) => setPwForm((p) => ({ ...p, old_password: e.target.value }))}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">New Password</label>
                  <input
                    type="password"
                    required
                    minLength={8}
                    value={pwForm.new_password}
                    onChange={(e) => setPwForm((p) => ({ ...p, new_password: e.target.value }))}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Confirm New Password</label>
                  <input
                    type="password"
                    required
                    value={pwForm.confirm_password}
                    onChange={(e) => setPwForm((p) => ({ ...p, confirm_password: e.target.value }))}
                    className={clsx(
                      'w-full px-3 py-2.5 rounded-xl border text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300',
                      pwForm.confirm_password && pwForm.confirm_password !== pwForm.new_password
                        ? 'border-red-300'
                        : 'border-slate-200',
                    )}
                  />
                  {pwForm.confirm_password && pwForm.confirm_password !== pwForm.new_password && (
                    <p className="text-xs text-red-500 mt-1">Passwords do not match</p>
                  )}
                </div>
              </div>
              <button
                type="submit"
                disabled={savingPw}
                className="w-full bg-slate-800 hover:bg-slate-900 disabled:opacity-60 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors"
              >
                {savingPw ? 'Updating…' : 'Update Password'}
              </button>
            </form>
          )}
        </div>
      </div>
    </Layout>
  );
}

function Row({
  icon,
  label,
  children,
}: {
  icon: React.ReactNode;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-start gap-3 py-2 border-b border-slate-50 last:border-0">
      <span className="text-slate-400 mt-0.5 flex-shrink-0">{icon}</span>
      <dt className="text-xs font-semibold text-slate-500 w-28 flex-shrink-0 mt-0.5">{label}</dt>
      <dd className="text-sm text-slate-800 font-medium">{children}</dd>
    </div>
  );
}
