'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import { guestService } from '@/lib/services';
import clsx from 'clsx';
import {
  PlusIcon, XMarkIcon, EyeIcon, PencilSquareIcon, TrashIcon,
  CheckCircleIcon, UserIcon, ChevronLeftIcon, ChevronRightIcon,
  IdentificationIcon, HomeIcon,
} from '@heroicons/react/24/outline';

/* ── Types ── */
interface Guest {
  id: number;
  first_name: string;
  last_name: string;
  full_name?: string;
  email?: string;
  phone: string;
  gender?: string;
  date_of_birth?: string;
  nationality?: string;
  id_type?: string;
  id_number?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  vip_level?: number;
  is_blacklisted?: boolean;
  total_stays?: number;
  total_revenue?: string | number;
  created_at?: string;
}

const GENDER_OPTIONS = [
  { value: '', label: '— Select —' },
  { value: 'M', label: 'Male' },
  { value: 'F', label: 'Female' },
  { value: 'O', label: 'Other' },
];

const ID_TYPE_OPTIONS = [
  { value: '', label: '— Select —' },
  { value: 'PASSPORT', label: 'Passport' },
  { value: 'NATIONAL_ID', label: 'National ID' },
  { value: 'DRIVING_LICENSE', label: "Driver's License" },
  { value: 'RESIDENCE_PERMIT', label: 'Residence Permit' },
  { value: 'OTHER', label: 'Other' },
];

const EMPTY_FORM = {
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  gender: '',
  date_of_birth: '',
  nationality: '',
  id_type: '',
  id_number: '',
  address: '',
  city: '',
  state: '',
  country: '',
  postal_code: '',
};

/* ── Auto-generate guest ID ── */
function generateGuestId(): string {
  const now = new Date();
  const yr = now.getFullYear();
  const mo = String(now.getMonth() + 1).padStart(2, '0');
  const rand = Math.random().toString(36).substring(2, 6).toUpperCase();
  return `GX-${yr}${mo}-${rand}`;
}

