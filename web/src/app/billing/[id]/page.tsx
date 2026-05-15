'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import api from '@/lib/api';
import { format } from 'date-fns';
import clsx from 'clsx';
import {
  HomeIcon, ChevronRightIcon, CheckCircleIcon, ExclamationTriangleIcon, CreditCardIcon,
  DocumentArrowDownIcon, ArrowLeftIcon,
} from '@heroicons/react/24/outline';

interface Charge {
  id: number;
  charge_code: number;
  charge_code_name: string;
  description: string;
  quantity: string;
  unit_price: string;
  amount: string;
  charge_date: string;
}
interface Payment {
  id: number;
  payment_method: string;
  amount: string;
  reference: string;
  card_last_four: string;
  payment_date: string;
  status: string;
}
interface Folio {
  id: number;
  folio_number: string;
  folio_type: string;
  status: string;
  guest_name: string;
  room_number: string;
  total_charges: string;
  total_taxes: string;
  total_payments: string;
  balance: string;
  open_date: string;
  close_date: string | null;
  charges: Charge[];
  payments: Payment[];
}

const PAYMENT_METHODS: Record<string, string> = {
  CASH: 'Cash', CREDIT_CARD: 'Credit Card', DEBIT_CARD: 'Debit Card',
  BANK_TRANSFER: 'Bank Transfer', CITY_LEDGER: 'City Ledger',
  VOUCHER: 'Voucher', LOYALTY: 'Loyalty Points',
};

