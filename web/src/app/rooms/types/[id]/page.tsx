'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { roomTypeService } from '@/lib/services';

const BED_TYPES = ['single', 'double', 'queen', 'king', 'twin', 'suite'];

export default function RoomTypeDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [roomType, setRoomType] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [formData, setFormData] = useState<any>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (params.id) loadRoomType();
  }, [params.id]);

  const loadRoomType = async () => {
    try {
      const data = await roomTypeService.getById(parseInt(params.id as string));
      setRoomType(data);
      setFormData({
        name: data.name,
        code: data.code,
        description: data.description || '',
        base_rate: data.base_rate,
        max_occupancy: data.max_occupancy,
        bed_type: data.bed_type || 'double',
        is_active: data.is_active ?? true,
      });
    } catch {
      setError('Failed to load room type. Please refresh.');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const updated = await roomTypeService.update(parseInt(params.id as string), {
        ...formData,
        base_rate: parseFloat(formData.base_rate),
        max_occupancy: parseInt(formData.max_occupancy),
      });
      setRoomType(updated);
      setEditing(false);
    } catch (error: any) {
      setError(error?.response?.data ? JSON.stringify(error.response.data) : 'Failed to save changes');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Delete room type "${roomType?.name}"? Rooms using this type will be affected.`)) return;
    try {
      setDeleting(true);
      await roomTypeService.delete(parseInt(params.id as string));
      router.push('/rooms/types');
    } catch {
      setError('Failed to delete room type. Please try again.');
      setDeleting(false);
    }
  };

  const cancelEdit = () => {
    setEditing(false);
    setFormData({
      name: roomType.name,
      code: roomType.code,
      description: roomType.description || '',
      base_rate: roomType.base_rate,
      max_occupancy: roomType.max_occupancy,
      bed_type: roomType.bed_type || 'double',
      is_active: roomType.is_active ?? true,
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

  return (
    <Layout>
      <div className="max-w-2xl mx-auto space-y-6">
        {error && (
          <div className="px-4 py-3 rounded-lg bg-red-50 text-red-800 border border-red-200 text-sm font-medium">{error}</div>
        )}
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{roomType?.name}</h1>
            <p className="text-sm text-gray-500 mt-1">Room Type #{roomType?.id}</p>
          </div>
          <div className="flex gap-2">
            {!editing ? (
              <>
                <Button variant="secondary" onClick={() => router.back()}>Back</Button>
                <Button variant="secondary" onClick={() => setEditing(true)}>Edit</Button>
                <Button variant="danger" onClick={handleDelete} isLoading={deleting}>Delete</Button>
              </>
            ) : (
              <>
                <Button variant="secondary" onClick={cancelEdit}>Cancel</Button>
                <Button onClick={handleSave} isLoading={saving}>Save Changes</Button>
              </>
            )}
          </div>
        </div>

        {!editing ? (
          /* ── View Mode ── */
          <div className="space-y-6">
            <Card title="Room Type Details">
              <dl className="grid grid-cols-2 gap-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Name</dt>
                  <dd className="mt-1 text-lg font-semibold text-gray-900">{roomType?.name}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Status</dt>
                  <dd className="mt-1">
                    <span className={`px-3 py-1 text-sm font-semibold rounded-full ${roomType?.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                      {roomType?.is_active ? 'ACTIVE' : 'INACTIVE'}
                    </span>
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Base Rate</dt>
                  <dd className="mt-1 text-2xl font-bold text-primary-600">
                    ${roomType?.base_rate?.toLocaleString()}
                    <span className="text-sm text-gray-500 font-normal"> / night</span>
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Max Occupancy</dt>
                  <dd className="mt-1 text-lg font-semibold text-gray-900">{roomType?.max_occupancy} guests</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Bed Type</dt>
                  <dd className="mt-1 text-sm text-gray-900 capitalize">{roomType?.bed_type}</dd>
                </div>
              </dl>
              {roomType?.description && (
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <dt className="text-sm font-medium text-gray-500">Description</dt>
                  <dd className="mt-1 text-sm text-gray-700">{roomType.description}</dd>
                </div>
              )}
            </Card>

            {roomType?.amenities?.length > 0 && (
              <Card title="Amenities">
                <div className="flex flex-wrap gap-2">
                  {roomType.amenities.map((amenity: string, idx: number) => (
                    <span key={idx} className="px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-sm font-medium">
                      {amenity}
                    </span>
                  ))}
                </div>
              </Card>
            )}
          </div>
        ) : (
          /* ── Edit Mode ── */
          <Card title="Edit Room Type">
            <div className="space-y-4">
              <Input
                label="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />

              <Input
                label="Code"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                helperText="Short unique identifier (max 20 chars)"
                maxLength={20}
                required
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Base Rate (per night)"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.base_rate}
                  onChange={(e) => setFormData({ ...formData, base_rate: e.target.value })}
                  required
                />
                <Input
                  label="Max Occupancy"
                  type="number"
                  min="1"
                  max="20"
                  value={formData.max_occupancy}
                  onChange={(e) => setFormData({ ...formData, max_occupancy: e.target.value })}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Bed Type</label>
                <select
                  value={formData.bed_type}
                  onChange={(e) => setFormData({ ...formData, bed_type: e.target.value })}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
                >
                  {BED_TYPES.map((b) => (
                    <option key={b} value={b}>{b.charAt(0).toUpperCase() + b.slice(1)}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_active_edit"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <label htmlFor="is_active_edit" className="text-sm font-medium text-gray-700">
                  Active (available for booking)
                </label>
              </div>

              <div className="flex gap-3 pt-2">
                <Button type="button" variant="secondary" onClick={cancelEdit} fullWidth>Cancel</Button>
                <Button onClick={handleSave} isLoading={saving} fullWidth>Save Changes</Button>
              </div>
            </div>
          </Card>
        )}
      </div>
    </Layout>
  );
}
