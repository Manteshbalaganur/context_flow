"""Storage boundary: durable JSON demo store, replaceable by Databricks SQL implementation."""
import json
from utils.config import DATA_FILE
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
