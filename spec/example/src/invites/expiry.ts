const DAY_MS = 24 * 60 * 60 * 1000;

export const INVITE_TTL_MS = 7 * DAY_MS; // DEC-0002

export function expiresAt(createdAt: number): number {
  return createdAt + INVITE_TTL_MS; // stored once, DEC-0003
}
