'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import api from '@/lib/api';
import { format, subDays } from 'date-fns';
import clsx from 'clsx';
import {
  HomeIcon, ChevronRightIcon, CheckCircleIcon, ArrowDownTrayIcon,
  ArrowLeftIcon, CurrencyDollarIcon, BuildingOfficeIcon, UsersIcon,
  CalendarDaysIcon,
} from '@heroicons/react/24/outline';

interface ExportItem {
  id: string;
  title: string;
  description: string;
  endpoint: string;
  params: (start: string, end: string) => Record<string, string>;
}

const EXPORTS: ExportItem[] = [
  {
    id: 'revenue',
    title: 'Revenue Report',
    description: 'Daily revenue breakdown by category (CSV)',
    endpoint: '/api/v1/reports/revenue/',
    params: (start, end) => ({ start, end }),
  },
  {
    id: 'occupancy',
    title: 'Occupancy Report',
    description: 'Daily occupancy, ADR and RevPAR (CSV)',
    endpoint: '/api/v1/reports/occupancy/',
    params: (start, end) => ({ start, end }),
  },
  {
    id: 'guests',
    title: 'Guest Analytics',
    description: 'Guest counts and nationality breakdown (CSV)',
    endpoint: '/api/v1/reports/guests/',
    params: (start, end) => ({ start_date: start, end_date: end }),
  },
  {
    id: 'reservations',
    title: 'Reservations',
    description: 'All reservations for this property (CSV)',
    endpoint: '/api/v1/reservations/',
    params: (start, end) => ({ start_date: start, end_date: end }),
  },
];

const ICONS: Record<string, React.ReactNode> = {
  revenue:      <CurrencyDollarIcon className="w-5 h-5 text-violet-600" />,
  occupancy:    <BuildingOfficeIcon  className="w-5 h-5 text-blue-600" />,
  guests:       <UsersIcon           className="w-5 h-5 text-emerald-600" />,
  reservations: <CalendarDaysIcon    className="w-5 h-5 text-amber-600" />,
};

function normaliseForCsv(raw: unknown, itemId: string): unknown[] {
  if (Array.isArray(raw)) return raw;
  if (Array.isArray((raw as any).data)) return (raw as any).data;
  if (Array.isArray((raw as any).results)) return (raw as any).results;
  // Guest report: flatten summary + nationalities + types into labelled rows
  if (itemId === 'guests' && (raw as any).top_nationalities) {
    const d = raw as any;
    return [
      { category: 'Summary', label: 'Total Guests',              value: d.total_guests },
      { category: 'Summary', label: 'New Guests',                value: d.new_guests },
      { category: 'Summary', label: 'Returning Guests',          value: d.returning_guests },
      { category: 'Summary', label: 'Total Reservations',        value: d.total_reservations },
      { category: 'Summary', label: 'Avg Stay Duration (nights)',value: d.avg_stay_duration },
      ...d.top_nationalities.map((n: any) => ({ category: 'Nationality', label: n.country || 'Unknown', value: n.count })),
      ...d.by_type.map((t: any) => ({ category: 'Guest Type', label: t.type, value: t.count })),
    ];
  }
  return [raw as Record<string, unknown>];
}

function jsonToCsv(data: unknown): string {
  if (!Array.isArray(data) || data.length === 0) return '';
  const headers = Object.keys(data[0] as object);
  const rows = (data as Record<string, unknown>[]).map(row =>
    headers.map(h => JSON.stringify(row[h] ?? '')).join(',')
  );
  return [headers.join(','), ...rows].join('\n');
}

export default function ExportCenterPage() {
  const router = useRouter();
  const [loading, setLoading] = useState<string | null>(null);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const [dates, setDates] = useState({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  };

  const handleExport = async (item: ExportItem) => {
    setLoading(item.id);
    try {
      const resp = await api.get(item.endpoint, { params: item.params(dates.start, dates.end) });
      const raw = resp.data;
      // Normalise: extract array from known shapes (guest report gets flattened)
      const arr = normaliseForCsv(raw, item.id);
      const csv = jsonToCsv(arr);
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${item.id}-${dates.start}-${dates.end}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      showToast(`${item.title} exported`, true);
    } catch {
      showToast(`Failed to export ${item.title}`, false);
    } finally {
      setLoading(null);
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
          <span className="text-slate-700 font-medium">Export</span>
        </nav>

        <div className="flex items-center gap-3">
          <button onClick={() => router.push('/reports')} className="p-2 rounded-xl text-slate-400 hover:bg-slate-100">
            <ArrowLeftIcon className="w-5 h-5" />
          </button>
          <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center">
            <ArrowDownTrayIcon className="w-5 h-5 text-slate-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Export Center</h1>
            <p className="text-slate-500 text-sm">Download report data as CSV files</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
          <div className="flex flex-wrap gap-3 items-end">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">From</label>
              <input type="date" value={dates.start}
                onChange={e => setDates(d => ({ ...d, start: e.target.value }))}
                className="px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-300" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">To</label>
              <input type="date" value={dates.end}
                onChange={e => setDates(d => ({ ...d, end: e.target.value }))}
                className="px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-slate-300" />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {EXPORTS.map(item => (
            <div key={item.id} className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center flex-shrink-0">
                {ICONS[item.id]}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-slate-800">{item.title}</p>
                <p className="text-xs text-slate-400 mt-0.5">{item.description}</p>
              </div>
              <button
                onClick={() => handleExport(item)}
                disabled={loading === item.id}
                className="flex-shrink-0 flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-900 text-white text-sm font-medium disabled:opacity-50">
                <ArrowDownTrayIcon className="w-4 h-4" />
                {loading === item.id ? 'Exporting…' : 'Export'}
              </button>
            </div>
          ))}
        </div>

      </div>
    </Layout>
  );
}
