import React, { useMemo } from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';
import {
  isSuperuser,
  isAdminOrManager,
  isFrontDeskOrAbove,
  isHousekeepingStaff,
  isMaintenanceStaff,
  isAccountantOrAbove,
  isPOSStaff,
  type User,
} from '../utils/permissions';

// Dashboard
import DashboardScreen from '../screens/dashboard/DashboardScreen';

// Reservations
import ReservationListScreen from '../screens/reservations/ReservationListScreen';
import ReservationDetailScreen from '../screens/reservations/ReservationDetailScreen';
import CreateReservationScreen from '../screens/reservations/CreateReservationScreen';
import ReservationEditScreen from '../screens/reservations/ReservationEditScreen';

// Guests
import GuestListScreen from '../screens/guests/GuestListScreen';
import GuestDetailScreen from '../screens/guests/GuestDetailScreen';
import CreateGuestScreen from '../screens/guests/CreateGuestScreen';
import GuestEditScreen from '../screens/guests/GuestEditScreen';

// Front Desk
import ArrivalsScreen from '../screens/frontdesk/ArrivalsScreen';
import DeparturesScreen from '../screens/frontdesk/DeparturesScreen';
import InHouseScreen from '../screens/frontdesk/InHouseScreen';

// Rooms
import RoomListScreen from '../screens/rooms/RoomListScreen';
import RoomDetailScreen from '../screens/rooms/RoomDetailScreen';

// Housekeeping
import HousekeepingListScreen from '../screens/housekeeping/HousekeepingListScreen';
import HousekeepingTaskScreen from '../screens/housekeeping/HousekeepingTaskScreen';
import RoomStatusScreen from '../screens/housekeeping/RoomStatusScreen';

// Maintenance
import MaintenanceListScreen from '../screens/maintenance/MaintenanceListScreen';
import MaintenanceRequestScreen from '../screens/maintenance/MaintenanceRequestScreen';
import CreateMaintenanceScreen from '../screens/maintenance/CreateMaintenanceScreen';

// Billing
import InvoiceDetailScreen from '../screens/billing/InvoiceDetailScreen';
import PaymentScreen from '../screens/billing/PaymentScreen';

// POS
import OrderHistoryScreen from '../screens/pos/OrderHistoryScreen';
import OrderDetailScreen from '../screens/pos/OrderDetailScreen';

// Reports
import ReportsScreen from '../screens/reports/ReportsScreen';

// Notifications
import NotificationListScreen from '../screens/notifications/NotificationListScreen';
import NotificationDetailScreen from '../screens/notifications/NotificationDetailScreen';

// Properties
import PropertyListScreen from '../screens/properties/PropertyListScreen';

// Profile
import ProfileScreen from '../screens/profile/ProfileScreen';

const Tab = createBottomTabNavigator();
const ReservationsStack = createNativeStackNavigator();
const GuestsStack = createNativeStackNavigator();
const FrontDeskStack = createNativeStackNavigator();
const RoomsStack = createNativeStackNavigator();
const HousekeepingStack = createNativeStackNavigator();
const MaintenanceStack = createNativeStackNavigator();
const BillingStack = createNativeStackNavigator();
const POSStack = createNativeStackNavigator();
const NotificationsStack = createNativeStackNavigator();
const PropertiesStack = createNativeStackNavigator();

function ReservationsNavigator() {
  return (
    <ReservationsStack.Navigator>
      <ReservationsStack.Screen
        name="ReservationList"
        component={ReservationListScreen}
        options={{ title: 'Reservations' }}
      />
      <ReservationsStack.Screen
        name="ReservationDetail"
        component={ReservationDetailScreen}
        options={{ title: 'Reservation Details' }}
      />
      <ReservationsStack.Screen
        name="ReservationEdit"
        component={ReservationEditScreen}
        options={{ title: 'Edit Reservation' }}
      />
      <ReservationsStack.Screen
        name="CreateReservation"
        component={CreateReservationScreen}
        options={{ title: 'New Reservation' }}
      />
    </ReservationsStack.Navigator>
  );
}

