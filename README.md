# Truss

An open format for product docs that live in your repo: plain markdown, typed frontmatter, typed links. Built for coding agents to read, and for people too.

**Spec draft 0.1.** Expect breaking changes before 1.0.

- **[spec/SPEC.md](spec/SPEC.md)**: the whole format.
- **[spec/schemas/](spec/schemas/)**: a JSON Schema for each type, the type registry and the link table.
- **[spec/example/](spec/example/)**: a small repo that passes every required check.
- **[spec/conformance/](spec/conformance/)**: repos a checker must accept or reject, with the result each one should give.

## In one minute

Put a `truss.md` at the root of your repo:

```markdown
---
spec: "0.1"
---
# Docs in this repo

Product docs live in `truss/`, in the Truss format.
```

Then write docs under `truss/`, one folder per type. Every doc starts with frontmatter that says what it is and what it rests on:

```markdown
---
type: decision
id: DEC-0002
title: Invite links expire after 7 days
status: accepted
date: 2026-08-04
accepted_by: "@marcus"
supersedes: DEC-0001
carries:
  - RES-0001#F3
---
## Context
...
```

## Eleven types

| Type | What it is |
|---|---|
| `problem` | A customer or business problem we have identified and articulated |
| `idea` | A solution thought of first, before any problem |
| `bug` | Unintended behaviour: we intended x, the software did y |
| `prd` | What we are building, and how we will know it is done |
| `change` | The unit of work: one or more PRs or commits |
| `feature` | What one capability of the product does today |
| `plan` | How a piece of work will be done, written before doing it |
| `decision` | A choice and its reasons |
| `research` | What we learned, as numbered findings |
| `interview` | Notes from one conversation with a customer |
| `support` | One topic customers keep raising with support, drawn from any number of tickets |

Problems, ideas and bugs are where work starts. A PRD answers them, changes build it, and the feature doc records what the product does as a result. Decisions record choices along the way. Interviews and support docs hold what customers said, and research holds what we learned from it. A repo uses the types it needs.

## Contributing

Questions, comments and proposals are welcome as issues. See [CONTRIBUTING.md](CONTRIBUTING.md).

To report a vulnerability, see [SECURITY.md](SECURITY.md). Please do not open a public issue.

## Licence

The spec text (`spec/*.md`) is licensed under [CC BY 4.0](LICENSE-SPEC). The schemas, the example, the conformance suite and the scripts are licensed under the [Apache License 2.0](LICENSE). You may build tools, products and services on this format, open or closed, without asking. If you republish the spec text, credit "the Truss spec, truss.md".
