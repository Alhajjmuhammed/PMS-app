import React from 'react';
import { View, StyleSheet, FlatList, RefreshControl } from 'react-native';
import { Card, Text, Chip, FAB, Searchbar, SegmentedButtons } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { maintenanceApi } from '../../services/api';
import { useNavigation } from '@react-navigation/native';

export default function MaintenanceListScreen() {
  const navigation = useNavigation<any>();
  const [status, setStatus] = React.useState('OPEN');
  const [search, setSearch] = React.useState('');

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['maintenanceRequests', status],
    queryFn: () => maintenanceApi.getRequests({ status }),
  });

  const requests = data?.data || [];

  const filteredRequests = requests.filter(
    (req: any) =>
      req.title.toLowerCase().includes(search.toLowerCase()) ||
      req.room_number?.toLowerCase().includes(search.toLowerCase())
  );

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'CRITICAL':
        return '#d32f2f';
      case 'HIGH':
        return '#f44336';
      case 'MEDIUM':
        return '#ff9800';
      case 'LOW':
        return '#4caf50';
      default:
        return '#9e9e9e';
    }
  };

  const getStatusColor = (reqStatus: string) => {
    switch (reqStatus) {
      case 'OPEN':
        return '#2196f3';
      case 'ASSIGNED':
        return '#9c27b0';
      case 'IN_PROGRESS':
        return '#ff9800';
      case 'COMPLETED':
        return '#4caf50';
      default:
        return '#9e9e9e';
    }
  };

  const renderRequest = ({ item }: { item: any }) => (
    <Card
      style={styles.card}
      onPress={() => navigation.navigate('MaintenanceRequest', { requestId: item.id })}
    >
      <Card.Content>
        <View style={styles.cardHeader}>
          <Text variant="titleMedium" numberOfLines={1} style={styles.title}>
            {item.title}
          </Text>
          <Chip
            style={{ backgroundColor: getPriorityColor(item.priority) }}
            textStyle={{ color: '#fff' }}
            compact
          >
            {item.priority}
          </Chip>
        </View>

        <Text variant="bodySmall" style={styles.requestNumber}>
          {item.request_number}
        </Text>

        <Text variant="bodyMedium" style={styles.location}>
          {item.room_number ? `Room ${item.room_number}` : item.location}
        </Text>

        <View style={styles.cardFooter}>
          <Chip icon="tag" compact>
            {item.category}
          </Chip>
          <Chip
            style={{ backgroundColor: getStatusColor(item.status) }}
            textStyle={{ color: '#fff' }}
            compact
          >
            {item.status}
          </Chip>
        </View>

        {item.assigned_to_name && (
          <Text variant="bodySmall" style={styles.assigned}>
            Assigned to: {item.assigned_to_name}
          </Text>
        )}
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <View style={styles.filters}>
        <Searchbar
          placeholder="Search requests..."
          onChangeText={setSearch}
          value={search}
          style={styles.searchbar}
        />
        <SegmentedButtons
          value={status}
          onValueChange={setStatus}
          buttons={[
            { value: 'OPEN', label: 'Open' },
            { value: 'IN_PROGRESS', label: 'Active' },
            { value: 'COMPLETED', label: 'Done' },
          ]}
          style={styles.segments}
        />
      </View>

      <FlatList
        data={filteredRequests}
        renderItem={renderRequest}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={isLoading} onRefresh={refetch} />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text>No requests found</Text>
          </View>
        }
      />

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => navigation.navigate('CreateMaintenance')}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  filters: {
    padding: 16,
    backgroundColor: '#fff',
  },
  searchbar: {
    marginBottom: 12,
  },
  segments: {
    marginBottom: 8,
  },
  list: {
    padding: 16,
  },
  card: {
    marginBottom: 12,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    flex: 1,
    marginRight: 8,
  },
  requestNumber: {
    color: '#666',
    marginTop: 4,
  },
  location: {
    marginVertical: 8,
  },
  cardFooter: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 8,
  },
  assigned: {
    color: '#666',
    marginTop: 8,
  },
  empty: {
    padding: 32,
    alignItems: 'center',
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: '#1a73e8',
  },
});
