'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import api from '@/lib/api';
import { format } from 'date-fns';

export default function NightAuditPage() {
  const [loading, setLoading] = useState(false);
  const [auditDate, setAuditDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [summary, setSummary] = useState<any>(null);
  const [completed, setCompleted] = useState(false);

  const loadSummary = async () => {
    try {
      const response = await api.get('/api/v1/reports/night-audit/', {
        params: { date: auditDate }
      });
      setSummary(response.data);
    } catch (error) {
      console.error('Failed to load summary:', error);
    }
  };

  useEffect(() => {
    loadSummary();
  }, [auditDate]);

  const runNightAudit = async () => {
    if (!confirm('Are you sure you want to run the night audit? This will close the business day.')) {
      return;
    }

    try {
      setLoading(true);
      await api.post('/api/v1/frontdesk/night-audit/', { date: auditDate });
      alert('Night audit completed successfully!');
      setCompleted(true);
      await loadSummary();
    } catch (error) {
      alert('Failed to run night audit');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Night Audit</h1>
          <div>
            <input
              type="date"
              value={auditDate}
              onChange={(e) => setAuditDate(e.target.value)}
              className="rounded-md border-gray-300 shadow-sm focus:ring-primary-500 focus:border-primary-500 px-3 py-2"
            />
          </div>
        </div>

        {completed && (
          <Card>
            <div className="flex items-center gap-3 text-green-700">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="font-medium">Night audit completed for {format(new Date(auditDate), 'PPP')}</span>
            </div>
          </Card>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-500">Total Revenue</p>
              <p className="text-3xl font-bold text-primary-600">
                ${summary?.total_revenue?.toLocaleString() || 0}
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-500">Check-ins</p>
              <p className="text-3xl font-bold text-blue-600">
                {summary?.total_checkins || 0}
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm font-medium text-gray-500">Check-outs</p>
              <p className="text-3xl font-bold text-green-600">
                {summary?.total_checkouts || 0}
              </p>
            </div>
          </Card>
        </div>

        <Card title="Room Status">
          <dl className="grid grid-cols-2 gap-4">
            <div>
              <dt className="text-sm font-medium text-gray-500">Occupied</dt>
              <dd className="mt-1 text-2xl font-semibold text-gray-900">
                {summary?.occupied_rooms || 0}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Available</dt>
              <dd className="mt-1 text-2xl font-semibold text-gray-900">
                {summary?.available_rooms || 0}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Dirty</dt>
              <dd className="mt-1 text-2xl font-semibold text-gray-900">
                {summary?.dirty_rooms || 0}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Maintenance</dt>
              <dd className="mt-1 text-2xl font-semibold text-gray-900">
                {summary?.maintenance_rooms || 0}
              </dd>
            </div>
          </dl>
        </Card>

        <Card title="Financial Summary">
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-sm text-gray-500">Room Revenue:</dt>
              <dd className="text-sm font-semibold">${summary?.room_revenue?.toLocaleString() || 0}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm text-gray-500">F&B Revenue:</dt>
              <dd className="text-sm font-semibold">${summary?.fnb_revenue?.toLocaleString() || 0}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm text-gray-500">Other Revenue:</dt>
              <dd className="text-sm font-semibold">${summary?.other_revenue?.toLocaleString() || 0}</dd>
            </div>
            <div className="flex justify-between border-t pt-3">
              <dt className="text-base font-semibold text-gray-900">Total:</dt>
              <dd className="text-base font-semibold text-primary-600">
                ${summary?.total_revenue?.toLocaleString() || 0}
              </dd>
            </div>
          </dl>
        </Card>

        <Card title="Outstanding Items">
          <div className="space-y-2">
            {summary?.outstanding_invoices > 0 && (
              <div className="flex justify-between items-center p-3 bg-yellow-50 rounded">
                <span className="text-sm font-medium text-yellow-800">
                  Outstanding Invoices
                </span>
                <span className="text-lg font-bold text-yellow-900">
                  {summary.outstanding_invoices}
                </span>
              </div>
            )}
            {summary?.pending_checkouts > 0 && (
              <div className="flex justify-between items-center p-3 bg-blue-50 rounded">
                <span className="text-sm font-medium text-blue-800">
                  Pending Check-outs
                </span>
                <span className="text-lg font-bold text-blue-900">
                  {summary.pending_checkouts}
                </span>
              </div>
            )}
            {summary?.housekeeping_pending > 0 && (
              <div className="flex justify-between items-center p-3 bg-orange-50 rounded">
                <span className="text-sm font-medium text-orange-800">
                  Pending Housekeeping Tasks
                </span>
                <span className="text-lg font-bold text-orange-900">
                  {summary.housekeeping_pending}
                </span>
              </div>
            )}
          </div>
        </Card>

        <Card>
          <div className="space-y-4">
            <h3 className="font-semibold text-lg">Pre-Audit Checklist</h3>
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input type="checkbox" className="rounded border-gray-300" />
                <span className="text-sm">All check-ins processed</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" className="rounded border-gray-300" />
                <span className="text-sm">All check-outs completed</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" className="rounded border-gray-300" />
                <span className="text-sm">Room rates posted</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" className="rounded border-gray-300" />
                <span className="text-sm">Payments reconciled</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" className="rounded border-gray-300" />
                <span className="text-sm">Reports reviewed</span>
              </label>
            </div>
          </div>
        </Card>

        <Card>
          <Button onClick={runNightAudit} isLoading={loading} variant="primary" fullWidth>
            Run Night Audit
          </Button>
        </Card>
      </div>
    </Layout>
  );
}
