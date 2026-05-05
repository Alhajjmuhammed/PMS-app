'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import { guestService } from '@/lib/services';

export default function GuestDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [guest, setGuest] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      loadGuest();
    }
  }, [params.id]);

  const loadGuest = async () => {
    try {
      const data = await guestService.getById(parseInt(params.id as string));
      setGuest(data);
    } catch (error) {
      alert('Failed to load guest details');
    } finally {
      setLoading(false);
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

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Guest Details</h1>
          <Button variant="secondary" onClick={() => router.back()}>
            Back
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="Personal Information">
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Full Name</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {guest?.first_name} {guest?.last_name}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Email</dt>
                <dd className="mt-1 text-sm text-gray-900">{guest?.email}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Phone</dt>
                <dd className="mt-1 text-sm text-gray-900">{guest?.phone}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Nationality</dt>
                <dd className="mt-1 text-sm text-gray-900">{guest?.nationality || 'N/A'}</dd>
              </div>
            </dl>
          </Card>

          <Card title="Identification">
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">ID Type</dt>
                <dd className="mt-1 text-sm text-gray-900 capitalize">
                  {guest?.id_type?.replace('_', ' ') || 'N/A'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">ID Number</dt>
                <dd className="mt-1 text-sm text-gray-900">{guest?.id_number || 'N/A'}</dd>
              </div>
            </dl>
          </Card>
        </div>

        <Card title="Reservation History">
          {guest?.reservations && guest.reservations.length > 0 ? (
            <div className="space-y-2">
              {guest.reservations.map((res: any) => (
                <div key={res.id} className="p-3 bg-gray-50 rounded-md flex justify-between items-center">
                  <div>
                    <p className="font-medium">Reservation #{res.id}</p>
                    <p className="text-sm text-gray-500">
                      Room {res.room?.number} - {res.status}
                    </p>
                  </div>
                  <Button size="sm" onClick={() => router.push(`/reservations/${res.id}`)}>
                    View
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No reservation history</p>
          )}
        </Card>
      </div>
    </Layout>
  );
}
