from services import project_service,git_service,entire_service,graph_service,event_normalizer,analysis_service,databricks_service
from utils.helpers import new_id
def check_in_project(project_id,manual_context=None):
    project=project_service.get_project(project_id)
    if not project: raise ValueError("Select a valid project before CheckIN.")
    checkpoint_id=new_id("cp"); git,changes=git_service.collect_git(project,checkpoint_id); context=entire_service.collect_context(project_id,checkpoint_id,manual_context); impacts=graph_service.collect_impact(project,checkpoint_id,changes); event=event_normalizer.normalize(project,git,context,impacts); intelligence=analysis_service.analyze(event)
    databricks_service.store_event(event.model_dump(),context.model_dump(),changes,[x.model_dump() for x in impacts]); databricks_service.store_analysis(intelligence.model_dump()); project_service.mark_checked_in(project)
    return {"project":project,"event":event,"context":context,"impacts":impacts,"intelligence":intelligence}