/* ── Pagination ── */
function Pagination({ total, safePage, perPage, totalPages, onPageChange, onPerPageChange }: any) {
  if (total === 0) return null;
  const start = (safePage - 1) * perPage + 1;
  const end = Math.min(safePage * perPage, total);
  return (
    <div className="flex items-center justify-between flex-wrap gap-3 pt-2">
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <span>Rows per page:</span>
        <select value={perPage} onChange={(e) => onPerPageChange(Number(e.target.value))}
          className="border border-slate-200 rounded-lg px-2 py-1 text-sm text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-300">
          {[5, 10, 20, 50].map((n) => <option key={n} value={n}>{n}</option>)}
        </select>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-sm text-slate-500">{start}–{end} of {total}</span>
        <div className="flex items-center gap-1">
          <button onClick={() => onPageChange(Math.max(1, safePage - 1))} disabled={safePage === 1}
            className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
            <ChevronLeftIcon className="w-4 h-4" />
          </button>
          {Array.from({ length: totalPages }).map((_, i) => {
            const pg = i + 1;
            const near = pg === 1 || pg === totalPages || Math.abs(pg - safePage) <= 1;
            const gap = !near && (pg === 2 || pg === totalPages - 1);
            if (!near && !gap) return null;
            if (gap) return <span key={pg} className="px-1 text-slate-400 text-sm">…</span>;
            return (
              <button key={pg} onClick={() => onPageChange(pg)}
                className={clsx('w-8 h-8 rounded-lg text-sm font-semibold transition-colors',
                  pg === safePage ? 'bg-blue-600 text-white shadow-sm' : 'border border-slate-200 text-slate-600 hover:bg-slate-100')}>
                {pg}
              </button>
            );
          })}
          <button onClick={() => onPageChange(Math.min(totalPages, safePage + 1))} disabled={safePage === totalPages}
            className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
            <ChevronRightIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

/* ── Page ── */
export default function GuestsPage() {
  const [guests, setGuests] = useState<Guest[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [search, setSearch] = useState('');

  // Panels
  const [editingId, setEditingId] = useState<number | 'new' | null>(null);
  const [viewingGuest, setViewingGuest] = useState<Guest | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<Guest | null>(null);
  const [form, setForm] = useState<typeof EMPTY_FORM>(EMPTY_FORM);

  // Toast
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);

  // Pagination
  const [perPage, setPerPage] = useState(10);
  const [page, setPage] = useState(1);

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  };

  const load = async (searchTerm?: string) => {
    setLoading(true);
    try {
      const params = searchTerm ? { search: searchTerm } : {};
      const data = await guestService.getAll(params);
      setGuests(data.results || data);
    } catch {
      showToast('Failed to load guests', false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);
  useEffect(() => { setPage(1); }, [search, perPage]);

  const totalPages = Math.max(1, Math.ceil(guests.length / perPage));
  const safePage = Math.min(page, totalPages);
  const paginated = guests.slice((safePage - 1) * perPage, safePage * perPage);

  /* ── Panel helpers ── */
  const openNew = () => {
    setForm({ ...EMPTY_FORM, id_number: generateGuestId() });
    setEditingId('new');
  };
  const openEdit = (g: Guest) => {
    setForm({
      first_name: g.first_name,
      last_name: g.last_name,
      email: g.email ?? '',
      phone: g.phone,
      gender: g.gender ?? '',
      date_of_birth: g.date_of_birth ?? '',
      nationality: g.nationality ?? '',
      id_type: g.id_type ?? '',
      id_number: g.id_number ?? '',
      address: g.address ?? '',
      city: g.city ?? '',
      state: g.state ?? '',
      country: g.country ?? '',
      postal_code: g.postal_code ?? '',
    });
    setEditingId(g.id);
  };
  const closePanel = () => setEditingId(null);

  const inp = (key: keyof typeof EMPTY_FORM) => ({
    value: form[key],
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value })),
  });

  /* ── Save ── */
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.first_name.trim()) { showToast('First name is required', false); return; }
    if (!form.last_name.trim()) { showToast('Last name is required', false); return; }
    if (!form.phone.trim()) { showToast('Phone number is required', false); return; }
    setSaving(true);
    try {
      const payload: any = {
        first_name: form.first_name,
        last_name: form.last_name,
        phone: form.phone,
        gender: form.gender || undefined,
        date_of_birth: form.date_of_birth || undefined,
        nationality: form.nationality || undefined,
        id_type: form.id_type || undefined,
        id_number: form.id_number || undefined,
        address: form.address || undefined,
        city: form.city || undefined,
        state: form.state || undefined,
        country: form.country || undefined,
        postal_code: form.postal_code || undefined,
      };
      if (form.email) payload.email = form.email;
      if (editingId === 'new') {
        await guestService.create(payload);
        showToast('Guest created successfully');
      } else {
        await guestService.update(editingId as number, payload);
        showToast('Guest updated successfully');
      }
      closePanel();
      await load(search || undefined);
    } catch (err: any) {
      const detail = err?.response?.data;
      const msg = typeof detail === 'object' ? Object.values(detail).flat().join(' ') : 'Failed to save guest';
      showToast(msg as string, false);
    } finally {
      setSaving(false);
    }
  };

  /* ── Delete ── */
  const handleDelete = async () => {
    if (!deleteConfirm) return;
    try {
      await guestService.delete(deleteConfirm.id);
      showToast(`"${deleteConfirm.first_name} ${deleteConfirm.last_name}" deleted`);
      setDeleteConfirm(null);
      setViewingGuest(null);
      await load(search || undefined);
    } catch {
      showToast('Failed to delete guest', false);
    }
  };

  /* ── Search ── */
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    load(search || undefined);
  };

  const genderLabel = (g?: string) => GENDER_OPTIONS.find((o) => o.value === g)?.label ?? g ?? '—';
  const idTypeLabel = (t?: string) => ID_TYPE_OPTIONS.find((o) => o.value === t)?.label ?? t ?? '—';

  return (
    <Layout>
      <div className="p-5 lg:p-6 space-y-5">

        {/* Toast */}
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
          <span className="text-slate-700 font-medium">Guests</span>
        </nav>

        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-violet-100 flex items-center justify-center flex-shrink-0">
              <UserIcon className="w-5 h-5 text-violet-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Guests</h1>
              <p className="text-slate-500 text-sm mt-0.5">{guests.length} guest{guests.length !== 1 ? 's' : ''}</p>
            </div>
          </div>
          <button onClick={openNew}
            className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-sm">
            <PlusIcon className="w-4 h-4" /> New Guest
          </button>
        </div>

        {/* Stats cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-4">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Guests</p>
            <p className="text-2xl font-bold text-slate-800 mt-1">{guests.length}</p>
          </div>
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-4">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">VIP</p>
            <p className="text-2xl font-bold text-violet-600 mt-1">{guests.filter(g => (g.vip_level ?? 0) > 0).length}</p>
          </div>
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm px-5 py-4 col-span-2 sm:col-span-1">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Blacklisted</p>
            <p className="text-2xl font-bold text-red-600 mt-1">{guests.filter(g => g.is_blacklisted).length}</p>
          </div>
        </div>

        {/* Search */}
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name, email, phone or ID…"
            className="flex-1 px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
          <button type="submit"
            className="px-4 py-2.5 rounded-xl bg-slate-700 hover:bg-slate-800 text-white text-sm font-semibold transition-colors">
            Search
          </button>
        </form>

        {/* Table */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : guests.length === 0 ? (
          <div className="text-center py-20 text-slate-400">
            <UserIcon className="w-14 h-14 mx-auto mb-3 opacity-30" />
            <p className="font-medium">No guests found</p>
            <p className="text-sm mt-1">Add your first guest to get started</p>
          </div>
        ) : (
          <>
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-100 bg-slate-50/60">
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Guest</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">Phone</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">Nationality</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">ID Number</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:table-cell">Stays</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {paginated.map((guest) => (
                      <tr key={guest.id} className="hover:bg-slate-50/50 transition-colors cursor-pointer"
                        onClick={() => setViewingGuest(guest)}>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2.5">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-400 to-violet-600 flex items-center justify-center text-white font-bold text-xs flex-shrink-0">
                              {guest.first_name[0]}{guest.last_name[0]}
                            </div>
                            <div>
                              <p className="font-semibold text-slate-800 leading-tight">{guest.first_name} {guest.last_name}</p>
                              {guest.email && <p className="text-xs text-slate-400 leading-tight">{guest.email}</p>}
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-slate-600 text-xs hidden sm:table-cell">{guest.phone}</td>
                        <td className="px-4 py-3 text-slate-500 text-xs hidden md:table-cell">{guest.nationality || '—'}</td>
                        <td className="px-4 py-3 hidden md:table-cell">
                          {guest.id_number ? (
                            <span className="inline-flex items-center gap-1 text-xs font-mono bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md">
                              <IdentificationIcon className="w-3 h-3" /> {guest.id_number}
                            </span>
                          ) : <span className="text-slate-400 text-xs">—</span>}
                        </td>
                        <td className="px-4 py-3 text-slate-500 text-xs hidden lg:table-cell">{guest.total_stays ?? 0}</td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-0.5" onClick={(e) => e.stopPropagation()}>
                            <button onClick={() => setViewingGuest(guest)} title="View"
                              className="p-1.5 rounded-lg text-blue-500 hover:text-blue-700 hover:bg-blue-50 transition-colors">
                              <EyeIcon className="w-4 h-4" />
                            </button>
                            <button onClick={() => openEdit(guest)} title="Edit"
                              className="p-1.5 rounded-lg text-emerald-500 hover:text-emerald-700 hover:bg-emerald-50 transition-colors">
                              <PencilSquareIcon className="w-4 h-4" />
                            </button>
                            <button onClick={() => setDeleteConfirm(guest)} title="Delete"
                              className="p-1.5 rounded-lg text-red-500 hover:text-red-700 hover:bg-red-50 transition-colors">
                              <TrashIcon className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            <Pagination total={guests.length} safePage={safePage} perPage={perPage} totalPages={totalPages}
              onPageChange={setPage} onPerPageChange={setPerPage} />
          </>
        )}

      </div>

        {/* ── Create / Edit slide-over ── */}
        {editingId !== null && (
          <div className="fixed inset-0 z-50 flex">
            <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={closePanel} />
            <aside className="w-full max-w-lg bg-white shadow-2xl flex flex-col overflow-hidden h-screen">
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-violet-700 flex items-center justify-center">
                    <UserIcon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="font-semibold text-gray-900">{editingId === 'new' ? 'Add New Guest' : 'Edit Guest'}</h2>
                    <p className="text-xs text-gray-500">{editingId === 'new' ? 'Fill in the details below' : 'Update guest details'}</p>
                  </div>
                </div>
                <button onClick={closePanel} className="p-2 rounded-full hover:bg-gray-200 transition-colors">
                  <XMarkIcon className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              <form onSubmit={handleSave} className="flex-1 overflow-y-auto p-6 space-y-5">

                {/* Personal Info */}
                <section>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Personal Info</p>
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">First Name *</label>
                        <input {...inp('first_name')} required placeholder="John"
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Last Name *</label>
                        <input {...inp('last_name')} required placeholder="Doe"
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
                        <select {...inp('gender')}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
                          {GENDER_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
                        <input {...inp('date_of_birth')} type="date"
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Nationality</label>
                      <input {...inp('nationality')} placeholder="e.g. Tanzanian"
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                    </div>
                  </div>
                </section>

                {/* Contact */}
                <section>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Contact</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Phone *</label>
                      <input {...inp('phone')} required placeholder="+255 712 345 678"
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Email <span className="text-gray-400 font-normal">(optional)</span></label>
                      <input {...inp('email')} type="email" placeholder="john@example.com"
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                    </div>
                  </div>
                </section>

                {/* Identity */}
                <section>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Identity</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">ID Type</label>
                      <select {...inp('id_type')}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
                        {ID_TYPE_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center justify-between">
                        <span>ID Number</span>
                        {editingId === 'new' && (
                          <button type="button" onClick={() => setForm((p) => ({ ...p, id_number: generateGuestId() }))}
                            className="text-blue-500 hover:text-blue-700 text-xs font-medium">↻ Regenerate</button>
                        )}
                      </label>
                      <input {...inp('id_number')} placeholder="Auto-generated"
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-400 bg-gray-50" />
                    </div>
                  </div>
                </section>

                {/* Address */}
                <section>
                  <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Address <span className="text-gray-300 font-normal normal-case">(optional)</span></p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Street Address</label>
                      <input {...inp('address')} placeholder="123 Main Street"
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                        <input {...inp('city')} placeholder="Dar es Salaam"
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">State / Region</label>
                        <input {...inp('state')} placeholder="Tanzania"
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
                        <input {...inp('country')} placeholder="Tanzania"
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Postal Code</label>
                        <input {...inp('postal_code')} placeholder="00100"
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                      </div>
                    </div>
                  </div>
                </section>

              </form>
              <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-end gap-3">
                <button onClick={closePanel} className="px-4 py-2 rounded-lg text-sm font-semibold text-gray-600 hover:bg-gray-100 transition-colors">Cancel</button>
                <button onClick={handleSave} disabled={saving}
                  className="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold transition-colors shadow-sm disabled:opacity-60">
                  {saving ? 'Saving…' : editingId === 'new' ? 'Create Guest' : 'Save Changes'}
                </button>
              </div>
            </aside>
          </div>
        )}

        {/* ── View slide-over ── */}
        {viewingGuest && (
          <div className="fixed inset-0 z-50 flex">
            <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={() => setViewingGuest(null)} />
            <aside className="w-full max-w-lg bg-white shadow-2xl flex flex-col overflow-hidden h-screen">
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-400 to-violet-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                    {viewingGuest.first_name[0]}{viewingGuest.last_name[0]}
                  </div>
                  <div>
                    <h2 className="font-semibold text-gray-900">{viewingGuest.first_name} {viewingGuest.last_name}</h2>
                    <p className="text-xs text-gray-500">{viewingGuest.email || viewingGuest.phone}</p>
                  </div>
                </div>
                <button onClick={() => setViewingGuest(null)} className="p-2 rounded-full hover:bg-gray-200 transition-colors">
                  <XMarkIcon className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto p-6 space-y-5">
                {viewingGuest.is_blacklisted && (
                  <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-2.5 text-sm font-semibold text-red-700">
                    ⚠ This guest is blacklisted
                  </div>
                )}
                {[
                  { label: 'Personal Info', rows: [
                    ['Full Name', `${viewingGuest.first_name} ${viewingGuest.last_name}`],
                    ['Gender', genderLabel(viewingGuest.gender)],
                    ['Date of Birth', viewingGuest.date_of_birth ?? '—'],
                    ['Nationality', viewingGuest.nationality ?? '—'],
                  ]},
                  { label: 'Contact', rows: [
                    ['Phone', viewingGuest.phone],
                    ['Email', viewingGuest.email ?? '—'],
                  ]},
                  { label: 'Identity', rows: [
                    ['ID Type', idTypeLabel(viewingGuest.id_type)],
                    ['ID Number', viewingGuest.id_number ?? '—'],
                  ]},
                  { label: 'Address', rows: [
                    ['Address', viewingGuest.address ?? '—'],
                    ['City', viewingGuest.city ?? '—'],
                    ['State / Region', viewingGuest.state ?? '—'],
                    ['Country', viewingGuest.country ?? '—'],
                    ['Postal Code', viewingGuest.postal_code ?? '—'],
                  ]},
                  { label: 'Stay History', rows: [
                    ['Total Stays', String(viewingGuest.total_stays ?? 0)],
                    ['Total Revenue', viewingGuest.total_revenue != null ? `$${Number(viewingGuest.total_revenue).toFixed(2)}` : '—'],
                    ['VIP Level', String(viewingGuest.vip_level ?? 0)],
                  ]},
                ].map(({ label, rows }) => (
                  <section key={label}>
                    <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">{label}</p>
                    <div className="bg-gray-50 rounded-xl divide-y divide-gray-100">
                      {(rows as [string, string][]).map(([k, v]) => (
                        <div key={k} className="flex items-center justify-between px-4 py-2.5">
                          <span className="text-xs text-gray-500">{k}</span>
                          <span className="text-xs font-semibold text-gray-700">{v || '—'}</span>
                        </div>
                      ))}
                    </div>
                  </section>
                ))}
              </div>
              <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-end gap-2">
                <button onClick={() => { setViewingGuest(null); openEdit(viewingGuest); }}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold text-blue-600 border border-blue-200 hover:bg-blue-50 transition-colors">
                  <PencilSquareIcon className="w-4 h-4" /> Edit
                </button>
                <button onClick={() => { setDeleteConfirm(viewingGuest); setViewingGuest(null); }}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold text-red-600 border border-red-200 hover:bg-red-50 transition-colors">
                  <TrashIcon className="w-4 h-4" /> Delete
                </button>
                <button onClick={() => setViewingGuest(null)}
                  className="px-4 py-2 rounded-lg text-sm font-semibold text-gray-600 hover:bg-gray-100 transition-colors">
                  Close
                </button>
              </div>
            </aside>
          </div>
        )}

        {/* ── Delete confirmation modal ── */}
        {deleteConfirm && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setDeleteConfirm(null)} />
            <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
              <div className="flex items-center justify-center w-12 h-12 rounded-full bg-red-100 mx-auto mb-4">
                <TrashIcon className="w-6 h-6 text-red-600" />
              </div>
              <h3 className="text-center font-bold text-slate-800 text-lg mb-1">Delete Guest</h3>
              <p className="text-center text-sm text-slate-500 mb-6">
                Are you sure you want to delete <span className="font-semibold text-slate-700">&ldquo;{deleteConfirm.first_name} {deleteConfirm.last_name}&rdquo;</span>? This cannot be undone.
              </p>
              <div className="flex gap-3">
                <button onClick={() => setDeleteConfirm(null)}
                  className="flex-1 px-4 py-2.5 rounded-xl text-sm font-semibold text-slate-600 border border-slate-200 hover:bg-slate-50 transition-colors">Cancel</button>
                <button onClick={handleDelete}
                  className="flex-1 px-4 py-2.5 rounded-xl text-sm font-semibold bg-red-600 hover:bg-red-700 text-white transition-colors shadow-sm">Delete</button>
              </div>
            </div>
          </div>
        )}
    </Layout>
  );
}
