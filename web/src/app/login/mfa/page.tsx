'use client';

import { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { authService } from '@/lib/auth';
import { BuildingLibraryIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';

function MFAForm() {
  const router = useRouter();
  const params = useSearchParams();
  const method = params.get('method') ?? 'EMAIL';
  const mfaToken = params.get('mfa_token') ?? '';

  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!mfaToken) {
      setError('Session expired. Please log in again.');
      return;
    }
    setLoading(true);
    try {
      await authService.verifyMFALogin(mfaToken, code);
      // Token stored — load user and go to dashboard
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Invalid code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const methodLabel: Record<string, string> = {
    EMAIL: 'your email',
    SMS: 'your phone',
    TOTP: 'your authenticator app',
  };

  return (
    <div className="min-h-screen flex">
      {/* Left branding panel */}
      <div className="hidden lg:flex lg:w-[45%] relative flex-col justify-between p-12 overflow-hidden bg-[#0f172a]">
        <div className="absolute -top-32 -left-32 w-[480px] h-[480px] rounded-full bg-blue-600/20 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-0 w-[380px] h-[380px] rounded-full bg-violet-600/20 blur-3xl pointer-events-none" />
        <div className="relative z-10 flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-blue-500 flex items-center justify-center shadow-lg shadow-blue-500/30">
            <BuildingLibraryIcon className="w-6 h-6 text-white" />
          </div>
          <span className="text-white text-xl font-bold tracking-tight">Hotel PMS</span>
        </div>
        <div className="relative z-10">
          <div className="w-16 h-16 rounded-2xl bg-violet-500/20 border border-violet-500/30 flex items-center justify-center mb-6">
            <ShieldCheckIcon className="w-8 h-8 text-violet-400" />
          </div>
          <h2 className="text-3xl font-bold text-white mb-3">Two-Factor Authentication</h2>
          <p className="text-slate-400 text-base leading-relaxed">
            Your account is protected with an extra layer of security.
          </p>
        </div>
        <p className="relative z-10 text-slate-500 text-sm">© {new Date().getFullYear()} Hotel PMS</p>
      </div>

      {/* Right form panel */}
      <div className="flex-1 flex items-center justify-center p-8 bg-slate-50">
        <div className="w-full max-w-md">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-violet-100 mb-4">
              <ShieldCheckIcon className="w-7 h-7 text-violet-600" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900">Verify your identity</h1>
            <p className="text-slate-500 mt-2 text-sm">
              Enter the 6-digit code sent to {methodLabel[method] ?? 'your device'}.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-slate-100 shadow-sm p-8 space-y-5">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                Verification Code
              </label>
              <input
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                maxLength={6}
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                placeholder="000000"
                required
                autoFocus
                className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-center text-2xl font-mono tracking-widest focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent"
              />
            </div>

            <button
              type="submit"
              disabled={loading || code.length < 6}
              className="w-full bg-violet-600 hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-2.5 rounded-xl transition-colors"
            >
              {loading ? 'Verifying…' : 'Verify & Sign In'}
            </button>

            <div className="text-center">
              <a href="/login" className="text-sm text-slate-500 hover:text-slate-700">
                ← Back to login
              </a>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function MFALoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><div className="text-slate-500">Loading…</div></div>}>
      <MFAForm />
    </Suspense>
  );
}
