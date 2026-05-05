'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import api from '@/lib/api';
import { format } from 'date-fns';

export default function MaintenanceDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [request, setRequest] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      loadRequest();
    }
  }, [params.id]);

  const loadRequest = async () => {
    try {
      const response = await api.get(`/api/v1/maintenance/requests/${params.id}/`);
      setRequest(response.data);
    } catch (error) {
      alert('Failed to load request');
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (newStatus: string) => {
    try {
      await api.patch(`/api/v1/maintenance/requests/${params.id}/`, { status: newStatus });
      await loadRequest();
    } catch (error) {
      alert('Failed to update status');
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
          <h1 className="text-3xl font-bold text-gray-900">Request #{request?.id}</h1>
          <Button variant="secondary" onClick={() => router.back()}>
            Back
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="Request Details">
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Room Number</dt>
                <dd className="mt-1 text-lg font-semibold text-gray-900">
                  {request?.room?.number || 'N/A'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Issue</dt>
                <dd className="mt-1 text-sm font-semibold text-gray-900">
                  {request?.issue || 'N/A'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Priority</dt>
                <dd className="mt-1">{getPriorityBadge(request?.priority || 'medium')}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Status</dt>
                <dd className="mt-1 text-sm text-gray-900 capitalize">
                  {request?.status || 'N/A'}
                </dd>
              </div>
            </dl>
          </Card>

          <Card title="Tracking">
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Reported By</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {request?.reported_by
                    ? `${request.reported_by.first_name} ${request.reported_by.last_name}`
                    : 'Unknown'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Assigned To</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {request?.assigned_to
                    ? `${request.assigned_to.first_name} ${request.assigned_to.last_name}`
                    : 'Unassigned'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Created</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {request?.created_at ? format(new Date(request.created_at), 'PPpp') : 'N/A'}
                </dd>
              </div>
              {request?.resolved_at && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Resolved</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {format(new Date(request.resolved_at), 'PPpp')}
                  </dd>
                </div>
              )}
            </dl>
          </Card>
        </div>

        <Card title="Description">
          <p className="text-sm text-gray-700 whitespace-pre-wrap">
            {request?.description || 'No description provided'}
          </p>
        </Card>

        {request?.resolution_notes && (
          <Card title="Resolution Notes">
            <p className="text-sm text-gray-700 whitespace-pre-wrap">
              {request.resolution_notes}
            </p>
          </Card>
        )}

        <Card title="Actions">
          <div className="flex gap-3">
            {request?.status === 'open' && (
              <Button onClick={() => updateStatus('in_progress')}>
                Start Work
              </Button>
            )}
            {request?.status === 'in_progress' && (
              <Button variant="success" onClick={() => updateStatus('resolved')}>
                Mark Resolved
              </Button>
            )}
            {request?.status === 'resolved' && (
              <Button variant="secondary" onClick={() => updateStatus('open')}>
                Reopen Request
              </Button>
            )}
          </div>
        </Card>
      </div>
    </Layout>
  );
}
