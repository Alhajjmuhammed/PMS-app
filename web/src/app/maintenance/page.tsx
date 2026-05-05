'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import Table from '@/components/Table';
import Card from '@/components/Card';
import Button from '@/components/Button';
import api from '@/lib/api';
import { format } from 'date-fns';

interface MaintenanceRequest {
  id: number;
  room: {
    number: string;
  };
  issue: string;
  priority: string;
  status: string;
  reported_by?: {
    first_name: string;
    last_name: string;
  };
  created_at: string;
}

export default function MaintenancePage() {
  const [requests, setRequests] = useState<MaintenanceRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('open');

  useEffect(() => {
    loadRequests();
  }, [filter]);

  const loadRequests = async () => {
    try {
      setLoading(true);
      const params = filter !== 'all' ? { status: filter } : {};
      const response = await api.get('/api/v1/maintenance/requests/', { params });
      setRequests(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to load requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async (requestId: number) => {
    try {
      await api.patch(`/api/v1/maintenance/requests/${requestId}/`, { status: 'resolved' });
      await loadRequests();
    } catch (error) {
      alert('Failed to update request');
    }
  };

  const getPriorityBadge = (priority: string) => {
    const colors = {
      urgent: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800',
    };
    
    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${colors[priority as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {priority.toUpperCase()}
      </span>
    );
  };

  const columns = [
    { header: 'ID', accessor: 'id' as keyof MaintenanceRequest },
{ header: 'Room', accessor: (row: MaintenanceRequest) => row.room?.number || 'N/A' },
    { header: 'Issue', accessor: 'issue' as keyof MaintenanceRequest },
    { header: 'Priority', accessor: (row: MaintenanceRequest) => getPriorityBadge(row.priority) },
    { 
      header: 'Reported By', 
      accessor: (row: MaintenanceRequest) => {
        return row.reported_by 
          ? `${row.reported_by.first_name} ${row.reported_by.last_name}`
          : 'Unknown';
      }
    },
    { header: 'Status', accessor: 'status' as keyof MaintenanceRequest },
    {
      header: 'Date',
      accessor: (row: MaintenanceRequest) => format(new Date(row.created_at), 'MMM dd, yyyy'),
    },
    {
      header: 'Actions',
      accessor: (row: MaintenanceRequest) => (
        <Button
          size="sm"
          variant="success"
          onClick={(e) => {
            e.stopPropagation();
            handleResolve(row.id);
          }}
          disabled={row.status === 'resolved'}
        >
          {row.status === 'resolved' ? 'Resolved' : 'Resolve'}
        </Button>
      ),
    },
  ];

  return (
    <Layout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Maintenance Requests</h1>

        <Card padding="none">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex gap-2">
              {['all', 'open', 'in_progress', 'resolved'].map((status) => (
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
            data={requests}
            columns={columns}
            loading={loading}
            emptyMessage="No maintenance requests found"
          />
        </Card>
      </div>
    </Layout>
  );
}
