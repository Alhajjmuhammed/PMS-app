import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Text, Card, Button, Chip, DataTable, Portal, Modal } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { billingApi } from '../services/apiServices';
import { Loading, ErrorMessage } from '../components';

export default function BillingScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState<any>(null);
  
  const { data: invoices, isLoading, error, refetch } = useQuery({
    queryKey: ['invoices'],
    queryFn: () => billingApi.invoices.list(),
  });

  const onRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  const getStatusColor = (status: string) => {
    const colors: any = {
      PAID: '#4caf50',
      ISSUED: '#2196f3',
      OVERDUE: '#f44336',
      DRAFT: '#9e9e9e',
      CANCELLED: '#757575',
    };
    return colors[status] || '#9e9e9e';
  };

  if (isLoading) return <Loading message="Loading invoices..." />;
  if (error) return <ErrorMessage message="Failed to load invoices" onRetry={refetch} />;

  return (
    <View style={styles.container}>
      <ScrollView
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Summary Cards */}
        <View style={styles.summaryContainer}>
          <Card style={styles.summaryCard}>
            <Card.Content>
              <Text variant="titleSmall">Total Due</Text>
              <Text variant="headlineMedium" style={styles.amount}>
                ${invoices?.data?.reduce((sum: number, inv: any) => 
                  sum + parseFloat(inv.balance || 0), 0).toFixed(2)}
              </Text>
            </Card.Content>
          </Card>
          
          <Card style={styles.summaryCard}>
            <Card.Content>
              <Text variant="titleSmall">Paid Today</Text>
              <Text variant="headlineMedium" style={[styles.amount, styles.successText]}>
                $0.00
              </Text>
            </Card.Content>
          </Card>
        </View>

        {/* Invoices List */}
        <Card style={styles.card}>
          <Card.Title title="Recent Invoices" />
          <Card.Content>
            <DataTable>
              <DataTable.Header>
                <DataTable.Title>Invoice #</DataTable.Title>
                <DataTable.Title>Guest</DataTable.Title>
                <DataTable.Title numeric>Amount</DataTable.Title>
                <DataTable.Title>Status</DataTable.Title>
              </DataTable.Header>

              {invoices?.data?.results?.slice(0, 10).map((invoice: any) => (
                <DataTable.Row 
                  key={invoice.id}
                  onPress={() => setSelectedInvoice(invoice)}
                >
                  <DataTable.Cell>{invoice.invoice_number}</DataTable.Cell>
                  <DataTable.Cell>{invoice.guest_name}</DataTable.Cell>
                  <DataTable.Cell numeric>${invoice.total_amount}</DataTable.Cell>
                  <DataTable.Cell>
                    <Chip 
                      style={{ backgroundColor: getStatusColor(invoice.status) }}
                      textStyle={{ color: 'white', fontSize: 10 }}
                    >
                      {invoice.status}
                    </Chip>
                  </DataTable.Cell>
                </DataTable.Row>
              ))}
            </DataTable>
          </Card.Content>
        </Card>
      </ScrollView>

      {/* Invoice Detail Modal */}
      <Portal>
        <Modal
          visible={!!selectedInvoice}
          onDismiss={() => setSelectedInvoice(null)}
          contentContainerStyle={styles.modal}
        >
          {selectedInvoice && (
            <Card>
              <Card.Title title={`Invoice ${selectedInvoice.invoice_number}`} />
              <Card.Content>
                <Text variant="bodyLarge">Guest: {selectedInvoice.guest_name}</Text>
                <Text>Issue Date: {selectedInvoice.issue_date}</Text>
                <Text>Due Date: {selectedInvoice.due_date}</Text>
                <View style={styles.divider} />
                <Text variant="titleMedium">Amount: ${selectedInvoice.total_amount}</Text>
                <Text>Paid: ${selectedInvoice.paid_amount}</Text>
                <Text style={styles.balanceText}>
                  Balance: ${selectedInvoice.balance}
                </Text>
              </Card.Content>
              <Card.Actions>
                <Button onPress={() => setSelectedInvoice(null)}>Close</Button>
                <Button mode="contained">Process Payment</Button>
              </Card.Actions>
            </Card>
          )}
        </Modal>
      </Portal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  summaryContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  summaryCard: {
    flex: 1,
  },
  amount: {
    marginTop: 8,
    fontWeight: 'bold',
  },
  successText: {
    color: '#4caf50',
  },
  card: {
    margin: 16,
    marginTop: 0,
  },
  modal: {
    backgroundColor: 'white',
    padding: 20,
    margin: 20,
  },
  divider: {
    height: 1,
    backgroundColor: '#e0e0e0',
    marginVertical: 12,
  },
  balanceText: {
    color: '#f44336',
    fontWeight: 'bold',
    marginTop: 4,
  },
});
