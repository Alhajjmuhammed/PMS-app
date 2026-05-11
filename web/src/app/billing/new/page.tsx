'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import api from '@/lib/api';
import clsx from 'clsx';
import {
  HomeIcon, ChevronRightIcon, CheckCircleIcon, DocumentPlusIcon, ArrowLeftIcon,
} from '@heroicons/react/24/outline';

interface Guest {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
}

const FOLIO_TYPES = [
  { value: 'GUEST', label: 'Guest' },
  { value: 'MASTER', label: 'Master' },
  { value: 'GROUP', label: 'Group' },
  { value: 'COMPANY', label: 'Company' },
];

export default function NewFolioPage() {
  const router = useRouter();
  const [guests, setGuests] = useState<Guest[]>([]);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const [form, setForm] = useState({
    folio_type: 'GUEST',
    guest: '',
    billing_address: '',
    notes: '',
  });

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  };

  useEffect(() => {
    api.get('/api/v1/guests/')
      .then(r => setGuests(r.data.results ?? r.data))
      .catch(() => showToast('Failed to load guests', false));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.guest) { showToast('Select a guest', false); return; }
    setLoading(true);
    try {
      const resp = await api.post('/api/v1/billing/folios/', {
        folio_type: form.folio_type,
        guest: parseInt(form.guest),
        billing_address: form.billing_address || '',
        notes: form.notes || '',
      });
      showToast('Folio created');
      setTimeout(() => router.push(`/billing/${resp.data.id}`), 1000);
    } catch (e: any) {
      showToast(
        e?.response?.data?.error ||
        JSON.stringify(e?.response?.data) ||
        'Failed to create folio',
        false
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="p-5 lg:p-6 space-y-5 max-w-xl">

        {toast && (
          <div className={clsx(
            'fixed top-5 right-5 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium',
            toast.ok ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white'
          )}>
            <CheckCircleIcon className="w-5 h-5 flex-shrink-0" />
            {toast.msg}
          </div>
        )}

        <nav className="flex items-center gap-1.5 text-sm text-slate-400">
          <HomeIcon className="w-4 h-4" />
          <span>Home</span>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <button onClick={() => router.push('/billing')} className="hover:text-slate-700">Billing</button>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <span className="text-slate-700 font-medium">New Folio</span>
        </nav>

        <div className="flex items-center gap-3">
          <button onClick={() => router.back()} className="p-2 rounded-xl text-slate-400 hover:bg-slate-100">
            <ArrowLeftIcon className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-violet-100 flex items-center justify-center">
              <DocumentPlusIcon className="w-5 h-5 text-violet-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">New Folio</h1>
              <p className="text-slate-500 text-sm">Create a guest billing folio</p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 space-y-4">

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Guest *</label>
              <select value={form.guest} required
                onChange={e => setForm(f => ({ ...f, guest: e.target.value }))}
                className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300">
                <option value="">Select a guest...</option>
                {guests.map(g => (
                  <option key={g.id} value={g.id}>
                    {g.first_name} {g.last_name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Folio Type</label>
              <select value={form.folio_type}
                onChange={e => setForm(f => ({ ...f, folio_type: e.target.value }))}
                className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300">
                {FOLIO_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">Billing Address</label>
            <input value={form.billing_address}
              onChange={e => setForm(f => ({ ...f, billing_address: e.target.value }))}
              placeholder="Optional billing address"
              className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">Notes</label>
            <textarea rows={3} value={form.notes}
              onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
              placeholder="Internal notes..."
              className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 resize-none" />
          </div>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={() => router.back()}
              className="px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-700">
              Cancel
            </button>
            <button type="submit" disabled={loading}
              className="px-6 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-700 text-white text-sm font-semibold disabled:opacity-50">
              {loading ? 'Creating...' : 'Create Folio'}
            </button>
          </div>

        </form>

      </div>
    </Layout>
  );
}
