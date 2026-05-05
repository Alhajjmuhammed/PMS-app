'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Input from '@/components/Input';
import Button from '@/components/Button';
import { reservationService } from '@/lib/services';

export default function NewReservationPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    guest_id: '',
    room_id: '',
    check_in: '',
    check_out: '',
    adults: 1,
    children: 0,
    special_requests: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await reservationService.create({
        ...formData,
        guest: parseInt(formData.guest_id),
        room: parseInt(formData.room_id),
      });
      router.push('/reservations');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create reservation');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <Layout>
      <div className="max-w-2xl">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">New Reservation</h1>

        <Card>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Guest ID"
                name="guest_id"
                type="number"
                value={formData.guest_id}
                onChange={handleChange}
                required
                helperText="Enter existing guest ID"
              />
              <Input
                label="Room ID"
                name="room_id"
                type="number"
                value={formData.room_id}
                onChange={handleChange}
                required
                helperText="Enter available room ID"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Check-in Date"
                name="check_in"
                type="date"
                value={formData.check_in}
                onChange={handleChange}
                required
              />
              <Input
                label="Check-out Date"
                name="check_out"
                type="date"
                value={formData.check_out}
                onChange={handleChange}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Adults"
                name="adults"
                type="number"
                min="1"
                value={formData.adults}
                onChange={handleChange}
                required
              />
              <Input
                label="Children"
                name="children"
                type="number"
                min="0"
                value={formData.children}
                onChange={handleChange}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Special Requests
              </label>
              <textarea
                name="special_requests"
                value={formData.special_requests}
                onChange={handleChange}
                rows={4}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:ring-primary-500 focus:border-primary-500 px-3 py-2"
                placeholder="Any special requests or notes..."
              />
            </div>

            <div className="flex justify-end gap-3">
              <Button
                type="button"
                variant="secondary"
                onClick={() => router.back()}
              >
                Cancel
              </Button>
              <Button type="submit" isLoading={loading}>
                Create Reservation
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </Layout>
  );
}
