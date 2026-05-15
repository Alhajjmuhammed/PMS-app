'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import { reservationService, guestService, roomTypeService, roomService } from '@/lib/services';
import clsx from 'clsx';
import { format, parseISO } from 'date-fns';
import {
  PlusIcon, XMarkIcon, EyeIcon, PencilSquareIcon,
  XCircleIcon, CalendarDaysIcon, ChevronLeftIcon, ChevronRightIcon,
  CheckCircleIcon, UserIcon, ArrowRightCircleIcon, ArrowLeftCircleIcon,
  ClockIcon, HomeIcon,
} from '@heroicons/react/24/outline';

/* ── Types ─────────────────────────────────────────────────── */
interface GuestSummary {
  id: number;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  nationality?: string;
}

interface ReservationRoom {
  id: number;
  room: number | null;
  room_number: string | null;
  room_type: number | null;
  room_type_name: string | null;
  rate_per_night: string | number;
  total_rate: string | number;
  adults: number;
  children: number;
}

interface Reservation {
  id: number;
  confirmation_number: string;
  hotel: number;
  guest: GuestSummary;
  check_in_date: string;
  check_out_date: string;
  nights: number;
  adults: number;
  children: number;
  status: string;
  source: string;
  rate_plan?: string;
  total_amount: string | number;
  special_requests?: string;
  rooms: ReservationRoom[];
  created_at: string;
  created_by_name?: string | null;
  modified_by_name?: string | null;
  cancelled_by_name?: string | null;
  checked_in_by_name?: string | null;
  checked_out_by_name?: string | null;
  assigned_room_number?: string | null;
}

interface RoomType {
  id: number;
  name: string;
  base_rate?: string | number;
}

interface Guest {
  id: number;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
}

interface Room {
  id: number;
  room_number: string;
  room_type?: number;
  room_type_name?: string;
  status: string;
}

type Panel = 'none' | 'view' | 'create' | 'cancel' | 'checkin';

const STATUS_TABS = ['ALL', 'PENDING', 'CONFIRMED', 'CHECKED_IN', 'CHECKED_OUT', 'CANCELLED', 'NO_SHOW'];

const STATUS_COLORS: Record<string, string> = {
  PENDING:     'bg-yellow-100 text-yellow-800',
  CONFIRMED:   'bg-blue-100   text-blue-800',
  CHECKED_IN:  'bg-green-100  text-green-800',
  CHECKED_OUT: 'bg-gray-100   text-gray-800',
  CANCELLED:   'bg-red-100    text-red-800',
  NO_SHOW:     'bg-orange-100 text-orange-800',
  WAITLIST:    'bg-purple-100 text-purple-800',
};

const SOURCE_OPTIONS = [
  { value: 'DIRECT',       label: 'Direct Booking' },
  { value: 'PHONE',        label: 'Phone' },
  { value: 'EMAIL',        label: 'Email' },
  { value: 'WALK_IN',      label: 'Walk-in' },
  { value: 'WEBSITE',      label: 'Website' },
  { value: 'OTA',          label: 'OTA' },
  { value: 'CORPORATE',    label: 'Corporate' },
  { value: 'TRAVEL_AGENT', label: 'Travel Agent' },
];

const EMPTY_FORM = {
  guest_id: '',
  room_type_id: '',
  check_in_date: '',
  check_out_date: '',
  adults: '1',
  children: '0',
  source: 'DIRECT',
  special_requests: '',
};

/* ── Pagination helper ─────────────────────────────────────── */
const PAGE_SIZE = 15;

function paginate<T>(items: T[], page: number): T[] {
  return items.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
}

/* ── Status badge ──────────────────────────────────────────── */
function StatusBadge({ status }: { status: string }) {
  return (
    <span className={clsx('px-2 py-0.5 rounded-full text-xs font-semibold', STATUS_COLORS[status] ?? 'bg-gray-100 text-gray-700')}>
      {status.replace('_', ' ')}
    </span>
  );
}

