"""Generates spec/conformance/: one small repo per case, plus the expected.json a checker must agree with.

Usage: python scripts/gen-conformance.py [out-dir]    (default: spec/conformance)
CI runs it and fails if the committed files differ, so edit this file, not the generated cases.
Standard library only."""
import json, shutil, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "spec" / "conformance"
shutil.rmtree(OUT, ignore_errors=True)

CONFIG = '---\nspec: "0.1"\n---\n# Docs in this repo\n\nProduct docs live in `truss/`.\n'
BASE = {
"truss/research/RES-0001-invite-friction.md": """---
type: research
id: RES-0001
title: Invite friction
status: published
date: 2026-07-28
method: interviews
---
## Findings

**F1.** 72-hour links expire over the weekend.

**F2.** Admins want to revoke links early.
""",
"truss/decisions/DEC-0001-links-72h.md": """---
type: decision
id: DEC-0001
title: Invite links expire after 72 hours
status: superseded
date: 2026-06-02
accepted_by: "@marcus"
---
## Decision

Links expire after 72 hours.
""",
"truss/decisions/DEC-0002-links-7d.md": """---
type: decision
id: DEC-0002
title: Invite links expire after 7 days
status: accepted
date: 2026-08-04
accepted_by: "@marcus"
supersedes: DEC-0001
carries:
  - RES-0001#F1
---
## Decision

Links expire after 7 days.
""",
"truss/prds/PRD-0001-team-invites.md": """---
type: prd
id: PRD-0001
title: Team invites by link
status: draft
date: 2026-08-04
carries:
  - DEC-0002
---
## Acceptance

**AC1.** An admin generates a link scoped to a role.
""",
"truss/changes/CHG-0001-invite-links.md": """---
type: change
id: CHG-0001
title: Invite teammates by link
status: open
date: 2026-08-05
kind: add
user_facing: true
carries:
  - PRD-0001
---
## Summary

Role-scoped invite links.
""",
}

def case(name, about, valid, errors=(), edit=None, add=None, drop=(), config=CONFIG):
    d = OUT / name
    files = dict(BASE)
    files["truss.md"] = config
    for path in drop:
        files.pop(path)
    for path, (old, new) in (edit or {}).items():
        assert files[path].count(old) == 1, (name, path, old)
        files[path] = files[path].replace(old, new)
    files.update(add or {})
    for path, text in files.items():
        if text is None:
            continue
        f = d / path; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(text)
    def path_of(doc):
        if "/" in doc or doc.endswith(".md"):
            return doc
        hits = [p for p, t in files.items() if t and f"\nid: {doc}\n" in t]
        assert len(hits) >= 1, (name, doc)
        return sorted(hits)[0]
    exp = {"about": about, "valid": valid, "errors": [{"check": c, "file": path_of(doc)} for c, doc in errors]}
    (d / "expected.json").write_text(json.dumps(exp, indent=2) + "\n")

R, D1, D2, P, C = (
    "truss/research/RES-0001-invite-friction.md", "truss/decisions/DEC-0001-links-72h.md",
    "truss/decisions/DEC-0002-links-7d.md", "truss/prds/PRD-0001-team-invites.md", "truss/changes/CHG-0001-invite-links.md")

case("valid-minimal", "A small repo with research, a superseded decision, a PRD and a change.", True)
case("valid-agent-accepts-low-impact", "An agent may accept a low-impact decision that supersedes nothing (§6.4).", True,
     add={"truss/decisions/DEC-0003-absolute-expiry.md": """---
type: decision
id: DEC-0003
title: Store expiry as an absolute timestamp
status: accepted
date: 2026-08-11
impact: low
accepted_by: agent:claude-code
---
## Decision

Store expires_at when the link is created.
"""})
case("valid-custom-type", "A declared custom type is validated like a core type (§10.2).", True,
     config='---\nspec: "0.1"\ntypes:\n  memo:\n    prefix: MEMO\n    statuses: [draft, published]\n    carries: [research]\n    carried_by: [decision]\n---\n# Docs\n',
     add={"truss/memos/MEMO-0001-working-session.md": """---
type: memo
id: MEMO-0001
title: Working session notes
status: published
date: 2026-08-01
carries:
  - RES-0001
---
Notes.
"""})
case("valid-support-topic", "A support doc groups tickets; a problem and a change may cite it (§4.11, §5.1).", True,
     add={"truss/support/SUP-0001-link-expired.md": """---
type: support
id: SUP-0001
title: "Invite link says expired, I just sent it"
status: triaged
date: 2026-07-27
first_seen: 2026-06-12
source: intercom
count: 12
tickets:
  - intercom:2291
  - intercom:2297
---
> Invite link says expired, I just sent it.
""", "truss/problems/PROB-0001-invites-expire.md": """---
type: problem
id: PROB-0001
title: Invites expire before people open them
status: open
date: 2026-07-29
carries:
  - SUP-0001
  - RES-0001#F1
---
Admins who invite on Fridays.
"""}, edit={C: ("  - PRD-0001\n", "  - PRD-0001\n  - SUP-0001\n")})

case("schema-missing-truss-md", "A repo without truss.md is not a Truss repo (§1).", False, [("schema", "truss.md")], drop=["truss.md"])
case("schema-status-not-allowed", "A status the type does not allow.", False, [("schema", "PRD-0001")],
     edit={P: ("status: draft", "status: aproved")})
