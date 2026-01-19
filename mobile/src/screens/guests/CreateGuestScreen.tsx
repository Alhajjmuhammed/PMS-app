import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Text, TextInput, Button, Card, SegmentedButtons } from 'react-native-paper';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { guestsApi } from '../../services/apiServices';

export default function CreateGuestScreen({ navigation }: any) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    date_of_birth: '',
    gender: '',
    nationality: '',
    id_type: '',
    id_number: '',
    address: '',
    city: '',
    state: '',
    country: '',
    postal_code: '',
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => guestsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guests'] });
      Alert.alert('Success', 'Guest created successfully');
      navigation.goBack();
    },
    onError: (error: any) => {
      Alert.alert('Error', error?.response?.data?.message || 'Failed to create guest');
    },
  });

  const handleSubmit = () => {
    if (!formData.first_name || !formData.last_name || !formData.email) {
      Alert.alert('Error', 'Please fill in required fields (Name and Email)');
      return;
    }

    createMutation.mutate(formData);
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Title title="Personal Information" />
        <Card.Content>
          <TextInput
            label="First Name *"
            value={formData.first_name}
            onChangeText={(text) => setFormData({ ...formData, first_name: text })}
            mode="outlined"
            style={styles.input}
          />
          <TextInput
            label="Last Name *"
            value={formData.last_name}
            onChangeText={(text) => setFormData({ ...formData, last_name: text })}
            mode="outlined"
            style={styles.input}
          />
          <TextInput
            label="Date of Birth (YYYY-MM-DD)"
            value={formData.date_of_birth}
            onChangeText={(text) => setFormData({ ...formData, date_of_birth: text })}
            placeholder="1990-01-15"
            mode="outlined"
            style={styles.input}
          />
          
          <Text variant="labelMedium" style={styles.label}>Gender</Text>
          <SegmentedButtons
            value={formData.gender}
            onValueChange={(value) => setFormData({ ...formData, gender: value })}
            buttons={[
              { value: 'M', label: 'Male' },
              { value: 'F', label: 'Female' },
              { value: 'O', label: 'Other' },
            ]}
            style={styles.segmented}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Contact Information" />
        <Card.Content>
          <TextInput
            label="Email *"
            value={formData.email}
            onChangeText={(text) => setFormData({ ...formData, email: text })}
            keyboardType="email-address"
            autoCapitalize="none"
            mode="outlined"
            style={styles.input}
          />
          <TextInput
            label="Phone"
            value={formData.phone}
            onChangeText={(text) => setFormData({ ...formData, phone: text })}
            keyboardType="phone-pad"
            mode="outlined"
            style={styles.input}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Address" />
        <Card.Content>
          <TextInput
            label="Street Address"
            value={formData.address}
            onChangeText={(text) => setFormData({ ...formData, address: text })}
            mode="outlined"
            style={styles.input}
          />
          <TextInput
            label="City"
            value={formData.city}
            onChangeText={(text) => setFormData({ ...formData, city: text })}
            mode="outlined"
            style={styles.input}
          />
          <TextInput
            label="State/Province"
            value={formData.state}
            onChangeText={(text) => setFormData({ ...formData, state: text })}
            mode="outlined"
            style={styles.input}
          />
          <TextInput
            label="Country"
            value={formData.country}
            onChangeText={(text) => setFormData({ ...formData, country: text })}
            mode="outlined"
            style={styles.input}
          />
          <TextInput
            label="Postal Code"
            value={formData.postal_code}
            onChangeText={(text) => setFormData({ ...formData, postal_code: text })}
            mode="outlined"
            style={styles.input}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Identification" />
        <Card.Content>
          <TextInput
            label="ID Type"
            value={formData.id_type}
            onChangeText={(text) => setFormData({ ...formData, id_type: text })}
            placeholder="Passport, ID Card, Driver License"
            mode="outlined"
            style={styles.input}
          />
          <TextInput
            label="ID Number"
            value={formData.id_number}
            onChangeText={(text) => setFormData({ ...formData, id_number: text })}
            mode="outlined"
            style={styles.input}
          />
          <TextInput
            label="Nationality"
            value={formData.nationality}
            onChangeText={(text) => setFormData({ ...formData, nationality: text })}
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
          Create Guest
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
  label: {
    marginBottom: 8,
    marginTop: 8,
  },
  segmented: {
    marginBottom: 12,
  },
  actions: {
    padding: 16,
    gap: 12,
    marginBottom: 24,
  },
  submitButton: {
    marginVertical: 4,
  },
  cancelButton: {
    marginVertical: 4,
  },
});
