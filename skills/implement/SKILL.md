---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

# Implement

Implement the work described by the user in the provided spec or tickets.

## Establish the delivery contract

Before editing:

- read the spec or tickets and identify the acceptance criteria, constraints, and explicit exclusions
- inspect repository guidance and the current working-tree state
- preserve unrelated changes
- clarify only genuine blockers or product decisions that cannot be inferred safely

Treat the agreed spec and tickets as the source of truth. Do not expand scope without user approval.

## Implement

1. Break the work into small, verifiable increments.
2. Use `/tdd` where possible at pre-agreed seams. Do not force test-first development onto seams where it was not agreed or is impractical.
3. After each meaningful increment, run the relevant single test file or smallest focused test target.
4. Run typechecking regularly while working, not only after implementation is complete.
5. Inspect the diff throughout and correct scope drift, regressions, and unintended edits.

Do not hide failing checks or weaken tests merely to make them pass.

## Verify

Once implementation is complete:

1. Rerun the affected focused tests and typechecking.
2. Run the full test suite once, at the end.
3. Confirm the acceptance criteria are satisfied and the final diff contains only intended changes.

If the full suite cannot run or fails for reasons outside the change, report the exact blocker and evidence rather than claiming success.

## Commit

Commit the completed work to the current branch.

- include only files belonging to this work; do not commit unrelated user changes
- use a concise commit message that describes the implemented outcome
- verify the commit succeeded and report the commit hash
