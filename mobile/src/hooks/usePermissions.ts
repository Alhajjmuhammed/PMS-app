/**
 * usePermissions Hook for React Native
 * Easy access to permission checks in mobile components
 */

import { useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import type { User } from '../utils/permissions';
import {
  isSuperuser,
  isAdminOrManager,
  isFrontDeskOrAbove,
  isHousekeepingStaff,
  isMaintenanceStaff,
  isAccountantOrAbove,
  isPOSStaff,
  canManageProperties,
  canManageUsers,
} from '../utils/permissions';

export interface Permissions {
  isSuperuser: boolean;
  isAdminOrManager: boolean;
  isFrontDeskOrAbove: boolean;
  isHousekeepingStaff: boolean;
  isMaintenanceStaff: boolean;
  isAccountantOrAbove: boolean;
  isPOSStaff: boolean;
  canManageProperties: boolean;
  canManageUsers: boolean;
  canViewReports: boolean;
  canManageReservations: boolean;
  canManageGuests: boolean;
  canViewBilling: boolean;
  canManageRoomStatus: boolean;
}

export function usePermissions(): Permissions {
  const { user } = useAuth();

  return useMemo(() => {
    const typedUser = user as User | null;
    
    return {
      isSuperuser: isSuperuser(typedUser),
      isAdminOrManager: isAdminOrManager(typedUser),
      isFrontDeskOrAbove: isFrontDeskOrAbove(typedUser),
      isHousekeepingStaff: isHousekeepingStaff(typedUser),
      isMaintenanceStaff: isMaintenanceStaff(typedUser),
      isAccountantOrAbove: isAccountantOrAbove(typedUser),
      isPOSStaff: isPOSStaff(typedUser),
      canManageProperties: canManageProperties(typedUser),
      canManageUsers: canManageUsers(typedUser),
      canViewReports: isAdminOrManager(typedUser),
      canManageReservations: isFrontDeskOrAbove(typedUser),
      canManageGuests: isFrontDeskOrAbove(typedUser),
      canViewBilling: isAccountantOrAbove(typedUser),
      canManageRoomStatus: isHousekeepingStaff(typedUser),
    };
  }, [user]);
}
