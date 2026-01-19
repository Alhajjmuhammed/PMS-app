import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Text, TextInput, Button, Card, Chip } from 'react-native-paper';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { reservationsApi, guestsApi, roomsApi } from '../../services/apiServices';
import { Loading } from '../../components';

export default function CreateReservationScreen({ navigation }: any) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    guest_id: '',
    check_in_date: '',
    check_out_date: '',
    adults: '2',
    children: '0',
    special_requests: '',
  });
  const [availabilityChecked, setAvailabilityChecked] = useState(false);
  const [estimatedPrice, setEstimatedPrice] = useState<number | null>(null);

  const { data: guests } = useQuery({
    queryKey: ['guests'],
    queryFn: () => guestsApi.list(),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => reservationsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
      Alert.alert('Success', 'Reservation created successfully');
      navigation.goBack();
    },
    onError: (error: any) => {
      Alert.alert('Error', error?.response?.data?.message || 'Failed to create reservation');
    },
  });

  const checkAvailability = async () => {
    if (!formData.check_in_date || !formData.check_out_date) {
      Alert.alert('Error', 'Please enter check-in and check-out dates');
      return;
    }

    try {
      const result = await reservationsApi.checkAvailability({
        check_in_date: formData.check_in_date,
        check_out_date: formData.check_out_date,
        adults: parseInt(formData.adults),
        children: parseInt(formData.children),
      });
      
      if (result.data.available) {
        setAvailabilityChecked(true);
        Alert.alert('Available', `${result.data.available_rooms?.length || 0} rooms available`);
      } else {
        Alert.alert('Not Available', 'No rooms available for selected dates');
      }
    } catch (error: any) {
      Alert.alert('Error', 'Failed to check availability');
    }
  };

  const calculatePrice = async () => {
    if (!formData.check_in_date || !formData.check_out_date) {
      Alert.alert('Error', 'Please enter check-in and check-out dates');
      return;
    }

    try {
      const result = await reservationsApi.calculatePrice({
        check_in_date: formData.check_in_date,
        check_out_date: formData.check_out_date,
        adults: parseInt(formData.adults),
        children: parseInt(formData.children),
      });
      
      setEstimatedPrice(result.data.total_amount);
    } catch (error: any) {
      Alert.alert('Error', 'Failed to calculate price');
    }
  };

  const handleSubmit = () => {
    if (!formData.guest_id || !formData.check_in_date || !formData.check_out_date) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    if (!availabilityChecked) {
      Alert.alert('Warning', 'Please check availability before creating reservation');
      return;
    }

    createMutation.mutate({
      guest_id: parseInt(formData.guest_id),
      check_in_date: formData.check_in_date,
      check_out_date: formData.check_out_date,
      adults: parseInt(formData.adults),
      children: parseInt(formData.children),
      special_requests: formData.special_requests,
    });
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Title title="Guest Information" />
        <Card.Content>
          <TextInput
            label="Guest ID *"
            value={formData.guest_id}
            onChangeText={(text) => setFormData({ ...formData, guest_id: text })}
            keyboardType="numeric"
            mode="outlined"
            style={styles.input}
          />
          <Button mode="text" onPress={() => navigation.navigate('GuestList')}>
            Search Guests
          </Button>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Stay Dates" />
        <Card.Content>
          <TextInput
            label="Check-in Date (YYYY-MM-DD) *"
            value={formData.check_in_date}
            onChangeText={(text) => setFormData({ ...formData, check_in_date: text })}
            placeholder="2026-01-15"
            mode="outlined"
            style={styles.input}
          />
          <TextInput
            label="Check-out Date (YYYY-MM-DD) *"
            value={formData.check_out_date}
            onChangeText={(text) => setFormData({ ...formData, check_out_date: text })}
            placeholder="2026-01-17"
            mode="outlined"
            style={styles.input}
          />
          
          <View style={styles.buttonRow}>
            <Button 
              mode="outlined" 
              onPress={checkAvailability}
              style={styles.halfButton}
            >
              Check Availability
            </Button>
            <Button 
              mode="outlined" 
              onPress={calculatePrice}
              style={styles.halfButton}
            >
              Calculate Price
            </Button>
          </View>

          {availabilityChecked && (
            <Chip icon="check-circle" style={styles.chip}>
              Availability Confirmed
            </Chip>
          )}

          {estimatedPrice && (
            <Card style={styles.priceCard}>
              <Card.Content>
                <Text variant="titleMedium">Estimated Price</Text>
                <Text variant="headlineMedium" style={styles.price}>
                  ${estimatedPrice.toFixed(2)}
                </Text>
              </Card.Content>
            </Card>
          )}
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Guest Details" />
        <Card.Content>
          <TextInput
            label="Adults *"
            value={formData.adults}
            onChangeText={(text) => setFormData({ ...formData, adults: text })}
            keyboardType="numeric"
            mode="outlined"
            style={styles.input}
          />
          <TextInput
            label="Children"
            value={formData.children}
            onChangeText={(text) => setFormData({ ...formData, children: text })}
            keyboardType="numeric"
            mode="outlined"
            style={styles.input}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Special Requests" />
        <Card.Content>
          <TextInput
            label="Special Requests"
            value={formData.special_requests}
            onChangeText={(text) => setFormData({ ...formData, special_requests: text })}
            multiline
            numberOfLines={4}
            mode="outlined"
            style={styles.input}
          />
        </Card.Content>
      </Card>

      <View style={styles.actions}>
        <Button 
          mode="contained" 
          onPress={handleSubmit}
          loading={createMutation.isPending}
          disabled={createMutation.isPending}
          style={styles.submitButton}
        >
          Create Reservation
        </Button>
        <Button 
          mode="outlined" 
          onPress={() => navigation.goBack()}
          style={styles.cancelButton}
        >
          Cancel
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
  input: {
    marginBottom: 12,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 8,
  },
  halfButton: {
    flex: 1,
  },
  chip: {
    marginTop: 12,
    backgroundColor: '#4caf50',
  },
  priceCard: {
    marginTop: 12,
    backgroundColor: '#e8f5e9',
  },
  price: {
    color: '#4caf50',
    fontWeight: 'bold',
    marginTop: 8,
  },
  actions: {
    padding: 16,
    gap: 12,
  },
  submitButton: {
    marginVertical: 4,
  },
  cancelButton: {
    marginVertical: 4,
  },
});
