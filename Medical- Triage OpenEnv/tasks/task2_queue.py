from environment import MedicalTriageEnv
from models.actions import AgentAction, QueueAction

def grade_er_queue(env: MedicalTriageEnv, action: AgentAction) -> float:
    """Weighted accuracy by deterioration rate"""
    if not action.queue:
        return 0.0
    
    # Gold standard: sort by true_urgency (RED > YELLOW > GREEN)
    true_order = sorted(env.patients.keys(), 
                       key=lambda pid: env.patients[pid].true_urgency, reverse=True)
    
    predicted_order = action.queue.order
    correct_positions = sum(1 for i, pid in enumerate(predicted_order) 
                           if pid == true_order[i])
    
    # Weight by position importance (top of queue matters more)
    weights = [0.4, 0.25, 0.15, 0.1, 0.1]
    weighted_score = sum(weights[i] for i in range(5) 
                        if i < len(predicted_order) and predicted_order[i] == true_order[i])
    
    return weighted_score

def run_queue_baseline(env: MedicalTriageEnv) -> float:
    """Random baseline for Task 2"""
    patient_ids = list(env.patients.keys())
    random.shuffle(patient_ids)
    action = AgentAction(
        task_type="er_queue_management",
        queue=QueueAction(order=patient_ids)
    )
    _, reward, _, _ = env.step(action)
    return reward