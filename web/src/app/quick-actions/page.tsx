'use client';

import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

interface QuickStat {
  label: string;
  value: number | string;
  color: string;
}

export default function QuickActionsPage() {
  const router = useRouter();
  const [stats, setStats] = useState<QuickStat[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await api.get('/frontdesk/dashboard/stats/');
      setStats([
        { label: 'Check-ins Today', value: response.data.check_ins_today || 0, color: 'green' },
        { label: 'Check-outs Today', value: response.data.check_outs_today || 0, color: 'blue' },
        { label: 'Available Rooms', value: response.data.available_rooms || 0, color: 'purple' },
        { label: 'Pending Tasks', value: response.data.housekeeping_pending || 0, color: 'yellow' },
      ]);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      title: 'New Reservation',
      description: 'Create a new room reservation',
      icon: '📝',
      color: 'blue',
      action: () => router.push('/reservations/new'),
    },
    {
      title: 'Check In Guest',
      description: 'Process guest check-in',
      icon: '✅',
      color: 'green',
      action: () => router.push('/frontdesk/check-in'),
    },
    {
      title: 'Check Out Guest',
      description: 'Process guest check-out',
      icon: '🚪',
      color: 'purple',
      action: () => router.push('/frontdesk/check-out'),
    },
    {
      title: 'Create Invoice',
      description: 'Generate a new invoice',
      icon: '💰',
      color: 'yellow',
      action: () => router.push('/billing/new'),
    },
    {
      title: 'Room Status',
      description: 'View all room statuses',
      icon: '🏨',
      color: 'indigo',
      action: () => router.push('/rooms'),
    },
    {
      title: 'Housekeeping Task',
      description: 'Create housekeeping task',
      icon: '🧹',
      color: 'pink',
      action: () => router.push('/housekeeping/new'),
    },
    {
      title: 'Maintenance Request',
      description: 'Report maintenance issue',
      icon: '🔧',
      color: 'red',
      action: () => router.push('/maintenance/new'),
    },
    {
      title: 'Process Payment',
      description: 'Record a payment',
      icon: '💳',
      color: 'teal',
      action: () => router.push('/billing/payments'),
    },
  ];

  const recentActivities = [
    {
      action: 'Upcoming arrivals',
      link: '/reservations?filter=arriving',
      icon: '📅',
    },
    {
      action: 'Pending check-outs',
      link: '/reservations?filter=departing',
      icon: '🚪',
    },
    {
      action: 'Dirty rooms',
      link: '/housekeeping?status=pending',
      icon: '🧹',
    },
    {
      action: 'Open maintenance',
      link: '/maintenance?status=open',
      icon: '⚠️',
    },
    {
      action: 'Unpaid invoices',
      link: '/billing?status=pending',
      icon: '💸',
    },
    {
      action: 'Night audit',
      link: '/night-audit',
      icon: '🌙',
    },
  ];

  const colorClasses = {
    blue: 'bg-blue-50 hover:bg-blue-100 border-blue-200',
    green: 'bg-green-50 hover:bg-green-100 border-green-200',
    purple: 'bg-purple-50 hover:bg-purple-100 border-purple-200',
    yellow: 'bg-yellow-50 hover:bg-yellow-100 border-yellow-200',
    indigo: 'bg-indigo-50 hover:bg-indigo-100 border-indigo-200',
    pink: 'bg-pink-50 hover:bg-pink-100 border-pink-200',
    red: 'bg-red-50 hover:bg-red-100 border-red-200',
    teal: 'bg-teal-50 hover:bg-teal-100 border-teal-200',
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Quick Actions Dashboard</h1>
          <p className="text-gray-500">Fast access to common front desk operations</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {stats.map((stat, index) => (
            <Card key={index}>
              <div className="text-center">
                <p className="text-sm text-gray-500">{stat.label}</p>
                <p className={`text-3xl font-bold text-${stat.color}-600 mt-1`}>{stat.value}</p>
              </div>
            </Card>
          ))}
        </div>

        {/* Quick Actions Grid */}
        <Card>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action, index) => (
              <button
                key={index}
                onClick={action.action}
                className={`p-6 border-2 rounded-lg transition-all ${
                  colorClasses[action.color as keyof typeof colorClasses]
                } text-left`}
              >
                <div className="text-4xl mb-3">{action.icon}</div>
                <h3 className="font-semibold text-gray-900 mb-1">{action.title}</h3>
                <p className="text-sm text-gray-600">{action.description}</p>
              </button>
            ))}
          </div>
        </Card>

        {/* Recent Activities & Quick Links */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Attention Needed</h2>
            <div className="space-y-2">
              {recentActivities.map((activity, index) => (
                <a
                  key={index}
                  href={activity.link}
                  className="flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{activity.icon}</span>
                    <span className="text-gray-900 font-medium">{activity.action}</span>
                  </div>
                  <span className="text-gray-400">→</span>
                </a>
              ))}
            </div>
          </Card>

          <Card>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Reports & Analytics</h2>
            <div className="space-y-2">
              <a
                href="/reports/revenue"
                className="flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">📊</span>
                  <span className="text-gray-900 font-medium">Revenue Report</span>
                </div>
                <span className="text-gray-400">→</span>
              </a>

              <a
                href="/reports/occupancy"
                className="flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">📈</span>
                  <span className="text-gray-900 font-medium">Occupancy Report</span>
                </div>
                <span className="text-gray-400">→</span>
              </a>

              <a
                href="/reports/guests"
                className="flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">👥</span>
                  <span className="text-gray-900 font-medium">Guest Analytics</span>
                </div>
                <span className="text-gray-400">→</span>
              </a>

              <a
                href="/reports/export"
                className="flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">📤</span>
                  <span className="text-gray-900 font-medium">Export Center</span>
                </div>
                <span className="text-gray-400">→</span>
              </a>
            </div>
          </Card>
        </div>

        {/* Keyboard Shortcuts Hint */}
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-900">Pro Tip</h3>
              <p className="text-sm text-gray-600">Use keyboard shortcuts for faster navigation</p>
            </div>
            <Button variant="outline" size="sm">
              View Shortcuts
            </Button>
          </div>
        </Card>
      </div>
    </Layout>
  );
}
