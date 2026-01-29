import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Card, Text, Button, Chip, Divider, DataTable } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { billingApi } from '../../services/apiServices';
import { useNavigation, useRoute } from '@react-navigation/native';
import { format } from 'date-fns';

export default function InvoiceDetailScreen() {
  const navigation = useNavigation();
  const route = useRoute<any>();
  const { invoiceId } = route.params;

  const { data, isLoading } = useQuery({
    queryKey: ['invoice', invoiceId],
    queryFn: () => billingApi.getInvoiceDetail(invoiceId),
  });

  if (isLoading || !data) {
    return (
      <View style={styles.loading}>
        <Text>Loading...</Text>
      </View>
    );
  }

  const invoice = data.data;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PAID':
        return '#4caf50';
      case 'ISSUED':
        return '#2196f3';
      case 'OVERDUE':
        return '#f44336';
      case 'DRAFT':
        return '#ff9800';
      case 'CANCELLED':
        return '#9e9e9e';
      default:
        return '#757575';
    }
  };

  return (
    <ScrollView style={styles.container}>
      {/* Invoice Header */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.header}>
            <View>
              <Text variant="headlineSmall">{invoice.invoice_number}</Text>
              <Text variant="bodySmall" style={styles.subtitle}>
                {invoice.guest_name}
              </Text>
            </View>
            <Chip
              style={{ backgroundColor: getStatusColor(invoice.status) }}
              textStyle={{ color: '#fff' }}
            >
              {invoice.status}
            </Chip>
          </View>

          <Divider style={styles.divider} />

          <View style={styles.detailRow}>
            <Text variant="bodyMedium" style={styles.label}>Issue Date:</Text>
            <Text variant="bodyMedium">
              {format(new Date(invoice.issue_date), 'MMM dd, yyyy')}
            </Text>
          </View>

          <View style={styles.detailRow}>
            <Text variant="bodyMedium" style={styles.label}>Due Date:</Text>
            <Text variant="bodyMedium">
              {format(new Date(invoice.due_date), 'MMM dd, yyyy')}
            </Text>
          </View>

          {invoice.reservation && (
            <View style={styles.detailRow}>
              <Text variant="bodyMedium" style={styles.label}>Reservation:</Text>
              <Text variant="bodyMedium">{invoice.reservation}</Text>
            </View>
          )}
        </Card.Content>
      </Card>

      {/* Line Items */}
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.sectionTitle}>
            Line Items
          </Text>
          <DataTable>
            <DataTable.Header>
              <DataTable.Title>Description</DataTable.Title>
              <DataTable.Title numeric>Qty</DataTable.Title>
              <DataTable.Title numeric>Amount</DataTable.Title>
            </DataTable.Header>

            {invoice.line_items?.map((item: any, index: number) => (
              <DataTable.Row key={index}>
                <DataTable.Cell>{item.description}</DataTable.Cell>
                <DataTable.Cell numeric>{item.quantity}</DataTable.Cell>
                <DataTable.Cell numeric>${item.amount.toFixed(2)}</DataTable.Cell>
              </DataTable.Row>
            ))}
          </DataTable>

          <Divider style={styles.divider} />

          <View style={styles.totalRow}>
            <Text variant="bodyMedium" style={styles.label}>Subtotal:</Text>
            <Text variant="bodyMedium">${invoice.subtotal?.toFixed(2)}</Text>
          </View>

          {invoice.tax_amount > 0 && (
            <View style={styles.totalRow}>
              <Text variant="bodyMedium" style={styles.label}>Tax:</Text>
              <Text variant="bodyMedium">${invoice.tax_amount.toFixed(2)}</Text>
            </View>
          )}

          <View style={styles.totalRow}>
            <Text variant="titleLarge" style={styles.totalLabel}>Total:</Text>
            <Text variant="titleLarge" style={styles.totalAmount}>
              ${invoice.total_amount.toFixed(2)}
            </Text>
          </View>

          {invoice.paid_amount > 0 && (
            <>
              <View style={styles.totalRow}>
                <Text variant="bodyMedium" style={styles.label}>Paid:</Text>
                <Text variant="bodyMedium" style={styles.paidAmount}>
                  ${invoice.paid_amount.toFixed(2)}
                </Text>
              </View>
              <View style={styles.totalRow}>
                <Text variant="titleMedium" style={styles.label}>Balance Due:</Text>
                <Text variant="titleMedium" style={styles.balanceAmount}>
                  ${(invoice.total_amount - invoice.paid_amount).toFixed(2)}
                </Text>
              </View>
            </>
          )}
        </Card.Content>
      </Card>

      {/* Payment History */}
      {invoice.payments && invoice.payments.length > 0 && (
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Payment History
            </Text>
            {invoice.payments.map((payment: any, index: number) => (
              <View key={index} style={styles.paymentItem}>
                <View style={styles.paymentHeader}>
                  <Text variant="bodyMedium">{payment.payment_method}</Text>
                  <Text variant="bodyMedium" style={styles.paymentAmount}>
                    ${payment.amount.toFixed(2)}
                  </Text>
                </View>
                <Text variant="bodySmall" style={styles.paymentDate}>
                  {format(new Date(payment.payment_date), 'MMM dd, yyyy HH:mm')}
                </Text>
                {payment.reference && (
                  <Text variant="bodySmall" style={styles.paymentRef}>
                    Ref: {payment.reference}
                  </Text>
                )}
              </View>
            ))}
          </Card.Content>
        </Card>
      )}

      {/* Actions */}
      <View style={styles.actions}>
        {invoice.status !== 'PAID' && invoice.status !== 'CANCELLED' && (
          <Button
            mode="contained"
            onPress={() => (navigation as any).navigate('PaymentScreen', { invoiceId })}
            icon="credit-card"
            style={styles.button}
          >
            Record Payment
          </Button>
        )}
        <Button
          mode="outlined"
          onPress={() => {/* Download/Share PDF */}}
          icon="download"
          style={styles.button}
        >
          Download PDF
        </Button>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  card: {
    margin: 16,
    marginBottom: 8,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  subtitle: {
    color: '#666',
    marginTop: 4,
  },
  divider: {
    marginVertical: 16,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  label: {
    color: '#666',
  },
  sectionTitle: {
    marginBottom: 12,
    fontWeight: '600',
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
  },
  totalLabel: {
    fontWeight: 'bold',
  },
  totalAmount: {
    fontWeight: 'bold',
    color: '#2196f3',
  },
  paidAmount: {
    color: '#4caf50',
  },
  balanceAmount: {
    color: '#f44336',
    fontWeight: '600',
  },
  paymentItem: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  paymentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  paymentAmount: {
    color: '#4caf50',
    fontWeight: '600',
  },
  paymentDate: {
    color: '#666',
  },
  paymentRef: {
    color: '#999',
    fontSize: 12,
  },
  actions: {
    padding: 16,
    gap: 8,
  },
  button: {
    marginBottom: 8,
  },
});
