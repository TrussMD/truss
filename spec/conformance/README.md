# Conformance suite

Each folder is a small Truss repo and an `expected.json` that says what a conforming checker reports for it, using only the four required checks (SPEC.md §11.1).

```json
{
  "about": "What the case tests, with the section of the spec.",
  "valid": false,
  "errors": [{ "check": "links", "file": "truss/decisions/DEC-0002-links-7d.md" }]
}
```

- `valid` is whether the repo passes all four required checks.
- `errors` lists each check that must fail and the file it must fail on, relative to the case folder.
- A checker passes a case when it agrees on `valid`, reports every listed error, and reports no errors for files that are not listed. It may report more than one check for a listed file.

The worked example in [../example/](../example/) is a valid case too.
