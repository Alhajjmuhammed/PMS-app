import React, { useState } from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { Card, Text, Chip, Searchbar, FAB } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { posApi } from '../../services/apiServices';
import { useNavigation } from '@react-navigation/native';
import { format } from 'date-fns';

export default function OrderHistoryScreen() {
  const navigation = useNavigation();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['posOrders', searchQuery, statusFilter],
    queryFn: async () => {
      const params: any = {};
      if (searchQuery) params.search = searchQuery;
      if (statusFilter !== 'all') params.status = statusFilter;
      const response = await posApi.listOrders(params);
      return response.data;
    },
  });

  const orders = data?.results || [];

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

  const renderOrder = ({ item }: any) => (
    <Card
      style={styles.card}
      onPress={() => (navigation as any).navigate('OrderDetailScreen', { orderId: item.id })}
    >
      <Card.Content>
        <View style={styles.orderHeader}>
          <View style={styles.orderInfo}>
            <Text variant="titleMedium">{item.order_number}</Text>
            <Text variant="bodySmall" style={styles.orderDate}>
              {format(new Date(item.created_at), 'MMM dd, yyyy HH:mm')}
            </Text>
          </View>
          <Chip
            style={{ backgroundColor: getStatusColor(item.status) }}
            textStyle={{ color: '#fff' }}
          >
            {item.status}
          </Chip>
        </View>

        {item.guest_name && (
          <Text variant="bodyMedium" style={styles.guestName}>
            {item.guest_name} - Room {item.room_number}
          </Text>
        )}

        <View style={styles.orderDetails}>
          <Text variant="bodySmall" style={styles.itemCount}>
            {item.items_count || 0} items
          </Text>
          <Text variant="titleMedium" style={styles.totalAmount}>
            ${item.total_amount?.toFixed(2) || '0.00'}
          </Text>
        </View>
      </Card.Content>
    </Card>
  );

  if (isLoading) {
    return (
      <View style={styles.loading}>
        <Text>Loading orders...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Searchbar
        placeholder="Search orders..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchbar}
      />

      <View style={styles.filters}>
        <Chip
          selected={statusFilter === 'all'}
          onPress={() => setStatusFilter('all')}
          style={styles.filterChip}
        >
          All
        </Chip>
        <Chip
          selected={statusFilter === 'PENDING'}
          onPress={() => setStatusFilter('PENDING')}
          style={styles.filterChip}
        >
          Pending
        </Chip>
        <Chip
          selected={statusFilter === 'PREPARING'}
          onPress={() => setStatusFilter('PREPARING')}
          style={styles.filterChip}
        >
          Preparing
        </Chip>
        <Chip
          selected={statusFilter === 'DELIVERED'}
          onPress={() => setStatusFilter('DELIVERED')}
          style={styles.filterChip}
        >
          Delivered
        </Chip>
      </View>

      <FlatList
        data={orders}
        renderItem={renderOrder}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContent}
        refreshing={isLoading}
        onRefresh={refetch}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text variant="bodyLarge" style={styles.emptyText}>
              No orders found
            </Text>
          </View>
        }
      />

      <FAB
        style={styles.fab}
        icon="plus"
        onPress={() => navigation.navigate('POSScreen' as never)}
        label="New Order"
      />
    </View>
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
  searchbar: {
    margin: 16,
    marginBottom: 8,
  },
  filters: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingBottom: 8,
    gap: 8,
  },
  filterChip: {
    marginRight: 4,
  },
  listContent: {
    padding: 16,
    paddingTop: 8,
  },
  card: {
    marginBottom: 12,
  },
  orderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  orderInfo: {
    flex: 1,
  },
  orderDate: {
    color: '#666',
    marginTop: 4,
  },
  guestName: {
    color: '#2196f3',
    marginBottom: 8,
  },
  orderDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
  },
  itemCount: {
    color: '#666',
  },
  totalAmount: {
    color: '#4caf50',
    fontWeight: '600',
  },
  emptyContainer: {
    padding: 32,
    alignItems: 'center',
  },
  emptyText: {
    color: '#666',
  },
  fab: {
    position: 'absolute',
    right: 16,
    bottom: 16,
  },
});
