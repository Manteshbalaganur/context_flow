# CheckIN — Bengaluru Tech Week Buildathon 2026

> **Know where your code is, and why it’s there.**

CheckIN is a checkpoint-native developer intelligence and handoff platform for
human developers and AI coding agents. It combines Git evidence, Entire
checkpoint context, dependency impact, and Databricks processing into a
project-scoped Streamlit workspace.

## Problem statement

Modern development teams increasingly work alongside AI coding agents. A pull
request or Git diff tells the next person *what* changed, but rarely explains:

- the requirement and original intent behind a change;
- assumptions made by the author or agent;
- failed approaches and unresolved work;
- which components may be affected;
- whether an implementation drifted beyond its stated scope; or
- whether a project is safe to hand over.

This creates a costly context gap. Developers joining a project and agents
resuming work must reconstruct decisions from commits, conversations, logs, and
files. Existing project dashboards normally track delivery activity, not the
reasoning and evidence needed for a reliable handoff.

## Proposed solution

CheckIN creates a persistent development-memory layer. A project CheckIN joins
four evidence sources into one `DevelopmentEvent`:

1. **Git evidence** — branch, commits, changed files, and working-tree status.
2. **Entire context** — native checkpoint/session metadata when Entire is
   available, plus clearly labelled manually entered context when it is not.
3. **Graph evidence** — Python import/dependency analysis that estimates
   affected modules and confidence.
4. **Databricks intelligence** — checkpoint processing and project-scoped
   insights stored in Delta tables.

The result is an explainable health view, a timeline of development memory, and
a downloadable CheckOUT handoff rather than an unexplained score.

## Buildathon track alignment

**Track 1: Build a Checkpoint-Native Developer Experience**

Entire is the source of record for checkpoint-backed context. CheckIN does not
pretend that manual notes are Entire checkpoints. It surfaces the distinction:

- **Native Entire checkpoint:** created when Entire captures agent-session
  context and links it to a Git commit.
- **CheckIN event:** a normalized project-memory record assembled by the
  application, including Git, context, and impact evidence.

This preserves trust in the checkpoint model while allowing a working dashboard
in local/demo mode before integrations are configured.

## Key capabilities

| Capability | What it provides |
| --- | --- |
| Multi-project portfolio | Register, select, and inspect isolated projects; every local record and production query carries `project_id`. |
| CheckIN workflow | Collect Git data, context, dependency impact, normalized events, and explainable intelligence in one action. |
| Entire visibility | Detect Entire CLI availability, show native checkpoint history, and guide correct setup when unavailable. |
| Context capture | Record intent, assumptions, attempted actions, failures, unresolved work, and verification status. |
| Intelligence | Completion, risk, intent drift, context debt, blast radius, checkpoint gaps, release readiness, and handoff readiness. |
| Databricks insights | Read Delta-processed checkpoint insights through Databricks SQL Connector. |
| CheckOUT | Generate and download a project-specific Markdown handoff. |

## Architecture

```text
Developer / AI agent
       │
       ├── code changes ───────────────► Git repository
       │                                      │
       └── session context ────────────► Entire agent + Git hooks
                                              │
                                      Native checkpoint / session
                                              │
Git evidence + Entire context + dependency evidence
                                              │
                                              ▼
                              CheckIN ingestion layer
                         (git_service, entire_service,
                                  graph_service)
                                              │
                                              ▼
                           Normalization layer
                       (validated DevelopmentEvent)
                                              │
                       ┌──────────────────────┴──────────────────────┐
                       ▼                                             ▼
              Local JSON demo store                         Databricks Delta
              (safe fallback)                     raw_checkpoints → llm_insights
                       │                                             │
                       └──────────────────────┬──────────────────────┘
                                              ▼
                                  Analysis + exposure layer
                                              │
                                              ▼
                                  Streamlit project dashboard
                                              │
                                              ▼
                                      CheckOUT handoff
```

### Service boundaries

| Service | Responsibility |
| --- | --- |
| `project_service.py` | Project registration, repository mapping, selection, and metadata. |
| `sync_service.py` | Project-aware orchestration of a CheckIN workflow. |
| `git_service.py` | Read-only Git repository and working-tree evidence. |
| `entire_service.py` | Optional Entire CLI status and checkpoint discovery. |
| `graph_service.py` | Python import/dependency impact estimation. |
| `event_normalizer.py` | Validation and construction of the central `DevelopmentEvent`. |
| `analysis_service.py` | Explainable score and readiness heuristics. |
| `databricks_service.py` | Local fallback storage and read-only Databricks SQL insight access. |
| `handoff_service.py` | Markdown CheckOUT generation. |

## Entire integration workflow

1. Install and authenticate the Entire CLI on the developer machine.
2. From the target Git repository, enable capture for the coding agent:

   ```powershell
   entire enable --agent codex
   ```

3. Work with the enabled agent, stage the resulting changes, and commit them.
4. Entire’s hooks link captured agent-session context to that commit, producing
   a native checkpoint.
5. In CheckIN, register the repository path and select the project.
6. The **Entire Context** page calls the CLI read-only to show real checkpoint
   records. If the CLI is missing or unavailable, it shows a setup warning;
   CheckIN never fabricates a native Entire ID.

Native checkpoint creation belongs to Entire’s agent and Git-hook workflow, not
to a Streamlit button. A saved context form creates a labelled local CheckIN
event that can enrich a future checkpoint-backed handoff.

## Databricks workflow

The repository includes `databricks/checkpoint_processor.py`, designed for the
`hackathon-data-pipeline` job and its `checkpoint_processor` notebook.

