'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Table from '@/components/Table';
import Button from '@/components/Button';
import Card from '@/components/Card';
import { reservationService, Reservation } from '@/lib/services';
import { format } from 'date-fns';

export default function ReservationsPage() {
  const router = useRouter();
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadReservations();
  }, [filter]);

  const loadReservations = async () => {
    try {
      setLoading(true);
      const params = filter !== 'all' ? { status: filter } : {};
      const data = await reservationService.getAll(params);
      setReservations(data.results || data);
    } catch (error) {
      console.error('Failed to load reservations:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirmed: 'bg-blue-100 text-blue-800',
      checked_in: 'bg-green-100 text-green-800',
      checked_out: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-red-100 text-red-800',
    };
    
    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {status.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  const columns = [
    {
      header: 'ID',
      accessor: 'id' as keyof Reservation,
    },
    {
      header: 'Guest',
      accessor: (row: Reservation) => `${row.guest?.first_name} ${row.guest?.last_name}`,
    },
    {
      header: 'Room',
      accessor: (row: Reservation) => row.room?.number || 'N/A',
    },
    {
      header: 'Check-in',
      accessor: (row: Reservation) => format(new Date(row.check_in), 'MMM dd, yyyy'),
    },
    {
      header: 'Check-out',
      accessor: (row: Reservation) => format(new Date(row.check_out), 'MMM dd, yyyy'),
    },
    {
      header: 'Status',
      accessor: (row: Reservation) => getStatusBadge(row.status),
    },
    {
      header: 'Total',
      accessor: (row: Reservation) => `$${row.total_amount?.toLocaleString() || 0}`,
    },
  ];

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Reservations</h1>
          <Button onClick={() => router.push('/reservations/new')}>
            + New Reservation
          </Button>
        </div>

        <Card padding="none">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex gap-2">
              {['all', 'confirmed', 'checked_in', 'pending', 'cancelled'].map((status) => (
                <button
                  key={status}
                  onClick={() => setFilter(status)}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    filter === status
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {status.replace('_', ' ').toUpperCase()}
                </button>
              ))}
            </div>
          </div>
          
          <Table
            data={reservations}
            columns={columns}
            onRowClick={(row) => router.push(`/reservations/${row.id}`)}
            loading={loading}
            emptyMessage="No reservations found"
          />
        </Card>
      </div>
    </Layout>
  );
}
