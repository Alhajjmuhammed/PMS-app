'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import { roomTypeService } from '@/lib/services';
import clsx from 'clsx';
import {
  PlusIcon, XMarkIcon, EyeIcon, PencilSquareIcon, TrashIcon,
  CheckCircleIcon, TagIcon, ChevronLeftIcon, ChevronRightIcon,
} from '@heroicons/react/24/outline';

/* ── Types ── */
interface RoomTypeAmenity {
  id?: number;
  amenity_name?: string;
  amenity?: number;
  amenity_category?: string;
}

interface RoomType {
  id: number;
  name: string;
  code: string;
  description?: string;
  base_rate: number;
  max_occupancy: number;
  bed_type?: string;
  amenities?: RoomTypeAmenity[];
}

const EMPTY_FORM = {
  name: '',
  code: '',
  description: '',
  base_rate: '',
  max_occupancy: '',
  bed_type: '',
};

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

export default function RoomTypesPage() {
  const router = useRouter();
  const [roomTypes, setRoomTypes] = useState<RoomType[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Panels
  const [editingId, setEditingId] = useState<number | 'new' | null>(null);
  const [viewingType, setViewingType] = useState<RoomType | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<RoomType | null>(null);
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
      const data = await roomTypeService.getAll();
      setRoomTypes(data.results || data);
    } catch {
      showToast('Failed to load room types', false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);
  useEffect(() => { setPage(1); }, [perPage]);

  const totalPages = Math.max(1, Math.ceil(roomTypes.length / perPage));
  const safePage = Math.min(page, totalPages);
  const paginated = roomTypes.slice((safePage - 1) * perPage, safePage * perPage);

  /* ── Panel helpers ── */
  const openNew = () => {
    setForm(EMPTY_FORM);
    setEditingId('new');
  };
  const openEdit = (rt: RoomType) => {
    setForm({
      name: rt.name,
      code: rt.code ?? '',
      description: rt.description ?? '',
      base_rate: String(rt.base_rate ?? ''),
      max_occupancy: String(rt.max_occupancy ?? ''),
      bed_type: rt.bed_type ?? '',
    });
    setEditingId(rt.id);
  };
  const closePanel = () => setEditingId(null);

  const inp = (key: keyof typeof EMPTY_FORM) => ({
    value: form[key],
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value })),
  });

  /* ── Save ── */
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) { showToast('Name is required', false); return; }
    if (!form.code.trim() || form.code.trim().length < 2) { showToast('Code must be at least 2 characters', false); return; }
    if (!form.base_rate || isNaN(Number(form.base_rate))) { showToast('Valid base rate is required', false); return; }
    if (!form.max_occupancy || isNaN(Number(form.max_occupancy))) { showToast('Valid max occupancy is required', false); return; }
    setSaving(true);
    try {
      const payload: any = {
        name: form.name,
        code: form.code.trim().toUpperCase(),
        description: form.description,
        base_rate: parseFloat(form.base_rate),
        max_occupancy: parseInt(form.max_occupancy),
        bed_type: form.bed_type,
      };
      if (editingId === 'new') {
        await roomTypeService.create(payload);
        showToast('Room type created successfully');
      } else {
        await roomTypeService.update(editingId as number, payload);
        showToast('Room type updated successfully');
      }
      closePanel();
      await load();
    } catch (err: any) {
      const detail = err?.response?.data;
      const msg = typeof detail === 'object' ? Object.values(detail).flat().join(' ') : 'Failed to save room type';
      showToast(msg as string, false);
    } finally {
      setSaving(false);
    }
  };

  /* ── Delete ── */
  const handleDelete = async () => {
    if (!deleteConfirm) return;
    try {
      await roomTypeService.delete(deleteConfirm.id);
      showToast(`"${deleteConfirm.name}" deleted`);
      setDeleteConfirm(null);
      setViewingType(null);
      await load();
    } catch {
      showToast('Failed to delete room type', false);
    }
  };

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
            <h1 className="text-2xl font-bold text-slate-900">Room Types</h1>
            <p className="text-slate-500 text-sm mt-0.5">{roomTypes.length} type{roomTypes.length !== 1 ? 's' : ''}</p>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <button onClick={() => router.push('/rooms')}
              className="px-4 py-2.5 rounded-xl text-sm font-semibold text-slate-600 border border-slate-200 hover:bg-slate-50 transition-colors">
              Rooms
            </button>
            <button onClick={openNew}
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-sm">
              <PlusIcon className="w-4 h-4" /> New Room Type
            </button>
          </div>
        </div>

        {/* Table */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : roomTypes.length === 0 ? (
          <div className="text-center py-20 text-slate-400">
            <TagIcon className="w-14 h-14 mx-auto mb-3 opacity-30" />
            <p className="font-medium">No room types yet</p>
            <p className="text-sm mt-1">Add your first room type to get started</p>
          </div>
        ) : (
          <>
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-100 bg-slate-50/60">
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Name</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">Bed Type</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Base Rate</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">Occupancy</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:table-cell">Amenities</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {paginated.map((rt) => (
                      <tr key={rt.id} className="hover:bg-slate-50/50 transition-colors cursor-pointer" onClick={() => setViewingType(rt)}>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2.5">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-violet-600 flex items-center justify-center text-white flex-shrink-0">
                              <TagIcon className="w-4 h-4" />
                            </div>
                            <div>
                              <p className="font-semibold text-slate-800">{rt.name}</p>
                              {rt.description && <p className="text-xs text-slate-400 truncate max-w-[180px]">{rt.description}</p>}
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-xs text-slate-500 hidden sm:table-cell">{rt.bed_type || '—'}</td>
                        <td className="px-4 py-3">
                          <span className="text-sm font-semibold text-slate-700">${rt.base_rate?.toLocaleString()}</span>
                          <span className="text-xs text-slate-400">/night</span>
                        </td>
                        <td className="px-4 py-3 text-xs text-slate-500 hidden md:table-cell">{rt.max_occupancy} guest{rt.max_occupancy !== 1 ? 's' : ''}</td>
                        <td className="px-4 py-3 hidden lg:table-cell">
                          <div className="flex flex-wrap gap-1">
                            {(rt.amenities ?? []).slice(0, 3).map((a, i) => (
                              <span key={i} className="px-2 py-0.5 bg-violet-50 text-violet-700 rounded-full text-xs font-medium">{a.amenity_name}</span>
                            ))}
                            {(rt.amenities?.length ?? 0) > 3 && (
                              <span className="px-2 py-0.5 bg-slate-100 text-slate-500 rounded-full text-xs">+{(rt.amenities?.length ?? 0) - 3}</span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-0.5" onClick={(e) => e.stopPropagation()}>
                            <button onClick={() => setViewingType(rt)} title="View"
                              className="p-1.5 rounded-lg text-blue-500 hover:text-blue-700 hover:bg-blue-50 transition-colors">
                              <EyeIcon className="w-4 h-4" />
                            </button>
                            <button onClick={() => openEdit(rt)} title="Edit"
                              className="p-1.5 rounded-lg text-emerald-500 hover:text-emerald-700 hover:bg-emerald-50 transition-colors">
                              <PencilSquareIcon className="w-4 h-4" />
                            </button>
                            <button onClick={() => setDeleteConfirm(rt)} title="Delete"
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
            <Pagination total={roomTypes.length} safePage={safePage} perPage={perPage} totalPages={totalPages} onPageChange={setPage} onPerPageChange={setPerPage} />
          </>
        )}

        {/* ── Create / Edit slide-over ── */}
        {editingId !== null && (
          <div className="fixed inset-0 z-50 flex">
            <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={closePanel} />
            <aside className="w-full max-w-lg bg-white shadow-2xl flex flex-col overflow-hidden">
              <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
                <h2 className="font-bold text-slate-800 text-lg">{editingId === 'new' ? 'Add Room Type' : 'Edit Room Type'}</h2>
                <button onClick={closePanel} className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 transition-colors">
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
              <form onSubmit={handleSave} className="flex-1 overflow-y-auto p-6 space-y-5">
                <section>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Basic Info</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Name *</label>
                      <input {...inp('name')} required placeholder="e.g. Deluxe King" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Code * <span className="text-slate-400 font-normal">(short unique code, e.g. DLX, STD)</span></label>
                      <input {...inp('code')} required placeholder="DLX" maxLength={20}
                        className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 uppercase" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Description</label>
                      <textarea {...inp('description')} rows={3} placeholder="Optional description…"
                        className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300 resize-none" />
                    </div>
                  </div>
                </section>
                <section>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Pricing & Capacity</p>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Base Rate ($/night) *</label>
                      <input {...inp('base_rate')} type="number" min="0" step="0.01" required placeholder="150.00"
                        className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Max Occupancy *</label>
                      <input {...inp('max_occupancy')} type="number" min="1" required placeholder="2"
                        className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300" />
                    </div>
                  </div>
                </section>
                <section>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Room Features</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 mb-1">Bed Type</label>
                      <input {...inp('bed_type')} placeholder="e.g. King, Twin, Queen" className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-300" />
                    </div>

                  </div>
                </section>
              </form>
              <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-end gap-3">
                <button onClick={closePanel} className="px-4 py-2.5 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-100 transition-colors">Cancel</button>
                <button onClick={handleSave} disabled={saving}
                  className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold transition-colors shadow-sm disabled:opacity-60">
                  {saving ? 'Saving…' : editingId === 'new' ? 'Create Type' : 'Save Changes'}
                </button>
              </div>
            </aside>
          </div>
        )}

        {/* ── View slide-over ── */}
        {viewingType && (
          <div className="fixed inset-0 z-50 flex">
            <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={() => setViewingType(null)} />
            <aside className="w-full max-w-lg bg-white shadow-2xl flex flex-col overflow-hidden">
              <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-violet-600 flex items-center justify-center flex-shrink-0">
                    <TagIcon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="font-bold text-slate-800 text-base leading-tight">{viewingType.name}</h2>
                    <p className="text-xs text-slate-400">{viewingType.code}{viewingType.description ? ` · ${viewingType.description}` : ''}</p>
                  </div>
                </div>
                <button onClick={() => setViewingType(null)} className="p-2 rounded-xl text-slate-400 hover:bg-slate-100 transition-colors">
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto p-6 space-y-5">
                <section>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Details</p>
                  <div className="bg-slate-50 rounded-xl divide-y divide-slate-100">
                    {([
                      ['Code', viewingType.code],
                      ['Base Rate', `$${viewingType.base_rate?.toLocaleString()}/night`],
                      ['Max Occupancy', `${viewingType.max_occupancy} guest${viewingType.max_occupancy !== 1 ? 's' : ''}`],
                      ['Bed Type', viewingType.bed_type || '—'],
                    ] as [string, string][]).map(([k, v]) => (
                      <div key={k} className="flex items-center justify-between px-4 py-2.5">
                        <span className="text-xs text-slate-500">{k}</span>
                        <span className="text-xs font-semibold text-slate-700">{v}</span>
                      </div>
                    ))}
                  </div>
                </section>
                {(viewingType.amenities ?? []).length > 0 && (
                  <section>
                    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Amenities</p>
                    <div className="flex flex-wrap gap-2">
                      {(viewingType.amenities ?? []).map((a, i) => (
                        <span key={i} className="px-3 py-1 bg-violet-50 text-violet-700 rounded-full text-xs font-medium">{a.amenity_name}</span>
                      ))}
                    </div>
                  </section>
                )}
              </div>
              <div className="px-6 py-4 border-t border-slate-100 flex justify-end gap-2">
                <button onClick={() => { setViewingType(null); openEdit(viewingType); }}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold text-blue-600 border border-blue-200 hover:bg-blue-50 transition-colors">
                  <PencilSquareIcon className="w-4 h-4" /> Edit
                </button>
                <button onClick={() => { setDeleteConfirm(viewingType); setViewingType(null); }}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold text-red-600 border border-red-200 hover:bg-red-50 transition-colors">
                  <TrashIcon className="w-4 h-4" /> Delete
                </button>
                <button onClick={() => setViewingType(null)} className="px-4 py-2 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-100 transition-colors">
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
              <h3 className="text-center font-bold text-slate-800 text-lg mb-1">Delete Room Type</h3>
              <p className="text-center text-sm text-slate-500 mb-6">
                Are you sure you want to delete <span className="font-semibold text-slate-700">&ldquo;{deleteConfirm.name}&rdquo;</span>? Rooms using this type will be affected.
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
