// Rentido Role-Based Access Control (RBAC) & Authorization Helper

export type RoleType =
  | 'SUPER_ADMIN'
  | 'ADMIN'
  | 'OPERATIONS_ADMIN'
  | 'FINANCE_ADMIN'
  | 'SUPPORT_ADMIN'
  | 'VERIFICATION_ADMIN'
  | 'OWNER'
  | 'RENTER'
  | 'DRIVER'
  | 'SERVICE_PROVIDER';

export interface UserRoleRecord {
  id: number;
  role: RoleType | string;
  is_active: boolean;
  assigned_at?: string;
}

export interface AuthUser {
  id: number;
  email: string;
  username: string;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  is_email_verified?: boolean;
  is_phone_verified?: boolean;
  is_staff?: boolean;
  is_superuser?: boolean;
  roles?: (UserRoleRecord | string)[];
  renter_profile?: any;
  owner_profile?: any;
}

/**
 * Extracts active role string array from user payload.
 */
export function getUserRoles(user: AuthUser | null | undefined): string[] {
  if (!user) return [];
  if (!user.roles || !Array.isArray(user.roles)) return [];
  return user.roles
    .map((r) => (typeof r === 'string' ? r : r.is_active !== false ? r.role : null))
    .filter((r): r is string => Boolean(r));
}

/**
 * Checks if user holds any administrative privileges.
 */
export function isAdminUser(user: AuthUser | null | undefined): boolean {
  if (!user) return false;
  if (user.is_superuser || user.is_staff) return true;
  const roles = getUserRoles(user);
  const adminRoles = [
    'SUPER_ADMIN',
    'ADMIN',
    'OPERATIONS_ADMIN',
    'FINANCE_ADMIN',
    'SUPPORT_ADMIN',
    'VERIFICATION_ADMIN',
  ];
  return roles.some((r) => adminRoles.includes(r));
}

/**
 * Checks if user holds Equipment Owner role.
 */
export function isOwnerUser(user: AuthUser | null | undefined): boolean {
  if (!user) return false;
  if (isAdminUser(user)) return true; // Admins can manage owner actions
  const roles = getUserRoles(user);
  return roles.includes('OWNER') || Boolean(user.owner_profile);
}

/**
 * Checks if user is a Renter.
 */
export function isRenterUser(user: AuthUser | null | undefined): boolean {
  if (!user) return false;
  const roles = getUserRoles(user);
  return roles.includes('RENTER') || (!isAdminUser(user) && !roles.includes('OWNER'));
}

/**
 * Determines primary operational role for UI presentation and default view.
 */
export function getPrimaryRole(user: AuthUser | null | undefined): 'ADMIN' | 'OWNER' | 'RENTER' | 'GUEST' {
  if (!user) return 'GUEST';
  if (isAdminUser(user)) return 'ADMIN';
  if (getUserRoles(user).includes('OWNER')) return 'OWNER';
  return 'RENTER';
}

/**
 * Human readable role label with icon emoji.
 */
export function getRoleBadgeInfo(user: AuthUser | null | undefined): {
  title: string;
  badge: string;
  colorClass: string;
  bgClass: string;
} {
  const role = getPrimaryRole(user);
  switch (role) {
    case 'ADMIN':
      return {
        title: 'Platform Administrator',
        badge: '🛡️ Super Admin',
        colorClass: 'text-purple-700 border-purple-200 bg-purple-50',
        bgClass: 'from-purple-600 to-indigo-600',
      };
    case 'OWNER':
      return {
        title: 'Equipment Host / Owner',
        badge: '📷 Equipment Owner',
        colorClass: 'text-emerald-700 border-emerald-200 bg-emerald-50',
        bgClass: 'from-emerald-600 to-teal-600',
      };
    case 'RENTER':
      return {
        title: 'Verified Renter',
        badge: '🎒 Verified Renter',
        colorClass: 'text-indigo-700 border-indigo-200 bg-indigo-50',
        bgClass: 'from-indigo-600 to-violet-600',
      };
    default:
      return {
        title: 'Guest Visitor',
        badge: 'Guest',
        colorClass: 'text-gray-700 border-gray-200 bg-gray-50',
        bgClass: 'from-gray-600 to-gray-700',
      };
  }
}
