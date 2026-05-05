'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Table from '@/components/Table';
import Card from '@/components/Card';
import Input from '@/components/Input';
import Button from '@/components/Button';
import { roomService, Room } from '@/lib/services';
import { format } from 'date-fns';

export default function RoomsPage() {
  const router = useRouter();
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [availability, setAvailability] = useState<any[]>([]);
  const [checkIn, setCheckIn] = useState('');
  const [checkOut, setCheckOut] = useState('');
  const [showAvailability, setShowAvailability] = useState(false);

  useEffect(() => {
    loadRooms();
  }, [statusFilter]);

  const loadRooms = async () => {
    try {
      setLoading(true);
      const params = statusFilter !== 'all' ? { status: statusFilter } : {};
      const data = await roomService.getAll(params);
      setRooms(data.results || data);
    } catch (error) {
      console.error('Failed to load rooms:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckAvailability = async () => {
    if (!checkIn || !checkOut) {
      alert('Please select check-in and check-out dates');
      return;
    }

    try {
      const data = await roomService.getAvailability(checkIn, checkOut);
      setAvailability(data);
      setShowAvailability(true);
    } catch (error) {
      console.error('Failed to check availability:', error);
      alert('Failed to check availability');
    }
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      available: 'bg-green-100 text-green-800',
      occupied: 'bg-red-100 text-red-800',
      maintenance: 'bg-yellow-100 text-yellow-800',
      cleaning: 'bg-blue-100 text-blue-800',
    };
    
    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {status.toUpperCase()}
      </span>
    );
  };

  const columns = [
    { header: 'Number', accessor: 'number' as keyof Room },
    { header: 'Floor', accessor: 'floor' as keyof Room },
    { header: 'Type', accessor: (row: Room) => row.room_type?.name || 'N/A' },
    { header: 'Price', accessor: (row: Room) => `$${row.room_type?.base_price || 0}/night` },
    { header: 'Status', accessor: (row: Room) => getStatusBadge(row.status) },
    { header: 'Clean', accessor: (row: Room) => row.is_clean ? '✓ Yes' : '✗ No' },
  ];

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Rooms</h1>
        </div>

        {/* Availability Checker */}
        <Card title="Check Availability">
          <div className="flex gap-4 items-end">
            <Input
              label="Check-in"
              type="date"
              value={checkIn}
              onChange={(e) => setCheckIn(e.target.value)}
            />
            <Input
              label="Check-out"
              type="date"
              value={checkOut}
              onChange={(e) => setCheckOut(e.target.value)}
            />
            <Button onClick={handleCheckAvailability}>
              Check Availability
            </Button>
          </div>
          
          {showAvailability && (
            <div className="mt-4">
              <p className="text-sm font-medium text-gray-700 mb-2">
                Available Rooms: {availability.length}
              </p>
              <div className="grid grid-cols-3 gap-2">
                {availability.map((room: any) => (
                  <div key={room.id} className="p-3 border rounded-md">
                    <p className="font-semibold">Room {room.number}</p>
                    <p className="text-sm text-gray-600">{room.room_type?.name}</p>
                    <p className="text-sm font-medium">${room.room_type?.base_price}/night</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>

        {/* Rooms List */}
        <Card padding="none">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex gap-2">
              {['all', 'available', 'occupied', 'cleaning', 'maintenance'].map((status) => (
                <button
                  key={status}
                  onClick={() => setStatusFilter(status)}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    statusFilter === status
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {status.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
          
          <Table
            data={rooms}
            columns={columns}
            onRowClick={(row) => router.push(`/rooms/${row.id}`)}
            loading={loading}
            emptyMessage="No rooms found"
          />
        </Card>
      </div>
    </Layout>
  );
}
