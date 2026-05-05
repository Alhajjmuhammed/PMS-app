'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import api from '@/lib/api';
import { format } from 'date-fns';

export default function TaskDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [task, setTask] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      loadTask();
    }
  }, [params.id]);

  const loadTask = async () => {
    try {
      const response = await api.get(`/api/v1/housekeeping/tasks/${params.id}/`);
      setTask(response.data);
    } catch (error) {
      alert('Failed to load task');
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (newStatus: string) => {
    try {
      await api.patch(`/api/v1/housekeeping/tasks/${params.id}/`, { status: newStatus });
      await loadTask();
    } catch (error) {
      alert('Failed to update status');
    }
  };

  const getPriorityBadge = (priority: string) => {
    const colors = {
      high: 'bg-red-100 text-red-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800',
    };
    return (
      <span className={`px-3 py-1 text-sm font-semibold rounded-full ${colors[priority as keyof typeof colors]}`}>
        {priority.toUpperCase()}
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
          <h1 className="text-3xl font-bold text-gray-900">Task #{task?.id}</h1>
          <Button variant="secondary" onClick={() => router.back()}>
            Back
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="Task Details">
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Room Number</dt>
                <dd className="mt-1 text-lg font-semibold text-gray-900">
                  {task?.room?.number || 'N/A'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Task Type</dt>
                <dd className="mt-1 text-sm text-gray-900 capitalize">
                  {task?.task_type?.replace('_', ' ') || 'N/A'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Priority</dt>
                <dd className="mt-1">{getPriorityBadge(task?.priority || 'medium')}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Status</dt>
                <dd className="mt-1 text-sm text-gray-900 capitalize">
                  {task?.status || 'N/A'}
                </dd>
              </div>
            </dl>
          </Card>

          <Card title="Assignment">
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Assigned To</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {task?.assigned_to
                    ? `${task.assigned_to.first_name} ${task.assigned_to.last_name}`
                    : 'Unassigned'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Created</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {task?.created_at ? format(new Date(task.created_at), 'PPpp') : 'N/A'}
                </dd>
              </div>
              {task?.completed_at && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Completed</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {format(new Date(task.completed_at), 'PPpp')}
                  </dd>
                </div>
              )}
            </dl>
          </Card>
        </div>

        {task?.notes && (
          <Card title="Notes">
            <p className="text-sm text-gray-700">{task.notes}</p>
          </Card>
        )}

        <Card title="Actions">
          <div className="flex gap-3">
            {task?.status === 'pending' && (
              <Button onClick={() => updateStatus('in_progress')}>
                Start Task
              </Button>
            )}
            {task?.status === 'in_progress' && (
              <Button variant="success" onClick={() => updateStatus('completed')}>
                Mark Complete
              </Button>
            )}
            {task?.status === 'completed' && (
              <Button variant="secondary" onClick={() => updateStatus('pending')}>
                Reopen Task
              </Button>
            )}
          </div>
        </Card>
      </div>
    </Layout>
  );
}
