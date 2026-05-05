'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Input from '@/components/Input';
import api from '@/lib/api';

export default function RatesPage() {
  const [rates, setRates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    rate_type: 'base',
    amount: 0,
    percentage: 0,
  });

  useEffect(() => {
    loadRates();
  }, []);

  const loadRates = async () => {
    try {
      const response = await api.get('/api/v1/rates/');
      setRates(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to load rates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editing) {
        await api.patch(`/api/v1/rates/${editing}/`, formData);
      } else {
        await api.post('/api/v1/rates/', formData);
      }
      
      setFormData({ name: '', rate_type: 'base', amount: 0, percentage: 0 });
      setEditing(null);
      await loadRates();
    } catch (error) {
      alert('Failed to save rate');
    }
  };

  const handleEdit = (rate: any) => {
    setEditing(rate.id);
    setFormData(rate);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this rate?')) return;
    
    try {
      await api.delete(`/api/v1/rates/${id}/`);
      await loadRates();
    } catch (error) {
      alert('Failed to delete rate');
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Rate Management</h1>

        <Card title={editing ? 'Edit Rate' : 'Create New Rate'}>
          <form onSubmit={handleSave} className="space-y-4">
            <Input
              label="Rate Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Weekend Rate, Corporate Discount"
              required
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rate Type
              </label>
              <select
                value={formData.rate_type}
                onChange={(e) => setFormData({ ...formData, rate_type: e.target.value })}
                className="w-full rounded-md border-gray-300 shadow-sm focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="base">Base Rate</option>
                <option value="seasonal">Seasonal Rate</option>
                <option value="discount">Discount</option>
                <option value="package">Package Rate</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Fixed Amount ($)"
                type="number"
                step="0.01"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) })}
              />
              
              <Input
                label="Percentage (%)"
                type="number"
                step="0.01"
                value={formData.percentage}
                onChange={(e) => setFormData({ ...formData, percentage: parseFloat(e.target.value) })}
              />
            </div>

            <div className="flex gap-3">
              {editing && (
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => {
                    setEditing(null);
                    setFormData({ name: '', rate_type: 'base', amount: 0, percentage: 0 });
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
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Percentage</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center">
                      <svg className="animate-spin h-8 w-8 text-primary-600 mx-auto" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
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
                      <td className="px-6 py-4 text-sm text-gray-900 capitalize">{rate.rate_type}</td>
                      <td className="px-6 py-4 text-sm text-gray-900 text-right">
                        ${rate.amount?.toFixed(2) || '0.00'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 text-right">
                        {rate.percentage?.toFixed(2) || '0.00'}%
                      </td>
                      <td className="px-6 py-4 text-right text-sm font-medium space-x-2">
                        <button
                          onClick={() => handleEdit(rate)}
                          className="text-primary-600 hover:text-primary-900"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(rate.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
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
