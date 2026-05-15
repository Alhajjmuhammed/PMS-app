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
  ClipboardDocumentListIcon,
  SparklesIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  FunnelIcon,
  ArchiveBoxIcon,
  ArrowsRightLeftIcon,
  PencilSquareIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  HomeIcon,
} from '@heroicons/react/24/outline';

// ── Types ─────────────────────────────────────────────────────────
interface Choice { value: string; label: string; }

interface Choices {
  task_types: Choice[];
  priorities: Choice[];
  statuses: Choice[];
  movement_types: Choice[];
  linen_types: Choice[];
}

interface Task {
  id: number;
  room: number;
  room_number: string;
  task_type: string;
  priority: string;
  status: string;
  assigned_to: number | null;
  assigned_to_name: string | null;
  scheduled_date: string;
  started_at: string | null;
  completed_at: string | null;
  notes: string;
  special_instructions: string;
  created_by_name: string | null;
  created_at: string;
}

interface DashboardStats {
  pending_tasks: number;
  in_progress_tasks: number;
  completed_today: number;
  clean_rooms: number;
  dirty_rooms: number;
  inspecting_rooms: number;
  out_of_order_rooms: number;
}

interface LinenInventory {
  id: number;
  linen_type: string;
  quantity_total: number;
  quantity_in_use: number;
  quantity_in_laundry: number;
  quantity_damaged: number;
  reorder_level: number;
}

interface AmenityInventory {
  id: number;
  name: string;
  code: string;
  category: string;
  quantity: number;
  reorder_level: number;
  unit_cost: string;
}

interface StockMovement {
  id: number;
  movement_type: string;
  quantity: number;
  balance_after: number;
  amenity_inventory: number | null;
  linen_inventory: number | null;
  amenity_name: string | null;
  linen_type_display: string | null;
  reason: string;
  notes: string;
  from_location: string;
  to_location: string;
  created_by_name: string | null;
  created_at: string;
}

interface StaffUser { id: number; first_name: string; last_name: string; }
interface Room { id: number; room_number: string; }

// ── Fallback constants (used until choices loaded) ─────────────────
const DEFAULT_PRIORITIES = [
  { value: 'LOW', label: 'Low' },
  { value: 'NORMAL', label: 'Normal' },
  { value: 'HIGH', label: 'High' },
  { value: 'URGENT', label: 'Urgent' },
];
const DEFAULT_STATUSES = [
  { value: 'PENDING', label: 'Pending' },
  { value: 'IN_PROGRESS', label: 'In Progress' },
  { value: 'COMPLETED', label: 'Completed' },
  { value: 'INSPECTED', label: 'Inspected' },
  { value: 'CANCELLED', label: 'Cancelled' },
];

// ── Colour helpers ────────────────────────────────────────────────
const PRIORITY_COLORS: Record<string, string> = {
  LOW: 'bg-slate-100 text-slate-600',
  NORMAL: 'bg-blue-100 text-blue-700',
  HIGH: 'bg-orange-100 text-orange-700',
  URGENT: 'bg-red-100 text-red-700',
};
const STATUS_COLORS: Record<string, string> = {
  PENDING: 'bg-amber-100 text-amber-700',
  IN_PROGRESS: 'bg-blue-100 text-blue-700',
  COMPLETED: 'bg-emerald-100 text-emerald-700',
  INSPECTED: 'bg-purple-100 text-purple-700',
  CANCELLED: 'bg-slate-100 text-slate-500',
};
const MOVEMENT_COLORS: Record<string, string> = {
  RECEIVE: 'bg-emerald-100 text-emerald-700',
  ISSUE: 'bg-blue-100 text-blue-700',
  TRANSFER: 'bg-indigo-100 text-indigo-700',
  ADJUST: 'bg-amber-100 text-amber-700',
  RETURN: 'bg-teal-100 text-teal-700',
  DAMAGE: 'bg-red-100 text-red-700',
};

function pColor(p: string) { return PRIORITY_COLORS[p] ?? 'bg-slate-100 text-slate-600'; }
function sColor(s: string) { return STATUS_COLORS[s] ?? 'bg-slate-100 text-slate-600'; }
function mColor(m: string) { return MOVEMENT_COLORS[m] ?? 'bg-slate-100 text-slate-600'; }

function choiceLabel(choices: Choice[], val: string) {
  return choices.find((c) => c.value === val)?.label ?? val;
}

function formatDate(s: string) {
  if (!s) return '—';
  return new Date(s).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}
