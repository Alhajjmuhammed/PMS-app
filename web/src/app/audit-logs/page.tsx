'use client';

import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Input from '@/components/Input';
import Button from '@/components/Button';
import Table from '@/components/Table';
import api from '@/lib/api';
import { format } from 'date-fns';

interface AuditLog {
  id: number;
  user: {
    first_name: string;
    last_name: string;
    email: string;
  };
  action: string;
  resource_type: string;
  resource_id: number;
  changes: any;
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
    resource_type: '',
    start_date: '',
    end_date: '',
  });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadLogs();
  }, [page, filters]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params = {
        page,
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== '')),
      };

      const response = await api.get('/audit-logs/', { params });
      setLogs(response.data.results || response.data);
      setTotalPages(Math.ceil((response.data.count || logs.length) / 20));
    } catch (error) {
      console.error('Failed to load audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    loadLogs();
  };

  const handleReset = () => {
    setFilters({
      user: '',
      action: '',
      resource_type: '',
      start_date: '',
      end_date: '',
    });
    setPage(1);
  };

  const actionTypes = [
    { value: '', label: 'All Actions' },
    { value: 'create', label: 'Create' },
    { value: 'update', label: 'Update' },
    { value: 'delete', label: 'Delete' },
    { value: 'login', label: 'Login' },
    { value: 'logout', label: 'Logout' },
    { value: 'view', label: 'View' },
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

  const getActionBadge = (action: string) => {
    const colors: { [key: string]: string } = {
      create: 'bg-green-100 text-green-800',
      update: 'bg-blue-100 text-blue-800',
      delete: 'bg-red-100 text-red-800',
      login: 'bg-purple-100 text-purple-800',
      logout: 'bg-gray-100 text-gray-800',
      view: 'bg-yellow-100 text-yellow-800',
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

  if (loading && logs.length === 0) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading audit logs...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Audit Logs</h1>
          <p className="text-gray-500">Track all system activity and changes</p>
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
                value={filters.resource_type}
                onChange={(e) => setFilters({ ...filters, resource_type: e.target.value })}
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
                  <div className="font-medium text-gray-900">
                    {log.user.first_name} {log.user.last_name}
                  </div>
                  <div className="text-sm text-gray-500">{log.user.email}</div>
                </div>
              ),
              action: getActionBadge(log.action),
              resource: (
                <div>
                  <div className="font-medium text-gray-900 capitalize">{log.resource_type}</div>
                  <div className="text-sm text-gray-500">ID: {log.resource_id}</div>
                </div>
              ),
              ip: log.ip_address,
              details:
                log.changes && Object.keys(log.changes).length > 0 ? (
                  <button
                    onClick={() => alert(JSON.stringify(log.changes, null, 2))}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    View Changes
                  </button>
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
              <Button variant="outline" size="sm">
                Export CSV
              </Button>
              <Button variant="outline" size="sm">
                Export PDF
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </Layout>
  );
}
