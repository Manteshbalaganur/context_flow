from typing import Any, Dict, List
from pydantic import BaseModel, Field
class CodeChange(BaseModel):
    change_id: str; project_id: str; checkpoint_id: str; timestamp: str; file_path: str; change_type: str; insertions: int = 0; deletions: int = 0; diff_summary: str = ""
class EntireCheckpoint(BaseModel):
    checkpoint_id: str; project_id: str; timestamp: str; intent: str = ""; assumptions: List[str] = Field(default_factory=list); actions_attempted: List[str] = Field(default_factory=list); failures: List[str] = Field(default_factory=list); unresolved_work: List[str] = Field(default_factory=list); verification_status: str = "unknown"; source: str = "manual"
class GraphImpact(BaseModel):
    impact_id: str; project_id: str; checkpoint_id: str; changed_component: str; related_components: List[str] = Field(default_factory=list); dependencies: List[str] = Field(default_factory=list); impacted_modules: List[str] = Field(default_factory=list); verification_status: str = "estimated"
class DevelopmentEvent(BaseModel):
    event_id: str; project_id: str; checkpoint_id: str; timestamp: str; git_evidence: Dict[str, Any] = Field(default_factory=dict); intent: str = ""; assumptions: List[str] = Field(default_factory=list); actions_attempted: List[str] = Field(default_factory=list); failures: List[str] = Field(default_factory=list); unresolved_work: List[str] = Field(default_factory=list); impacted_components: List[str] = Field(default_factory=list); dependencies: List[str] = Field(default_factory=list); metadata: Dict[str, Any] = Field(default_factory=dict)
class ProjectIntelligence(BaseModel):
    analysis_id: str; project_id: str; checkpoint_id: str; timestamp: str; completion_score: int; risk_score: int; risk_level: str; unfinished_requirements: List[str] = Field(default_factory=list); unresolved_risks: List[str] = Field(default_factory=list); release_readiness: str; recommended_next_step: str; intent_drift_status: str; intent_drift_reason: str; context_debt_score: int; context_debt_level: str; context_debt_reason: str; blast_radius: str; blast_radius_reason: str; smart_checkpoint_gaps: List[str] = Field(default_factory=list); handoff_readiness: str; handoff_readiness_reason: str; evidence: Dict[str, Any] = Field(default_factory=dict)
class ProjectHandoff(BaseModel):
    project_id: str; generated_at: str; markdown: str
