from models import ProjectIntelligence
from utils.helpers import new_id,now_iso
def _level(value): return "Low" if value<35 else "Medium" if value<65 else "High"
def analyze(event):
    changed=event.git_evidence.get("changed_files",[]); unresolved=event.unresolved_work; failures=event.failures
    debt=min(100,int(not event.intent)*25+int(not event.assumptions)*10+int(not event.actions_attempted)*10+len(unresolved)*12+len(failures)*10+(15 if len(changed)>8 else 0)+15)
    risk=min(100,len(unresolved)*18+len(failures)*15+len(event.impacted_components)*5+(12 if event.git_evidence.get("warnings") else 0))
    words={w.lower() for w in event.intent.split() if len(w)>3}; unrelated=[c["file_path"] for c in changed if words and not any(w in c["file_path"].lower() for w in words)]
    drift="Significant Drift" if len(unrelated)>=5 else "Minor Drift" if len(unrelated)>=2 else "Aligned"
    drift_reason="Changed paths broadly match the stated intent." if drift=="Aligned" else f"{len(unrelated)} changed path(s) are not clearly connected to the intent: {', '.join(unrelated[:3])}."
    completion=max(5,min(100,82-len(unresolved)*12-len(failures)*7-(10 if not event.git_evidence.get("available") else 0)))
    blast="High" if len(event.impacted_components)>=8 or len(event.dependencies)>=10 else "Medium" if len(event.impacted_components)>=3 else "Low"
    gaps=[]
    if len(changed)>5 and not event.assumptions: gaps.append("Large change set has no documented assumptions.")
    if unresolved and not event.actions_attempted: gaps.append("Unresolved work has no recorded next-action evidence.")
    if event.git_evidence.get("available") and not changed: gaps.append("Checkpoint has no uncommitted Git evidence; commit-level verification may be needed.")
    readiness="Ready" if risk<30 and debt<35 and not unresolved else "Needs context" if debt>=45 else "Needs resolution"
    return ProjectIntelligence(analysis_id=new_id("analysis"),project_id=event.project_id,checkpoint_id=event.checkpoint_id,timestamp=now_iso(),completion_score=completion,risk_score=risk,risk_level=_level(risk),unfinished_requirements=unresolved,unresolved_risks=failures+unresolved,release_readiness="Ready" if completion>=80 and risk<30 else "Not ready",recommended_next_step="Verify the change and prepare release notes." if readiness=="Ready" else "Document missing context and resolve the highest-priority unresolved item.",intent_drift_status=drift,intent_drift_reason=drift_reason,context_debt_score=debt,context_debt_level=_level(debt),context_debt_reason=f"Debt is driven by {len(unresolved)} unresolved item(s), {len(failures)} failure(s), and context completeness.",blast_radius=blast,blast_radius_reason=f"Estimate based on {len(event.impacted_components)} changed component(s) and {len(event.dependencies)} discovered dependency reference(s).",smart_checkpoint_gaps=gaps,handoff_readiness=readiness,handoff_readiness_reason="Handoff readiness reflects risk, unresolved work, and context debt.",evidence={"changed_files":[x["file_path"] for x in changed],"failures":failures,"unresolved_work":unresolved,"dependencies":event.dependencies})
