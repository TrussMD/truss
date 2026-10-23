---
type: prd
id: PRD-0001
title: Team invites by link
status: shipped
date: 2026-08-04
owner: "@priya"
approved_by: "@priya"
carries:
  - PROB-0001
  - FEAT-0001
  - DEC-0002
  - RES-0001#F2
---
**Goal.** An admin adds a teammate with one link, with no email address needed.

**Non-goals.** Bulk import. Public join links.

## Acceptance

**AC1.** An admin generates a link scoped to a role.

**AC2.** The link expires 7 days after it is created (DEC-0002).

**AC3.** Revoking a link takes effect immediately.

**AC4.** Every join is recorded in the audit log.

~~**AC5.** A link can be shared as a QR code.~~ (removed, see IDEA-0001)
