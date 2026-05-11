'use client';

import { useEffect, useState, useCallback, useMemo } from 'react';
import Layout from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import clsx from 'clsx';
import {
  PlusIcon,
  XMarkIcon,
  CheckCircleIcon,
  PlayIcon,
  WrenchScrewdriverIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  UserPlusIcon,
  EyeIcon,
  PauseIcon,
  ArrowPathIcon,
  HandRaisedIcon,
  InboxArrowDownIcon,
} from '@heroicons/react/24/outline';

// ── Types ─────────────────────────────────────────────────────────────────────
interface MaintenanceRequest {
  id: number;
  request_number: string;
  property: number;
  room: number | null;
  room_number: string | null;
  location: string;
  request_type: string;
  priority: string;
  status: string;
  title: string;
  description: string;
  assigned_to: number | null;
  assigned_to_name: string | null;
  assigned_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  resolution_notes: string;
  parts_cost: string;
  labor_hours: string;
  reported_by: number;
  reported_by_name: string | null;
  logs: any[];
  total_cost: number;
  duration_hours: number | null;
  is_overdue: boolean;
  created_at: string;
}

interface DashboardStats {
  pending_requests: number;
  assigned_requests: number;
  in_progress_requests: number;
  completed_today: number;
  emergency_requests: number;
  overdue_requests: number;
  pool_requests: number;
}

interface StaffProfile { id: number; user: number; user_name: string; user_role: string; }
interface Room { id: number; room_number: string; }

// ── Constants ─────────────────────────────────────────────────────────────────
const REQUEST_TYPES = [
  { value: 'ELECTRICAL', label: 'Electrical' },
  { value: 'PLUMBING',   label: 'Plumbing'   },
  { value: 'HVAC',       label: 'HVAC'        },
  { value: 'FURNITURE',  label: 'Furniture'  },
  { value: 'APPLIANCE',  label: 'Appliance'  },
  { value: 'STRUCTURAL', label: 'Structural' },
  { value: 'GENERAL',    label: 'General'    },
  { value: 'PREVENTIVE', label: 'Preventive' },
];
const PRIORITIES = [
  { value: 'LOW',       label: 'Low'       },
  { value: 'MEDIUM',    label: 'Medium'    },
  { value: 'HIGH',      label: 'High'      },
  { value: 'EMERGENCY', label: 'Emergency' },
];
const STATUSES = [
  { value: 'PENDING',     label: 'Pending'     },
  { value: 'ASSIGNED',    label: 'Assigned'    },
  { value: 'IN_PROGRESS', label: 'In Progress' },
  { value: 'ON_HOLD',     label: 'On Hold'     },
  { value: 'COMPLETED',   label: 'Completed'   },
  { value: 'CANCELLED',   label: 'Cancelled'   },
];

const PRIORITY_COLORS: Record<string, string> = {
  LOW:       'bg-slate-100 text-slate-600',
  MEDIUM:    'bg-blue-100 text-blue-700',
  HIGH:      'bg-orange-100 text-orange-700',
  EMERGENCY: 'bg-red-100 text-red-700',
};
const STATUS_COLORS: Record<string, string> = {
  PENDING:     'bg-amber-100 text-amber-700',
  ASSIGNED:    'bg-blue-100 text-blue-700',
  IN_PROGRESS: 'bg-indigo-100 text-indigo-700',
  ON_HOLD:     'bg-slate-100 text-slate-500',
  COMPLETED:   'bg-emerald-100 text-emerald-700',
  CANCELLED:   'bg-red-100 text-red-600',
};

function pColor(p: string) { return PRIORITY_COLORS[p] ?? 'bg-slate-100 text-slate-600'; }
function sColor(s: string) { return STATUS_COLORS[s]   ?? 'bg-slate-100 text-slate-600'; }

function choiceLabel(arr: { value: string; label: string }[], val: string) {
  return arr.find((x) => x.value === val)?.label ?? val;
}
function formatDate(s: string | null) {
  if (!s) return '—';
  return new Date(s).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}
