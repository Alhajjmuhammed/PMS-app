'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Table from '@/components/Table';
import Card from '@/components/Card';
import Button from '@/components/Button';
import api from '@/lib/api';

interface RoomType {
  id: number;
  name: string;
  description: string;
  base_price: number;
  max_occupancy: number;
  bed_type: string;
  amenities: string[];
}

export default function RoomTypesPage() {
  const router = useRouter();
  const [roomTypes, setRoomTypes] = useState<RoomType[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRoomTypes();
  }, []);

  const loadRoomTypes = async () => {
    try {
      const response = await api.get('/api/v1/room-types/');
      setRoomTypes(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to load room types:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { header: 'ID', accessor: 'id' as keyof RoomType },
    { header: 'Name', accessor: 'name' as keyof RoomType },
    { 
      header: 'Base Price', 
      accessor: (row: RoomType) => `$${row.base_price?.toLocaleString() || 0} / night` 
    },
    { header: 'Max Occupancy', accessor: 'max_occupancy' as keyof RoomType },
    { header: 'Bed Type', accessor: 'bed_type' as keyof RoomType },
    {
      header: 'Amenities',
      accessor: (row: RoomType) => (
        <div className="flex flex-wrap gap-1">
          {row.amenities?.slice(0, 3).map((amenity, idx) => (
            <span key={idx} className="px-2 py-0.5 bg-primary-100 text-primary-700 rounded text-xs">
              {amenity}
            </span>
          ))}
          {row.amenities?.length > 3 && (
            <span className="text-xs text-gray-500">+{row.amenities.length - 3}</span>
          )}
        </div>
      ),
    },
  ];

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Room Types</h1>
          <Button onClick={() => router.push('/rooms/types/new')}>
            New Room Type
          </Button>
        </div>

        <Card padding="none">
          <Table
            data={roomTypes}
            columns={columns}
            loading={loading}
            emptyMessage="No room types found"
            onRowClick={(row) => router.push(`/rooms/types/${row.id}`)}
          />
        </Card>
      </div>
    </Layout>
  );
}
