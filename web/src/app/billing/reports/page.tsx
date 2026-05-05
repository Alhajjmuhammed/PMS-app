'use client';

import { useState } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Input from '@/components/Input';
import Button from '@/components/Button';
import Table from '@/components/Table';
import api from '@/lib/api';
import { format } from 'date-fns';

interface BillingStats {
  totalRevenue: number;
  paidAmount: number;
  pendingAmount: number;
  overdueAmount: number;
  invoiceCount: number;
  averageInvoiceValue: number;
  revenueByCategory: { category: string; amount: number }[];
  topPayingGuests: { guest: string; total: number }[];
  paymentMethodBreakdown: { method: string; amount: number }[];
}

export default function BillingReportsPage() {
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState({
    start_date: format(new Date(new Date().setMonth(new Date().getMonth() - 1)), 'yyyy-MM-dd'),
    end_date: format(new Date(), 'yyyy-MM-dd'),
  });
  const [stats, setStats] = useState<BillingStats>({
    totalRevenue: 0,
    paidAmount: 0,
    pendingAmount: 0,
    overdueAmount: 0,
    invoiceCount: 0,
    averageInvoiceValue: 0,
    revenueByCategory: [],
    topPayingGuests: [],
    paymentMethodBreakdown: [],
  });

  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      const response = await api.get('/billing/reports/', {
        params: dateRange,
      });

      const data = response.data;
      setStats({
        totalRevenue: data.total_revenue || 0,
        paidAmount: data.paid_amount || 0,
        pendingAmount: data.pending_amount || 0,
        overdueAmount: data.overdue_amount || 0,
        invoiceCount: data.invoice_count || 0,
        averageInvoiceValue: data.avg_invoice_value || 0,
        revenueByCategory: data.revenue_by_category || [],
        topPayingGuests: data.top_paying_guests || [],
        paymentMethodBreakdown: data.payment_methods || [],
      });
    } catch (error) {
      console.error('Failed to generate billing report:', error);
      alert('Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Billing Reports</h1>
          <p className="text-gray-500">Detailed billing and revenue analysis</p>
        </div>

        {/* Filters */}
        <Card>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label="Start Date"
              type="date"
              value={dateRange.start_date}
              onChange={(e) => setDateRange({ ...dateRange, start_date: e.target.value })}
            />
            <Input
              label="End Date"
              type="date"
              value={dateRange.end_date}
              onChange={(e) => setDateRange({ ...dateRange, end_date: e.target.value })}
            />
            <div className="flex items-end">
              <Button onClick={handleGenerateReport} disabled={loading} className="w-full">
                {loading ? 'Generating...' : 'Generate Report'}
              </Button>
            </div>
          </div>
        </Card>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <div className="space-y-2">
              <p className="text-sm text-gray-500">Total Revenue</p>
              <p className="text-3xl font-bold text-gray-900">${stats.totalRevenue.toFixed(2)}</p>
            </div>
          </Card>

          <Card>
            <div className="space-y-2">
              <p className="text-sm text-gray-500">Paid Amount</p>
              <p className="text-3xl font-bold text-green-600">${stats.paidAmount.toFixed(2)}</p>
            </div>
          </Card>

          <Card>
            <div className="space-y-2">
              <p className="text-sm text-gray-500">Pending Amount</p>
              <p className="text-3xl font-bold text-yellow-600">${stats.pendingAmount.toFixed(2)}</p>
            </div>
          </Card>

          <Card>
            <div className="space-y-2">
              <p className="text-sm text-gray-500">Overdue Amount</p>
              <p className="text-3xl font-bold text-red-600">${stats.overdueAmount.toFixed(2)}</p>
            </div>
          </Card>
        </div>

        {/* Additional Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <div className="space-y-2">
              <p className="text-sm text-gray-500">Total Invoices</p>
              <p className="text-2xl font-bold text-gray-900">{stats.invoiceCount}</p>
            </div>
          </Card>

          <Card>
            <div className="space-y-2">
              <p className="text-sm text-gray-500">Average Invoice Value</p>
              <p className="text-2xl font-bold text-gray-900">${stats.averageInvoiceValue.toFixed(2)}</p>
            </div>
          </Card>

          <Card>
            <div className="space-y-2">
              <p className="text-sm text-gray-500">Collection Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.totalRevenue > 0 ? ((stats.paidAmount / stats.totalRevenue) * 100).toFixed(1) : 0}%
              </p>
            </div>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Revenue by Category */}
          <Card>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue by Category</h3>
            <div className="space-y-3">
              {stats.revenueByCategory.length > 0 ? (
                stats.revenueByCategory.map((item, index) => (
                  <div key={index} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-700 capitalize">{item.category}</span>
                      <span className="font-medium text-gray-900">${item.amount.toFixed(2)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full"
                        style={{
                          width: `${stats.totalRevenue > 0 ? (item.amount / stats.totalRevenue) * 100 : 0}%`,
                        }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-4">No data available</p>
              )}
            </div>
          </Card>

          {/* Payment Method Breakdown */}
          <Card>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Payment Methods</h3>
            <div className="space-y-3">
              {stats.paymentMethodBreakdown.length > 0 ? (
                stats.paymentMethodBreakdown.map((item, index) => (
                  <div key={index} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-700 capitalize">{item.method.replace('_', ' ')}</span>
                      <span className="font-medium text-gray-900">${item.amount.toFixed(2)}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{
                          width: `${stats.paidAmount > 0 ? (item.amount / stats.paidAmount) * 100 : 0}%`,
                        }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-4">No data available</p>
              )}
            </div>
          </Card>
        </div>

        {/* Top Paying Guests */}
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Paying Guests</h3>
          {stats.topPayingGuests.length > 0 ? (
            <Table
              columns={[
                { key: 'guest', label: 'Guest Name' },
                { key: 'total', label: 'Total Spent' },
              ]}
              data={stats.topPayingGuests.map((guest) => ({
                guest: guest.guest,
                total: `$${guest.total.toFixed(2)}`,
              }))}
            />
          ) : (
            <p className="text-gray-500 text-center py-4">No data available</p>
          )}
        </Card>

        {/* Export Options */}
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Export Report</h3>
              <p className="text-sm text-gray-500">Download detailed billing report</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                Export CSV
              </Button>
              <Button variant="outline" size="sm">
                Export Excel
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
