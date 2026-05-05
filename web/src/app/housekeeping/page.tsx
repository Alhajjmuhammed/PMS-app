'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import Table from '@/components/Table';
import Card from '@/components/Card';
import Button from '@/components/Button';
import api from '@/lib/api';

interface HousekeepingTask {
  id: number;
  room: {
    number: string;
  };
  task_type: string;
  status: string;
  assigned_to?: {
    first_name: string;
    last_name: string;
  };
  priority: string;
}

export default function HousekeepingPage() {
  const [tasks, setTasks] = useState<HousekeepingTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('pending');

  useEffect(() => {
    loadTasks();
  }, [filter]);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const params = filter !== 'all' ? { status: filter } : {};
      const response = await api.get('/api/v1/housekeeping/tasks/', { params });
      setTasks(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async (taskId: number) => {
    try {
      await api.patch(`/api/v1/housekeeping/tasks/${taskId}/`, { status: 'completed' });
      await loadTasks();
    } catch (error) {
      alert('Failed to update task');
    }
  };

  const getPriorityBadge = (priority: string) => {
    const colors = {
      high: 'bg-red-100 text-red-800',
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
    { header: 'ID', accessor: 'id' as keyof HousekeepingTask },
    { header: 'Room', accessor: (row: HousekeepingTask) => row.room?.number || 'N/A' },
    { header: 'Task Type', accessor: 'task_type' as keyof HousekeepingTask },
    { header: 'Priority', accessor: (row: HousekeepingTask) => getPriorityBadge(row.priority) },
    { 
      header: 'Assigned To', 
      accessor: (row: HousekeepingTask) => {
        return row.assigned_to 
          ? `${row.assigned_to.first_name} ${row.assigned_to.last_name}`
          : 'Unassigned';
      }
    },
    { header: 'Status', accessor: 'status' as keyof HousekeepingTask },
    {
      header: 'Actions',
      accessor: (row: HousekeepingTask) => (
        <Button
          size="sm"
          variant="success"
          onClick={(e) => {
            e.stopPropagation();
            handleComplete(row.id);
          }}
          disabled={row.status === 'completed'}
        >
          {row.status === 'completed' ? 'Completed' : 'Complete'}
        </Button>
      ),
    },
  ];

  return (
    <Layout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Housekeeping</h1>

        <Card padding="none">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex gap-2">
              {['all', 'pending', 'in_progress', 'completed'].map((status) => (
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
            data={tasks}
            columns={columns}
            loading={loading}
            emptyMessage="No housekeeping tasks found"
          />
        </Card>
      </div>
    </Layout>
  );
}
