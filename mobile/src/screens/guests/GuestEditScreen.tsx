import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, TextInput, Button, Switch } from 'react-native-paper';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { guestsApi } from '../../services/apiServices';
import { Loading, ErrorMessage } from '../../components';

export default function GuestEditScreen({ route, navigation }: any) {
  const { id } = route.params;
  const queryClient = useQueryClient();

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    country: '',
    postal_code: '',
    id_type: '',
    id_number: '',
    nationality: '',
    vip_status: false,
    notes: '',
  });

  const { data: guest, isLoading } = useQuery({
    queryKey: ['guests', id],
    queryFn: () => guestsApi.get(id),
  });

  useEffect(() => {
    if (guest?.data) {
      const g = guest.data;
      setFormData({
        first_name: g.first_name || '',
        last_name: g.last_name || '',
        email: g.email || '',
        phone: g.phone || '',
        address: g.address || '',
        city: g.city || '',
        state: g.state || '',
        country: g.country || '',
        postal_code: g.postal_code || '',
        id_type: g.id_type || '',
        id_number: g.id_number || '',
        nationality: g.nationality || '',
        vip_status: g.vip_status || false,
        notes: g.notes || '',
      });
    }
  }, [guest]);

  const updateMutation = useMutation({
    mutationFn: (data: any) => guestsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guests', id] });
      queryClient.invalidateQueries({ queryKey: ['guests'] });
      navigation.goBack();
    },
  });

  const handleSubmit = () => {
    updateMutation.mutate(formData);
  };

  if (isLoading) return <Loading message="Loading guest..." />;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text variant="titleMedium" style={styles.sectionTitle}>Personal Information</Text>
        
        <TextInput
          label="First Name *"
          value={formData.first_name}
          onChangeText={(text) => setFormData({ ...formData, first_name: text })}
          style={styles.input}
          mode="outlined"
        />
        
        <TextInput
          label="Last Name *"
          value={formData.last_name}
          onChangeText={(text) => setFormData({ ...formData, last_name: text })}
          style={styles.input}
          mode="outlined"
        />
        
        <TextInput
          label="Email"
          value={formData.email}
          onChangeText={(text) => setFormData({ ...formData, email: text })}
          style={styles.input}
          mode="outlined"
          keyboardType="email-address"
          autoCapitalize="none"
        />
        
        <TextInput
          label="Phone *"
          value={formData.phone}
          onChangeText={(text) => setFormData({ ...formData, phone: text })}
          style={styles.input}
          mode="outlined"
          keyboardType="phone-pad"
        />

        <TextInput
          label="Nationality"
          value={formData.nationality}
          onChangeText={(text) => setFormData({ ...formData, nationality: text })}
          style={styles.input}
          mode="outlined"
        />
      </View>

      <View style={styles.section}>
        <Text variant="titleMedium" style={styles.sectionTitle}>Address</Text>
        
        <TextInput
          label="Street Address"
          value={formData.address}
          onChangeText={(text) => setFormData({ ...formData, address: text })}
          style={styles.input}
          mode="outlined"
          multiline
          numberOfLines={2}
        />
        
        <TextInput
          label="City"
          value={formData.city}
          onChangeText={(text) => setFormData({ ...formData, city: text })}
          style={styles.input}
          mode="outlined"
        />
        
        <TextInput
          label="State/Province"
          value={formData.state}
          onChangeText={(text) => setFormData({ ...formData, state: text })}
          style={styles.input}
          mode="outlined"
        />
        
        <TextInput
          label="Country"
          value={formData.country}
          onChangeText={(text) => setFormData({ ...formData, country: text })}
          style={styles.input}
          mode="outlined"
        />
        
        <TextInput
          label="Postal Code"
          value={formData.postal_code}
          onChangeText={(text) => setFormData({ ...formData, postal_code: text })}
          style={styles.input}
          mode="outlined"
        />
      </View>

      <View style={styles.section}>
        <Text variant="titleMedium" style={styles.sectionTitle}>Identification</Text>
        
        <TextInput
          label="ID Type"
          value={formData.id_type}
          onChangeText={(text) => setFormData({ ...formData, id_type: text })}
          style={styles.input}
          mode="outlined"
          placeholder="e.g., Passport, National ID"
        />
        
        <TextInput
          label="ID Number"
          value={formData.id_number}
          onChangeText={(text) => setFormData({ ...formData, id_number: text })}
          style={styles.input}
          mode="outlined"
        />
      </View>

      <View style={styles.section}>
        <Text variant="titleMedium" style={styles.sectionTitle}>Additional Information</Text>
        
        <View style={styles.switchRow}>
          <Text variant="bodyLarge">VIP Status</Text>
          <Switch
            value={formData.vip_status}
            onValueChange={(value) => setFormData({ ...formData, vip_status: value })}
          />
        </View>

        <TextInput
          label="Notes"
          value={formData.notes}
          onChangeText={(text) => setFormData({ ...formData, notes: text })}
          style={styles.input}
          mode="outlined"
          multiline
          numberOfLines={4}
        />
      </View>

      <View style={styles.actions}>
        <Button
          mode="outlined"
          onPress={() => navigation.goBack()}
          style={styles.button}
        >
          Cancel
        </Button>
        <Button
          mode="contained"
          onPress={handleSubmit}
          loading={updateMutation.isPending}
          disabled={!formData.first_name || !formData.last_name || !formData.phone}
          style={styles.button}
        >
          Save Changes
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
  section: {
    backgroundColor: 'white',
    padding: 16,
    marginBottom: 8,
  },
  sectionTitle: {
    marginBottom: 16,
    fontWeight: 'bold',
  },
  input: {
    marginBottom: 12,
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
    padding: 16,
    backgroundColor: 'white',
    marginBottom: 16,
  },
  button: {
    flex: 1,
  },
});
