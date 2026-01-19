import React from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { Text, Card, Chip } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { frontdeskApi } from '../../services/apiServices';
import { Loading, ErrorMessage } from '../../components';

export default function DeparturesScreen({ navigation }: any) {
  const today = new Date().toISOString().split('T')[0];
  
  const { data: departures, isLoading, error, refetch } = useQuery({
    queryKey: ['departures', today],
    queryFn: () => frontdeskApi.departures(today),
  });

  if (isLoading) return <Loading message="Loading departures..." />;
  if (error) return <ErrorMessage message="Failed to load departures" onRetry={refetch} />;

  const departuresList = departures?.data || [];

  const renderDeparture = ({ item }: any) => (
    <Card 
      style={styles.card}
      onPress={() => navigation.navigate('ReservationDetail', { id: item.id })}
    >
      <Card.Content>
        <View style={styles.header}>
          <Text variant="titleMedium">{item.guest_name}</Text>
          <Chip 
            icon={item.status === 'CHECKED_OUT' ? 'check' : 'clock'}
            style={{ backgroundColor: item.status === 'CHECKED_OUT' ? '#9e9e9e' : '#4caf50' }}
            textStyle={{ color: 'white' }}
          >
            {item.status}
          </Chip>
        </View>
        
        <Text variant="bodyMedium" style={styles.confirmationNumber}>
          #{item.confirmation_number}
        </Text>
        
        <View style={styles.row}>
          <Text variant="bodySmall">Check-out: {item.check_out_date}</Text>
          {item.room_number && <Text variant="bodySmall">Room: {item.room_number}</Text>}
        </View>
        
        {item.total_amount && (
          <Text variant="titleSmall" style={styles.amount}>
            Balance: ${parseFloat(item.total_amount).toFixed(2)}
          </Text>
        )}
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Card style={styles.summaryCard}>
        <Card.Content>
          <Text variant="headlineSmall">Today's Departures</Text>
          <Text variant="titleLarge" style={styles.count}>{departuresList.length}</Text>
          <Text variant="bodyMedium">{today}</Text>
        </Card.Content>
      </Card>

      <FlatList
        data={departuresList}
        renderItem={renderDeparture}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text variant="bodyLarge">No departures today</Text>
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
    backgroundColor: '#9c27b0',
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
  amount: {
    color: '#f44336',
    fontWeight: 'bold',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
});
