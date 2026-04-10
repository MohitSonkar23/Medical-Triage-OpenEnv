from environment import MedicalTriageEnv
from models.actions import AgentAction, TriageAction
from models.patient import UrgencyLevel

def grade_triage_priority(env: MedicalTriageEnv, action: AgentAction) -> float:
    """Exact match grader for Task 1"""
    if not action.triage:
        return 0.0
    
    patient = list(env.patients.values())[0]
    gold_standard = patient.true_urgency
    predicted = action.triage.urgency
    
    return 1.0 if predicted == gold_standard else 0.0

def run_triage_baseline(env: MedicalTriageEnv) -> float:
    """Random baseline for Task 1"""
    action = AgentAction(
        task_type="triage_priority",
        triage=TriageAction(urgency=UrgencyLevel.YELLOW)  # Always yellow
    )
    _, reward, _, _ = env.step(action)
    return reward