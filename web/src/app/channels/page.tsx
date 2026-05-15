'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import api from '@/lib/api';
import clsx from 'clsx';
import {
  HomeIcon, ChevronRightIcon, GlobeAltIcon,
  CheckCircleIcon, ExclamationTriangleIcon, XMarkIcon,
} from '@heroicons/react/24/outline';

const CHANNEL_TYPES = [
  { value: 'OTA', label: 'Online Travel Agency (OTA)' },
  { value: 'GDS', label: 'Global Distribution System (GDS)' },
  { value: 'DIRECT', label: 'Direct Booking' },
];

const PRESET_CHANNELS = [
  'Booking.com', 'Expedia', 'Airbnb', 'Hotels.com',
  'Agoda', 'TripAdvisor', 'Google Hotel Ads', 'direct.com',
];

export default function ChannelManagerPage() {
  const [channels, setChannels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);

  // Add Channel modal state
  const [showAddModal, setShowAddModal] = useState(false);
  const [addForm, setAddForm] = useState({ name: '', code: '', channel_type: 'OTA', commission_percent: '15' });
  const [saving, setSaving] = useState(false);

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  };

  useEffect(() => {
    loadChannels();
  }, []);

  const loadChannels = async () => {
    try {
      const response = await api.get('/api/v1/channels/property-channels/');
      setChannels(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to load channels:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleChannel = async (channelId: number, isActive: boolean) => {
    try {
      await api.patch(`/api/v1/channels/property-channels/${channelId}/`, { is_active: !isActive });
      await loadChannels();
    } catch (error) {
      showToast('Failed to update channel', false);
    }
  };

  const syncChannel = async (channelId: number) => {
    try {
      await api.post(`/api/v1/channels/property-channels/${channelId}/sync/`);
      showToast('Sync initiated successfully!');
    } catch (error) {
      showToast('Failed to sync channel', false);
    }
  };

  const handleAddChannel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!addForm.name || !addForm.code) return;
    setSaving(true);
    try {
      await api.post('/api/v1/channels/channels/', {
        name: addForm.name,
        code: addForm.code.toUpperCase(),
        channel_type: addForm.channel_type,
        commission_percent: parseFloat(addForm.commission_percent) || 0,
        is_active: true,
      });
      showToast(`Channel "${addForm.name}" added`);
      setAddForm({ name: '', code: '', channel_type: 'OTA', commission_percent: '15' });
      setShowAddModal(false);
      await loadChannels();
    } catch (e: any) {
      showToast(e?.response?.data?.detail || e?.response?.data?.code?.[0] || 'Failed to add channel', false);
    } finally {
      setSaving(false);
    }
  };

  const openAddWithPreset = (name: string) => {
    setAddForm(f => ({
      ...f,
      name,
      code: name.replace(/[^A-Z0-9]/gi, '').toUpperCase().slice(0, 10),
    }));
    setShowAddModal(true);
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
      {/* Toast */}
      {toast && (
        <div className={clsx(
          'fixed top-5 right-5 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium',
          toast.ok ? 'bg-emerald-600 text-white' : 'bg-red-600 text-white'
        )}>
          {toast.ok
            ? <CheckCircleIcon className="w-5 h-5 flex-shrink-0" />
            : <ExclamationTriangleIcon className="w-5 h-5 flex-shrink-0" />}
          {toast.msg}
        </div>
      )}

      {/* Add Channel Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setShowAddModal(false)} />
          <div className="relative bg-white rounded-2xl shadow-2xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-5">
              <h3 className="font-semibold text-lg text-slate-900">Add Channel</h3>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-slate-600">
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleAddChannel} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Channel Name</label>
                <input
                  type="text"
                  value={addForm.name}
                  onChange={e => setAddForm(f => ({ ...f, name: e.target.value }))}
                  placeholder="e.g., Booking.com"
                  className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-300"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Channel Code</label>
                <input
                  type="text"
                  value={addForm.code}
                  onChange={e => setAddForm(f => ({ ...f, code: e.target.value.toUpperCase() }))}
                  placeholder="e.g., BOOKING"
                  maxLength={20}
                  className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-300 font-mono"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Channel Type</label>
                <select
                  value={addForm.channel_type}
                  onChange={e => setAddForm(f => ({ ...f, channel_type: e.target.value }))}
                  className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-300"
                >
                  {CHANNEL_TYPES.map(t => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Commission % </label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  value={addForm.commission_percent}
                  onChange={e => setAddForm(f => ({ ...f, commission_percent: e.target.value }))}
                  className="w-full px-3 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-300"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowAddModal(false)}
                  className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-600 hover:bg-slate-50">
                  Cancel
                </button>
                <button type="submit" disabled={saving}
                  className="flex-1 px-4 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-700 text-white text-sm font-semibold disabled:opacity-50">
                  {saving ? 'Adding…' : 'Add Channel'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="p-5 lg:p-6 space-y-5">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-1.5 text-sm text-slate-400">
          <HomeIcon className="w-4 h-4" />
          <span>Home</span>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <span className="text-slate-700 font-medium">Channels</span>
        </nav>

        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-sky-100 flex items-center justify-center flex-shrink-0">
              <GlobeAltIcon className="w-5 h-5 text-sky-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Channel Manager</h1>
              <p className="text-slate-500 text-sm mt-0.5">{channels.length} channel{channels.length !== 1 ? 's' : ''} configured</p>
            </div>
          </div>
          <Button onClick={() => setShowAddModal(true)}>Add Channel</Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            <div className="col-span-full flex items-center justify-center py-20">
              <div className="w-10 h-10 border-4 border-sky-500 border-t-transparent rounded-full animate-spin" />
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
            {PRESET_CHANNELS.map((name) => (
              <button
                key={name}
                onClick={() => openAddWithPreset(name)}
                className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-sky-500 hover:bg-sky-50 transition-colors text-center"
              >
                <div className="font-medium text-gray-700">{name}</div>
                <div className="text-xs text-gray-500 mt-1">Click to connect</div>
              </button>
            ))}
          </div>
        </Card>
      </div>
    </Layout>
  );
}