function GuestsNavigator() {
  return (
    <GuestsStack.Navigator>
      <GuestsStack.Screen
        name="GuestList"
        component={GuestListScreen}
        options={{ title: 'Guests' }}
      />
      <GuestsStack.Screen
        name="GuestDetail"
        component={GuestDetailScreen}
        options={{ title: 'Guest Details' }}
      />
      <GuestsStack.Screen
        name="GuestEdit"
        component={GuestEditScreen}
        options={{ title: 'Edit Guest' }}
      />
      <GuestsStack.Screen
        name="CreateGuest"
        component={CreateGuestScreen}
        options={{ title: 'New Guest' }}
      />
    </GuestsStack.Navigator>
  );
}

function FrontDeskNavigator() {
  return (
    <FrontDeskStack.Navigator>
      <FrontDeskStack.Screen
        name="Arrivals"
        component={ArrivalsScreen}
        options={{ title: 'Arrivals' }}
      />
      <FrontDeskStack.Screen
        name="Departures"
        component={DeparturesScreen}
        options={{ title: 'Departures' }}
      />
      <FrontDeskStack.Screen
        name="InHouse"
        component={InHouseScreen}
        options={{ title: 'In-House' }}
      />
    </FrontDeskStack.Navigator>
  );
}

function RoomsNavigator() {
  return (
    <RoomsStack.Navigator>
      <RoomsStack.Screen
        name="RoomList"
        component={RoomListScreen}
        options={{ title: 'Rooms' }}
      />
      <RoomsStack.Screen
        name="RoomDetail"
        component={RoomDetailScreen}
        options={{ title: 'Room Details' }}
      />
    </RoomsStack.Navigator>
  );
}

function HousekeepingNavigator() {
  return (
    <HousekeepingStack.Navigator>
      <HousekeepingStack.Screen
        name="HousekeepingList"
        component={HousekeepingListScreen}
        options={{ title: 'Housekeeping' }}
      />
      <HousekeepingStack.Screen
        name="HousekeepingTask"
        component={HousekeepingTaskScreen}
        options={{ title: 'Task Details' }}
      />
      <HousekeepingStack.Screen
        name="RoomStatus"
        component={RoomStatusScreen}
        options={{ title: 'Room Status' }}
      />
    </HousekeepingStack.Navigator>
  );
}

function MaintenanceNavigator() {
  return (
    <MaintenanceStack.Navigator>
      <MaintenanceStack.Screen
        name="MaintenanceList"
        component={MaintenanceListScreen}
        options={{ title: 'Maintenance' }}
      />
      <MaintenanceStack.Screen
        name="MaintenanceRequest"
        component={MaintenanceRequestScreen}
        options={{ title: 'Request Details' }}
      />
      <MaintenanceStack.Screen
        name="CreateMaintenance"
        component={CreateMaintenanceScreen}
        options={{ title: 'New Request' }}
      />
    </MaintenanceStack.Navigator>
  );
}

function BillingNavigator() {
  return (
    <BillingStack.Navigator>
      <BillingStack.Screen
        name="InvoiceDetail"
        component={InvoiceDetailScreen}
        options={{ title: 'Invoice Details' }}
      />
      <BillingStack.Screen
        name="PaymentScreen"
        component={PaymentScreen}
        options={{ title: 'Record Payment' }}
      />
    </BillingStack.Navigator>
  );
}

function POSNavigator() {
  return (
    <POSStack.Navigator>
      <POSStack.Screen
        name="OrderHistory"
        component={OrderHistoryScreen}
        options={{ title: 'POS Orders' }}
      />
      <POSStack.Screen
        name="OrderDetailScreen"
        component={OrderDetailScreen}
        options={{ title: 'Order Details' }}
      />
    </POSStack.Navigator>
  );
}

function NotificationsNavigator() {
  return (
    <NotificationsStack.Navigator>
      <NotificationsStack.Screen
        name="NotificationList"
        component={NotificationListScreen}
        options={{ title: 'Notifications' }}
      />
      <NotificationsStack.Screen
        name="NotificationDetail"
        component={NotificationDetailScreen}
        options={{ title: 'Notification Details' }}
      />
    </NotificationsStack.Navigator>
  );
}

function PropertiesNavigator() {
  return (
    <PropertiesStack.Navigator>
      <PropertiesStack.Screen
        name="PropertyList"
        component={PropertyListScreen}
        options={{ title: 'Properties' }}
      />
    </PropertiesStack.Navigator>
  );
}

