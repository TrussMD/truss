# Changelog

## 0.1 (draft)

First public draft.

- Eleven types: problem, idea, bug, prd, change, feature, plan, decision, research, interview, support.
- Typed links through `carries`, with the meaning taken from the two types, plus `related`, `supersedes`, `depends_on` and `parent`.
- IDs as `PREFIX-NNNN`, labels for findings, acceptance criteria and quotes.
- `truss.md` at the repo root for configuration.
- Four required checks and seven policy checks.
- A conformance suite: 25 small repos with the result a checker must give for each.
- Security considerations (§14): doc text is data, paths stay inside the repo, links are not fetched, YAML is parsed safely.

Changed in the draft on 2026-11-11:

- `agents_accept` is removed from `truss.md`. An agent that made a decision records it under its own name, whatever the decision's size. A file that still carries the field stays valid.
- `recorded_by` is added to decisions, PRDs and plans, for a person's judgement that an agent wrote down (§6.4).
- `impact` on a decision is a hint for reviewers only, and a superseding decision no longer counts as high.
- Conformance: `valid-agent-accepts-low-impact` and `schema-agent-accepts-high-impact` are replaced by `valid-recorded-by` and `valid-agent-accepts`.

Changed in the draft on 2026-11-15:

- A folder under the docs folder whose name begins with a dot is not read for docs, at any depth (§1). A file in it needs no frontmatter, and a link to an ID found only there does not resolve.
- A custom type's `folder` may not name such a folder (§10.2). The `schema` check fails on a `truss.md` that does.
- Conformance: `valid-dot-folder`, `links-target-in-dot-folder` and `schema-custom-folder-dot-folder` are added. The suite is now 28 repos.
- Migration: docs kept in such a folder are no longer found, and links to them fail, so move them to a folder that is read. A custom type whose `folder` names such a folder needs another folder.
