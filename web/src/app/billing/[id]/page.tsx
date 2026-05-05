'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import api from '@/lib/api';
import { format } from 'date-fns';

export default function InvoiceDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [invoice, setInvoice] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (params.id) {
      loadInvoice();
    }
  }, [params.id]);

  const loadInvoice = async () => {
    try {
      const response = await api.get(`/api/v1/billing/invoices/${params.id}/`);
      setInvoice(response.data);
    } catch (error) {
      alert('Failed to load invoice');
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
      <span className={`px-3 py-1 text-sm font-semibold rounded-full ${colors[status as keyof typeof colors]}`}>
        {status.toUpperCase()}
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
          <h1 className="text-3xl font-bold text-gray-900">Invoice #{invoice?.id}</h1>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => window.print()}>
              Print
            </Button>
            <Button variant="secondary" onClick={() => router.back()}>
              Back
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="Invoice Information">
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Invoice Number</dt>
                <dd className="mt-1 text-lg font-semibold text-gray-900">#{invoice?.id}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Status</dt>
                <dd className="mt-1">{getStatusBadge(invoice?.status)}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Issue Date</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {invoice?.created_at ? format(new Date(invoice.created_at), 'PPP') : 'N/A'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Due Date</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {invoice?.due_date ? format(new Date(invoice.due_date), 'PPP') : 'N/A'}
                </dd>
              </div>
            </dl>
          </Card>

          <Card title="Customer Information">
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Guest Name</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {invoice?.reservation?.guest
                    ? `${invoice.reservation.guest.first_name} ${invoice.reservation.guest.last_name}`
                    : 'N/A'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Email</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {invoice?.reservation?.guest?.email || 'N/A'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Reservation</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  #{invoice?.reservation?.id || 'N/A'}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Room</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {invoice?.reservation?.room?.number || 'N/A'}
                </dd>
              </div>
            </dl>
          </Card>
        </div>

        <Card title="Line Items">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Description
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Quantity
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Unit Price
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Amount
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {invoice?.line_items?.map((item: any, idx: number) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 text-sm text-gray-900">{item.description}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 text-right">{item.quantity}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 text-right">
                      ${item.unit_price?.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 text-right">
                      ${item.amount?.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card>
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Subtotal:</span>
              <span className="text-gray-900">${invoice?.subtotal?.toLocaleString() || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Tax:</span>
              <span className="text-gray-900">${invoice?.tax_amount?.toLocaleString() || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Discount:</span>
              <span className="text-gray-900">-${invoice?.discount_amount?.toLocaleString() || 0}</span>
            </div>
            <div className="border-t pt-3 flex justify-between text-lg font-bold">
              <span>Total:</span>
              <span className="text-primary-600">${invoice?.total_amount?.toLocaleString() || 0}</span>
            </div>
            <div className="flex justify-between text-base font-semibold">
              <span className="text-gray-500">Paid:</span>
              <span className="text-green-600">${invoice?.paid_amount?.toLocaleString() || 0}</span>
            </div>
            <div className="flex justify-between text-lg font-bold">
              <span className="text-red-600">Balance Due:</span>
              <span className="text-red-600">
                ${((invoice?.total_amount || 0) - (invoice?.paid_amount || 0)).toLocaleString()}
              </span>
            </div>
          </div>
        </Card>

        {invoice?.status !== 'paid' && invoice?.status !== 'cancelled' && (
          <Card title="Payment">
            <div className="flex gap-3">
              <Button onClick={() => router.push(`/billing/${params.id}/pay`)}>
                Record Payment
              </Button>
              <Button variant="secondary">
                Send Invoice
              </Button>
            </div>
          </Card>
        )}
      </div>
    </Layout>
  );
}
