'use client';

import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Input from '@/components/Input';
import Button from '@/components/Button';
import Table from '@/components/Table';
import api from '@/lib/api';
import clsx from 'clsx';
import { format } from 'date-fns';
import {
  HomeIcon, ChevronRightIcon, ClipboardDocumentListIcon,
  CheckCircleIcon, ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

interface AuditLog {
  id: number;
  user: number;
  user_email: string;
  user_name: string;
  action: string;
  action_display: string;
  model_name: string;
  object_id: string;
  description: string;
  ip_address: string;
  user_agent: string;
  timestamp: string;
}

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    user: '',
    action: '',
    model_name: '',
    start_date: '',
    end_date: '',
  });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  };

  useEffect(() => {
    loadLogs();
  }, [page, filters]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params = {
        page,
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== '')),
      };

      const response = await api.get('/api/v1/accounts/activity-logs/', { params });
      setLogs(response.data.results || response.data);
      setTotalPages(Math.ceil((response.data.count || 1) / 20));
    } catch {
      showToast('Failed to load audit logs', false);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    // Let useEffect handle the fetch — just reset to page 1
    // If already on page 1, manually trigger since page state won't change
    if (page === 1) {
      loadLogs();
    } else {
      setPage(1);
    }
  };

  const handleReset = () => {
    setFilters({
      user: '',
      action: '',
      model_name: '',
      start_date: '',
      end_date: '',
    });
    if (page !== 1) {
      setPage(1);
    }
    // useEffect fires because filters reference always changes
  };

  const actionTypes = [
    { value: '', label: 'All Actions' },
    { value: 'CREATE', label: 'Create' },
    { value: 'UPDATE', label: 'Update' },
    { value: 'DELETE', label: 'Delete' },
    { value: 'LOGIN', label: 'Login' },
    { value: 'LOGOUT', label: 'Logout' },
    { value: 'VIEW', label: 'View' },
    { value: 'PRINT', label: 'Print' },
    { value: 'EXPORT', label: 'Export' },
  ];

  const resourceTypes = [
    { value: '', label: 'All Resources' },
    { value: 'reservation', label: 'Reservation' },
    { value: 'guest', label: 'Guest' },
    { value: 'room', label: 'Room' },
    { value: 'invoice', label: 'Invoice' },
    { value: 'payment', label: 'Payment' },
    { value: 'user', label: 'User' },
    { value: 'property', label: 'Property' },
  ];

  const handleExport = async () => {
    try {
      const params: Record<string, string> = {};
      if (filters.action) params.action = filters.action;
      if (filters.start_date) params.start_date = filters.start_date;
      if (filters.end_date) params.end_date = filters.end_date;
      if (filters.user) params.user = filters.user;
      if (filters.model_name) params.model_name = filters.model_name;

      const response = await api.get('/api/v1/accounts/activity-logs/export/', { params });
      const exportedLogs: AuditLog[] = response.data.logs || [];

      const headers = ['ID', 'Timestamp', 'User', 'Email', 'Action', 'Model', 'Object ID', 'Description', 'IP Address'];
      const rows = exportedLogs.map((log) => [
        log.id,
        log.timestamp,
        `"${(log.user_name || '').replace(/"/g, '""')}"`,
        log.user_email,
        log.action_display || log.action,
        log.model_name,
        log.object_id,
        `"${(log.description || '').replace(/"/g, '""')}"`,
        log.ip_address || '',
      ]);

      const csv = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-logs-${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      showToast(`Exported ${exportedLogs.length} log${exportedLogs.length !== 1 ? 's' : ''}`);
    } catch {
      showToast('Failed to export audit logs', false);
    }
  };

  const getActionBadge = (action: string) => {
    const colors: { [key: string]: string } = {
      create: 'bg-green-100 text-green-800',
      update: 'bg-blue-100 text-blue-800',
      delete: 'bg-red-100 text-red-800',
      login: 'bg-purple-100 text-purple-800',
      logout: 'bg-gray-100 text-gray-800',
      view: 'bg-yellow-100 text-yellow-800',
      print: 'bg-orange-100 text-orange-800',
      export: 'bg-teal-100 text-teal-800',
    };

    return (
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          colors[action.toLowerCase()] || 'bg-gray-100 text-gray-800'
        }`}
      >
        {action}
      </span>
    );
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

      <div className="p-5 lg:p-6 space-y-5">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-1.5 text-sm text-slate-400">
          <HomeIcon className="w-4 h-4" />
          <span>Home</span>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <span className="text-slate-700 font-medium">Audit Logs</span>
        </nav>

        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center flex-shrink-0">
              <ClipboardDocumentListIcon className="w-5 h-5 text-slate-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Audit Logs</h1>
              <p className="text-slate-500 text-sm mt-0.5">Track all system activity and changes</p>
            </div>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <Input
              label="User Email"
              value={filters.user}
              onChange={(e) => setFilters({ ...filters, user: e.target.value })}
              placeholder="user@example.com"
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Action</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={filters.action}
                onChange={(e) => setFilters({ ...filters, action: e.target.value })}
              >
                {actionTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Resource Type</label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={filters.model_name}
                onChange={(e) => setFilters({ ...filters, model_name: e.target.value })}
              >
                {resourceTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <Input
              label="Start Date"
              type="date"
              value={filters.start_date}
              onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
            />

            <Input
              label="End Date"
              type="date"
              value={filters.end_date}
              onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
            />
          </div>

          <div className="flex gap-4 mt-4">
            <Button onClick={handleSearch}>Search</Button>
            <Button variant="outline" onClick={handleReset}>
              Reset Filters
            </Button>
          </div>
        </Card>

        {/* Audit Logs Table */}
        <Card>
          <Table
            loading={loading}
            columns={[
              { key: 'timestamp', label: 'Timestamp' },
              { key: 'user', label: 'User' },
              { key: 'action', label: 'Action' },
              { key: 'resource', label: 'Resource' },
              { key: 'ip', label: 'IP Address' },
              { key: 'details', label: 'Details' },
            ]}
            data={logs.map((log) => ({
              timestamp: format(new Date(log.timestamp), 'MMM dd, yyyy HH:mm:ss'),
              user: (
                <div>
                  <div className="font-medium text-gray-900">{log.user_name}</div>
                  <div className="text-sm text-gray-500">{log.user_email}</div>
                </div>
              ),
              action: getActionBadge(log.action_display || log.action),
              resource: (
                <div>
                  <div className="font-medium text-gray-900 capitalize">{log.model_name}</div>
                  <div className="text-sm text-gray-500">ID: {log.object_id}</div>
                </div>
              ),
              ip: log.ip_address,
              details: log.description ? (
                <span className="text-sm text-gray-700">{log.description}</span>
              ) : (
                <span className="text-gray-400 text-sm">-</span>
              ),
            }))}
          />

          {/* Pagination */}
          <div className="flex items-center justify-between mt-4 pt-4 border-t">
            <div className="text-sm text-gray-500">
              Page {page} of {totalPages}
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={() => setPage(page - 1)} disabled={page === 1}>
                Previous
              </Button>
              <Button size="sm" variant="outline" onClick={() => setPage(page + 1)} disabled={page === totalPages}>
                Next
              </Button>
            </div>
          </div>
        </Card>

        {/* Export */}
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-900">Export Audit Logs</h3>
              <p className="text-sm text-gray-500">Download filtered audit logs for compliance</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={handleExport}>
                Export CSV
              </Button>
              <Button variant="outline" size="sm" onClick={() => showToast('PDF export is not available — please use Export CSV', false)}>
                Export PDF
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </Layout>
  );
}
