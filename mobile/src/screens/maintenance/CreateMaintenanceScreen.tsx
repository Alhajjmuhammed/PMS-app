import React from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { TextInput, Button, SegmentedButtons, Text } from 'react-native-paper';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { maintenanceApi } from '../../services/api';
import { useNavigation } from '@react-navigation/native';

export default function CreateMaintenanceScreen() {
  const navigation = useNavigation();
  const queryClient = useQueryClient();

  const [title, setTitle] = React.useState('');
  const [description, setDescription] = React.useState('');
  const [location, setLocation] = React.useState('');
  const [roomNumber, setRoomNumber] = React.useState('');
  const [category, setCategory] = React.useState('GENERAL');
  const [priority, setPriority] = React.useState('MEDIUM');

  const createMutation = useMutation({
    mutationFn: () =>
      maintenanceApi.createRequest({
        title,
        description,
        location: roomNumber ? '' : location,
        room: roomNumber || null,
        category,
        priority,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenanceRequests'] });
      Alert.alert('Success', 'Maintenance request created!', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    },
    onError: (error: any) => {
      Alert.alert('Error', error.response?.data?.error || 'Failed to create request');
    },
  });

  const handleSubmit = () => {
    if (!title.trim()) {
      Alert.alert('Error', 'Please enter a title');
      return;
    }
    if (!description.trim()) {
      Alert.alert('Error', 'Please enter a description');
      return;
    }
    if (!location.trim() && !roomNumber.trim()) {
      Alert.alert('Error', 'Please enter a location or room number');
      return;
    }
    createMutation.mutate();
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.form}>
        <TextInput
          mode="outlined"
          label="Title *"
          value={title}
          onChangeText={setTitle}
          style={styles.input}
          placeholder="Brief description of the issue"
        />

        <TextInput
          mode="outlined"
          label="Room Number"
          value={roomNumber}
          onChangeText={setRoomNumber}
          style={styles.input}
          placeholder="e.g., 101"
          keyboardType="number-pad"
        />

        <TextInput
          mode="outlined"
          label="Location (if not a room)"
          value={location}
          onChangeText={setLocation}
          style={styles.input}
          placeholder="e.g., Lobby, Pool Area"
          disabled={!!roomNumber}
        />

        <Text variant="labelLarge" style={styles.label}>Category</Text>
        <SegmentedButtons
          value={category}
          onValueChange={setCategory}
          buttons={[
            { value: 'PLUMBING', label: 'Plumb' },
            { value: 'ELECTRICAL', label: 'Elec' },
            { value: 'HVAC', label: 'HVAC' },
            { value: 'GENERAL', label: 'General' },
          ]}
          style={styles.segments}
        />

        <Text variant="labelLarge" style={styles.label}>Priority</Text>
        <SegmentedButtons
          value={priority}
          onValueChange={setPriority}
          buttons={[
            { value: 'LOW', label: 'Low' },
            { value: 'MEDIUM', label: 'Medium' },
            { value: 'HIGH', label: 'High' },
            { value: 'CRITICAL', label: 'Critical' },
          ]}
          style={styles.segments}
        />

        <TextInput
          mode="outlined"
          label="Description *"
          value={description}
          onChangeText={setDescription}
          style={styles.input}
          multiline
          numberOfLines={5}
          placeholder="Detailed description of the issue..."
        />

        <Button
          mode="contained"
          onPress={handleSubmit}
          loading={createMutation.isPending}
          disabled={createMutation.isPending}
          style={styles.button}
        >
          Create Request
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
  form: {
    padding: 16,
  },
  input: {
    marginBottom: 16,
    backgroundColor: '#fff',
  },
  label: {
    marginBottom: 8,
    color: '#666',
  },
  segments: {
    marginBottom: 16,
  },
  button: {
    marginTop: 16,
    paddingVertical: 8,
  },
});
