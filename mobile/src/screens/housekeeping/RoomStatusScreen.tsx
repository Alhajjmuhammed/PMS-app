import React from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Card, Text, Chip, SegmentedButtons } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { housekeepingApi } from '../../services/api';

export default function RoomStatusScreen() {
  const [floor, setFloor] = React.useState('all');

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['roomStatus', floor],
    queryFn: () => housekeepingApi.getRoomStatus(floor !== 'all' ? parseInt(floor) : undefined),
  });

  const rooms = data?.data?.rooms || [];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'VC':
        return '#4caf50'; // Vacant Clean - Green
      case 'VD':
        return '#ff9800'; // Vacant Dirty - Orange
      case 'OC':
        return '#2196f3'; // Occupied Clean - Blue
      case 'OD':
        return '#9c27b0'; // Occupied Dirty - Purple
      case 'OOO':
        return '#f44336'; // Out of Order - Red
      case 'OOS':
        return '#795548'; // Out of Service - Brown
      default:
        return '#9e9e9e';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'VC':
        return 'Vacant Clean';
      case 'VD':
        return 'Vacant Dirty';
      case 'OC':
        return 'Occupied Clean';
      case 'OD':
        return 'Occupied Dirty';
      case 'OOO':
        return 'Out of Order';
      case 'OOS':
        return 'Out of Service';
      default:
        return status;
    }
  };

  // Group rooms by status for summary
  const statusSummary = rooms.reduce((acc: any, room: any) => {
    acc[room.status] = (acc[room.status] || 0) + 1;
    return acc;
  }, {});

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={isLoading} onRefresh={refetch} />
      }
    >
      {/* Summary */}
      <View style={styles.summary}>
        <Text variant="titleMedium" style={styles.sectionTitle}>Summary</Text>
        <View style={styles.summaryChips}>
          {Object.entries(statusSummary).map(([status, count]) => (
            <Chip
              key={status}
              style={{ backgroundColor: getStatusColor(status), marginRight: 8, marginBottom: 8 }}
              textStyle={{ color: '#fff' }}
            >
              {status}: {count as number}
            </Chip>
          ))}
        </View>
      </View>

      {/* Legend */}
      <Card style={styles.legend}>
        <Card.Content>
          <Text variant="titleSmall" style={styles.legendTitle}>Legend</Text>
          <View style={styles.legendItems}>
            {['VC', 'VD', 'OC', 'OD', 'OOO', 'OOS'].map((status) => (
              <View key={status} style={styles.legendItem}>
                <View
                  style={[styles.legendDot, { backgroundColor: getStatusColor(status) }]}
                />
                <Text variant="bodySmall">{getStatusLabel(status)}</Text>
              </View>
            ))}
          </View>
        </Card.Content>
      </Card>

      {/* Room Grid */}
      <View style={styles.roomGrid}>
        {rooms.map((room: any) => (
          <View
            key={room.id}
            style={[styles.roomCard, { borderColor: getStatusColor(room.status) }]}
          >
            <Text variant="titleMedium" style={styles.roomNumber}>
              {room.room_number}
            </Text>
            <View
              style={[styles.statusBadge, { backgroundColor: getStatusColor(room.status) }]}
            >
              <Text style={styles.statusText}>{room.status}</Text>
            </View>
            <Text variant="bodySmall" style={styles.roomType}>
              {room.room_type}
            </Text>
            {room.has_pending_task && (
              <Chip icon="broom" compact style={styles.taskChip}>
                Task
              </Chip>
            )}
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  summary: {
    padding: 16,
    backgroundColor: '#fff',
  },
  sectionTitle: {
    marginBottom: 12,
  },
  summaryChips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  legend: {
    margin: 16,
    marginTop: 0,
  },
  legendTitle: {
    marginBottom: 8,
  },
  legendItems: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '50%',
    marginBottom: 4,
  },
  legendDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  roomGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 8,
  },
  roomCard: {
    width: '30%',
    margin: '1.5%',
    padding: 12,
    backgroundColor: '#fff',
    borderRadius: 8,
    borderWidth: 3,
    alignItems: 'center',
  },
  roomNumber: {
    fontWeight: 'bold',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    marginVertical: 4,
  },
  statusText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  roomType: {
    color: '#666',
    fontSize: 10,
    textAlign: 'center',
  },
  taskChip: {
    marginTop: 4,
  },
});
