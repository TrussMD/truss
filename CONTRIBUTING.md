# Contributing

## Who decides

The spec is maintained by the Truss team, who decide what goes in. Anyone can comment and propose.

## Questions and comments

Open an issue. Point at the section of [SPEC.md](spec/SPEC.md) you mean.

## Proposing a change

Most proposals start as an extension a team already uses (SPEC.md §10.3):

1. **Use it locally first.** Declare the field or type in your own `truss.md`.
2. **Share it.** Open a proposal issue with the template. If others use it too, it goes on [EXTENSIONS.md](spec/EXTENSIONS.md) with a suggested name and shape.
3. **Make it official.** An extension that several teams use is added in a later version, with migration notes in [CHANGELOG.md](spec/CHANGELOG.md).

A proposal is stronger with evidence: repos that use the extension, and what breaks without it.

## What makes a new type

A new core type needs its own required fields and its own link rules. If it can be a field or a status on an existing type, it should be.
