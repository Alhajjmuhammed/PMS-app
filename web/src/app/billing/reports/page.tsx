'use client';

import { useState } from 'react';
import Layout from '@/components/Layout';
import api from '@/lib/api';
import { format, subMonths } from 'date-fns';
import clsx from 'clsx';
import {
  HomeIcon, ChevronRightIcon, CheckCircleIcon, ExclamationTriangleIcon, ChartBarIcon,
} from '@heroicons/react/24/outline';

interface RevenueDay {
  date: string;
  room_revenue: number;
  fb_revenue: number;
  other_revenue: number;
  total: number;
}

export default function BillingReportsPage() {
  const [loading, setLoading] = useState(false);
  const [rows, setRows] = useState<RevenueDay[]>([]);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const [dates, setDates] = useState({
    start: format(subMonths(new Date(), 1), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  };

  const generate = async () => {
    setLoading(true);
    try {
      const resp = await api.get('/api/v1/reports/revenue/', { params: { start: dates.start, end: dates.end } });
      setRows(resp.data.data ?? resp.data.results ?? resp.data);
    } catch {
      showToast('Failed to generate report', false);
    } finally {
      setLoading(false);
    }
  };

  const totals = rows.reduce((acc, r) => ({
    room: acc.room + Number(r.room_revenue),
    fb: acc.fb + Number(r.fb_revenue),
    other: acc.other + Number(r.other_revenue),
    total: acc.total + Number(r.total),
  }), { room: 0, fb: 0, other: 0, total: 0 });

  return (
    <Layout>
      <div className="p-5 lg:p-6 space-y-5">

        {toast && (
          <div className={clsx('fixed top-5 right-5 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium',
            toast.ok ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white')}>
            {toast.ok ? <CheckCircleIcon className="w-5 h-5 flex-shrink-0" /> : <ExclamationTriangleIcon className="w-5 h-5 flex-shrink-0" />}
            {toast.msg}
          </div>
        )}

        <nav className="flex items-center gap-1.5 text-sm text-slate-400">
          <HomeIcon className="w-4 h-4" />
          <span>Home</span>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <span className="text-slate-700 font-medium">Billing Reports</span>
        </nav>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-violet-100 flex items-center justify-center">
            <ChartBarIcon className="w-5 h-5 text-violet-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Revenue Reports</h1>
            <p className="text-slate-500 text-sm">Daily breakdown by revenue category</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
          <div className="flex flex-wrap gap-3 items-end">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">From</label>
              <input type="date" value={dates.start}
                onChange={e => setDates(d => ({ ...d, start: e.target.value }))}
                className="px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">To</label>
              <input type="date" value={dates.end}
                onChange={e => setDates(d => ({ ...d, end: e.target.value }))}
                className="px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
            </div>
            <button onClick={generate} disabled={loading}
              className="px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-700 text-white text-sm font-semibold disabled:opacity-50">
              {loading ? 'Loading...' : 'Generate Report'}
            </button>
          </div>
        </div>

        {rows.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: 'Room Revenue', value: totals.room, color: 'text-blue-600' },
              { label: 'F&B Revenue', value: totals.fb, color: 'text-amber-600' },
              { label: 'Other Revenue', value: totals.other, color: 'text-slate-700' },
              { label: 'Total Revenue', value: totals.total, color: 'text-violet-600' },
            ].map(({ label, value, color }) => (
              <div key={label} className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-4">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</p>
                <p className={clsx('text-2xl font-bold mt-1', color)}>${value.toLocaleString()}</p>
              </div>
            ))}
          </div>
        )}

        {rows.length > 0 && (
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100">
              <h2 className="font-semibold text-slate-800">Daily Breakdown</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50/60 border-b border-slate-100">
                    {['Date', 'Room Revenue', 'F&B Revenue', 'Other', 'Total'].map(h => (
                      <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {rows.map((r, i) => (
                    <tr key={i} className="hover:bg-slate-50/50">
                      <td className="px-4 py-3 text-slate-600 font-medium">{format(new Date(r.date), 'MMM d, yyyy')}</td>
                      <td className="px-4 py-3 text-blue-600">${Number(r.room_revenue).toLocaleString()}</td>
                      <td className="px-4 py-3 text-amber-600">${Number(r.fb_revenue).toLocaleString()}</td>
                      <td className="px-4 py-3 text-slate-600">${Number(r.other_revenue).toLocaleString()}</td>
                      <td className="px-4 py-3 font-bold text-violet-700">${Number(r.total).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="border-t border-slate-200 bg-slate-50/60">
                    <td className="px-4 py-3 font-bold text-slate-700">Totals</td>
                    <td className="px-4 py-3 font-bold text-blue-600">${totals.room.toLocaleString()}</td>
                    <td className="px-4 py-3 font-bold text-amber-600">${totals.fb.toLocaleString()}</td>
                    <td className="px-4 py-3 font-bold text-slate-700">${totals.other.toLocaleString()}</td>
                    <td className="px-4 py-3 font-bold text-violet-700">${totals.total.toLocaleString()}</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        )}

        {rows.length === 0 && !loading && (
          <div className="text-center py-20 text-slate-400">
            <ChartBarIcon className="w-14 h-14 mx-auto mb-3 opacity-30" />
            <p className="font-medium">Select a date range and click Generate Report</p>
          </div>
        )}

      </div>
    </Layout>
  );
}
