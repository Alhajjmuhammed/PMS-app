'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import api from '@/lib/api';
import { format, subDays } from 'date-fns';
import clsx from 'clsx';
import {
  HomeIcon, ChevronRightIcon, CheckCircleIcon, BuildingOfficeIcon, ArrowLeftIcon,
} from '@heroicons/react/24/outline';

interface OccRow { date: string; occupancy: number; adr: number; revpar: number; rooms_sold: number; }
interface OccAverages { occupancy: number; adr: number; revpar: number; }

export default function OccupancyReportPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [hasGenerated, setHasGenerated] = useState(false);
  const [rows, setRows] = useState<OccRow[]>([]);
  const [averages, setAverages] = useState<OccAverages | null>(null);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const [dates, setDates] = useState({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  };

  const generate = async () => {
    setLoading(true);
    try {
      const resp = await api.get('/api/v1/reports/occupancy/', {
        params: { start: dates.start, end: dates.end },
      });
      setRows(resp.data.data ?? []);
      setAverages(resp.data.averages ?? null);
    } catch {
      showToast('Failed to generate occupancy report', false);
    } finally {
      setLoading(false);
      setHasGenerated(true);
    }
  };

  return (
    <Layout>
      <div className="p-5 lg:p-6 space-y-5">

        {toast && (
          <div className={clsx('fixed top-5 right-5 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium',
            toast.ok ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white')}>
            <CheckCircleIcon className="w-5 h-5 flex-shrink-0" />
            {toast.msg}
          </div>
        )}

        <nav className="flex items-center gap-1.5 text-sm text-slate-400">
          <HomeIcon className="w-4 h-4" />
          <span>Home</span>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <button onClick={() => router.push('/reports')} className="hover:text-slate-700">Reports</button>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <span className="text-slate-700 font-medium">Occupancy</span>
        </nav>

        <div className="flex items-center gap-3">
          <button onClick={() => router.push('/reports')} className="p-2 rounded-xl text-slate-400 hover:bg-slate-100">
            <ArrowLeftIcon className="w-5 h-5" />
          </button>
          <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
            <BuildingOfficeIcon className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Occupancy Report</h1>
            <p className="text-slate-500 text-sm">Room occupancy, ADR and RevPAR trends</p>
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
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold disabled:opacity-50">
              {loading ? 'Loading…' : 'Generate Report'}
            </button>
          </div>
        </div>

        {rows.length > 0 && averages && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { label: 'Avg Occupancy', value: `${Number(averages.occupancy).toFixed(1)}%`, color: 'text-blue-600' },
              { label: 'Avg ADR',       value: `$${Number(averages.adr).toLocaleString()}`,   color: 'text-violet-600' },
              { label: 'Avg RevPAR',    value: `$${Number(averages.revpar).toLocaleString()}`, color: 'text-emerald-600' },
            ].map(({ label, value, color }) => (
              <div key={label} className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-4">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</p>
                <p className={clsx('text-2xl font-bold mt-1', color)}>{value}</p>
              </div>
            ))}
          </div>
        )}

        {rows.length > 0 && (
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100">
              <h2 className="font-semibold text-slate-800">Daily Trend</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50/60 border-b border-slate-100">
                    {['Date', 'Rooms Sold', 'Occupancy %', 'ADR', 'RevPAR'].map(h => (
                      <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {rows.map((r, i) => (
                    <tr key={i} className="hover:bg-slate-50/50">
                      <td className="px-4 py-3 font-medium text-slate-700">{format(new Date(r.date), 'MMM d, yyyy')}</td>
                      <td className="px-4 py-3 text-slate-600">{r.rooms_sold}</td>
                      <td className="px-4 py-3">
                        <span className={clsx('font-semibold', Number(r.occupancy) >= 80 ? 'text-emerald-600' : Number(r.occupancy) >= 50 ? 'text-amber-600' : 'text-red-500')}>
                          {Number(r.occupancy).toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-4 py-3 text-violet-600">${Number(r.adr).toLocaleString()}</td>
                      <td className="px-4 py-3 text-emerald-600">${Number(r.revpar).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {!loading && rows.length === 0 && (
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm py-16 text-center text-slate-400">
            <BuildingOfficeIcon className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="font-medium">
              {hasGenerated ? 'No occupancy data for this period' : 'Select a date range and click Generate Report'}
            </p>
          </div>
        )}

      </div>
    </Layout>
  );
}
