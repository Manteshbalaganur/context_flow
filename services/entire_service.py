"""Optional Entire CLI adapter.

Entire checkpoints are created by Entire's agent and Git hooks when a captured
agent session is linked to a Git commit. CheckIN never invents an Entire ID.
"""
import json
import os
import shutil
import subprocess
from models import EntireCheckpoint
from utils.helpers import now_iso

def _cli():
    configured = os.getenv("ENTIRE_CLI_PATH", "entire")
    return configured if shutil.which(configured) else None

def _run(args, cwd):
    cli = _cli()
    if not cli:
        return None, "Entire CLI is not installed or is not on PATH."
    try:
        result = subprocess.run([cli, *args], cwd=cwd, text=True, capture_output=True, timeout=20)
        if result.returncode:
            return None, (result.stderr or result.stdout or "Entire command failed.").strip()
        return result.stdout.strip(), None
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"Entire command could not run: {exc}"

def get_status(repository_path=None):
    output, error = _run(["status", "--json", "--no-pager"], repository_path)
    if error:
        return {"available": False, "enabled": False, "message": error}
    try:
        return {"available": True, "enabled": True, "data": json.loads(output), "message": "Entire CLI connected."}
    except json.JSONDecodeError:
        return {"available": True, "enabled": True, "data": {"raw": output}, "message": "Entire CLI connected."}

def list_native_checkpoints(repository_path=None):
    """Return actual CLI records only; errors are surfaced instead of mocked."""
    output, error = _run(["checkpoint", "list", "--json", "--no-pager"], repository_path)
    if error:
        return [], error
    try:
        parsed = json.loads(output)
        return parsed if isinstance(parsed, list) else parsed.get("checkpoints", []), None
    except (json.JSONDecodeError, AttributeError):
        return [], "Entire returned checkpoint data in an unexpected format."

def collect_context(project_id,checkpoint_id,manual=None):
    m=manual or {}
    return EntireCheckpoint(checkpoint_id=checkpoint_id,project_id=project_id,timestamp=now_iso(),intent=m.get("intent","Capture and explain the latest development change."),assumptions=m.get("assumptions",[]),actions_attempted=m.get("actions_attempted",[]),failures=m.get("failures",[]),unresolved_work=m.get("unresolved_work",[]),verification_status=m.get("verification_status","not verified"),source="manual" if manual else "demo/mock")
