import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Text, Card, DataTable, Chip, SegmentedButtons, Badge } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { channelsApi } from '../services/apiServices';
import { Loading, ErrorMessage } from '../components';

export default function ChannelsScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const [view, setView] = useState('channels');

  const { data: channels, isLoading: loadingChannels, error: errorChannels, refetch: refetchChannels } = useQuery({
    queryKey: ['channels'],
    queryFn: () => channelsApi.list(),
  });

  const { data: propertyChannels, isLoading: loadingProperty, error: errorProperty, refetch: refetchProperty } = useQuery({
    queryKey: ['propertyChannels'],
    queryFn: () => channelsApi.propertyChannels.list(),
  });

  const { data: mappings, isLoading: loadingMappings, error: errorMappings, refetch: refetchMappings } = useQuery({
    queryKey: ['roomMappings'],
    queryFn: () => channelsApi.roomMappings.list(),
  });

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([refetchChannels(), refetchProperty(), refetchMappings()]);
    setRefreshing(false);
  };

  const isLoading = loadingChannels || loadingProperty || loadingMappings;
  const error = errorChannels || errorProperty || errorMappings;

  if (isLoading) return <Loading message="Loading channels..." />;
  if (error) return <ErrorMessage message="Failed to load channels" onRetry={onRefresh} />;

  const getChannelTypeColor = (type: string) => {
    const colors: any = {
      OTA: '#2196f3',
      GDS: '#9c27b0',
      DIRECT: '#4caf50',
      META: '#ff9800',
      CORPORATE: '#607d8b',
    };
    return colors[type] || '#9e9e9e';
  };

  return (
    <View style={styles.container}>
      <SegmentedButtons
        value={view}
        onValueChange={setView}
        buttons={[
          { value: 'channels', label: 'Channels' },
          { value: 'connections', label: 'Connections' },
          { value: 'mappings', label: 'Mappings' },
        ]}
        style={styles.segmented}
      />

      <ScrollView
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {view === 'channels' && (
          <View style={styles.content}>
            {channels?.data?.results?.map((channel: any) => (
              <Card key={channel.id} style={styles.channelCard}>
                <Card.Content>
                  <View style={styles.channelHeader}>
                    <View>
                      <Text variant="titleLarge">{channel.name}</Text>
                      <Text variant="bodySmall" style={styles.code}>Code: {channel.code}</Text>
                    </View>
                    <View style={styles.badges}>
                      <Chip
                        style={{ backgroundColor: getChannelTypeColor(channel.channel_type) }}
                        textStyle={{ color: 'white' }}
                      >
                        {channel.channel_type}
                      </Chip>
                      {channel.is_active && (
                        <Badge style={styles.activeBadge}>Active</Badge>
                      )}
                    </View>
                  </View>
                  
                  <View style={styles.channelInfo}>
                    <View style={styles.infoItem}>
                      <Text variant="bodySmall" style={styles.infoLabel}>Commission</Text>
                      <Text variant="titleMedium">{channel.commission_percent}%</Text>
                    </View>
                  </View>
                </Card.Content>
              </Card>
            ))}
          </View>
        )}

        {view === 'connections' && (
          <Card style={styles.card}>
            <Card.Title
              title="Property Connections"
              subtitle={`${propertyChannels?.data?.results?.length || 0} connections`}
            />
            <Card.Content>
              <DataTable>
                <DataTable.Header>
                  <DataTable.Title>Channel</DataTable.Title>
                  <DataTable.Title>Property Code</DataTable.Title>
                  <DataTable.Title>Sync Status</DataTable.Title>
                  <DataTable.Title>Last Sync</DataTable.Title>
                </DataTable.Header>

                {propertyChannels?.data?.results?.map((conn: any) => (
                  <DataTable.Row key={conn.id}>
                    <DataTable.Cell>{conn.channel_name}</DataTable.Cell>
                    <DataTable.Cell>{conn.property_code}</DataTable.Cell>
                    <DataTable.Cell>
                      <View style={styles.syncChips}>
                        {conn.sync_rates && <Chip style={styles.smallChip}>Rates</Chip>}
                        {conn.sync_availability && <Chip style={styles.smallChip}>Avail</Chip>}
                        {conn.sync_reservations && <Chip style={styles.smallChip}>Res</Chip>}
                      </View>
                    </DataTable.Cell>
                    <DataTable.Cell>
                      {conn.last_sync_at
                        ? new Date(conn.last_sync_at).toLocaleString()
                        : 'Never'}
                    </DataTable.Cell>
                  </DataTable.Row>
                ))}
              </DataTable>
            </Card.Content>
          </Card>
        )}

        {view === 'mappings' && (
          <Card style={styles.card}>
            <Card.Title
              title="Room Type Mappings"
              subtitle={`${mappings?.data?.results?.length || 0} mappings`}
            />
            <Card.Content>
              <DataTable>
                <DataTable.Header>
                  <DataTable.Title>Room Type</DataTable.Title>
                  <DataTable.Title>Channel Code</DataTable.Title>
                  <DataTable.Title>Channel Name</DataTable.Title>
                  <DataTable.Title>Status</DataTable.Title>
                </DataTable.Header>

                {mappings?.data?.results?.map((mapping: any) => (
                  <DataTable.Row key={mapping.id}>
                    <DataTable.Cell>{mapping.room_type_name}</DataTable.Cell>
                    <DataTable.Cell>{mapping.channel_room_code}</DataTable.Cell>
                    <DataTable.Cell>{mapping.channel_room_name}</DataTable.Cell>
                    <DataTable.Cell>
                      <Chip
                        icon={mapping.is_active ? 'check' : 'close'}
                        style={{
                          backgroundColor: mapping.is_active ? '#4caf50' : '#f44336',
                        }}
                        textStyle={{ color: 'white', fontSize: 10 }}
                      >
                        {mapping.is_active ? 'Active' : 'Inactive'}
                      </Chip>
                    </DataTable.Cell>
                  </DataTable.Row>
                ))}
              </DataTable>
            </Card.Content>
          </Card>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  segmented: {
    margin: 16,
  },
  content: {
    padding: 16,
  },
  card: {
    margin: 16,
    marginTop: 0,
  },
  channelCard: {
    marginBottom: 16,
  },
  channelHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  code: {
    color: '#666',
    marginTop: 4,
  },
  badges: {
    flexDirection: 'row',
    gap: 8,
    alignItems: 'center',
  },
  activeBadge: {
    backgroundColor: '#4caf50',
  },
  channelInfo: {
    flexDirection: 'row',
    gap: 24,
    marginTop: 12,
  },
  infoItem: {
    flex: 1,
  },
  infoLabel: {
    color: '#666',
    marginBottom: 4,
  },
  syncChips: {
    flexDirection: 'row',
    gap: 4,
  },
  smallChip: {
    height: 24,
    fontSize: 10,
  },
});
