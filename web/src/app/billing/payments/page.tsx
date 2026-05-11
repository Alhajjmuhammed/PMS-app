'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Layout from '@/components/Layout';
import api from '@/lib/api';
import clsx from 'clsx';
import {
  HomeIcon, ChevronRightIcon, CheckCircleIcon, CreditCardIcon, ArrowLeftIcon,
} from '@heroicons/react/24/outline';

interface Folio {
  id: number;
  folio_number: string;
  guest_name: string;
  room_number: string;
  balance: string;
  status: string;
}

const PAYMENT_METHODS = [
  { value: 'CASH', label: 'Cash' },
  { value: 'CREDIT_CARD', label: 'Credit Card' },
  { value: 'DEBIT_CARD', label: 'Debit Card' },
  { value: 'BANK_TRANSFER', label: 'Bank Transfer' },
  { value: 'CITY_LEDGER', label: 'City Ledger' },
  { value: 'VOUCHER', label: 'Voucher' },
];

const CARD_METHODS = ['CREDIT_CARD', 'DEBIT_CARD'];

function PaymentForm() {
  const router = useRouter();
  const params = useSearchParams();
  const folioId = params.get('folio_id');
  const [folio, setFolio] = useState<Folio | null>(null);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const [form, setForm] = useState({
    amount: '',
    payment_method: 'CASH',
    reference_number: '',
    card_last_four: '',
  });

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  };

  useEffect(() => {
    if (!folioId) return;
    setFetching(true);
    api.get(`/api/v1/billing/folios/${folioId}/`)
      .then(r => setFolio(r.data))
      .catch(() => showToast('Failed to load folio', false))
      .finally(() => setFetching(false));
  }, [folioId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!folioId) { showToast('No folio selected', false); return; }
    setLoading(true);
    try {
      const payload: Record<string, unknown> = {
        amount: parseFloat(form.amount),
        payment_method: form.payment_method,
      };
      if (form.reference_number) payload.reference_number = form.reference_number;
      if (CARD_METHODS.includes(form.payment_method) && form.card_last_four)
        payload.card_last_four = form.card_last_four;

      await api.post(`/api/v1/billing/folios/${folioId}/payments/`, payload);
      showToast('Payment recorded successfully');
      setTimeout(() => router.push(`/billing/${folioId}`), 1200);
    } catch (e: any) {
      showToast(
        e?.response?.data?.error ||
        JSON.stringify(e?.response?.data) ||
        'Payment failed',
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
          {folioId && (
            <>
              <button onClick={() => router.push(`/billing/${folioId}`)} className="hover:text-slate-700">
                Folio #{folioId}
              </button>
              <ChevronRightIcon className="w-3.5 h-3.5" />
            </>
          )}
          <span className="text-slate-700 font-medium">Record Payment</span>
        </nav>

        <div className="flex items-center gap-3">
          <button onClick={() => folioId ? router.push(`/billing/${folioId}`) : router.back()}
            className="p-2 rounded-xl text-slate-400 hover:bg-slate-100">
            <ArrowLeftIcon className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
              <CreditCardIcon className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Record Payment</h1>
              <p className="text-slate-500 text-sm">Apply a payment to folio</p>
            </div>
          </div>
        </div>

        {!folioId ? (
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-8 text-center text-slate-400">
            No folio selected. Use <code>?folio_id=X</code> to specify a folio.
          </div>
        ) : fetching ? (
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-8 text-center text-slate-400">
            Loading folio...
          </div>
        ) : (
          <>
            {folio && (
              <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">Folio</p>
                    <p className="font-semibold text-slate-900">{folio.folio_number}</p>
                    <p className="text-sm text-slate-500 mt-0.5">{folio.guest_name} · Room {folio.room_number}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">Balance</p>
                    <p className={clsx(
                      'text-xl font-bold',
                      parseFloat(folio.balance) > 0 ? 'text-red-600' : 'text-emerald-600'
                    )}>
                      ${parseFloat(folio.balance).toFixed(2)}
                    </p>
                  </div>
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 space-y-4">

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Amount *</label>
                  <input
                    type="number" min="0.01" step="0.01" required
                    value={form.amount}
                    onChange={e => setForm(f => ({ ...f, amount: e.target.value }))}
                    placeholder="0.00"
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Payment Method</label>
                  <select value={form.payment_method}
                    onChange={e => setForm(f => ({ ...f, payment_method: e.target.value }))}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300">
                    {PAYMENT_METHODS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Reference Number</label>
                <input value={form.reference_number}
                  onChange={e => setForm(f => ({ ...f, reference_number: e.target.value }))}
                  placeholder="Optional transaction reference"
                  className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300" />
              </div>

              {CARD_METHODS.includes(form.payment_method) && (
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Card Last 4 Digits</label>
                  <input
                    maxLength={4} pattern="\d{4}"
                    value={form.card_last_four}
                    onChange={e => setForm(f => ({ ...f, card_last_four: e.target.value }))}
                    placeholder="1234"
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300" />
                </div>
              )}

              <div className="flex gap-3 pt-2">
                <button type="button"
                  onClick={() => folioId ? router.push(`/billing/${folioId}`) : router.back()}
                  className="px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-700">
                  Cancel
                </button>
                <button type="submit" disabled={loading}
                  className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold disabled:opacity-50">
                  {loading ? 'Processing...' : 'Record Payment'}
                </button>
              </div>

            </form>
          </>
        )}

      </div>
    </Layout>
  );
}

export default function PaymentsPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-slate-400">Loading...</div>}>
      <PaymentForm />
    </Suspense>
  );
}
