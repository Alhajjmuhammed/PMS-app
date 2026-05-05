'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import clsx from 'clsx';
import {
  UserGroupIcon,
  PencilSquareIcon,
  TrashIcon,
  EyeIcon,
  NoSymbolIcon,
  PlusIcon,
  XMarkIcon,
  CheckCircleIcon,
  PhoneIcon,
  BuildingOfficeIcon,
  Squares2X2Icon,
  TableCellsIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  phone: string;
  is_active: boolean;
  assigned_property: number | null;
  property_name: string | null;
  last_login: string | null;
  date_joined: string;
}

interface Property { id: number; name: string; }

const ROLES = ['ADMIN', 'MANAGER', 'FRONT_DESK', 'HOUSEKEEPING', 'MAINTENANCE', 'ACCOUNTANT', 'POS_STAFF'];

const ROLE_COLORS: Record<string, string> = {
  ADMIN:        'bg-purple-100 text-purple-700',
  MANAGER:      'bg-blue-100 text-blue-700',
  FRONT_DESK:   'bg-emerald-100 text-emerald-700',
  HOUSEKEEPING: 'bg-amber-100 text-amber-700',
  MAINTENANCE:  'bg-orange-100 text-orange-700',
  ACCOUNTANT:   'bg-teal-100 text-teal-700',
  POS_STAFF:    'bg-pink-100 text-pink-700',
};

const EMPTY_FORM = {
  email: '', first_name: '', last_name: '',
  role: 'FRONT_DESK', phone: '',
  assigned_property: '' as string | number,
  password: '', is_active: true,
};

