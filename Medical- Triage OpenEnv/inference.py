#!/usr/bin/env python3
"""
OpenEnv EXACT format - Phase 1 compliant
"""
import sys
import json
from typing import Dict, Any, Tuple

# Self-contained MedicalTriageEnv
class MedicalTriageEnv:
    def __init__(self, task_type: str = "triage_priority"):
        self.task_type = task_type
        self.reset()
    
    def reset(self) -> Dict[str, Any]:
        self.step_count = 0
        obs = {
            "task_type": self.task_type,
            "patient": {
                "id": "p1",
                "name": "John Doe",
                "age": 65,
                "symptoms": [{"name": "chest_pain", "severity": 7}],
                "vitals": {
                    "heart_rate": 110,
                    "blood_pressure": "140/90", 
                    "respiratory_rate": 24,
                    "oxygen_saturation": 92.5,
                    "temperature": 38.5
                }
            }
        }
        return {"observation": obs, "state": {"step": 0}}
    
    def step(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float, bool, Dict]:
        self.step_count += 1
        reward = 1.0 if self._is_valid_action(action) else 0.0
        done = self.step_count >= 20
        
        obs = {"status": f"step {self.step_count}", "action_received": action}
        return (
            {"observation": obs, "reward": reward, "done": done, "info": {}}, 
            reward, 
            done, 
            {}
        )
    
    def _is_valid_action(self, action: Dict) -> bool:
        return isinstance(action, dict) and len(action) > 0

def main():
    env = None
    for line in sys.stdin:
        try:
            msg = json.loads(line.strip())
            
            if msg.get("type") == "start":
                task = msg.get("task", "triage_priority")
                env = MedicalTriageEnv(task)
                obs = env.reset()
                print(json.dumps({
                    "type": "start",
                    "observation": obs["observation"],
                    "state": obs["state"]
                }))
                
            elif msg.get("type") == "step" and env:
                action = msg.get("action", {})
                step_result = env.step(action)
                obs, reward, done, info = step_result[0]["observation"], step_result[1], step_result[2], step_result[3]
                
                print(json.dumps({
                    "type": "step",
                    "observation": obs,
                    "reward": float(reward),
                    "done": bool(done),
                    "info": dict(info or {})
                }))
                
            elif msg.get("type") == "end":
                print(json.dumps({"type": "end", "final_score": 0.0}))
                
        except json.JSONDecodeError:
            continue
        except Exception as e:
            print(json.dumps({"type": "error", "message": str(e)}))

if __name__ == "__main__":
    main()
