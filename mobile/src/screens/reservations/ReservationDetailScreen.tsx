import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, Card, Button, Chip, Divider } from 'react-native-paper';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { reservationsApi } from '../../services/apiServices';
import { Loading, ErrorMessage } from '../../components';

export default function ReservationDetailScreen({ route, navigation }: any) {
  const { id } = route.params;
  const queryClient = useQueryClient();

  const { data: reservation, isLoading, error, refetch } = useQuery({
    queryKey: ['reservations', id],
    queryFn: () => reservationsApi.get(id),
  });

  const cancelMutation = useMutation({
    mutationFn: (reason: string) => reservationsApi.cancel(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
      navigation.goBack();
    },
  });

  if (isLoading) return <Loading message="Loading reservation..." />;
  if (error) return <ErrorMessage message="Failed to load reservation" onRetry={refetch} />;

  const res = reservation?.data;
  const getStatusColor = (status: string) => {
    const colors: any = {
      PENDING: '#ff9800',
      CONFIRMED: '#2196f3',
      CHECKED_IN: '#4caf50',
      CHECKED_OUT: '#9e9e9e',
      CANCELLED: '#f44336',
      NO_SHOW: '#e91e63',
    };
    return colors[status] || '#9e9e9e';
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.header}>
            <Text variant="headlineSmall">{res.guest_name}</Text>
            <Chip 
              style={{ backgroundColor: getStatusColor(res.status) }}
              textStyle={{ color: 'white' }}
            >
              {res.status}
            </Chip>
          </View>
          
          <Text variant="titleMedium" style={styles.confirmationNumber}>
            Confirmation: #{res.confirmation_number}
          </Text>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Stay Details" />
        <Card.Content>
          <View style={styles.row}>
            <Text variant="bodyMedium">Check-in:</Text>
            <Text variant="bodyMedium" style={styles.value}>{res.check_in_date}</Text>
          </View>
          <View style={styles.row}>
            <Text variant="bodyMedium">Check-out:</Text>
            <Text variant="bodyMedium" style={styles.value}>{res.check_out_date}</Text>
          </View>
          <View style={styles.row}>
            <Text variant="bodyMedium">Nights:</Text>
            <Text variant="bodyMedium" style={styles.value}>{res.nights || 0}</Text>
          </View>
          <Divider style={styles.divider} />
          <View style={styles.row}>
            <Text variant="bodyMedium">Adults:</Text>
            <Text variant="bodyMedium" style={styles.value}>{res.adults}</Text>
          </View>
          <View style={styles.row}>
            <Text variant="bodyMedium">Children:</Text>
            <Text variant="bodyMedium" style={styles.value}>{res.children || 0}</Text>
          </View>
        </Card.Content>
      </Card>

      {res.room_type_name && (
        <Card style={styles.card}>
          <Card.Title title="Room Information" />
          <Card.Content>
            <View style={styles.row}>
              <Text variant="bodyMedium">Room Type:</Text>
              <Text variant="bodyMedium" style={styles.value}>{res.room_type_name}</Text>
            </View>
            {res.room_number && (
              <View style={styles.row}>
                <Text variant="bodyMedium">Room Number:</Text>
                <Text variant="bodyMedium" style={styles.value}>{res.room_number}</Text>
              </View>
            )}
          </Card.Content>
        </Card>
      )}

      {res.total_amount && (
        <Card style={styles.card}>
          <Card.Title title="Pricing" />
          <Card.Content>
            <View style={styles.row}>
              <Text variant="titleMedium">Total Amount:</Text>
              <Text variant="titleLarge" style={styles.totalAmount}>
                ${parseFloat(res.total_amount).toFixed(2)}
              </Text>
            </View>
          </Card.Content>
        </Card>
      )}

      {res.special_requests && (
        <Card style={styles.card}>
          <Card.Title title="Special Requests" />
          <Card.Content>
            <Text variant="bodyMedium">{res.special_requests}</Text>
          </Card.Content>
        </Card>
      )}

      {res.status === 'CONFIRMED' && (
        <View style={styles.actions}>
          <Button 
            mode="contained" 
            onPress={() => navigation.navigate('CheckIn', { reservationId: id })}
            style={styles.button}
          >
            Check In
          </Button>
          <Button 
            mode="outlined" 
            onPress={() => navigation.navigate('ReservationEdit', { id })}
            style={styles.button}
          >
            Edit Reservation
          </Button>
          <Button 
            mode="outlined" 
            onPress={() => cancelMutation.mutate('User requested cancellation')}
            style={styles.button}
            buttonColor="#f44336"
            textColor="white"
          >
            Cancel Reservation
          </Button>
        </View>
      )}

      {res.status === 'CHECKED_IN' && (
        <View style={styles.actions}>
          <Button 
            mode="contained" 
            onPress={() => navigation.navigate('CheckOut', { reservationId: id })}
            style={styles.button}
          >
            Check Out
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
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  confirmationNumber: {
    color: '#666',
    marginTop: 8,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  value: {
    fontWeight: 'bold',
  },
  divider: {
    marginVertical: 8,
  },
  totalAmount: {
    color: '#4caf50',
    fontWeight: 'bold',
  },
  actions: {
    padding: 16,
    gap: 12,
  },
  button: {
    marginVertical: 4,
  },
});
