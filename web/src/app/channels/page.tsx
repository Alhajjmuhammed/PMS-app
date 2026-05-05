'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import api from '@/lib/api';

export default function ChannelManagerPage() {
  const [channels, setChannels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadChannels();
  }, []);

  const loadChannels = async () => {
    try {
      const response = await api.get('/api/v1/channels/');
      setChannels(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to load channels:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleChannel = async (channelId: number, isActive: boolean) => {
    try {
      await api.patch(`/api/v1/channels/${channelId}/`, { is_active: !isActive });
      await loadChannels();
    } catch (error) {
      alert('Failed to update channel');
    }
  };

  const syncChannel = async (channelId: number) => {
    try {
      await api.post(`/api/v1/channels/${channelId}/sync/`);
      alert('Sync initiated successfully!');
    } catch (error) {
      alert('Failed to sync channel');
    }
  };

  const getStatusBadge = (isActive: boolean, connected: boolean) => {
    if (!isActive) {
      return <span className="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">Inactive</span>;
    }
    if (connected) {
      return <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Connected</span>;
    }
    return <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">Disconnected</span>;
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Channel Manager</h1>
          <Button>Add Channel</Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            <div className="col-span-full flex justify-center py-12">
              <svg className="animate-spin h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            </div>
          ) : channels.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <p className="text-gray-500">No channels configured</p>
            </div>
          ) : (
            channels.map((channel) => (
              <Card key={channel.id}>
                <div className="space-y-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{channel.name}</h3>
                      <p className="text-sm text-gray-500">{channel.type}</p>
                    </div>
                    {getStatusBadge(channel.is_active, channel.is_connected)}
                  </div>

                  <dl className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <dt className="text-gray-500">Reservations:</dt>
                      <dd className="font-medium">{channel.total_reservations || 0}</dd>
                    </div>
                    <div className="flex justify-between text-sm">
                      <dt className="text-gray-500">Last Sync:</dt>
                      <dd className="font-medium">
                        {channel.last_sync ? new Date(channel.last_sync).toLocaleString() : 'Never'}
                      </dd>
                    </div>
                    <div className="flex justify-between text-sm">
                      <dt className="text-gray-500">Commission:</dt>
                      <dd className="font-medium">{channel.commission_rate || 0}%</dd>
                    </div>
                  </dl>

                  <div className="flex gap-2 pt-2">
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => syncChannel(channel.id)}
                      fullWidth
                    >
                      Sync Now
                    </Button>
                    <Button
                      size="sm"
                      variant={channel.is_active ? 'danger' : 'success'}
                      onClick={() => toggleChannel(channel.id, channel.is_active)}
                      fullWidth
                    >
                      {channel.is_active ? 'Disable' : 'Enable'}
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>

        <Card title="Available Channels">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {['Booking.com', 'Expedia', 'Airbnb', 'Hotels.com', 'Agoda', 'TripAdvisor', 'Google Hotel Ads', 'direct.com'].map((name) => (
              <button
                key={name}
                className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors text-center"
              >
                <div className="font-medium text-gray-700">{name}</div>
                <div className="text-xs text-gray-500 mt-1">Not connected</div>
              </button>
            ))}
          </div>
        </Card>
      </div>
    </Layout>
  );
}
