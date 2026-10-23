---
type: bug
id: BUG-0001
title: A revoked invite link still works for up to a minute
status: fixed
date: 2026-08-26
carries:
  - FEAT-0001
  - PRD-0001#AC3
  - intercom:2304
---
## Expected

Revoking a link takes effect immediately (PRD-0001 AC3).

## Actual

The link keeps working for up to 60 seconds after it is revoked.

## How to reproduce

Create a link, revoke it, and open it straight away in a private window.
