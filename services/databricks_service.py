"""Storage boundary: durable JSON demo store, replaceable by Databricks SQL implementation."""
import json
import re
from utils.config import DATA_FILE, has_databricks_config, databricks_table
EMPTY = {"projects": [], "checkpoints": [], "code_changes": [], "graph_impact": [], "events": [], "analysis": []}
def _load():
    if not DATA_FILE.exists(): return {k: list(v) for k,v in EMPTY.items()}
    try: return {**EMPTY, **json.loads(DATA_FILE.read_text(encoding="utf-8"))}
    except (json.JSONDecodeError, OSError): return {k: list(v) for k,v in EMPTY.items()}
def _save(data): DATA_FILE.parent.mkdir(parents=True, exist_ok=True); DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
def query_projects(): return _load()["projects"]
def store_project(project):
    data=_load(); data["projects"]=[x for x in data["projects"] if x["project_id"] != project["project_id"]]+[project]; _save(data)
def store_event(event, checkpoint, changes, impacts):
    data=_load(); pid,cid=event["project_id"],event["checkpoint_id"]
    data["events"]=[x for x in data["events"] if x.get("event_id") != event["event_id"]]+[event]
    data["checkpoints"]=[x for x in data["checkpoints"] if x.get("checkpoint_id") != checkpoint["checkpoint_id"]]+[checkpoint]
    data["code_changes"]=[x for x in data["code_changes"] if not(x["project_id"]==pid and x["checkpoint_id"]==cid)]+changes
    data["graph_impact"]=[x for x in data["graph_impact"] if not(x["project_id"]==pid and x["checkpoint_id"]==cid)]+impacts; _save(data)
def store_analysis(analysis):
    data=_load(); data["analysis"]=[x for x in data["analysis"] if x["analysis_id"] != analysis["analysis_id"]]+[analysis]; _save(data)
def project_rows(name, project_id): return [x for x in _load()[name] if x.get("project_id")==project_id]
def latest_analysis(project_id):
    rows=project_rows("analysis",project_id); return sorted(rows,key=lambda x:x.get("timestamp",""))[-1] if rows else None
def latest_event(project_id):
    rows=project_rows("events",project_id); return sorted(rows,key=lambda x:x.get("timestamp",""))[-1] if rows else None

def pipeline_connection_status():
    """Report connection readiness without exposing credentials."""
    if not has_databricks_config():
        return {"connected": False, "message": "Databricks credentials are not configured; using local CheckIN storage."}
    try:
        from databricks import sql  # noqa: F401
        return {"connected": True, "message": "Databricks SQL connector is configured."}
    except ImportError:
        return {"connected": False, "message": "Install databricks-sql-connector to query pipeline insights."}

def query_pipeline_insights(project_id, limit=50):
    """Read only processed, project-scoped pipeline results from Delta/Databricks SQL."""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", project_id or ""):
        return [], "Invalid project identifier."
    status = pipeline_connection_status()
    if not status["connected"]:
        return [], status["message"]
    table = databricks_table("CHECKIN_DATABRICKS_INSIGHTS_TABLE", "processed_db.llm_insights")
    if not re.fullmatch(r"[A-Za-z_][\w.]*", table):
        return [], "Invalid configured insights table name."
    try:
        from databricks import sql
        import os
        with sql.connect(server_hostname=os.environ["DATABRICKS_SERVER_HOSTNAME"], http_path=os.environ["DATABRICKS_HTTP_PATH"], access_token=os.environ["DATABRICKS_ACCESS_TOKEN"]) as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT checkpoint_id, timestamp, agent, intent, status, summary, risk_level, completion_score, recommendations, unresolved_issues, files_changed, processing_time FROM {table} WHERE project_id = :project_id ORDER BY processing_time DESC LIMIT {int(limit)}", {"project_id": project_id})
                columns = [item[0] for item in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()], None
    except Exception as exc:
        return [], f"Databricks query unavailable: {exc}"
