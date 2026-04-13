import React, { useEffect, useRef, useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { Snackbar } from 'react-native-paper';
import Constants from 'expo-constants';
import {
  registerForPushNotifications,
  addNotificationReceivedListener,
  addNotificationResponseListener,
} from '../services/notifications';
import { useAuth } from '../contexts/AuthContext';

// Check if running in Expo Go
const isExpoGo = Constants.appOwnership === 'expo';

interface NotificationProviderProps {
  children: React.ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const { user } = useAuth();
  const isAuthenticated = !!user;
  const [notification, setNotification] = useState<any>(null);
  const [visible, setVisible] = useState(false);
  
  const notificationListener = useRef<any>(null);
  const responseListener = useRef<any>(null);
  
  // Skip notification setup in Expo Go
  if (isExpoGo) {
    return <View style={styles.container}>{children}</View>;
  }

  useEffect(() => {
    if (isAuthenticated) {
      // Register for push notifications (will skip if in Expo Go)
      registerForPushNotifications().catch((error) => {
        console.log('Push notification registration skipped:', error?.message || 'Not available in Expo Go');
      });

      // Handle notifications received while app is foregrounded
      notificationListener.current = addNotificationReceivedListener((notification) => {
        setNotification(notification);
        setVisible(true);
      });

      // Handle notification responses (user tapped notification)
      responseListener.current = addNotificationResponseListener((response) => {
        const data = response.notification.request.content.data;
        // Navigate based on notification data
        if (data?.screen) {
          // You can implement navigation logic here
          console.log('Navigate to:', data.screen);
        }
      });

      return () => {
        if (notificationListener.current) {
          notificationListener.current.remove();
        }
        if (responseListener.current) {
          responseListener.current.remove();
        }
      };
    }
  }, [isAuthenticated]);

  return (
    <View style={styles.container}>
      {children}
      <Snackbar
        visible={visible}
        onDismiss={() => setVisible(false)}
        duration={4000}
        action={{
          label: 'View',
          onPress: () => {
            // Handle notification tap
            setVisible(false);
          },
        }}
      >
        {notification?.request.content.title}: {notification?.request.content.body}
      </Snackbar>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});

export default NotificationProvider;
