---
type: change
id: CHG-0002
title: Check revocation on every join
status: shipped
date: 2026-08-27
kind: fix
user_facing: true
carries:
  - BUG-0001
  - FEAT-0001
---
## Summary

The join endpoint read revocation from a cache with a 60-second lifetime. It now reads `revoked_at` from the database on every join.

## Release note

Revoking an invite link now takes effect immediately.
