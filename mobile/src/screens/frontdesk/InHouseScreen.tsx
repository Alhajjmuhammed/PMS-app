import React from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { Text, Card, Chip } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { frontdeskApi } from '../../services/apiServices';
import { Loading, ErrorMessage } from '../../components';

export default function InHouseScreen({ navigation }: any) {
  const { data: inHouseGuests, isLoading, error, refetch } = useQuery({
    queryKey: ['inHouse'],
    queryFn: () => frontdeskApi.inHouse(),
  });

  if (isLoading) return <Loading message="Loading in-house guests..." />;
  if (error) return <ErrorMessage message="Failed to load in-house guests" onRetry={refetch} />;

  const guestsList = inHouseGuests?.data || [];

  const renderGuest = ({ item }: any) => (
    <Card 
      style={styles.card}
      onPress={() => navigation.navigate('ReservationDetail', { id: item.id })}
    >
      <Card.Content>
        <View style={styles.header}>
          <Text variant="titleMedium">{item.guest_name}</Text>
          <Chip 
            icon="bed"
            style={{ backgroundColor: '#4caf50' }}
            textStyle={{ color: 'white' }}
          >
            IN-HOUSE
          </Chip>
        </View>
        
        <View style={styles.row}>
          <Text variant="bodyMedium">Room: {item.room_number || 'TBA'}</Text>
          <Text variant="bodyMedium">#{item.confirmation_number}</Text>
        </View>
        
        <View style={styles.row}>
          <Text variant="bodySmall">Check-in: {item.check_in_date}</Text>
          <Text variant="bodySmall">Check-out: {item.check_out_date}</Text>
        </View>
        
        <View style={styles.row}>
          <Text variant="bodySmall">Adults: {item.adults}</Text>
          {item.children > 0 && <Text variant="bodySmall">Children: {item.children}</Text>}
          <Text variant="bodySmall">Nights: {item.nights || 0}</Text>
        </View>

        {item.room_type_name && (
          <Text variant="bodySmall" style={styles.roomType}>
            {item.room_type_name}
          </Text>
        )}
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Card style={styles.summaryCard}>
        <Card.Content>
          <Text variant="headlineSmall">In-House Guests</Text>
          <Text variant="titleLarge" style={styles.count}>{guestsList.length}</Text>
          <Text variant="bodyMedium">Currently staying</Text>
        </Card.Content>
      </Card>

      <FlatList
        data={guestsList}
        renderItem={renderGuest}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text variant="bodyLarge">No guests in-house</Text>
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
    backgroundColor: '#4caf50',
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
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  roomType: {
    color: '#666',
    marginTop: 4,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
});