```text
Entire checkpoint JSON / job parameter
        │
        ▼
checkin_db.raw_checkpoints (Delta)
        │  idempotent MERGE on project_id + checkpoint_id
        ▼
deterministic / AI-backed processing
        │
        ▼
processed_db.llm_insights (Delta)
        │
        ▼
Databricks SQL Connector
        │  selected project_id only
        ▼
CheckIN → Project Intelligence page
```

### Delta tables

`checkin_db.raw_checkpoints`

- `project_id`, `checkpoint_id`, `timestamp`, `agent`, `message`
- `files_changed`, `raw_context`, `branch`, `ingestion_time`

`processed_db.llm_insights`

- `project_id`, `checkpoint_id`, `timestamp`, `agent`
- `intent`, `status`, `summary`, `risk_level`, `completion_score`
- `recommendations`, `unresolved_issues`, `files_changed`, `processing_time`

The notebook performs a safe legacy migration: if an existing table lacks
`project_id`, it adds the column. A `default_project_id` job parameter can
backfill only null legacy rows once. All future ingestion must supply a real
`project_id` with every checkpoint.

### Streamlit connection configuration

Create a local `.env` file from `.env.example`; never commit it.

```text
DATABRICKS_SERVER_HOSTNAME=<workspace-hostname>
DATABRICKS_HTTP_PATH=<sql-warehouse-http-path>
DATABRICKS_ACCESS_TOKEN=<personal-access-token>
CHECKIN_DATABRICKS_INSIGHTS_TABLE=processed_db.llm_insights
```

The Project Intelligence page includes a read-only **Test Databricks
connection** action. It runs `SELECT 1`, then schema-inspects the configured
insights table. If legacy rows lack `project_id`, the UI shows them with an
explicit migration warning rather than silently claiming project isolation.

## Explainable analytics

CheckIN treats analytics as evidence-led heuristics. Every outcome includes a
result, a reason, and evidence used.

| Metric | Evidence considered |
| --- | --- |
| Completion score | Unresolved work, failures, Git availability, and change coverage. |
| Risk | Unresolved work, failures, affected component count, and collection warnings. |
| Context debt | Missing intent/assumptions/actions, unresolved work, failures, and unverified impact. |
| Intent drift | Stated intent compared with changed paths and scope. |
| Blast radius | Changed components and discovered dependency references. |
| Smart gaps | Large undocumented changes, unresolved work without action context, and missing verification. |
| Handoff readiness | Risk, context debt, unresolved work, and evidence completeness. |

Impact analysis is labelled **estimated** unless verified evidence exists.

## Critical and Curveball behavior

### Critical behavior

- A CheckIN without a connected Git repository remains usable and reports a
  clear warning rather than crashing.
- Missing Entire CLI or Databricks credentials results in explicit setup state,
  not invented checkpoint or pipeline data.
- Databricks SQL access is read-only from Streamlit and validates project/table
  identifiers before querying.
- Every normalized local event uses the selected `project_id`.
- CheckOUT produces a project-specific Markdown document without mixing
  portfolio evidence.

### Curveball: legacy Databricks schema

The pipeline may already contain useful rows without `project_id`. CheckIN
detects this schema, displays the legacy records with a warning, and the
provided notebook migrates the tables without deleting data. This lets a
Buildathon demo continue while moving toward correct multi-project isolation.

### Curveball: Entire unavailable during a demo

The dashboard stays functional with local CheckIN events and demo records. It
never labels those records as native Entire checkpoints and presents the exact
CLI setup required to enable capture later.

## Validation and test checklist

Run these commands from the `checkin` directory before a demo:

```powershell
python -m pip install -r requirements.txt
python -m compileall -q .
python -m streamlit run app.py
```

Critical-path acceptance checks:

- [x] Python compilation passes for application, services, pages, and notebook
  source.
- [x] A CheckIN creates a project-scoped event in local fallback storage.
- [x] Git/Entire/Databricks unavailability produces user-facing warnings rather
  than application failure.
- [x] The Databricks connector validates credentials/configuration before
  querying.
- [x] CheckOUT download produces a readable project-specific Markdown handoff.

Curveball acceptance checks:

- [x] Legacy `processed_db.llm_insights` schemas without `project_id` are
  detected and shown with a migration warning.
- [x] The Databricks notebook adds `project_id` without dropping existing
  records and supports a one-time null-row backfill.
- [x] No credentials, tokens, hosts, warehouse paths, or user data are stored
  in source-controlled files.

## Local runbook

```powershell
cd C:\Users\Mahantesh\OneDrive\Desktop\contextflow\checkin
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m streamlit run app.py
```

1. Register/select a project.
2. Map its local repository path.
3. Use **CHECK IN PROJECT** to collect evidence.
4. Add context on the **Entire Context** page.
5. Configure Databricks locally and run the checkpoint processor job.
6. Review results on **Project Intelligence**.
7. Generate a **CheckOUT** handoff.

## Security and privacy

- `.env` and Streamlit secrets are excluded from Git.
- This document contains placeholders only—no secrets, access tokens, hosts,
  or workspace identifiers.
- Streamlit uses Databricks only for read-only insight queries.
- Entire records are shown only when the local CLI can access the mapped
  repository.
- Project-scoped querying prevents cross-project data exposure after migration.

## Demo narrative

Start with the portfolio dashboard to show multiple project health states. Open
a project, run a CheckIN, and show how changed files and recorded context become
an explainable risk and context-debt assessment. Show native Entire checkpoint
history when configured, then open the Databricks insight table. Finish with a
CheckOUT handoff that gives the next human or agent a concrete, evidence-backed
next step.
