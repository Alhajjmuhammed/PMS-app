'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
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

export default function CreateRoomPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [roomTypes, setRoomTypes] = useState<any[]>([]);
  const [floors, setFloors] = useState<any[]>([]);
  const [formData, setFormData] = useState({
    room_number: '',
    room_type: '',
    floor: '',
    status: 'VC',
  });

  useEffect(() => {
    loadRoomTypes();
    loadFloors();
  }, []);

  const loadFloors = async () => {
    try {
      const data = await floorService.getAll();
      setFloors(data.results || data);
    } catch {
      // non-critical
    }
  };

  const loadRoomTypes = async () => {
    try {
      const data = await roomTypeService.getAll();
      setRoomTypes(data.results || data);
    } catch (error) {
      console.error('Failed to load room types:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      const payload: any = {
        room_number: formData.room_number,
        room_type: parseInt(formData.room_type),
        status: formData.status,
      };
      if (formData.floor) payload.floor = parseInt(formData.floor);
      await roomService.create(payload);
      router.push('/rooms');
    } catch (error: any) {
      alert(error?.response?.data ? JSON.stringify(error.response.data) : 'Failed to create room');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Create New Room</h1>
          <Button variant="secondary" onClick={() => router.back()}>
            Cancel
          </Button>
        </div>

        <Card>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Room Number"
              value={formData.room_number}
              onChange={(e) => setFormData({ ...formData, room_number: e.target.value })}
              placeholder="101"
              required
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Room Type <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.room_type}
                onChange={(e) => setFormData({ ...formData, room_type: e.target.value })}
                className="w-full rounded-md border-gray-300 shadow-sm focus:ring-primary-500 focus:border-primary-500 text-sm"
                required
              >
                <option value="">Select a room type...</option>
                {roomTypes.map((rt) => (
                  <option key={rt.id} value={rt.id}>
                    {rt.name} — ${rt.base_rate}/night · {rt.max_occupancy} guests
                  </option>
                ))}
              </select>
              {roomTypes.length === 0 && (
                <p className="mt-1 text-xs text-amber-600">
                  No room types found.{' '}
                  <a href="/rooms/types/new" className="underline">Create a room type first</a>.
                </p>
              )}
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
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>

            <div className="flex gap-3 pt-4">
              <Button type="button" variant="secondary" onClick={() => router.back()} fullWidth>
                Cancel
              </Button>
              <Button type="submit" isLoading={loading} fullWidth>
                Create Room
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </Layout>
  );
}
