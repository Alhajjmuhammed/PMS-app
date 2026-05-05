'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import api from '@/lib/api';
import { format, subDays } from 'date-fns';

export default function ReportsPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });

  useEffect(() => {
    loadStats();
  }, [dateRange]);

  const loadStats = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/reports/summary/', {
        params: dateRange,
      });
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
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
        <h1 className="text-3xl font-bold text-gray-900">Reports & Analytics</h1>

        {/* Date Range Selector */}
        <Card>
          <div className="flex gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
                className="rounded-md border-gray-300 shadow-sm focus:ring-primary-500 focus:border-primary-500 px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <input
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
                className="rounded-md border-gray-300 shadow-sm focus:ring-primary-500 focus:border-primary-500 px-3 py-2"
              />
            </div>
          </div>
        </Card>

        {/* Revenue Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-500">Total Revenue</p>
              <p className="text-3xl font-bold text-primary-600">
                ${stats?.total_revenue?.toLocaleString() || 0}
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-500">Total Reservations</p>
              <p className="text-3xl font-bold text-blue-600">
                {stats?.total_reservations || 0}
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-500">Avg Occupancy Rate</p>
              <p className="text-3xl font-bold text-green-600">
                {stats?.avg_occupancy_rate || 0}%
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-500">Avg Daily Rate</p>
              <p className="text-3xl font-bold text-purple-600">
                ${stats?.avg_daily_rate || 0}
              </p>
            </div>
          </Card>
        </div>

        {/* Detailed Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="Room Statistics">
            <dl className="space-y-3">
              <div className="flex justify-between">
                <dt className="text-sm text-gray-500">Total Rooms:</dt>
                <dd className="text-sm font-semibold">{stats?.total_rooms || 0}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-500">Occupied:</dt>
                <dd className="text-sm font-semibold text-green-600">{stats?.occupied_rooms || 0}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-500">Available:</dt>
                <dd className="text-sm font-semibold text-blue-600">{stats?.available_rooms || 0}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-500">Maintenance:</dt>
                <dd className="text-sm font-semibold text-yellow-600">{stats?.maintenance_rooms || 0}</dd>
              </div>
            </dl>
          </Card>

          <Card title="Guest Statistics">
            <dl className="space-y-3">
              <div className="flex justify-between">
                <dt className="text-sm text-gray-500">Total Guests:</dt>
                <dd className="text-sm font-semibold">{stats?.total_guests || 0}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-500">Check-ins (Period):</dt>
                <dd className="text-sm font-semibold text-green-600">{stats?.total_checkins || 0}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-500">Check-outs (Period):</dt>
                <dd className="text-sm font-semibold text-blue-600">{stats?.total_checkouts || 0}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-sm text-gray-500">Cancellations:</dt>
                <dd className="text-sm font-semibold text-red-600">{stats?.cancellations || 0}</dd>
              </div>
            </dl>
          </Card>
        </div>
      </div>
    </Layout>
  );
}
