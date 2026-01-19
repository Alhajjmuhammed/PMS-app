import React from 'react';
import { View, StyleSheet, FlatList, RefreshControl } from 'react-native';
import { Card, Text, Chip, FAB, Searchbar, SegmentedButtons } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { housekeepingApi } from '../../services/api';
import { useNavigation } from '@react-navigation/native';

export default function HousekeepingListScreen() {
  const navigation = useNavigation<any>();
  const [status, setStatus] = React.useState('PENDING');
  const [search, setSearch] = React.useState('');

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['housekeepingTasks', status],
    queryFn: () => housekeepingApi.getTasks({ status }),
  });

  const tasks = data?.data || [];

  const filteredTasks = tasks.filter((task: any) =>
    task.room_number.toLowerCase().includes(search.toLowerCase())
  );

  const getStatusColor = (taskStatus: string) => {
    switch (taskStatus) {
      case 'PENDING':
        return '#ff9800';
      case 'IN_PROGRESS':
        return '#2196f3';
      case 'COMPLETED':
        return '#4caf50';
      default:
        return '#9e9e9e';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'HIGH':
        return '#f44336';
      case 'RUSH':
        return '#ff5722';
      default:
        return undefined;
    }
  };

  const renderTask = ({ item }: { item: any }) => (
    <Card
      style={styles.card}
      onPress={() => navigation.navigate('HousekeepingTask', { taskId: item.id })}
    >
      <Card.Content>
        <View style={styles.cardHeader}>
          <Text variant="titleLarge">Room {item.room_number}</Text>
          <Chip
            style={{ backgroundColor: getStatusColor(item.status) }}
            textStyle={{ color: '#fff' }}
          >
            {item.status}
          </Chip>
        </View>
        <Text variant="bodyMedium" style={styles.roomType}>
          {item.room_type}
        </Text>
        <View style={styles.cardFooter}>
          <Chip icon="broom" compact>
            {item.task_type}
          </Chip>
          {item.priority !== 'NORMAL' && (
            <Chip
              icon="alert"
              compact
              style={{ backgroundColor: getPriorityColor(item.priority) }}
              textStyle={{ color: '#fff' }}
            >
              {item.priority}
            </Chip>
          )}
        </View>
        {item.special_instructions && (
          <Text variant="bodySmall" style={styles.instructions}>
            {item.special_instructions}
          </Text>
        )}
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <View style={styles.filters}>
        <Searchbar
          placeholder="Search room..."
          onChangeText={setSearch}
          value={search}
          style={styles.searchbar}
        />
        <SegmentedButtons
          value={status}
          onValueChange={setStatus}
          buttons={[
            { value: 'PENDING', label: 'Pending' },
            { value: 'IN_PROGRESS', label: 'In Progress' },
            { value: 'COMPLETED', label: 'Done' },
          ]}
          style={styles.segments}
        />
      </View>

      <FlatList
        data={filteredTasks}
        renderItem={renderTask}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={isLoading} onRefresh={refetch} />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Text>No tasks found</Text>
          </View>
        }
      />

      <FAB
        icon="floor-plan"
        style={styles.fab}
        onPress={() => navigation.navigate('RoomStatus')}
        label="Room Status"
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
  roomType: {
    color: '#666',
    marginVertical: 4,
  },
  cardFooter: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 8,
  },
  instructions: {
    marginTop: 8,
    color: '#ff9800',
    fontStyle: 'italic',
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
  },
});
