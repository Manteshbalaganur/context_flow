# CheckIN

**Know where your code is, and why it's there.**

CheckIN is a multi-project developer-intelligence and persistent project-memory workspace. It merges Git evidence, development context, dependency impact, and explainable project intelligence into a project-scoped CheckOUT handoff.

## Run

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The application launches in demo mode with isolated sample projects. Register a local Git repository from the sidebar to run a real CheckIN. Git, Entire, and Databricks integrations degrade gracefully when not configured.

## Entire checkpoints

CheckIN displays real Entire CLI checkpoint history when Entire is installed and enabled for the mapped repository. Checkpoints are created by Entire when captured agent-session context is linked to a Git commit; saving the CheckIN context form creates a local CheckIN event, not an artificial Entire checkpoint. Set up capture with `entire enable --agent codex`, work through the agent, then stage and commit the change.

## Architecture

`Git + Entire context + dependency evidence → DevelopmentEvent → storage → intelligence → project memory → Streamlit → CheckOUT`

Every stored object and query is scoped by `project_id`. Local JSON persistence is used for demos; `.env` can configure production integrations using `.env.example`. Dependency impact is heuristic unless explicitly verified.

## Databricks pipeline

Import `databricks/checkpoint_processor.py` into the `checkpoint_processor` notebook for the `hackathon-data-pipeline` job. Add `DATABRICKS_SERVER_HOSTNAME`, `DATABRICKS_HTTP_PATH`, and `DATABRICKS_ACCESS_TOKEN` to `.env`. The notebook and dashboard both use the active CheckIN project's `project_id`; use that exact value when ingesting checkpoint records. The dashboard is read-only against `processed_db.llm_insights` and gracefully falls back to local data if Databricks is unavailable.
