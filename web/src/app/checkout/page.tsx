'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { reservationService } from '@/lib/services';
import { format } from 'date-fns';

export default function CheckOutPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [reservationId, setReservationId] = useState('');
  const [reservation, setReservation] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      const data = await reservationService.getById(parseInt(reservationId));
      
      if (data.status !== 'checked_in') {
        alert('This reservation is not currently checked in');
        return;
      }
      
      setReservation(data);
      setStep(2);
    } catch (error) {
      alert('Reservation not found');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckOut = async () => {
    try {
      setLoading(true);
      await reservationService.checkOut(reservation.id);
      alert('Check-out successful!');
      router.push('/dashboard');
    } catch (error) {
      alert('Failed to check out');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Guest Check-Out</h1>

        {step === 1 && (
          <Card title="Find Reservation">
            <form onSubmit={handleSearch} className="space-y-4">
              <Input
                label="Reservation ID"
                value={reservationId}
                onChange={(e) => setReservationId(e.target.value)}
                placeholder="Enter reservation ID"
                required
              />
              <Button type="submit" isLoading={loading} fullWidth>
                Search
              </Button>
            </form>
          </Card>
        )}

        {step === 2 && reservation && (
          <>
            <Card title="Reservation Details">
              <dl className="space-y-3">
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Reservation ID:</dt>
                  <dd className="text-sm text-gray-900">#{reservation.id}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Guest Name:</dt>
                  <dd className="text-sm text-gray-900">
                    {reservation.guest?.first_name} {reservation.guest?.last_name}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Room Number:</dt>
                  <dd className="text-sm text-gray-900">{reservation.room?.number}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Check-in Date:</dt>
                  <dd className="text-sm text-gray-900">
                    {format(new Date(reservation.check_in_date), 'EEEE, MMMM dd, yyyy')}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Check-out Date:</dt>
                  <dd className="text-sm text-gray-900">
                    {format(new Date(reservation.check_out_date), 'EEEE, MMMM dd, yyyy')}
                  </dd>
                </div>
              </dl>
            </Card>

            <Card title="Billing Summary">
              <dl className="space-y-3">
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Room Charges:</dt>
                  <dd className="text-sm text-gray-900">${reservation.total_amount?.toLocaleString() || 0}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">Additional Charges:</dt>
                  <dd className="text-sm text-gray-900">$0</dd>
                </div>
                <div className="flex justify-between pt-3 border-t">
                  <dt className="text-base font-semibold text-gray-900">Total Amount:</dt>
                  <dd className="text-base font-semibold text-gray-900">
                    ${reservation.total_amount?.toLocaleString() || 0}
                  </dd>
                </div>
              </dl>
            </Card>

            <div className="flex gap-3">
              <Button variant="secondary" onClick={() => setStep(1)} fullWidth>
                Back
              </Button>
              <Button onClick={handleCheckOut} isLoading={loading} fullWidth>
                Confirm Check-Out
              </Button>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}
