'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import { roomService } from '@/lib/services';

export default function RoomDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [room, setRoom] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      loadRoom();
    }
  }, [params.id]);

  const loadRoom = async () => {
    try {
      const data = await roomService.getById(parseInt(params.id as string));
      setRoom(data);
    } catch (error) {
      alert('Failed to load room details');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      available: 'bg-green-100 text-green-800',
      occupied: 'bg-red-100 text-red-800',
      cleaning: 'bg-yellow-100 text-yellow-800',
      maintenance: 'bg-orange-100 text-orange-800',
      blocked: 'bg-gray-100 text-gray-800',
    };
    
    return (
      <span className={`px-3 py-1 text-sm font-semibold rounded-full ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {status?.toUpperCase()}
      </span>
    );
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
          <h1 className="text-3xl font-bold text-gray-900">Room {room?.number}</h1>
          <Button variant="secondary" onClick={() => router.back()}>
            Back
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="Room Information">
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Room Number</dt>
                <dd className="mt-1 text-2xl font-bold text-gray-900">{room?.number}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Floor</dt>
                <dd className="mt-1 text-sm text-gray-900">{room?.floor}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Room Type</dt>
                <dd className="mt-1 text-sm text-gray-900 capitalize">
                  {room?.room_type?.name || 'N/A'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Status</dt>
                <dd className="mt-1">{getStatusBadge(room?.status)}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Cleanliness</dt>
                <dd className="mt-1">
                  <span className={`px-3 py-1 text-sm font-semibold rounded-full ${
                    room?.is_clean 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {room?.is_clean ? 'CLEAN' : 'DIRTY'}
                  </span>
                </dd>
              </div>
            </dl>
          </Card>

          <Card title="Pricing & Capacity">
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Base Price</dt>
                <dd className="mt-1 text-2xl font-bold text-primary-600">
                  ${room?.room_type?.base_price?.toLocaleString() || 0}
                  <span className="text-sm text-gray-500 font-normal"> / night</span>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Max Occupancy</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {room?.room_type?.max_occupancy || 'N/A'} guests
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Beds</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {room?.room_type?.bed_type || 'N/A'}
                </dd>
              </div>
            </dl>
          </Card>
        </div>

        <Card title="Amenities">
          {room?.room_type?.amenities && room.room_type.amenities.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {room.room_type.amenities.map((amenity: string, idx: number) => (
                <span 
                  key={idx}
                  className="px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-sm font-medium"
                >
                  {amenity}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No amenities listed</p>
          )}
        </Card>

        {room?.description && (
          <Card title="Description">
            <p className="text-sm text-gray-700">{room.description}</p>
          </Card>
        )}
      </div>
    </Layout>
  );
}
