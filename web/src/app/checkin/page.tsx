'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Input from '@/components/Input';
import Button from '@/components/Button';
import { reservationService, roomService } from '@/lib/services';

export default function CheckInPage() {
  const router = useRouter();
  const [step, setStep] = useState<'search' | 'confirm'>('search');
  const [reservationId, setReservationId] = useState('');
  const [reservation, setReservation] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!reservationId) {
      alert('Please enter a reservation ID');
      return;
    }

    setLoading(true);
    try {
      const data = await reservationService.getById(parseInt(reservationId));
      setReservation(data);
      setStep('confirm');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Reservation not found');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckIn = async () => {
    if (!confirm('Proceed with check-in?')) return;

    setLoading(true);
    try {
      await reservationService.checkIn(parseInt(reservationId));
      alert('Check-in successful!');
      router.push('/dashboard');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Check-in failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Check-In</h1>

        {step === 'search' && (
          <Card title="Find Reservation">
            <div className="space-y-4">
              <Input
                label="Reservation ID"
                placeholder="Enter reservation ID..."
                value={reservationId}
                onChange={(e) => setReservationId(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Button onClick={handleSearch} isLoading={loading} fullWidth>
                Search
              </Button>
            </div>
          </Card>
        )}

        {step === 'confirm' && reservation && (
          <div className="space-y-6">
            <Card title="Guest Information">
              <dl className="space-y-3">
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Name:</dt>
                  <dd className="text-sm text-gray-900 font-semibold">
                    {reservation.guest?.first_name} {reservation.guest?.last_name}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Email:</dt>
                  <dd className="text-sm text-gray-900">{reservation.guest?.email}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Room:</dt>
                  <dd className="text-sm text-gray-900 font-semibold">
                    {reservation.room?.number}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Check-in Date:</dt>
                  <dd className="text-sm text-gray-900">{reservation.check_in}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Check-out Date:</dt>
                  <dd className="text-sm text-gray-900">{reservation.check_out}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Total Amount:</dt>
                  <dd className="text-lg text-gray-900 font-bold">
                    ${reservation.total_amount?.toLocaleString()}
                  </dd>
                </div>
              </dl>
            </Card>

            <div className="flex justify-end gap-3">
              <Button variant="secondary" onClick={() => setStep('search')}>
                Cancel
              </Button>
              <Button variant="success" onClick={handleCheckIn} isLoading={loading}>
                Confirm Check-In
              </Button>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
