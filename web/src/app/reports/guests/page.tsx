'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import api from '@/lib/api';
import { format, subDays } from 'date-fns';
import clsx from 'clsx';
import {
  HomeIcon, ChevronRightIcon, CheckCircleIcon, UsersIcon, ArrowLeftIcon,
} from '@heroicons/react/24/outline';

interface GuestData {
  total_guests: number;
  new_guests: number;
  returning_guests: number;
  avg_stay_duration: number;
  total_reservations: number;
  top_nationalities: { country: string; count: number }[];
  by_type: { type: string; count: number }[];
}

export default function GuestReportsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [hasGenerated, setHasGenerated] = useState(false);
  const [data, setData] = useState<GuestData | null>(null);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const [dates, setDates] = useState({
    start_date: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end_date: format(new Date(), 'yyyy-MM-dd'),
  });

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  };

  const generate = async () => {
    setLoading(true);
    try {
      const resp = await api.get('/api/v1/reports/guests/', {
        params: dates,
      });
      setData(resp.data);
    } catch {
      showToast('Failed to generate guest report', false);
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
          <span className="text-slate-700 font-medium">Guests</span>
        </nav>

        <div className="flex items-center gap-3">
          <button onClick={() => router.push('/reports')} className="p-2 rounded-xl text-slate-400 hover:bg-slate-100">
            <ArrowLeftIcon className="w-5 h-5" />
          </button>
          <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
            <UsersIcon className="w-5 h-5 text-emerald-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Guest Report</h1>
            <p className="text-slate-500 text-sm">Guest analytics and stay patterns</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
          <div className="flex flex-wrap gap-3 items-end">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">From</label>
              <input type="date" value={dates.start_date}
                onChange={e => setDates(d => ({ ...d, start_date: e.target.value }))}
                className="px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">To</label>
              <input type="date" value={dates.end_date}
                onChange={e => setDates(d => ({ ...d, end_date: e.target.value }))}
                className="px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-300" />
            </div>
            <button onClick={generate} disabled={loading}
              className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold disabled:opacity-50">
              {loading ? 'Loading…' : 'Generate Report'}
            </button>
          </div>
        </div>

        {data && (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
              {[
                { label: 'Total Guests',       value: data.total_guests,       color: 'text-slate-800' },
                { label: 'New Guests',          value: data.new_guests,         color: 'text-emerald-600' },
                { label: 'Returning',           value: data.returning_guests,   color: 'text-blue-600' },
                { label: 'Reservations',        value: data.total_reservations, color: 'text-violet-600' },
                { label: 'Avg Stay (nights)',   value: Number(data.avg_stay_duration).toFixed(1), color: 'text-amber-600' },
              ].map(({ label, value, color }) => (
                <div key={label} className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-4">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</p>
                  <p className={clsx('text-2xl font-bold mt-1', color)}>{value}</p>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">

              {data.top_nationalities.length > 0 && (
                <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                  <div className="px-6 py-4 border-b border-slate-100">
                    <h2 className="font-semibold text-slate-800">Top Nationalities</h2>
                  </div>
                  <div className="divide-y divide-slate-50">
                    {data.top_nationalities.map((n, i) => (
                      <div key={i} className="flex items-center justify-between px-6 py-3">
                        <span className="text-slate-700">{n.country || 'Unknown'}</span>
                        <span className="text-sm font-semibold text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full">{n.count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {data.by_type.length > 0 && (
                <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                  <div className="px-6 py-4 border-b border-slate-100">
                    <h2 className="font-semibold text-slate-800">By Guest Type</h2>
                  </div>
                  <div className="divide-y divide-slate-50">
                    {data.by_type.map((t, i) => (
                      <div key={i} className="flex items-center justify-between px-6 py-3">
                        <span className="text-slate-700 capitalize">{t.type.toLowerCase()}</span>
                        <span className="text-sm font-semibold text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full">{t.count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          </>
        )}

        {!loading && !data && (
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm py-16 text-center text-slate-400">
            <UsersIcon className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="font-medium">
              {hasGenerated ? 'No guest data for this period' : 'Select a date range and click Generate Report'}
            </p>
          </div>
        )}

      </div>
    </Layout>
  );
}
