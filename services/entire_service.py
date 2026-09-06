from models import EntireCheckpoint
from utils.helpers import now_iso
def collect_context(project_id,checkpoint_id,manual=None):
    m=manual or {}; return EntireCheckpoint(checkpoint_id=checkpoint_id,project_id=project_id,timestamp=now_iso(),intent=m.get("intent","Capture and explain the latest development change."),assumptions=m.get("assumptions",[]),actions_attempted=m.get("actions_attempted",[]),failures=m.get("failures",[]),unresolved_work=m.get("unresolved_work",[]),verification_status=m.get("verification_status","not verified"),source="manual" if manual else "demo/mock")
