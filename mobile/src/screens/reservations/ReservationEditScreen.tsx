import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Text, TextInput, Button, Menu } from 'react-native-paper';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { reservationsApi, roomsApi, guestsApi } from '../../services/apiServices';
import { Loading } from '../../components';

export default function ReservationEditScreen({ route, navigation }: any) {
  const { id } = route.params;
  const queryClient = useQueryClient();

  const [formData, setFormData] = useState({
    check_in_date: new Date().toISOString().split('T')[0],
    check_out_date: new Date().toISOString().split('T')[0],
    room: '',
    guest: '',
    adults: '1',
    children: '0',
    status: 'PENDING',
    special_requests: '',
  });

  const [roomMenuVisible, setRoomMenuVisible] = useState(false);
  const [guestMenuVisible, setGuestMenuVisible] = useState(false);
  const [statusMenuVisible, setStatusMenuVisible] = useState(false);

  const { data: reservation, isLoading } = useQuery({
    queryKey: ['reservations', id],
    queryFn: () => reservationsApi.get(id),
  });

  const { data: rooms } = useQuery({
    queryKey: ['rooms'],
    queryFn: () => roomsApi.list(),
  });

  const { data: guests } = useQuery({
    queryKey: ['guests'],
    queryFn: () => guestsApi.list(),
  });

  useEffect(() => {
    if (reservation?.data) {
      const r = reservation.data;
      setFormData({
        check_in_date: r.check_in_date,
        check_out_date: r.check_out_date,
        room: r.room?.toString() || '',
        guest: r.guest?.toString() || '',
        adults: r.adults?.toString() || '1',
        children: r.children?.toString() || '0',
        status: r.status || 'PENDING',
        special_requests: r.special_requests || '',
      });
    }
  }, [reservation]);

  const updateMutation = useMutation({
    mutationFn: (data: any) => reservationsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reservations', id] });
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
      navigation.goBack();
    },
  });

  const handleSubmit = () => {
    const data = {
      check_in_date: formData.check_in_date,
      check_out_date: formData.check_out_date,
      room: parseInt(formData.room),
      guest: parseInt(formData.guest),
      adults: parseInt(formData.adults),
      children: parseInt(formData.children),
      status: formData.status,
      special_requests: formData.special_requests,
    };
    updateMutation.mutate(data);
  };

  const getSelectedRoomLabel = () => {
    if (!formData.room) return 'Select Room';
    const room = rooms?.data?.results?.find((r: any) => r.id.toString() === formData.room);
    return room ? `${room.number} - ${room.room_type_name}` : 'Select Room';
  };

  const getSelectedGuestLabel = () => {
    if (!formData.guest) return 'Select Guest';
    const guest = guests?.data?.results?.find((g: any) => g.id.toString() === formData.guest);
    return guest ? `${guest.first_name} ${guest.last_name}` : 'Select Guest';
  };

  const getStatusLabel = () => {
    const statuses: Record<string, string> = {
      PENDING: 'Pending',
      CONFIRMED: 'Confirmed',
      CHECKED_IN: 'Checked In',
      CHECKED_OUT: 'Checked Out',
      CANCELLED: 'Cancelled',
      NO_SHOW: 'No Show',
    };
    return statuses[formData.status] || 'Select Status';
  };

  if (isLoading) return <Loading message="Loading reservation..." />;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text variant="titleMedium" style={styles.sectionTitle}>Dates</Text>
        
        <TextInput
          label="Check-in Date (YYYY-MM-DD) *"
          value={formData.check_in_date}
          onChangeText={(text) => setFormData({ ...formData, check_in_date: text })}
          style={styles.input}
          mode="outlined"
          placeholder="2024-01-15"
        />

        <TextInput
          label="Check-out Date (YYYY-MM-DD) *"
          value={formData.check_out_date}
          onChangeText={(text) => setFormData({ ...formData, check_out_date: text })}
          style={[styles.input, styles.marginTop]}
          mode="outlined"
          placeholder="2024-01-20"
        />
      </View>

      <View style={styles.section}>
        <Text variant="titleMedium" style={styles.sectionTitle}>Room & Guest</Text>
        
        <Text variant="bodyMedium" style={styles.label}>Room *</Text>
        <Menu
          visible={roomMenuVisible}
          onDismiss={() => setRoomMenuVisible(false)}
          anchor={
            <Button 
              mode="outlined" 
              onPress={() => setRoomMenuVisible(true)}
              style={styles.menuButton}
              contentStyle={styles.menuButtonContent}
            >
              {getSelectedRoomLabel()}
            </Button>
          }
        >
          {rooms?.data?.results?.map((room: any) => (
            <Menu.Item
              key={room.id}
              onPress={() => {
                setFormData({ ...formData, room: room.id.toString() });
                setRoomMenuVisible(false);
              }}
              title={`${room.number} - ${room.room_type_name}`}
            />
          ))}
        </Menu>

        <Text variant="bodyMedium" style={[styles.label, styles.marginTop]}>Guest *</Text>
        <Menu
          visible={guestMenuVisible}
          onDismiss={() => setGuestMenuVisible(false)}
          anchor={
            <Button 
              mode="outlined" 
              onPress={() => setGuestMenuVisible(true)}
              style={styles.menuButton}
              contentStyle={styles.menuButtonContent}
            >
              {getSelectedGuestLabel()}
            </Button>
          }
        >
          {guests?.data?.results?.map((guest: any) => (
            <Menu.Item
              key={guest.id}
              onPress={() => {
                setFormData({ ...formData, guest: guest.id.toString() });
                setGuestMenuVisible(false);
              }}
              title={`${guest.first_name} ${guest.last_name}`}
            />
          ))}
        </Menu>
      </View>

      <View style={styles.section}>
        <Text variant="titleMedium" style={styles.sectionTitle}>Occupancy</Text>
        
        <View style={styles.row}>
          <View style={styles.field}>
            <TextInput
              label="Adults *"
              value={formData.adults}
              onChangeText={(text) => setFormData({ ...formData, adults: text })}
              style={styles.input}
              mode="outlined"
              keyboardType="number-pad"
            />
          </View>
          
          <View style={styles.field}>
            <TextInput
              label="Children"
              value={formData.children}
              onChangeText={(text) => setFormData({ ...formData, children: text })}
              style={styles.input}
              mode="outlined"
              keyboardType="number-pad"
            />
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text variant="titleMedium" style={styles.sectionTitle}>Status & Notes</Text>
        
        <Text variant="bodyMedium" style={styles.label}>Status *</Text>
        <Menu
          visible={statusMenuVisible}
          onDismiss={() => setStatusMenuVisible(false)}
          anchor={
            <Button 
              mode="outlined" 
              onPress={() => setStatusMenuVisible(true)}
              style={styles.menuButton}
              contentStyle={styles.menuButtonContent}
            >
              {getStatusLabel()}
            </Button>
          }
        >
          <Menu.Item onPress={() => { setFormData({ ...formData, status: 'PENDING' }); setStatusMenuVisible(false); }} title="Pending" />
          <Menu.Item onPress={() => { setFormData({ ...formData, status: 'CONFIRMED' }); setStatusMenuVisible(false); }} title="Confirmed" />
          <Menu.Item onPress={() => { setFormData({ ...formData, status: 'CHECKED_IN' }); setStatusMenuVisible(false); }} title="Checked In" />
          <Menu.Item onPress={() => { setFormData({ ...formData, status: 'CHECKED_OUT' }); setStatusMenuVisible(false); }} title="Checked Out" />
          <Menu.Item onPress={() => { setFormData({ ...formData, status: 'CANCELLED' }); setStatusMenuVisible(false); }} title="Cancelled" />
          <Menu.Item onPress={() => { setFormData({ ...formData, status: 'NO_SHOW' }); setStatusMenuVisible(false); }} title="No Show" />
        </Menu>

        <TextInput
          label="Special Requests"
          value={formData.special_requests}
          onChangeText={(text) => setFormData({ ...formData, special_requests: text })}
          style={[styles.input, styles.marginTop]}
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
          disabled={!formData.room || !formData.guest}
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
  label: {
    marginBottom: 8,
    color: '#666',
  },
  marginTop: {
    marginTop: 16,
  },
  row: {
    flexDirection: 'row',
    gap: 12,
  },
  field: {
    flex: 1,
  },
  input: {
    backgroundColor: 'white',
  },
  menuButton: {
    justifyContent: 'flex-start',
  },
  menuButtonContent: {
    justifyContent: 'flex-start',
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
