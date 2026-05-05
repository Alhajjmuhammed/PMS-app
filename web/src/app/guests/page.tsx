'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Table from '@/components/Table';
import Button from '@/components/Button';
import Card from '@/components/Card';
import Input from '@/components/Input';
import { guestService, Guest } from '@/lib/services';

export default function GuestsPage() {
  const router = useRouter();
  const [guests, setGuests] = useState<Guest[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadGuests();
  }, []);

  const loadGuests = async () => {
    try {
      setLoading(true);
      const params = search ? { search } : {};
      const data = await guestService.getAll(params);
      setGuests(data.results || data);
    } catch (error) {
      console.error('Failed to load guests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    loadGuests();
  };

  const columns = [
    { header: 'ID', accessor: 'id' as keyof Guest },
    { 
      header: 'Name', 
      accessor: (row: Guest) => `${row.first_name} ${row.last_name}` 
    },
    { header: 'Email', accessor: 'email' as keyof Guest },
    { header: 'Phone', accessor: 'phone' as keyof Guest },
    { header: 'Nationality', accessor: (row: Guest) => row.nationality || 'N/A' },
    { 
      header: 'Reservations', 
      accessor: (row: Guest) => row.total_reservations || 0 
    },
  ];

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Guests</h1>
          <Button onClick={() => router.push('/guests/new')}>
            + New Guest
          </Button>
        </div>

        <Card>
          <div className="flex gap-3">
            <Input
              placeholder="Search by name, email, or phone..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button onClick={handleSearch}>Search</Button>
          </div>
        </Card>

        <Card padding="none">
          <Table
            data={guests}
            columns={columns}
            onRowClick={(row) => router.push(`/guests/${row.id}`)}
            loading={loading}
            emptyMessage="No guests found"
          />
        </Card>
      </div>
    </Layout>
  );
}
