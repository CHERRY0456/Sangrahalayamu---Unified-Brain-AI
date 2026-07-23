/**
 * Verifies if an active user's permissions array contains the required permission tag.
 */
export function hasPermission(userPermissions: string[] | null | undefined, requiredPermission: string): boolean {
  if (!userPermissions) return false;
  return userPermissions.includes(requiredPermission);
}
