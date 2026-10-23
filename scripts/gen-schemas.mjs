// Generates spec/schemas/ from one definition, so the schemas, types.json and links.json always agree.
// Usage: node scripts/gen-schemas.mjs [out-dir]    (default: spec/schemas)
// CI runs it and fails if the committed files differ, so edit this file, not the generated ones.
import { writeFileSync, mkdirSync } from "node:fs";
import { join, dirname, relative } from "node:path";
import { fileURLToPath } from "node:url";

const repo = join(dirname(fileURLToPath(import.meta.url)), "..");
const out = process.argv[2] ?? join(repo, "spec", "schemas");
mkdirSync(out, { recursive: true });
const BASE = "https://truss.md/spec/0.1/schemas/";
// A path relative to the repo that cannot leave it: not absolute, no drive letter, no ~, no backslash, no .. segment.
const SAFE_PATH = "^(?![/~\\\\])(?![A-Za-z]:)(?!(?:.*/)?\\.\\.(?:/|$))[^\\\\]+$";

const types = {
  problem:   { prefix: "PROB", folder: "problems",   statuses: ["open", "solved", "wont-solve"], frozen: ["solved", "wont-solve"] },
  idea:      { prefix: "IDEA", folder: "ideas",      statuses: ["open", "parked", "dropped", "shipped"], frozen: ["dropped", "shipped"] },
  bug:       { prefix: "BUG",  folder: "bugs",       statuses: ["open", "fixed", "wont-fix", "not-a-bug"], frozen: ["fixed", "wont-fix", "not-a-bug"] },
  prd:       { prefix: "PRD",  folder: "prds",       statuses: ["draft", "in-review", "approved", "shipped", "dropped", "superseded"], frozen: ["shipped", "dropped", "superseded"], label: "AC" },
  change:    { prefix: "CHG",  folder: "changes",    statuses: ["open", "shipped", "dropped"], frozen: ["shipped", "dropped"] },
  feature:   { prefix: "FEAT", folder: "features",   statuses: ["planned", "live", "deprecated", "removed", "dropped"], frozen: ["removed", "dropped"] },
  plan:      { prefix: "PLAN", folder: "plans",      statuses: ["draft", "approved", "done", "superseded", "dropped"], frozen: ["done", "superseded", "dropped"] },
  decision:  { prefix: "DEC",  folder: "decisions",  statuses: ["proposed", "accepted", "rejected", "contested", "superseded"], frozen: ["accepted", "rejected", "contested", "superseded"] },
  research:  { prefix: "RES",  folder: "research",   statuses: ["draft", "published"], frozen: ["published"], label: "F" },
  interview: { prefix: "INTV", folder: "interviews", statuses: ["draft", "published"], frozen: ["published"], label: "Q" },
  support:   { prefix: "SUP",  folder: "support",    statuses: ["open", "triaged", "closed"], frozen: ["closed"] },
};

// carries: from -> { to: meaning }. "ticket" is a ticket reference, not a type.
const carries = {
  problem:   { research: "cites", interview: "cites", support: "cites", ticket: "cites", decision: "rests on" },
  idea:      { problem: "addresses", research: "cites", interview: "cites", support: "cites", ticket: "cites", decision: "rests on" },
  bug:       { feature: "breaks the intent written in", prd: "breaks the intent written in", decision: "breaks the intent written in", interview: "reported in", support: "reported in", ticket: "reported in" },
  prd:       { problem: "answers", idea: "answers", bug: "answers", feature: "creates or changes", decision: "rests on", research: "cites", interview: "cites", support: "cites", ticket: "cites" },
  change:    { prd: "implements", bug: "fixes", feature: "touches", decision: "rests on", research: "cites", support: "cites" },
  feature:   { decision: "governed by" },
  plan:      { change: "plans", prd: "plans", decision: "rests on", research: "cites" },
  decision:  { problem: "addresses", decision: "rests on", research: "cites", interview: "cites", support: "cites", ticket: "cites" },
  research:  { interview: "draws on", research: "cites", support: "cites", ticket: "cites" },
  interview: {},
  support:   {},
};

const sameType = {
  supersedes: ["decision", "prd", "plan"],
  depends_on: { change: ["change"], plan: ["plan", "change"] },
  parent: { plan: ["plan"] },
};

const json = (name, obj) => writeFileSync(join(out, name), JSON.stringify(obj, null, 2) + "\n");

// ---------- registry and link table ----------
json("types.json", {
  $comment: "The eleven core types: prefix, default folder, statuses, frozen statuses, and label kind. Truss spec 0.1.",
  spec: "0.1",
  types: Object.fromEntries(Object.entries(types).map(([k, t]) => [k, {
    prefix: t.prefix, folder: t.folder, statuses: t.statuses, frozen: t.frozen, ...(t.label ? { label: t.label } : {}),
  }])),
});

