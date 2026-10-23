export function isUsable(invite: { expires_at: number; revoked_at: number | null }, now: number): boolean {
  // Read on every join, never cached (BUG-0001).
  return invite.revoked_at === null && now < invite.expires_at;
}
