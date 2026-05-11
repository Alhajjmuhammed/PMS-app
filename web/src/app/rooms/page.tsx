'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { roomService, roomTypeService, floorService, Room } from '@/lib/services';
import clsx from 'clsx';
import {
  PlusIcon, XMarkIcon, EyeIcon, PencilSquareIcon, TrashIcon,
  CheckCircleIcon, HomeModernIcon, ChevronLeftIcon, ChevronRightIcon,
} from '@heroicons/react/24/outline';

/* ── Constants ── */
const STATUS_OPTIONS = [
  { value: 'VC', label: 'Vacant Clean' },
  { value: 'VD', label: 'Vacant Dirty' },
  { value: 'OC', label: 'Occupied Clean' },
  { value: 'OD', label: 'Occupied Dirty' },
  { value: 'OOO', label: 'Out of Order' },
  { value: 'OOS', label: 'Out of Service' },
];

const STATUS_COLORS: Record<string, string> = {
  VC:  'bg-emerald-100 text-emerald-700',
  VD:  'bg-amber-100 text-amber-700',
  OC:  'bg-blue-100 text-blue-700',
  OD:  'bg-orange-100 text-orange-700',
  OOO: 'bg-red-100 text-red-700',
  OOS: 'bg-slate-100 text-slate-600',
};

function StatusBadge({ status }: { status: string }) {
  const label = STATUS_OPTIONS.find((s) => s.value === status)?.label ?? status;
  return (
    <span className={clsx('text-xs font-semibold px-2.5 py-0.5 rounded-full', STATUS_COLORS[status] ?? 'bg-slate-100 text-slate-600')}>
      {label}
    </span>
  );
}

