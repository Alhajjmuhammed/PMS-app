'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Input from '@/components/Input';
import api from '@/lib/api';
import clsx from 'clsx';
import {
  HomeIcon, ChevronRightIcon, TagIcon,
  PencilSquareIcon, TrashIcon, CheckCircleIcon, ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

export default function RatesPage() {
  const [rates, setRates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<number | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ id: number; name: string } | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    rate_type: 'BAR',
    description: '',
  });
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);

  const showToast = (msg: string, ok = true) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  };

  useEffect(() => {
    loadRates();
  }, []);

  const loadRates = async () => {
    try {
      const response = await api.get('/api/v1/rates/rate-plans/');
      setRates(response.data.results || response.data);
    } catch {
      showToast('Failed to load rate plans', false);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editing) {
        await api.patch(`/api/v1/rates/plans/${editing}/`, formData);
        showToast('Rate plan updated');
      } else {
        await api.post('/api/v1/rates/rate-plans/', formData);
        showToast('Rate plan created');
      }
      setFormData({ name: '', code: '', rate_type: 'BAR', description: '' });
      setEditing(null);
      await loadRates();
    } catch {
      showToast('Failed to save rate plan', false);
    }
  };

  const handleEdit = (rate: any) => {
    setEditing(rate.id);
    setFormData({
      name: rate.name || '',
      code: rate.code || '',
      rate_type: rate.rate_type || 'BAR',
      description: rate.description || '',
    });
  };

  const handleDelete = async () => {
    if (!deleteConfirm) return;
    try {
      await api.delete(`/api/v1/rates/plans/${deleteConfirm.id}/`);
      showToast(`"${deleteConfirm.name}" deleted`);
      setDeleteConfirm(null);
      await loadRates();
    } catch {
      showToast('Failed to delete rate plan', false);
    }
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

      {/* Delete confirm modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setDeleteConfirm(null)} />
          <div className="relative bg-white rounded-2xl shadow-2xl p-6 w-full max-w-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                <ExclamationTriangleIcon className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Delete Rate Plan</h3>
                <p className="text-xs text-gray-500">This cannot be undone</p>
              </div>
            </div>
            <p className="text-sm text-slate-600 mb-6">
              Are you sure you want to delete <span className="font-semibold text-slate-800">"{deleteConfirm.name}"</span>?
            </p>
            <div className="flex gap-3 justify-end">
              <button onClick={() => setDeleteConfirm(null)}
                className="px-4 py-2 rounded-lg text-sm font-semibold bg-gray-200 hover:bg-gray-300 text-gray-700 transition-colors">
                Cancel
              </button>
              <button onClick={handleDelete}
                className="px-4 py-2 rounded-lg text-sm font-semibold bg-red-600 hover:bg-red-700 text-white transition-colors">
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="p-5 lg:p-6 space-y-5">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-1.5 text-sm text-slate-400">
          <HomeIcon className="w-4 h-4" />
          <span>Home</span>
          <ChevronRightIcon className="w-3.5 h-3.5" />
          <span className="text-slate-700 font-medium">Rates</span>
        </nav>

        {/* Header */}
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center flex-shrink-0">
              <TagIcon className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Rate Management</h1>
              <p className="text-slate-500 text-sm mt-0.5">{rates.length} rate plan{rates.length !== 1 ? 's' : ''}</p>
            </div>
          </div>
        </div>

        <Card title={editing ? 'Edit Rate' : 'Create New Rate'}>
          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Rate Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Weekend Rate"
                required
              />
              <Input
                label="Code"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                placeholder="e.g., WKND-RATE"
                maxLength={20}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rate Type
              </label>
              <select
                value={formData.rate_type}
                onChange={(e) => setFormData({ ...formData, rate_type: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                <option value="RACK">Rack Rate</option>
                <option value="BAR">Best Available Rate</option>
                <option value="CORPORATE">Corporate Rate</option>
                <option value="GOVERNMENT">Government Rate</option>
                <option value="AAA">AAA Rate</option>
                <option value="SENIOR">Senior Rate</option>
                <option value="PACKAGE">Package Rate</option>
                <option value="PROMOTIONAL">Promotional Rate</option>
                <option value="OTA">OTA Rate</option>
              </select>
            </div>

            <Input
              label="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Optional description"
            />

            <div className="flex gap-3">
              {editing && (
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => {
                    setEditing(null);
                    setFormData({ name: '', code: '', rate_type: 'BAR', description: '' });
                  }}
                >
                  Cancel
                </Button>
              )}
              <Button type="submit">
                {editing ? 'Update Rate' : 'Create Rate'}
              </Button>
            </div>
          </form>
        </Card>

        <Card title="Existing Rates" padding="none">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center">
                      <div className="w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto" />
                    </td>
                  </tr>
                ) : rates.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                      No rates configured
                    </td>
                  </tr>
                ) : (
                  rates.map((rate) => (
                    <tr key={rate.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">{rate.name}</td>
                      <td className="px-6 py-4 text-sm text-gray-500 font-mono">{rate.code}</td>
                      <td className="px-6 py-4 text-sm text-gray-900 capitalize">{rate.rate_type}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">{rate.description || '—'}</td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <button
                            onClick={() => handleEdit(rate)}
                            className="p-1.5 rounded-lg text-green-600 hover:bg-green-50 transition-colors"
                            title="Edit"
                          >
                            <PencilSquareIcon className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => setDeleteConfirm({ id: rate.id, name: rate.name })}
                            className="p-1.5 rounded-lg text-red-600 hover:bg-red-50 transition-colors"
                            title="Delete"
                          >
                            <TrashIcon className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </Layout>
  );
}
