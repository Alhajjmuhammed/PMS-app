import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, Chip, Button } from 'react-native-paper';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationsApi } from '../../services/apiServices';
import { Loading, ErrorMessage } from '../../components';

export default function NotificationDetailScreen({ route, navigation }: any) {
  const { id } = route.params;
  const queryClient = useQueryClient();

  const { data: notification, isLoading, error, refetch } = useQuery({
    queryKey: ['notifications', id],
    queryFn: () => notificationsApi.get(id),
  });

  const markReadMutation = useMutation({
    mutationFn: () => notificationsApi.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  React.useEffect(() => {
    const notif = notification?.data;
    if (notif && !notif.is_read) {
      markReadMutation.mutate();
    }
  }, [notification]);

  if (isLoading) return <Loading message="Loading notification..." />;
  if (error) return <ErrorMessage message="Failed to load notification" onRetry={refetch} />;

  const notif = notification?.data;

  const getPriorityColor = (priority: string) => {
    const colors: any = {
      URGENT: '#f44336',
      HIGH: '#ff9800',
      NORMAL: '#2196f3',
      LOW: '#9e9e9e',
    };
    return colors[priority] || '#2196f3';
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.header}>
            <Chip 
              style={{ backgroundColor: getPriorityColor(notif.priority) }}
              textStyle={{ color: 'white' }}
            >
              {notif.priority} PRIORITY
            </Chip>
            {notif.is_read && (
              <Chip icon="check" style={styles.readChip}>
                Read
              </Chip>
            )}
          </View>

          <Text variant="headlineSmall" style={styles.title}>
            {notif.title || 'Notification'}
          </Text>

          {notif.notification_type && (
            <Chip icon="label" style={styles.typeChip}>
              {notif.notification_type}
            </Chip>
          )}
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Message" />
        <Card.Content>
          <Text variant="bodyLarge">{notif.message}</Text>
        </Card.Content>
      </Card>

      {notif.action_url && (
        <Card style={styles.card}>
          <Card.Title title="Action Required" />
          <Card.Content>
            <Button 
              mode="contained" 
              icon="open-in-new"
              onPress={() => {
                // Handle action URL navigation
                console.log('Navigate to:', notif.action_url);
              }}
            >
              Take Action
            </Button>
          </Card.Content>
        </Card>
      )}

      <Card style={styles.card}>
        <Card.Title title="Details" />
        <Card.Content>
          <View style={styles.row}>
            <Text variant="bodyMedium">Sent:</Text>
            <Text variant="bodyMedium" style={styles.value}>
              {formatDate(notif.created_at)}
            </Text>
          </View>
          
          {notif.read_at && (
            <View style={styles.row}>
              <Text variant="bodyMedium">Read:</Text>
              <Text variant="bodyMedium" style={styles.value}>
                {formatDate(notif.read_at)}
              </Text>
            </View>
          )}

          {notif.sender_name && (
            <View style={styles.row}>
              <Text variant="bodyMedium">From:</Text>
              <Text variant="bodyMedium" style={styles.value}>
                {notif.sender_name}
              </Text>
            </View>
          )}
        </Card.Content>
      </Card>

      {notif.related_reservation_id && (
        <View style={styles.actions}>
          <Button 
            mode="outlined" 
            icon="calendar"
            onPress={() => navigation.navigate('ReservationDetail', { id: notif.related_reservation_id })}
          >
            View Related Reservation
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
  card: {
    margin: 16,
    marginBottom: 8,
  },
  header: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  title: {
    marginBottom: 12,
  },
  typeChip: {
    backgroundColor: '#e3f2fd',
    alignSelf: 'flex-start',
  },
  readChip: {
    backgroundColor: '#4caf50',
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  value: {
    fontWeight: 'bold',
    flex: 1,
    textAlign: 'right',
  },
  actions: {
    padding: 16,
  },
});
