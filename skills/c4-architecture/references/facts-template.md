# Facts file template

One file per research area (`facts-infra.md`, `facts-runtime.md`, `facts-core.md`). Every line is a fact the page
may state, with the path (and symbol or line) that proves it. The page and the audit draw only from these files.

```markdown
# Facts: <area> (built state at <short sha>)

Path aliases: `TF`=deploy/terraform, `M`=cmd/server/main.go, ... (cite as alias + path below it, never `..`)

## <topic, e.g. Runtime topology>
- <fact in one line, with exact names/numbers>. (`TF/sql.tf` google_sql_database_instance.main; `M` flag --port)
- <fact> **PLANNED** (docs/roadmap.md "Webhooks") — only in docs/issues, absent in code.
- <fact> **UNSURE** — <what was checked, what is missing>.
- <fact> **UNDEPLOYED** (`X/server.py` mode flag) — in code, but no IaC/CI/compose runs it.
- <fact> **DOC-DRIFT** (README says 3 phases; `X/spec.py` has 4) — the page follows the code.

## For the diagrams
- L<n> elements: <name> [kind] — <one-line role> (path)
- L<n> edges: <from> → <to> "<label>" (path where the call happens)

## Open questions
- <anything the page should not claim until resolved>
```

Rules:
- **At most 120 lines per file, one fact per line, each line under ~200 characters.** No paragraphs, no code
  excerpts, no file listings. A fact the diagrams or notes won't use stays out.
- Write only this file. The repo is read-only.
- Built means present in code/IaC/CI on HEAD. Docs, plans, TODOs, and issues are **PLANNED**.
- Names and numbers are copied exactly (resource names, flags, defaults, table names, intervals).
- Facts no file proves are marked **UNSURE** and stay off the page.
- **UNDEPLOYED** code may appear in L3/L4 with a note, never as a running box in L2.
- When docs and code disagree, code wins; mark **DOC-DRIFT** so the audit can mention it.
