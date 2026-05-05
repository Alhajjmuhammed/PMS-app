'use client';

import { useState } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import api from '@/lib/api';

export default function ExportCenterPage() {
  const [loading, setLoading] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState({
    start: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0],
  });

  const handleExport = async (type: string, format: string) => {
    try {
      setLoading(`${type}-${format}`);
      
      const response = await api.get(`/api/v1/reports/export/${type}/`, {
        params: { ...dateRange, format },
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${type}-${dateRange.start}-${dateRange.end}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      alert('Export downloaded successfully!');
    } catch (error) {
      alert('Failed to export data');
    } finally {
      setLoading(null);
    }
  };

  const exportTypes = [
    {
      id: 'reservations',
      title: 'Reservations',
      description: 'Export all reservation data',
      icon: '📅',
    },
    {
      id: 'revenue',
      title: 'Revenue Report',
      description: 'Financial summary and revenue breakdown',
      icon: '💰',
    },
    {
      id: 'guests',
      title: 'Guest List',
      description: 'Complete guest database',
      icon: '👤',
    },
    {
      id: 'occupancy',
      title: 'Occupancy Report',
      description: 'Room occupancy statistics',
      icon: '🏨',
    },
    {
      id: 'housekeeping',
      title: 'Housekeeping',
      description: 'Task history and status',
      icon: '🧹',
    },
    {
      id: 'maintenance',
      title: 'Maintenance',
      description: 'Maintenance request history',
      icon: '🔧',
    },
  ];

  return (
    <Layout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Export Center</h1>

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

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {exportTypes.map((type) => (
            <Card key={type.id}>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="text-4xl">{type.icon}</div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{type.title}</h3>
                    <p className="text-sm text-gray-500">{type.description}</p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => handleExport(type.id, 'csv')}
                    isLoading={loading === `${type.id}-csv`}
                    fullWidth
                  >
                    Export CSV
                  </Button>
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => handleExport(type.id, 'xlsx')}
                    isLoading={loading === `${type.id}-xlsx`}
                    fullWidth
                  >
                    Export Excel
                  </Button>
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => handleExport(type.id, 'pdf')}
                    isLoading={loading === `${type.id}-pdf`}
                    fullWidth
                  >
                    Export PDF
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>

        <Card title="Export History">
          <p className="text-sm text-gray-500">Recent exports will appear here</p>
          <div className="mt-4 text-center text-gray-400 py-8">
            No export history available
          </div>
        </Card>
      </div>
    </Layout>
  );
}
