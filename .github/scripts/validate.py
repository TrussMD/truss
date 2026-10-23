"""Checks what this repository promises: the schemas are valid JSON Schema and agree with types.json and
links.json, the worked example validates against them, and every conformance case is well formed.
It is not a Truss checker: links, IDs and supersession are left to the conformance suite."""
import datetime, json, re, sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2] / "spec"
SCH = ROOT / "schemas"
problems = []

def fail(where, msg):
    problems.append(f"{where}: {msg}")

def normalise(v):
    # SPEC.md 2.1: YAML dates become YYYY-MM-DD strings before validation.
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()[:10]
    if isinstance(v, dict):
        return {k: normalise(x) for k, x in v.items()}
    if isinstance(v, list):
        return [normalise(x) for x in v]
    return v

def frontmatter(path):
    m = re.match(r"^---\n(.*?)\n---\n", path.read_text(), re.S)
    return normalise(yaml.safe_load(m.group(1)) or {}) if m else None

# Schemas
schemas = {}
for f in sorted(SCH.glob("*.schema.json")):
    s = json.loads(f.read_text())
    try:
        Draft202012Validator.check_schema(s)
    except Exception as e:
        fail(f.name, f"not valid JSON Schema: {e}")
    schemas[f.name] = s
registry = Registry().with_resources([(s["$id"], Resource.from_contents(s)) for s in schemas.values()])
types = json.loads((SCH / "types.json").read_text())["types"]
links = json.loads((SCH / "links.json").read_text())
for t in types:
    if f"{t}.schema.json" not in schemas:
        fail("types.json", f"{t} has no schema")
for frm, targets in links["carries"].items():
    for to in [frm, *targets]:
        if to not in types and to != "ticket":
            fail("links.json", f"unknown type {to}")
validator = {t: Draft202012Validator(schemas[f"{t}.schema.json"], registry=registry) for t in types}
config = Draft202012Validator(schemas["config.schema.json"], registry=registry)

def check_repo(repo, label):
    cfg = frontmatter(repo / "truss.md")
    for e in config.iter_errors(cfg or {}):
        fail(f"{label}/truss.md", e.message)
    custom = set(((cfg or {}).get("types") or {}))
    for f in sorted((repo / (cfg or {}).get("root", "truss")).rglob("*.md")):
        fm = frontmatter(f)
        t = (fm or {}).get("type")
        if t in custom:
            continue
        if t not in validator:
            fail(f"{label}/{f.relative_to(repo)}", f"unknown type {t!r}")
            continue
        for e in validator[t].iter_errors(fm):
            fail(f"{label}/{f.relative_to(repo)}", e.message)

# SPEC.md 14: nothing under spec/ may be a symbolic link, so no tool is led outside the repo.
for f in sorted(ROOT.rglob("*")):
    if f.is_symlink():
        fail(str(f.relative_to(ROOT)), "symbolic links are not allowed")

check_repo(ROOT / "example", "example")

# Conformance cases
CHECKS = {"schema", "ids", "links", "supersession"}
cases = sorted(p for p in (ROOT / "conformance").iterdir() if p.is_dir())
for case in cases:
    label = f"conformance/{case.name}"
    try:
        exp = json.loads((case / "expected.json").read_text())
    except Exception as e:
        fail(label, f"expected.json unreadable: {e}")
        continue
    if not isinstance(exp.get("about"), str) or not isinstance(exp.get("valid"), bool) or not isinstance(exp.get("errors"), list):
        fail(label, "expected.json needs about, valid and errors")
        continue
    if exp["valid"] == bool(exp["errors"]):
        fail(label, "valid must be true exactly when errors is empty")
    for e in exp["errors"]:
        if e.get("check") not in CHECKS:
            fail(label, f"unknown check {e.get('check')!r}")
        if not (case / e.get("file", "")).exists() and e.get("file") != "truss.md":
            fail(label, f"listed file {e.get('file')!r} does not exist")
    if exp["valid"]:
        check_repo(case, label)

for p in problems:
    print(p)
print(f"{len(schemas)} schemas, the example and {len(cases)} conformance cases: " + ("ok" if not problems else f"{len(problems)} problem(s)"))
sys.exit(1 if problems else 0)
