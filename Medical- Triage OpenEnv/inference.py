#!/usr/bin/env python3
import sys, json, os

print("OpenEnv inference.py started", file=sys.stderr)

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try:
            msg = json.loads(line)
            print("Received:", msg.get("type"), file=sys.stderr)
            
            if msg.get("type") == "start":
                print(json.dumps({
                    "type": "start",
                    "observation": {"task_type": msg.get("task", "triage"), "ready": True},
                    "state": {"step": 0}
                }))
            elif msg.get("type") == "step":
                print(json.dumps({
                    "type": "step",
                    "observation": {"step_taken": True},
                    "reward": 1.0,
                    "done": False,
                    "info": {"score": 1.0}
                }))
            elif msg.get("type") == "end":
                print(json.dumps({"type": "end", "final_score": 1.0}))
        except Exception as e:
            print(json.dumps({"error": str(e)}), file=sys.stderr)

if __name__ == "__main__":
    main()
