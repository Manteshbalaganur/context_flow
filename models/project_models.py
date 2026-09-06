from typing import Optional
from pydantic import BaseModel
class Project(BaseModel):
    project_id: str
    project_name: str
    description: str = ""
    repository_path: Optional[str] = None
    repository_url: Optional[str] = None
    default_branch: str = "main"
    created_at: str
    last_checkin_at: Optional[str] = None
