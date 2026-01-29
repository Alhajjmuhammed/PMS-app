/**
 * Role-Based Permission Helper for React Native
 * Centralizes permission checking logic for the mobile app
 */

export type UserRole = 
  | 'ADMIN'
  | 'MANAGER'
  | 'FRONT_DESK'
  | 'HOUSEKEEPING'
  | 'MAINTENANCE'
  | 'ACCOUNTANT'
  | 'POS_STAFF'
  | 'GUEST';

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_superuser?: boolean;
  assigned_property?: number | null;
}

/**
 * Check if user is superuser
 */
export const isSuperuser = (user: User | null): boolean => {
  return user?.is_superuser === true;
};

/**
 * Check if user has Admin or Manager role
 */
export const isAdminOrManager = (user: User | null): boolean => {
  if (!user) return false;
  return isSuperuser(user) || ['ADMIN', 'MANAGER'].includes(user.role);
};

/**
 * Check if user has Front Desk or above role
 */
export const isFrontDeskOrAbove = (user: User | null): boolean => {
  if (!user) return false;
  return isSuperuser(user) || ['ADMIN', 'MANAGER', 'FRONT_DESK'].includes(user.role);
};

/**
 * Check if user has Housekeeping staff role
 */
export const isHousekeepingStaff = (user: User | null): boolean => {
  if (!user) return false;
  return isSuperuser(user) || ['ADMIN', 'MANAGER', 'HOUSEKEEPING'].includes(user.role);
};

/**
 * Check if user has Maintenance staff role
 */
export const isMaintenanceStaff = (user: User | null): boolean => {
  if (!user) return false;
  return isSuperuser(user) || ['ADMIN', 'MANAGER', 'MAINTENANCE'].includes(user.role);
};

/**
 * Check if user has Accountant or above role
 */
export const isAccountantOrAbove = (user: User | null): boolean => {
  if (!user) return false;
  return isSuperuser(user) || ['ADMIN', 'MANAGER', 'ACCOUNTANT', 'FRONT_DESK'].includes(user.role);
};

/**
 * Check if user has POS staff role
 */
export const isPOSStaff = (user: User | null): boolean => {
  if (!user) return false;
  return isSuperuser(user) || ['ADMIN', 'MANAGER', 'POS_STAFF'].includes(user.role);
};

/**
 * Check if user can manage properties
 */
export const canManageProperties = (user: User | null): boolean => {
  return isSuperuser(user);
};

/**
 * Check if user can manage users
 */
export const canManageUsers = (user: User | null): boolean => {
  return isSuperuser(user);
};

/**
 * Navigation screen permission mapping
 */
export interface NavScreen {
  name: string;
  label: string;
  icon?: string;
  permission: (user: User | null) => boolean;
}

/**
 * Define all navigation screens with their required permissions
 */
export const navigationScreens: NavScreen[] = [
  {
    name: 'Dashboard',
    label: 'Dashboard',
    permission: (user) => isFrontDeskOrAbove(user) || isAdminOrManager(user),
  },
  {
    name: 'Properties',
    label: 'Properties',
    permission: (user) => isSuperuser(user) || isAdminOrManager(user),
  },
  {
    name: 'Users',
    label: 'Users',
    permission: (user) => canManageUsers(user),
  },
  {
    name: 'Reservations',
    label: 'Reservations',
    permission: (user) => isFrontDeskOrAbove(user),
  },
  {
    name: 'Guests',
    label: 'Guests',
    permission: (user) => isFrontDeskOrAbove(user),
  },
  {
    name: 'Rooms',
    label: 'Rooms',
    permission: () => true, // All authenticated users
  },
  {
    name: 'Housekeeping',
    label: 'Housekeeping',
    permission: (user) => isHousekeepingStaff(user),
  },
  {
    name: 'Maintenance',
    label: 'Maintenance',
    permission: (user) => isMaintenanceStaff(user),
  },
  {
    name: 'Billing',
    label: 'Billing',
    permission: (user) => isAccountantOrAbove(user),
  },
  {
    name: 'POS',
    label: 'POS',
    permission: (user) => isPOSStaff(user),
  },
  {
    name: 'Reports',
    label: 'Reports',
    permission: (user) => isAdminOrManager(user),
  },
];

/**
 * Filter navigation screens based on user permissions
 */
export const getAuthorizedScreens = (user: User | null): NavScreen[] => {
  return navigationScreens.filter(screen => screen.permission(user));
};

/**
 * Check if user can access a specific screen
 */
export const canAccessScreen = (user: User | null, screenName: string): boolean => {
  const screen = navigationScreens.find(nav => nav.name === screenName);
  if (!screen) return true; // Allow access to undefined screens
  return screen.permission(user);
};

/**
 * Get user's default landing screen based on role
 */
export const getDefaultScreen = (user: User | null): string => {
  if (!user) return 'Login';
  
  if (isSuperuser(user)) return 'Properties';
  if (isAdminOrManager(user)) return 'Dashboard';
  if (isFrontDeskOrAbove(user)) return 'Reservations';
  if (isHousekeepingStaff(user)) return 'Housekeeping';
  if (isMaintenanceStaff(user)) return 'Maintenance';
  if (isPOSStaff(user)) return 'POS';
  
  return 'Rooms'; // Default for guests or undefined roles
};