function formatDateTime(s: string | null) {
  if (!s) return '—';
  return new Date(s).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

const EMPTY_FORM = {
  room: '',
  location: '',
  title: '',
  request_type: 'GENERAL',
  priority: 'MEDIUM',
  description: '',
  assign_to: '',   // '' = post to pool; a user ID = direct assign
};

// ── Pagination ─────────────────────────────────────────────────────────────────
function Pagination({ total, safePage, perPage, totalPages, onPageChange, onPerPageChange }: any) {
  if (total === 0) return null;
  const start = (safePage - 1) * perPage + 1;
  const end = Math.min(safePage * perPage, total);
  return (
    <div className="flex items-center justify-between flex-wrap gap-3 pt-2 px-2">
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <span>Rows:</span>
        <select value={perPage} onChange={(e) => onPerPageChange(Number(e.target.value))}
          className="border border-slate-200 rounded-lg px-2 py-1 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-300">
          {[10, 20, 50].map((n) => <option key={n} value={n}>{n}</option>)}
        </select>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-sm text-slate-500">{start}–{end} of {total}</span>
        <div className="flex items-center gap-1">
          <button onClick={() => onPageChange(Math.max(1, safePage - 1))} disabled={safePage === 1}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 disabled:opacity-30">
            <ChevronLeftIcon className="w-4 h-4" />
          </button>
          <button onClick={() => onPageChange(Math.min(totalPages, safePage + 1))} disabled={safePage === totalPages}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 disabled:opacity-30">
            <ChevronRightIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, color }: { label: string; value: number; icon: React.ReactNode; color: string }) {
  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-4 flex items-center gap-4">
      <div className={clsx('w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0', color)}>{icon}</div>
      <div>
        <p className="text-2xl font-bold text-slate-900">{value}</p>
        <p className="text-xs text-slate-500 mt-0.5">{label}</p>
      </div>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function MaintenancePage() {
  const { user } = useAuth();
  const canManage   = user?.role && ['ADMIN', 'MANAGER'].includes(user.role);
  const isMaintenance = user?.role === 'MAINTENANCE';

  // ── State ──────────────────────────────────────────────────────────────────
  const [requests, setRequests] = useState<MaintenanceRequest[]>([]);
  const [stats, setStats]       = useState<DashboardStats | null>(null);
  const [rooms, setRooms]       = useState<Room[]>([]);
  const [staff, setStaff]       = useState<StaffProfile[]>([]);
  const [loading, setLoading]   = useState(true);

  const [statusFilter,   setStatusFilter]   = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [page,    setPage]    = useState(1);
  const [perPage, setPerPage] = useState(10);

  const [showCreate, setShowCreate] = useState(false);
  const [form,       setForm]       = useState(EMPTY_FORM);
  const [saving,     setSaving]     = useState(false);

  const [viewReq,   setViewReq]   = useState<MaintenanceRequest | null>(null);
  const [assignTo,  setAssignTo]  = useState('');
  const [notesMode, setNotesMode] = useState<'complete' | 'resolve' | null>(null);
  const [notes,     setNotes]     = useState('');
  const [acting,    setActing]    = useState(false);

  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  };

  // ── Load data ──────────────────────────────────────────────────────────────
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (statusFilter)   params.status   = statusFilter;
      if (priorityFilter) params.priority = priorityFilter;
      const [rRes, sRes] = await Promise.all([
        api.get('/api/v1/maintenance/requests/', { params }),
        api.get('/api/v1/maintenance/dashboard/'),
      ]);
      const data = rRes.data?.results ?? rRes.data;
      setRequests(Array.isArray(data) ? data : []);
      setStats(sRes.data);
    } catch {
      showToast('Failed to load requests', false);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, priorityFilter]);

  useEffect(() => { loadData(); }, [loadData]);
  useEffect(() => { setPage(1); }, [statusFilter, priorityFilter]);

  useEffect(() => {
    if (!canManage) return;
    Promise.all([
      api.get('/api/v1/rooms/').catch(() => null),
      api.get('/api/v1/accounts/staff-profiles/', { params: { user__role: 'MAINTENANCE' } }).catch(() => null),
    ]).then(([rR, sR]) => {
      if (rR) { const d = rR.data?.results ?? rR.data; setRooms(Array.isArray(d) ? d : []); }
      if (sR) { const d = sR.data?.results ?? sR.data; setStaff(Array.isArray(d) ? d : []); }
    });
  }, [canManage]);

  // ── Pagination ─────────────────────────────────────────────────────────────
  const totalPages = Math.max(1, Math.ceil(requests.length / perPage));
  const safePage   = Math.min(page, totalPages);
  const paginated  = useMemo(
    () => requests.slice((safePage - 1) * perPage, safePage * perPage),
    [requests, safePage, perPage],
  );

  // ── Actions ────────────────────────────────────────────────────────────────
  const openView = (req: MaintenanceRequest) => {
    setViewReq(req);
    setAssignTo('');
    setNotesMode(null);
    setNotes('');
  };

  const refreshView = async (id: number) => {
    try {
      const r = await api.get(`/api/v1/maintenance/requests/${id}/`);
      setViewReq(r.data);
    } catch {}
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload: any = { ...form };
      if (!payload.room)      delete payload.room;
      if (!payload.location)  delete payload.location;
      if (!payload.assign_to) delete payload.assign_to;
      else                    payload.assigned_to = Number(payload.assign_to);
      delete payload.assign_to;
      await api.post('/api/v1/maintenance/requests/', payload);
      showToast(payload.assigned_to ? 'Request created & assigned' : 'Request posted to pool');
      setShowCreate(false);
      setForm(EMPTY_FORM);
      loadData();
    } catch (err: any) {
      const d = err?.response?.data;
      showToast(typeof d === 'object' ? Object.values(d).flat().join(' ') : 'Failed to create request', false);
    } finally { setSaving(false); }
  };

  const handleClaim = async (req: MaintenanceRequest) => {
    setActing(true);
    try {
      await api.post(`/api/v1/maintenance/requests/${req.id}/claim/`, {});
      showToast('Task claimed — it\'s yours!');
      if (viewReq?.id === req.id) await refreshView(req.id);
      loadData();
    } catch (err: any) {
      showToast(err?.response?.data?.error ?? 'Could not claim — try refreshing', false);
    } finally { setActing(false); }
  };

  const handleStart = async (req: MaintenanceRequest) => {
    setActing(true);
    try {
      await api.post(`/api/v1/maintenance/requests/${req.id}/start/`, {});
      showToast('Request started — good luck!');
      await refreshView(req.id);
      loadData();
    } catch (err: any) {
      showToast(err?.response?.data?.error ?? 'Failed to start request', false);
    } finally { setActing(false); }
  };

  const handleOnHold = async (req: MaintenanceRequest) => {
    setActing(true);
    try {
      await api.post(`/api/v1/maintenance/requests/${req.id}/on-hold/`, {});
      showToast('Request put on hold');
      if (viewReq?.id === req.id) await refreshView(req.id);
      loadData();
    } catch (err: any) {
      showToast(err?.response?.data?.error ?? 'Failed to put on hold', false);
    } finally { setActing(false); }
  };

  const handleResume = async (req: MaintenanceRequest) => {
    setActing(true);
    try {
      await api.post(`/api/v1/maintenance/requests/${req.id}/resume/`, {});
      showToast('Request resumed');
      if (viewReq?.id === req.id) await refreshView(req.id);
      loadData();
    } catch (err: any) {
      showToast(err?.response?.data?.error ?? 'Failed to resume request', false);
    } finally { setActing(false); }
  };

  const handleAssign = async () => {
    if (!viewReq || !assignTo) return;
    setActing(true);
    try {
      await api.post(`/api/v1/maintenance/requests/${viewReq.id}/assign/`, { assigned_to: Number(assignTo) });
      showToast('Assigned successfully');
      setAssignTo('');
      await refreshView(viewReq.id);
      loadData();
    } catch (err: any) {
      showToast(err?.response?.data?.error ?? 'Failed to assign', false);
    } finally { setActing(false); }
  };

  const handleNotesSubmit = async () => {
    if (!viewReq || !notes.trim()) { showToast('Please enter resolution notes', false); return; }
    setActing(true);
    try {
      if (notesMode === 'complete') {
        await api.post(`/api/v1/maintenance/requests/${viewReq.id}/complete/`, { resolution_notes: notes.trim() });
      } else {
        await api.patch(`/api/v1/maintenance/requests/${viewReq.id}/`, { status: 'COMPLETED', resolution_notes: notes.trim() });
      }
      showToast('Request completed');
      setNotesMode(null);
      setNotes('');
      await refreshView(viewReq.id);
      loadData();
    } catch (err: any) {
      showToast(err?.response?.data?.error ?? 'Failed to update request', false);
    } finally { setActing(false); }
  };

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <Layout>
      <div className="p-5 lg:p-6 space-y-5">

        {/* Toast */}
        {toast && (
          <div className={clsx(
            'fixed top-5 right-5 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium',
            toast.ok ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white',
          )}>
            <CheckCircleIcon className="w-5 h-5 flex-shrink-0" />
            {toast.msg}
          </div>
        )}

        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Maintenance</h1>
            {isMaintenance && <p className="text-sm text-slate-400 mt-0.5">Showing your assigned tasks</p>}
          </div>
          {canManage && (
            <button onClick={() => setShowCreate(true)}
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-sm">
              <PlusIcon className="w-4 h-4" />
              New Request
            </button>
          )}
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {canManage && <StatCard label="In Pool"     value={stats.pool_requests}        color="bg-violet-50"  icon={<InboxArrowDownIcon      className="w-5 h-5 text-violet-600"  />} />}
            {isMaintenance && <StatCard label="In Pool (Available)" value={stats.pool_requests} color="bg-violet-50" icon={<InboxArrowDownIcon className="w-5 h-5 text-violet-600" />} />}
            <StatCard label="Pending"     value={stats.pending_requests}     color="bg-amber-50"   icon={<ClockIcon              className="w-5 h-5 text-amber-600"   />} />
            <StatCard label="Assigned"    value={stats.assigned_requests}    color="bg-blue-50"    icon={<UserPlusIcon            className="w-5 h-5 text-blue-600"    />} />
            <StatCard label="In Progress" value={stats.in_progress_requests} color="bg-indigo-50"  icon={<PlayIcon                className="w-5 h-5 text-indigo-600"  />} />
            <StatCard label="Done Today"  value={stats.completed_today}      color="bg-emerald-50" icon={<CheckCircleIcon         className="w-5 h-5 text-emerald-600" />} />
            <StatCard label="Emergency"   value={stats.emergency_requests}   color="bg-red-50"     icon={<ExclamationTriangleIcon className="w-5 h-5 text-red-600"    />} />
            <StatCard label="Overdue"     value={stats.overdue_requests}     color="bg-orange-50"  icon={<WrenchScrewdriverIcon   className="w-5 h-5 text-orange-600" />} />
          </div>
        )}

        {/* Filters */}
        <div className="flex items-center gap-2 flex-wrap">
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
            className="border border-slate-200 rounded-xl px-3 py-2 text-sm text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-300">
            <option value="">All Statuses</option>
            {STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
          <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}
            className="border border-slate-200 rounded-xl px-3 py-2 text-sm text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-300">
            <option value="">All Priorities</option>
            {PRIORITIES.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
          </select>
          {(statusFilter || priorityFilter) && (
            <button onClick={() => { setStatusFilter(''); setPriorityFilter(''); }}
              className="text-xs text-slate-500 hover:text-slate-700 underline">
              Clear
            </button>
          )}
          <span className="text-xs text-slate-400 ml-auto">{requests.length} request{requests.length !== 1 ? 's' : ''}</span>
        </div>

        {/* Table */}
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : requests.length === 0 ? (
            <div className="text-center py-20 text-slate-400">
              <WrenchScrewdriverIcon className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p className="font-medium">No maintenance requests found</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-100 bg-slate-50/60">
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Ref #</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Title</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">Room / Location</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">Type</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Priority</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:table-cell">Assigned To</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:table-cell">Date</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {paginated.map((req) => {
                      const isDone = req.status === 'COMPLETED' || req.status === 'CANCELLED';
                      return (
                        <tr key={req.id} className="hover:bg-slate-50/50 transition-colors">
                          <td className="px-4 py-3">
                            <button onClick={() => openView(req)}
                              className="font-mono text-xs font-bold text-slate-700 hover:text-blue-600 transition-colors">
                              {req.request_number}
                            </button>
                          </td>
                          <td className="px-4 py-3 font-medium text-slate-800 max-w-[200px] truncate">
                            {req.title}
                            {req.assigned_to === null && req.status === 'PENDING' && (
                              <span className="ml-2 text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-violet-100 text-violet-700">POOL</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-slate-500 text-xs hidden sm:table-cell">
                            {req.room_number ?? req.location ?? '—'}
                          </td>
                          <td className="px-4 py-3 text-slate-500 text-xs hidden md:table-cell">
                            {choiceLabel(REQUEST_TYPES, req.request_type)}
                          </td>
                          <td className="px-4 py-3">
                            <span className={clsx('text-xs font-semibold px-2.5 py-0.5 rounded-full', pColor(req.priority))}>
                              {choiceLabel(PRIORITIES, req.priority)}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <span className={clsx('text-xs font-semibold px-2.5 py-0.5 rounded-full', sColor(req.status))}>
                              {choiceLabel(STATUSES, req.status)}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-slate-500 text-xs hidden lg:table-cell">
                            {req.assigned_to_name ?? <span className="italic text-slate-400">Unassigned</span>}
                          </td>
                          <td className="px-4 py-3 text-xs text-slate-400 hidden lg:table-cell">{formatDate(req.created_at)}</td>
                          <td className="px-4 py-3 text-right">
                            <div className="flex items-center justify-end gap-1">
                              <button onClick={() => openView(req)} title="View"
                                className="p-1.5 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-colors">
                                <EyeIcon className="w-4 h-4" />
                              </button>
                              {isMaintenance && !isDone && req.assigned_to === null && req.status === 'PENDING' && (
                                <button onClick={() => handleClaim(req)} title="Claim this task"
                                  className="p-1.5 rounded-lg text-violet-600 hover:bg-violet-50 transition-colors">
                                  <HandRaisedIcon className="w-4 h-4" />
                                </button>
                              )}
                              {isMaintenance && !isDone && req.status === 'ASSIGNED' && (
                                <button onClick={() => handleStart(req)} title="Start work"
                                  className="p-1.5 rounded-lg text-blue-500 hover:bg-blue-50 transition-colors">
                                  <PlayIcon className="w-4 h-4" />
                                </button>
                              )}
                              {isMaintenance && !isDone && req.status === 'IN_PROGRESS' && (
                                <>
                                  <button onClick={() => handleOnHold(req)} title="Put on hold"
                                    className="p-1.5 rounded-lg text-amber-500 hover:bg-amber-50 transition-colors">
                                    <PauseIcon className="w-4 h-4" />
                                  </button>
                                  <button onClick={() => { openView(req); setNotesMode('complete'); }} title="Mark complete"
                                    className="p-1.5 rounded-lg text-emerald-600 hover:bg-emerald-50 transition-colors">
                                    <CheckCircleIcon className="w-4 h-4" />
                                  </button>
                                </>
                              )}
                              {isMaintenance && !isDone && req.status === 'ON_HOLD' && (
                                <button onClick={() => handleResume(req)} title="Resume work"
                                  className="p-1.5 rounded-lg text-indigo-500 hover:bg-indigo-50 transition-colors">
                                  <ArrowPathIcon className="w-4 h-4" />
                                </button>
                              )}
                              {canManage && !isDone && (
                                <button onClick={() => { openView(req); }} title="Assign / Resolve"
                                  className="p-1.5 rounded-lg text-indigo-500 hover:bg-indigo-50 transition-colors">
                                  <UserPlusIcon className="w-4 h-4" />
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              <div className="py-3 px-4 border-t border-slate-50">
                <Pagination total={requests.length} safePage={safePage} perPage={perPage}
                  totalPages={totalPages} onPageChange={setPage} onPerPageChange={setPerPage} />
              </div>
            </>
          )}
        </div>

        {/* ── Create Request Slide-over ─────────────────────────────────────── */}
        {showCreate && canManage && (
          <div className="fixed inset-0 z-50 flex">
            <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={() => setShowCreate(false)} />
            <aside className="w-full max-w-md bg-white shadow-2xl flex flex-col overflow-hidden">
              <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
                <h2 className="font-bold text-slate-800 text-lg">New Maintenance Request</h2>
                <button onClick={() => setShowCreate(false)} className="p-2 rounded-xl text-slate-400 hover:bg-slate-100">
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
              <form onSubmit={handleCreate} className="flex-1 overflow-y-auto p-6 space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Room</label>
                  <select value={form.room} onChange={(e) => setForm((p) => ({ ...p, room: e.target.value }))}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white">
                    <option value="">— No specific room —</option>
                    {rooms.map((r) => <option key={r.id} value={r.id}>{r.room_number}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">
                    Location <span className="font-normal text-slate-400">(optional)</span>
                  </label>
                  <input type="text" value={form.location}
                    onChange={(e) => setForm((p) => ({ ...p, location: e.target.value }))}
                    placeholder="e.g. Lobby, Pool area, Parking..."
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Title *</label>
                  <input type="text" required value={form.title}
                    onChange={(e) => setForm((p) => ({ ...p, title: e.target.value }))}
                    placeholder="e.g. AC not cooling, Pipe leak..."
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Type *</label>
                    <select required value={form.request_type}
                      onChange={(e) => setForm((p) => ({ ...p, request_type: e.target.value }))}
                      className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white">
                      {REQUEST_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Priority *</label>
                    <select required value={form.priority}
                      onChange={(e) => setForm((p) => ({ ...p, priority: e.target.value }))}
                      className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white">
                      {PRIORITIES.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Description *</label>
                  <textarea required rows={3} value={form.description}
                    onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
                    placeholder="Describe the issue in detail..."
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 resize-none" />
                </div>
                {/* Assignment mode */}
                <div className="bg-slate-50 rounded-2xl p-4 space-y-3">
                  <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider">Assignment</p>
                  <div className="grid grid-cols-2 gap-2">
                    <button type="button"
                      onClick={() => setForm((p) => ({ ...p, assign_to: '' }))}
                      className={clsx(
                        'flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 text-sm font-semibold transition-colors',
                        form.assign_to === ''
                          ? 'border-violet-400 bg-violet-50 text-violet-700'
                          : 'border-slate-200 bg-white text-slate-500 hover:border-slate-300'
                      )}>
                      <InboxArrowDownIcon className="w-5 h-5" />
                      Post to Pool
                      <span className="text-[10px] font-normal text-center leading-tight">First available worker claims it</span>
                    </button>
                    <button type="button"
                      onClick={() => setForm((p) => ({ ...p, assign_to: p.assign_to || (staff[0]?.user?.toString() ?? '') }))}
                      className={clsx(
                        'flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 text-sm font-semibold transition-colors',
                        form.assign_to !== ''
                          ? 'border-blue-400 bg-blue-50 text-blue-700'
                          : 'border-slate-200 bg-white text-slate-500 hover:border-slate-300'
                      )}>
                      <UserPlusIcon className="w-5 h-5" />
                      Assign Directly
                      <span className="text-[10px] font-normal text-center leading-tight">Pick a specific worker</span>
                    </button>
                  </div>
                  {form.assign_to !== '' && (
                    <select value={form.assign_to}
                      onChange={(e) => setForm((p) => ({ ...p, assign_to: e.target.value }))}
                      className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white">
                      <option value="">— Select maintenance staff —</option>
                      {staff.map((s) => <option key={s.user} value={s.user}>{s.user_name}</option>)}
                    </select>
                  )}
                </div>

                <div className="flex gap-2 pt-1">
                  <button type="submit" disabled={saving}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors">
                    {saving ? 'Creating…' : form.assign_to ? 'Create & Assign' : 'Post to Pool'}
                  </button>
                  <button type="button" onClick={() => setShowCreate(false)}
                    className="px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-600 hover:bg-slate-50">
                    Cancel
                  </button>
                </div>
              </form>
            </aside>
          </div>
        )}

        {/* ── View / Assign / Action Slide-over ────────────────────────────── */}
        {viewReq && (
          <div className="fixed inset-0 z-50 flex">
            <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={() => { setViewReq(null); setNotesMode(null); }} />
            <aside className="w-full max-w-lg bg-white shadow-2xl flex flex-col overflow-hidden">
              <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
                <div>
                  <span className="font-mono text-xs text-slate-400">{viewReq.request_number}</span>
                  <h2 className="font-bold text-slate-800 text-lg leading-tight">{viewReq.title}</h2>
                </div>
                <button onClick={() => { setViewReq(null); setNotesMode(null); }} className="p-2 rounded-xl text-slate-400 hover:bg-slate-100">
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-6 space-y-5">
                {/* Badges */}
                <div className="flex items-center gap-2 flex-wrap">
                  <span className={clsx('text-xs font-semibold px-2.5 py-1 rounded-full', sColor(viewReq.status))}>
                    {choiceLabel(STATUSES, viewReq.status)}
                  </span>
                  <span className={clsx('text-xs font-semibold px-2.5 py-1 rounded-full', pColor(viewReq.priority))}>
                    {choiceLabel(PRIORITIES, viewReq.priority)}
                  </span>
                  <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 text-slate-600">
                    {choiceLabel(REQUEST_TYPES, viewReq.request_type)}
                  </span>
                  {viewReq.is_overdue && (
                    <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-red-100 text-red-700">Overdue</span>
                  )}
                </div>

                {/* Details grid */}
                <div className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
                  <div>
                    <p className="text-xs text-slate-400 font-medium mb-0.5">Room</p>
                    <p className="text-slate-700 font-medium">{viewReq.room_number ?? '—'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 font-medium mb-0.5">Location</p>
                    <p className="text-slate-700">{viewReq.location || '—'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 font-medium mb-0.5">Reported By</p>
                    <p className="text-slate-700">{viewReq.reported_by_name ?? '—'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 font-medium mb-0.5">Assigned To</p>
                    <p className="text-slate-700">{viewReq.assigned_to_name ?? <span className="italic text-slate-400">Unassigned</span>}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 font-medium mb-0.5">Created</p>
                    <p className="text-slate-600 text-xs">{formatDate(viewReq.created_at)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 font-medium mb-0.5">Started</p>
                    <p className="text-slate-600 text-xs">{formatDateTime(viewReq.started_at)}</p>
                  </div>
                  {viewReq.completed_at && (
                    <div>
                      <p className="text-xs text-slate-400 font-medium mb-0.5">Completed</p>
                      <p className="text-slate-600 text-xs">{formatDateTime(viewReq.completed_at)}</p>
                    </div>
                  )}
                  {viewReq.duration_hours != null && (
                    <div>
                      <p className="text-xs text-slate-400 font-medium mb-0.5">Duration</p>
                      <p className="text-slate-600 text-xs">{viewReq.duration_hours}h</p>
                    </div>
                  )}
                </div>

                {/* Description */}
                <div>
                  <p className="text-xs text-slate-400 font-medium mb-1">Description</p>
                  <p className="text-sm text-slate-700 bg-slate-50 rounded-xl px-3 py-2.5 leading-relaxed">{viewReq.description}</p>
                </div>

                {/* Resolution notes */}
                {viewReq.resolution_notes && (
                  <div>
                    <p className="text-xs text-slate-400 font-medium mb-1">Resolution Notes</p>
                    <p className="text-sm text-emerald-700 bg-emerald-50 rounded-xl px-3 py-2.5 leading-relaxed">{viewReq.resolution_notes}</p>
                  </div>
                )}

                {/* Assign section */}
                {canManage && viewReq.status !== 'COMPLETED' && viewReq.status !== 'CANCELLED' && (
                  <div className="bg-slate-50 rounded-2xl p-4 space-y-3">
                    <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider">Assign to Staff</p>
                    <div className="flex gap-2">
                      <select value={assignTo} onChange={(e) => setAssignTo(e.target.value)}
                        className="flex-1 px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white">
                        <option value="">— Select maintenance staff —</option>
                        {staff.map((s) => (
                          <option key={s.user} value={s.user}>{s.user_name}</option>
                        ))}
                      </select>
                      <button onClick={handleAssign} disabled={!assignTo || acting}
                        className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-semibold transition-colors">
                        {acting ? '…' : 'Assign'}
                      </button>
                    </div>
                  </div>
                )}

                {/* Actions */}
                {viewReq.status !== 'COMPLETED' && viewReq.status !== 'CANCELLED' && (
                  <div className="space-y-3">
                    {isMaintenance && viewReq.assigned_to === null && viewReq.status === 'PENDING' && (
                      <button onClick={() => handleClaim(viewReq)} disabled={acting}
                        className="w-full inline-flex items-center justify-center gap-2 bg-violet-600 hover:bg-violet-700 disabled:opacity-60 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors">
                        <HandRaisedIcon className="w-4 h-4" />
                        {acting ? 'Claiming…' : 'Claim This Task'}
                      </button>
                    )}
                    {isMaintenance && viewReq.status === 'ASSIGNED' && (
                      <button onClick={() => handleStart(viewReq)} disabled={acting}
                        className="w-full inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors">
                        <PlayIcon className="w-4 h-4" />
                        {acting ? 'Starting…' : 'Start Work'}
                      </button>
                    )}
                    {isMaintenance && viewReq.status === 'IN_PROGRESS' && (
                      <div className="grid grid-cols-2 gap-2">
                        <button onClick={() => handleOnHold(viewReq)} disabled={acting}
                          className="inline-flex items-center justify-center gap-2 bg-amber-500 hover:bg-amber-600 disabled:opacity-60 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors">
                          <PauseIcon className="w-4 h-4" />
                          {acting ? '…' : 'Put On Hold'}
                        </button>
                        {notesMode !== 'complete' && (
                          <button onClick={() => setNotesMode('complete')}
                            className="inline-flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors">
                            <CheckCircleIcon className="w-4 h-4" />
                            Mark Complete
                          </button>
                        )}
                      </div>
                    )}
                    {isMaintenance && viewReq.status === 'ON_HOLD' && (
                      <button onClick={() => handleResume(viewReq)} disabled={acting}
                        className="w-full inline-flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors">
                        <ArrowPathIcon className="w-4 h-4" />
                        {acting ? 'Resuming…' : 'Resume Work'}
                      </button>
                    )}
                    {canManage && notesMode !== 'resolve' && (
                      <button onClick={() => setNotesMode('resolve')}
                        className="w-full inline-flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors">
                        <CheckCircleIcon className="w-4 h-4" />
                        Resolve Request
                      </button>
                    )}

                    {notesMode && (
                      <div className="bg-slate-50 rounded-2xl p-4 space-y-3">
                        <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider">
                          {notesMode === 'complete' ? 'Completion Notes' : 'Resolution Notes'}
                        </p>
                        <textarea rows={3} value={notes} onChange={(e) => setNotes(e.target.value)}
                          placeholder="Describe what was done to resolve this issue..."
                          className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 resize-none" />
                        <div className="flex gap-2">
                          <button onClick={handleNotesSubmit} disabled={acting}
                            className="flex-1 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors">
                            {acting ? 'Saving…' : notesMode === 'complete' ? 'Mark Complete' : 'Mark Resolved'}
                          </button>
                          <button onClick={() => { setNotesMode(null); setNotes(''); }}
                            className="px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-600 hover:bg-slate-50">
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </aside>
          </div>
        )}

      </div>
    </Layout>
  );
}