case("schema-missing-accepted-by", "An accepted decision must record who accepted it (§6.4).", False, [("schema", "DEC-0002")],
     edit={D2: ('accepted_by: "@marcus"\n', "")})
case("schema-agent-accepts-high-impact", "An agent may not accept a decision that supersedes another (§6.4).", False, [("schema", "DEC-0002")],
     edit={D2: ('accepted_by: "@marcus"', "accepted_by: agent:claude-code")})
case("schema-undeclared-type", "A type that is neither core nor declared.", False, [("schema", "truss/roadmaps/ROAD-0001-q4.md")],
     add={"truss/roadmaps/ROAD-0001-q4.md": "---\ntype: roadmap\nid: ROAD-0001\ntitle: Q4\nstatus: draft\ndate: 2026-10-01\n---\n"})
case("schema-type-not-in-use", "A doc whose type truss.md does not use (§9.1).", False, [("schema", "CHG-0001")],
     config='---\nspec: "0.1"\nuse: [prd, decision, research]\n---\n# Docs\n')
case("schema-invalid-yaml", "A title containing ': ' must be quoted (§2.1).", False, [("schema", "truss/changes/CHG-0001-invite-links.md")],
     edit={C: ("title: Invite teammates by link", "title: Invites: by link")})
case("schema-interview-public", "An interview is always internal (§8).", False, [("schema", "INTV-0001")],
     add={"truss/interviews/INTV-0001-agency-admin.md": """---
type: interview
id: INTV-0001
title: Workspace admin at an agency
status: published
date: 2026-07-14
visibility: public
participant:
  ref: P-01
  role: workspace admin
---
Notes.
"""})
case("schema-root-outside-repo", "root must stay inside the repo (§9, §14).", False, [("schema", "truss.md")],
     config='---\nspec: "0.1"\nroot: ../..\n---\n# Docs\n')
case("schema-root-absolute", "root must be a relative path (§9, §14).", False, [("schema", "truss.md")],
     config='---\nspec: "0.1"\nroot: /etc\n---\n# Docs\n')
case("schema-custom-folder-outside-repo", "A custom type's folder must stay inside the repo (§10.2, §14).", False, [("schema", "truss.md")],
     config='---\nspec: "0.1"\ntypes:\n  memo:\n    prefix: MEMO\n    folder: ../memos\n    statuses: [draft]\n---\n# Docs\n')
case("schema-feature-path-outside-repo", "A feature's paths must stay inside the repo (§4.6, §14).", False, [("schema", "FEAT-0001")],
     add={"truss/features/FEAT-0001-team-invites.md": """---
type: feature
id: FEAT-0001
title: Team invites
status: live
date: 2026-08-04
paths:
  - src/invites/**
  - ../../**
---
## Behaviour

An admin creates an invite link for a role.
"""})
case("ids-duplicate", "Two docs share an ID; both files are reported (§11.1).", False,
     [("ids", "truss/research/RES-0001-invite-friction.md"), ("ids", "truss/research/RES-0001-copy.md")],
     add={"truss/research/RES-0001-copy.md": BASE[R]})
case("ids-prefix-mismatch", "An ID whose prefix does not match its type.", False, [("ids", "truss/decisions/PRD-0099-wrong.md")],
     add={"truss/decisions/PRD-0099-wrong.md": "---\ntype: decision\nid: PRD-0099\ntitle: Wrong prefix\nstatus: proposed\ndate: 2026-08-01\n---\n"})
case("links-unresolved", "A link to a doc that does not exist.", False, [("links", "PRD-0001")],
     edit={P: ("  - DEC-0002", "  - DEC-0099")})
case("links-pair-not-allowed", "Research may not carry a change (§5.1).", False, [("links", "RES-0001")],
     edit={R: ("method: interviews\n", "method: interviews\ncarries:\n  - CHG-0001\n")})
case("links-missing-label", "A label that does not exist in its target (§2.3).", False, [("links", "DEC-0002")],
     edit={D2: ("RES-0001#F1", "RES-0001#F9")})
case("links-wrong-label-kind", "Research has F labels, not AC labels (§2.3).", False, [("links", "DEC-0002")],
     edit={D2: ("RES-0001#F1", "RES-0001#AC1")})
case("links-support-carries", "A support doc carries nothing (§5.1).", False, [("links", "SUP-0001")],
     add={"truss/support/SUP-0001-link-expired.md": """---
type: support
id: SUP-0001
title: Link expired
status: open
date: 2026-07-27
first_seen: 2026-06-12
carries:
  - RES-0001
---
> Link expired.
"""})
case("supersession-old-not-superseded", "The doc a decision supersedes must have status superseded (§6.3).", False, [("supersession", "DEC-0002")],
     edit={D1: ("status: superseded", "status: accepted")})
case("supersession-orphan", "A superseded doc must be superseded by some doc (§6.3).", False, [("supersession", "DEC-0001")],
     edit={D2: ("supersedes: DEC-0001\n", "")})

(OUT / "README.md").write_text("""# Conformance suite

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
""")
print(len([p for p in OUT.iterdir() if p.is_dir()]), "cases")
