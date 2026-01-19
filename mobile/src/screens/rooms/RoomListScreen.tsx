import React, { useState } from 'react';
import { View, StyleSheet, FlatList, RefreshControl } from 'react-native';
import { Text, Card, Searchbar, Chip, SegmentedButtons } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { roomsApi } from '../../services/apiServices';
import { Loading, ErrorMessage } from '../../components';

export default function RoomListScreen({ navigation }: any) {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [refreshing, setRefreshing] = useState(false);

  const { data: rooms, isLoading, error, refetch } = useQuery({
    queryKey: ['rooms', statusFilter !== 'all' ? { status: statusFilter } : {}],
    queryFn: () => roomsApi.list(statusFilter !== 'all' ? { status: statusFilter } : {}),
  });

  const onRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  const filteredRooms = rooms?.data?.filter((room: any) =>
    room.number?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    room.room_type_name?.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  const getStatusColor = (status: string) => {
    const colors: any = {
      VACANT_CLEAN: '#4caf50',
      VACANT_DIRTY: '#ff9800',
      OCCUPIED_CLEAN: '#2196f3',
      OCCUPIED_DIRTY: '#9c27b0',
      OUT_OF_ORDER: '#f44336',
      OUT_OF_SERVICE: '#e91e63',
    };
    return colors[status] || '#9e9e9e';
  };

  if (isLoading) return <Loading message="Loading rooms..." />;
  if (error) return <ErrorMessage message="Failed to load rooms" onRetry={refetch} />;

  const renderRoom = ({ item }: any) => (
    <Card 
      style={styles.card}
      onPress={() => navigation.navigate('RoomDetail', { id: item.id })}
    >
      <Card.Content>
        <View style={styles.header}>
          <Text variant="titleLarge">{item.number}</Text>
          <Chip 
            style={{ backgroundColor: getStatusColor(item.status) }}
            textStyle={{ color: 'white' }}
          >
            {item.status?.replace(/_/g, ' ')}
          </Chip>
        </View>
        
        <Text variant="titleMedium" style={styles.roomType}>
          {item.room_type_name || 'Standard Room'}
        </Text>
        
        <View style={styles.detailRow}>
          <Text variant="bodySmall">Floor: {item.floor || 'N/A'}</Text>
          <Text variant="bodySmall">Max: {item.max_occupancy || 0} guests</Text>
        </View>

        {item.fo_status && (
          <Chip 
            icon="information"
            style={styles.foChip}
            textStyle={{ fontSize: 12 }}
          >
            FO: {item.fo_status.replace(/_/g, ' ')}
          </Chip>
        )}
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Searchbar
        placeholder="Search rooms..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchbar}
      />

      <SegmentedButtons
        value={statusFilter}
        onValueChange={setStatusFilter}
        buttons={[
          { value: 'all', label: 'All' },
          { value: 'VACANT_CLEAN', label: 'Available' },
          { value: 'OCCUPIED_CLEAN', label: 'Occupied' },
        ]}
        style={styles.segmented}
      />

      <FlatList
        data={filteredRooms}
        renderItem={renderRoom}
        keyExtractor={(item) => item.id.toString()}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        numColumns={2}
        columnWrapperStyle={styles.row}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text variant="bodyLarge">No rooms found</Text>
          </View>
        }
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
  row: {
    justifyContent: 'space-between',
    paddingHorizontal: 16,
  },
  card: {
    flex: 1,
    marginBottom: 12,
    marginHorizontal: 4,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  roomType: {
    color: '#666',
    marginBottom: 8,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  foChip: {
    backgroundColor: '#e3f2fd',
    marginTop: 4,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
});
