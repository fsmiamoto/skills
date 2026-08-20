---
name: delegate
description: Deliver an already-aligned change through coordinated implementation delegation, independent review, verification, and real user-surface UAT. Use after scope and acceptance criteria are settled when implementation should be handed off without reopening product decisions.
disable-model-invocation: true
---

# Delegate

Use this skill **after alignment**. The goal is to carry settled intent through implementation, review, and verification—not to add planning ceremony or renegotiate the request.

## Preserve the agreement

Before delegating, capture a short delivery contract:

- acceptance criteria and required user-visible behavior
- settled decisions and constraints
- relevant files/surfaces and known context
- explicit exclusions
- verification expectations
- the Git/release boundary

Treat these as fixed. Ask the user only when work encounters a true blocker, a risky or irreversible boundary, or missing product judgment that cannot be inferred safely. Do not ask for preferences that were already settled.

## Assign ownership adaptively

1. Identify implementation surfaces and where edits may overlap.
2. Give each overlapping surface to **one coordinated writer**. Prefer one writer for a tightly coupled change; use multiple writers only for clearly disjoint ownership.
3. Require a separate, read-only peer review after implementation. The reviewer must not fix the code they review.
4. Keep orchestration and independent UAT under your ownership. Add focused specialists—security, accessibility, database, performance, platform, or domain experts—only when the risk justifies them.

Use the reusable briefs in [references/briefs.md](references/briefs.md). Give agents enough settled context to act without rediscovery, plus explicit file ownership and stop conditions.

## Deliver

1. **Establish a baseline.** Inspect repository guidance and working-tree state. Preserve unrelated user changes.
2. **Delegate implementation.** Send one coordinated writer per overlapping surface. Do not create competing edits.
3. **Wait normally.** Avoid polling or peeking. Use the host's normal completion mechanism. Inspect a running agent only after an unusually long wait **and** when there is a concrete reason to suspect it is stuck.
4. **Inspect directly.** Treat agent summaries and test claims as evidence, not proof. Read the resulting diff and relevant files yourself; check for scope drift, omissions, regressions, and unintended edits.
5. **Run relevant checks.** Execute the tests, lint, typecheck, and build steps appropriate to the changed surface. A passing build or test suite is not UAT.
6. **Require peer review.** Give a separate reviewer the delivery contract and current diff. Keep review read-only and ask for findings prioritized by severity with file/line evidence.
7. **Close blocking findings.** Return blocking findings to the owning writer. After fixes or any materially changed code, inspect again and rerun affected checks. Send the affected surface back to a separate read-only peer reviewer; do not close the finding until that reviewer confirms no blocking issue remains. Repeat as needed.
8. **Perform independent UAT.** Exercise the real user-facing surface through the interface users actually use. Verify acceptance criteria and important failure/edge behavior. Examples include using the browser, driving a CLI/TUI in a real terminal, calling the public API, or running the packaged artifact.

If UAT cannot be run, do not call the work green. Either resolve the environment gap or report a genuine blocker and the evidence gathered.

## Green gate

Delivery is green only when all are true:

- aligned acceptance criteria are satisfied
- direct diff inspection found no unresolved scope or correctness issue
- no blocking peer-review findings remain
- independent user-surface UAT passed
- relevant tests, lint, typecheck, and build checks passed

Report changed paths, review disposition, UAT performed, check results, and any non-blocking residual risk.

## Notifications and Git boundary

When the delivery becomes green, notify the user once through an available host mechanism. If progress is genuinely blocked and needs the user, notify them with the blocker and required action instead. Never notify for routine intermediate progress. When available, a concrete option is:

```bash
cmux notify --title "Delivery" --body "[project] Green: verified change ready for review"
```

Adapt the mechanism and message to the host. If no host notifier is available, use the final response as the fallback; notifier availability or failure does not change the delivery verdict.

By default, leave verified changes in the working tree. Never commit, push, open or update a pull request, deploy, or publish unless that action was explicitly part of the aligned request.
