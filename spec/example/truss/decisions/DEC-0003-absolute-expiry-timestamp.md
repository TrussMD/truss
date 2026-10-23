---
type: decision
id: DEC-0003
title: Store an invite's expiry as an absolute timestamp
status: accepted
date: 2026-08-11
impact: low
accepted_by: agent:claude-code
---
## Context

Expiry could be computed from the creation time on every check, or stored once when the link is created.

## Decision

Store `expires_at` on the invite when it is created.

## Consequences

Changing the expiry rule later does not change links that already exist.