json("links.json", {
  $comment: "The link table. carries[from][to] is the meaning of the link; a pair not listed is not allowed. 'ticket' is a ticket reference. Truss spec 0.1.",
  spec: "0.1",
  carries,
  supersedes: sameType.supersedes,
  depends_on: sameType.depends_on,
  parent: sameType.parent,
  related: "any",
});

// ---------- common definitions ----------
const idPattern = "^[A-Z][A-Z0-9]*-[0-9]{4,}$";
json("common.schema.json", {
  $schema: "https://json-schema.org/draft/2020-12/schema",
  $id: BASE + "common.schema.json",
  title: "Fields every Truss doc shares",
  $defs: {
    id: { type: "string", pattern: idPattern },
    docRef: { type: "string", pattern: "^[A-Z][A-Z0-9]*-[0-9]{4,}(#(F|AC|Q)[0-9]+)?$", description: "An ID, optionally with a label: DEC-0002, RES-0001#F3" },
    ticketRef: {
      anyOf: [
        { type: "string", pattern: "^https?://\\S+$" },
        { type: "string", pattern: "^[a-z][a-z0-9-]*:\\S+$" },
      ],
      description: "A ticket in another system: a URL, or source:id such as intercom:2291",
    },
    ticketObject: {
      type: "object",
      required: ["ref"],
      properties: { ref: { $ref: "#/$defs/ticketRef" }, count: { type: "integer", minimum: 1 } },
    },
    carriesItem: { anyOf: [{ $ref: "#/$defs/docRef" }, { $ref: "#/$defs/ticketRef" }, { $ref: "#/$defs/ticketObject" }] },
    idOrList: { anyOf: [{ $ref: "#/$defs/id" }, { type: "array", items: { $ref: "#/$defs/id" }, minItems: 1 }] },
    person: { type: "string", pattern: "^@[A-Za-z0-9][A-Za-z0-9._-]*$", description: "A person: \"@handle\"" },
    actor: {
      anyOf: [{ $ref: "#/$defs/person" }, { type: "string", pattern: "^agent:[a-z0-9][a-z0-9._-]*$" }],
      description: "A person (\"@handle\") or an agent (agent:name)",
    },
    date: { type: "string", pattern: "^[0-9]{4}-[0-9]{2}-[0-9]{2}$" },
    doc: {
      type: "object",
      required: ["type", "id", "title", "status", "date"],
      properties: {
        type: { type: "string" },
        id: { $ref: "#/$defs/id" },
        title: { type: "string", minLength: 1 },
        status: { type: "string" },
        date: { $ref: "#/$defs/date" },
        owner: { $ref: "#/$defs/person" },
        carries: { type: "array", items: { $ref: "#/$defs/carriesItem" } },
        related: { type: "array", items: { $ref: "#/$defs/docRef" } },
        visibility: { enum: ["internal", "public"], default: "internal" },
      },
    },
  },
});

// ---------- per-type schemas ----------
const C = "common.schema.json#/$defs/";
const requireWhen = (field, statuses) => ({
  if: { properties: { status: { enum: statuses } }, required: ["status"] },
  then: { required: [field] },
});

const extra = {
  problem: {},
  idea: {},
  bug: { properties: { intent: { const: "undocumented" } } },
  prd: {
    properties: { approved_by: { $ref: C + "person" }, supersedes: { $ref: C + "idOrList" } },
    allOf: [requireWhen("approved_by", ["approved", "shipped"])],
  },
  change: {
    required: ["kind", "user_facing"],
    properties: {
      kind: { enum: ["add", "improve", "fix"] },
      user_facing: { type: "boolean" },
      depends_on: { type: "array", items: { $ref: C + "id" } },
      branch: { type: "string" },
      pr: { type: ["string", "integer"] },
    },
  },
  feature: { properties: { paths: { type: "array", items: { type: "string", pattern: SAFE_PATH } } } },
  plan: {
    properties: {
      approved_by: { $ref: C + "person" },
      supersedes: { $ref: C + "idOrList" },
      depends_on: { type: "array", items: { $ref: C + "id" } },
      parent: { $ref: C + "id" },
      step: { type: "integer", minimum: 1 },
    },
    allOf: [requireWhen("approved_by", ["approved", "done"])],
  },
  decision: {
    properties: {
      impact: { enum: ["low", "high"], default: "high" },
      accepted_by: { $ref: C + "actor" },
      rejected_by: { $ref: C + "actor" },
      supersedes: { $ref: C + "idOrList" },
    },
    allOf: [requireWhen("accepted_by", ["accepted", "contested", "superseded"]), requireWhen("rejected_by", ["rejected"])],
  },
  research: {
    required: ["method"],
    properties: {
      method: {
        type: "string", minLength: 1,
        examples: ["interviews", "survey", "analytics", "experiment", "market-scan", "competitor-review", "due-diligence", "deep-research"],
      },
    },
  },
  interview: {
    required: ["participant"],
    properties: {
      format: { enum: ["interview", "usability-test", "sales-call", "support-call"], default: "interview" },
      participant: {
        type: "object",
        required: ["ref", "role"],
        properties: { ref: { type: "string", minLength: 1 }, role: { type: "string", minLength: 1 }, segment: { type: "string" } },
      },
      source: { anyOf: [{ type: "string", pattern: "^https?://\\S+$" }, { type: "string", pattern: "^[a-z][a-z0-9-]*:\\S+$" }] },
      visibility: { const: "internal" },
    },
  },
  support: {
    required: ["first_seen"],
    properties: {
      first_seen: { $ref: C + "date" },
      source: { type: "string", pattern: "^[a-z][a-z0-9-]*$" },
      tickets: { type: "array", items: { $ref: C + "ticketRef" } },
      count: { type: "integer", minimum: 1 },
      visibility: { const: "internal" },
    },
  },
};

