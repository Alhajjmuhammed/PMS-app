'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import api from '@/lib/api';
import { format } from 'date-fns';
import clsx from 'clsx';
import {
  HomeIcon,
  ChevronRightIcon,
  CreditCardIcon,
  MagnifyingGlassIcon,
  DocumentTextIcon,
  ChevronLeftIcon,
} from '@heroicons/react/24/outline';

interface Folio {
  id: number;
  folio_number: string;
  folio_type: string;
  status: string;
  guest_name: string;
  room_number: string;
  total_charges: string;
  total_payments: string;
  balance: string;
  open_date: string;
  close_date: string | null;
}

const STATUS_COLORS: Record<string, string> = {
  OPEN:     'bg-blue-50 text-blue-700 border-blue-200',
  CLOSED:   'bg-emerald-50 text-emerald-700 border-emerald-200',
  SETTLED:  'bg-slate-50 text-slate-600 border-slate-200',
};

function StatusBadge({ status }: { status: string }) {
  return (
    <span className={clsx('inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border', STATUS_COLORS[status] || 'bg-slate-50 text-slate-500 border-slate-200')}>
      {status}
    </span>
  );
}

export default function BillingPage() {
  const router = useRouter();
  const [folios, setFolios] = useState<Folio[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const perPage = 10;

  useEffect(() => {
    load();
  }, [statusFilter]);

  const load = async (q?: string) => {
    try {
      setLoading(true);
      const params: Record<string, string> = {};
      if (statusFilter) params.status = statusFilter;
      if (q !== undefined) params.search = q;
      else if (search) params.search = search;
      const resp = await api.get('/api/v1/billing/folios/', { params });
      setFolios(resp.data.results ?? resp.data);
      setPage(1);
    } catch {
      console.error('Failed to load folios');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    load(search);
  };

  const totalPages = Math.max(1, Math.ceil(folios.length / perPage));
  const safePage = Math.min(page, totalPages);
  const paginated = folios.slice((safePage - 1) * perPage, safePage * perPage);

  const totalBalance = folios.reduce((s, f) => s + Number(f.balance), 0);
  const openCount   = folios.filter(f => f.status === 'OPEN').length;

  return (
    <Layout>
      <div className="p-5 lg:p-6 space-y-5">

        {/* Breadcrumb */}
        <nav className="flex items-center gap-1.5 text-sm text-slate-400">
          <HomeIcon className="w-4 h-4" />
          <span>Home</span>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <span className="text-slate-700 font-medium">Billing</span>
        </nav>

        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-violet-100 flex items-center justify-center flex-shrink-0">
              <CreditCardIcon className="w-5 h-5 text-violet-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Billing</h1>
              <p className="text-slate-500 text-sm mt-0.5">{folios.length} folio{folios.length !== 1 ? 's' : ''}</p>
            </div>
          </div>
        </div>

        {/* Quick stats */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-4">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Outstanding</p>
            <p className="text-2xl font-bold text-violet-600 mt-1">${totalBalance.toLocaleString()}</p>
          </div>
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-4">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Open Folios</p>
            <p className="text-2xl font-bold text-blue-600 mt-1">{openCount}</p>
          </div>
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-4 col-span-2 sm:col-span-1">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Folios</p>
            <p className="text-2xl font-bold text-slate-800 mt-1">{folios.length}</p>
          </div>
        </div>

        {/* Search + filter row */}
        <div className="flex flex-wrap gap-3">
          <form onSubmit={handleSearch} className="flex gap-2 flex-1 min-w-[200px]">
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search folio number or guest…"
              className="flex-1 px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300"
            />
            <button type="submit" className="px-4 py-2.5 rounded-xl bg-slate-700 hover:bg-slate-800 text-white text-sm font-semibold transition-colors">
              <MagnifyingGlassIcon className="w-4 h-4" />
            </button>
          </form>
          <div className="flex gap-1.5 flex-wrap">
            {[['', 'All'], ['OPEN', 'Open'], ['CLOSED', 'Closed'], ['SETTLED', 'Settled']].map(([val, label]) => (
              <button
                key={val}
                onClick={() => setStatusFilter(val)}
                className={clsx('px-3 py-2 text-sm font-semibold rounded-xl transition-colors',
                  statusFilter === val ? 'bg-violet-600 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50')}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-10 h-10 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : folios.length === 0 ? (
          <div className="text-center py-20 text-slate-400">
            <DocumentTextIcon className="w-14 h-14 mx-auto mb-3 opacity-30" />
            <p className="font-medium">No folios found</p>
          </div>
        ) : (
          <>
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-100 bg-slate-50/60">
                      {['Folio #', 'Guest', 'Room', 'Charges', 'Payments', 'Balance', 'Status', 'Opened'].map(h => (
                        <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {paginated.map((f) => (
                      <tr key={f.id}
                        className="hover:bg-slate-50/50 transition-colors cursor-pointer"
                        onClick={() => router.push(`/billing/${f.id}`)}>
                        <td className="px-4 py-3">
                          <span className="font-mono text-xs font-semibold text-violet-700 bg-violet-50 px-2 py-0.5 rounded-md">{f.folio_number}</span>
                        </td>
                        <td className="px-4 py-3 font-medium text-slate-800">{f.guest_name}</td>
                        <td className="px-4 py-3 text-slate-500">{f.room_number || '—'}</td>
                        <td className="px-4 py-3 text-slate-700">${Number(f.total_charges).toLocaleString()}</td>
                        <td className="px-4 py-3 text-emerald-700">${Number(f.total_payments).toLocaleString()}</td>
                        <td className="px-4 py-3">
                          <span className={clsx('font-bold', Number(f.balance) > 0 ? 'text-red-600' : 'text-emerald-600')}>
                            ${Number(f.balance).toLocaleString()}
                          </span>
                        </td>
                        <td className="px-4 py-3"><StatusBadge status={f.status} /></td>
                        <td className="px-4 py-3 text-slate-400 text-xs">{format(new Date(f.open_date), 'MMM d, yyyy')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between flex-wrap gap-3 pt-1">
                <span className="text-sm text-slate-500">
                  {(safePage - 1) * perPage + 1}–{Math.min(safePage * perPage, folios.length)} of {folios.length}
                </span>
                <div className="flex items-center gap-1">
                  <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={safePage === 1}
                    className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-100 disabled:opacity-40">
                    <ChevronLeftIcon className="w-4 h-4" />
                  </button>
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(pg => (
                    <button key={pg} onClick={() => setPage(pg)}
                      className={clsx('w-8 h-8 rounded-lg text-sm font-semibold',
                        pg === safePage ? 'bg-violet-600 text-white' : 'border border-slate-200 text-slate-600 hover:bg-slate-100')}>
                      {pg}
                    </button>
                  ))}
                  <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={safePage === totalPages}
                    className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-100 disabled:opacity-40">
                    <ChevronRightIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}

      </div>
    </Layout>
  );
}
