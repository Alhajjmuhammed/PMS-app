import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Card, Text, Chip, Divider, DataTable, Button } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { posApi } from '../../services/apiServices';
import { useRoute } from '@react-navigation/native';
import { format } from 'date-fns';

export default function OrderDetailScreen() {
  const route = useRoute<any>();
  const { orderId } = route.params;

  const { data, isLoading } = useQuery({
    queryKey: ['posOrder', orderId],
    queryFn: () => posApi.getOrderDetail(orderId),
  });

  if (isLoading || !data) {
    return (
      <View style={styles.loading}>
        <Text>Loading...</Text>
      </View>
    );
  }

  const order = data.data;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING':
        return '#ff9800';
      case 'CONFIRMED':
        return '#2196f3';
      case 'PREPARING':
        return '#9c27b0';
      case 'READY':
        return '#4caf50';
      case 'DELIVERED':
        return '#4caf50';
      case 'CANCELLED':
        return '#f44336';
      default:
        return '#9e9e9e';
    }
  };

  return (
    <ScrollView style={styles.container}>
      {/* Order Header */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.header}>
            <View>
              <Text variant="headlineSmall">{order.order_number}</Text>
              <Text variant="bodySmall" style={styles.subtitle}>
                {format(new Date(order.created_at), 'MMM dd, yyyy HH:mm')}
              </Text>
            </View>
            <Chip
              style={{ backgroundColor: getStatusColor(order.status) }}
              textStyle={{ color: '#fff' }}
            >
              {order.status}
            </Chip>
          </View>

          <Divider style={styles.divider} />

          {order.guest_name && (
            <View style={styles.detailRow}>
              <Text variant="bodyMedium" style={styles.label}>Guest:</Text>
              <Text variant="bodyMedium">{order.guest_name}</Text>
            </View>
          )}

          {order.room_number && (
            <View style={styles.detailRow}>
              <Text variant="bodyMedium" style={styles.label}>Room:</Text>
              <Text variant="bodyMedium">{order.room_number}</Text>
            </View>
          )}

          <View style={styles.detailRow}>
            <Text variant="bodyMedium" style={styles.label}>Order Type:</Text>
            <Text variant="bodyMedium">{order.order_type || 'DINE_IN'}</Text>
          </View>

          {order.table_number && (
            <View style={styles.detailRow}>
              <Text variant="bodyMedium" style={styles.label}>Table:</Text>
              <Text variant="bodyMedium">{order.table_number}</Text>
            </View>
          )}

          {order.staff_name && (
            <View style={styles.detailRow}>
              <Text variant="bodyMedium" style={styles.label}>Served By:</Text>
              <Text variant="bodyMedium">{order.staff_name}</Text>
            </View>
          )}
        </Card.Content>
      </Card>

      {/* Order Items */}
      <Card style={styles.card}>
        <Card.Content>
          <Text variant="titleMedium" style={styles.sectionTitle}>
            Order Items
          </Text>
          <DataTable>
            <DataTable.Header>
              <DataTable.Title>Item</DataTable.Title>
              <DataTable.Title numeric>Qty</DataTable.Title>
              <DataTable.Title numeric>Price</DataTable.Title>
            </DataTable.Header>

            {order.items?.map((item: any, index: number) => (
              <DataTable.Row key={index}>
                <DataTable.Cell>
                  <View>
                    <Text>{item.item_name}</Text>
                    {item.notes && (
                      <Text variant="bodySmall" style={styles.itemNotes}>
                        {item.notes}
                      </Text>
                    )}
                  </View>
                </DataTable.Cell>
                <DataTable.Cell numeric>{item.quantity}</DataTable.Cell>
                <DataTable.Cell numeric>${item.price.toFixed(2)}</DataTable.Cell>
              </DataTable.Row>
            ))}
          </DataTable>

          <Divider style={styles.divider} />

          <View style={styles.totalRow}>
            <Text variant="bodyMedium" style={styles.label}>Subtotal:</Text>
            <Text variant="bodyMedium">${order.subtotal?.toFixed(2) || '0.00'}</Text>
          </View>

          {order.tax_amount > 0 && (
            <View style={styles.totalRow}>
              <Text variant="bodyMedium" style={styles.label}>Tax:</Text>
              <Text variant="bodyMedium">${order.tax_amount.toFixed(2)}</Text>
            </View>
          )}

          {order.service_charge > 0 && (
            <View style={styles.totalRow}>
              <Text variant="bodyMedium" style={styles.label}>Service Charge:</Text>
              <Text variant="bodyMedium">${order.service_charge.toFixed(2)}</Text>
            </View>
          )}

          {order.discount_amount > 0 && (
            <View style={styles.totalRow}>
              <Text variant="bodyMedium" style={styles.label}>Discount:</Text>
              <Text variant="bodyMedium" style={styles.discountAmount}>
                -${order.discount_amount.toFixed(2)}
              </Text>
            </View>
          )}

          <View style={styles.totalRow}>
            <Text variant="titleLarge" style={styles.totalLabel}>Total:</Text>
            <Text variant="titleLarge" style={styles.totalAmount}>
              ${order.total_amount?.toFixed(2) || '0.00'}
            </Text>
          </View>
        </Card.Content>
      </Card>

      {/* Special Instructions */}
      {order.special_instructions && (
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Special Instructions
            </Text>
            <Text variant="bodyMedium">{order.special_instructions}</Text>
          </Card.Content>
        </Card>
      )}

      {/* Actions */}
      {order.status !== 'DELIVERED' && order.status !== 'CANCELLED' && (
        <View style={styles.actions}>
          <Button
            mode="outlined"
            onPress={() => {/* Print order */}}
            icon="printer"
            style={styles.button}
          >
            Print
          </Button>
        </View>
      )}
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
  itemNotes: {
    color: '#666',
    fontStyle: 'italic',
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
    color: '#4caf50',
  },
  discountAmount: {
    color: '#f44336',
  },
  actions: {
    padding: 16,
  },
  button: {
    marginBottom: 8,
  },
});
