import React from 'react';
import { View, StyleSheet, FlatList, RefreshControl } from 'react-native';
import { Text, Card, Chip, FAB } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { propertiesApi } from '../../services/apiServices';
import { Loading, ErrorMessage } from '../../components';

export default function PropertyListScreen({ navigation }: any) {
  const { data: properties, isLoading, error, refetch } = useQuery({
    queryKey: ['properties'],
    queryFn: () => propertiesApi.list(),
  });

  if (isLoading) return <Loading message="Loading properties..." />;
  if (error) return <ErrorMessage message="Failed to load properties" onRetry={refetch} />;

  const propertiesList = properties?.data || [];

  const renderProperty = ({ item }: any) => (
    <Card 
      style={styles.card}
      onPress={() => navigation.navigate('PropertyDetail', { id: item.id })}
    >
      <Card.Content>
        <View style={styles.header}>
          <Text variant="titleLarge">{item.name}</Text>
          <Chip 
            icon={item.is_active ? 'check-circle' : 'circle-outline'}
            style={{ backgroundColor: item.is_active ? '#4caf50' : '#9e9e9e' }}
            textStyle={{ color: 'white' }}
          >
            {item.is_active ? 'Active' : 'Inactive'}
          </Chip>
        </View>
        
        {item.code && (
          <Text variant="bodyMedium" style={styles.code}>
            Code: {item.code}
          </Text>
        )}
        
        {item.address && (
          <Text variant="bodySmall" style={styles.address}>
            {item.address}, {item.city}, {item.country}
          </Text>
        )}
        
        <View style={styles.statsRow}>
          <View style={styles.stat}>
            <Text variant="titleMedium">{item.total_rooms || 0}</Text>
            <Text variant="bodySmall">Rooms</Text>
          </View>
          {item.phone && (
            <View style={styles.stat}>
              <Text variant="bodySmall">{item.phone}</Text>
            </View>
          )}
        </View>
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      <Card style={styles.summaryCard}>
        <Card.Content>
          <Text variant="headlineSmall">Properties</Text>
          <Text variant="titleLarge" style={styles.count}>{propertiesList.length}</Text>
        </Card.Content>
      </Card>

      <FlatList
        data={propertiesList}
        renderItem={renderProperty}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text variant="bodyLarge">No properties found</Text>
          </View>
        }
      />

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => navigation.navigate('CreateProperty')}
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
    marginTop: 8,
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
  code: {
    color: '#666',
    marginBottom: 4,
  },
  address: {
    color: '#999',
    marginBottom: 12,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  stat: {
    alignItems: 'center',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: '#1a73e8',
  },
});