export default function MainNavigator() {
  const { user } = useAuth();

  // Define which screens should be visible based on permissions
  const visibleScreens = useMemo(() => {
    const screens = {
      dashboard: isFrontDeskOrAbove(user as User) || isAdminOrManager(user as User),
      properties: isSuperuser(user as User) || isAdminOrManager(user as User),
      reservations: isFrontDeskOrAbove(user as User),
      guests: isFrontDeskOrAbove(user as User),
      frontDesk: isFrontDeskOrAbove(user as User),
      rooms: true, // All users
      housekeeping: isHousekeepingStaff(user as User),
      maintenance: isMaintenanceStaff(user as User),
      billing: isAccountantOrAbove(user as User),
      pos: isPOSStaff(user as User),
      reports: isAdminOrManager(user as User),
      notifications: true, // All users
      profile: true, // All users
    };
    return screens;
  }, [user]);

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap = 'home';

          if (route.name === 'Dashboard') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Reservations') {
            iconName = focused ? 'calendar' : 'calendar-outline';
          } else if (route.name === 'Guests') {
            iconName = focused ? 'people' : 'people-outline';
          } else if (route.name === 'FrontDesk') {
            iconName = focused ? 'desktop' : 'desktop-outline';
          } else if (route.name === 'Rooms') {
            iconName = focused ? 'business' : 'business-outline';
          } else if (route.name === 'Housekeeping') {
            iconName = focused ? 'bed' : 'bed-outline';
          } else if (route.name === 'Maintenance') {
            iconName = focused ? 'construct' : 'construct-outline';
          } else if (route.name === 'Billing') {
            iconName = focused ? 'card' : 'card-outline';
          } else if (route.name === 'POS') {
            iconName = focused ? 'restaurant' : 'restaurant-outline';
          } else if (route.name === 'Reports') {
            iconName = focused ? 'bar-chart' : 'bar-chart-outline';
          } else if (route.name === 'Notifications') {
            iconName = focused ? 'notifications' : 'notifications-outline';
          } else if (route.name === 'Properties') {
            iconName = focused ? 'briefcase' : 'briefcase-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#1a73e8',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      {visibleScreens.dashboard && (
        <Tab.Screen
          name="Dashboard"
          component={DashboardScreen}
          options={{ title: 'Dashboard' }}
        />
      )}
      {visibleScreens.properties && (
        <Tab.Screen
          name="Properties"
          component={PropertiesNavigator}
          options={{ headerShown: false }}
        />
      )}
      {visibleScreens.reservations && (
        <Tab.Screen
          name="Reservations"
          component={ReservationsNavigator}
          options={{ headerShown: false }}
        />
      )}
      {visibleScreens.guests && (
        <Tab.Screen
          name="Guests"
          component={GuestsNavigator}
          options={{ headerShown: false }}
        />
      )}
      {visibleScreens.frontDesk && (
        <Tab.Screen
          name="FrontDesk"
          component={FrontDeskNavigator}
          options={{ headerShown: false, title: 'Front Desk' }}
        />
      )}
      {visibleScreens.rooms && (
        <Tab.Screen
          name="Rooms"
          component={RoomsNavigator}
          options={{ headerShown: false }}
        />
      )}
      {visibleScreens.housekeeping && (
        <Tab.Screen
          name="Housekeeping"
          component={HousekeepingNavigator}
          options={{ headerShown: false }}
        />
      )}
      {visibleScreens.maintenance && (
        <Tab.Screen
          name="Maintenance"
          component={MaintenanceNavigator}
          options={{ headerShown: false }}
        />
      )}
      {visibleScreens.billing && (
        <Tab.Screen
          name="Billing"
          component={BillingNavigator}
          options={{ headerShown: false }}
        />
      )}
      {visibleScreens.pos && (
        <Tab.Screen
          name="POS"
          component={POSNavigator}
          options={{ headerShown: false }}
        />
      )}
      {visibleScreens.reports && (
        <Tab.Screen
          name="Reports"
          component={ReportsScreen}
          options={{ title: 'Reports' }}
        />
      )}
      {visibleScreens.notifications && (
        <Tab.Screen
          name="Notifications"
          component={NotificationsNavigator}
          options={{ headerShown: false }}
        />
      )}
      {visibleScreens.profile && (
        <Tab.Screen
          name="Profile"
          component={ProfileScreen}
          options={{ title: 'Profile' }}
        />
      )}
    </Tab.Navigator>
  );
}
