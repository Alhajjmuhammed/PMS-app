import React from 'react';
import { View, StyleSheet, ScrollView, FlatList } from 'react-native';
import { Text, Card, Chip } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { frontdeskApi } from '../../services/apiServices';
import { Loading, ErrorMessage } from '../../components';

export default function ArrivalsScreen({ navigation }: any) {
  const today = new Date().toISOString().split('T')[0];
  
  const { data: arrivals, isLoading, error, refetch } = useQuery({
    queryKey: ['arrivals', today],
    queryFn: () => frontdeskApi.arrivals(today),
  });

  if (isLoading) return <Loading message="Loading arrivals..." />;
  if (error) return <ErrorMessage message="Failed to load arrivals" onRetry={refetch} />;

  const arrivalsList = arrivals?.data || [];

  const renderArrival = ({ item }: any) => (
    <Card 
      style={styles.card}
      onPress={() => navigation.navigate('ReservationDetail', { id: item.id })}
    >
      <Card.Content>
        <View style={styles.header}>
          <Text variant="titleMedium">{item.guest_name}</Text>
          <Chip 
            icon={item.status === 'CHECKED_IN' ? 'check' : 'clock'}
            style={{ backgroundColor: item.status === 'CHECKED_IN' ? '#4caf50' : '#ff9800' }}
            textStyle={{ color: 'white' }}
          >
            {item.status}
          </Chip>
        </View>
        
        <Text variant="bodyMedium" style={styles.confirmationNumber}>
          #{item.confirmation_number}
        </Text>
        
        <View style={styles.row}>
          <Text variant="bodySmall">Check-in: {item.check_in_date}</Text>
          <Text variant="bodySmall">Adults: {item.adults}</Text>
        </View>
        
        {item.room_type_name && (
          <Text variant="bodySmall" style={styles.roomType}>
            Room Type: {item.room_type_name}
          </Text>
        )}
        
        {item.special_requests && (
          <Text variant="bodySmall" style={styles.requests}>
            Requests: {item.special_requests}
          </Text>
        )}
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Card style={styles.summaryCard}>
        <Card.Content>
          <Text variant="headlineSmall">Today's Arrivals</Text>
          <Text variant="titleLarge" style={styles.count}>{arrivalsList.length}</Text>
          <Text variant="bodyMedium">{today}</Text>
        </Card.Content>
      </Card>

      <FlatList
        data={arrivalsList}
        renderItem={renderArrival}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text variant="bodyLarge">No arrivals today</Text>
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
    backgroundColor: '#1a73e8',
  },
  count: {
    color: 'white',
    fontWeight: 'bold',
    marginVertical: 8,
  },
  card: {
    marginHorizontal: 16,
    marginBottom: 12,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  confirmationNumber: {
    color: '#666',
    marginBottom: 8,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  roomType: {
    color: '#666',
    marginBottom: 4,
  },
  requests: {
    color: '#ff9800',
    fontStyle: 'italic',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
});
