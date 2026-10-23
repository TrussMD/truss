---
type: decision
id: DEC-0002
title: Invite links expire after 7 days, and admins can revoke them
status: accepted
date: 2026-08-04
impact: high
accepted_by: "@marcus"
supersedes: DEC-0001
carries:
  - PROB-0001
  - RES-0001#F3
  - RES-0001#F4
---
## Context

72-hour links expire over the weekend for admins who invite on Fridays (RES-0001 F3). Admins also want to cut access off early (RES-0001 F4).

## Decision

Invite links expire 7 days after they are created. An admin can revoke any link, effective immediately.

## Consequences

A forwarded link stays usable for longer, which revocation offsets. Supersedes DEC-0001.