const EMPTY_FORM = { room_number: '', room_type: '', floor: '', status: 'VC', notes: '' };

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
export default function RoomsPage() {
  const router = useRouter();
  const { user } = useAuth();
  const canManage = user?.role && ['ADMIN', 'MANAGER'].includes(user.role);
  const isHousekeeping = user?.role === 'HOUSEKEEPING';
  const [rooms, setRooms] = useState<Room[]>([]);
  const [roomTypes, setRoomTypes] = useState<any[]>([]);
  const [floors, setFloors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [statusFilter, setStatusFilter] = useState('all');

  // Panels
  const [editingId, setEditingId] = useState<number | 'new' | null>(null);
  const [viewingRoom, setViewingRoom] = useState<Room | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<Room | null>(null);
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

  const load = async () => {
    setLoading(true);
    try {
      const params = statusFilter !== 'all' ? { status: statusFilter } : {};
      const [roomsData, typesData, floorsData] = await Promise.all([
        roomService.getAll(params),
        roomTypeService.getAll().catch(() => []),
        floorService.getAll().catch(() => ({ results: [] })),
      ]);
      setRooms(roomsData.results || roomsData);
      setRoomTypes(typesData.results || typesData);
      setFloors((floorsData as any).results || floorsData || []);
    } catch {
      showToast('Failed to load rooms', false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [statusFilter]);
  useEffect(() => { setPage(1); }, [statusFilter, perPage]);

  const filtered = rooms;
  const totalPages = Math.max(1, Math.ceil(filtered.length / perPage));
  const safePage = Math.min(page, totalPages);
  const paginated = filtered.slice((safePage - 1) * perPage, safePage * perPage);

  /* ── Panel open/close ── */
  const openNew = () => {
    setForm(EMPTY_FORM);
    setEditingId('new');
  };
  const openEdit = (r: Room) => {
    setForm({
      room_number: r.room_number,
      room_type: String((r as any).room_type ?? ''),
      floor: String((r as any).floor ?? ''),
      status: r.status,
      notes: (r as any).notes ?? '',
    });
    setEditingId(r.id);
  };
  const closePanel = () => setEditingId(null);

  /* ── Save ── */
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.room_number.trim()) { showToast('Room number is required', false); return; }
    if (editingId === 'new' && !form.room_type) { showToast('Room type is required', false); return; }
    setSaving(true);
    try {
      const payload: any = {
        room_number: form.room_number,
        status: form.status,
        notes: form.notes,
      };
      if (form.room_type) payload.room_type = parseInt(form.room_type);
      if (form.floor) payload.floor = parseInt(form.floor); else payload.floor = null;

      if (editingId === 'new') {
        await roomService.create(payload);
        showToast('Room created successfully');
      } else {
        await roomService.update(editingId as number, payload);
        showToast('Room updated successfully');
      }
      closePanel();
      await load();
    } catch (err: any) {
      const detail = err?.response?.data;
      const msg = typeof detail === 'object' ? Object.values(detail).flat().join(' ') : 'Failed to save room';
      showToast(msg as string, false);
    } finally {
      setSaving(false);
    }
  };

  /* ── Delete ── */
  const handleDelete = async () => {
    if (!deleteConfirm) return;
    try {
      await roomService.delete(deleteConfirm.id);
      showToast(`Room ${deleteConfirm.room_number} deleted`);
      setDeleteConfirm(null);
      setViewingRoom(null);
      await load();
    } catch {
      showToast('Failed to delete room', false);
    }
  };

  const inp = (key: keyof typeof EMPTY_FORM) => ({
    value: form[key],
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
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
            <h1 className="text-2xl font-bold text-slate-900">Rooms</h1>
            <p className="text-slate-500 text-sm mt-0.5">{filtered.length} room{filtered.length !== 1 ? 's' : ''}{statusFilter !== 'all' ? ` · ${statusFilter}` : ''}</p>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            {!isHousekeeping && (
              <button onClick={() => router.push('/rooms/types')}
                className="px-4 py-2.5 rounded-xl text-sm font-semibold text-slate-600 border border-slate-200 hover:bg-slate-50 transition-colors">
                Room Types
              </button>
            )}
            {canManage && (
              <button onClick={openNew}
                className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-sm">
                <PlusIcon className="w-4 h-4" /> New Room
              </button>
            )}
          </div>
        </div>

        {/* Status filters */}
        <div className="flex gap-2 flex-wrap">
          {['all', 'VC', 'VD', 'OC', 'OD', 'OOO', 'OOS'].map((s) => (
            <button key={s} onClick={() => setStatusFilter(s)}
              className={clsx('px-4 py-2 text-sm font-semibold rounded-xl transition-colors',
                statusFilter === s ? 'bg-blue-600 text-white shadow-sm' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50')}>
              {s.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Table */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20 text-slate-400">
            <HomeModernIcon className="w-14 h-14 mx-auto mb-3 opacity-30" />
            <p className="font-medium">No rooms found</p>
          </div>
        ) : (
          <>
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-100 bg-slate-50/60">
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Room</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">Floor</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Type</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">Price</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {paginated.map((room) => (
                      <tr key={room.id} className="hover:bg-slate-50/50 transition-colors cursor-pointer" onClick={() => setViewingRoom(room)}>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2.5">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-bold text-xs flex-shrink-0">
                              {room.room_number}
                            </div>
                            <span className="font-semibold text-slate-800">Room {room.room_number}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-slate-500 text-xs hidden sm:table-cell">{room.floor_name || 'N/A'}</td>
                        <td className="px-4 py-3 text-xs text-slate-600">{room.room_type_name || 'N/A'}</td>
                        <td className="px-4 py-3 text-xs text-slate-500 hidden md:table-cell">
                          ${room.room_type_detail?.base_rate ?? 0}/night
                        </td>
                        <td className="px-4 py-3"><StatusBadge status={room.status} /></td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-0.5" onClick={(e) => e.stopPropagation()}>
                            <button onClick={() => setViewingRoom(room)} title="View"
                              className="p-1.5 rounded-lg text-blue-500 hover:text-blue-700 hover:bg-blue-50 transition-colors">
                              <EyeIcon className="w-4 h-4" />
                            </button>
                            {canManage && (
                              <>
                                <button onClick={() => openEdit(room)} title="Edit"
                                  className="p-1.5 rounded-lg text-emerald-500 hover:text-emerald-700 hover:bg-emerald-50 transition-colors">
                                  <PencilSquareIcon className="w-4 h-4" />
                                </button>
                                <button onClick={() => setDeleteConfirm(room)} title="Delete"
                                  className="p-1.5 rounded-lg text-red-500 hover:text-red-700 hover:bg-red-50 transition-colors">
                                  <TrashIcon className="w-4 h-4" />
                                </button>
                              </>
                            )}
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

        {/* ── Create / Edit slide-over ── */}
        {editingId !== null && (
          <div className="fixed inset-0 z-50 flex">
            <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={closePanel} />
            <aside className="w-full max-w-lg bg-white shadow-2xl flex flex-col overflow-hidden">
              <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
                <h2 className="font-bold text-slate-800 text-lg">{editingId === 'new' ? 'Add New Room' : 'Edit Room'}</h2>
                <button onClick={closePanel} className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 transition-colors">
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
              <form onSubmit={handleSave} className="flex-1 overflow-y-auto p-6 space-y-5">
                <section>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Room Details</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Room Number *</label>
                      <input {...inp('room_number')} required placeholder="101" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Room Type {editingId === 'new' && '*'}</label>
                      <select {...inp('room_type')} required={editingId === 'new'} className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white">
                        <option value="">Select a room type…</option>
                        {roomTypes.map((rt) => (
                          <option key={rt.id} value={rt.id}>{rt.name} — ${rt.base_rate}/night · {rt.max_occupancy} guests</option>
                        ))}
                      </select>
                      {roomTypes.length === 0 && (
                        <p className="mt-1 text-xs text-amber-600">No room types found. <a href="/rooms/types/new" className="underline">Create one first.</a></p>
                      )}
                    </div>
                  </div>
                </section>
                <section>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Location & Status</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Floor <span className="text-slate-400 font-normal">(optional)</span></label>
                      <select {...inp('floor')} className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white">
                        <option value="">— No floor assigned —</option>
                        {floors.map((f: any) => (
                          <option key={f.id} value={f.id}>Floor {f.number}{f.name ? ` — ${f.name}` : ''}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Status</label>
                      <select {...inp('status')} className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 bg-white">
                        {STATUS_OPTIONS.map((s) => <option key={s.value} value={s.value}>{s.value} — {s.label}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Notes</label>
                      <textarea {...inp('notes')} rows={3} placeholder="Optional notes…"
                        className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 resize-none" />
                    </div>
                  </div>
                </section>
              </form>
              <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-end gap-3">
                <button onClick={closePanel} className="px-4 py-2.5 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-100 transition-colors">Cancel</button>
                <button onClick={handleSave} disabled={saving}
                  className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold transition-colors shadow-sm disabled:opacity-60">
                  {saving ? 'Saving…' : editingId === 'new' ? 'Create Room' : 'Save Changes'}
                </button>
              </div>
            </aside>
          </div>
        )}

        {/* ── View slide-over ── */}
        {viewingRoom && (
          <div className="fixed inset-0 z-50 flex">
            <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={() => setViewingRoom(null)} />
            <aside className="w-full max-w-lg bg-white shadow-2xl flex flex-col overflow-hidden">
              <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                    {viewingRoom.room_number}
                  </div>
                  <div>
                    <h2 className="font-bold text-slate-800 text-base leading-tight">Room {viewingRoom.room_number}</h2>
                    <p className="text-xs text-slate-400">{viewingRoom.room_type_name || 'No room type'}</p>
                  </div>
                </div>
                <button onClick={() => setViewingRoom(null)} className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 transition-colors">
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto p-6 space-y-5">
                <div>
                  <StatusBadge status={viewingRoom.status} />
                </div>
                {[
                  { label: 'Room Info', rows: [
                    ['Room Number', viewingRoom.room_number],
                    ['Floor', viewingRoom.floor_name ?? 'N/A'],
                    ['Building', (viewingRoom as any).building_name ?? 'N/A'],
                    ['Room Type', viewingRoom.room_type_name ?? 'N/A'],
                  ]},
                  { label: 'Pricing & Capacity', rows: [
                    ['Base Rate', viewingRoom.room_type_detail?.base_rate != null ? `$${viewingRoom.room_type_detail.base_rate}/night` : '—'],
                    ['Max Occupancy', viewingRoom.room_type_detail?.max_occupancy ? `${viewingRoom.room_type_detail.max_occupancy} guests` : '—'],
                    ['Bed Type', viewingRoom.room_type_detail?.bed_type ?? '—'],
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
                {(viewingRoom as any).notes && (
                  <section>
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Notes</p>
                    <p className="text-sm text-slate-600 bg-slate-50 rounded-xl px-4 py-3">{(viewingRoom as any).notes}</p>
                  </section>
                )}
              </div>
              <div className="px-6 py-4 border-t border-slate-100 flex justify-end gap-2">
                {canManage && (
                  <>
                    <button onClick={() => { setViewingRoom(null); openEdit(viewingRoom); }}
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold text-blue-600 border border-blue-200 hover:bg-blue-50 transition-colors">
                      <PencilSquareIcon className="w-4 h-4" /> Edit
                    </button>
                    <button onClick={() => { setDeleteConfirm(viewingRoom); setViewingRoom(null); }}
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold text-red-600 border border-red-200 hover:bg-red-50 transition-colors">
                      <TrashIcon className="w-4 h-4" /> Delete
                    </button>
                  </>
                )}
                <button onClick={() => setViewingRoom(null)} className="px-4 py-2 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-100 transition-colors">
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
              <h3 className="text-center font-bold text-slate-800 text-lg mb-1">Delete Room</h3>
              <p className="text-center text-sm text-slate-500 mb-6">
                Are you sure you want to delete <span className="font-semibold text-slate-700">Room {deleteConfirm.room_number}</span>? This cannot be undone.
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


