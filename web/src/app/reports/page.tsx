'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import api from '@/lib/api';
import { format, subDays } from 'date-fns';
import clsx from 'clsx';
import {
  HomeIcon, ChevronRightIcon, ChartBarIcon, CheckCircleIcon,
  CurrencyDollarIcon, UsersIcon, BuildingOfficeIcon,
  DocumentChartBarIcon, ArrowTrendingUpIcon, TableCellsIcon,
} from '@heroicons/react/24/outline';

export default function ReportsPage() {
  const router = useRouter();
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const [dateRange, setDateRange] = useState({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  };

  useEffect(() => { load(); }, [dateRange]);

  const load = async () => {
    try {
      setLoading(true);
      const resp = await api.get('/api/v1/reports/summary/', {
        params: { start: dateRange.start, end: dateRange.end },
      });
      setSummary(resp.data);
    } catch {
      showToast('Failed to load summary', false);
    } finally {
      setLoading(false);
    }
  };

  const today = summary?.today ?? {};
  const period = summary?.period ?? {};

  const reportLinks = [
    { href: '/reports/revenue',   icon: CurrencyDollarIcon,   label: 'Revenue Report',   desc: 'Daily revenue by category', color: 'bg-violet-100 text-violet-600' },
    { href: '/reports/occupancy', icon: BuildingOfficeIcon,    label: 'Occupancy Report', desc: 'Room occupancy & ADR trends', color: 'bg-blue-100 text-blue-600' },
    { href: '/reports/guests',    icon: UsersIcon,             label: 'Guest Analytics',  desc: 'Guest behaviour & demographics', color: 'bg-emerald-100 text-emerald-600' },
    { href: '/reports/export',    icon: TableCellsIcon,        label: 'Export Center',    desc: 'Download CSV / JSON reports', color: 'bg-amber-100 text-amber-600' },
  ];

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

        {/* Breadcrumb */}
        <nav className="flex items-center gap-1.5 text-sm text-slate-400">
          <HomeIcon className="w-4 h-4" />
          <span>Home</span>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <span className="text-slate-700 font-medium">Reports</span>
        </nav>

        {/* Header + date range */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-violet-100 flex items-center justify-center flex-shrink-0">
              <ChartBarIcon className="w-5 h-5 text-violet-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Reports & Analytics</h1>
              <p className="text-slate-500 text-sm mt-0.5">Overview for selected period</p>
            </div>
          </div>
          <div className="flex gap-2 items-end flex-wrap">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">From</label>
              <input type="date" value={dateRange.start}
                onChange={e => setDateRange(d => ({ ...d, start: e.target.value }))}
                className="px-3 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-300" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">To</label>
              <input type="date" value={dateRange.end}
                onChange={e => setDateRange(d => ({ ...d, end: e.target.value }))}
                className="px-3 py-2 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-violet-300" />
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-10 h-10 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <>
            {/* Today snapshot */}
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Today — {format(new Date(), 'MMMM d, yyyy')}</p>
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
                {[
                  { label: 'Total Rooms',   value: today.total_rooms ?? '—',             color: 'text-slate-800' },
                  { label: 'Occupied',      value: today.occupied ?? '—',                color: 'text-blue-600' },
                  { label: 'Available',     value: today.available ?? '—',               color: 'text-emerald-600' },
                  { label: 'Occupancy',     value: `${today.occupancy_percent ?? 0}%`,   color: 'text-violet-600' },
                  { label: 'Arrivals',      value: today.arrivals ?? 0,                  color: 'text-amber-600' },
                  { label: 'Departures',    value: today.departures ?? 0,                color: 'text-red-500' },
                  { label: "Today's Rev",   value: `$${Number(today.revenue ?? 0).toLocaleString()}`, color: 'text-violet-700' },
                ].map(({ label, value, color }) => (
                  <div key={label} className="bg-white rounded-2xl border border-slate-100 shadow-sm px-4 py-3">
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</p>
                    <p className={clsx('text-xl font-bold mt-1', color)}>{value}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Period summary */}
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                Period — {period.start} → {period.end}
              </p>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3">
                {[
                  { label: 'Total Revenue',  value: `$${Number(period.total_revenue ?? 0).toLocaleString()}`,    color: 'text-violet-700' },
                  { label: 'Room Revenue',   value: `$${Number(period.room_revenue ?? 0).toLocaleString()}`,     color: 'text-blue-600' },
                  { label: 'F&B Revenue',    value: `$${Number(period.fb_revenue ?? 0).toLocaleString()}`,       color: 'text-amber-600' },
                  { label: 'Other Revenue',  value: `$${Number(period.other_revenue ?? 0).toLocaleString()}`,    color: 'text-slate-700' },
                  { label: 'Reservations',   value: period.total_reservations ?? 0,                              color: 'text-emerald-600' },
                  { label: 'Avg Occupancy',  value: `${period.avg_occupancy ?? 0}%`,                            color: 'text-violet-600' },
                  { label: 'Avg ADR',        value: `$${Number(period.avg_adr ?? 0).toLocaleString()}`,          color: 'text-blue-700' },
                ].map(({ label, value, color }) => (
                  <div key={label} className="bg-white rounded-2xl border border-slate-100 shadow-sm px-4 py-3">
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</p>
                    <p className={clsx('text-xl font-bold mt-1', color)}>{value}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Report links */}
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Detailed Reports</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {reportLinks.map(({ href, icon: Icon, label, desc, color }) => (
                  <button key={href} onClick={() => router.push(href)}
                    className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 text-left hover:shadow-md hover:border-slate-200 transition-all group">
                    <div className={clsx('w-10 h-10 rounded-xl flex items-center justify-center mb-3', color)}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <p className="font-semibold text-slate-800 group-hover:text-violet-700">{label}</p>
                    <p className="text-slate-400 text-xs mt-1">{desc}</p>
                  </button>
                ))}
              </div>
            </div>
          </>
        )}

      </div>
    </Layout>
  );
}
