import React from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Card, Text, Button, Chip, Divider, TextInput } from 'react-native-paper';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { housekeepingApi } from '../../services/api';
import { useNavigation, useRoute } from '@react-navigation/native';

export default function HousekeepingTaskScreen() {
  const navigation = useNavigation();
  const route = useRoute<any>();
  const queryClient = useQueryClient();
  const { taskId } = route.params;

  const [notes, setNotes] = React.useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['housekeepingTask', taskId],
    queryFn: () => housekeepingApi.getTaskDetail(taskId),
  });

  const startMutation = useMutation({
    mutationFn: () => housekeepingApi.startTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['housekeepingTask', taskId] });
      queryClient.invalidateQueries({ queryKey: ['housekeepingTasks'] });
    },
  });

  const completeMutation = useMutation({
    mutationFn: () => housekeepingApi.completeTask(taskId, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['housekeepingTask', taskId] });
      queryClient.invalidateQueries({ queryKey: ['housekeepingTasks'] });
      Alert.alert('Success', 'Task completed!', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    },
  });

  const task = data?.data;

  if (isLoading || !task) {
    return (
      <View style={styles.loading}>
        <Text>Loading...</Text>
      </View>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'PENDING':
        return '#ff9800';
      case 'IN_PROGRESS':
        return '#2196f3';
      case 'COMPLETED':
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
            <Text variant="headlineMedium">Room {task.room_number}</Text>
            <Chip
              style={{ backgroundColor: getStatusColor(task.status) }}
              textStyle={{ color: '#fff' }}
            >
              {task.status}
            </Chip>
          </View>

          <Text variant="bodyLarge" style={styles.roomType}>
            {task.room_type}
          </Text>

          <Divider style={styles.divider} />

          <View style={styles.detailRow}>
            <Text variant="bodyMedium" style={styles.label}>Task Type:</Text>
            <Text variant="bodyMedium">{task.task_type}</Text>
          </View>

          <View style={styles.detailRow}>
            <Text variant="bodyMedium" style={styles.label}>Priority:</Text>
            <Chip compact>{task.priority}</Chip>
          </View>

          <View style={styles.detailRow}>
            <Text variant="bodyMedium" style={styles.label}>Assigned To:</Text>
            <Text variant="bodyMedium">{task.assigned_to_name || 'Unassigned'}</Text>
          </View>

          {task.scheduled_date && (
            <View style={styles.detailRow}>
              <Text variant="bodyMedium" style={styles.label}>Scheduled:</Text>
              <Text variant="bodyMedium">{task.scheduled_date}</Text>
            </View>
          )}

          {task.special_instructions && (
            <>
              <Divider style={styles.divider} />
              <Text variant="bodyMedium" style={styles.label}>Special Instructions:</Text>
              <Text variant="bodyMedium" style={styles.instructions}>
                {task.special_instructions}
              </Text>
            </>
          )}
        </Card.Content>
      </Card>

      {task.status === 'IN_PROGRESS' && (
        <Card style={styles.card}>
          <Card.Content>
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Completion Notes
            </Text>
            <TextInput
              mode="outlined"
              multiline
              numberOfLines={4}
              placeholder="Add any notes about the task..."
              value={notes}
              onChangeText={setNotes}
              style={styles.notesInput}
            />
          </Card.Content>
        </Card>
      )}

      <View style={styles.actions}>
        {task.status === 'PENDING' && (
          <Button
            mode="contained"
            onPress={() => startMutation.mutate()}
            loading={startMutation.isPending}
            icon="play"
            style={styles.button}
          >
            Start Task
          </Button>
        )}

        {task.status === 'IN_PROGRESS' && (
          <Button
            mode="contained"
            onPress={() => completeMutation.mutate()}
            loading={completeMutation.isPending}
            icon="check"
            style={styles.button}
          >
            Complete Task
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
    alignItems: 'center',
  },
  roomType: {
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
  instructions: {
    marginTop: 8,
    color: '#ff9800',
  },
  sectionTitle: {
    marginBottom: 12,
  },
  notesInput: {
    backgroundColor: '#fff',
  },
  actions: {
    padding: 16,
  },
  button: {
    paddingVertical: 8,
  },
});
