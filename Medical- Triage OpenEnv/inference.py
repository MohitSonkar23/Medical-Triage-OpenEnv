"""
Exact OpenEnv [START]/[STEP]/[END] format - SELF-CONTAINED
"""
import json
import sys
from typing import Dict, Any
from environment import MedicalTriageEnv

# Inline graders - no external dependencies
def grade_triage_priority(env: MedicalTriageEnv, action: Dict[str, Any]) -> float:
    """Task 1 Grader: Exact match"""
    predicted = action.get("triage", {}).get("urgency", "GREEN")
    patient = list(env.patients.values())[0]
    gold_standard = patient.true_urgency
    return 1.0 if predicted == gold_standard.value else 0.0

def grade_er_queue(env: MedicalTriageEnv, action: Dict[str, Any]) -> float:
    """Task 2 Grader: Queue accuracy"""
    predicted_order = action.get("queue", {}).get("order", [])
    true_order = sorted(env.patients.keys(), 
                       key=lambda pid: list(env.patients.values())[0].true_urgency, reverse=True)
    correct = sum(1 for i, pid in enumerate(predicted_order) if pid == true_order[i])
    return correct / len(predicted_order) if predicted_order else 0.0

def grade_treatment_planning(env: MedicalTriageEnv, action: Dict[str, Any]) -> float:
    """Task 3 Grader: Clinical compliance"""
    predicted_dx = action.get("treatment", {}).get("diagnosis", "none")
    patient = list(env.patients.values())[0]
    
    # Simple diagnosis logic
    true_dx = "sepsis" if patient.vitals.oxygen_saturation < 92 else "none"
    return 1.0 if predicted_dx == true_dx else 0.3

def main():
    env = None
    for line in sys.stdin:
        try:
            message = json.loads(line.strip())
        except:
            continue
            
        if message.get("type") == "start":
            task_type = message.get("task", "triage_priority")
            env = MedicalTriageEnv(task_type=task_type)
            obs = env.reset()
            
            print(json.dumps({
                "type": "start",
                "observation": obs["observation"],
                "state": env.get_state()
            }, default=str))
            
        elif message.get("type") == "step" and env:
            action_dict = message.get("action", {})
            
            # Handle both dict and simple action
            result = env.step(action_dict)
            observation, reward, done, info = result[0], result[1], result[2], result[3]
            
            # Grade action
            if env.task_type == "triage_priority":
                score = grade_triage_priority(env, action_dict)
            elif env.task_type == "er_queue_management":
                score = grade_er_queue(env, action_dict)
            else:
                score = grade_treatment_planning(env, action_dict)
            
            print(json.dumps({
                "type": "step",
                "observation": observation["observation"],
                "reward": float(reward),
                "done": done,
                "info": {
                    **(info or {}),
                    "grader_score": float(score),
                    "task_type": env.task_type
                }
            }, default=str))
            
        elif message.get("type") == "end":
            print(json.dumps({
                "type": "end", 
                "final_score": float(reward) if 'reward' in locals() else 0.0
            }))

if __name__ == "__main__":
    # Test mode
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("🧪 Testing inference.py...")
        env = MedicalTriageEnv("triage_priority")
        obs = env.reset()
        print("✅ Reset OK:", obs["observation"]["patient"]["name"])
        
        action = {"triage": {"urgency": "RED"}}
        result = env.step(action)
        print("✅ Step OK:", result[1])
        print("✅ inference.py READY!")
    else:
        main()