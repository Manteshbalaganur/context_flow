# CheckIN

**Know where your code is, and why it's there.**

CheckIN is a multi-project developer-intelligence and persistent project-memory workspace. It merges Git evidence, development context, dependency impact, and explainable project intelligence into a project-scoped CheckOUT handoff.

## Run

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The application launches in demo mode with isolated sample projects. Register a local Git repository from the sidebar to run a real CheckIN. Git, Entire, and Databricks integrations degrade gracefully when not configured.

## Architecture

`Git + Entire context + dependency evidence → DevelopmentEvent → storage → intelligence → project memory → Streamlit → CheckOUT`

Every stored object and query is scoped by `project_id`. Local JSON persistence is used for demos; `.env` can configure production integrations using `.env.example`. Dependency impact is heuristic unless explicitly verified.
