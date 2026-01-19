import React, { useState } from 'react';
import { View, StyleSheet, FlatList, RefreshControl } from 'react-native';
import { Text, Card, Searchbar, FAB, Chip } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { guestsApi } from '../../services/apiServices';
import { Loading, ErrorMessage } from '../../components';

export default function GuestListScreen({ navigation }: any) {
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const { data: guests, isLoading, error, refetch } = useQuery({
    queryKey: ['guests'],
    queryFn: () => guestsApi.list(),
  });

  const onRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  const filteredGuests = guests?.data?.filter((guest: any) =>
    guest.first_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    guest.last_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    guest.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    guest.phone?.includes(searchQuery)
  ) || [];

  if (isLoading) return <Loading message="Loading guests..." />;
  if (error) return <ErrorMessage message="Failed to load guests" onRetry={refetch} />;

  const renderGuest = ({ item }: any) => (
    <Card 
      style={styles.card} 
      onPress={() => navigation.navigate('GuestDetail', { id: item.id })}
    >
      <Card.Content>
        <View style={styles.cardHeader}>
          <Text variant="titleMedium">{item.full_name || `${item.first_name} ${item.last_name}`}</Text>
          {item.vip_level && (
            <Chip icon="star" style={styles.vipChip}>VIP</Chip>
          )}
        </View>
        
        <Text variant="bodyMedium" style={styles.email}>{item.email}</Text>
        {item.phone && <Text variant="bodySmall" style={styles.phone}>{item.phone}</Text>}
        
        <View style={styles.statsRow}>
          <View style={styles.stat}>
            <Text variant="labelSmall">Total Stays</Text>
            <Text variant="titleMedium">{item.total_stays || 0}</Text>
          </View>
          {item.total_revenue && (
            <View style={styles.stat}>
              <Text variant="labelSmall">Total Revenue</Text>
              <Text variant="titleMedium" style={styles.revenue}>
                ${parseFloat(item.total_revenue).toFixed(2)}
              </Text>
            </View>
          )}
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Searchbar
        placeholder="Search guests..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchbar}
      />

      <FlatList
        data={filteredGuests}
        renderItem={renderGuest}
        keyExtractor={(item) => item.id.toString()}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text variant="bodyLarge">No guests found</Text>
          </View>
        }
      />

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => navigation.navigate('CreateGuest')}
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
  vipChip: {
    backgroundColor: '#ffd700',
  },
  email: {
    color: '#666',
    marginBottom: 4,
  },
  phone: {
    color: '#999',
    marginBottom: 12,
  },
  statsRow: {
    flexDirection: 'row',
    gap: 24,
  },
  stat: {
    flex: 1,
  },
  revenue: {
    color: '#4caf50',
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
