import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, Button, Chip, Divider, List } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { guestsApi } from '../../services/apiServices';
import { Loading, ErrorMessage } from '../../components';

export default function GuestDetailScreen({ route, navigation }: any) {
  const { id } = route.params;

  const { data: guest, isLoading, error, refetch } = useQuery({
    queryKey: ['guests', id],
    queryFn: () => guestsApi.get(id),
  });

  if (isLoading) return <Loading message="Loading guest..." />;
  if (error) return <ErrorMessage message="Failed to load guest" onRetry={refetch} />;

  const g = guest?.data;

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.header}>
            <Text variant="headlineSmall">{g.full_name || `${g.first_name} ${g.last_name}`}</Text>
            {g.vip_level && (
              <Chip icon="star" style={styles.vipChip}>VIP {g.vip_level}</Chip>
            )}
          </View>
          
          {g.is_blacklisted && (
            <Chip icon="alert" style={styles.blacklistChip}>Blacklisted</Chip>
          )}
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Contact Information" />
        <Card.Content>
          <View style={styles.row}>
            <Text variant="bodyMedium">Email:</Text>
            <Text variant="bodyMedium" style={styles.value}>{g.email}</Text>
          </View>
          {g.phone && (
            <View style={styles.row}>
              <Text variant="bodyMedium">Phone:</Text>
              <Text variant="bodyMedium" style={styles.value}>{g.phone}</Text>
            </View>
          )}
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Personal Details" />
        <Card.Content>
          {g.date_of_birth && (
            <View style={styles.row}>
              <Text variant="bodyMedium">Date of Birth:</Text>
              <Text variant="bodyMedium" style={styles.value}>{g.date_of_birth}</Text>
            </View>
          )}
          {g.gender && (
            <View style={styles.row}>
              <Text variant="bodyMedium">Gender:</Text>
              <Text variant="bodyMedium" style={styles.value}>{g.gender}</Text>
            </View>
          )}
          {g.nationality && (
            <View style={styles.row}>
              <Text variant="bodyMedium">Nationality:</Text>
              <Text variant="bodyMedium" style={styles.value}>{g.nationality}</Text>
            </View>
          )}
        </Card.Content>
      </Card>

      {(g.address || g.city || g.country) && (
        <Card style={styles.card}>
          <Card.Title title="Address" />
          <Card.Content>
            {g.address && <Text variant="bodyMedium">{g.address}</Text>}
            <Text variant="bodyMedium">
              {[g.city, g.state, g.country, g.postal_code].filter(Boolean).join(', ')}
            </Text>
          </Card.Content>
        </Card>
      )}

      {(g.id_type || g.id_number) && (
        <Card style={styles.card}>
          <Card.Title title="Identification" />
          <Card.Content>
            {g.id_type && (
              <View style={styles.row}>
                <Text variant="bodyMedium">ID Type:</Text>
                <Text variant="bodyMedium" style={styles.value}>{g.id_type}</Text>
              </View>
            )}
            {g.id_number && (
              <View style={styles.row}>
                <Text variant="bodyMedium">ID Number:</Text>
                <Text variant="bodyMedium" style={styles.value}>{g.id_number}</Text>
              </View>
            )}
          </Card.Content>
        </Card>
      )}

      <Card style={styles.card}>
        <Card.Title title="Guest Statistics" />
        <Card.Content>
          <View style={styles.statRow}>
            <View style={styles.stat}>
              <Text variant="titleLarge">{g.total_stays || 0}</Text>
              <Text variant="labelSmall">Total Stays</Text>
            </View>
            <View style={styles.stat}>
              <Text variant="titleLarge" style={styles.revenue}>
                ${parseFloat(g.total_revenue || 0).toFixed(2)}
              </Text>
              <Text variant="labelSmall">Total Revenue</Text>
            </View>
          </View>
        </Card.Content>
      </Card>

      {g.preferences && g.preferences.length > 0 && (
        <Card style={styles.card}>
          <Card.Title title="Preferences" />
          <Card.Content>
            {g.preferences.map((pref: any, index: number) => (
              <List.Item
                key={index}
                title={pref.preference}
                description={pref.category}
                left={props => <List.Icon {...props} icon="heart" />}
              />
            ))}
          </Card.Content>
        </Card>
      )}

      <View style={styles.actions}>
        <Button 
          mode="contained" 
          onPress={() => navigation.navigate('CreateReservation', { guestId: id })}
          style={styles.button}
        >
          Create Reservation
        </Button>
        <Button 
          mode="outlined" 
          onPress={() => navigation.navigate('GuestEdit', { id })}
          style={styles.button}
        >
          Edit Guest
        </Button>
      </View>
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
    marginBottom: 8,
  },
  vipChip: {
    backgroundColor: '#ffd700',
  },
  blacklistChip: {
    backgroundColor: '#f44336',
    marginTop: 8,
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
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  stat: {
    alignItems: 'center',
  },
  revenue: {
    color: '#4caf50',
  },
  actions: {
    padding: 16,
    gap: 12,
  },
  button: {
    marginVertical: 4,
  },
});
