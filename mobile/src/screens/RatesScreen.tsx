import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Text, Card, DataTable, Chip, SegmentedButtons } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { ratesApi } from '../services/apiServices';
import { Loading, ErrorMessage } from '../components';

export default function RatesScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const [view, setView] = useState('plans');

  const { data: ratePlans, isLoading: loadingPlans, error: errorPlans, refetch: refetchPlans } = useQuery({
    queryKey: ['ratePlans'],
    queryFn: () => ratesApi.plans.list(),
  });

  const { data: seasons, isLoading: loadingSeasons, error: errorSeasons, refetch: refetchSeasons } = useQuery({
    queryKey: ['seasons'],
    queryFn: () => ratesApi.seasons.list(),
  });

  const { data: roomRates, isLoading: loadingRates, error: errorRates, refetch: refetchRates } = useQuery({
    queryKey: ['roomRates'],
    queryFn: () => ratesApi.roomRates.list(),
  });

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([refetchPlans(), refetchSeasons(), refetchRates()]);
    setRefreshing(false);
  };

  const isLoading = loadingPlans || loadingSeasons || loadingRates;
  const error = errorPlans || errorSeasons || errorRates;

  if (isLoading) return <Loading message="Loading rates..." />;
  if (error) return <ErrorMessage message="Failed to load rates" onRetry={onRefresh} />;

  return (
    <View style={styles.container}>
      <SegmentedButtons
        value={view}
        onValueChange={setView}
        buttons={[
          { value: 'plans', label: 'Rate Plans' },
          { value: 'seasons', label: 'Seasons' },
          { value: 'rates', label: 'Room Rates' },
        ]}
        style={styles.segmented}
      />

      <ScrollView
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {view === 'plans' && (
          <Card style={styles.card}>
            <Card.Title title="Rate Plans" subtitle={`${ratePlans?.data?.results?.length || 0} plans`} />
            <Card.Content>
              {ratePlans?.data?.results?.map((plan: any) => (
                <Card key={plan.id} style={styles.itemCard}>
                  <Card.Content>
                    <View style={styles.itemHeader}>
                      <View>
                        <Text variant="titleMedium">{plan.name}</Text>
                        <Text variant="bodySmall" style={styles.code}>Code: {plan.code}</Text>
                      </View>
                      <Chip mode="outlined" style={styles.typeChip}>
                        {plan.rate_type}
                      </Chip>
                    </View>
                    
                    {plan.description && (
                      <Text variant="bodyMedium" style={styles.description}>
                        {plan.description}
                      </Text>
                    )}
                    
                    <View style={styles.details}>
                      {plan.min_nights && (
                        <Text variant="bodySmall">Min nights: {plan.min_nights}</Text>
                      )}
                      {plan.max_nights && (
                        <Text variant="bodySmall">Max nights: {plan.max_nights}</Text>
                      )}
                      <Chip
                        icon={plan.is_refundable ? 'check' : 'close'}
                        style={styles.refundChip}
                      >
                        {plan.is_refundable ? 'Refundable' : 'Non-refundable'}
                      </Chip>
                    </View>
                  </Card.Content>
                </Card>
              ))}
            </Card.Content>
          </Card>
        )}

        {view === 'seasons' && (
          <Card style={styles.card}>
            <Card.Title title="Seasons" subtitle={`${seasons?.data?.results?.length || 0} seasons`} />
            <Card.Content>
              <DataTable>
                <DataTable.Header>
                  <DataTable.Title>Season</DataTable.Title>
                  <DataTable.Title>Start Date</DataTable.Title>
                  <DataTable.Title>End Date</DataTable.Title>
                  <DataTable.Title numeric>Priority</DataTable.Title>
                </DataTable.Header>

                {seasons?.data?.results?.map((season: any) => (
                  <DataTable.Row key={season.id}>
                    <DataTable.Cell>{season.name}</DataTable.Cell>
                    <DataTable.Cell>{season.start_date}</DataTable.Cell>
                    <DataTable.Cell>{season.end_date}</DataTable.Cell>
                    <DataTable.Cell numeric>{season.priority}</DataTable.Cell>
                  </DataTable.Row>
                ))}
              </DataTable>
            </Card.Content>
          </Card>
        )}

        {view === 'rates' && (
          <Card style={styles.card}>
            <Card.Title title="Room Rates" subtitle={`${roomRates?.data?.results?.length || 0} rates`} />
            <Card.Content>
              <DataTable>
                <DataTable.Header>
                  <DataTable.Title>Rate Plan</DataTable.Title>
                  <DataTable.Title>Room Type</DataTable.Title>
                  <DataTable.Title numeric>Single</DataTable.Title>
                  <DataTable.Title numeric>Double</DataTable.Title>
                </DataTable.Header>

                {roomRates?.data?.results?.map((rate: any) => (
                  <DataTable.Row key={rate.id}>
                    <DataTable.Cell>{rate.rate_plan_name}</DataTable.Cell>
                    <DataTable.Cell>{rate.room_type_name}</DataTable.Cell>
                    <DataTable.Cell numeric>${rate.single_rate}</DataTable.Cell>
                    <DataTable.Cell numeric>${rate.double_rate}</DataTable.Cell>
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
  card: {
    margin: 16,
    marginTop: 0,
  },
  itemCard: {
    marginBottom: 12,
  },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  code: {
    color: '#666',
    marginTop: 4,
  },
  typeChip: {
    height: 28,
  },
  description: {
    marginVertical: 8,
    color: '#666',
  },
  details: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 8,
    alignItems: 'center',
  },
  refundChip: {
    marginLeft: 'auto',
  },
});
