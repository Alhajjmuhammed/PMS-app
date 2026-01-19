import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Text, Card, Button, Chip, FAB, Portal, Modal, TextInput } from 'react-native-paper';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { maintenanceApi } from '../services/apiServices';
import { Loading, ErrorMessage } from '../components';

export default function MaintenanceScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<any>(null);
  const queryClient = useQueryClient();

  const { data: requests, isLoading, error, refetch } = useQuery({
    queryKey: ['maintenance'],
    queryFn: () => maintenanceApi.list(),
  });

  const resolveRequest = useMutation({
    mutationFn: ({ id, notes }: { id: number; notes: string }) =>
      maintenanceApi.resolve(id, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['maintenance'] });
      setSelectedRequest(null);
    },
  });

  const onRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  const getPriorityColor = (priority: string) => {
    const colors: any = {
      URGENT: '#f44336',
      HIGH: '#ff9800',
      MEDIUM: '#2196f3',
      LOW: '#4caf50',
    };
    return colors[priority] || '#9e9e9e';
  };

  const getStatusColor = (status: string) => {
    const colors: any = {
      REPORTED: '#f44336',
      IN_PROGRESS: '#ff9800',
      RESOLVED: '#4caf50',
      CLOSED: '#9e9e9e',
    };
    return colors[status] || '#9e9e9e';
  };

  if (isLoading) return <Loading message="Loading maintenance requests..." />;
  if (error) return <ErrorMessage message="Failed to load requests" onRetry={refetch} />;

  const stats = {
    urgent: requests?.data?.results?.filter((r: any) => r.priority === 'URGENT').length || 0,
    inProgress: requests?.data?.results?.filter((r: any) => r.status === 'IN_PROGRESS').length || 0,
    resolved: requests?.data?.results?.filter((r: any) => r.status === 'RESOLVED').length || 0,
  };

  return (
    <View style={styles.container}>
      <ScrollView
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {/* Stats */}
        <View style={styles.statsContainer}>
          <Card style={[styles.statCard, { borderLeftColor: '#f44336' }]}>
            <Card.Content>
              <Text variant="headlineMedium">{stats.urgent}</Text>
              <Text variant="bodySmall">Urgent</Text>
            </Card.Content>
          </Card>
          <Card style={[styles.statCard, { borderLeftColor: '#ff9800' }]}>
            <Card.Content>
              <Text variant="headlineMedium">{stats.inProgress}</Text>
              <Text variant="bodySmall">In Progress</Text>
            </Card.Content>
          </Card>
          <Card style={[styles.statCard, { borderLeftColor: '#4caf50' }]}>
            <Card.Content>
              <Text variant="headlineMedium">{stats.resolved}</Text>
              <Text variant="bodySmall">Resolved</Text>
            </Card.Content>
          </Card>
        </View>

        {/* Requests List */}
        {requests?.data?.results?.map((request: any) => (
          <Card
            key={request.id}
            style={styles.requestCard}
            onPress={() => setSelectedRequest(request)}
          >
            <Card.Content>
              <View style={styles.requestHeader}>
                <Text variant="titleMedium">{request.issue_type}</Text>
                <View style={styles.badges}>
                  <Chip
                    style={{ backgroundColor: getPriorityColor(request.priority) }}
                    textStyle={{ color: 'white', fontSize: 10 }}
                  >
                    {request.priority}
                  </Chip>
                  <Chip
                    style={{ backgroundColor: getStatusColor(request.status), marginLeft: 4 }}
                    textStyle={{ color: 'white', fontSize: 10 }}
                  >
                    {request.status}
                  </Chip>
                </View>
              </View>
              
              <Text variant="bodyMedium" style={styles.description}>
                {request.description}
              </Text>
              
              <View style={styles.requestFooter}>
                <Text variant="bodySmall">
                  {request.room_number ? `Room ${request.room_number}` : 'General'}
                </Text>
                <Text variant="bodySmall" style={styles.date}>
                  {new Date(request.created_at).toLocaleDateString()}
                </Text>
              </View>
            </Card.Content>
          </Card>
        ))}
      </ScrollView>

      {/* Request Detail Modal */}
      <Portal>
        <Modal
          visible={!!selectedRequest}
          onDismiss={() => setSelectedRequest(null)}
          contentContainerStyle={styles.modal}
        >
          {selectedRequest && (
            <Card>
              <Card.Title
                title={selectedRequest.issue_type}
                subtitle={`Room ${selectedRequest.room_number || 'N/A'}`}
              />
              <Card.Content>
                <View style={styles.modalBadges}>
                  <Chip style={{ backgroundColor: getPriorityColor(selectedRequest.priority) }}>
                    {selectedRequest.priority}
                  </Chip>
                  <Chip style={{ backgroundColor: getStatusColor(selectedRequest.status) }}>
                    {selectedRequest.status}
                  </Chip>
                </View>
                
                <Text variant="titleSmall" style={styles.sectionTitle}>Description:</Text>
                <Text variant="bodyMedium">{selectedRequest.description}</Text>
                
                <Text variant="titleSmall" style={styles.sectionTitle}>Reported:</Text>
                <Text variant="bodyMedium">
                  {new Date(selectedRequest.created_at).toLocaleString()}
                </Text>
                
                {selectedRequest.status !== 'RESOLVED' && (
                  <TextInput
                    label="Resolution Notes"
                    mode="outlined"
                    multiline
                    numberOfLines={3}
                    style={styles.input}
                  />
                )}
              </Card.Content>
              <Card.Actions>
                <Button onPress={() => setSelectedRequest(null)}>Close</Button>
                {selectedRequest.status !== 'RESOLVED' && (
                  <Button
                    mode="contained"
                    onPress={() => resolveRequest.mutate({ id: selectedRequest.id, notes: '' })}
                    loading={resolveRequest.isPending}
                  >
                    Mark Resolved
                  </Button>
                )}
              </Card.Actions>
            </Card>
          )}
        </Modal>
      </Portal>

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => setModalVisible(true)}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  statCard: {
    flex: 1,
    borderLeftWidth: 4,
  },
  requestCard: {
    margin: 16,
    marginTop: 0,
    marginBottom: 12,
  },
  requestHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  badges: {
    flexDirection: 'row',
  },
  description: {
    marginVertical: 8,
    color: '#666',
  },
  requestFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  date: {
    color: '#999',
  },
  modal: {
    backgroundColor: 'white',
    padding: 20,
    margin: 20,
  },
  modalBadges: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  sectionTitle: {
    marginTop: 12,
    marginBottom: 4,
    fontWeight: 'bold',
  },
  input: {
    marginTop: 12,
  },
  fab: {
    position: 'absolute',
    right: 16,
    bottom: 16,
  },
});
