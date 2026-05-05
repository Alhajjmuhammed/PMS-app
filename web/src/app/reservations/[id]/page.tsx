'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import { reservationService, Reservation } from '@/lib/services';
import { format } from 'date-fns';

export default function ReservationDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [reservation, setReservation] = useState<Reservation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReservation();
  }, [params.id]);

  const loadReservation = async () => {
    try {
      const data = await reservationService.getById(parseInt(params.id));
      setReservation(data);
    } catch (error) {
      console.error('Failed to load reservation:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckIn = async () => {
    if (!confirm('Check in this reservation?')) return;
    
    try {
      await reservationService.checkIn(parseInt(params.id));
      await loadReservation();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to check in');
    }
  };

  const handleCheckOut = async () => {
    if (!confirm('Check out this reservation?')) return;
    
    try {
      await reservationService.checkOut(parseInt(params.id));
      await loadReservation();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to check out');
    }
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

  if (!reservation) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-500">Reservation not found</p>
          <Button onClick={() => router.push('/reservations')} className="mt-4">
            Back to Reservations
          </Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Reservation #{reservation.id}</h1>
          <div className="flex gap-3">
            {reservation.status === 'confirmed' && (
              <Button onClick={handleCheckIn} variant="success">
                Check In
              </Button>
            )}
            {reservation.status === 'checked_in' && (
              <Button onClick={handleCheckOut} variant="primary">
                Check Out
              </Button>
            )}
            <Button variant="secondary" onClick={() => router.push('/reservations')}>
              Back
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="Guest Information">
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Name</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {reservation.guest?.first_name} {reservation.guest?.last_name}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Email</dt>
                <dd className="mt-1 text-sm text-gray-900">{reservation.guest?.email}</dd>
              </div>
            </dl>
          </Card>

          <Card title="Room Information">
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Room Number</dt>
                <dd className="mt-1 text-sm text-gray-900">{reservation.room?.number}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Room Type</dt>
                <dd className="mt-1 text-sm text-gray-900">{reservation.room?.type?.name}</dd>
              </div>
            </dl>
          </Card>

          <Card title="Stay Details">
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Check-in</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {format(new Date(reservation.check_in), 'EEEE, MMMM dd, yyyy')}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Check-out</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {format(new Date(reservation.check_out), 'EEEE, MMMM dd, yyyy')}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Guests</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {reservation.adults} Adults, {reservation.children} Children
                </dd>
              </div>
            </dl>
          </Card>

          <Card title="Billing">
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Status</dt>
                <dd className="mt-1">
                  <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                    {reservation.status.replace('_', ' ').toUpperCase()}
                  </span>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Total Amount</dt>
                <dd className="mt-1 text-2xl font-bold text-gray-900">
                  ${reservation.total_amount?.toLocaleString() || 0}
                </dd>
              </div>
            </dl>
          </Card>
        </div>

        {reservation.special_requests && (
          <Card title="Special Requests">
            <p className="text-sm text-gray-700">{reservation.special_requests}</p>
          </Card>
        )}
      </div>
    </Layout>
  );
}
