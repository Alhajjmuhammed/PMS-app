import React from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Card, Text, Button, Chip, Divider, TextInput } from 'react-native-paper';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { maintenanceApi } from '../../services/api';
import { useNavigation, useRoute } from '@react-navigation/native';

export default function MaintenanceRequestScreen() {
  const navigation = useNavigation();
  const route = useRoute<any>();
  const queryClient = useQueryClient();
  const { requestId } = route.params;

  const [notes, setNotes] = React.useState('');
  const [cost, setCost] = React.useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['maintenanceRequest', requestId],
    queryFn: () => maintenanceApi.getRequestDetail(requestId),
  });

  const startMutation = useMutation({
    mutationFn: () => maintenanceApi.startRequest(requestId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenanceRequest', requestId] });
      queryClient.invalidateQueries({ queryKey: ['maintenanceRequests'] });
    },
  });

  const completeMutation = useMutation({
    mutationFn: () =>
      maintenanceApi.completeRequest(requestId, {
        notes,
        actual_cost: cost ? parseFloat(cost) : undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenanceRequest', requestId] });
      queryClient.invalidateQueries({ queryKey: ['maintenanceRequests'] });
      Alert.alert('Success', 'Request completed!', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    },
  });

  const request = data?.data?.request;
  const logs = data?.data?.logs || [];

  if (isLoading || !request) {
    return (
      <View style={styles.loading}>
        <Text>Loading...</Text>
      </View>
    );
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'CRITICAL':
        return '#d32f2f';
      case 'HIGH':
        return '#f44336';
      case 'MEDIUM':
        return '#ff9800';
      case 'LOW':
        return '#4caf50';
      default:
        return '#9e9e9e';
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.header}>
            <Text variant="headlineSmall">{request.title}</Text>
            <Chip
              style={{ backgroundColor: getPriorityColor(request.priority) }}
              textStyle={{ color: '#fff' }}
            >
              {request.priority}
            </Chip>
          </View>

          <Text variant="bodySmall" style={styles.requestNumber}>
            {request.request_number}
          </Text>

          <Divider style={styles.divider} />

          <View style={styles.detailRow}>
            <Text variant="bodyMedium" style={styles.label}>Location:</Text>
            <Text variant="bodyMedium">
              {request.room_number ? `Room ${request.room_number}` : request.location}
            </Text>
          </View>

          <View style={styles.detailRow}>
            <Text variant="bodyMedium" style={styles.label}>Category:</Text>
            <Chip compact>{request.category}</Chip>
          </View>

          <View style={styles.detailRow}>
            <Text variant="bodyMedium" style={styles.label}>Status:</Text>
            <Chip compact>{request.status}</Chip>
          </View>

          <View style={styles.detailRow}>
            <Text variant="bodyMedium" style={styles.label}>Reported by:</Text>
            <Text variant="bodyMedium">{request.reported_by_name}</Text>
          </View>

          {request.assigned_to_name && (
            <View style={styles.detailRow}>
              <Text variant="bodyMedium" style={styles.label}>Assigned to:</Text>
              <Text variant="bodyMedium">{request.assigned_to_name}</Text>
            </View>
          )}

          <Divider style={styles.divider} />

          <Text variant="bodyMedium" style={styles.label}>Description:</Text>
          <Text variant="bodyMedium" style={styles.description}>
            {request.description}
          </Text>
        </Card.Content>
      </Card>

      {/* Activity Log */}
      {logs.length > 0 && (
        <Card style={styles.card}>
          <Card.Title title="Activity Log" />
          <Card.Content>
            {logs.map((log: any, index: number) => (
              <View key={log.id || index} style={styles.logItem}>
                <View style={styles.logHeader}>
                  <Text variant="bodyMedium" style={{ fontWeight: 'bold' }}>
                    {log.action}
                  </Text>
                  <Text variant="bodySmall" style={styles.logTime}>
                    {new Date(log.created_at).toLocaleString()}
                  </Text>
                </View>
                {log.notes && (
                  <Text variant="bodySmall" style={styles.logNotes}>
                    {log.notes}
                  </Text>
                )}
                <Text variant="bodySmall" style={styles.logBy}>
                  By: {log.performed_by_name}
                </Text>
              </View>
            ))}
          </Card.Content>
        </Card>
      )}

      {/* Completion Form */}
      {request.status === 'IN_PROGRESS' && (
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Complete Request
            </Text>
            <TextInput
              mode="outlined"
              label="Resolution Notes"
              multiline
              numberOfLines={4}
              placeholder="Describe the work done..."
              value={notes}
              onChangeText={setNotes}
              style={styles.input}
            />
            <TextInput
              mode="outlined"
              label="Actual Cost (optional)"
              keyboardType="decimal-pad"
              value={cost}
              onChangeText={setCost}
              style={styles.input}
            />
          </Card.Content>
        </Card>
      )}

      <View style={styles.actions}>
        {(request.status === 'OPEN' || request.status === 'ASSIGNED') && (
          <Button
            mode="contained"
            onPress={() => startMutation.mutate()}
            loading={startMutation.isPending}
            icon="play"
            style={styles.button}
          >
            Start Work
          </Button>
        )}

        {request.status === 'IN_PROGRESS' && (
          <Button
            mode="contained"
            onPress={() => completeMutation.mutate()}
            loading={completeMutation.isPending}
            icon="check"
            style={styles.button}
          >
            Complete Request
          </Button>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  card: {
    margin: 16,
    marginBottom: 8,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  requestNumber: {
    color: '#666',
    marginTop: 4,
  },
  divider: {
    marginVertical: 16,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  label: {
    color: '#666',
  },
  description: {
    marginTop: 8,
  },
  logItem: {
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  logHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  logTime: {
    color: '#666',
  },
  logNotes: {
    marginTop: 4,
  },
  logBy: {
    color: '#666',
    marginTop: 4,
  },
  sectionTitle: {
    marginBottom: 12,
  },
  input: {
    marginBottom: 12,
    backgroundColor: '#fff',
  },
  actions: {
    padding: 16,
  },
  button: {
    paddingVertical: 8,
  },
});
