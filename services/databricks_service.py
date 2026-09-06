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

def _safe_table_name():
    table = databricks_table("CHECKIN_DATABRICKS_INSIGHTS_TABLE", "processed_db.llm_insights")
    if not re.fullmatch(r"[A-Za-z_][\w.]*", table):
        raise ValueError("Invalid configured insights table name.")
    return table

def _connect():
    from databricks import sql
    import os
    return sql.connect(server_hostname=os.environ["DATABRICKS_SERVER_HOSTNAME"], http_path=os.environ["DATABRICKS_HTTP_PATH"], access_token=os.environ["DATABRICKS_ACCESS_TOKEN"])

def test_pipeline_connection():
    """Run a minimal read-only query so the UI can distinguish config from access."""
    status = pipeline_connection_status()
    if not status["connected"]:
        return False, status["message"]
    try:
        with _connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        return True, "Connected to Databricks SQL Warehouse."
    except Exception as exc:
        return False, f"Databricks connection failed: {exc}"

def query_pipeline_insights(project_id, limit=50):
    """Read processed insights, preserving isolation where the Delta schema supports it."""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", project_id or ""):
        return [], "Invalid project identifier."
    status = pipeline_connection_status()
    if not status["connected"]:
        return [], status["message"]
    try:
        table = _safe_table_name()
        with _connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"DESCRIBE {table}")
                schema_columns = {row[0].lower() for row in cursor.fetchall()}
                if not schema_columns:
                    return [], f"Databricks table `{table}` was not found or has no columns."
                order_column = "processing_time" if "processing_time" in schema_columns else "timestamp"
                if "project_id" in schema_columns:
                    query = f"SELECT * FROM {table} WHERE project_id = :project_id ORDER BY {order_column} DESC LIMIT {int(limit)}"
                    cursor.execute(query, {"project_id": project_id})
                    warning = None
                else:
                    # Existing screenshot schema is legacy: it predates project_id.
                    # Surface it for migration, but never claim it is project-isolated.
                    cursor.execute(f"SELECT * FROM {table} ORDER BY {order_column} DESC LIMIT {int(limit)}")
                    warning = f"Legacy Databricks schema detected: `{table}` has no project_id, so these rows are not project-isolated. Add project_id and rerun the pipeline."
                columns = [item[0] for item in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()], warning
    except Exception as exc:
        return [], f"Databricks query unavailable: {exc}"
