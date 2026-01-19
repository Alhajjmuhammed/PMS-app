import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Text, Card, SegmentedButtons, DataTable } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { reportsApi } from '../../services/apiServices';
import { Loading, ErrorMessage } from '../../components';

export default function ReportsScreen() {
  const [view, setView] = useState('daily');
  const [refreshing, setRefreshing] = useState(false);
  const today = new Date().toISOString().split('T')[0];

  const { data: dailyStats, isLoading: loadingDaily, error: errorDaily, refetch: refetchDaily } = useQuery({
    queryKey: ['dailyStats', today],
    queryFn: () => reportsApi.dailyStats(today),
    enabled: view === 'daily',
  });

  const { data: occupancy, isLoading: loadingOccupancy, error: errorOccupancy, refetch: refetchOccupancy } = useQuery({
    queryKey: ['occupancyReport', today],
    queryFn: () => reportsApi.occupancy({ date: today }),
    enabled: view === 'occupancy',
  });

  const { data: revenue, isLoading: loadingRevenue, error: errorRevenue, refetch: refetchRevenue } = useQuery({
    queryKey: ['revenueReport', today],
    queryFn: () => reportsApi.revenue({ date: today }),
    enabled: view === 'revenue',
  });

  const onRefresh = async () => {
    setRefreshing(true);
    if (view === 'daily') await refetchDaily();
    if (view === 'occupancy') await refetchOccupancy();
    if (view === 'revenue') await refetchRevenue();
    setRefreshing(false);
  };

  const isLoading = loadingDaily || loadingOccupancy || loadingRevenue;
  const error = errorDaily || errorOccupancy || errorRevenue;

  if (isLoading) return <Loading message="Loading reports..." />;
  if (error) return <ErrorMessage message="Failed to load reports" onRetry={onRefresh} />;

  const renderDailyStats = () => {
    const stats = dailyStats?.data;
    if (!stats) return null;

    return (
      <View>
        <Card style={styles.card}>
          <Card.Title title="Occupancy Statistics" />
          <Card.Content>
            <View style={styles.statRow}>
              <View style={styles.stat}>
                <Text variant="headlineMedium">{stats.occupied_rooms || 0}</Text>
                <Text variant="bodySmall">Occupied Rooms</Text>
              </View>
              <View style={styles.stat}>
                <Text variant="headlineMedium">{stats.available_rooms || 0}</Text>
                <Text variant="bodySmall">Available Rooms</Text>
              </View>
              <View style={styles.stat}>
                <Text variant="headlineMedium">{stats.occupancy_percent?.toFixed(1) || 0}%</Text>
                <Text variant="bodySmall">Occupancy Rate</Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Title title="Revenue Statistics" />
          <Card.Content>
            <View style={styles.statRow}>
              <View style={styles.stat}>
                <Text variant="headlineMedium" style={styles.revenue}>
                  ${parseFloat(stats.room_revenue || 0).toFixed(0)}
                </Text>
                <Text variant="bodySmall">Room Revenue</Text>
              </View>
              <View style={styles.stat}>
                <Text variant="headlineMedium" style={styles.revenue}>
                  ${parseFloat(stats.total_revenue || 0).toFixed(0)}
                </Text>
                <Text variant="bodySmall">Total Revenue</Text>
              </View>
            </View>
            
            <View style={styles.row}>
              <Text variant="bodyMedium">ADR:</Text>
              <Text variant="titleMedium" style={styles.revenue}>
                ${parseFloat(stats.adr || 0).toFixed(2)}
              </Text>
            </View>
            <View style={styles.row}>
              <Text variant="bodyMedium">RevPAR:</Text>
              <Text variant="titleMedium" style={styles.revenue}>
                ${parseFloat(stats.revpar || 0).toFixed(2)}
              </Text>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Title title="Reservations" />
          <Card.Content>
            <View style={styles.statRow}>
              <View style={styles.stat}>
                <Text variant="headlineMedium">{stats.arrivals || 0}</Text>
                <Text variant="bodySmall">Arrivals</Text>
              </View>
              <View style={styles.stat}>
                <Text variant="headlineMedium">{stats.departures || 0}</Text>
                <Text variant="bodySmall">Departures</Text>
              </View>
              <View style={styles.stat}>
                <Text variant="headlineMedium">{stats.no_shows || 0}</Text>
                <Text variant="bodySmall">No Shows</Text>
              </View>
            </View>
          </Card.Content>
        </Card>
      </View>
    );
  };

  const renderOccupancyReport = () => {
    const data = occupancy?.data || {};
    
    return (
      <Card style={styles.card}>
        <Card.Title title="Occupancy Report" />
        <Card.Content>
          <DataTable>
            <DataTable.Header>
              <DataTable.Title>Metric</DataTable.Title>
              <DataTable.Title numeric>Value</DataTable.Title>
            </DataTable.Header>

            <DataTable.Row>
              <DataTable.Cell>Total Rooms</DataTable.Cell>
              <DataTable.Cell numeric>{data.total_rooms || 0}</DataTable.Cell>
            </DataTable.Row>

            <DataTable.Row>
              <DataTable.Cell>Occupied</DataTable.Cell>
              <DataTable.Cell numeric>{data.occupied_rooms || 0}</DataTable.Cell>
            </DataTable.Row>

            <DataTable.Row>
              <DataTable.Cell>Available</DataTable.Cell>
              <DataTable.Cell numeric>{data.available_rooms || 0}</DataTable.Cell>
            </DataTable.Row>

            <DataTable.Row>
              <DataTable.Cell>Out of Order</DataTable.Cell>
              <DataTable.Cell numeric>{data.out_of_order || 0}</DataTable.Cell>
            </DataTable.Row>

            <DataTable.Row>
              <DataTable.Cell>Occupancy %</DataTable.Cell>
              <DataTable.Cell numeric>{data.occupancy_percent?.toFixed(1) || 0}%</DataTable.Cell>
            </DataTable.Row>
          </DataTable>
        </Card.Content>
      </Card>
    );
  };

  const renderRevenueReport = () => {
    const data = revenue?.data || {};
    
    return (
      <View>
        <Card style={styles.card}>
          <Card.Title title="Revenue Breakdown" />
          <Card.Content>
            <DataTable>
              <DataTable.Header>
                <DataTable.Title>Category</DataTable.Title>
                <DataTable.Title numeric>Amount</DataTable.Title>
              </DataTable.Header>

              <DataTable.Row>
                <DataTable.Cell>Room Revenue</DataTable.Cell>
                <DataTable.Cell numeric>${parseFloat(data.room_revenue || 0).toFixed(2)}</DataTable.Cell>
              </DataTable.Row>

              <DataTable.Row>
                <DataTable.Cell>F&B Revenue</DataTable.Cell>
                <DataTable.Cell numeric>${parseFloat(data.fb_revenue || 0).toFixed(2)}</DataTable.Cell>
              </DataTable.Row>

              <DataTable.Row>
                <DataTable.Cell>Other Revenue</DataTable.Cell>
                <DataTable.Cell numeric>${parseFloat(data.other_revenue || 0).toFixed(2)}</DataTable.Cell>
              </DataTable.Row>

              <DataTable.Row>
                <DataTable.Cell><Text style={styles.totalLabel}>Total Revenue</Text></DataTable.Cell>
                <DataTable.Cell numeric>
                  <Text style={styles.totalValue}>${parseFloat(data.total_revenue || 0).toFixed(2)}</Text>
                </DataTable.Cell>
              </DataTable.Row>
            </DataTable>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Title title="Key Metrics" />
          <Card.Content>
            <View style={styles.row}>
              <Text variant="bodyMedium">Average Daily Rate (ADR):</Text>
              <Text variant="titleMedium" style={styles.revenue}>
                ${parseFloat(data.adr || 0).toFixed(2)}
              </Text>
            </View>
            <View style={styles.row}>
              <Text variant="bodyMedium">Revenue Per Available Room (RevPAR):</Text>
              <Text variant="titleMedium" style={styles.revenue}>
                ${parseFloat(data.revpar || 0).toFixed(2)}
              </Text>
            </View>
          </Card.Content>
        </Card>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <SegmentedButtons
        value={view}
        onValueChange={setView}
        buttons={[
          { value: 'daily', label: 'Daily' },
          { value: 'occupancy', label: 'Occupancy' },
          { value: 'revenue', label: 'Revenue' },
        ]}
        style={styles.segmented}
      />

      <ScrollView
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        {view === 'daily' && renderDailyStats()}
        {view === 'occupancy' && renderOccupancyReport()}
        {view === 'revenue' && renderRevenueReport()}
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
    marginBottom: 8,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginVertical: 8,
  },
  stat: {
    alignItems: 'center',
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
  },
  revenue: {
    color: '#4caf50',
    fontWeight: 'bold',
  },
  totalLabel: {
    fontWeight: 'bold',
    fontSize: 16,
  },
  totalValue: {
    fontWeight: 'bold',
    fontSize: 16,
    color: '#4caf50',
  },
});