export default function FolioDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [folio, setFolio] = useState<Folio | null>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);

  // Add Charge state
  const [showChargeForm, setShowChargeForm] = useState(false);
  const [chargeCodes, setChargeCodes] = useState<any[]>([]);
  const [chargeForm, setChargeForm] = useState({ charge_code_id: '', description: '', quantity: '1', unit_price: '' });
  const [savingCharge, setSavingCharge] = useState(false);

  // Add Payment state
  const [showPayForm, setShowPayForm] = useState(false);
  const [payForm, setPayForm] = useState({ amount: '', payment_method: 'CASH', reference_number: '' });
  const [savingPay, setSavingPay] = useState(false);

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  };

  const load = async () => {
    try {
      setLoading(true);
      const resp = await api.get(`/api/v1/billing/folios/${params.id}/`);
      setFolio(resp.data);
    } catch {
      showToast('Failed to load folio', false);
    } finally {
      setLoading(false);
    }
  };

  const loadCodes = async () => {
    try {
      const resp = await api.get('/api/v1/billing/charge-codes/');
      setChargeCodes(resp.data.results ?? resp.data);
    } catch {}
  };

  useEffect(() => {
    if (params.id) { load(); loadCodes(); }
  }, [params.id]);

  const handleAddCharge = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chargeForm.charge_code_id || !chargeForm.unit_price) return;
    setSavingCharge(true);
    try {
      await api.post(`/api/v1/billing/folios/${params.id}/add-charge/`, {
        charge_code_id: parseInt(chargeForm.charge_code_id),
        description: chargeForm.description || undefined,
        quantity: parseInt(chargeForm.quantity),
        unit_price: chargeForm.unit_price,
      });
      showToast('Charge added');
      setChargeForm({ charge_code_id: '', description: '', quantity: '1', unit_price: '' });
      setShowChargeForm(false);
      await load();
    } catch (e: any) {
      showToast(e?.response?.data?.error || 'Failed to add charge', false);
    } finally {
      setSavingCharge(false);
    }
  };

  const handleAddPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!payForm.amount) return;
    setSavingPay(true);
    try {
      await api.post(`/api/v1/billing/folios/${params.id}/payments/`, {
        amount: payForm.amount,
        payment_method: payForm.payment_method,
        reference_number: payForm.reference_number || '',
      });
      showToast('Payment recorded');
      setPayForm({ amount: '', payment_method: 'CASH', reference_number: '' });
      setShowPayForm(false);
      await load();
    } catch (e: any) {
      showToast(e?.response?.data?.error || 'Failed to record payment', false);
    } finally {
      setSavingPay(false);
    }
  };

  const handleCloseFolio = async () => {
    if (!folio) return;
    if (Number(folio.balance) > 0) {
      showToast(`Cannot close — outstanding balance $${Number(folio.balance).toLocaleString()}`, false);
      return;
    }
    if (!confirm('Close this folio? This cannot be undone.')) return;
    try {
      await api.post(`/api/v1/billing/folios/${params.id}/close/`);
      showToast('Folio closed');
      await load();
    } catch (e: any) {
      showToast(e?.response?.data?.error || 'Failed to close folio', false);
    }
  };

  const handleExport = async () => {
    try {
      const resp = await api.get(`/api/v1/billing/folios/${params.id}/export/`, {
        responseType: 'blob',
      });
      const url = URL.createObjectURL(new Blob([resp.data], { type: 'application/pdf' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = `folio-${folio?.folio_number ?? params.id}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      showToast('Export failed', false);
    }
  };

  if (loading) return (
    <Layout>
      <div className="flex items-center justify-center py-32">
        <div className="w-10 h-10 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    </Layout>
  );

  if (!folio) return (
    <Layout><div className="p-6 text-slate-500">Folio not found.</div></Layout>
  );

  const balance = Number(folio.balance);
  const isClosed = folio.status === 'CLOSED';

  return (
    <Layout>
      <div className="p-5 lg:p-6 space-y-5">

        {/* Toast */}
        {toast && (
          <div className={clsx('fixed top-5 right-5 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium',
            toast.ok ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white')}>
            {toast.ok ? <CheckCircleIcon className="w-5 h-5 flex-shrink-0" /> : <ExclamationTriangleIcon className="w-5 h-5 flex-shrink-0" />}
            {toast.msg}
          </div>
        )}

        {/* Breadcrumb */}
        <nav className="flex items-center gap-1.5 text-sm text-slate-400">
          <HomeIcon className="w-4 h-4" />
          <span>Home</span>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <button onClick={() => router.push('/billing')} className="hover:text-slate-700">Billing</button>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <span className="text-slate-700 font-medium">{folio.folio_number}</span>
        </nav>

        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <button onClick={() => router.push('/billing')} className="p-2 rounded-xl text-slate-400 hover:bg-slate-100">
              <ArrowLeftIcon className="w-5 h-5" />
            </button>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold text-slate-900">{folio.folio_number}</h1>
                <span className={clsx('inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border',
                  isClosed ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-blue-50 text-blue-700 border-blue-200')}>
                  {folio.status}
                </span>
              </div>
              <p className="text-slate-500 text-sm mt-0.5">
                {folio.guest_name}{folio.room_number ? ` · Room ${folio.room_number}` : ''} · Opened {format(new Date(folio.open_date), 'MMM d, yyyy')}
              </p>
            </div>
          </div>
          <div className="flex gap-2 flex-wrap">
            <button onClick={handleExport}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border border-slate-200 bg-white text-sm font-semibold text-slate-700 hover:bg-slate-50">
              <DocumentArrowDownIcon className="w-4 h-4" /> Export PDF
            </button>
            {!isClosed && (
              <>
                <button onClick={() => setShowChargeForm(v => !v)}
                  className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border border-slate-200 bg-white text-sm font-semibold text-slate-700 hover:bg-slate-50">
                  + Add Charge
                </button>
                <button onClick={() => setShowPayForm(v => !v)}
                  className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold">
                  <CreditCardIcon className="w-4 h-4" /> Add Payment
                </button>
                <button onClick={handleCloseFolio}
                  className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-700 hover:bg-slate-800 text-white text-sm font-semibold">
                  Close Folio
                </button>
              </>
            )}
          </div>
        </div>

        {/* Balance summary */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: 'Charges', value: `$${Number(folio.total_charges).toLocaleString()}`, color: 'text-slate-800' },
            { label: 'Taxes', value: `$${Number(folio.total_taxes).toLocaleString()}`, color: 'text-slate-800' },
            { label: 'Payments', value: `$${Number(folio.total_payments).toLocaleString()}`, color: 'text-emerald-600' },
            { label: 'Balance', value: `$${balance.toLocaleString()}`, color: balance > 0 ? 'text-red-600' : 'text-emerald-600' },
          ].map(({ label, value, color }) => (
            <div key={label} className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-4">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</p>
              <p className={clsx('text-2xl font-bold mt-1', color)}>{value}</p>
            </div>
          ))}
        </div>

        {/* Add Charge inline form */}
        {showChargeForm && (
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
            <h3 className="font-semibold text-slate-800 mb-4">Add Charge</h3>
            <form onSubmit={handleAddCharge} className="grid grid-cols-1 sm:grid-cols-4 gap-3">
              <select value={chargeForm.charge_code_id}
                onChange={e => setChargeForm(f => ({ ...f, charge_code_id: e.target.value }))}
                className="px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
                required>
                <option value="">Charge Code…</option>
                {chargeCodes.map(c => <option key={c.id} value={c.id}>{c.code} — {c.name}</option>)}
              </select>
              <input placeholder="Description (optional)" value={chargeForm.description}
                onChange={e => setChargeForm(f => ({ ...f, description: e.target.value }))}
                className="px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
              <input type="number" min="1" placeholder="Qty" value={chargeForm.quantity}
                onChange={e => setChargeForm(f => ({ ...f, quantity: e.target.value }))}
                className="px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" required />
              <input type="number" min="0" step="0.01" placeholder="Unit Price" value={chargeForm.unit_price}
                onChange={e => setChargeForm(f => ({ ...f, unit_price: e.target.value }))}
                className="px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" required />
              <div className="sm:col-span-4 flex gap-2 justify-end">
                <button type="button" onClick={() => setShowChargeForm(false)}
                  className="px-4 py-2 rounded-xl border border-slate-200 text-sm text-slate-600">Cancel</button>
                <button type="submit" disabled={savingCharge}
                  className="px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 text-white text-sm font-semibold disabled:opacity-50">
                  {savingCharge ? 'Saving…' : 'Add Charge'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Add Payment inline form */}
        {showPayForm && (
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
            <h3 className="font-semibold text-slate-800 mb-4">Record Payment</h3>
            <form onSubmit={handleAddPayment} className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <input type="number" min="0.01" step="0.01" placeholder={`Amount (balance: $${balance})`}
                value={payForm.amount}
                onChange={e => setPayForm(f => ({ ...f, amount: e.target.value }))}
                className="px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" required />
              <select value={payForm.payment_method}
                onChange={e => setPayForm(f => ({ ...f, payment_method: e.target.value }))}
                className="px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300">
                {Object.entries(PAYMENT_METHODS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
              <input placeholder="Reference # (optional)" value={payForm.reference_number}
                onChange={e => setPayForm(f => ({ ...f, reference_number: e.target.value }))}
                className="px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
              <div className="sm:col-span-3 flex gap-2 justify-end">
                <button type="button" onClick={() => setShowPayForm(false)}
                  className="px-4 py-2 rounded-xl border border-slate-200 text-sm text-slate-600">Cancel</button>
                <button type="submit" disabled={savingPay}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold disabled:opacity-50">
                  {savingPay ? 'Saving…' : 'Record Payment'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Two-column: charges + payments */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

          {/* Charges (2/3) */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100">
              <h2 className="font-semibold text-slate-800">Charges <span className="text-slate-400 text-sm font-normal">({folio.charges.length})</span></h2>
            </div>
            {folio.charges.length === 0 ? (
              <div className="py-12 text-center text-slate-400 text-sm">No charges posted yet</div>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50/60 border-b border-slate-100">
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Date</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Description</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Qty</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Amount</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {folio.charges.map(c => (
                    <tr key={c.id}>
                      <td className="px-4 py-3 text-slate-400 text-xs">{c.charge_date}</td>
                      <td className="px-4 py-3 text-slate-700">{c.description}</td>
                      <td className="px-4 py-3 text-right text-slate-500">{Number(c.quantity)}</td>
                      <td className="px-4 py-3 text-right font-medium text-slate-800">${Number(c.amount).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="border-t border-slate-200 bg-slate-50/60">
                    <td colSpan={3} className="px-4 py-3 text-sm font-bold text-slate-700 text-right">Total Charges</td>
                    <td className="px-4 py-3 text-right font-bold text-slate-900">${Number(folio.total_charges).toLocaleString()}</td>
                  </tr>
                </tfoot>
              </table>
            )}
          </div>

          {/* Payments (1/3) */}
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100">
              <h2 className="font-semibold text-slate-800">Payments <span className="text-slate-400 text-sm font-normal">({folio.payments.length})</span></h2>
            </div>
            {folio.payments.length === 0 ? (
              <div className="py-12 text-center text-slate-400 text-sm">No payments recorded</div>
            ) : (
              <ul className="divide-y divide-slate-50">
                {folio.payments.map(p => (
                  <li key={p.id} className="px-5 py-3 flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-800">{PAYMENT_METHODS[p.payment_method] ?? p.payment_method}</p>
                      <p className="text-xs text-slate-400">{format(new Date(p.payment_date), 'MMM d, yyyy HH:mm')}</p>
                      {p.reference && <p className="text-xs text-slate-400">Ref: {p.reference}</p>}
                    </div>
                    <span className="font-bold text-emerald-600">${Number(p.amount).toLocaleString()}</span>
                  </li>
                ))}
              </ul>
            )}
            <div className="px-5 py-3 border-t border-slate-100 flex justify-between items-center">
              <span className="text-sm font-bold text-slate-700">Total Paid</span>
              <span className="font-bold text-emerald-600">${Number(folio.total_payments).toLocaleString()}</span>
            </div>
          </div>

        </div>

      </div>
    </Layout>
  );
}
