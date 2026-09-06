from models import DevelopmentEvent
from utils.helpers import new_id,now_iso
def normalize(project,git,context,impacts):
    if not project.project_id or not context.checkpoint_id: raise ValueError("project_id and checkpoint_id are required")
    return DevelopmentEvent(event_id=new_id("evt"),project_id=project.project_id,checkpoint_id=context.checkpoint_id,timestamp=now_iso(),git_evidence=git,intent=context.intent,assumptions=context.assumptions,actions_attempted=context.actions_attempted,failures=context.failures,unresolved_work=context.unresolved_work,impacted_components=[x.changed_component for x in impacts],dependencies=sorted({d for x in impacts for d in x.dependencies}),metadata={"context_source":context.source,"impact_confidence":"estimated"})
