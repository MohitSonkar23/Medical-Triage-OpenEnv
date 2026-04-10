from pydantic import BaseModel
from typing import List, Optional
from .patient import UrgencyLevel, Diagnosis, Treatment

class TriageAction(BaseModel):
    urgency: UrgencyLevel

class QueueAction(BaseModel):
    order: List[str]  # patient_ids in priority order

class TreatmentAction(BaseModel):
    diagnosis: Diagnosis
    treatment: Treatment

class AgentAction(BaseModel):
    task_type: str
    triage: Optional[TriageAction] = None
    queue: Optional[QueueAction] = None
    treatment: Optional[TreatmentAction] = None
    
    class Config:
        extra = "forbid"