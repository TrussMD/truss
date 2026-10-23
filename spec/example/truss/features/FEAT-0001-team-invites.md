---
type: feature
id: FEAT-0001
title: Team invites
status: live
date: 2026-08-04
owner: "@priya"
visibility: public
paths:
  - src/invites/**
carries:
  - DEC-0002
  - DEC-0003
---
## Behaviour

An admin creates an invite link for a role. Anyone with the link can join the workspace in that role.

- A link expires 7 days after it is created.
- An admin can revoke a link at any time. Revoking takes effect immediately.
- Every join is recorded in the audit log.

## Who it is for

Workspace admins adding teammates and contractors.
