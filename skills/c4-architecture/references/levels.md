# Levels: what each zoom shows

The page is one zoom: each level is a box from the level above, opened. The hero lens and the "you are here"
minis draw that nesting, so every level must visibly be *inside* the previous one.

Figure budget: L1 one figure; L2 one or two; L3 one or two; L4 two to five. Each figure gets a `<h3>`, a one-line
`.sub` reading hint, a `<figcaption>`, and "What is true today" notes (3–5 bullets, each with a src link).

## L1 System context
- Shows: people (by role, with what they are allowed to do), the system in focus as one `kf` box, every external
  system it calls or is called by (source host, cloud, SaaS APIs, identity provider), with one labelled arrow each.
- Answers: who uses it, what it depends on, which direction each call goes (push, poll, webhook).
- Facts to find: entrypoints, auth/roles, outbound clients (SDK imports, base URLs), inbound hooks.

## L2 Containers and infrastructure
- Shows: every separately deployable/running unit (service, worker, job, CLI, SPA, database, queue, bucket),
  inside boundaries for the account/project/cluster/region that hosts it. Secrets, registry, proxy/IAP/LB,
  scheduler. Optionally a second figure for *delivery*: how code becomes a running container (CI jobs, artifacts,
  rollout).
- Answers: what runs where, how a request reaches it, where state lives, how it ships.
- Facts to find: IaC (Terraform, Helm, k8s manifests, CDK, compose), Dockerfiles, CI workflows, deploy scripts,
  env/config files, runbooks. Mark resources created outside IaC (scripts, console) explicitly.
- Several near-identical environments (dev/stage/prod): draw one representative (usually prod) and name the
  others and their differences in the caption.

## L3 Components
- Shows: the main container opened: packages/modules as boxes, solid arrows for runtime calls, dashed for imports
  of shared types. A second figure for a second big container (UI layers, worker) when it has its own structure.
- Answers: how the code is cut, which way dependencies point, which rules enforce it (lint configs, module
  graph rules, CODEOWNERS).
- Facts to find: `cmd/` / `main` wiring, package docs, import graph (`go list -deps`, `grep import`), boundary
  rules in lint config.

## L4 The core mechanism
Pick the one thing a new engineer must understand to change the system safely; name L4 after it (Engine, Request
path, Pipeline, Scheduler, Sync loop). Match the figure to its shape:

| Mechanism shape | Figure | c4kit helper |
|---|---|---|
| periodic loop / reconciler / tick | numbered step ring + `<ol class="ticks">` list | `ring()` |
| entity lifecycle / slot / job status | state machine of pills, labelled transitions | `state()` + `edge()` |
| request or event flowing through parts | numbered sequence with phase bands | `sequence()` |
| pure decision function | inputs → function box → outputs/commands | `box()` + `edge()` |
| data model | entity boxes (`shape='db'` for stores) with relation labels | `box()` |
| crash safety / idempotency | one row's status lane with durable-write diamonds | `state()` + paths |

Two to five figures usually tell it: the loop or entry, the decision core, one lifecycle, one end-to-end trace.

## Lens tuples
`LEVELS = [('l1', 'L1  System context', '<3-4 words>'), ('l2', ...), ('l3', ...), ('l4', 'L4  <name>', ...)]`,
outermost first. Labels are short; subs fit the frame (c4kit WARNs otherwise).
