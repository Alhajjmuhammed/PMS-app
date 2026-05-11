'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import api from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { format } from 'date-fns';
import clsx from 'clsx';
import {
  CheckCircleIcon,
  ClockIcon,
  HomeIcon,
  ChevronRightIcon,
  MoonIcon,
} from '@heroicons/react/24/outline';

export default function NightAuditPage() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [auditDate, setAuditDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [summary, setSummary] = useState<any>(null);
  const [existingAudit, setExistingAudit] = useState<any>(null);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 4000);
  };

  const loadAuditStatus = async (date: string) => {
    try {
      const resp = await api.get('/api/v1/reports/night-audits/', { params: { business_date: date } });
      const allList: any[] = resp.data.results ?? resp.data;
      const forDate = allList.filter((a: any) => a.business_date === date);
      setExistingAudit(forDate.length > 0 ? forDate[0] : null);
    } catch {
      setExistingAudit(null);
    }
  };

  const loadSummary = async () => {
    try {
      const response = await api.get('/api/v1/reports/daily/', { params: { date: auditDate } });
      const d = response.data;
      setSummary({
        ...d,
        total_checkins: d.arrivals ?? d.total_checkins ?? 0,
        total_checkouts: d.departures ?? d.total_checkouts ?? 0,
        occupied_rooms: d.in_house ?? d.occupied_rooms ?? 0,
        available_rooms: d.total_rooms != null && d.rooms_sold != null
          ? d.total_rooms - d.rooms_sold
          : (d.available_rooms ?? 0),
        fnb_revenue: d.fb_revenue ?? d.fnb_revenue ?? 0,
      });
    } catch {
      console.error('Failed to load summary');
    }
  };

  useEffect(() => {
    loadSummary();
    loadAuditStatus(auditDate);
  }, [auditDate]);

  const runNightAudit = async () => {
    if (!confirm('Are you sure you want to run the night audit? This will close the business day.')) return;

    try {
      setLoading(true);
      const existing = await api.get('/api/v1/reports/night-audits/', { params: { business_date: auditDate } });
      const allList: any[] = existing.data.results ?? existing.data;
      const list = allList.filter((a: any) => a.business_date === auditDate);
      const pending = list.find((a: any) => a.status === 'PENDING');
      const inProgress = list.find((a: any) => a.status === 'IN_PROGRESS');
      const alreadyCompleted = list.find((a: any) => a.status === 'COMPLETED');

      if (alreadyCompleted) {
        showToast('This night audit is already completed for this date.', false);
        await loadAuditStatus(auditDate);
        return;
      }

      if (inProgress) {
        await api.post(`/api/v1/reports/night-audits/${inProgress.id}/complete/`);
      } else {
        let auditId: number;
        if (pending) {
          auditId = pending.id;
        } else {
          const createResp = await api.post('/api/v1/reports/night-audits/', {
            business_date: auditDate,
            property: user?.assigned_property?.id,
          });
          auditId = createResp.data.id;
        }
        await api.post(`/api/v1/reports/night-audits/${auditId}/start/`);
        await api.post(`/api/v1/reports/night-audits/${auditId}/complete/`);
      }

      showToast('Night audit completed successfully!');
      await loadSummary();
      await loadAuditStatus(auditDate);
    } catch (error: any) {
      const data = error?.response?.data;
      const msg = typeof data === 'string'
        ? data
        : data?.error || data?.detail || data?.non_field_errors?.[0]
          || JSON.stringify(data) || 'Unknown error';
      showToast(`Failed: ${msg}`, false);
    } finally {
      setLoading(false);
    }
  };

  const isCompleted = existingAudit?.status === 'COMPLETED';
  const isInProgress = existingAudit?.status === 'IN_PROGRESS';
  const isPending = !existingAudit || existingAudit?.status === 'PENDING';

  const statusColor = isCompleted
    ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
    : isInProgress
    ? 'bg-blue-50 text-blue-700 border-blue-200'
    : 'bg-amber-50 text-amber-700 border-amber-200';

  const statusLabel = isCompleted ? 'Completed' : isInProgress ? 'In Progress' : 'Pending';

  const checklist = [
    { label: 'No-shows processed',  done: existingAudit?.no_shows_processed },
    { label: 'Room rates posted',   done: existingAudit?.room_rates_posted },
    { label: 'Departures checked',  done: existingAudit?.departures_checked },
    { label: 'Folios settled',      done: existingAudit?.folios_settled },
    { label: 'Audit completed',     done: isCompleted },
  ];

  const doneCount = checklist.filter((c) => c.done).length;

  return (
    <Layout>
      <div className="p-5 lg:p-6 space-y-5">

        {/* Toast */}
        {toast && (
          <div className={clsx(
            'fixed top-5 right-5 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium transition-all',
            toast.ok ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white'
          )}>
            <CheckCircleIcon className="w-5 h-5 flex-shrink-0" />
            {toast.msg}
          </div>
        )}

        {/* Breadcrumb */}
        <nav className="flex items-center gap-1.5 text-sm text-slate-400">
          <HomeIcon className="w-4 h-4" />
          <span>Home</span>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <span className="text-slate-700 font-medium">Night Audit</span>
        </nav>

        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center flex-shrink-0">
              <MoonIcon className="w-5 h-5 text-indigo-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Night Audit</h1>
              <p className="text-slate-500 text-sm mt-0.5">
                Business date:{' '}
                <span className="font-medium text-slate-700">
                  {format(new Date(auditDate + 'T00:00:00'), 'MMMM d, yyyy')}
                </span>
                {existingAudit && (
                  <span className={clsx('ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border', statusColor)}>
                    {statusLabel}
                  </span>
                )}
              </p>
            </div>
          </div>

          {/* Date Picker */}
          <div className="flex items-center gap-2">
            <label className="text-sm text-slate-500 font-medium">Audit Date</label>
            <input
              type="date"
              value={auditDate}
              onChange={(e) => setAuditDate(e.target.value)}
              className="px-3 py-2 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300"
            />
          </div>
        </div>

        {/* Completed banner */}
        {isCompleted && (
          <div className="flex items-center gap-3 px-5 py-4 bg-emerald-50 border border-emerald-200 rounded-2xl">
            <CheckCircleIcon className="w-6 h-6 text-emerald-600 flex-shrink-0" />
            <div>
              <p className="font-semibold text-emerald-800">Night Audit Completed</p>
              <p className="text-emerald-600 text-sm mt-0.5">
                Closed on {existingAudit.completed_at
                  ? format(new Date(existingAudit.completed_at), 'MMM d, yyyy · HH:mm')
                  : format(new Date(auditDate + 'T00:00:00'), 'MMM d, yyyy')}
                {existingAudit.completed_by_name && ` by ${existingAudit.completed_by_name}`}
              </p>
            </div>
          </div>
        )}

        {/* In-progress banner */}
        {isInProgress && (
          <div className="flex items-center gap-3 px-5 py-4 bg-blue-50 border border-blue-200 rounded-2xl">
            <ClockIcon className="w-6 h-6 text-blue-600 flex-shrink-0 animate-pulse" />
            <div>
              <p className="font-semibold text-blue-800">Audit In Progress</p>
              <p className="text-blue-600 text-sm mt-0.5">Steps are running — click the button below to finalise.</p>
            </div>
          </div>
        )}

        {/* Top stat cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { label: 'Total Revenue',  value: `$${(summary?.total_revenue ?? 0).toLocaleString()}`, color: 'text-indigo-600' },
            { label: 'Check-ins',      value: summary?.total_checkins ?? 0,                         color: 'text-blue-600' },
            { label: 'Check-outs',     value: summary?.total_checkouts ?? 0,                        color: 'text-emerald-600' },
          ].map(({ label, value, color }) => (
            <div key={label} className="bg-white rounded-2xl border border-slate-100 shadow-sm px-6 py-5 text-center">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</p>
              <p className={clsx('text-3xl font-bold mt-1', color)}>{value}</p>
            </div>
          ))}
        </div>

        {/* Two-column layout: left = details, right = checklist + action */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">

          {/* Left column (3/5) */}
          <div className="lg:col-span-3 space-y-5">

            {/* Room Status */}
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-100">
                <h2 className="font-semibold text-slate-800">Room Status</h2>
              </div>
              <div className="grid grid-cols-2 divide-x divide-y divide-slate-100">
                {[
                  { label: 'Occupied',    value: summary?.occupied_rooms   ?? 0, dot: 'bg-indigo-500' },
                  { label: 'Available',   value: summary?.available_rooms  ?? 0, dot: 'bg-emerald-500' },
                  { label: 'Dirty',       value: summary?.dirty_rooms      ?? 0, dot: 'bg-amber-400' },
                  { label: 'Maintenance', value: summary?.maintenance_rooms ?? 0, dot: 'bg-red-400' },
                ].map(({ label, value, dot }) => (
                  <div key={label} className="px-6 py-5 flex items-center gap-3">
                    <span className={clsx('w-2.5 h-2.5 rounded-full flex-shrink-0', dot)} />
                    <div>
                      <p className="text-xs text-slate-400 font-medium">{label}</p>
                      <p className="text-2xl font-bold text-slate-800 leading-tight">{value}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Financial Summary */}
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-100">
                <h2 className="font-semibold text-slate-800">Financial Summary</h2>
                <p className="text-xs text-slate-400 mt-0.5">All charges for {format(new Date(auditDate + 'T00:00:00'), 'MMM d, yyyy')}</p>
              </div>
              <div className="px-6 py-4 space-y-3">
                {[
                  { label: 'Room Revenue',  value: summary?.room_revenue  ?? 0 },
                  { label: 'F&B Revenue',   value: summary?.fnb_revenue   ?? 0 },
                  { label: 'Other Revenue', value: summary?.other_revenue ?? 0 },
                ].map(({ label, value }) => (
                  <div key={label} className="flex items-center justify-between py-1">
                    <span className="text-sm text-slate-500">{label}</span>
                    <span className="text-sm font-semibold text-slate-800">${Number(value).toLocaleString()}</span>
                  </div>
                ))}
                <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                  <span className="text-sm font-bold text-slate-900">Total</span>
                  <span className="text-base font-bold text-indigo-600">
                    ${Number(summary?.total_revenue ?? 0).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>

          </div>

          {/* Right column (2/5) */}
          <div className="lg:col-span-2 space-y-5">

            {/* Pre-Audit Checklist */}
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
                <h2 className="font-semibold text-slate-800">Pre-Audit Checklist</h2>
                <span className="text-xs font-semibold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full">
                  {doneCount}/{checklist.length}
                </span>
              </div>
              {/* Progress bar */}
              <div className="h-1 bg-slate-100">
                <div
                  className="h-1 bg-emerald-500 transition-all duration-500"
                  style={{ width: `${(doneCount / checklist.length) * 100}%` }}
                />
              </div>
              <ul className="px-6 py-4 space-y-3">
                {checklist.map(({ label, done }) => (
                  <li key={label} className="flex items-center gap-3">
                    <span className={clsx(
                      'w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 border-2 transition-colors',
                      done
                        ? 'bg-emerald-500 border-emerald-500'
                        : 'bg-white border-slate-300'
                    )}>
                      {done && (
                        <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </span>
                    <span className={clsx('text-sm', done ? 'text-emerald-700 font-medium line-through' : 'text-slate-600')}>
                      {label}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Action card */}
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm px-6 py-5">
              {isCompleted ? (
                <div className="flex flex-col items-center gap-2 text-center py-2">
                  <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center mb-1">
                    <CheckCircleIcon className="w-7 h-7 text-emerald-600" />
                  </div>
                  <p className="font-semibold text-slate-800">Audit Closed</p>
                  <p className="text-xs text-slate-400">
                    {format(new Date(auditDate + 'T00:00:00'), 'MMMM d, yyyy')}
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  <p className="text-sm text-slate-500">
                    {isInProgress
                      ? 'Audit steps have run. Click below to finalise and close the business day.'
                      : 'Click below to run all audit steps and close the business day.'}
                  </p>
                  <button
                    onClick={runNightAudit}
                    disabled={loading}
                    className={clsx(
                      'w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-semibold transition-colors shadow-sm',
                      loading
                        ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                        : isInProgress
                        ? 'bg-blue-600 hover:bg-blue-700 text-white'
                        : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                    )}
                  >
                    {loading ? (
                      <>
                        <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                        Running…
                      </>
                    ) : (
                      <>
                        <MoonIcon className="w-4 h-4" />
                        {isInProgress ? 'Complete Night Audit' : 'Run Night Audit'}
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>

          </div>
        </div>

      </div>
    </Layout>
  );
}
