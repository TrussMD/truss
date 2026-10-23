---
type: change
id: CHG-0001
title: Invite teammates by link
status: shipped
date: 2026-08-05
kind: add
user_facing: true
branch: feat/invite-links
pr: 318
carries:
  - PRD-0001
  - FEAT-0001
  - DEC-0002
  - DEC-0003
---
## Summary

Role-scoped invite links with a 7-day expiry, revocation and audit logging. Creates FEAT-0001. Touches `src/invites/`.

## Release note

Invite teammates with a link, no email address needed. Links last 7 days, and you can revoke one at any time.
