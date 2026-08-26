---
name: pr-comments
description: Iterate over PR review comments with the user to build an action plan, then execute it. Use when the user wants to address, triage, or work through PR review feedback. Keywords - PR comments, review comments, address feedback, review feedback.
---

# PR Comments

Work through PR review feedback **with** the user, not for them. Grill them into an action plan first; only touch code or GitHub after they approve.

## 1. Fetch

Determine the PR (current branch's PR via `gh pr view --json number,url,title`, or ask). Then fetch:

- **Inline review comments**: `gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate`
- **Review bodies**: `gh api repos/{owner}/{repo}/pulls/{number}/reviews --paginate` (skip empty bodies)

Skip the user's own comments unless they ask otherwise. Group inline comments by thread (`in_reply_to_id`); treat a thread as one item, and read replies for context. Present a short numbered overview (author, file:line, one-line gist) before starting.

## 2. Grill — one comment at a time

For each item, in order:

1. Show the comment verbatim with its context (file, line, diff hunk). Read the referenced code before forming an opinion.
2. Give your assessment: is the reviewer right? What would fixing it involve? What are the trade-offs?
3. Ask the user for a decision, one question at a time, with your recommended answer first. Decisions per item:
   - **Fix** — agree the concrete change (what, where, how far).
   - **Reply** — draft a response; no fix needed or pushing back.
   - **Defer** — out of scope; capture as follow-up (note/ticket).
   - **Dismiss** — no action; capture the rationale.
4. If the decision has sub-questions (approach A vs B, scope boundaries), walk down them one by one until the action is unambiguous.

Facts you can look up in the repo (does X handle Y? is there a test?), look up yourself. Decisions belong to the user.

**During this loop: no code edits, no GitHub writes, nothing user-visible without consent.**

## 3. Plan

After the last item, present the consolidated action plan: every comment with its decision and planned action. Get explicit approval. The user may reorder, merge, or revise items here.

## 4. Execute

Only after plan approval:

- Implement the agreed fixes. Stay within the agreed scope; if a fix reveals something unplanned, come back and ask.
- Run relevant tests/lint for touched code.
- Do **not** commit or push unless the user asks.

## GitHub writes — explicit consent, every time

Never reply to a comment, resolve a thread, submit a review, or perform any other GitHub write without showing the exact text/action and getting a fresh, explicit yes for that specific write. Plan approval does not count as consent for GitHub writes.
