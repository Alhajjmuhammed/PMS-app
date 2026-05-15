'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { roomTypeService } from '@/lib/services';

const BED_TYPES = ['single', 'double', 'queen', 'king', 'twin', 'suite'];

export default function CreateRoomTypePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    description: '',
    base_rate: '',
    max_occupancy: '2',
    bed_type: 'double',
    is_active: true,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      await roomTypeService.create({
        ...formData,
        base_rate: parseFloat(formData.base_rate),
        max_occupancy: parseInt(formData.max_occupancy),
      });
      router.push('/rooms/types');
    } catch (error: any) {
      setError(error?.response?.data ? JSON.stringify(error.response.data) : 'Failed to create room type');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-2xl mx-auto space-y-6">
        {error && (
          <div className="px-4 py-3 rounded-lg bg-red-50 text-red-800 border border-red-200 text-sm font-medium">{error}</div>
        )}
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Create Room Type</h1>
          <Button variant="secondary" onClick={() => router.back()}>
            Cancel
          </Button>
        </div>

        <Card>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g. Deluxe King"
                required
              />
              <Input
                label="Code"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                placeholder="e.g. DLX-KING"
                helperText="Short unique identifier (max 20 chars)"
                maxLength={20}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                placeholder="Describe this room type..."
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
                placeholder="99.00"
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
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <label htmlFor="is_active" className="text-sm font-medium text-gray-700">
                Active (available for booking)
              </label>
            </div>

            <div className="flex gap-3 pt-4">
              <Button type="button" variant="secondary" onClick={() => router.back()} fullWidth>
                Cancel
              </Button>
              <Button type="submit" isLoading={loading} fullWidth>
                Create Room Type
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </Layout>
  );
}
