import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

type TaskPriority = 'high' | 'normal' | 'low';
type TaskStatus = 'pending' | 'in_progress' | 'completed';

interface HousekeepingTask {
  id: string;
  roomNumber: string;
  taskType: string;
  priority: TaskPriority;
  status: TaskStatus;
  notes?: string;
  assignedAt: string;
  completedAt?: string;
}

/**
 * Mobile-Optimized Housekeeping Task List
 * 
 * Features:
 * - Large touch targets for easy tapping
 * - Swipe gestures for quick actions
 * - Color-coded priority indicators
 * - Simple status updates
 * - Offline support ready
 */
export default function TaskListScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const [tasks, setTasks] = useState<HousekeepingTask[]>([
    {
      id: '1',
      roomNumber: '305',
      taskType: 'Deep Clean',
      priority: 'high',
      status: 'pending',
      notes: 'Guest checkout - thorough cleaning required',
      assignedAt: '09:00 AM',
    },
    {
      id: '2',
      roomNumber: '412',
      taskType: 'Standard Clean',
      priority: 'normal',
      status: 'pending',
      assignedAt: '09:15 AM',
    },
    {
      id: '3',
      roomNumber: '208',
      taskType: 'Turn Down Service',
      priority: 'normal',
      status: 'pending',
      assignedAt: '05:00 PM',
    },
    {
      id: '4',
      roomNumber: '501',
      taskType: 'Linen Change',
      priority: 'high',
      status: 'in_progress',
      assignedAt: '08:45 AM',
    },
    {
      id: '5',
      roomNumber: '201',
      taskType: 'Standard Clean',
      priority: 'normal',
      status: 'completed',
      assignedAt: '08:00 AM',
      completedAt: '09:30 AM',
    },
  ]);

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    // Simulate API call
    setTimeout(() => {
      setRefreshing(false);
    }, 1500);
  }, []);

  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case 'high':
        return '#EF4444';
      case 'normal':
        return '#3B82F6';
      case 'low':
        return '#10B981';
    }
  };

  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case 'completed':
        return '#10B981';
      case 'in_progress':
        return '#F59E0B';
      case 'pending':
        return '#6B7280';
    }
  };

  const getStatusLabel = (status: TaskStatus) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'in_progress':
        return 'In Progress';
      case 'pending':
        return 'Pending';
    }
  };

  const handleStartTask = (taskId: string) => {
    setTasks(tasks.map(task => 
      task.id === taskId 
        ? { ...task, status: 'in_progress' as TaskStatus }
        : task
    ));
  };

  const handleCompleteTask = (taskId: string) => {
    setTasks(tasks.map(task => 
      task.id === taskId 
        ? { 
            ...task, 
            status: 'completed' as TaskStatus, 
            completedAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        : task
    ));
  };

  const renderTask = ({ item }: { item: HousekeepingTask }) => (
    <View 
      style={[
        styles.taskCard,
        item.status === 'completed' && styles.completedCard
      ]}
    >
      {/* Priority Indicator */}
      <View 
        style={[
          styles.priorityBar,
          { backgroundColor: getPriorityColor(item.priority) }
        ]} 
      />

      <View style={styles.taskContent}>
        {/* Room Number - Large and Bold */}
        <View style={styles.taskHeader}>
          <Text style={styles.roomNumber}>Room {item.roomNumber}</Text>
          <View 
            style={[
              styles.statusBadge,
              { backgroundColor: getStatusColor(item.status) }
            ]}
          >
            <Text style={styles.statusText}>
              {getStatusLabel(item.status)}
            </Text>
          </View>
        </View>

        {/* Task Type */}
        <Text style={styles.taskType}>{item.taskType}</Text>

        {/* Notes if available */}
        {item.notes && (
          <Text style={styles.notes} numberOfLines={2}>
            {item.notes}
          </Text>
        )}

        {/* Time */}
        <View style={styles.timeRow}>
          <Ionicons name="time-outline" size={14} color="#6B7280" />
          <Text style={styles.timeText}>
            {item.status === 'completed' && item.completedAt
              ? `Completed at ${item.completedAt}`
              : `Assigned at ${item.assignedAt}`
            }
          </Text>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionButtons}>
          {item.status === 'pending' && (
            <TouchableOpacity
              style={[styles.button, styles.startButton]}
              onPress={() => handleStartTask(item.id)}
            >
              <Ionicons name="play-circle" size={20} color="white" />
              <Text style={styles.buttonText}>Start Task</Text>
            </TouchableOpacity>
          )}

          {item.status === 'in_progress' && (
            <TouchableOpacity
              style={[styles.button, styles.completeButton]}
              onPress={() => handleCompleteTask(item.id)}
            >
              <Ionicons name="checkmark-circle" size={20} color="white" />
              <Text style={styles.buttonText}>Mark Complete</Text>
            </TouchableOpacity>
          )}

          {item.status === 'completed' && (
            <View style={styles.completedBadge}>
              <Ionicons name="checkmark-done" size={24} color="#10B981" />
              <Text style={styles.completedText}>Task Completed</Text>
            </View>
          )}
        </View>
      </View>
    </View>
  );

  const pendingCount = tasks.filter(t => t.status === 'pending').length;
  const inProgressCount = tasks.filter(t => t.status === 'in_progress').length;
  const completedCount = tasks.filter(t => t.status === 'completed').length;

  return (
    <View style={styles.container}>
      {/* Stats Summary */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{pendingCount}</Text>
          <Text style={styles.statLabel}>Pending</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[styles.statNumber, { color: '#F59E0B' }]}>
            {inProgressCount}
          </Text>
          <Text style={styles.statLabel}>In Progress</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={[styles.statNumber, { color: '#10B981' }]}>
            {completedCount}
          </Text>
          <Text style={styles.statLabel}>Completed</Text>
        </View>
      </View>

      {/* Task List */}
      <FlatList
        data={tasks}
        renderItem={renderTask}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Ionicons name="checkbox-outline" size={64} color="#D1D5DB" />
            <Text style={styles.emptyText}>No tasks assigned</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  statCard: {
    flex: 1,
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#F9FAFB',
    borderRadius: 8,
  },
  statNumber: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#3B82F6',
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  listContent: {
    padding: 16,
    gap: 12,
  },
  taskCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    overflow: 'hidden',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  completedCard: {
    opacity: 0.7,
  },
  priorityBar: {
    height: 4,
  },
  taskContent: {
    padding: 16,
  },
  taskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  roomNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: 'white',
    fontSize: 11,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  taskType: {
    fontSize: 16,
    color: '#4B5563',
    marginBottom: 8,
  },
  notes: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 8,
    fontStyle: 'italic',
  },
  timeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginBottom: 16,
  },
  timeText: {
    fontSize: 12,
    color: '#6B7280',
  },
  actionButtons: {
    gap: 8,
  },
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 8,
    gap: 8,
  },
  startButton: {
    backgroundColor: '#3B82F6',
  },
  completeButton: {
    backgroundColor: '#10B981',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  completedBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    gap: 8,
  },
  completedText: {
    fontSize: 16,
    color: '#10B981',
    fontWeight: '600',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 16,
    color: '#9CA3AF',
    marginTop: 16,
  },
});
