'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Input from '@/components/Input';
import Button from '@/components/Button';
import api from '@/lib/api';

interface Invoice {
  id: number;
  invoice_number: string;
  guest: {
    first_name: string;
    last_name: string;
  };
  total: number;
  paid_amount: number;
  balance_due: number;
}

export default function PaymentProcessingPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const invoiceId = searchParams.get('invoice_id');

  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    amount: '',
    payment_method: 'cash',
    card_number: '',
    card_holder: '',
    expiry_date: '',
    cvv: '',
    notes: '',
  });

  useEffect(() => {
    if (invoiceId) {
      loadInvoice(parseInt(invoiceId));
    }
  }, [invoiceId]);

  const loadInvoice = async (id: number) => {
    try {
      const response = await api.get(`/billing/invoices/${id}/`);
      setInvoice(response.data);
      setFormData({ ...formData, amount: response.data.balance_due.toFixed(2) });
    } catch (error) {
      console.error('Failed to load invoice:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const paymentData: any = {
        invoice: invoice?.id,
        amount: parseFloat(formData.amount),
        payment_method: formData.payment_method,
        notes: formData.notes,
      };

      // Add card details if card payment
      if (formData.payment_method === 'credit_card' || formData.payment_method === 'debit_card') {
        paymentData.card_last_four = formData.card_number.slice(-4);
        paymentData.card_holder_name = formData.card_holder;
      }

      await api.post('/billing/payments/', paymentData);

      alert('Payment processed successfully!');
      
      if (invoice) {
        router.push(`/billing/${invoice.id}`);
      } else {
        router.push('/billing');
      }
    } catch (error) {
      console.error('Failed to process payment:', error);
      alert('Payment processing failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const paymentMethods = [
    { value: 'cash', label: 'Cash' },
    { value: 'credit_card', label: 'Credit Card' },
    { value: 'debit_card', label: 'Debit Card' },
    { value: 'bank_transfer', label: 'Bank Transfer' },
    { value: 'check', label: 'Check' },
    { value: 'mobile_payment', label: 'Mobile Payment' },
  ];

  const showCardFields = formData.payment_method === 'credit_card' || formData.payment_method === 'debit_card';

  return (
    <Layout>
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Process Payment</h1>
          <p className="text-gray-500">Record a payment for an invoice</p>
        </div>

        {/* Invoice Summary */}
        {invoice && (
          <Card>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Invoice Details</h2>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Invoice Number</span>
                <span className="font-medium text-gray-900">{invoice.invoice_number}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Guest</span>
                <span className="font-medium text-gray-900">
                  {invoice.guest.first_name} {invoice.guest.last_name}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total Amount</span>
                <span className="font-medium text-gray-900">${invoice.total.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Paid Amount</span>
                <span className="font-medium text-green-600">${invoice.paid_amount.toFixed(2)}</span>
              </div>
              <div className="flex justify-between border-t pt-2">
                <span className="text-gray-900 font-semibold">Balance Due</span>
                <span className="font-bold text-red-600">${invoice.balance_due.toFixed(2)}</span>
              </div>
            </div>
          </Card>
        )}

        {/* Payment Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <Card>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Payment Information</h2>

            <div className="space-y-4">
              <Input
                label="Payment Amount"
                type="number"
                step="0.01"
                min="0.01"
                max={invoice?.balance_due || undefined}
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                required
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Payment Method</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={formData.payment_method}
                  onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                  required
                >
                  {paymentMethods.map((method) => (
                    <option key={method.value} value={method.value}>
                      {method.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Card Details (shown only for card payments) */}
              {showCardFields && (
                <div className="border-t pt-4 space-y-4">
                  <h3 className="text-md font-medium text-gray-900">Card Details</h3>

                  <Input
                    label="Card Number"
                    type="text"
                    pattern="[0-9]{13,19}"
                    maxLength={19}
                    placeholder="1234 5678 9012 3456"
                    value={formData.card_number}
                    onChange={(e) => setFormData({ ...formData, card_number: e.target.value })}
                    required
                  />

                  <Input
                    label="Cardholder Name"
                    type="text"
                    placeholder="John Doe"
                    value={formData.card_holder}
                    onChange={(e) => setFormData({ ...formData, card_holder: e.target.value })}
                    required
                  />

                  <div className="grid grid-cols-2 gap-4">
                    <Input
                      label="Expiry Date"
                      type="text"
                      pattern="(0[1-9]|1[0-2])\/[0-9]{2}"
                      placeholder="MM/YY"
                      maxLength={5}
                      value={formData.expiry_date}
                      onChange={(e) => {
                        let value = e.target.value.replace(/\D/g, '');
                        if (value.length >= 2) {
                          value = value.slice(0, 2) + '/' + value.slice(2, 4);
                        }
                        setFormData({ ...formData, expiry_date: value });
                      }}
                      required
                    />

                    <Input
                      label="CVV"
                      type="text"
                      pattern="[0-9]{3,4}"
                      maxLength={4}
                      placeholder="123"
                      value={formData.cvv}
                      onChange={(e) => setFormData({ ...formData, cvv: e.target.value.replace(/\D/g, '') })}
                      required
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Payment reference or additional notes..."
                />
              </div>
            </div>
          </Card>

          {/* Security Notice */}
          {showCardFields && (
            <Card>
              <div className="flex items-start gap-3">
                <span className="text-2xl">🔒</span>
                <div>
                  <h3 className="font-semibold text-gray-900">Secure Payment</h3>
                  <p className="text-sm text-gray-600">
                    Your payment information is encrypted and secure. We do not store complete card details.
                  </p>
                </div>
              </div>
            </Card>
          )}

          {/* Actions */}
          <div className="flex gap-4">
            <Button type="submit" disabled={loading}>
              {loading ? 'Processing...' : `Process Payment ($${formData.amount || '0.00'})`}
            </Button>
            <Button type="button" variant="outline" onClick={() => router.back()}>
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </Layout>
  );
}
