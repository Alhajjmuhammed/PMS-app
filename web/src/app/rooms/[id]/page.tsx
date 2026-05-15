'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { roomService, roomTypeService, floorService } from '@/lib/services';

const STATUS_OPTIONS = [
  { value: 'VC', label: 'Vacant Clean' },
  { value: 'VD', label: 'Vacant Dirty' },
  { value: 'OC', label: 'Occupied Clean' },
  { value: 'OD', label: 'Occupied Dirty' },
  { value: 'OOO', label: 'Out of Order' },
  { value: 'OOS', label: 'Out of Service' },
];

const STATUS_COLORS: Record<string, string> = {
  VC: 'bg-green-100 text-green-800',
  VD: 'bg-yellow-100 text-yellow-800',
  OC: 'bg-blue-100 text-blue-800',
  OD: 'bg-orange-100 text-orange-800',
  OOO: 'bg-red-100 text-red-800',
  OOS: 'bg-gray-100 text-gray-800',
};

export default function RoomDetailPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [room, setRoom] = useState<any>(null);
  const [roomTypes, setRoomTypes] = useState<any[]>([]);
  const [floors, setFloors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [statusUpdating, setStatusUpdating] = useState(false);
  const [formData, setFormData] = useState<any>({});
  const [pageError, setPageError] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  useEffect(() => {
    if (params.id) {
      Promise.all([loadRoom(), loadRoomTypes(), loadFloors()]);
    }
  }, [params.id]);

  useEffect(() => {
    if (searchParams.get('edit') === '1') {
      setEditing(true);
    }
  }, [searchParams]);

  const loadRoom = async () => {
    try {
      const data = await roomService.getById(parseInt(params.id as string));
      setRoom(data);
      setFormData({
        room_number: data.room_number,
        room_type: data.room_type || '',
        floor: data.floor || '',
        status: data.status,
        notes: data.notes || '',
      });
    } catch {
      setPageError('Failed to load room details. Please refresh.');
    } finally {
      setLoading(false);
    }
  };

  const loadRoomTypes = async () => {
    try {
      const data = await roomTypeService.getAll();
      setRoomTypes(data.results || data);
    } catch {
      // non-critical
    }
  };

  const loadFloors = async () => {
    try {
      const data = await floorService.getAll();
      setFloors(data.results || data);
    } catch {
      // non-critical
    }
  };

  const handleSave = async () => {
    if (!formData.room_number.trim()) {
      setSaveError('Room number is required');
      return;
    }
    try {
      setSaving(true);
      const payload: any = {
        room_number: formData.room_number,
        status: formData.status,
        notes: formData.notes,
      };
      if (formData.room_type) {
        payload.room_type = parseInt(formData.room_type);
      }
      if (formData.floor) {
        payload.floor = parseInt(formData.floor);
      } else {
        payload.floor = null;
      }
      const updated = await roomService.update(parseInt(params.id as string), payload);
      setRoom(updated);
      setEditing(false);
    } catch (error: any) {
      setSaveError(error?.response?.data ? JSON.stringify(error.response.data) : 'Failed to save changes');
    } finally {
      setSaving(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (statusUpdating || room.status === newStatus) return;
    try {
      setStatusUpdating(true);
      await roomService.updateStatus(parseInt(params.id as string), newStatus);
      setRoom({ ...room, status: newStatus });
    } catch (error: any) {
      setSaveError(error?.response?.data ? JSON.stringify(error.response.data) : 'Failed to update status');
    } finally {
      setStatusUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Delete Room ${room?.room_number}? This action cannot be undone.`)) return;
    try {
      setDeleting(true);
      await roomService.delete(parseInt(params.id as string));
      router.push('/rooms');
    } catch {
      setSaveError('Failed to delete room. Please try again.');
      setDeleting(false);
    }
  };

  const cancelEdit = () => {
    setEditing(false);
    setFormData({
      room_number: room.room_number,
      room_type: room.room_type || '',
      floor: room.floor || '',
      status: room.status,
      notes: room.notes || '',
    });
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center py-12">
          <svg className="animate-spin h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        </div>
      </Layout>
    );
  }

  if (!room) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">Room not found.</p>
          <Button onClick={() => router.push('/rooms')}>Back to Rooms</Button>
        </div>
      </Layout>
    );
  }

  const statusInfo = STATUS_OPTIONS.find((s) => s.value === room.status);

  return (
    <Layout>
      <div className="space-y-6">
        {pageError && (
          <div className="px-4 py-3 rounded-lg bg-red-50 text-red-800 border border-red-200 text-sm font-medium">{pageError}</div>
        )}
        {saveError && (
          <div className="px-4 py-3 rounded-lg bg-red-50 text-red-800 border border-red-200 text-sm font-medium">{saveError}</div>
        )}

        {/* ── Header ── */}
        <div className="flex justify-between items-center">
          <div>
            <button
              onClick={() => router.push('/rooms')}
              className="text-sm text-gray-500 hover:text-gray-700 mb-1 flex items-center gap-1"
            >
              ← Back to Rooms
            </button>
            <h1 className="text-3xl font-bold text-gray-900">Room {room.room_number}</h1>
          </div>

          <div className="flex gap-2">
            {!editing ? (
              <>
                <Button variant="secondary" onClick={() => setEditing(true)}>
                  Edit
                </Button>
                <Button variant="danger" onClick={handleDelete} isLoading={deleting}>
                  Delete
                </Button>
              </>
            ) : (
              <>
                <Button variant="secondary" onClick={cancelEdit}>
                  Cancel
                </Button>
                <Button onClick={handleSave} isLoading={saving}>
                  Save Changes
                </Button>
              </>
            )}
          </div>
        </div>

        {/* ── Quick Status Switcher (view mode only) ── */}
        {!editing && (
          <Card title="Quick Status Update">
            <div className="flex gap-2 flex-wrap">
              {STATUS_OPTIONS.map((s) => (
                <button
                  key={s.value}
                  onClick={() => handleStatusChange(s.value)}
                  disabled={statusUpdating}
                  className={`px-4 py-2 text-sm font-medium rounded-full border-2 transition-all disabled:opacity-50 ${
                    room.status === s.value
                      ? `${STATUS_COLORS[s.value]} border-current font-bold`
                      : 'border-transparent bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <span className="font-bold">{s.value}</span>
                  <span className="hidden sm:inline"> — {s.label}</span>
                </button>
              ))}
            </div>
          </Card>
        )}

        {/* ── View / Edit Content ── */}
        {!editing ? (

          /* ── VIEW MODE ── */
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card title="Room Information">
              <dl className="space-y-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Room Number</dt>
                  <dd className="mt-1 text-2xl font-bold text-gray-900">{room.room_number}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Room Type</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {room.room_type_detail?.name || room.room_type_name || 'N/A'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Floor</dt>
                  <dd className="mt-1 text-sm text-gray-900">{room.floor_name || 'N/A'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Building</dt>
                  <dd className="mt-1 text-sm text-gray-900">{room.building_name || 'N/A'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Status</dt>
                  <dd className="mt-1">
                    <span className={`px-3 py-1 text-xs font-bold rounded-full ${STATUS_COLORS[room.status] || 'bg-gray-100 text-gray-800'}`}>
                      {statusInfo?.label || room.status}
                    </span>
                  </dd>
                </div>
                {room.notes && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Notes</dt>
                    <dd className="mt-1 text-sm text-gray-900">{room.notes}</dd>
                  </div>
                )}
              </dl>
            </Card>

            <Card title="Pricing & Capacity">
              <dl className="space-y-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Base Rate</dt>
                  <dd className="mt-1 text-2xl font-bold text-primary-600">
                    {room.room_type_detail?.base_rate != null
                      ? `$${Number(room.room_type_detail.base_rate).toLocaleString()}`
                      : '—'}
                    <span className="text-sm text-gray-500 font-normal"> / night</span>
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Max Occupancy</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {room.room_type_detail?.max_occupancy
                      ? `${room.room_type_detail.max_occupancy} guests`
                      : 'N/A'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Bed Type</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {room.room_type_detail?.bed_type || 'N/A'}
                  </dd>
                </div>
              </dl>
            </Card>
          </div>

        ) : (

          /* ── EDIT MODE ── */
          <Card title="Edit Room">
            <div className="space-y-4 max-w-lg">

              <Input
                label="Room Number *"
                value={formData.room_number}
                onChange={(e) => setFormData({ ...formData, room_number: e.target.value })}
                required
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Room Type</label>
                <select
                  value={formData.room_type}
                  onChange={(e) => setFormData({ ...formData, room_type: e.target.value })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
                >
                  <option value="">— No type assigned —</option>
                  {roomTypes.map((rt) => (
                    <option key={rt.id} value={rt.id}>
                      {rt.name} — ${rt.base_rate}/night · {rt.max_occupancy} guests
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Floor <span className="text-gray-400 text-xs">(optional)</span>
                </label>
                <select
                  value={formData.floor}
                  onChange={(e) => setFormData({ ...formData, floor: e.target.value })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
                >
                  <option value="">— No floor assigned —</option>
                  {floors.map((f) => (
                    <option key={f.id} value={f.id}>
                      Floor {f.number}{f.name ? ` — ${f.name}` : ''}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
                >
                  {STATUS_OPTIONS.map((s) => (
                    <option key={s.value} value={s.value}>
                      {s.value} — {s.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  rows={3}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
                  placeholder="Optional notes about this room..."
                />
              </div>

              <div className="flex gap-3 pt-2">
                <Button type="button" variant="secondary" onClick={cancelEdit} fullWidth>
                  Cancel
                </Button>
                <Button onClick={handleSave} isLoading={saving} fullWidth>
                  Save Changes
                </Button>
              </div>
            </div>
          </Card>
        )}
      </div>
    </Layout>
  );
}