/* ── Field helper ──────────────────────────────────────────── */
function Field({ label, value }: { label: string; value?: string | number | null }) {
  return (
    <div>
      <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
      <p className="text-sm font-medium text-gray-900 mt-0.5">{value || '—'}</p>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════ */
export default function ReservationsPage() {
  const [reservations, setReservations]     = useState<Reservation[]>([]);
  const [loading, setLoading]               = useState(true);
  const [statusFilter, setStatusFilter]     = useState('ALL');
  const [search, setSearch]                 = useState('');
  const [page, setPage]                     = useState(1);
  const [panel, setPanel]                   = useState<Panel>('none');
  const [selected, setSelected]             = useState<Reservation | null>(null);
  const [toast, setToast]                   = useState('');
  const [saving, setSaving]                 = useState(false);
  const [cancelReason, setCancelReason]     = useState('');
  const [form, setForm]                     = useState({ ...EMPTY_FORM });
  const [formError, setFormError]           = useState('');
  const [guests, setGuests]                 = useState<Guest[]>([]);
  const [roomTypes, setRoomTypes]           = useState<RoomType[]>([]);
  const [rooms, setRooms]                   = useState<Room[]>([]);
  const [checkInRoomId, setCheckInRoomId]   = useState('');

  /* load data */
  useEffect(() => { loadAll(); }, []);

  async function loadAll() {
    setLoading(true);
    try {
      const [resData, guestData, rtData, roomData] = await Promise.all([
        reservationService.getAll({ page_size: 500 }),
        guestService.getAll({ page_size: 500 }),
        roomTypeService.getAll(),
        roomService.getAll({ page_size: 500 }),
      ]);
      setReservations(resData.results ?? resData);
      setGuests(guestData.results ?? guestData);
      setRoomTypes(rtData.results ?? rtData);
      setRooms(roomData.results ?? roomData);
    } catch {
      showToast('Failed to load data');
    } finally {
      setLoading(false);
    }
  }

  function showToast(msg: string) {
    setToast(msg);
    setTimeout(() => setToast(''), 3500);
  }

  /* filtering */
  const filtered = reservations.filter(r => {
    const matchStatus = statusFilter === 'ALL' || r.status === statusFilter;
    const q = search.toLowerCase();
    const matchSearch = !q
      || r.confirmation_number?.toLowerCase().includes(q)
      || r.guest?.first_name?.toLowerCase().includes(q)
      || r.guest?.last_name?.toLowerCase().includes(q)
      || r.guest?.email?.toLowerCase().includes(q);
    return matchStatus && matchSearch;
  });

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const paged = paginate(filtered, page);

  /* open panels */
  function openView(r: Reservation) { setSelected(r); setPanel('view'); }
  function openCreate() { setForm({ ...EMPTY_FORM }); setFormError(''); setPanel('create'); }
  function openCancel(r: Reservation) { setSelected(r); setCancelReason(''); setPanel('cancel'); }
  function openCheckin(r: Reservation) { setSelected(r); setCheckInRoomId(''); setPanel('checkin'); }
  function closePanel() { setPanel('none'); setSelected(null); }

  /* form field change */
  function fc(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) {
    setForm(p => ({ ...p, [e.target.name]: e.target.value }));
  }

  /* CREATE */
  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setFormError('');
    if (!form.guest_id) { setFormError('Please select a guest.'); return; }
    if (!form.room_type_id) { setFormError('Please select a room type.'); return; }
    if (!form.check_in_date || !form.check_out_date) { setFormError('Check-in and check-out dates are required.'); return; }
    if (form.check_out_date <= form.check_in_date) { setFormError('Check-out must be after check-in.'); return; }

    setSaving(true);
    try {
      await reservationService.create({
        guest_id: parseInt(form.guest_id),
        room_type_id: parseInt(form.room_type_id),
        check_in_date: form.check_in_date,
        check_out_date: form.check_out_date,
        adults: parseInt(form.adults) || 1,
        children: parseInt(form.children) || 0,
        source: form.source,
        special_requests: form.special_requests,
      });
      showToast('Reservation created successfully');
      closePanel();
      loadAll();
    } catch (err: any) {
      const msg = err?.response?.data;
      setFormError(typeof msg === 'string' ? msg : JSON.stringify(msg) ?? 'Failed to create reservation');
    } finally {
      setSaving(false);
    }
  }

  /* CANCEL */
  async function handleCancel() {
    if (!selected) return;
    setSaving(true);
    try {
      await reservationService.cancel(selected.id, cancelReason);
      showToast('Reservation cancelled');
      closePanel();
      loadAll();
    } catch (err: any) {
      showToast(err?.response?.data?.error ?? 'Failed to cancel reservation');
    } finally {
      setSaving(false);
    }
  }

  /* CONFIRM */
  async function handleConfirm(r: Reservation) {
    setSaving(true);
    try {
      await reservationService.confirm(r.id);
      showToast('Reservation confirmed');
      loadAll();
      // refresh selected if panel is open
      setSelected(prev => prev?.id === r.id ? { ...prev, status: 'CONFIRMED' } : prev);
    } catch (err: any) {
      showToast(err?.response?.data?.error ?? 'Failed to confirm');
    } finally {
      setSaving(false);
    }
  }

  /* CHECK-IN */
  async function handleCheckin() {
    if (!selected || !checkInRoomId) return;
    setSaving(true);
    try {
      await reservationService.checkIn(selected.id, parseInt(checkInRoomId));
      showToast('Guest checked in successfully');
      closePanel();
      loadAll();
    } catch (err: any) {
      showToast(err?.response?.data?.error ?? 'Failed to check in');
    } finally {
      setSaving(false);
    }
  }

  /* CHECK-OUT */
  async function handleCheckout(r: Reservation) {
    if (!confirm(`Check out ${r.guest?.first_name} ${r.guest?.last_name}?`)) return;
    setSaving(true);
    try {
      await reservationService.checkOut(r.id);
      showToast('Guest checked out successfully');
      closePanel();
      loadAll();
    } catch (err: any) {
      showToast(err?.response?.data?.error ?? 'Failed to check out');
    } finally {
      setSaving(false);
    }
  }

  /* NO-SHOW */
  async function handleNoShow(r: Reservation) {
    if (!confirm(`Mark ${r.guest?.first_name} ${r.guest?.last_name} as No-Show?`)) return;
    setSaving(true);
    try {
      await reservationService.noShow(r.id);
      showToast('Marked as no-show');
      closePanel();
      loadAll();
    } catch (err: any) {
      showToast(err?.response?.data?.error ?? 'Failed to mark no-show');
    } finally {
      setSaving(false);
    }
  }

  const today = new Date().toISOString().split('T')[0];

  /* ── Render ──────────────────────────────────────────────── */
  return (
    <Layout>
      {/* Toast */}
      {toast && (
        <div className="fixed top-5 right-5 z-[100] flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium bg-emerald-600 text-white">
          <CheckCircleIcon className="w-5 h-5 flex-shrink-0" />
          {toast}
        </div>
      )}

      <div className="p-5 lg:p-6 space-y-5">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-1.5 text-sm text-slate-400">
          <HomeIcon className="w-4 h-4" />
          <span>Home</span>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <span className="text-slate-700 font-medium">Reservations</span>
        </nav>

        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center flex-shrink-0">
              <CalendarDaysIcon className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Reservations</h1>
              <p className="text-slate-500 text-sm mt-0.5">{filtered.length} reservation{filtered.length !== 1 ? 's' : ''}</p>
            </div>
          </div>
          <button
            onClick={openCreate}
            className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-sm"
          >
            <PlusIcon className="w-4 h-4" />
            New Reservation
          </button>
        </div>

        {/* Stats cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-4">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total</p>
            <p className="text-2xl font-bold text-slate-800 mt-1">{reservations.length}</p>
          </div>
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-4">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Confirmed</p>
            <p className="text-2xl font-bold text-blue-600 mt-1">{reservations.filter(r => r.status === 'CONFIRMED').length}</p>
          </div>
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-4">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Checked In</p>
            <p className="text-2xl font-bold text-emerald-600 mt-1">{reservations.filter(r => r.status === 'CHECKED_IN').length}</p>
          </div>
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-4">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Pending</p>
            <p className="text-2xl font-bold text-amber-600 mt-1">{reservations.filter(r => r.status === 'PENDING').length}</p>
          </div>
        </div>

        {/* Search + filter row */}
        <div className="flex flex-wrap gap-3">
          <input
            type="text"
            placeholder="Search confirmation #, guest name…"
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }}
            className="flex-1 min-w-[200px] px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
          <div className="flex gap-1.5 flex-wrap">
            {STATUS_TABS.map(s => (
              <button
                key={s}
                onClick={() => { setStatusFilter(s); setPage(1); }}
                className={clsx(
                  'px-3 py-2 text-xs font-semibold rounded-xl transition-colors',
                  statusFilter === s ? 'bg-blue-600 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                )}
              >
                {s.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : paged.length === 0 ? (
          <div className="flex flex-col items-center py-20 text-slate-400">
            <CalendarDaysIcon className="w-12 h-12 mb-3 opacity-40" />
            <p className="font-medium">No reservations found</p>
            {search && <p className="text-sm mt-1">Try clearing the search</p>}
          </div>
        ) : (
          <>
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-100 bg-slate-50/60">
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Confirmation #</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Guest</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Room Type</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Room #</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Check-in</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Check-out</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Nights</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Total</th>
                      <th className="text-center px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {paged.map(r => (
                      <tr key={r.id} className="hover:bg-slate-50/50 transition-colors">
                        <td className="px-4 py-3">
                          <span className="font-mono text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-md">{r.confirmation_number}</span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center flex-shrink-0">
                              <span className="text-white text-xs font-bold">
                                {r.guest?.first_name?.[0]}{r.guest?.last_name?.[0]}
                              </span>
                            </div>
                            <span className="font-medium text-slate-800">
                              {r.guest?.first_name} {r.guest?.last_name}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-slate-600 text-xs">
                          {r.rooms?.[0]?.room_type_name ?? '—'}
                        </td>
                        <td className="px-4 py-3 text-slate-600 text-xs font-medium">
                          {r.assigned_room_number
                            ? <span className="bg-green-50 text-green-700 px-2 py-0.5 rounded font-semibold">{r.assigned_room_number}</span>
                            : <span className="text-slate-300">—</span>}
                        </td>
                        <td className="px-4 py-3 text-slate-700 text-xs">
                          {format(parseISO(r.check_in_date), 'dd MMM yyyy')}
                        </td>
                        <td className="px-4 py-3 text-slate-700 text-xs">
                          {format(parseISO(r.check_out_date), 'dd MMM yyyy')}
                        </td>
                        <td className="px-4 py-3 text-slate-600 text-xs">{r.nights ?? '—'}</td>
                        <td className="px-4 py-3"><StatusBadge status={r.status} /></td>
                        <td className="px-4 py-3 text-right font-semibold text-slate-900">
                          ${Number(r.total_amount).toLocaleString()}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center justify-center gap-1">
                            <button
                              onClick={() => openView(r)}
                              title="View"
                              className="p-1.5 rounded hover:bg-blue-50 text-blue-600 transition-colors"
                            >
                              <EyeIcon className="w-4 h-4" />
                            </button>
                            {!['CANCELLED', 'CHECKED_OUT', 'NO_SHOW'].includes(r.status) && (
                              <button
                                onClick={() => openCancel(r)}
                                title="Cancel"
                                className="p-1.5 rounded hover:bg-red-50 text-red-500 transition-colors"
                              >
                                <XCircleIcon className="w-4 h-4" />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between flex-wrap gap-3 pt-1">
                <span className="text-sm text-slate-500">{filtered.length} total</span>
                <div className="flex items-center gap-1">
                  <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
                    className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-100 disabled:opacity-40">
                    <ChevronLeftIcon className="w-4 h-4" />
                  </button>
                  <span className="px-2 text-sm text-slate-600">Page {page} of {totalPages}</span>
                  <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}
                    className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-100 disabled:opacity-40">
                    <ChevronRightIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* ── Slide panels ────────────────────────────────────── */}
      {panel !== 'none' && (
        <div className="fixed inset-0 z-50 flex">
          <div className="flex-1 bg-black/30 backdrop-blur-sm" onClick={closePanel} />
          <aside className="w-full max-w-lg bg-white shadow-2xl flex flex-col overflow-y-auto animate-slide-in-right">

            {/* ── VIEW panel ── */}
            {panel === 'view' && selected && (
              <>
                <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
                      <CalendarDaysIcon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h2 className="font-semibold text-gray-900">{selected.confirmation_number}</h2>
                      <p className="text-xs text-gray-500">Reservation Details</p>
                    </div>
                  </div>
                  <button onClick={closePanel} className="p-2 rounded-full hover:bg-gray-200 transition-colors">
                    <XMarkIcon className="w-5 h-5 text-gray-500" />
                  </button>
                </div>

                <div className="flex-1 px-6 py-5 space-y-6">
                  {/* Status */}
                  <div className="flex items-center gap-3">
                    <StatusBadge status={selected.status} />
                    <span className="text-sm text-gray-500">{selected.source?.replace('_', ' ')}</span>
                  </div>

                  {/* Guest */}
                  <div className="bg-blue-50 rounded-xl p-4">
                    <p className="text-xs text-blue-600 font-semibold uppercase tracking-wide mb-2 flex items-center gap-1">
                      <UserIcon className="w-3.5 h-3.5" /> Guest
                    </p>
                    <p className="font-semibold text-gray-900">
                      {selected.guest?.first_name} {selected.guest?.last_name}
                    </p>
                    {selected.guest?.email && <p className="text-sm text-gray-600">{selected.guest.email}</p>}
                    {selected.guest?.phone && <p className="text-sm text-gray-600">{selected.guest.phone}</p>}
                    {selected.guest?.nationality && <p className="text-xs text-gray-500 mt-1">{selected.guest.nationality}</p>}
                  </div>

                  {/* Dates */}
                  <div className="grid grid-cols-3 gap-4">
                    <Field label="Check-in"   value={format(parseISO(selected.check_in_date), 'dd MMM yyyy')} />
                    <Field label="Check-out"  value={format(parseISO(selected.check_out_date), 'dd MMM yyyy')} />
                    <Field label="Nights"     value={selected.nights} />
                  </div>

                  {/* Occupancy */}
                  <div className="grid grid-cols-2 gap-4">
                    <Field label="Adults"   value={selected.adults} />
                    <Field label="Children" value={selected.children} />
                  </div>

                  {/* Rooms */}
                  {(selected.rooms?.length > 0 || selected.assigned_room_number) && (
                    <div>
                      <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">Rooms</p>
                      <div className="space-y-2">
                        {selected.rooms?.length > 0 ? selected.rooms.map(room => (
                          <div key={room.id} className="bg-gray-50 rounded-lg px-4 py-3 flex justify-between items-center">
                            <div>
                              <p className="font-medium text-gray-900">{room.room_type_name ?? 'Room'}</p>
                              {(room.room_number || selected.assigned_room_number) && (
                                <p className="text-xs text-green-600 font-semibold">Room #{room.room_number ?? selected.assigned_room_number}</p>
                              )}
                            </div>
                            <div className="text-right">
                              <p className="font-semibold text-gray-900">${Number(room.total_rate).toLocaleString()}</p>
                              <p className="text-xs text-gray-500">${Number(room.rate_per_night).toLocaleString()}/night</p>
                            </div>
                          </div>
                        )) : (
                          /* Fallback: no ReservationRoom records but we know the assigned room */
                          <div className="bg-gray-50 rounded-lg px-4 py-3 flex justify-between items-center">
                            <div>
                              <p className="font-medium text-gray-900">Assigned Room</p>
                              <p className="text-xs text-green-600 font-semibold">Room #{selected.assigned_room_number}</p>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Financial */}
                  <div className="bg-gray-50 rounded-xl p-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Total Amount</span>
                      <span className="text-xl font-bold text-gray-900">${Number(selected.total_amount).toLocaleString()}</span>
                    </div>
                  </div>

                  {/* Special requests */}
                  {selected.special_requests && (
                    <div>
                      <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Special Requests</p>
                      <p className="text-sm text-gray-700 bg-yellow-50 rounded-lg px-3 py-2">{selected.special_requests}</p>
                    </div>
                  )}

                  {/* Assigned room (once checked in) */}
                  {selected.assigned_room_number && (
                    <div className="bg-green-50 rounded-xl px-4 py-3 flex justify-between items-center">
                      <span className="text-xs font-semibold text-green-700 uppercase tracking-wide">Assigned Room</span>
                      <span className="font-bold text-green-800 text-sm">Room {selected.assigned_room_number}</span>
                    </div>
                  )}

                  {/* Staff activity */}
                  {(selected.created_by_name || selected.modified_by_name || selected.cancelled_by_name ||
                    selected.checked_in_by_name || selected.checked_out_by_name) && (
                    <div>
                      <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">Staff Activity</p>
                      <div className="space-y-1.5">
                        {selected.created_by_name && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-500">Created by</span>
                            <span className="font-medium text-gray-800">{selected.created_by_name}</span>
                          </div>
                        )}
                        {selected.modified_by_name && ['CONFIRMED', 'NO_SHOW'].includes(selected.status) && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-500">
                              {selected.status === 'CONFIRMED' ? 'Confirmed by' : 'Marked no-show by'}
                            </span>
                            <span className="font-medium text-gray-800">{selected.modified_by_name}</span>
                          </div>
                        )}
                        {selected.checked_in_by_name && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-500">Checked in by</span>
                            <span className="font-medium text-gray-800">{selected.checked_in_by_name}</span>
                          </div>
                        )}
                        {selected.checked_out_by_name && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-500">Checked out by</span>
                            <span className="font-medium text-gray-800">{selected.checked_out_by_name}</span>
                          </div>
                        )}
                        {selected.cancelled_by_name && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-500">Cancelled by</span>
                            <span className="font-medium text-gray-800">{selected.cancelled_by_name}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Booked on */}
                  <Field label="Booked on" value={format(parseISO(selected.created_at), 'dd MMM yyyy, HH:mm')} />
                </div>

                {/* Footer actions */}
                <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 space-y-2">
                  {/* Row 1: status-advancing actions */}
                  <div className="flex gap-2">
                    {selected.status === 'PENDING' && (
                      <button
                        onClick={() => handleConfirm(selected)}
                        disabled={saving}
                        className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white rounded-lg text-sm font-semibold transition-colors flex items-center justify-center gap-1"
                      >
                        <CheckCircleIcon className="w-4 h-4" /> Confirm
                      </button>
                    )}
                    {selected.status === 'CONFIRMED' && (
                      <button
                        onClick={() => openCheckin(selected)}
                        disabled={saving}
                        className="flex-1 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-60 text-white rounded-lg text-sm font-semibold transition-colors flex items-center justify-center gap-1"
                      >
                        <ArrowRightCircleIcon className="w-4 h-4" /> Check In
                      </button>
                    )}
                    {selected.status === 'CHECKED_IN' && (
                      <button
                        onClick={() => handleCheckout(selected)}
                        disabled={saving}
                        className="flex-1 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white rounded-lg text-sm font-semibold transition-colors flex items-center justify-center gap-1"
                      >
                        <ArrowLeftCircleIcon className="w-4 h-4" /> Check Out
                      </button>
                    )}
                    {['PENDING', 'CONFIRMED'].includes(selected.status) && (
                      <button
                        onClick={() => handleNoShow(selected)}
                        disabled={saving}
                        className="flex-1 py-2 bg-orange-500 hover:bg-orange-600 disabled:opacity-60 text-white rounded-lg text-sm font-semibold transition-colors flex items-center justify-center gap-1"
                      >
                        <ClockIcon className="w-4 h-4" /> No-Show
                      </button>
                    )}
                  </div>
                  {/* Row 2: cancel + close */}
                  <div className="flex gap-2">
                    {!['CANCELLED', 'CHECKED_OUT', 'NO_SHOW'].includes(selected.status) && (
                      <button
                        onClick={() => openCancel(selected)}
                        className="flex-1 py-2 border border-red-300 text-red-600 rounded-lg text-sm font-semibold hover:bg-red-50 transition-colors flex items-center justify-center gap-1"
                      >
                        <XCircleIcon className="w-4 h-4" /> Cancel
                      </button>
                    )}
                    <button onClick={closePanel} className="flex-1 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg text-sm font-semibold transition-colors">
                      Close
                    </button>
                  </div>
                </div>
              </>
            )}

            {/* ── CHECK-IN panel ── */}
            {panel === 'checkin' && selected && (
              <>
                <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-green-700 flex items-center justify-center">
                      <ArrowRightCircleIcon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h2 className="font-semibold text-gray-900">Check In Guest</h2>
                      <p className="text-xs text-gray-500">{selected.confirmation_number}</p>
                    </div>
                  </div>
                  <button onClick={closePanel} className="p-2 rounded-full hover:bg-gray-200 transition-colors">
                    <XMarkIcon className="w-5 h-5 text-gray-500" />
                  </button>
                </div>

                <div className="flex-1 px-6 py-5 space-y-5">
                  <div className="bg-green-50 rounded-xl p-4 space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Guest</span>
                      <span className="font-medium">{selected.guest?.first_name} {selected.guest?.last_name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Check-in</span>
                      <span>{format(parseISO(selected.check_in_date), 'dd MMM yyyy')}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Check-out</span>
                      <span>{format(parseISO(selected.check_out_date), 'dd MMM yyyy')}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Nights</span>
                      <span>{selected.nights}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Room type</span>
                      <span>{selected.rooms?.[0]?.room_type_name ?? '—'}</span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Assign Room <span className="text-red-500">*</span>
                    </label>
                    {(() => {
                      const reservedTypeId = selected.rooms?.[0]?.room_type ?? null;
                      const available = rooms.filter(r =>
                        ['VC', 'VD'].includes(r.status) &&
                        (reservedTypeId === null || r.room_type === reservedTypeId)
                      );
                      const allAvailable = rooms.filter(r => ['VC', 'VD'].includes(r.status));
                      return available.length === 0 ? (
                        <div className="space-y-2">
                          <p className="text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
                            No vacant rooms of type <strong>{selected.rooms?.[0]?.room_type_name ?? 'reserved type'}</strong> available.
                          </p>
                          {allAvailable.length > 0 && (
                            <>
                              <p className="text-xs text-gray-500">You can assign a different room type if needed:</p>
                              <select
                                value={checkInRoomId}
                                onChange={e => setCheckInRoomId(e.target.value)}
                                className="w-full border border-amber-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"
                              >
                                <option value="">— Select a room —</option>
                                {allAvailable.map(r => (
                                  <option key={r.id} value={r.id}>
                                    Room {r.room_number}{r.room_type_name ? ` · ${r.room_type_name}` : ''} · {r.status === 'VC' ? 'Vacant Clean' : 'Vacant Dirty'}
                                  </option>
                                ))}
                              </select>
                            </>
                          )}
                        </div>
                      ) : (
                        <select
                          value={checkInRoomId}
                          onChange={e => setCheckInRoomId(e.target.value)}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
                        >
                          <option value="">— Select a room —</option>
                          {available.map(r => (
                            <option key={r.id} value={r.id}>
                              Room {r.room_number}{r.room_type_name ? ` · ${r.room_type_name}` : ''} · {r.status === 'VC' ? 'Vacant Clean' : 'Vacant Dirty'}
                            </option>
                          ))}
                        </select>
                      );
                    })()}
                  </div>
                </div>

                <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex gap-3">
                  <button
                    onClick={handleCheckin}
                    disabled={saving || !checkInRoomId}
                    className="flex-1 bg-green-600 hover:bg-green-700 disabled:opacity-60 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors"
                  >
                    {saving ? 'Checking in…' : 'Confirm Check-In'}
                  </button>
                  <button onClick={closePanel} className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2.5 rounded-lg text-sm transition-colors">
                    Cancel
                  </button>
                </div>
              </>
            )}

            {/* ── CREATE panel ── */}
            {panel === 'create' && (
              <>
                <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center">
                      <PlusIcon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h2 className="font-semibold text-gray-900">New Reservation</h2>
                      <p className="text-xs text-gray-500">Fill in the details below</p>
                    </div>
                  </div>
                  <button onClick={closePanel} className="p-2 rounded-full hover:bg-gray-200 transition-colors">
                    <XMarkIcon className="w-5 h-5 text-gray-500" />
                  </button>
                </div>

                <form onSubmit={handleCreate} className="flex-1 px-6 py-5 space-y-4">
                  {formError && (
                    <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
                      {formError}
                    </div>
                  )}

                  {/* Guest */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Guest <span className="text-red-500">*</span></label>
                    <select name="guest_id" value={form.guest_id} onChange={fc}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
                      <option value="">— Select guest —</option>
                      {guests.map(g => (
                        <option key={g.id} value={g.id}>
                          {g.first_name} {g.last_name}{g.phone ? ` · ${g.phone}` : ''}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Room Type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Room Type <span className="text-red-500">*</span></label>
                    <select name="room_type_id" value={form.room_type_id} onChange={fc}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
                      <option value="">— Select room type —</option>
                      {roomTypes.map(rt => (
                        <option key={rt.id} value={rt.id}>
                          {rt.name}{rt.base_rate ? ` — $${Number(rt.base_rate).toLocaleString()}/night` : ''}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Dates */}
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Check-in <span className="text-red-500">*</span></label>
                      <input type="date" name="check_in_date" value={form.check_in_date} min={today} onChange={fc}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Check-out <span className="text-red-500">*</span></label>
                      <input type="date" name="check_out_date" value={form.check_out_date} min={form.check_in_date || today} onChange={fc}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                    </div>
                  </div>

                  {/* Occupancy */}
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Adults</label>
                      <input type="number" name="adults" value={form.adults} min="1" max="10" onChange={fc}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Children</label>
                      <input type="number" name="children" value={form.children} min="0" max="10" onChange={fc}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                    </div>
                  </div>

                  {/* Source */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Booking Source</label>
                    <select name="source" value={form.source} onChange={fc}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
                      {SOURCE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                  </div>

                  {/* Special requests */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Special Requests</label>
                    <textarea name="special_requests" value={form.special_requests} onChange={fc} rows={3}
                      placeholder="Late check-out, extra pillows, accessibility needs…"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none" />
                  </div>

                  <div className="pt-2 flex gap-3">
                    <button type="submit" disabled={saving}
                      className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors">
                      {saving ? 'Creating…' : 'Create Reservation'}
                    </button>
                    <button type="button" onClick={closePanel}
                      className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2.5 rounded-lg text-sm transition-colors">
                      Cancel
                    </button>
                  </div>
                </form>
              </>
            )}

            {/* ── CANCEL panel ── */}
            {panel === 'cancel' && selected && (
              <>
                <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-red-400 to-red-600 flex items-center justify-center">
                      <XCircleIcon className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h2 className="font-semibold text-gray-900">Cancel Reservation</h2>
                      <p className="text-xs text-gray-500">{selected.confirmation_number}</p>
                    </div>
                  </div>
                  <button onClick={closePanel} className="p-2 rounded-full hover:bg-gray-200 transition-colors">
                    <XMarkIcon className="w-5 h-5 text-gray-500" />
                  </button>
                </div>

                <div className="flex-1 px-6 py-5 space-y-5">
                  <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-800">
                    <p className="font-semibold">You are about to cancel this reservation.</p>
                    <p className="mt-1 text-red-600">This action cannot be undone.</p>
                  </div>

                  <div className="bg-gray-50 rounded-xl p-4 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Guest</span>
                      <span className="font-medium">{selected.guest?.first_name} {selected.guest?.last_name}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Check-in</span>
                      <span>{format(parseISO(selected.check_in_date), 'dd MMM yyyy')}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Check-out</span>
                      <span>{format(parseISO(selected.check_out_date), 'dd MMM yyyy')}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Total</span>
                      <span className="font-semibold">${Number(selected.total_amount).toLocaleString()}</span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Cancellation Reason <span className="text-gray-400">(optional)</span></label>
                    <textarea
                      value={cancelReason}
                      onChange={e => setCancelReason(e.target.value)}
                      rows={3}
                      placeholder="e.g. Guest changed travel plans…"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400 resize-none"
                    />
                  </div>
                </div>

                <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex gap-3">
                  <button
                    onClick={handleCancel}
                    disabled={saving}
                    className="flex-1 bg-red-600 hover:bg-red-700 disabled:opacity-60 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors"
                  >
                    {saving ? 'Cancelling…' : 'Confirm Cancellation'}
                  </button>
                  <button onClick={closePanel}
                    className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2.5 rounded-lg text-sm transition-colors">
                    Go Back
                  </button>
                </div>
              </>
            )}
          </aside>
        </div>
      )}
    </Layout>
  );
}
