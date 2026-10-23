# Security

## Reporting a vulnerability

Report it privately, never in a public issue:

- Use **Report a vulnerability** on the Security tab of this repository, or
- email **security@truss.md**.

We aim to reply within three working days and to agree a fix and a disclosure date with you.

## What counts

This repository holds a format, not a running service. In scope:

- The schemas in `spec/schemas/`: a pattern or rule that lets a document escape what the spec allows, such as a path that leaves the repo, or a pattern that takes too long to evaluate.
- The scripts in `scripts/` and `.github/`: anything that lets a pull request run code it should not, or read or write outside the repository.
- The spec text: a rule that, followed as written, would make a conforming tool unsafe. SPEC.md §14 lists the safety rules tools must follow; a gap in them counts.

Bugs in tools that implement the format belong to those tools.
