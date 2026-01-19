import React from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Text, Card, Button, Chip } from 'react-native-paper';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { roomsApi } from '../../services/apiServices';
import { Loading, ErrorMessage } from '../../components';

export default function RoomDetailScreen({ route, navigation }: any) {
  const { id } = route.params;
  const queryClient = useQueryClient();

  const { data: room, isLoading, error, refetch } = useQuery({
    queryKey: ['rooms', id],
    queryFn: () => roomsApi.get(id),
  });

  const updateStatusMutation = useMutation({
    mutationFn: (status: string) => roomsApi.updateStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rooms'] });
      Alert.alert('Success', 'Room status updated');
    },
    onError: () => {
      Alert.alert('Error', 'Failed to update room status');
    },
  });

  if (isLoading) return <Loading message="Loading room..." />;
  if (error) return <ErrorMessage message="Failed to load room" onRetry={refetch} />;

  const r = room?.data;
  
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

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.header}>
            <Text variant="headlineLarge">{r.number}</Text>
            <Chip 
              style={{ backgroundColor: getStatusColor(r.status) }}
              textStyle={{ color: 'white', fontSize: 16 }}
            >
              {r.status?.replace(/_/g, ' ')}
            </Chip>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Room Information" />
        <Card.Content>
          <View style={styles.row}>
            <Text variant="bodyMedium">Room Type:</Text>
            <Text variant="bodyMedium" style={styles.value}>
              {r.room_type_name || 'Standard'}
            </Text>
          </View>
          <View style={styles.row}>
            <Text variant="bodyMedium">Floor:</Text>
            <Text variant="bodyMedium" style={styles.value}>{r.floor || 'N/A'}</Text>
          </View>
          <View style={styles.row}>
            <Text variant="bodyMedium">Max Occupancy:</Text>
            <Text variant="bodyMedium" style={styles.value}>{r.max_occupancy || 0}</Text>
          </View>
          {r.fo_status && (
            <View style={styles.row}>
              <Text variant="bodyMedium">Front Office Status:</Text>
              <Text variant="bodyMedium" style={styles.value}>
                {r.fo_status.replace(/_/g, ' ')}
              </Text>
            </View>
          )}
        </Card.Content>
      </Card>

      {r.features && r.features.length > 0 && (
        <Card style={styles.card}>
          <Card.Title title="Features & Amenities" />
          <Card.Content>
            <View style={styles.featureContainer}>
              {r.features.map((feature: string, index: number) => (
                <Chip key={index} icon="check" style={styles.featureChip}>
                  {feature}
                </Chip>
              ))}
            </View>
          </Card.Content>
        </Card>
      )}

      {r.description && (
        <Card style={styles.card}>
          <Card.Title title="Description" />
          <Card.Content>
            <Text variant="bodyMedium">{r.description}</Text>
          </Card.Content>
        </Card>
      )}

      <Card style={styles.card}>
        <Card.Title title="Quick Actions" />
        <Card.Content>
          <View style={styles.actions}>
            <Button 
              mode="contained" 
              icon="broom"
              onPress={() => updateStatusMutation.mutate('VACANT_CLEAN')}
              style={[styles.button, { backgroundColor: '#4caf50' }]}
            >
              Mark Clean
            </Button>
            <Button 
              mode="contained" 
              icon="alert"
              onPress={() => updateStatusMutation.mutate('VACANT_DIRTY')}
              style={[styles.button, { backgroundColor: '#ff9800' }]}
            >
              Mark Dirty
            </Button>
            <Button 
              mode="contained" 
              icon="wrench"
              onPress={() => updateStatusMutation.mutate('OUT_OF_ORDER')}
              style={[styles.button, { backgroundColor: '#f44336' }]}
            >
              Out of Order
            </Button>
            <Button 
              mode="outlined" 
              icon="calendar-check"
              onPress={() => navigation.navigate('CreateReservation', { roomId: id })}
              style={styles.button}
            >
              Create Reservation
            </Button>
          </View>
        </Card.Content>
      </Card>
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
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  value: {
    fontWeight: 'bold',
  },
  featureContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  featureChip: {
    marginBottom: 4,
  },
  actions: {
    gap: 12,
  },
  button: {
    marginVertical: 4,
  },
});
