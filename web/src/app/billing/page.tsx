'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Table from '@/components/Table';
import Card from '@/components/Card';
import Button from '@/components/Button';
import api from '@/lib/api';
import { format } from 'date-fns';

interface Invoice {
  id: number;
  reservation: any;
  total_amount: number;
  paid_amount: number;
  status: string;
  created_at: string;
}

export default function BillingPage() {
  const router = useRouter();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadInvoices();
  }, [filter]);

  const loadInvoices = async () => {
    try {
      setLoading(true);
      const params = filter !== 'all' ? { status: filter } : {};
      const response = await api.get('/api/v1/billing/invoices/', { params });
      setInvoices(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to load invoices:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      paid: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      partial: 'bg-blue-100 text-blue-800',
      cancelled: 'bg-red-100 text-red-800',
    };
    
    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
        {status.toUpperCase()}
      </span>
    );
  };

  const columns = [
    { header: 'Invoice #', accessor: 'id' as keyof Invoice },
    { 
      header: 'Reservation', 
      accessor: (row: Invoice) => `#${row.reservation?.id || 'N/A'}` 
    },
    { 
      header: 'Guest', 
      accessor: (row: Invoice) => {
        const guest = row.reservation?.guest;
        return guest ? `${guest.first_name} ${guest.last_name}` : 'N/A';
      }
    },
    { 
      header: 'Total', 
      accessor: (row: Invoice) => `$${row.total_amount?.toLocaleString() || 0}` 
    },
    { 
      header: 'Paid', 
      accessor: (row: Invoice) => `$${row.paid_amount?.toLocaleString() || 0}` 
    },
    { 
      header: 'Status', 
      accessor: (row: Invoice) => getStatusBadge(row.status) 
    },
    { 
      header: 'Date', 
      accessor: (row: Invoice) => format(new Date(row.created_at), 'MMM dd, yyyy') 
    },
  ];

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Billing & Invoices</h1>
        </div>

        <Card padding="none">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex gap-2">
              {['all', 'pending', 'paid', 'partial', 'cancelled'].map((status) => (
                <button
                  key={status}
                  onClick={() => setFilter(status)}
                  className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                    filter === status
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {status.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
          
          <Table
            data={invoices}
            columns={columns}
            onRowClick={(row) => router.push(`/billing/${row.id}`)}
            loading={loading}
            emptyMessage="No invoices found"
          />
        </Card>
      </div>
    </Layout>
  );
}
