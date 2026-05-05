'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import clsx from 'clsx';
import {
  BuildingOfficeIcon,
  PencilSquareIcon,
  TrashIcon,
  EyeIcon,
  NoSymbolIcon,
  PlusIcon,
  XMarkIcon,
  CheckCircleIcon,
  MapPinIcon,
  PhoneIcon,
  GlobeAltIcon,
  StarIcon,
  Squares2X2Icon,
  TableCellsIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';

interface Property {
  id: number;
  name: string;
  code: string;
  property_type: string;
  address: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  phone: string;
  email: string;
  website: string;
  star_rating: number;
  total_rooms: number;
  check_in_time: string;
  check_out_time: string;
  currency: string;
  is_active: boolean;
}

const EMPTY_FORM: Omit<Property, 'id' | 'total_rooms'> = {
  name: '', code: '', property_type: 'HOTEL',
  address: '', city: '', state: '', country: '', postal_code: '',
  phone: '', email: '', website: '',
  star_rating: 3, check_in_time: '14:00', check_out_time: '12:00',
  currency: 'USD', is_active: true,
};

const TYPE_COLORS: Record<string, string> = {
  HOTEL:      'bg-blue-100 text-blue-700',
  RESORT:     'bg-emerald-100 text-emerald-700',
  MOTEL:      'bg-amber-100 text-amber-700',
  HOSTEL:     'bg-violet-100 text-violet-700',
  APARTMENT:  'bg-pink-100 text-pink-700',
  VILLA:      'bg-teal-100 text-teal-700',
  GUESTHOUSE: 'bg-orange-100 text-orange-700',
};

/* ── Module-level helper components (stable references) ── */
function Stars({ rating }: { rating: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {Array.from({ length: 5 }).map((_, i) => (
        <StarIcon key={i} className={clsx('w-3 h-3', i < rating ? 'text-amber-400 fill-amber-400' : 'text-slate-200')} />
      ))}
    </div>
  );
}

function StatusBadge({ p }: { p: Property }) {
  return (
    <span
      className={clsx(
        'text-xs font-semibold px-2.5 py-1 rounded-full',
        p.is_active
          ? 'bg-emerald-100 text-emerald-700'
          : 'bg-red-100 text-red-600',
      )}
    >
      {p.is_active ? 'Active' : 'Inactive'}
    </span>
  );
}

function ViewBtn({ p, onView }: { p: Property; onView: (p: Property) => void }) {
  return (
    <button
      onClick={() => onView(p)}
      title="View details"
      className="p-1.5 rounded-lg text-blue-500 hover:text-blue-700 hover:bg-blue-50 transition-colors"
    >
      <EyeIcon className="w-4 h-4" />
    </button>
  );
}

function EditBtn({ p, onEdit }: { p: Property; onEdit: (p: Property) => void }) {
  return (
    <button
      onClick={() => onEdit(p)}
      title="Edit property"
      className="p-1.5 rounded-lg text-emerald-500 hover:text-emerald-700 hover:bg-emerald-50 transition-colors"
    >
      <PencilSquareIcon className="w-4 h-4" />
    </button>
  );
}

function BlockBtn({ p, onToggle }: { p: Property; onToggle: (p: Property) => void }) {
  return (
    <button
      onClick={() => onToggle(p)}
      title={p.is_active ? 'Block property' : 'Unblock property'}
      className={clsx(
        'p-1.5 rounded-lg transition-colors',
        p.is_active
          ? 'text-amber-500 hover:text-amber-700 hover:bg-amber-50'
          : 'text-amber-400 hover:text-amber-600 hover:bg-amber-50',
      )}
    >
      <NoSymbolIcon className="w-4 h-4" />
    </button>
  );
}

function DeleteBtn({ p, onDelete }: { p: Property; onDelete: (p: Property) => void }) {
  return (
    <button
      onClick={() => onDelete(p)}
      title="Delete property"
      className="p-1.5 rounded-lg text-red-500 hover:text-red-700 hover:bg-red-50 transition-colors"
    >
      <TrashIcon className="w-4 h-4" />
    </button>
  );
}

interface PaginationProps {
  total: number;
  safePage: number;
  perPage: number;
  totalPages: number;
  onPageChange: (pg: number) => void;
  onPerPageChange: (n: number) => void;
}
function Pagination({ total, safePage, perPage, totalPages, onPageChange, onPerPageChange }: PaginationProps) {
  if (total === 0) return null;
  const start = (safePage - 1) * perPage + 1;
  const end = Math.min(safePage * perPage, total);
  return (
    <div className="flex items-center justify-between flex-wrap gap-3 pt-2">
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <span>Rows per page:</span>
        <select
          value={perPage}
          onChange={(e) => onPerPageChange(Number(e.target.value))}
          className="border border-slate-200 rounded-lg px-2 py-1 text-sm text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-300"
        >
          {[5, 6, 10, 15, 20, 50].map((n) => (
            <option key={n} value={n}>{n}</option>
          ))}
        </select>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-sm text-slate-500">{start}–{end} of {total}</span>
        <div className="flex items-center gap-1">
          <button
            onClick={() => onPageChange(Math.max(1, safePage - 1))}
            disabled={safePage === 1}
            className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeftIcon className="w-4 h-4" />
          </button>
          {Array.from({ length: totalPages }).map((_, i) => {
            const pg = i + 1;
            const near = pg === 1 || pg === totalPages || Math.abs(pg - safePage) <= 1;
            const gap = !near && (pg === 2 || pg === totalPages - 1);
            if (!near && !gap) return null;
            if (gap) return <span key={pg} className="px-1 text-slate-400 text-sm">…</span>;
            return (
              <button
                key={pg}
                onClick={() => onPageChange(pg)}
                className={clsx(
                  'w-8 h-8 rounded-lg text-sm font-semibold transition-colors',
                  pg === safePage
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'border border-slate-200 text-slate-600 hover:bg-slate-100',
                )}
              >
                {pg}
              </button>
            );
          })}
          <button
            onClick={() => onPageChange(Math.min(totalPages, safePage + 1))}
            disabled={safePage === totalPages}
            className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronRightIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

/* ── Superadmin: full property manager ── */
function PropertiesManager() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editingId, setEditingId] = useState<number | 'new' | null>(null);
  const [form, setForm] = useState<typeof EMPTY_FORM & { id?: number }>(EMPTY_FORM);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<Property | null>(null);
  const [viewingProp, setViewingProp] = useState<Property | null>(null);

  // View / pagination state
  const [viewMode, setViewMode] = useState<'card' | 'table'>('card');
  const [perPage, setPerPage] = useState(6);
  const [page, setPage] = useState(1);

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3000);
  };

  const load = async () => {
    setLoading(true);
    try {
      const r = await api.get<any>('/api/v1/properties/');
      const list = Array.isArray(r.data) ? r.data : (r.data.results ?? []);
      setProperties(list);
    } catch {
      showToast('Failed to load properties', false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);
  // Reset to page 1 when perPage or viewMode changes
  useEffect(() => { setPage(1); }, [perPage, viewMode]);

  const totalPages = Math.max(1, Math.ceil(properties.length / perPage));
  const safePage = Math.min(page, totalPages);
  const paginated = properties.slice((safePage - 1) * perPage, safePage * perPage);

  const openEdit = (p: Property) => { setForm({ ...p }); setEditingId(p.id); };
  const openNew  = () => { setForm({ ...EMPTY_FORM }); setEditingId('new'); };
  const closePanel = () => setEditingId(null);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editingId === 'new') {
        await api.post('/api/v1/properties/', form);
        showToast('Property created successfully');
      } else {
        await api.patch(`/api/v1/properties/${editingId}/`, form);
        showToast('Property updated successfully');
      }
      await load();
      closePanel();
    } catch {
      showToast('Failed to save property', false);
    } finally {
      setSaving(false);
    }
  };

  const handleToggleActive = async (p: Property) => {
    try {
      await api.patch(`/api/v1/properties/${p.id}/`, { is_active: !p.is_active });
      showToast(`${p.name} ${!p.is_active ? 'activated' : 'deactivated'}`);
      await load();
    } catch {
      showToast('Failed to update status', false);
    }
  };

  const handleDelete = async () => {
    if (!deleteConfirm) return;
    try {
      await api.delete(`/api/v1/properties/${deleteConfirm.id}/`);
      showToast(`${deleteConfirm.name} deleted`);
      setDeleteConfirm(null);
      await load();
    } catch {
      showToast('Failed to delete property', false);
    }
  };

  const f = (key: keyof typeof form) => ({
    value: String(form[key] ?? ''),
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value })),
  });

  return (
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
          <h1 className="text-2xl font-bold text-slate-900">All Properties</h1>
          <p className="text-slate-500 text-sm mt-0.5">{properties.length} propert{properties.length === 1 ? 'y' : 'ies'} registered</p>
        </div>
        <div className="flex items-center gap-2">
          {/* View toggle */}
          <div className="flex items-center bg-slate-100 rounded-xl p-1 gap-0.5">
            <button
              onClick={() => setViewMode('card')}
              title="Card view"
              className={clsx(
                'p-2 rounded-lg transition-colors',
                viewMode === 'card' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-400 hover:text-slate-600',
              )}
            >
              <Squares2X2Icon className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('table')}
              title="Table view"
              className={clsx(
                'p-2 rounded-lg transition-colors',
                viewMode === 'table' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-400 hover:text-slate-600',
              )}
            >
              <TableCellsIcon className="w-4 h-4" />
            </button>
          </div>
          <button
            onClick={openNew}
            className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-sm"
          >
            <PlusIcon className="w-4 h-4" />
            Add Property
          </button>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : properties.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          <BuildingOfficeIcon className="w-14 h-14 mx-auto mb-3 opacity-30" />
          <p className="font-medium">No properties yet</p>
          <p className="text-sm mt-1">Click "Add Property" to create the first one.</p>
        </div>
      ) : viewMode === 'card' ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {paginated.map((p) => (
              <div key={p.id} className="bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow overflow-hidden">
                <div className="flex items-start gap-3 p-4 pb-3">
                  <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center flex-shrink-0 shadow-sm">
                    <BuildingOfficeIcon className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <p className="font-bold text-slate-800 text-sm leading-tight">{p.name}</p>
                      <span className={clsx('flex-shrink-0 text-[10px] font-bold px-2 py-0.5 rounded-full', TYPE_COLORS[p.property_type] ?? 'bg-slate-100 text-slate-600')}>
                        {p.property_type}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5 font-mono">{p.code}</p>
                  </div>
                </div>
                <div className="px-4 pb-3 space-y-1.5">
                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <MapPinIcon className="w-3.5 h-3.5 flex-shrink-0" />
                    <span className="truncate">{p.city}{p.country ? `, ${p.country}` : ''}</span>
                  </div>
                  {p.phone && (
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <PhoneIcon className="w-3.5 h-3.5 flex-shrink-0" />
                      <span>{p.phone}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-3 pt-1">
                    <span className="text-xs text-slate-500">{p.total_rooms} rooms</span>
                    <span className="text-xs text-slate-400">·</span>
                    <Stars rating={p.star_rating} />
                  </div>
                </div>
                <div className="flex items-center justify-between px-4 py-3 border-t border-slate-50 bg-slate-50/50">
                  <StatusBadge p={p} />
                  <div className="flex items-center gap-0.5">
                    <ViewBtn p={p} onView={setViewingProp} />
                    <EditBtn p={p} onEdit={openEdit} />
                    <BlockBtn p={p} onToggle={handleToggleActive} />
                    <DeleteBtn p={p} onDelete={setDeleteConfirm} />
                  </div>
                </div>
              </div>
            ))}
          </div>
          <Pagination total={properties.length} safePage={safePage} perPage={perPage} totalPages={totalPages} onPageChange={setPage} onPerPageChange={setPerPage} />
        </>
      ) : (
        <>
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100 bg-slate-50/60">
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Property</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Code</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">Type</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">Location</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:table-cell">Rooms</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:table-cell">Rating</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                    <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {paginated.map((p) => (
                    <tr key={p.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2.5">
                          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center flex-shrink-0">
                            <BuildingOfficeIcon className="w-4 h-4 text-white" />
                          </div>
                          <span className="font-semibold text-slate-800 whitespace-nowrap">{p.name}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 font-mono text-xs text-slate-500">{p.code}</td>
                      <td className="px-4 py-3 hidden sm:table-cell">
                        <span className={clsx('text-[10px] font-bold px-2 py-0.5 rounded-full', TYPE_COLORS[p.property_type] ?? 'bg-slate-100 text-slate-600')}>
                          {p.property_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-500 whitespace-nowrap hidden md:table-cell">
                        {p.city}{p.country ? `, ${p.country}` : ''}
                      </td>
                      <td className="px-4 py-3 text-slate-600 hidden lg:table-cell">{p.total_rooms}</td>
                      <td className="px-4 py-3 hidden lg:table-cell">
                        <Stars rating={p.star_rating} />
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge p={p} />
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-0.5">
                          <ViewBtn p={p} onView={setViewingProp} />
                          <EditBtn p={p} onEdit={openEdit} />
                          <BlockBtn p={p} onToggle={handleToggleActive} />
                          <DeleteBtn p={p} onDelete={setDeleteConfirm} />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <Pagination total={properties.length} safePage={safePage} perPage={perPage} totalPages={totalPages} onPageChange={setPage} onPerPageChange={setPerPage} />
        </>
      )}

      {/* Edit / New slide-over panel */}
      {editingId !== null && (
        <div className="fixed inset-0 z-50 flex">
          <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={closePanel} />
          <aside className="w-full max-w-lg bg-white shadow-2xl flex flex-col overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <h2 className="font-bold text-slate-800 text-lg">
                {editingId === 'new' ? 'Add New Property' : 'Edit Property'}
              </h2>
              <button onClick={closePanel} className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 transition-colors">
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSave} className="flex-1 overflow-y-auto p-6 space-y-5">
              <section>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Basic Information</p>
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Property Name *</label>
                    <input {...f('name')} required placeholder="Grand Plaza Hotel" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Code *</label>
                      <input {...f('code')} required placeholder="GPH" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400 uppercase" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Type</label>
                      <select {...f('property_type')} className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white">
                        {['HOTEL','RESORT','MOTEL','HOSTEL','APARTMENT','VILLA','GUESTHOUSE'].map((t) => (
                          <option key={t} value={t}>{t.charAt(0) + t.slice(1).toLowerCase()}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Address</label>
                    <input {...f('address')} placeholder="100 Grand Avenue" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">City</label>
                      <input {...f('city')} placeholder="New York" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">State</label>
                      <input {...f('state')} placeholder="NY" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Country</label>
                      <input {...f('country')} placeholder="US" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Postal Code</label>
                      <input {...f('postal_code')} placeholder="10001" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Contact</p>
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Phone</label>
                    <input {...f('phone')} type="tel" placeholder="+1-555-000-0000" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Email</label>
                    <input {...f('email')} type="email" placeholder="info@hotel.com" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Website</label>
                    <input {...f('website')} type="url" placeholder="https://hotel.com" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
                  </div>
                </div>
              </section>

              <section>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Operational Settings</p>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Check-in Time</label>
                      <input {...f('check_in_time')} type="time" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Check-out Time</label>
                      <input {...f('check_out_time')} type="time" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Currency</label>
                      <select {...f('currency')} className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white">
                        {['USD','EUR','GBP','JPY','AUD','CAD','SGD','AED','SAR','MYR'].map((c) => (
                          <option key={c} value={c}>{c}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Star Rating</label>
                      <select {...f('star_rating')} className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white">
                        {[1,2,3,4,5].map((s) => <option key={s} value={s}>{s} Star{s > 1 ? 's' : ''}</option>)}
                      </select>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 pt-1">
                    <input
                      id="is_active"
                      type="checkbox"
                      checked={!!form.is_active}
                      onChange={(e) => setForm((prev) => ({ ...prev, is_active: e.target.checked }))}
                      className="w-4 h-4 rounded border-slate-300 text-blue-500 focus:ring-blue-400"
                    />
                    <label htmlFor="is_active" className="text-sm text-slate-700 font-medium select-none cursor-pointer">Property is active</label>
                  </div>
                </div>
              </section>
            </form>

            <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-end gap-3">
              <button onClick={closePanel} className="px-4 py-2.5 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-100 transition-colors">
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold transition-colors shadow-sm disabled:opacity-60"
              >
                {saving ? 'Saving…' : editingId === 'new' ? 'Create Property' : 'Save Changes'}
              </button>
            </div>
          </aside>
        </div>
      )}

      {/* View slide-over panel */}
      {viewingProp && (
        <div className="fixed inset-0 z-50 flex">
          <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={() => setViewingProp(null)} />
          <aside className="w-full max-w-lg bg-white shadow-2xl flex flex-col overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                  <BuildingOfficeIcon className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="font-bold text-slate-800 text-base leading-tight">{viewingProp.name}</h2>
                  <p className="text-xs text-slate-400 font-mono">{viewingProp.code}</p>
                </div>
              </div>
              <button onClick={() => setViewingProp(null)} className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 transition-colors">
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-6 space-y-5">
              <div className="flex items-center gap-2 flex-wrap">
                <span className={clsx('text-xs font-bold px-2.5 py-1 rounded-full', TYPE_COLORS[viewingProp.property_type] ?? 'bg-slate-100 text-slate-600')}>
                  {viewingProp.property_type}
                </span>
                <span className={clsx('text-xs font-semibold px-2.5 py-1 rounded-full', viewingProp.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-600')}>
                  {viewingProp.is_active ? 'Active' : 'Inactive'}
                </span>
                <Stars rating={viewingProp.star_rating} />
              </div>

              {[
                { label: 'Basic', rows: [
                  ['Name', viewingProp.name],
                  ['Code', viewingProp.code],
                  ['Total Rooms', String(viewingProp.total_rooms)],
                  ['Currency', viewingProp.currency],
                ]},
                { label: 'Location', rows: [
                  ['Address', viewingProp.address],
                  ['City', viewingProp.city],
                  ['State', viewingProp.state],
                  ['Country', viewingProp.country],
                  ['Postal Code', viewingProp.postal_code],
                ]},
                { label: 'Contact', rows: [
                  ['Phone', viewingProp.phone],
                  ['Email', viewingProp.email],
                  ['Website', viewingProp.website],
                ]},
                { label: 'Operations', rows: [
                  ['Check-in', viewingProp.check_in_time],
                  ['Check-out', viewingProp.check_out_time],
                ]},
              ].map(({ label, rows }) => (
                <section key={label}>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">{label}</p>
                  <div className="bg-slate-50 rounded-xl divide-y divide-slate-100">
                    {(rows as [string, string][]).filter(([, v]) => v).map(([k, v]) => (
                      <div key={k} className="flex items-center justify-between px-4 py-2.5">
                        <span className="text-xs text-slate-500">{k}</span>
                        <span className="text-xs font-semibold text-slate-700">{v}</span>
                      </div>
                    ))}
                  </div>
                </section>
              ))}
            </div>
            <div className="px-6 py-4 border-t border-slate-100 flex justify-end gap-2">
              <button
                onClick={() => { setViewingProp(null); openEdit(viewingProp); }}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold text-blue-600 border border-blue-200 hover:bg-blue-50 transition-colors"
              >
                <PencilSquareIcon className="w-4 h-4" /> Edit
              </button>
              <button onClick={() => setViewingProp(null)} className="px-4 py-2 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-100 transition-colors">
                Close
              </button>
            </div>
          </aside>
        </div>
      )}

      {/* Delete confirmation modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setDeleteConfirm(null)} />
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-red-100 mx-auto mb-4">
              <TrashIcon className="w-6 h-6 text-red-600" />
            </div>
            <h3 className="text-center font-bold text-slate-800 text-lg mb-1">Delete Property</h3>
            <p className="text-center text-sm text-slate-500 mb-6">
              Are you sure you want to delete <span className="font-semibold text-slate-700">{deleteConfirm.name}</span>? This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="flex-1 px-4 py-2.5 rounded-xl text-sm font-semibold text-slate-600 border border-slate-200 hover:bg-slate-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                className="flex-1 px-4 py-2.5 rounded-xl text-sm font-semibold bg-red-600 hover:bg-red-700 text-white transition-colors shadow-sm"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Regular admin: single-property settings ── */
function SinglePropertySettings() {
  const { user } = useAuth();
  const [saving, setSaving] = useState(false);
  const [property, setProperty] = useState<any>(null);
  const [form, setForm] = useState<any>({});
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3000);
  };

  useEffect(() => {
    api.get(`/api/v1/properties/${user?.assigned_property?.id}/`)
      .then((r) => { setProperty(r.data); setForm(r.data); })
      .catch(() => showToast('Failed to load property', false));
  }, [user]);

  const f = (key: string) => ({
    value: form[key] ?? '',
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm((prev: any) => ({ ...prev, [key]: e.target.value })),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.patch(`/api/v1/properties/${property.id}/`, form);
      showToast('Settings saved successfully');
    } catch {
      showToast('Failed to save settings', false);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-5 lg:p-6 max-w-3xl space-y-6">
      {toast && (
        <div className={clsx(
          'fixed top-5 right-5 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium',
          toast.ok ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white',
        )}>
          <CheckCircleIcon className="w-5 h-5 flex-shrink-0" />
          {toast.msg}
        </div>
      )}

      <div>
        <h1 className="text-2xl font-bold text-slate-900">Property Settings</h1>
        <p className="text-slate-500 text-sm mt-0.5">{user?.assigned_property?.name}</p>
      </div>

      {!property ? (
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Basic */}
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 space-y-4">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Basic Information</p>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Property Name *</label>
              <input {...f('name')} required className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Address</label>
              <input {...f('address')} className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">City</label>
                <input {...f('city')} className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">State</label>
                <input {...f('state')} className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Country</label>
                <input {...f('country')} className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Postal Code</label>
                <input {...f('postal_code')} className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
              </div>
            </div>
          </div>

          {/* Contact */}
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 space-y-4">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Contact Information</p>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Phone</label>
              <input {...f('phone')} type="tel" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Email</label>
              <input {...f('email')} type="email" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Website</label>
              <input {...f('website')} type="url" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
            </div>
          </div>

          {/* Operational */}
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 space-y-4">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Operational Settings</p>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Check-in Time</label>
                <input {...f('check_in_time')} type="time" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">Check-out Time</label>
                <input {...f('check_out_time')} type="time" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-400" />
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Currency</label>
              <select {...f('currency')} className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white">
                {['USD','EUR','GBP','JPY','AUD','CAD','SGD','AED','SAR','MYR'].map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold transition-colors shadow-sm disabled:opacity-60"
            >
              {saving ? 'Saving…' : 'Save Settings'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

/* ── Page entry point ── */
export default function PropertyPage() {
  const { user } = useAuth();
  const isSuperAdmin = user?.is_superuser === true;

  return (
    <Layout>
      {isSuperAdmin ? <PropertiesManager /> : <SinglePropertySettings />}
    </Layout>
  );
}
