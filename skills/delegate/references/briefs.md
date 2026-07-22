# Delivery briefs

Use these as compact checklists, not ceremony. Remove irrelevant fields; retain settled decisions and boundaries. Adapt them to the host's required delegation schema; the headings below match hosts that require Goal, Success Criteria, Constraints, Output, and Stop Rules.

## Implementation brief

```markdown
# Goal
Implement the already-aligned change: <outcome>.

# Success Criteria
- <observable requirement>
- Preserve this settled decision: <decision>.

# Constraints
- Ownership: edit <surface>; do not edit <other owned/unrelated surface>.
- Preserve unrelated working-tree changes.
- Do not commit, push, create/update a PR, deploy, or publish unless explicitly included in the goal.

# Output
Implement the change, run <relevant focused checks>, and report changed paths, results, assumptions, and unresolved risks.

# Stop Rules
Stop and report rather than guessing across a true blocker, risky or irreversible boundary, or missing product judgment.
```

## Read-only peer-review brief

```markdown
# Goal
Review the current diff against the settled delivery contract: <contract>.

# Success Criteria
- Check correctness, regressions, edge and failure behavior, security or data risk, maintainability, test adequacy, and scope drift.
- Focus on changed code and affected call paths.
- Report actionable findings as blocking or non-blocking, with file/line evidence and rationale.
- State explicitly when no blocking findings remain and note verification gaps.

# Constraints
- Read only: do not edit files.
- Verify claims against the diff and repository; do not rely on the writer's summary.

# Output
Return a concise approval or rejection verdict with prioritized findings and evidence.

# Stop Rules
Stop when there is enough evidence for an approval or rejection verdict. Never modify the reviewed files.
```

## UAT and verification record

```markdown
Acceptance criterion: <criterion>
User surface exercised: <browser / CLI-TTY / public API / packaged artifact / other>
Scenario and inputs: <steps>
Observed result: <actual behavior>
Outcome: PASS | BLOCKED | FAIL
Evidence: <output, screenshot, trace, or concise observation>

Automated checks:
- <test/lint/typecheck/build command>: PASS | FAIL

Review:
- Blocking findings: <none or disposition>
- Separate peer reviewer confirmed no blocking findings after material changes: <yes/no/not applicable>
```
