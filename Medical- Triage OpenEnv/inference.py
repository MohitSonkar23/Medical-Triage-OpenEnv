#!/usr/bin/env python3
import sys, json

def main():
    for line in sys.stdin:
        try:
            msg = json.loads(line)
            if msg.get("type") == "start":
                print(json.dumps({
                    "type": "start",
                    "observation": {"ready": True, "task_type": msg.get("task", "default")},
                    "state": {}
                }))
            elif msg.get("type") == "step":
                print(json.dumps({
                    "type": "step",
                    "observation": {"step": 1},
                    "reward": 1.0,
                    "done": False,
                    "info": {}
                }))
            else:
                print(json.dumps({"type": msg.get("type", "unknown")}))
        except:
            print(json.dumps({"error": "parse fail"}))

if __name__ == "__main__":
    main()
