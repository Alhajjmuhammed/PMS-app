import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl, FlatList } from 'react-native';
import { Text, Card, Searchbar, Chip, FAB, Button, SegmentedButtons } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { reservationsApi } from '../../services/apiServices';
import { Loading, ErrorMessage } from '../../components';

export default function ReservationListScreen({ navigation }: any) {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [refreshing, setRefreshing] = useState(false);

  const { data: reservations, isLoading, error, refetch } = useQuery({
    queryKey: ['reservations', statusFilter !== 'all' ? { status: statusFilter } : {}],
    queryFn: () => reservationsApi.list(statusFilter !== 'all' ? { status: statusFilter } : {}),
  });

  const onRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  const filteredReservations = reservations?.data?.filter((res: any) =>
    res.guest_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    res.confirmation_number?.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  const getStatusColor = (status: string) => {
    const colors: any = {
      PENDING: '#ff9800',
      CONFIRMED: '#2196f3',
      CHECKED_IN: '#4caf50',
      CHECKED_OUT: '#9e9e9e',
      CANCELLED: '#f44336',
      NO_SHOW: '#e91e63',
    };
    return colors[status] || '#9e9e9e';
  };

  if (isLoading) return <Loading message="Loading reservations..." />;
  if (error) return <ErrorMessage message="Failed to load reservations" onRetry={refetch} />;

  const renderReservation = ({ item }: any) => (
    <Card 
      style={styles.card} 
      onPress={() => navigation.navigate('ReservationDetail', { id: item.id })}
    >
      <Card.Content>
        <View style={styles.cardHeader}>
          <Text variant="titleMedium">{item.guest_name || 'Guest'}</Text>
          <Chip 
            style={{ backgroundColor: getStatusColor(item.status) }}
            textStyle={{ color: 'white' }}
          >
            {item.status}
          </Chip>
        </View>
        
        <Text variant="bodyMedium" style={styles.confirmationNumber}>
          #{item.confirmation_number}
        </Text>
        
        <View style={styles.dateRow}>
          <Text variant="bodySmall" style={styles.dateText}>
            Check-in: {item.check_in_date}
          </Text>
          <Text variant="bodySmall" style={styles.dateText}>
            Check-out: {item.check_out_date}
          </Text>
        </View>
        
        <View style={styles.detailRow}>
          <Text variant="bodySmall">Adults: {item.adults}</Text>
          {item.children > 0 && <Text variant="bodySmall">Children: {item.children}</Text>}
          <Text variant="bodySmall">Nights: {item.nights || 0}</Text>
        </View>

        {item.total_amount && (
          <Text variant="titleSmall" style={styles.amount}>
            ${parseFloat(item.total_amount).toFixed(2)}
          </Text>
        )}
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Searchbar
        placeholder="Search by name or confirmation..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchbar}
      />

      <SegmentedButtons
        value={statusFilter}
        onValueChange={setStatusFilter}
        buttons={[
          { value: 'all', label: 'All' },
          { value: 'CONFIRMED', label: 'Confirmed' },
          { value: 'CHECKED_IN', label: 'In-House' },
        ]}
        style={styles.segmented}
      />

      <FlatList
        data={filteredReservations}
        renderItem={renderReservation}
        keyExtractor={(item) => item.id.toString()}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text variant="bodyLarge">No reservations found</Text>
          </View>
        }
      />

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => navigation.navigate('CreateReservation')}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  searchbar: {
    margin: 16,
    marginBottom: 8,
  },
  segmented: {
    marginHorizontal: 16,
    marginBottom: 16,
  },
  card: {
    marginHorizontal: 16,
    marginBottom: 12,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  confirmationNumber: {
    color: '#666',
    marginBottom: 8,
  },
  dateRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  dateText: {
    color: '#666',
  },
  detailRow: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 8,
  },
  amount: {
    color: '#4caf50',
    fontWeight: 'bold',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: '#1a73e8',
  },
});
