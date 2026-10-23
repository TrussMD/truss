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
