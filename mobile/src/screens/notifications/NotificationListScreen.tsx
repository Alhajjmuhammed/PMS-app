import React, { useState } from 'react';
import { View, StyleSheet, FlatList, RefreshControl } from 'react-native';
import { Text, Card, Chip, Badge, SegmentedButtons } from 'react-native-paper';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationsApi } from '../../services/apiServices';
import { Loading, ErrorMessage } from '../../components';

export default function NotificationListScreen({ navigation }: any) {
  const [filter, setFilter] = useState('all');
  const [refreshing, setRefreshing] = useState(false);
  const queryClient = useQueryClient();

  const { data: notifications, isLoading, error, refetch } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsApi.list(),
  });

  const { data: unreadData } = useQuery({
    queryKey: ['notifications', 'unread'],
    queryFn: () => notificationsApi.unread(),
  });

  const markReadMutation = useMutation({
    mutationFn: (id: number) => notificationsApi.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  const onRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  const notificationsList = notifications?.data || [];
  const unreadCount = unreadData?.data?.length || 0;

  const filteredNotifications = notificationsList.filter((notif: any) => {
    if (filter === 'unread') return !notif.is_read;
    if (filter === 'read') return notif.is_read;
    return true;
  });

  const getPriorityColor = (priority: string) => {
    const colors: any = {
      URGENT: '#f44336',
      HIGH: '#ff9800',
      NORMAL: '#2196f3',
      LOW: '#9e9e9e',
    };
    return colors[priority] || '#2196f3';
  };

  const getTimeSince = (timestamp: string) => {
    const now = new Date();
    const created = new Date(timestamp);
    const diff = Math.floor((now.getTime() - created.getTime()) / 1000);
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  if (isLoading) return <Loading message="Loading notifications..." />;
  if (error) return <ErrorMessage message="Failed to load notifications" onRetry={refetch} />;

  const renderNotification = ({ item }: any) => (
    <Card 
      style={[styles.card, !item.is_read && styles.unreadCard]}
      onPress={() => {
        if (!item.is_read) {
          markReadMutation.mutate(item.id);
        }
        navigation.navigate('NotificationDetail', { id: item.id });
      }}
    >
      <Card.Content>
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            {!item.is_read && <Badge style={styles.badge} />}
            <Text variant="titleMedium" numberOfLines={1}>
              {item.title || 'Notification'}
            </Text>
          </View>
          <Chip 
            style={{ backgroundColor: getPriorityColor(item.priority) }}
            textStyle={{ color: 'white', fontSize: 10 }}
          >
            {item.priority}
          </Chip>
        </View>
        
        <Text variant="bodyMedium" numberOfLines={2} style={styles.message}>
          {item.message}
        </Text>
        
        <View style={styles.footer}>
          <Text variant="bodySmall" style={styles.time}>
            {getTimeSince(item.created_at)}
          </Text>
          {item.notification_type && (
            <Chip icon="label" style={styles.typeChip}>
              {item.notification_type}
            </Chip>
          )}
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Card style={styles.summaryCard}>
        <Card.Content>
          <View style={styles.summaryRow}>
            <View>
              <Text variant="headlineSmall">Notifications</Text>
              <Text variant="bodyMedium">{unreadCount} unread</Text>
            </View>
            {unreadCount > 0 && (
              <Badge size={32} style={styles.summaryBadge}>{unreadCount}</Badge>
            )}
          </View>
        </Card.Content>
      </Card>

      <SegmentedButtons
        value={filter}
        onValueChange={setFilter}
        buttons={[
          { value: 'all', label: 'All' },
          { value: 'unread', label: 'Unread' },
          { value: 'read', label: 'Read' },
        ]}
        style={styles.segmented}
      />

      <FlatList
        data={filteredNotifications}
        renderItem={renderNotification}
        keyExtractor={(item) => item.id.toString()}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text variant="bodyLarge">No notifications</Text>
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
  summaryCard: {
    margin: 16,
    marginBottom: 8,
    backgroundColor: '#1a73e8',
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  summaryBadge: {
    backgroundColor: '#f44336',
  },
  segmented: {
    marginHorizontal: 16,
    marginBottom: 16,
  },
  card: {
    marginHorizontal: 16,
    marginBottom: 12,
  },
  unreadCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#1a73e8',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    gap: 8,
  },
  badge: {
    backgroundColor: '#1a73e8',
  },
  message: {
    color: '#666',
    marginBottom: 8,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  time: {
    color: '#999',
  },
  typeChip: {
    height: 24,
    backgroundColor: '#e3f2fd',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
});