function formatDateTime(s: string | null) {
  if (!s) return '—';
  return new Date(s).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

const EMPTY_TASK_FORM = {
  room: '',
  task_type: 'CLEANING',
  priority: 'NORMAL',
  assigned_to: '',
  scheduled_date: new Date().toISOString().slice(0, 10),
  notes: '',
  special_instructions: '',
};
const EMPTY_MOVE_FORM = {
  movement_type: 'RECEIVE',
  item_type: 'amenity' as 'amenity' | 'linen',
  amenity_inventory: '',
  linen_inventory: '',
  quantity: '',
  reason: '',
  notes: '',
  from_location: '',
  to_location: '',
};

const EMPTY_LINEN_FORM = {
  linen_type: 'BEDSHEET',
  quantity_total: '',
  quantity_in_use: '0',
  quantity_in_laundry: '0',
  quantity_damaged: '0',
  reorder_level: '',
};

const AMENITY_CATEGORIES = [
  'Bathroom',
  'Bedroom',
  'Food & Beverage',
  'Entertainment',
  'Business',
  'Fitness',
  'Cleaning',
  'Safety',
  'Other',
];

const EMPTY_AMENITY_FORM = {
  name: '',
  code: '',
  category: '',
  quantity: '',
  reorder_level: '',
  unit_cost: '',
};

// ── Pagination ────────────────────────────────────────────────────
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

// ── Main Page ─────────────────────────────────────────────────────
export default function HousekeepingPage() {
  const { user } = useAuth();
  const canManage = user?.role && ['ADMIN', 'MANAGER'].includes(user.role);

  // ── Choices (dynamic from backend) ────────────────────────────
  const [choices, setChoices] = useState<Choices>({
    task_types: [{ value: 'CLEANING', label: 'Cleaning' }],
    priorities: DEFAULT_PRIORITIES,
    statuses: DEFAULT_STATUSES,
    movement_types: [],
    linen_types: [],
  });

  // ── Tabs ───────────────────────────────────────────────────────
  const [tab, setTab] = useState<'tasks' | 'inventory' | 'movements'>('tasks');
  const [inventoryTab, setInventoryTab] = useState<'linens' | 'amenities'>('linens');

  // ── Tasks state ────────────────────────────────────────────────
  const [tasks, setTasks] = useState<Task[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [staff, setStaff] = useState<StaffUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);

  // ── Inventory state ────────────────────────────────────────────
  const [linens, setLinens] = useState<LinenInventory[]>([]);
  const [amenities, setAmenities] = useState<AmenityInventory[]>([]);
  const [movements, setMovements] = useState<StockMovement[]>([]);
  const [invLoading, setInvLoading] = useState(false);
  const [movLoading, setMovLoading] = useState(false);
  const [movPage, setMovPage] = useState(1);
  const [movPerPage, setMovPerPage] = useState(20);
  const [movDatePreset, setMovDatePreset] = useState<'all' | 'today' | 'week' | 'month' | 'year' | 'custom'>('all');
  const [movDateFrom, setMovDateFrom] = useState('');
  const [movDateTo, setMovDateTo] = useState('');

  // ── Slide-overs ────────────────────────────────────────────────
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [taskForm, setTaskForm] = useState(EMPTY_TASK_FORM);
  const [saving, setSaving] = useState(false);
  const [viewTask, setViewTask] = useState<Task | null>(null);
  const [showMoveForm, setShowMoveForm] = useState(false);
  const [moveForm, setMoveForm] = useState(EMPTY_MOVE_FORM);

  // ── Linen form state ───────────────────────────────────────────
  const [showLinenForm, setShowLinenForm] = useState(false);
  const [editLinen, setEditLinen] = useState<LinenInventory | null>(null);
  const [linenForm, setLinenForm] = useState(EMPTY_LINEN_FORM);

  // ── Amenity form state ─────────────────────────────────────────
  const [showAmenityForm, setShowAmenityForm] = useState(false);
  const [editAmenity, setEditAmenity] = useState<AmenityInventory | null>(null);
  const [amenityForm, setAmenityForm] = useState(EMPTY_AMENITY_FORM);

  // ── Toast ──────────────────────────────────────────────────────
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  };

  // ── Load choices once ──────────────────────────────────────────
  useEffect(() => {
    api.get('/api/v1/housekeeping/choices/').then((r) => {
      setChoices(r.data);
      setTaskForm((f) => ({ ...f, task_type: r.data.task_types[0]?.value ?? 'CLEANING' }));
    }).catch(() => {}); // keep fallback if it fails
  }, []);

  // ── Load tasks + stats ─────────────────────────────────────────
  const loadTasks = useCallback(async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (statusFilter) params.status = statusFilter;
      if (priorityFilter) params.priority = priorityFilter;
      const [tRes, sRes] = await Promise.all([
        api.get('/api/v1/housekeeping/tasks/', { params }),
        api.get('/api/v1/housekeeping/dashboard/'),
      ]);
      setTasks(Array.isArray(tRes.data?.results ?? tRes.data) ? (tRes.data?.results ?? tRes.data) : []);
      setStats(sRes.data);
    } catch { showToast('Failed to load tasks', false); }
    finally { setLoading(false); }
  }, [statusFilter, priorityFilter]);

  // ── Load inventory ─────────────────────────────────────────────
  const loadInventory = useCallback(async () => {
    setInvLoading(true);
    try {
      const [lRes, aRes] = await Promise.all([
        api.get('/api/v1/housekeeping/inventory/linens/'),
        api.get('/api/v1/housekeeping/inventory/amenities/'),
      ]);
      setLinens(lRes.data?.results ?? lRes.data ?? []);
      setAmenities(aRes.data?.results ?? aRes.data ?? []);
    } catch { showToast('Failed to load inventory', false); }
    finally { setInvLoading(false); }
  }, []);

  // ── Load movements ─────────────────────────────────────────────
  const loadMovements = useCallback(async () => {
    setMovLoading(true);
    try {
      const r = await api.get('/api/v1/housekeeping/inventory/movements/');
      setMovements(r.data?.results ?? r.data ?? []);
    } catch { showToast('Failed to load movements', false); }
    finally { setMovLoading(false); }
  }, []);

  // ── Load rooms + staff for forms ───────────────────────────────
  useEffect(() => {
    if (!canManage) return;
    Promise.all([
      api.get('/api/v1/rooms/').catch(() => null),
      api.get('/api/v1/auth/users/?role=HOUSEKEEPING').catch(() => null),
    ]).then(([rR, sR]) => {
      if (rR) setRooms(Array.isArray(rR.data?.results ?? rR.data) ? (rR.data?.results ?? rR.data) : []);
      if (sR) setStaff(Array.isArray(sR.data?.results ?? sR.data) ? (sR.data?.results ?? sR.data) : []);
    });
  }, [canManage]);

  // ── Filtered movements (date range) ───────────────────────────
  const filteredMovements = useMemo(() => {
    if (movDatePreset === 'all') return movements;
    const now = new Date();
    let from: Date;
    let to: Date = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999);
    if (movDatePreset === 'today') {
      from = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    } else if (movDatePreset === 'week') {
      from = new Date(now); from.setDate(now.getDate() - 6); from.setHours(0, 0, 0, 0);
    } else if (movDatePreset === 'month') {
      from = new Date(now.getFullYear(), now.getMonth(), 1);
    } else if (movDatePreset === 'year') {
      from = new Date(now.getFullYear(), 0, 1);
    } else {
      from = movDateFrom ? new Date(movDateFrom + 'T00:00:00') : new Date(0);
      to   = movDateTo   ? new Date(movDateTo   + 'T23:59:59') : new Date();
    }
    return movements.filter((m) => { const d = new Date(m.created_at); return d >= from && d <= to; });
  }, [movements, movDatePreset, movDateFrom, movDateTo]);

  useEffect(() => { loadTasks(); }, [loadTasks]);
  useEffect(() => { loadInventory(); }, [loadInventory]); // always load — needed for movement item selector
  useEffect(() => { setPage(1); }, [statusFilter, priorityFilter]);
  useEffect(() => { setMovPage(1); }, [movDatePreset, movDateFrom, movDateTo]);
  useEffect(() => {
    if (tab === 'movements') loadMovements();
  }, [tab, loadMovements]);

  const totalPages = Math.max(1, Math.ceil(tasks.length / perPage));
  const safePage = Math.min(page, totalPages);
  const paginated = tasks.slice((safePage - 1) * perPage, safePage * perPage);

  // ── Actions ────────────────────────────────────────────────────
  const handleStart = async (task: Task) => {
    try {
      await api.post(`/api/v1/housekeeping/tasks/${task.id}/start/`);
      showToast('Task started');
      loadTasks();
    } catch { showToast('Failed to start task', false); }
  };

  const handleComplete = async (task: Task) => {
    try {
      await api.post(`/api/v1/housekeeping/tasks/${task.id}/complete/`);
      showToast('Task completed');
      if (viewTask?.id === task.id) setViewTask(null);
      loadTasks();
    } catch { showToast('Failed to complete task', false); }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload: any = { ...taskForm };
      if (!payload.assigned_to) delete payload.assigned_to;
      await api.post('/api/v1/housekeeping/tasks/', payload);
      showToast('Task created');
      setShowTaskForm(false);
      setTaskForm(EMPTY_TASK_FORM);
      loadTasks();
    } catch (err: any) {
      const d = err?.response?.data;
      showToast(typeof d === 'object' ? Object.values(d).flat().join(' ') : 'Failed to create task', false);
    } finally { setSaving(false); }
  };

  // ── Open linen form ───────────────────────────────────────────
  const openLinenForm = (l?: LinenInventory) => {
    if (l) {
      setEditLinen(l);
      setLinenForm({
        linen_type: l.linen_type,
        quantity_total: String(l.quantity_total),
        quantity_in_use: String(l.quantity_in_use),
        quantity_in_laundry: String(l.quantity_in_laundry),
        quantity_damaged: String(l.quantity_damaged),
        reorder_level: String(l.reorder_level),
      });
    } else {
      const usedTypes = new Set(linens.map((ln) => ln.linen_type));
      const available = choices.linen_types.filter((t) => !usedTypes.has(t.value));
      if (available.length === 0) {
        showToast('All linen types are already added for this property', false);
        return;
      }
      setEditLinen(null);
      setLinenForm({ ...EMPTY_LINEN_FORM, linen_type: available[0].value });
    }
    setShowLinenForm(true);
  };

  const handleSaveLinen = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    const propertyId = user?.assigned_property?.id;
    if (!propertyId) { showToast('No property assigned to your account', false); setSaving(false); return; }
    try {
      const payload = {
        hotel: propertyId,
        linen_type: linenForm.linen_type,
        quantity_total: Number(linenForm.quantity_total),
        quantity_in_use: Number(linenForm.quantity_in_use),
        quantity_in_laundry: Number(linenForm.quantity_in_laundry),
        quantity_damaged: Number(linenForm.quantity_damaged),
        reorder_level: Number(linenForm.reorder_level),
      };
      if (editLinen) {
        await api.patch(`/api/v1/housekeeping/inventory/linens/${editLinen.id}/`, payload);
        showToast('Linen updated');
      } else {
        await api.post('/api/v1/housekeeping/inventory/linens/', payload);
        showToast('Linen added');
      }
      setShowLinenForm(false);
      loadInventory();
    } catch (err: any) {
      const d = err?.response?.data;
      showToast(typeof d === 'object' ? Object.values(d).flat().join(' ') : 'Failed to save linen', false);
    } finally { setSaving(false); }
  };

  const handleDeleteLinen = async (l: LinenInventory) => {
    if (!confirm(`Delete ${choiceLabel(choices.linen_types, l.linen_type)}? This cannot be undone.`)) return;
    try {
      await api.delete(`/api/v1/housekeeping/inventory/linens/${l.id}/`);
      showToast('Linen deleted');
      loadInventory();
    } catch { showToast('Failed to delete linen', false); }
  };

  // ── Open amenity form ──────────────────────────────────────────
  const openAmenityForm = (a?: AmenityInventory) => {
    if (a) {
      setEditAmenity(a);
      setAmenityForm({
        name: a.name,
        code: a.code,
        category: a.category,
        quantity: String(a.quantity),
        reorder_level: String(a.reorder_level),
        unit_cost: a.unit_cost,
      });
    } else {
      setEditAmenity(null);
      setAmenityForm(EMPTY_AMENITY_FORM);
    }
    setShowAmenityForm(true);
  };

  const handleSaveAmenity = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    const propertyId = user?.assigned_property?.id;
    if (!propertyId) { showToast('No property assigned to your account', false); setSaving(false); return; }
    try {
      const payload = {
        hotel: propertyId,
        name: amenityForm.name,
        code: amenityForm.code,
        category: amenityForm.category,
        quantity: Number(amenityForm.quantity),
        reorder_level: Number(amenityForm.reorder_level),
        unit_cost: amenityForm.unit_cost,
      };
      if (editAmenity) {
        await api.patch(`/api/v1/housekeeping/inventory/amenities/${editAmenity.id}/`, payload);
        showToast('Amenity updated');
      } else {
        await api.post('/api/v1/housekeeping/inventory/amenities/', payload);
        showToast('Amenity added');
      }
      setShowAmenityForm(false);
      loadInventory();
    } catch (err: any) {
      const d = err?.response?.data;
      showToast(typeof d === 'object' ? Object.values(d).flat().join(' ') : 'Failed to save amenity', false);
    } finally { setSaving(false); }
  };

  const handleDeleteAmenity = async (a: AmenityInventory) => {
    if (!confirm(`Delete "${a.name}"? This cannot be undone.`)) return;
    try {
      await api.delete(`/api/v1/housekeeping/inventory/amenities/${a.id}/`);
      showToast('Amenity deleted');
      loadInventory();
    } catch { showToast('Failed to delete amenity', false); }
  };

  const handleDeleteMovement = async (id: number) => {
    if (!confirm('Delete this movement record? This cannot be undone.')) return;
    try {
      await api.delete(`/api/v1/housekeeping/inventory/movements/${id}/`);
      showToast('Movement deleted');
      loadMovements();
    } catch { showToast('Failed to delete movement', false); }
  };

  // ── Export helpers ─────────────────────────────────────────────
  const getMovementItemName = (m: StockMovement) =>
    m.amenity_name
    ?? (m.linen_type_display ? choiceLabel(choices.linen_types, m.linen_type_display) : null)
    ?? (m.amenity_inventory ? amenities.find((a) => a.id === m.amenity_inventory)?.name : null)
    ?? (m.linen_inventory ? choiceLabel(choices.linen_types, linens.find((l) => l.id === m.linen_inventory)?.linen_type ?? '') : null)
    ?? '';

  const exportCSV = () => {
    const header = ['ID', 'Type', 'Item', 'Qty', 'Balance After', 'Reason', 'Notes', 'By', 'Date'];
    const rows = filteredMovements.map((m) => [
      m.id,
      choiceLabel(choices.movement_types, m.movement_type),
      getMovementItemName(m),
      m.quantity,
      m.balance_after,
      m.reason,
      m.notes,
      m.created_by_name ?? '',
      formatDateTime(m.created_at),
    ]);
    const csv = [header, ...rows]
      .map((r) => r.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(','))
      .join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `stock-movements-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportPDF = () => {
    const data = filteredMovements.map((m) => ({
      id: String(m.id),
      type: choiceLabel(choices.movement_types, m.movement_type),
      item: getMovementItemName(m),
      qty: m.quantity >= 0 ? `+${m.quantity}` : String(m.quantity),
      qtyPositive: m.quantity >= 0,
      balance: String(m.balance_after),
      reason: m.reason || '—',
      by: m.created_by_name ?? '—',
      date: formatDateTime(m.created_at),
    }));
    const headers = ['ID', 'Type', 'Item', 'Qty', 'Balance', 'Reason', 'By', 'Date'];
    const colW = [30, 60, 100, 30, 50, 100, 80, 120];
    const totalW = colW.reduce((a, b) => a + b, 0) + colW.length * 8;
    const rowH = 18;
    const headerH = 24;
    const paddingX = 20;
    const paddingY = 20;
    const titleH = 30;
    const height = paddingY * 2 + titleH + headerH + data.length * rowH + 10;
    const svgLines: string[] = [];
    let y = paddingY;
    svgLines.push(`<text x="${paddingX}" y="${y + 16}" font-family="Arial" font-size="14" font-weight="bold" fill="#1e293b">Stock Movements Export</text>`);
    svgLines.push(`<text x="${paddingX + totalW - 10}" y="${y + 16}" font-family="Arial" font-size="10" fill="#94a3b8" text-anchor="end">${new Date().toLocaleDateString()}</text>`);
    y += titleH;
    svgLines.push(`<rect x="${paddingX}" y="${y}" width="${totalW}" height="${headerH}" fill="#f1f5f9" rx="4"/>`);
    let x = paddingX + 4;
    headers.forEach((h, i) => {
      svgLines.push(`<text x="${x}" y="${y + 16}" font-family="Arial" font-size="9" font-weight="bold" fill="#64748b">${h}</text>`);
      x += colW[i] + 8;
    });
    y += headerH;
    data.forEach((row, ri) => {
      if (ri % 2 === 1) svgLines.push(`<rect x="${paddingX}" y="${y}" width="${totalW}" height="${rowH}" fill="#f8fafc"/>`);
      x = paddingX + 4;
      const cells = [row.id, row.type, row.item, row.qty, row.balance, row.reason, row.by, row.date];
      cells.forEach((cell, ci) => {
        const truncated = cell.length > 20 ? cell.slice(0, 18) + '\u2026' : cell;
        // ci===3 is Qty column — use the boolean flag, not string parsing
        const fill = ci === 3 ? (row.qtyPositive ? '#059669' : '#dc2626') : '#334155';
        svgLines.push(`<text x="${x}" y="${y + 13}" font-family="Arial" font-size="9" fill="${fill}">${truncated.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</text>`);
        x += colW[ci] + 8;
      });
      y += rowH;
    });
    svgLines.push(`<rect x="${paddingX}" y="${paddingY + titleH}" width="${totalW}" height="${headerH + data.length * rowH}" fill="none" stroke="#e2e8f0" stroke-width="1" rx="4"/>`);
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${totalW + paddingX * 2}" height="${height}">${svgLines.join('')}</svg>`;
    const blob = new Blob([svg], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `stock-movements-${new Date().toISOString().slice(0, 10)}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleLogMovement = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload: any = {
        movement_type: moveForm.movement_type,
        quantity: Number(moveForm.quantity),
        reason: moveForm.reason,
        notes: moveForm.notes,
        from_location: moveForm.from_location,
        to_location: moveForm.to_location,
      };
      if (moveForm.item_type === 'amenity') payload.amenity_inventory = Number(moveForm.amenity_inventory);
      else payload.linen_inventory = Number(moveForm.linen_inventory);
      await api.post('/api/v1/housekeeping/inventory/movements/', payload);
      showToast('Movement logged');
      setShowMoveForm(false);
      setMoveForm(EMPTY_MOVE_FORM);
      loadMovements();
      loadInventory(); // refresh stock numbers
    } catch (err: any) {
      const d = err?.response?.data;
      showToast(typeof d === 'object' ? Object.values(d).flat().join(' ') : 'Failed to log movement', false);
    } finally { setSaving(false); }
  };

  // ── Render ─────────────────────────────────────────────────────
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

        {/* Breadcrumb */}
        <nav className="flex items-center gap-1.5 text-sm text-slate-400">
          <HomeIcon className="w-4 h-4" />
          <span>Home</span>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <span className="text-slate-700 font-medium">Housekeeping</span>
        </nav>

        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-teal-100 flex items-center justify-center flex-shrink-0">
              <SparklesIcon className="w-5 h-5 text-teal-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Housekeeping</h1>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {tab === 'movements' && (
              <button onClick={() => setShowMoveForm(true)}
                className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-sm">
                <ArrowsRightLeftIcon className="w-4 h-4" />
                Log Movement
              </button>
            )}
            {tab === 'inventory' && inventoryTab === 'linens' && canManage && (
              choices.linen_types.length > linens.length ? (
                <button onClick={() => openLinenForm()}
                  className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-sm">
                  <PlusIcon className="w-4 h-4" />
                  Add Linen
                </button>
              ) : (
                <span className="text-xs text-slate-400 italic">All types added — use ✏️ to edit quantities</span>
              )
            )}
            {tab === 'inventory' && inventoryTab === 'amenities' && canManage && (
              <button onClick={() => openAmenityForm()}
                className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-sm">
                <PlusIcon className="w-4 h-4" />
                Add Amenity
              </button>
            )}
            {tab === 'tasks' && canManage && (
              <button onClick={() => setShowTaskForm(true)}
                className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2.5 rounded-xl transition-colors shadow-sm">
                <PlusIcon className="w-4 h-4" />
                New Task
              </button>
            )}
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
            <StatCard label="Pending"      value={stats.pending_tasks}      color="bg-amber-50"   icon={<ClockIcon className="w-5 h-5 text-amber-600" />} />
            <StatCard label="In Progress"  value={stats.in_progress_tasks}  color="bg-blue-50"    icon={<PlayIcon className="w-5 h-5 text-blue-600" />} />
            <StatCard label="Done Today"   value={stats.completed_today}    color="bg-emerald-50" icon={<CheckCircleIcon className="w-5 h-5 text-emerald-600" />} />
            <StatCard label="Clean"        value={stats.clean_rooms}        color="bg-teal-50"    icon={<SparklesIcon className="w-5 h-5 text-teal-600" />} />
            <StatCard label="Dirty"        value={stats.dirty_rooms}        color="bg-orange-50"  icon={<ClipboardDocumentListIcon className="w-5 h-5 text-orange-600" />} />
            <StatCard label="Inspecting"   value={stats.inspecting_rooms}   color="bg-purple-50"  icon={<FunnelIcon className="w-5 h-5 text-purple-600" />} />
            <StatCard label="Out of Order" value={stats.out_of_order_rooms} color="bg-red-50"     icon={<ExclamationTriangleIcon className="w-5 h-5 text-red-600" />} />
          </div>
        )}

        {/* Main Tabs */}
        <div className="flex gap-1 border-b border-slate-200">
          {([
            { id: 'tasks',      label: 'Tasks',     icon: <ClipboardDocumentListIcon className="w-4 h-4" /> },
            { id: 'inventory',  label: 'Inventory', icon: <ArchiveBoxIcon className="w-4 h-4" /> },
            { id: 'movements',  label: 'Stock Movements', icon: <ArrowsRightLeftIcon className="w-4 h-4" /> },
          ] as const).map((t) => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={clsx(
                'flex items-center gap-2 px-4 py-2.5 text-sm font-semibold border-b-2 -mb-px transition-colors',
                tab === t.id
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700',
              )}>
              {t.icon}{t.label}
            </button>
          ))}
        </div>

        {/* ── TASKS TAB ─────────────────────────────────────────── */}
        {tab === 'tasks' && (
          <>
            {/* Filters */}
            <div className="flex items-center gap-2 flex-wrap">
              <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
                className="border border-slate-200 rounded-xl px-3 py-2 text-sm text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-300">
                <option value="">All Statuses</option>
                {choices.statuses.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
              <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}
                className="border border-slate-200 rounded-xl px-3 py-2 text-sm text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-blue-300">
                <option value="">All Priorities</option>
                {choices.priorities.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
              </select>
              {(statusFilter || priorityFilter) && (
                <button onClick={() => { setStatusFilter(''); setPriorityFilter(''); }}
                  className="text-xs text-slate-500 hover:text-slate-700 underline">
                  Clear
                </button>
              )}
              <span className="text-xs text-slate-400 ml-auto">{tasks.length} task{tasks.length !== 1 ? 's' : ''}</span>
            </div>

            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
              {loading ? (
                <div className="flex items-center justify-center py-20">
                  <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : tasks.length === 0 ? (
                <div className="text-center py-20 text-slate-400">
                  <SparklesIcon className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p className="font-medium">No tasks found</p>
                </div>
              ) : (
                <>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-100 bg-slate-50/60">
                          <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Room</th>
                          <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">Type</th>
                          <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Priority</th>
                          <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                          <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">Assigned To</th>
                          <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:table-cell">Scheduled</th>
                          <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-50">
                        {paginated.map((task) => (
                          <tr key={task.id} className="hover:bg-slate-50/50 transition-colors">
                            <td className="px-4 py-3">
                              <button onClick={() => setViewTask(task)}
                                className="font-bold text-slate-800 hover:text-blue-600 transition-colors">
                                {task.room_number || `#${task.room}`}
                              </button>
                            </td>
                            <td className="px-4 py-3 text-slate-600 hidden sm:table-cell">
                              {choiceLabel(choices.task_types, task.task_type)}
                            </td>
                            <td className="px-4 py-3">
                              <span className={clsx('text-xs font-semibold px-2.5 py-0.5 rounded-full', pColor(task.priority))}>
                                {choiceLabel(choices.priorities, task.priority)}
                              </span>
                            </td>
                            <td className="px-4 py-3">
                              <span className={clsx('text-xs font-semibold px-2.5 py-0.5 rounded-full', sColor(task.status))}>
                                {choiceLabel(choices.statuses, task.status)}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-slate-500 text-xs hidden md:table-cell">
                              {task.assigned_to_name || <span className="italic text-slate-400">Unassigned</span>}
                            </td>
                            <td className="px-4 py-3 text-xs text-slate-400 hidden lg:table-cell">{formatDate(task.scheduled_date)}</td>
                            <td className="px-4 py-3 text-right">
                              <div className="flex items-center justify-end gap-1">
                                {task.status === 'PENDING' && (
                                  <button onClick={() => handleStart(task)} title="Start"
                                    className="p-1.5 rounded-lg text-blue-500 hover:bg-blue-50 transition-colors">
                                    <PlayIcon className="w-4 h-4" />
                                  </button>
                                )}
                                {(task.status === 'PENDING' || task.status === 'IN_PROGRESS') && (
                                  <button onClick={() => handleComplete(task)} title="Complete"
                                    className="p-1.5 rounded-lg text-emerald-600 hover:bg-emerald-50 transition-colors">
                                    <CheckCircleIcon className="w-4 h-4" />
                                  </button>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="py-3 px-4 border-t border-slate-50">
                    <Pagination total={tasks.length} safePage={safePage} perPage={perPage}
                      totalPages={totalPages} onPageChange={setPage} onPerPageChange={setPerPage} />
                  </div>
                </>
              )}
            </div>
          </>
        )}

        {/* ── INVENTORY TAB ────────────────────────────────────── */}
        {tab === 'inventory' && (
          <>
            <div className="flex gap-1">
              {(['linens', 'amenities'] as const).map((t) => (
                <button key={t} onClick={() => setInventoryTab(t)}
                  className={clsx(
                    'px-4 py-1.5 rounded-lg text-sm font-semibold transition-colors',
                    inventoryTab === t ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200',
                  )}>
                  {t === 'linens' ? 'Linens' : 'Amenities'}
                </button>
              ))}
            </div>

            {invLoading ? (
              <div className="flex items-center justify-center py-20">
                <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : inventoryTab === 'linens' ? (
              <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-100 bg-slate-50/60">
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Linen Type</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Total</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">In Use</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">In Laundry</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">Damaged</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Reorder At</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Stock</th>
                      {canManage && <th className="px-4 py-3" />}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {linens.length === 0 ? (
                      <tr><td colSpan={canManage ? 8 : 7} className="py-10 text-center text-slate-400 text-sm">No linen inventory found</td></tr>
                    ) : linens.map((l) => {
                      const avail = l.quantity_total - l.quantity_in_use - l.quantity_in_laundry - l.quantity_damaged;
                      const low = avail <= l.reorder_level;
                      return (
                        <tr key={l.id} className="hover:bg-slate-50/50">
                          <td className="px-4 py-3 font-medium text-slate-800">{choiceLabel(choices.linen_types, l.linen_type)}</td>
                          <td className="px-4 py-3 text-right text-slate-700">{l.quantity_total}</td>
                          <td className="px-4 py-3 text-right text-slate-500 hidden sm:table-cell">{l.quantity_in_use}</td>
                          <td className="px-4 py-3 text-right text-slate-500 hidden sm:table-cell">{l.quantity_in_laundry}</td>
                          <td className="px-4 py-3 text-right text-red-500 hidden md:table-cell">{l.quantity_damaged}</td>
                          <td className="px-4 py-3 text-right text-slate-500">{l.reorder_level}</td>
                          <td className="px-4 py-3">
                            <span className={clsx(
                              'text-xs font-semibold px-2 py-0.5 rounded-full',
                              low ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700',
                            )}>
                              {low ? `Low (${avail})` : `OK (${avail})`}
                            </span>
                          </td>
                          {canManage && (
                            <td className="px-4 py-3">
                              <div className="flex items-center justify-end gap-1">
                                <button onClick={() => openLinenForm(l)} title="Edit"
                                  className="p-1.5 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-colors">
                                  <PencilSquareIcon className="w-4 h-4" />
                                </button>
                                <button onClick={() => handleDeleteLinen(l)} title="Delete"
                                  className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors">
                                  <TrashIcon className="w-4 h-4" />
                                </button>
                              </div>
                            </td>
                          )}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-100 bg-slate-50/60">
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Name</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">Code</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">Category</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Qty</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Reorder At</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:table-cell">Unit Cost</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Stock</th>
                      {canManage && <th className="px-4 py-3" />}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {amenities.length === 0 ? (
                      <tr><td colSpan={canManage ? 8 : 7} className="py-10 text-center text-slate-400 text-sm">No amenity inventory found</td></tr>
                    ) : amenities.map((a) => {
                      const low = a.quantity <= a.reorder_level;
                      return (
                        <tr key={a.id} className="hover:bg-slate-50/50">
                          <td className="px-4 py-3 font-medium text-slate-800">{a.name}</td>
                          <td className="px-4 py-3 text-slate-500 hidden sm:table-cell font-mono text-xs">{a.code}</td>
                          <td className="px-4 py-3 text-slate-500 hidden md:table-cell">{a.category || '—'}</td>
                          <td className="px-4 py-3 text-right font-bold text-slate-700">{a.quantity}</td>
                          <td className="px-4 py-3 text-right text-slate-500">{a.reorder_level}</td>
                          <td className="px-4 py-3 text-right text-slate-500 hidden lg:table-cell">${Number(a.unit_cost).toFixed(2)}</td>
                          <td className="px-4 py-3">
                            <span className={clsx(
                              'text-xs font-semibold px-2 py-0.5 rounded-full',
                              low ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700',
                            )}>
                              {low ? 'Low' : 'OK'}
                            </span>
                          </td>
                          {canManage && (
                            <td className="px-4 py-3">
                              <div className="flex items-center justify-end gap-1">
                                <button onClick={() => openAmenityForm(a)} title="Edit"
                                  className="p-1.5 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-colors">
                                  <PencilSquareIcon className="w-4 h-4" />
                                </button>
                                <button onClick={() => handleDeleteAmenity(a)} title="Delete"
                                  className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors">
                                  <TrashIcon className="w-4 h-4" />
                                </button>
                              </div>
                            </td>
                          )}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}

        {/* ── MOVEMENTS TAB ─────────────────────────────────────── */}
        {tab === 'movements' && (() => {
          const movTotalPages = Math.max(1, Math.ceil(filteredMovements.length / movPerPage));
          const movSafePage = Math.min(movPage, movTotalPages);
          const pagedMovements = filteredMovements.slice((movSafePage - 1) * movPerPage, movSafePage * movPerPage);
          const PRESETS = [
            { key: 'all',   label: 'All' },
            { key: 'today', label: 'Today' },
            { key: 'week',  label: 'This Week' },
            { key: 'month', label: 'This Month' },
            { key: 'year',  label: 'This Year' },
            { key: 'custom',label: 'Custom' },
          ] as const;
          return (
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
            {/* Date filter bar */}
            <div className="px-4 py-3 border-b border-slate-100 space-y-3">
              <div className="flex flex-wrap gap-1.5">
                {PRESETS.map((p) => (
                  <button key={p.key} onClick={() => setMovDatePreset(p.key)}
                    className={clsx(
                      'px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors',
                      movDatePreset === p.key
                        ? 'bg-indigo-600 text-white border-indigo-600'
                        : 'border-slate-200 text-slate-600 hover:bg-slate-50',
                    )}>
                    {p.label}
                  </button>
                ))}
              </div>
              {movDatePreset === 'custom' && (
                <div className="flex items-center gap-2 flex-wrap">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs text-slate-500">From</span>
                    <input type="date" value={movDateFrom}
                      onChange={(e) => setMovDateFrom(e.target.value)}
                      className="px-2 py-1.5 rounded-lg border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-300" />
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs text-slate-500">To</span>
                    <input type="date" value={movDateTo}
                      onChange={(e) => setMovDateTo(e.target.value)}
                      className="px-2 py-1.5 rounded-lg border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-300" />
                  </div>
                  {(movDateFrom || movDateTo) && (
                    <button onClick={() => { setMovDateFrom(''); setMovDateTo(''); }}
                      className="text-xs text-slate-400 hover:text-slate-600 underline">
                      Clear
                    </button>
                  )}
                </div>
              )}
            </div>
            {/* Export toolbar */}
            <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-100 bg-slate-50/40">
              <span className="text-xs text-slate-500">
                {filteredMovements.length} movement{filteredMovements.length !== 1 ? 's' : ''}
                {movDatePreset !== 'all' && ` (filtered from ${movements.length} total)`}
              </span>
              <div className="flex items-center gap-2">
                <button onClick={exportCSV} disabled={filteredMovements.length === 0}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-white disabled:opacity-40 transition-colors">
                  <ArrowDownTrayIcon className="w-3.5 h-3.5" />
                  CSV
                </button>
                <button onClick={exportPDF} disabled={filteredMovements.length === 0}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-white disabled:opacity-40 transition-colors">
                  <ArrowDownTrayIcon className="w-3.5 h-3.5" />
                  PDF
                </button>
              </div>
            </div>
            {movLoading ? (
              <div className="flex items-center justify-center py-20">
                <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : movements.length === 0 ? (
              <div className="text-center py-20 text-slate-400">
                <ArrowsRightLeftIcon className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="font-medium">No stock movements yet</p>
                <p className="text-sm mt-1">Use &quot;Log Movement&quot; to record stock changes</p>
              </div>
            ) : filteredMovements.length === 0 ? (
              <div className="text-center py-16 text-slate-400">
                <FunnelIcon className="w-10 h-10 mx-auto mb-3 opacity-30" />
                <p className="font-medium">No movements in this date range</p>
                <button onClick={() => setMovDatePreset('all')}
                  className="mt-2 text-sm text-indigo-600 hover:underline">Clear filter</button>
              </div>
            ) : (
              <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-100 bg-slate-50/60">
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Type</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">Item</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Qty</th>
                      <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">Balance After</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:table-cell">Reason</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">By</th>
                      <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider hidden lg:table-cell">Date</th>
                      {canManage && <th className="px-4 py-3" />}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {pagedMovements.map((m) => (
                      <tr key={m.id} className="hover:bg-slate-50/50">
                        <td className="px-4 py-3">
                          <span className={clsx('text-xs font-semibold px-2 py-0.5 rounded-full', mColor(m.movement_type))}>
                            {choiceLabel(choices.movement_types, m.movement_type)}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-slate-600 hidden sm:table-cell text-xs">
                          {m.amenity_name
                            ?? (m.linen_type_display ? choiceLabel(choices.linen_types, m.linen_type_display) : null)
                            ?? (m.amenity_inventory ? amenities.find((a) => a.id === m.amenity_inventory)?.name : null)
                            ?? (m.linen_inventory ? choiceLabel(choices.linen_types, linens.find((l) => l.id === m.linen_inventory)?.linen_type ?? '') : null)
                            ?? '—'}
                        </td>
                        <td className="px-4 py-3 text-right font-bold">
                          <span className={m.quantity >= 0 ? 'text-emerald-600' : 'text-red-500'}>
                            {m.quantity >= 0 ? `+${m.quantity}` : m.quantity}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right text-slate-500 hidden md:table-cell">{m.balance_after}</td>
                        <td className="px-4 py-3 text-slate-500 text-xs hidden lg:table-cell max-w-xs truncate">{m.reason || '—'}</td>
                        <td className="px-4 py-3 text-slate-500 text-xs hidden md:table-cell">{m.created_by_name || '—'}</td>
                        <td className="px-4 py-3 text-slate-400 text-xs hidden lg:table-cell">{formatDateTime(m.created_at)}</td>
                        {canManage && (
                          <td className="px-4 py-3">
                            <button onClick={() => handleDeleteMovement(m.id)} title="Delete"
                              className="p-1.5 rounded-lg text-slate-300 hover:text-red-600 hover:bg-red-50 transition-colors">
                              <TrashIcon className="w-4 h-4" />
                            </button>
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {/* Pagination */}
              <div className="px-4 py-3 border-t border-slate-100">
                <Pagination
                  total={filteredMovements.length}
                  safePage={movSafePage}
                  perPage={movPerPage}
                  totalPages={movTotalPages}
                  onPageChange={setMovPage}
                  onPerPageChange={(n: number) => { setMovPerPage(n); setMovPage(1); }}
                />
              </div>
              </>
            )}
          </div>
          );
        })()}

      </div>

        {/* ── Add/Edit Linen Slide-over ─────────────────────────── */}
        {showLinenForm && canManage && (
          <div className="fixed inset-0 z-50 flex">
            <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={() => setShowLinenForm(false)} />
            <aside className="w-full max-w-md bg-white shadow-2xl flex flex-col overflow-hidden h-screen">
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-green-700 flex items-center justify-center">
                    <ArchiveBoxIcon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="font-semibold text-gray-900">{editLinen ? 'Edit Linen' : 'Add Linen'}</h2>
                    <p className="text-xs text-gray-500">Manage linen inventory</p>
                  </div>
                </div>
                <button onClick={() => setShowLinenForm(false)} className="p-2 rounded-full hover:bg-gray-200 transition-colors">
                  <XMarkIcon className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              <form onSubmit={handleSaveLinen} className="flex-1 overflow-y-auto p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Linen Type *</label>
                  <select required value={linenForm.linen_type}
                    onChange={(e) => setLinenForm((p) => ({ ...p, linen_type: e.target.value }))}
                    disabled={!!editLinen}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:bg-gray-50 disabled:text-gray-500">
                    {editLinen
                      ? choices.linen_types.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)
                      : choices.linen_types
                          .filter((t) => !linens.some((ln) => ln.linen_type === t.value))
                          .map((t) => <option key={t.value} value={t.value}>{t.label}</option>)
                    }
                  </select>
                  {editLinen && <p className="text-xs text-gray-400 mt-1">Linen type cannot be changed after creation</p>}
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Total Quantity *</label>
                    <input type="number" required min="0" value={linenForm.quantity_total}
                      onChange={(e) => setLinenForm((p) => ({ ...p, quantity_total: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Reorder Level *</label>
                    <input type="number" required min="0" value={linenForm.reorder_level}
                      onChange={(e) => setLinenForm((p) => ({ ...p, reorder_level: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">In Use</label>
                    <input type="number" min="0" value={linenForm.quantity_in_use}
                      onChange={(e) => setLinenForm((p) => ({ ...p, quantity_in_use: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">In Laundry</label>
                    <input type="number" min="0" value={linenForm.quantity_in_laundry}
                      onChange={(e) => setLinenForm((p) => ({ ...p, quantity_in_laundry: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Damaged</label>
                    <input type="number" min="0" value={linenForm.quantity_damaged}
                      onChange={(e) => setLinenForm((p) => ({ ...p, quantity_damaged: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                  </div>
                </div>
                <div className="flex gap-2 pt-1">
                  <button type="submit" disabled={saving}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-semibold py-2.5 rounded-lg transition-colors">
                    {saving ? 'Saving…' : editLinen ? 'Save Changes' : 'Add Linen'}
                  </button>
                  <button type="button" onClick={() => setShowLinenForm(false)}
                    className="px-4 py-2.5 rounded-lg border border-gray-200 text-sm font-semibold text-gray-600 hover:bg-gray-50">
                    Cancel
                  </button>
                </div>
              </form>
            </aside>
          </div>
        )}

        {/* ── Add/Edit Amenity Slide-over ───────────────────────── */}
        {showAmenityForm && canManage && (
          <div className="fixed inset-0 z-50 flex">
            <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={() => setShowAmenityForm(false)} />
            <aside className="w-full max-w-md bg-white shadow-2xl flex flex-col overflow-hidden h-screen">
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-700 flex items-center justify-center">
                    <SparklesIcon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="font-semibold text-gray-900">{editAmenity ? 'Edit Amenity' : 'Add Amenity'}</h2>
                    <p className="text-xs text-gray-500">Manage amenity inventory</p>
                  </div>
                </div>
                <button onClick={() => setShowAmenityForm(false)} className="p-2 rounded-full hover:bg-gray-200 transition-colors">
                  <XMarkIcon className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              <form onSubmit={handleSaveAmenity} className="flex-1 overflow-y-auto p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                  <input type="text" required value={amenityForm.name}
                    onChange={(e) => setAmenityForm((p) => ({ ...p, name: e.target.value }))}
                    placeholder="e.g. Shampoo (30ml)"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Code *</label>
                    <input type="text" required value={amenityForm.code}
                      onChange={(e) => setAmenityForm((p) => ({ ...p, code: e.target.value.toUpperCase() }))}
                      placeholder="e.g. SHAM-30"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-400" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                    <select value={amenityForm.category}
                      onChange={(e) => setAmenityForm((p) => ({ ...p, category: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
                      <option value="">— select —</option>
                      {AMENITY_CATEGORIES.map((c) => (
                        <option key={c} value={c}>{c}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Quantity *</label>
                    <input type="number" required min="0" value={amenityForm.quantity}
                      onChange={(e) => setAmenityForm((p) => ({ ...p, quantity: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Reorder At *</label>
                    <input type="number" required min="0" value={amenityForm.reorder_level}
                      onChange={(e) => setAmenityForm((p) => ({ ...p, reorder_level: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Unit Cost ($)</label>
                    <input type="number" min="0" step="0.01" value={amenityForm.unit_cost}
                      onChange={(e) => setAmenityForm((p) => ({ ...p, unit_cost: e.target.value }))}
                      placeholder="0.00"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                  </div>
                </div>
                <div className="flex gap-2 pt-1">
                  <button type="submit" disabled={saving}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-semibold py-2.5 rounded-lg transition-colors">
                    {saving ? 'Saving…' : editAmenity ? 'Save Changes' : 'Add Amenity'}
                  </button>
                  <button type="button" onClick={() => setShowAmenityForm(false)}
                    className="px-4 py-2.5 rounded-lg border border-gray-200 text-sm font-semibold text-gray-600 hover:bg-gray-50">
                    Cancel
                  </button>
                </div>
              </form>
            </aside>
          </div>
        )}

        {/* ── Create Task Slide-over ─────────────────────────────── */}
        {showTaskForm && canManage && (
          <div className="fixed inset-0 z-50 flex">
            <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={() => setShowTaskForm(false)} />
            <aside className="w-full max-w-md bg-white shadow-2xl flex flex-col overflow-hidden h-screen">
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-500 to-teal-700 flex items-center justify-center">
                    <ClipboardDocumentListIcon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="font-semibold text-gray-900">New Housekeeping Task</h2>
                    <p className="text-xs text-gray-500">Fill in the details below</p>
                  </div>
                </div>
                <button onClick={() => setShowTaskForm(false)} className="p-2 rounded-full hover:bg-gray-200 transition-colors">
                  <XMarkIcon className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              <form onSubmit={handleCreateTask} className="flex-1 overflow-y-auto p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Room *</label>
                  <select required value={taskForm.room} onChange={(e) => setTaskForm((p) => ({ ...p, room: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
                    <option value="">— Select room —</option>
                    {rooms.map((r) => <option key={r.id} value={r.id}>{r.room_number}</option>)}
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Task Type</label>
                    <select value={taskForm.task_type} onChange={(e) => setTaskForm((p) => ({ ...p, task_type: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
                      {choices.task_types.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                    <select value={taskForm.priority} onChange={(e) => setTaskForm((p) => ({ ...p, priority: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
                      {choices.priorities.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Assign To</label>
                  <select value={taskForm.assigned_to} onChange={(e) => setTaskForm((p) => ({ ...p, assigned_to: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
                    <option value="">— Unassigned —</option>
                    {staff.map((s) => <option key={s.id} value={s.id}>{s.first_name} {s.last_name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Scheduled Date</label>
                  <input type="date" required value={taskForm.scheduled_date}
                    onChange={(e) => setTaskForm((p) => ({ ...p, scheduled_date: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                  <textarea rows={2} value={taskForm.notes} onChange={(e) => setTaskForm((p) => ({ ...p, notes: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Special Instructions</label>
                  <textarea rows={2} value={taskForm.special_instructions} onChange={(e) => setTaskForm((p) => ({ ...p, special_instructions: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none" />
                </div>
                <div className="flex gap-2 pt-1">
                  <button type="submit" disabled={saving}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-semibold py-2.5 rounded-lg transition-colors">
                    {saving ? 'Creating…' : 'Create Task'}
                  </button>
                  <button type="button" onClick={() => setShowTaskForm(false)}
                    className="px-4 py-2.5 rounded-lg border border-gray-200 text-sm font-semibold text-gray-600 hover:bg-gray-50">
                    Cancel
                  </button>
                </div>
              </form>
            </aside>
          </div>
        )}

        {/* ── Log Movement Slide-over ────────────────────────────── */}
        {showMoveForm && (
          <div className="fixed inset-0 z-50 flex">
            <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={() => setShowMoveForm(false)} />
            <aside className="w-full max-w-md bg-white shadow-2xl flex flex-col overflow-hidden h-screen">
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center">
                    <ArrowsRightLeftIcon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="font-semibold text-gray-900">Log Stock Movement</h2>
                    <p className="text-xs text-gray-500">Record inventory changes</p>
                  </div>
                </div>
                <button onClick={() => setShowMoveForm(false)} className="p-2 rounded-full hover:bg-gray-200 transition-colors">
                  <XMarkIcon className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              <form onSubmit={handleLogMovement} className="flex-1 overflow-y-auto p-6 space-y-4">
                {/* Movement type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Movement Type *</label>
                  <div className="grid grid-cols-3 gap-2">
                    {choices.movement_types.map((mt) => (
                      <button key={mt.value} type="button"
                        onClick={() => setMoveForm((p) => ({ ...p, movement_type: mt.value }))}
                        className={clsx(
                          'py-2 rounded-lg text-xs font-semibold border transition-colors',
                          moveForm.movement_type === mt.value
                            ? `${mColor(mt.value)} border-current`
                            : 'border-gray-200 text-gray-600 hover:bg-gray-50',
                        )}>
                        {mt.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Item type toggle */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Item Category *</label>
                  <div className="flex rounded-lg border border-gray-200 overflow-hidden">
                    <button type="button" onClick={() => setMoveForm((p) => ({ ...p, item_type: 'amenity', linen_inventory: '' }))}
                      className={clsx('flex-1 py-2 text-sm font-semibold transition-colors',
                        moveForm.item_type === 'amenity' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50')}>
                      Amenity
                    </button>
                    <button type="button" onClick={() => setMoveForm((p) => ({ ...p, item_type: 'linen', amenity_inventory: '' }))}
                      className={clsx('flex-1 py-2 text-sm font-semibold transition-colors',
                        moveForm.item_type === 'linen' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50')}>
                      Linen
                    </button>
                  </div>
                </div>

                {/* Item selector */}
                {moveForm.item_type === 'amenity' ? (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Amenity *</label>
                    <select required value={moveForm.amenity_inventory}
                      onChange={(e) => setMoveForm((p) => ({ ...p, amenity_inventory: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
                      <option value="">— Select amenity —</option>
                      {amenities.map((a) => <option key={a.id} value={a.id}>{a.name} (stock: {a.quantity})</option>)}
                    </select>
                  </div>
                ) : (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Linen *</label>
                    <select required value={moveForm.linen_inventory}
                      onChange={(e) => setMoveForm((p) => ({ ...p, linen_inventory: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
                      <option value="">— Select linen —</option>
                      {linens.map((l) => (
                        <option key={l.id} value={l.id}>
                          {choiceLabel(choices.linen_types, l.linen_type)} (stock: {l.quantity_total})
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Quantity *</label>
                  <input type="number" required min="1" value={moveForm.quantity}
                    onChange={(e) => setMoveForm((p) => ({ ...p, quantity: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                </div>

                {moveForm.movement_type === 'TRANSFER' && (
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">From Location *</label>
                      <input type="text" value={moveForm.from_location}
                        onChange={(e) => setMoveForm((p) => ({ ...p, from_location: e.target.value }))}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">To Location *</label>
                      <input type="text" value={moveForm.to_location}
                        onChange={(e) => setMoveForm((p) => ({ ...p, to_location: e.target.value }))}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                    </div>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Reason</label>
                  <input type="text" value={moveForm.reason}
                    onChange={(e) => setMoveForm((p) => ({ ...p, reason: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                  <textarea rows={2} value={moveForm.notes}
                    onChange={(e) => setMoveForm((p) => ({ ...p, notes: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none" />
                </div>

                <div className="flex gap-2 pt-1">
                  <button type="submit" disabled={saving}
                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white text-sm font-semibold py-2.5 rounded-lg transition-colors">
                    {saving ? 'Logging…' : 'Log Movement'}
                  </button>
                  <button type="button" onClick={() => setShowMoveForm(false)}
                    className="px-4 py-2.5 rounded-lg border border-gray-200 text-sm font-semibold text-gray-600 hover:bg-gray-50">
                    Cancel
                  </button>
                </div>
              </form>
            </aside>
          </div>
        )}

        {/* ── Task Detail Slide-over ─────────────────────────────── */}
        {viewTask && (
          <div className="fixed inset-0 z-50 flex">
            <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={() => setViewTask(null)} />
            <aside className="w-full max-w-md bg-white shadow-2xl flex flex-col overflow-hidden h-screen">
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-500 to-teal-700 flex items-center justify-center">
                    <ClipboardDocumentListIcon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="font-semibold text-gray-900">Task #{viewTask.id}</h2>
                    <p className="text-xs text-gray-500">{viewTask.room_number || `Room #${viewTask.room}`}</p>
                  </div>
                </div>
                <button onClick={() => setViewTask(null)} className="p-2 rounded-full hover:bg-gray-200 transition-colors">
                  <XMarkIcon className="w-5 h-5 text-gray-500" />
                </button>
              </div>
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                <div className="flex items-center gap-3">
                  <span className={clsx('text-xs font-semibold px-2.5 py-1 rounded-full', sColor(viewTask.status))}>
                    {choiceLabel(choices.statuses, viewTask.status)}
                  </span>
                  <span className={clsx('text-xs font-semibold px-2.5 py-1 rounded-full', pColor(viewTask.priority))}>
                    {choiceLabel(choices.priorities, viewTask.priority)}
                  </span>
                </div>
                <dl className="space-y-3">
                  {([
                    ['Room',      viewTask.room_number || `#${viewTask.room}`],
                    ['Task Type', choiceLabel(choices.task_types, viewTask.task_type)],
                    ['Assigned',  viewTask.assigned_to_name || 'Unassigned'],
                    ['Scheduled', formatDate(viewTask.scheduled_date)],
                    ['Started',   formatDateTime(viewTask.started_at)],
                    ['Completed', formatDateTime(viewTask.completed_at)],
                    ['Created By',viewTask.created_by_name || '—'],
                  ] as [string, string][]).map(([label, val]) => (
                    <div key={label} className="flex gap-3 border-b border-gray-50 pb-3 last:border-0">
                      <dt className="text-xs font-semibold text-gray-500 w-24 flex-shrink-0 mt-0.5">{label}</dt>
                      <dd className="text-sm text-gray-800">{val}</dd>
                    </div>
                  ))}
                  {viewTask.notes && <div className="flex gap-3"><dt className="text-xs font-semibold text-gray-500 w-24 flex-shrink-0 mt-0.5">Notes</dt><dd className="text-sm text-gray-800">{viewTask.notes}</dd></div>}
                  {viewTask.special_instructions && <div className="flex gap-3"><dt className="text-xs font-semibold text-gray-500 w-24 flex-shrink-0 mt-0.5">Instructions</dt><dd className="text-sm text-gray-800">{viewTask.special_instructions}</dd></div>}
                </dl>
                <div className="flex gap-2 pt-2">
                  {viewTask.status === 'PENDING' && (
                    <button onClick={() => handleStart(viewTask)}
                      className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold py-2.5 rounded-lg">
                      <PlayIcon className="w-4 h-4" /> Start Task
                    </button>
                  )}
                  {(viewTask.status === 'PENDING' || viewTask.status === 'IN_PROGRESS') && (
                    <button onClick={() => handleComplete(viewTask)}
                      className="flex-1 flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold py-2.5 rounded-lg">
                      <CheckCircleIcon className="w-4 h-4" /> Complete
                    </button>
                  )}
                </div>
              </div>
            </aside>
          </div>
        )}
    </Layout>
  );
}

