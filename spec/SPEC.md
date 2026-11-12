# The Truss format

**Draft 0.1.** Expect breaking changes before 1.0. Comments and proposals welcome: see [CONTRIBUTING.md](../CONTRIBUTING.md).

Truss is a format for keeping product docs in a git repo, as plain markdown with typed frontmatter, so that coding agents can trust their shape and follow their links. People can read them too.

This document is the whole format. The [schemas](schemas/) are the same rules in machine-readable form, and the [example](example/) is a small repo that passes every required check.

The key words MUST, MUST NOT, SHOULD and MAY are used as in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

---

## 1. A Truss repo

A repo is a Truss repo when it has a file named `truss.md` at its root ([§9](#9-trussmd)). Without it, a tool MUST NOT treat the repo as a Truss repo.

Docs live under one folder, `truss/` unless `truss.md` says otherwise, with one folder per type:

```
truss.md
truss/
  problems/    ideas/      bugs/
  prds/        changes/    features/
  plans/       decisions/  research/
  interviews/  support/
```

The type of a doc comes from its frontmatter, never from its folder. Folders are a convention: a misfiled doc is a hygiene warning, not an error.

---

## 2. Documents

A doc is one markdown file that starts with YAML frontmatter between two `---` lines.

```markdown
---
type: decision
id: DEC-0002
title: Invite links expire in 7 days
status: accepted
date: 2026-08-21
impact: high
accepted_by: "@marcus"
supersedes: DEC-0001
carries:
  - RES-0001#F3
  - intercom:2291
---
## Context
...
```

### 2.1 Fields every type shares

| Field | Required | Value |
|---|---|---|
| `type` | Yes | One of the eleven core types ([§4](#4-types)) or a declared custom type ([§10](#10-extensions)) |
| `id` | Yes | The doc's ID ([§3](#3-ids)) |
| `title` | Yes | A short title, in plain words |
| `status` | Yes | One of the type's statuses ([§4](#4-types)) |
| `date` | Yes | The date the doc was created, as `YYYY-MM-DD`. Never changed afterwards |
| `owner` | No | A person, as `"@handle"` |
| `carries` | No | What this doc rests on ([§5.1](#51-carries)) |
| `related` | No | Docs worth knowing about, which count for nothing ([§5.2](#52-related)) |
| `visibility` | No | `internal` (the default) or `public` ([§8](#8-visibility-and-privacy)) |

Field names are `snake_case`. There is no "last updated" field: git holds that.

Dates are written unquoted, as `2026-08-21`. Many YAML parsers read such a value as a date rather than a string, so a tool MUST convert YAML dates to `YYYY-MM-DD` strings before validating frontmatter against the schemas. Booleans are written `true` and `false`, never `yes` or `no`. A value that contains `: `, such as a title like `Hold: the spec is open`, MUST be quoted, or the frontmatter is not valid YAML.

A person is written `"@handle"`, quoted because `@` cannot start a plain YAML value. An agent is written `agent:<name>`, for example `agent:claude-code`.

### 2.2 Body

The body is free markdown. Each type lists the sections it SHOULD have. Tools read only two things from a body: labels ([§2.3](#23-labels)) and the `## Release note` section of a change.

### 2.3 Labels

Three types number their parts so that other docs can cite one part:

| Type | Label | Written in the body as | Cited as |
|---|---|---|---|
| research | finding | `**F1.**` | `RES-0001#F1` |
| prd | acceptance criterion | `**AC1.**` | `PRD-0001#AC1` |
| interview | quote | `**Q1.**` | `INTV-0001#Q1` |

A label is written out at the start of a line, or of a list item. It is never taken from markdown list numbering, which renumbers when items are added or removed.

A label MUST NOT be reused within a doc. A new part takes the next unused number, wherever it sits. A removed part stays in place, struck through, and keeps its label:

```markdown
~~**AC3.** Links can be shared by QR code.~~ (removed)
```

---

## 3. IDs

An ID is a type prefix, a hyphen and a number of at least four digits: `DEC-0002`, `PRD-0142`.

- Numbers count up independently per type. `PRD-0142` and `CHG-0142` are unrelated.
- An ID MUST be unique within the repo, and its prefix MUST match its type.
- The frontmatter `id` is canonical. The filename SHOULD be the ID followed by a slug of the title: `DEC-0002-invite-links-7d.md`. When a title changes, the file may be renamed freely, because links use the ID alone.
- Links, commit messages and code comments use the bare ID. A tool that prints an ID SHOULD print the title next to it.
- An ID never changes, except to resolve a collision.

**Collisions.** Two branches can each create `DEC-0018`. Tools that create docs SHOULD look at the remote branches before choosing a number. The `ids` check fails when a collision reaches one branch, and the later doc is renumbered, with every link to it rewritten in the same commit.

**Across repos.** The form `<repo>:<ID>` is reserved for links between repos and is not defined in 0.1.

---

## 4. Types

Three types are the ways work starts: **problem**, **idea** and **bug**. A **prd** answers them, **changes** build it, and the **feature** doc records what the product does as a result. **Plans** say how work will be done. **Decisions** record choices. **Interviews** and **support** docs hold what customers said, and **research** holds what we learned from it.

| Type | Prefix | Folder | What it is |
|---|---|---|---|
| problem | `PROB` | `problems/` | A customer or business problem we have identified and articulated |
| idea | `IDEA` | `ideas/` | A solution thought of first, before any problem |
| bug | `BUG` | `bugs/` | Unintended behaviour: we intended x, the software did y |
| prd | `PRD` | `prds/` | What we are building, and how we will know it is done |
| change | `CHG` | `changes/` | The unit of work: one or more PRs or commits |
| feature | `FEAT` | `features/` | What one capability of the product does today |
| plan | `PLAN` | `plans/` | How a piece of work will be done, written before doing it |
| decision | `DEC` | `decisions/` | A choice and its reasons |
| research | `RES` | `research/` | What we learned, as numbered findings |
| interview | `INTV` | `interviews/` | Notes from one conversation with a customer |
| support | `SUP` | `support/` | One topic customers keep raising with support, drawn from any number of tickets |

For each type below, **frozen** lists the statuses in which the body is frozen ([§6.2](#62-frozen-bodies)).

### 4.1 problem

A distinct customer or business problem that we have identified and articulated.

- **Statuses:** `open`, `solved`, `wont-solve`. Frozen: `solved`, `wont-solve`.
- **Body:** who has the problem, what it costs them, and the evidence.
- A problem SHOULD carry its evidence: research, interviews, support docs or tickets.
- `solved` is set by a person, usually once a PRD that answers it has shipped.

### 4.2 idea

A solution we thought of first, without starting from a problem. It is worth building if it traces to a problem nobody had articulated, or if people liked it when they tried it.

- **Statuses:** `open`, `parked`, `dropped`, `shipped`. Frozen: `dropped`, `shipped`.
- **Body:** what it is, and why it might be worth building. A dropped idea SHOULD say why in one sentence.
- `parked` means not now, maybe later. `dropped` means we decided not to. An idea needs no problem to exist, but SHOULD carry a problem or research before a PRD answers it.
- An idea that a PRD carries is in progress. That is shown by the link and not stored as a status.

### 4.3 bug

Unintended behaviour. We intended the software to do x, and it did y.

- **Statuses:** `open`, `fixed`, `wont-fix`, `not-a-bug`. Frozen: all but `open`.
- **Fields:** `intent: undocumented` (optional), when the intended behaviour is written nowhere. That is a gap in the docs, and worth knowing.
- **Body:** expected, actual, and how to reproduce.
- A bug SHOULD carry where the intent is written down: the feature, a PRD criterion such as `PRD-0001#AC3`, or a decision. If it carries none of these, it SHOULD say `intent: undocumented`.
- A bug closed as `not-a-bug` (the software did what we intended, and people dislike it) SHOULD relate to the problem or idea it really is.
- A small bug is fixed by a change directly. A bug whose fix needs product thinking is answered by a PRD.

### 4.4 prd

What we are building, and how we will know it is done.

- **Statuses:** `draft`, `in-review`, `approved`, `shipped`, `dropped`, `superseded`. Frozen: `shipped`, `dropped`, `superseded`.
- **Fields:** `approved_by` (required when `approved` or `shipped`; a person), `recorded_by` (optional; [§6.4](#64-who-may-set-a-status)), `supersedes` (optional).
- **Body:** goal, non-goals, and acceptance criteria labelled `**AC1.**`, `**AC2.**` and so on.
- A PRD carries at least one problem, idea or bug, and the feature it creates or changes. A PRD for a new capability creates that feature's doc, with status `planned`, in the same commit.
- A PRD stays editable until it ships. Changes to its acceptance criteria MAY carry a decision explaining them.
- `shipped` is set by a person.

### 4.5 change

The unit of work. A change covers one or more PRs, or commits pushed straight to the main branch. Each PR belongs to exactly one change.

- **Statuses:** `open`, `shipped`, `dropped`. Frozen: `shipped`, `dropped`.
- **Fields:**
  - `kind` (required): `add` (creates a capability), `improve` (makes an existing one better), or `fix` (corrects unintended behaviour).
  - `user_facing` (required): `true` if a user will notice the change, including a performance change they will feel.
  - `depends_on` (optional): changes that must land first.
  - `branch`, `pr` (optional): for people to read. No tool depends on them.
- **Body:** a summary, and, for a user-facing change, a `## Release note` section of one or two sentences in customer wording.
- **What a change carries,** by kind:

  | Kind | Carries |
  |---|---|
  | `add` | The PRD it implements |
  | `improve`, user-facing | The PRD it implements |
  | `improve`, not user-facing | Nothing required |
  | `fix` | The bug it fixes |

- **What a user-facing change owes when it ships:** a release note, always. For `add` and `improve`, an updated feature doc: `add` makes the feature `live` and writes its behaviour, `improve` updates its behaviour. A `fix` updates the feature doc only when the bug said `intent: undocumented`.
- **Which commits belong to a change:** a commit belongs to a change if its message names the change ID, such as `invites: 7d expiry (CHG-0142)`, or if it edits the change doc.
- **A change that stops** is `dropped` only if none of its code reached the main branch. If some did, it is `shipped`: what landed is what shipped, and the remaining work becomes a new change.

### 4.6 feature

What one capability of the product does today. It is the one doc that is edited in place for as long as the capability exists.

- **Statuses:** `planned`, `live`, `deprecated`, `removed`, `dropped`. Frozen: `removed`, `dropped`.
  - `planned`: warranted by a PRD, not built yet.
  - `live`: built and in use.
  - `deprecated`: still works, but we decided it is going away. Do not extend it.
  - `removed`: was live and has been taken out. Kept for history.
  - `dropped`: was planned and never built.
- **Fields:** `paths` (optional), path patterns for the code the feature lives in, such as `src/invites/**`. Each pattern is relative to the repo root and MUST NOT reach outside the repo ([§14](#14-security-considerations)).
- **Body:** current behaviour, and who it is for. A planned feature says it is not built yet and names the PRD.
- **Size:** one feature is one capability a customer could name, about one help-centre page. Features do not nest in 0.1. A folder under `features/` may group them.
- **Paths:** a file may belong to several features. Code under no feature is fine. A feature without paths is valid: tools fall back to reading the feature docs, which is slower and, for an agent, costs tokens.

### 4.7 plan

How a piece of work will be done, written before doing it. The plan an agent writes before coding (for example in Claude Code's plan mode) is a plan doc, saved when the plan is approved.

- **Statuses:** `draft`, `approved`, `done`, `superseded`, `dropped`. Frozen: `done`, `superseded`, `dropped`.
- **Fields:** `approved_by` (required when `approved` or `done`; a person), `recorded_by` (optional; [§6.4](#64-who-may-set-a-status)), `supersedes` (a replan), `depends_on` (plans or changes that must finish first), `parent` and `step` (optional; this plan is step `step` of the plan `parent`).
- **Body:** goal, tasks, done when. Risks and open questions are optional.
- A plan carries what it is for: a change (an implementation plan), a PRD (a delivery plan across several changes), or decisions and research (a roadmap). A plan never decides anything: a choice made while planning is a decision the plan carries.
- An approved plan stays editable so that tasks can be ticked off. Changing direction is a new plan that supersedes it. When work deviates from a plan, the deviation is a decision.

### 4.8 decision

A choice and its reasons.

- **Statuses:** `proposed`, `accepted`, `rejected`, `contested`, `superseded`. Frozen: all but `proposed`.
  - `rejected`: proposed and turned down. Never in force. Do not propose it again without new evidence.
  - `contested`: accepted and still in force, but in question, because a person or new evidence disputes it. It ends superseded, or back to `accepted`.
- **Fields:**
  - `impact` (optional): `low` or `high`, default `high`. A hint for reviewers about which decisions deserve a closer look. No check reads it.
  - `accepted_by` (required when `accepted`, `contested` or `superseded`), `rejected_by` (required when `rejected`): a person or an agent ([§6.4](#64-who-may-set-a-status)).
  - `recorded_by` (optional): the agent that wrote the record when a person made the call ([§6.4](#64-who-may-set-a-status)).
  - `supersedes` (optional): the decision this one replaces.
- **Body:** context, decision, consequences.

### 4.9 research

What we learned, as numbered findings that other docs can cite. Research is evidence gathered by a method, never opinion.

- **Statuses:** `draft`, `published`. Frozen: `published`.
- **Fields:** `method` (required). Suggested values: `interviews`, `survey`, `analytics`, `experiment`, `market-scan`, `competitor-review`, `due-diligence`, `deep-research` (research done by an LLM).
- **Body:** the method, then findings labelled `**F1.**`, `**F2.**` and so on. Every finding SHOULD cite its sources: interviews, support docs, tickets or URLs. That rule matters most for `deep-research`.
- Published findings are not rewritten. A `## Corrections` section MAY be appended.

### 4.10 interview

Notes from one conversation with a customer.

- **Statuses:** `draft`, `published`. Frozen: `published`.
- **Fields:**
  - `format` (optional): `interview` (the default), `usability-test`, `sales-call` or `support-call`.
  - `participant` (required): `ref`, a pseudonym that stays the same across interviews, such as `P-07`; `role`; and `segment` (optional).
  - `source` (optional): where the recording or transcript lives, behind its own login.
- **Body:** what was said, with quotes kept as quotes. Quotes worth citing are labelled `**Q1.**`, `**Q2.**`.
- An interview never holds a personal name, email address or phone number ([§8](#8-visibility-and-privacy)), and is always `internal`.
- A support *call* is an interview with `format: support-call`. A support *ticket* belongs in a support doc ([§4.11](#411-support)).

### 4.11 support

One topic that customers keep raising with support, in their words, such as "Invite link says expired, I just sent it". One support doc draws on any number of tickets or threads in the helpdesk. It records what customers report before anyone has decided what it is: a bug, a problem, an idea or a question. Deciding that is the job of the doc that carries it.

- **Statuses:** `open`, `triaged`, `closed`. Frozen: `closed`.
  - `triaged`: a bug, problem or idea carries it.
  - `closed`: no longer reported, or resolved.
- **Fields:**
  - `first_seen` (required): the date of the earliest ticket on the topic.
  - `source` (optional): the helpdesk, such as `intercom` or `zendesk`.
  - `tickets` (optional): ticket references ([§5.4](#54-tickets)) worth keeping a link to. It need not be complete.
  - `count` (optional): how many tickets are on the topic, listed or not. It stays accurate only if an agent or a connector keeps it current.
- **Body:** one representative ticket, quoted and stripped of names, and how the reports vary.
- **One topic:** tickets that say the same thing in customers' terms. Tickets that sound alike but have different causes become separate support docs, each carried by its own bug or problem. A ticket that raises two topics may appear in both.
- A support doc never holds a personal name, email address or phone number, and is always `internal`.
- **Written by agents.** Support docs are meant to be generated from the helpdesk. An agent or a connector reads new tickets, matches each one to the support doc on the same topic or opens a new one, keeps `tickets`, `count` and `first_seen` current, and writes the quote with names removed. Before it opens a new support doc, it SHOULD search the existing ones for the same topic. No status on a support doc needs a person ([§6.4](#64-who-may-set-a-status)). Deciding what a topic really is stays with the bug, problem or idea that carries it.

---

## 5. Links

### 5.1 carries

`carries` lists what a doc rests on. Links point one way only. The reverse ("which changes touched this feature?") is computed by tools and never stored.

The meaning of a link comes from the two types. The table is also the allow-list: a pair that is not in it fails the `links` check.

| From | To | Meaning |
|---|---|---|
| problem | research, interview, support, ticket | cites |
| problem | decision | rests on |
| idea | problem | addresses |
| idea | research, interview, support, ticket | cites |
| idea | decision | rests on |
| bug | feature, prd, decision | breaks the intent written in |
| bug | interview, support, ticket | reported in |
| prd | problem, idea, bug | answers |
| prd | feature | creates or changes |
| prd | decision | rests on |
| prd | research, interview, support, ticket | cites |
| change | prd | implements |
| change | bug | fixes |
| change | feature | touches |
| change | decision | rests on |
| change | research, support | cites |
| feature | decision | governed by |
| plan | change, prd | plans |
| plan | decision | rests on |
| plan | research | cites |
| decision | problem | addresses |
| decision | decision | rests on |
| decision | research, interview, support, ticket | cites |
| research | interview | draws on |
| research | research, support, ticket | cites |

A support doc carries nothing: its tickets are listed in its own `tickets` field.

An entry in `carries` is an ID (`DEC-0002`), an ID with a label (`RES-0001#F3`), or a ticket ([§5.4](#54-tickets)).

### 5.2 related

`related` links any doc to any doc. It must resolve, and it counts for nothing: it is not followed by trace, it does not satisfy any check, and context tools list it by ID and title only. It is written on one doc and shown on both.

### 5.3 Links within one type

| Field | On | Points to | Meaning |
|---|---|---|---|
| `supersedes` | decision, prd, plan | One doc of the same type, or a list | Replaces it |
| `depends_on` | change | Changes | Must land after them |
| `depends_on` | plan | Plans, changes | Must start after they finish |
| `parent` | plan | One plan | Is a step of it, at position `step` |

### 5.4 Tickets

A ticket lives in the helpdesk, not in the repo. The usual way to bring tickets in is a support doc ([§4.11](#411-support)), which groups the tickets on one topic and quotes them, so an agent can read what customers said without opening the helpdesk. A doc may also refer to a ticket directly. Either way, a ticket is written as a ticket reference: a URL, or `<source>:<id>`, such as `intercom:2291` or `zendesk:88123`. The source is lowercase letters, digits and hyphens. A reference may also be written as an object, to say how many similar tickets there are:

```yaml
carries:
  - ref: intercom:2291
    count: 12
```

Tickets and support docs count as evidence. The `links` check confirms a ticket reference is well formed, and cannot confirm the ticket exists. A support doc is one topic, not a copy of one ticket: tools SHOULD NOT write one doc per ticket.

---

## 6. Lifecycle

### 6.1 Statuses

A status records something a person, or a permitted agent, decided. Anything the links already show is computed by tools and never stored: an idea in progress, a bug being fixed, a problem being addressed.

Statuses usually move forward, and MAY move back. Reopening a doc is an ordinary edit. The `schema` check confirms only that the status is one the type allows.

### 6.2 Frozen bodies

In a frozen status ([§4](#4-types)), the body is frozen. Status and links may still change, so a frozen doc can be superseded, reopened or relinked. A small fix such as a typo is allowed. The `frozen` policy check warns on any edit to a frozen body.

### 6.3 Supersession

When a doc supersedes another, both docs say so. If `DEC-0002` has `supersedes: DEC-0001`, then `DEC-0001` MUST have status `superseded`. A doc with status `superseded` MUST be superseded by some doc. The `supersession` check fails when the two disagree.

The status is stored on the old doc, not only computed, so that anyone reading the old doc directly sees that it is superseded.

### 6.4 Who may set a status

Some statuses record a judgement, and the doc records who made it.

| Type | Status | Recorded in | Who |
|---|---|---|---|
| prd | `approved` | `approved_by` | A person |
| plan | `approved` | `approved_by` | A person |
| decision | `accepted` | `accepted_by` | A person or an agent |
| decision | `rejected` | `rejected_by` | A person or an agent |

The `_by` field names whoever made the judgement. An agent that makes a decision on its own, in an unattended run for example, records it as accepted under its own name, such as `agent:claude-code`. A person still sees it in review: an agent-accepted decision lands in the same PR as the code.

When a person makes the judgement and an agent writes the doc, as when someone approves a plan or agrees a decision in a session, the `_by` field holds the person's handle and `recorded_by` names the agent:

```yaml
accepted_by: "@marcus"
recorded_by: agent:claude-code
```

A tool acting for an agent MUST NOT write a person's handle into an `_by` field unless that person made the judgement, and MUST then set `recorded_by`. An agent MUST NOT approve a PRD or a plan.

No check can tell who typed a file. `recorded_by` marks the docs where an agent wrote a person's name, so that review can confirm them.

---

## 7. Code and docs

**From a line to its docs.** A feature's `paths` lead from a file to its feature. Git leads from a line to the commit that last changed it, and that commit belongs to a change ([§4.5](#45-change)). From the change, `carries` leads to the PRD or bug, the decisions, and the evidence behind them.

**Comments in code.** A code comment MAY name a doc ID, such as `// DEC-0002`. Tools treat it as a hint and not as a link.

---

## 8. Visibility and privacy

**Visibility.** Every doc is `internal` unless it says `visibility: public`. A tool that publishes docs outside the repo, such as a help centre or a public site, MUST publish only docs marked `public`. Publishing goes through a build step that reshapes docs for their readers. Release notes are built from the `## Release note` sections of shipped, user-facing changes, and are not stored.

**Interviews and support docs.** Both are always `internal`. An interview identifies the participant by a pseudonym and a role; a support doc quotes tickets with names removed. The real identity lives only in the tool named in `source`. The mapping from pseudonym to person MUST NOT be stored in the repo.

Git keeps history, so a name committed once is hard to remove. A customer's request to be forgotten is easy to honour only if their name was never committed.

---

## 9. truss.md

`truss.md` sits at the repo root. Its frontmatter is the repo's configuration. Its body is a short introduction to the docs for people and agents, and agent instruction files such as `CLAUDE.md` and `AGENTS.md` SHOULD import or point to it.

```markdown
---
spec: "0.1"
root: truss
checks:
  coverage: error
  privacy: error
---
# Docs in this repo

This repo keeps its product docs in `truss/`, in the Truss format.
Before changing behaviour, read the change, PRD and feature docs that cover it.
Record decisions as you make them. Propose changes rather than overwriting them.
```

| Field | Required | Value |
|---|---|---|
| `spec` | Yes | The version of this spec the docs follow, as a string |
| `root` | No | The docs folder, relative to the repo root and inside it ([§14](#14-security-considerations)). Default `truss`. `.` means the repo root itself, for a repo that holds only docs |
| `checks` | No | A level for each policy check: `off`, `warn` (the default) or `error` |
| `fields` | No | Custom fields ([§10.1](#101-custom-fields)) |
| `types` | No | Custom types ([§10.2](#102-custom-types)) |
| `use` | No | The core types this repo tracks ([§9.1](#91-choosing-types)). Default: all eleven |

The smallest valid `truss.md` is a frontmatter block holding `spec: "0.1"`. The body SHOULD stay short: detailed instructions belong in agent skills, which load only when needed.

### 9.1 Choosing types

A repo need not track every type. `use` lists the core types it does:

```yaml
use: [bug, change, feature, decision]
```

- Leaving `use` out means all eleven core types are in use. A declared custom type is always in use.
- No type is mandatory. `use: [decision]` is a valid repo.
- A doc whose type is not in use fails the `schema` check, as an undeclared type does.
- Rows of the link table that involve a type not in use do not apply.
- A policy check drops any requirement that names a type not in use, and does not ask for anything in its place. Without `prd`, an `add` change carries nothing required. Without `feature`, `freshness` checks only the release note.
- A checker SHOULD say which core types are not in use and what that switches off, for example: "Not in use: idea, plan. Trace stops at changes, because `feature` is not in use."
- Tools SHOULD create folders and install agent skills only for the types in use.

---

## 10. Extensions

### 10.1 Custom fields

Any doc may carry fields this spec does not define. A team SHOULD declare them in `truss.md`, as a JSON Schema for the value:

```yaml
fields:
  priority: { type: string, enum: [p0, p1, p2] }
  jira: { type: string }
```

A declared field is validated by the `schema` check. An undeclared field is kept, and the `hygiene` check warns about it, which catches typos such as `stauts`. Tools MUST preserve fields they do not understand.

If a later version of this spec defines a field a team has already declared, the migration notes for that version say how to rename it.

### 10.2 Custom types

A team may declare its own types in `truss.md`:

```yaml
types:
  business-model:
    prefix: BIZ
    folder: business            # default: the type name; relative, inside the repo
    statuses: [draft, accepted, review, superseded]
    frozen: [superseded]
    carries: [decision, research]
    carried_by: [plan]          # core types allowed to carry it
    supersedes: true
    schema: truss/schemas/business-model.json   # optional: extra field rules; relative, inside the repo
```

- The prefix MUST NOT be one of the core prefixes.
- A custom type adds rows to the link table, through `carries` and `carried_by`. It cannot change the core rows.
- `related` works with custom types as with any other.
- The required checks apply to custom types in full.
- A doc whose type is neither core nor declared fails the `schema` check.

### 10.3 From local to official

1. **Local:** a team declares a field or type in its own `truss.md`. It works straight away.
2. **Shared:** [EXTENSIONS.md](EXTENSIONS.md) lists extensions several teams use, with a suggested name and shape, so teams use the same name before anything is official.
3. **Official:** a widely used extension is proposed ([CONTRIBUTING.md](../CONTRIBUTING.md)) and added in a later version.

---

## 11. Checks

### 11.1 Required checks

A repo that fails any of these is not a valid Truss repo. They read only the files at one commit: no git history, no network and no model.

| Check | Fails when |
|---|---|
| **schema** | `truss.md` is missing or invalid. A doc's frontmatter does not match the schema for its type, its type is not declared or not in use, its status is not one its type allows, a required `_by` field is missing or names someone not permitted ([§6.4](#64-who-may-set-a-status)), or a path in `truss.md` or in a feature's `paths` leaves the repo ([§14](#14-security-considerations)) |
| **ids** | Two docs share an ID (reported on each of them), an ID is malformed, or a prefix does not match its type |
| **links** | A link does not resolve, a `carries` pair is not in the link table, a `supersedes`, `depends_on` or `parent` link points to a type it may not, a `#label` does not exist in its target or is not that type's kind of label, or a ticket reference is malformed |
| **supersession** | A superseding doc and the doc it supersedes disagree ([§6.3](#63-supersession)) |

### 11.2 Policy checks

Each team sets these to `off`, `warn` or `error` in `truss.md`. All default to `warn`. They MAY use git history, comparing a branch with the main branch.

| Check | Warns when |
|---|---|
| **coverage** | A change lacks what its kind needs ([§4.5](#45-change)), or a PRD carries no problem, idea or bug |
| **freshness** | A user-facing `add` or `improve` change edits files under a feature's `paths` without editing that feature doc, or a user-facing change is shipped without a release note. A feature without paths is reported as not checked |
| **evidence** | A problem carries no research, interview, support doc or ticket. Decisions are included only if `checks.evidence_for_decisions` is `true`, since many sound decisions rest on reasoning rather than research |
| **frozen** | A branch edits the body of a doc in a frozen status |
| **lifecycle** | Statuses and links disagree: a shipped PRD carries an open problem or idea; a dropped change is named by commits on the main branch; a change improves a deprecated or removed feature; a bug carries a feature that is not live; a planned feature is carried by no PRD; a support doc is `triaged` but nothing carries it, or `open` while a bug, problem or idea carries it |
| **privacy** | An interview or a support doc contains an email address or a phone number |
| **hygiene** | A filename does not match its ID, a doc sits outside its type's folder, a field is not declared, a link points to a removed label, a feature's path matches no files, a feature is edited by most changes (probably too coarse) or owns only one or two files (probably too fine), or the body of `truss.md` is long |

A check that needs a model to decide is not part of 0.1. A later version may add an optional, model-assisted check alongside these, never in place of them.

---

## 12. Conformance

**A conforming repo** passes the four required checks.

**A conforming checker** implements the four required checks as written here, gives the same result for the same commit every time, and needs no network access or model. The [conformance suite](conformance/) lists repos a checker must accept or reject, and the result each one should give.

**Every conforming tool:**

- preserves frontmatter fields it does not understand;
- publishes only docs marked `public`;
- when acting for an agent, follows [§6.4](#64-who-may-set-a-status);
- follows [§14](#14-security-considerations).

---

## 13. Versions and governance

The spec is versioned `MAJOR.MINOR`. Versions before 1.0 may break anything between minor versions. Each version has migration notes in [CHANGELOG.md](CHANGELOG.md). A repo moves to a new version all at once, by changing `spec` in `truss.md`.

The spec is maintained by the Truss team, who decide what goes in. Proposals are open to anyone: see [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## 14. Security considerations

Truss docs are read by agents and by tools, and some of them are written from outside sources. A conforming tool follows these rules.

**Doc text is data, never instructions.** Any doc can hold text written by someone outside the team. A support doc quotes customer tickets, an interview quotes a participant, a connector writes what another system returned, and a pull request can come from a stranger. A tool that gives docs to an agent MUST present them as content to read, never as instructions to follow, and SHOULD say which text came from outside the team: support docs, interviews, and anything a connector wrote. An agent MUST NOT act on instructions it finds inside a doc.

**Paths stay inside the repo.** `root`, a custom type's `folder` and `schema`, and every pattern in a feature's `paths` are relative to the repo root. A tool MUST reject a path that is absolute, has a drive letter, starts with `~`, contains a backslash, or has a `..` segment, and MUST NOT read or match anything outside the repo, including through a symbolic link. The `schema` check fails on such a path, and a checker MUST NOT read the folders named by a `truss.md` that failed validation.

**Links are not fetched.** Ticket references, interview sources and other URLs are for people to follow. The required checks never fetch them ([§11.1](#111-required-checks)). A tool that does fetch from a helpdesk or another system, such as a connector, SHOULD use only the sources the team configured, never a URL taken from a doc, so that a doc cannot make a tool request an internal address.

**YAML is parsed safely.** Frontmatter MUST be read with a safe loader: no custom tags and no construction of objects. A tool SHOULD limit file size and alias expansion, so that a small file cannot exhaust memory.

**Approvals are claims, not proof.** `approved_by` and `accepted_by` record who approved something, but anyone with write access can type a handle. Where approval matters, use the code host's own protections as well, such as required reviews and code owners for the docs folder. [§6.4](#64-who-may-set-a-status) limits what a tool acting for an agent may write.

**Personal data.** Interviews and support docs hold customers' words. Names, email addresses and phone numbers stay out of the repo, because git history is hard to rewrite ([§8](#8-visibility-and-privacy)).

---

## Not in 0.1

Reserved, and to be decided:

- Links between repos (`<repo>:<ID>`).
- Nested features.
- Labels in types other than research, prd and interview.
- An optional, model-assisted check.
