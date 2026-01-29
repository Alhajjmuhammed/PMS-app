import React from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Card, Text, Title, Paragraph, Chip, Divider } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { reportsApi, housekeepingApi, maintenanceApi } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

export default function DashboardScreen() {
  const { user } = useAuth();

  const { data: stats, isLoading, refetch } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: () => reportsApi.getDashboardStats(),
  });

  const { data: myTasks } = useQuery({
    queryKey: ['myHousekeepingTasks'],
    queryFn: () => housekeepingApi.getMyTasks(),
    enabled: user?.role === 'HOUSEKEEPING',
  });

  const { data: myRequests } = useQuery({
    queryKey: ['myMaintenanceRequests'],
    queryFn: () => maintenanceApi.getMyRequests(),
    enabled: user?.role === 'MAINTENANCE',
  });

  const dashboardData = stats?.data;

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={isLoading} onRefresh={refetch} />
      }
    >
      <View style={styles.header}>
        <Text variant="headlineSmall">Welcome, {user?.first_name}!</Text>
        <Chip icon="office-building">{user?.property_name || 'All Properties'}</Chip>
      </View>

      {/* Stats Cards */}
      <View style={styles.statsRow}>
        <Card style={styles.statCard}>
          <Card.Content>
            <Title style={styles.statNumber}>
              {dashboardData?.occupancy_percent?.toFixed(1) || 0}%
            </Title>
            <Paragraph>Occupancy</Paragraph>
          </Card.Content>
        </Card>

        <Card style={styles.statCard}>
          <Card.Content>
            <Title style={styles.statNumber}>
              {dashboardData?.rooms_sold || dashboardData?.occupied || 0}
            </Title>
            <Paragraph>Occupied</Paragraph>
          </Card.Content>
        </Card>
      </View>

      <View style={styles.statsRow}>
        <Card style={styles.statCard}>
          <Card.Content>
            <Title style={styles.statNumber}>
              {dashboardData?.arrivals || 0}
            </Title>
            <Paragraph>Arrivals</Paragraph>
          </Card.Content>
        </Card>

        <Card style={styles.statCard}>
          <Card.Content>
            <Title style={styles.statNumber}>
              {dashboardData?.departures || 0}
            </Title>
            <Paragraph>Departures</Paragraph>
          </Card.Content>
        </Card>
      </View>

      <Divider style={styles.divider} />

      {/* Role-specific content */}
      {user?.role === 'HOUSEKEEPING' && myTasks?.data && (
        <Card style={styles.card}>
          <Card.Title title="My Housekeeping Tasks" />
          <Card.Content>
            {myTasks.data.length === 0 ? (
              <Text>No pending tasks</Text>
            ) : (
              myTasks.data.slice(0, 5).map((task: any) => (
                <View key={task.id} style={styles.taskItem}>
                  <Text variant="bodyLarge">Room {task.room_number}</Text>
                  <Chip compact>
                    {task.status}
                  </Chip>
                </View>
              ))
            )}
          </Card.Content>
        </Card>
      )}

      {user?.role === 'MAINTENANCE' && myRequests?.data && (
        <Card style={styles.card}>
          <Card.Title title="My Maintenance Requests" />
          <Card.Content>
            {myRequests.data.length === 0 ? (
              <Text>No pending requests</Text>
            ) : (
              myRequests.data.slice(0, 5).map((request: any) => (
                <View key={request.id} style={styles.taskItem}>
                  <View>
                    <Text variant="bodyLarge">{request.title}</Text>
                    <Text variant="bodySmall">{request.location || `Room ${request.room_number}`}</Text>
                  </View>
                  <Chip compact mode={request.priority === 'HIGH' ? 'flat' : 'outlined'}>
                    {request.priority}
                  </Chip>
                </View>
              ))
            )}
          </Card.Content>
        </Card>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
  },
  statsRow: {
    flexDirection: 'row',
    paddingHorizontal: 8,
    marginTop: 8,
  },
  statCard: {
    flex: 1,
    margin: 8,
  },
  statNumber: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1a73e8',
  },
  divider: {
    marginVertical: 16,
  },
  card: {
    margin: 16,
    marginTop: 0,
  },
  taskItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
});
