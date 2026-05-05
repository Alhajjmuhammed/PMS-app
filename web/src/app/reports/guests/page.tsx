'use client';

import { useState } from 'react';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Input from '@/components/Input';
import Button from '@/components/Button';
import api from '@/lib/api';
import { format } from 'date-fns';

interface GuestStats {
  totalGuests: number;
  newGuestsThisPeriod: number;
  returningGuests: number;
  averageStayDuration: number;
  topNationalities: { country: string; count: number }[];
  guestsByMonth: { month: string; count: number }[];
  averageSpending: number;
}

export default function GuestReportsPage() {
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState({
    start_date: format(new Date(new Date().setMonth(new Date().getMonth() - 1)), 'yyyy-MM-dd'),
    end_date: format(new Date(), 'yyyy-MM-dd'),
  });
  const [stats, setStats] = useState<GuestStats>({
    totalGuests: 0,
    newGuestsThisPeriod: 0,
    returningGuests: 0,
    averageStayDuration: 0,
    topNationalities: [],
    guestsByMonth: [],
    averageSpending: 0,
  });

  const handleGenerateReport = async () => {
    setLoading(true);
    try {
      const response = await api.get('/reports/guests/', {
        params: dateRange,
      });

      const data = response.data;
      setStats({
        totalGuests: data.total_guests || 0,
        newGuestsThisPeriod: data.new_guests || 0,
        returningGuests: data.returning_guests || 0,
        averageStayDuration: data.avg_stay_duration || 0,
        topNationalities: data.top_nationalities || [],
        guestsByMonth: data.guests_by_month || [],
        averageSpending: data.avg_spending || 0,
      });
    } catch (error) {
      console.error('Failed to generate guest report:', error);
      alert('Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Guest Analytics Reports</h1>
          <p className="text-gray-500">Analyze guest behavior and demographics</p>
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
              <p className="text-sm text-gray-500">Total Guests</p>
              <p className="text-3xl font-bold text-gray-900">{stats.totalGuests}</p>
            </div>
          </Card>

          <Card>
            <div className="space-y-2">
              <p className="text-sm text-gray-500">New Guests</p>
              <p className="text-3xl font-bold text-green-600">{stats.newGuestsThisPeriod}</p>
            </div>
          </Card>

          <Card>
            <div className="space-y-2">
              <p className="text-sm text-gray-500">Returning Guests</p>
              <p className="text-3xl font-bold text-blue-600">{stats.returningGuests}</p>
            </div>
          </Card>

          <Card>
            <div className="space-y-2">
              <p className="text-sm text-gray-500">Avg Stay Duration</p>
              <p className="text-3xl font-bold text-purple-600">{stats.averageStayDuration.toFixed(1)} days</p>
            </div>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Nationalities */}
          <Card>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Guest Nationalities</h3>
            <div className="space-y-3">
              {stats.topNationalities.length > 0 ? (
                stats.topNationalities.map((item, index) => (
                  <div key={index} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-700">{item.country}</span>
                      <span className="font-medium text-gray-900">{item.count} guests</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{
                          width: `${stats.topNationalities.length > 0 ? (item.count / stats.topNationalities[0].count) * 100 : 0}%`,
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

          {/* Guests by Month */}
          <Card>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Guest Arrivals by Month</h3>
            <div className="space-y-3">
              {stats.guestsByMonth.length > 0 ? (
                stats.guestsByMonth.map((item, index) => (
                  <div key={index} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-700">{item.month}</span>
                      <span className="font-medium text-gray-900">{item.count} guests</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-purple-600 h-2 rounded-full"
                        style={{
                          width: `${stats.guestsByMonth.length > 0 ? (item.count / Math.max(...stats.guestsByMonth.map((g) => g.count))) * 100 : 0}%`,
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

        {/* Additional Metrics */}
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Additional Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="border-l-4 border-green-500 pl-4">
              <p className="text-sm text-gray-500">Average Spending per Guest</p>
              <p className="text-2xl font-bold text-gray-900">${stats.averageSpending.toFixed(2)}</p>
            </div>

            <div className="border-l-4 border-blue-500 pl-4">
              <p className="text-sm text-gray-500">Return Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.totalGuests > 0 ? ((stats.returningGuests / stats.totalGuests) * 100).toFixed(1) : 0}%
              </p>
            </div>

            <div className="border-l-4 border-purple-500 pl-4">
              <p className="text-sm text-gray-500">New Guest Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.totalGuests > 0 ? ((stats.newGuestsThisPeriod / stats.totalGuests) * 100).toFixed(1) : 0}%
              </p>
            </div>
          </div>
        </Card>

        {/* Export Options */}
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Export Report</h3>
              <p className="text-sm text-gray-500">Download this report in various formats</p>
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
