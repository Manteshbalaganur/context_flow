from pathlib import Path
import re
from models import GraphImpact
from utils.helpers import new_id
def collect_impact(project,checkpoint_id,changes):
    results=[]; root=Path(project.repository_path) if project.repository_path else None
    for change in changes:
        path=change["file_path"]; deps=[]
        if root and path.endswith(".py") and (root/path).exists():
            try: deps=re.findall(r"^(?:from|import)\s+([\w.]+)",(root/path).read_text(encoding="utf-8",errors="ignore"),re.M)[:8]
            except OSError: pass
        results.append(GraphImpact(impact_id=new_id("impact"),project_id=project.project_id,checkpoint_id=checkpoint_id,changed_component=path,dependencies=deps,impacted_modules=deps,verification_status="estimated"))
    return results