const titles = {
  problem: "A customer or business problem we have identified and articulated",
  idea: "A solution thought of first, before any problem",
  bug: "Unintended behaviour: we intended x, the software did y",
  prd: "What we are building, and how we will know it is done",
  change: "The unit of work: one or more PRs or commits",
  feature: "What one capability of the product does today",
  plan: "How a piece of work will be done, written before doing it",
  decision: "A choice and its reasons",
  research: "What we learned, as numbered findings",
  interview: "Notes from one conversation with a customer",
  support: "One topic customers keep raising with support, drawn from any number of tickets",
};

for (const [name, t] of Object.entries(types)) {
  const e = extra[name];
  json(`${name}.schema.json`, {
    $schema: "https://json-schema.org/draft/2020-12/schema",
    $id: BASE + `${name}.schema.json`,
    title: `${name}: ${titles[name]}`,
    allOf: [
      { $ref: C + "doc" },
      {
        type: "object",
        required: e.required ?? [],
        properties: {
          type: { const: name },
          id: { type: "string", pattern: `^${t.prefix}-[0-9]{4,}$` },
          status: { enum: t.statuses },
          ...(e.properties ?? {}),
        },
      },
      ...(e.allOf ?? []),
    ],
  });
}

// ---------- truss.md frontmatter ----------
const policyChecks = ["coverage", "freshness", "evidence", "frozen", "lifecycle", "privacy", "hygiene"];
json("config.schema.json", {
  $schema: "https://json-schema.org/draft/2020-12/schema",
  $id: BASE + "config.schema.json",
  title: "truss.md frontmatter: the repo's Truss configuration",
  type: "object",
  required: ["spec"],
  properties: {
    spec: { type: "string", pattern: "^[0-9]+\\.[0-9]+$" },
    root: { type: "string", pattern: SAFE_PATH, default: "truss" },
    agents_accept: { enum: ["none", "low", "all"], default: "low" },
    use: {
      type: "array", uniqueItems: true,
      items: { enum: Object.keys(types) },
      description: "The core types this repo tracks. Default: all of them",
    },
    checks: {
      type: "object",
      properties: {
        ...Object.fromEntries(policyChecks.map((c) => [c, { enum: ["off", "warn", "error"], default: "warn" }])),
        evidence_for_decisions: { type: "boolean", default: false },
      },
      additionalProperties: false,
    },
    fields: { type: "object", additionalProperties: { type: "object", description: "A JSON Schema for the field's value" } },
    types: {
      type: "object",
      propertyNames: { pattern: "^[a-z][a-z0-9-]*$", not: { enum: Object.keys(types) } },
      additionalProperties: {
        type: "object",
        required: ["prefix", "statuses"],
        properties: {
          prefix: { type: "string", pattern: "^[A-Z][A-Z0-9]*$", not: { enum: Object.values(types).map((t) => t.prefix) } },
          folder: { type: "string", pattern: SAFE_PATH },
          statuses: { type: "array", items: { type: "string" }, minItems: 1 },
          frozen: { type: "array", items: { type: "string" } },
          carries: { type: "array", items: { type: "string" } },
          carried_by: { type: "array", items: { type: "string" } },
          supersedes: { type: "boolean", default: false },
          schema: { type: "string", pattern: SAFE_PATH },
        },
      },
    },
  },
});
console.log("wrote", relative(process.cwd(), out) || ".");
