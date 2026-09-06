from models import Project
from services import databricks_service as store
from utils.helpers import new_id, now_iso
def list_projects(): return [Project(**x) for x in store.query_projects()]
def get_project(project_id): return next((p for p in list_projects() if p.project_id==project_id),None)
def create_project(name, description="", repository_path=None, repository_url=None, default_branch="main"):
    p=Project(project_id=new_id("proj"),project_name=name,description=description,repository_path=repository_path or None,repository_url=repository_url or None,default_branch=default_branch,created_at=now_iso()); store.store_project(p.model_dump()); return p
def update_project(project): store.store_project(project.model_dump())
def mark_checked_in(project): project.last_checkin_at=now_iso(); update_project(project); return project
