---
type: plan
id: PLAN-0001
title: Build invite links
status: done
date: 2026-08-05
approved_by: "@priya"
carries:
  - CHG-0001
  - DEC-0002
---
**Goal.** Ship PRD-0001 AC1 to AC4 in one change.

## Tasks

1. Add the `invites` table with `role`, `expires_at` and `revoked_at`.
2. Create, revoke and join endpoints.
3. Expiry and revocation checks on join.
4. Audit event on every join.
5. Admin UI: create, copy and revoke.

## Done when

All four acceptance criteria pass in the end-to-end tests.