const AVATAR_COLORS = [
  'from-blue-500 to-blue-600', 'from-violet-500 to-violet-600', 'from-emerald-500 to-emerald-600',
  'from-amber-500 to-amber-600', 'from-pink-500 to-pink-600', 'from-teal-500 to-teal-600',
];
function avatarColor(id: number) { return AVATAR_COLORS[id % AVATAR_COLORS.length]; }
function getInitials(u: User) {
  return ((u.first_name?.[0] ?? '') + (u.last_name?.[0] ?? '')).toUpperCase() || u.email[0].toUpperCase();
}
function formatDate(str: string | null) {
  if (!str) return '—';
  return new Date(str).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

/* ── Stable module-level components ── */
function RoleBadge({ role }: { role: string }) {
  return (
    <span className={clsx('text-[10px] font-bold px-2 py-0.5 rounded-full', ROLE_COLORS[role] ?? 'bg-slate-100 text-slate-600')}>
      {role.replace('_', ' ')}
    </span>
  );
}
function StatusBadge({ u }: { u: User }) {
  return (
    <span className={clsx('text-xs font-semibold px-2.5 py-0.5 rounded-full', u.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-600')}>
      {u.is_active ? 'Active' : 'Inactive'}
    </span>
  );
}
function ViewBtn({ u, onView }: { u: User; onView: (u: User) => void }) {
  return (
    <button onClick={() => onView(u)} title="View details"
      className="p-1.5 rounded-lg text-blue-500 hover:text-blue-700 hover:bg-blue-50 transition-colors">
      <EyeIcon className="w-4 h-4" />
    </button>
  );
}
function EditBtn({ u, onEdit }: { u: User; onEdit: (u: User) => void }) {
  return (
    <button onClick={() => onEdit(u)} title="Edit user"
      className="p-1.5 rounded-lg text-emerald-500 hover:text-emerald-700 hover:bg-emerald-50 transition-colors">
      <PencilSquareIcon className="w-4 h-4" />
    </button>
  );
}
function BlockBtn({ u, onToggle }: { u: User; onToggle: (u: User) => void }) {
  return (
    <button onClick={() => onToggle(u)} title={u.is_active ? 'Block user' : 'Unblock user'}
      className={clsx('p-1.5 rounded-lg transition-colors',
        u.is_active ? 'text-amber-500 hover:text-amber-700 hover:bg-amber-50' : 'text-amber-400 hover:text-amber-600 hover:bg-amber-50')}>
      <NoSymbolIcon className="w-4 h-4" />
    </button>
  );
}
function DeleteBtn({ u, onDelete }: { u: User; onDelete: (u: User) => void }) {
  return (
    <button onClick={() => onDelete(u)} title="Delete user"
      className="p-1.5 rounded-lg text-red-500 hover:text-red-700 hover:bg-red-50 transition-colors">
      <TrashIcon className="w-4 h-4" />
    </button>
  );
}

interface PaginationProps {
  total: number; safePage: number; perPage: number; totalPages: number;
  onPageChange: (pg: number) => void; onPerPageChange: (n: number) => void;
}
function Pagination({ total, safePage, perPage, totalPages, onPageChange, onPerPageChange }: PaginationProps) {
  if (total === 0) return null;
  const start = (safePage - 1) * perPage + 1;
  const end = Math.min(safePage * perPage, total);
  return (
    <div className="flex items-center justify-between flex-wrap gap-3 pt-2">
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <span>Rows per page:</span>
        <select value={perPage} onChange={(e) => onPerPageChange(Number(e.target.value))}
          className="border border-slate-200 rounded-lg px-2 py-1 text-sm text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-300">
          {[5, 6, 10, 15, 20, 50].map((n) => <option key={n} value={n}>{n}</option>)}
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
export default function UsersPage() {
  const { user: currentUser, loading: authLoading } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editingId, setEditingId] = useState<number | 'new' | null>(null);
  const [form, setForm] = useState<typeof EMPTY_FORM>(EMPTY_FORM);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<User | null>(null);
  const [viewingUser, setViewingUser] = useState<User | null>(null);
  const [viewMode, setViewMode] = useState<'card' | 'table'>('table');
  const [perPage, setPerPage] = useState(10);
  const [page, setPage] = useState(1);
  const [roleFilter, setRoleFilter] = useState('');

  const isSuperAdmin = currentUser?.is_superuser === true;

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3000);
  };

  const load = async () => {
    setLoading(true);
    try {
      const [usersRes, propsRes] = await Promise.all([
        api.get<any>('/api/v1/auth/users/'),
        isSuperAdmin ? api.get<any>('/api/v1/properties/') : Promise.resolve(null),
      ]);
      const list = Array.isArray(usersRes.data) ? usersRes.data : (usersRes.data.results ?? []);
      setUsers(list);
      if (propsRes) {
        const plist = Array.isArray(propsRes.data) ? propsRes.data : (propsRes.data.results ?? []);
        setProperties(plist);
      }
    } catch {
      showToast('Failed to load users', false);
    } finally {
      setLoading(false);
    }
  };

  // Wait for auth to finish before loading — so isSuperAdmin is correctly known
  // when we decide whether to also fetch /api/v1/properties/
  useEffect(() => {
    if (!authLoading && currentUser) load();
  }, [authLoading, currentUser?.id]);
  useEffect(() => { setPage(1); }, [perPage, viewMode, roleFilter]);

  const filtered = roleFilter ? users.filter((u) => u.role === roleFilter) : users;
  const totalPages = Math.max(1, Math.ceil(filtered.length / perPage));
  const safePage = Math.min(page, totalPages);
  const paginated = filtered.slice((safePage - 1) * perPage, safePage * perPage);

  const openNew = () => {
    setForm({ ...EMPTY_FORM, assigned_property: currentUser?.assigned_property?.id ?? '' });
    setEditingId('new');
  };
  const openEdit = (u: User) => {
    setForm({
      email: u.email, first_name: u.first_name, last_name: u.last_name,
      role: u.role, phone: u.phone ?? '',
      assigned_property: u.assigned_property ?? '',
      password: '', is_active: u.is_active,
    });
    setEditingId(u.id);
  };
  const closePanel = () => setEditingId(null);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload: any = { ...form };
      if (!payload.password) delete payload.password;
      if (payload.assigned_property === '') payload.assigned_property = null;

      if (editingId === 'new') {
        await api.post('/api/v1/auth/users/', payload);
        showToast('User created successfully');
      } else {
        await api.patch(`/api/v1/auth/users/${editingId}/`, payload);
        showToast('User updated successfully');
      }
      await load();
      closePanel();
    } catch (err: any) {
      const detail = err?.response?.data;
      const msg = typeof detail === 'object' ? Object.values(detail).flat().join(' ') : 'Failed to save user';
      showToast(msg as string, false);
    } finally {
      setSaving(false);
    }
  };

  const handleToggleActive = async (u: User) => {
    try {
      await api.patch(`/api/v1/auth/users/${u.id}/`, { is_active: !u.is_active });
      showToast(`${u.email} ${!u.is_active ? 'activated' : 'blocked'}`);
      await load();
    } catch {
      showToast('Failed to update user', false);
    }
  };

  const handleDelete = async () => {
    if (!deleteConfirm) return;
    try {
      await api.delete(`/api/v1/auth/users/${deleteConfirm.id}/`);
      showToast(`${deleteConfirm.email} deleted`);
      setDeleteConfirm(null);
      await load();
    } catch {
      showToast('Failed to delete user', false);
    }
  };

  const f = (key: keyof typeof EMPTY_FORM) => ({
    value: String(form[key] ?? ''),
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value })),
  });

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

        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">System Users</h1>
            <p className="text-slate-500 text-sm mt-0.5">
              {filtered.length} user{filtered.length !== 1 ? 's' : ''}{roleFilter ? ` · ${roleFilter.replace('_', ' ')}` : ''}
            </p>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}
              className="border border-slate-200 rounded-xl px-3 py-2 text-sm text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-300">
              <option value="">All Roles</option>
              {ROLES.map((r) => <option key={r} value={r}>{r.replace('_', ' ')}</option>)}
            </select>
            <div className="flex items-center bg-slate-100 rounded-xl p-1 gap-0.5">
              <button onClick={() => setViewMode('card')} title="Card view"
                className={clsx('p-2 rounded-lg transition-colors',
                  viewMode === 'card' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-400 hover:text-slate-600')}>
                <Squares2X2Icon className="w-4 h-4" />
              </button>
              <button onClick={() => setViewMode('table')} title="Table view"
                className={clsx('p-2 rounded-lg transition-colors',
                  viewMode === 'table' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-400 hover:text-slate-600')}>
                <TableCellsIcon className="w-4 h-4" />
              </button>
            </div>
            <button onClick={openNew}
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-sm">
              <PlusIcon className="w-4 h-4" />
              Add User
            </button>
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20 text-slate-400">
            <UserGroupIcon className="w-14 h-14 mx-auto mb-3 opacity-30" />
            <p className="font-medium">No users found</p>
          </div>
        ) : viewMode === 'card' ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {paginated.map((u) => (
                <div key={u.id} className="bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow overflow-hidden">
                  <div className="flex items-start gap-3 p-4 pb-3">
                    <div className={clsx('w-11 h-11 rounded-xl bg-gradient-to-br flex items-center justify-center flex-shrink-0 shadow-sm text-white font-bold text-sm', avatarColor(u.id))}>
                      {getInitials(u)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <p className="font-bold text-slate-800 text-sm leading-tight truncate">{u.first_name} {u.last_name}</p>
                        <RoleBadge role={u.role} />
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5 truncate">{u.email}</p>
                    </div>
                  </div>
                  <div className="px-4 pb-3 space-y-1.5">
                    {u.phone && (
                      <div className="flex items-center gap-2 text-xs text-slate-500">
                        <PhoneIcon className="w-3.5 h-3.5 flex-shrink-0" />
                        <span>{u.phone}</span>
                      </div>
                    )}
                    {u.property_name && (
                      <div className="flex items-center gap-2 text-xs text-slate-500">
                        <BuildingOfficeIcon className="w-3.5 h-3.5 flex-shrink-0" />
                        <span className="truncate">{u.property_name}</span>
                      </div>
                    )}
                    <div className="text-xs text-slate-400">Joined {formatDate(u.date_joined)}</div>
                  </div>
                  <div className="flex items-center justify-between px-4 py-3 border-t border-slate-50 bg-slate-50/50">
                    <StatusBadge u={u} />
                    <div className="flex items-center gap-0.5">
                      <ViewBtn u={u} onView={setViewingUser} />
                      <EditBtn u={u} onEdit={openEdit} />
                      <BlockBtn u={u} onToggle={handleToggleActive} />
                      <DeleteBtn u={u} onDelete={setDeleteConfirm} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <Pagination total={filtered.length} safePage={safePage} perPage={perPage} totalPages={totalPages} onPageChange={setPage} onPerPageChange={setPerPage} />
          </>
        ) : (
          <>
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-100 bg-slate-50/60">
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">User</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">Email</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Role</th>
                      {isSuperAdmin && <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">Property</th>}
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:table-cell">Joined</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {paginated.map((u) => (
                      <tr key={u.id} className="hover:bg-slate-50/50 transition-colors">
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2.5">
                            <div className={clsx('w-8 h-8 rounded-lg bg-gradient-to-br flex items-center justify-center flex-shrink-0 text-white font-bold text-xs', avatarColor(u.id))}>
                              {getInitials(u)}
                            </div>
                            <span className="font-semibold text-slate-800 whitespace-nowrap">{u.first_name} {u.last_name}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-slate-500 text-xs hidden sm:table-cell">{u.email}</td>
                        <td className="px-4 py-3"><RoleBadge role={u.role} /></td>
                        {isSuperAdmin && <td className="px-4 py-3 text-xs text-slate-500 hidden md:table-cell">{u.property_name ?? '—'}</td>}
                        <td className="px-4 py-3 text-xs text-slate-400 hidden lg:table-cell">{formatDate(u.date_joined)}</td>
                        <td className="px-4 py-3"><StatusBadge u={u} /></td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-0.5">
                            <ViewBtn u={u} onView={setViewingUser} />
                            <EditBtn u={u} onEdit={openEdit} />
                            <BlockBtn u={u} onToggle={handleToggleActive} />
                            <DeleteBtn u={u} onDelete={setDeleteConfirm} />
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            <Pagination total={filtered.length} safePage={safePage} perPage={perPage} totalPages={totalPages} onPageChange={setPage} onPerPageChange={setPerPage} />
          </>
        )}

        {/* Create / Edit slide-over */}
        {editingId !== null && (
          <div className="fixed inset-0 z-50 flex">
            <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={closePanel} />
            <aside className="w-full max-w-lg bg-white shadow-2xl flex flex-col overflow-hidden">
              <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
                <h2 className="font-bold text-slate-800 text-lg">{editingId === 'new' ? 'Add New User' : 'Edit User'}</h2>
                <button onClick={closePanel} className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 transition-colors">
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
              <form onSubmit={handleSave} className="flex-1 overflow-y-auto p-6 space-y-5">
                <section>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Personal Information</p>
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 mb-1">First Name</label>
                        <input {...f('first_name')} placeholder="John" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300" />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 mb-1">Last Name</label>
                        <input {...f('last_name')} placeholder="Doe" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Email *</label>
                      <input {...f('email')} required type="email" placeholder="john@hotel.com" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Phone</label>
                      <input {...f('phone')} type="tel" placeholder="+1-555-000-0000" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300" />
                    </div>
                  </div>
                </section>
                <section>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Role & Access</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Role *</label>
                      <select {...f('role')} className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white">
                        {ROLES.map((r) => <option key={r} value={r}>{r.replace('_', ' ')}</option>)}
                      </select>
                    </div>
                    {isSuperAdmin && (
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 mb-1">Assign to Property</label>
                        <select value={String(form.assigned_property)}
                          onChange={(e) => setForm((prev) => ({ ...prev, assigned_property: e.target.value ? Number(e.target.value) : '' }))}
                          className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white">
                          <option value="">— No property —</option>
                          {properties.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
                        </select>
                      </div>
                    )}
                    <div className="flex items-center gap-2 pt-1">
                      <input id="ua_active" type="checkbox" checked={!!form.is_active}
                        onChange={(e) => setForm((prev) => ({ ...prev, is_active: e.target.checked }))}
                        className="w-4 h-4 rounded border-slate-300 text-blue-500 focus:ring-blue-400" />
                      <label htmlFor="ua_active" className="text-sm text-slate-700 font-medium select-none cursor-pointer">Account is active</label>
                    </div>
                  </div>
                </section>
                <section>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Password</p>
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">
                      {editingId === 'new' ? 'Password *' : 'New Password (leave blank to keep current)'}
                    </label>
                    <input {...f('password')} type="password" required={editingId === 'new'} placeholder="••••••••"
                      className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300" />
                  </div>
                </section>
              </form>
              <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-end gap-3">
                <button onClick={closePanel} className="px-4 py-2.5 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-100 transition-colors">Cancel</button>
                <button onClick={handleSave} disabled={saving}
                  className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold transition-colors shadow-sm disabled:opacity-60">
                  {saving ? 'Saving…' : editingId === 'new' ? 'Create User' : 'Save Changes'}
                </button>
              </div>
            </aside>
          </div>
        )}

        {/* View slide-over */}
        {viewingUser && (
          <div className="fixed inset-0 z-50 flex">
            <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={() => setViewingUser(null)} />
            <aside className="w-full max-w-lg bg-white shadow-2xl flex flex-col overflow-hidden">
              <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
                <div className="flex items-center gap-3">
                  <div className={clsx('w-10 h-10 rounded-xl bg-gradient-to-br flex items-center justify-center text-white font-bold text-sm flex-shrink-0', avatarColor(viewingUser.id))}>
                    {getInitials(viewingUser)}
                  </div>
                  <div>
                    <h2 className="font-bold text-slate-800 text-base leading-tight">{viewingUser.first_name} {viewingUser.last_name}</h2>
                    <p className="text-xs text-slate-400">{viewingUser.email}</p>
                  </div>
                </div>
                <button onClick={() => setViewingUser(null)} className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 transition-colors">
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto p-6 space-y-5">
                <div className="flex items-center gap-2 flex-wrap">
                  <RoleBadge role={viewingUser.role} />
                  <StatusBadge u={viewingUser} />
                </div>
                {[
                  { label: 'Account', rows: [
                    ['Email', viewingUser.email],
                    ['Phone', viewingUser.phone],
                    ['Property', viewingUser.property_name ?? '—'],
                  ]},
                  { label: 'Activity', rows: [
                    ['Joined', formatDate(viewingUser.date_joined)],
                    ['Last Login', formatDate(viewingUser.last_login)],
                  ]},
                ].map(({ label, rows }) => (
                  <section key={label}>
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">{label}</p>
                    <div className="bg-slate-50 rounded-xl divide-y divide-slate-100">
                      {(rows as [string, string][]).map(([k, v]) => (
                        <div key={k} className="flex items-center justify-between px-4 py-2.5">
                          <span className="text-xs text-slate-500">{k}</span>
                          <span className="text-xs font-semibold text-slate-700">{v || '—'}</span>
                        </div>
                      ))}
                    </div>
                  </section>
                ))}
              </div>
              <div className="px-6 py-4 border-t border-slate-100 flex justify-end gap-2">
                <button onClick={() => { setViewingUser(null); openEdit(viewingUser); }}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold text-blue-600 border border-blue-200 hover:bg-blue-50 transition-colors">
                  <PencilSquareIcon className="w-4 h-4" /> Edit
                </button>
                <button onClick={() => setViewingUser(null)} className="px-4 py-2 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-100 transition-colors">
                  Close
                </button>
              </div>
            </aside>
          </div>
        )}

        {/* Delete confirmation */}
        {deleteConfirm && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setDeleteConfirm(null)} />
            <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
              <div className="flex items-center justify-center w-12 h-12 rounded-full bg-red-100 mx-auto mb-4">
                <TrashIcon className="w-6 h-6 text-red-600" />
              </div>
              <h3 className="text-center font-bold text-slate-800 text-lg mb-1">Delete User</h3>
              <p className="text-center text-sm text-slate-500 mb-6">
                Are you sure you want to delete <span className="font-semibold text-slate-700">{deleteConfirm.email}</span>? This cannot be undone.
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
      </div>
    </Layout>
  );
}
