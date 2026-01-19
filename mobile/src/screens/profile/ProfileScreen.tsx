import React from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Card, Text, Button, Divider, Avatar, List } from 'react-native-paper';
import { useAuth } from '../../contexts/AuthContext';

export default function ProfileScreen() {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Logout', style: 'destructive', onPress: logout },
    ]);
  };

  const getRoleLabel = (role: string) => {
    const roles: { [key: string]: string } = {
      ADMIN: 'Administrator',
      MANAGER: 'Manager',
      FRONT_DESK: 'Front Desk',
      HOUSEKEEPING: 'Housekeeping',
      MAINTENANCE: 'Maintenance',
      ACCOUNTANT: 'Accountant',
      POS_STAFF: 'POS Staff',
      GUEST: 'Guest',
    };
    return roles[role] || role;
  };

  const getInitials = () => {
    if (user?.first_name && user?.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    return user?.email?.[0]?.toUpperCase() || '?';
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.profileCard}>
        <Card.Content style={styles.profileContent}>
          <Avatar.Text
            size={80}
            label={getInitials()}
            style={styles.avatar}
          />
          <Text variant="headlineSmall" style={styles.name}>
            {user?.first_name} {user?.last_name}
          </Text>
          <Text variant="bodyMedium" style={styles.email}>
            {user?.email}
          </Text>
          <View style={styles.roleChip}>
            <Text style={styles.roleText}>
              {getRoleLabel(user?.role || '')}
            </Text>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <List.Section>
            <List.Subheader>Account Information</List.Subheader>
            
            <List.Item
              title="Email"
              description={user?.email}
              left={props => <List.Icon {...props} icon="email" />}
            />
            
            <Divider />
            
            <List.Item
              title="Role"
              description={getRoleLabel(user?.role || '')}
              left={props => <List.Icon {...props} icon="badge-account" />}
            />
            
            <Divider />
            
            <List.Item
              title="Property"
              description={user?.property_name || 'All Properties'}
              left={props => <List.Icon {...props} icon="office-building" />}
            />
          </List.Section>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <List.Section>
            <List.Subheader>Settings</List.Subheader>
            
            <List.Item
              title="Notifications"
              description="Manage push notifications"
              left={props => <List.Icon {...props} icon="bell" />}
              right={props => <List.Icon {...props} icon="chevron-right" />}
              onPress={() => {}}
            />
            
            <Divider />
            
            <List.Item
              title="Change Password"
              description="Update your password"
              left={props => <List.Icon {...props} icon="lock" />}
              right={props => <List.Icon {...props} icon="chevron-right" />}
              onPress={() => {}}
            />
          </List.Section>
        </Card.Content>
      </Card>

      <View style={styles.logoutContainer}>
        <Button
          mode="outlined"
          onPress={handleLogout}
          icon="logout"
          style={styles.logoutButton}
          textColor="#d32f2f"
        >
          Logout
        </Button>
      </View>

      <Text variant="bodySmall" style={styles.version}>
        Hotel PMS Mobile v1.0.0
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  profileCard: {
    margin: 16,
  },
  profileContent: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  avatar: {
    backgroundColor: '#1a73e8',
  },
  name: {
    marginTop: 16,
    fontWeight: 'bold',
  },
  email: {
    color: '#666',
    marginTop: 4,
  },
  roleChip: {
    backgroundColor: '#e3f2fd',
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 16,
    marginTop: 12,
  },
  roleText: {
    color: '#1a73e8',
    fontWeight: '500',
  },
  card: {
    marginHorizontal: 16,
    marginBottom: 16,
  },
  logoutContainer: {
    padding: 16,
  },
  logoutButton: {
    borderColor: '#d32f2f',
  },
  version: {
    textAlign: 'center',
    color: '#999',
    marginBottom: 24,
  },
});
