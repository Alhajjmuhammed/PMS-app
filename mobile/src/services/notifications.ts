import { Platform } from 'react-native';
import Constants from 'expo-constants';
import api from './api';

// Check if running in Expo Go
const isExpoGo = Constants.appOwnership === 'expo';

// Dynamically import notifications only if not in Expo Go
let Notifications: any = null;

// Only configure notifications in development/production builds
if (!isExpoGo) {
  try {
    Notifications = require('expo-notifications');
    // Configure notification behavior
    Notifications.setNotificationHandler({
      handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: true,
        shouldShowBanner: true,
        shouldShowList: true,
      }),
    });
  } catch (error) {
    console.log('Push notifications not available');
  }
}

export const registerForPushNotifications = async (): Promise<string | null> => {
  try {
    // Skip push notification registration in Expo Go
    if (isExpoGo) {
      console.log('📱 Running in Expo Go - Push notifications are not available.');
      console.log('ℹ️  To test push notifications, create a development build:');
      console.log('   npx expo run:android  OR  npx expo run:ios');
      return null;
    }

    if (!Notifications) {
      console.log('⚠️  Notifications module not available');
      return null;
    }

    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('default', {
        name: 'default',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF231F7C',
      });
    }

    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== 'granted') {
      console.warn('⚠️  Failed to get push token for push notification!');
      return null;
    }

    const { data: token } = await Notifications.getExpoPushTokenAsync({
      projectId: 'your-project-id', // Replace with your Expo project ID
    });

    // Register token with backend
    await api.post('/notifications/register-device/', {
      token,
      device_type: Platform.OS,
    });

    console.log('✅ Push notifications registered successfully');
    return token;
  } catch (error) {
    console.error('❌ Error registering for push notifications:', error);
    return null;
  }
};

export const addNotificationReceivedListener = (
  callback: (notification: any) => void
) => {
  if (!Notifications) return { remove: () => {} };
  return Notifications.addNotificationReceivedListener(callback);
};

export const addNotificationResponseListener = (
  callback: (response: any) => void
) => {
  if (!Notifications) return { remove: () => {} };
  return Notifications.addNotificationResponseReceivedListener(callback);
};

export const schedulePushNotification = async (
  title: string,
  body: string,
  data?: any,
  seconds: number = 1
) => {
  if (!Notifications) return;
  await Notifications.scheduleNotificationAsync({
    content: {
      title,
      body,
      data,
    },
    trigger: null, // Use null for immediate notification, or pass a proper trigger object
  });
};

export const cancelAllNotifications = async () => {
  if (!Notifications) return;
  await Notifications.cancelAllScheduledNotificationsAsync();
};

export const getBadgeCount = async (): Promise<number> => {
  if (!Notifications) return 0;
  return await Notifications.getBadgeCountAsync();
};

export const setBadgeCount = async (count: number) => {
  if (!Notifications) return;
  await Notifications.setBadgeCountAsync(count);
};
