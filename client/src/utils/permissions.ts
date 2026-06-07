export const SUPERUSER_PERMISSION = "platform:superuser";

export function permissionKey(slug: string, capability: string): string {
  return `${slug}:${capability}`;
}
