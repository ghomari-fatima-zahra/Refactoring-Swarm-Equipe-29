import json
import os
from datetime import datetime
from enum import Enum

class ActionType(str, Enum):
    ANALYSIS = "ANALYSIS"
    GENERATION = "GENERATION"
    DEBUG = "DEBUG"
    FIX = "FIX"

def log_experiment(agent_name, model_used, action, details, status="SUCCESS"):
    if "input_prompt" not in details or "output_response" not in details:
        raise ValueError("Missing prompt/response in log")

    entry = {
        "timestamp": datetime.now().isoformat(),
        "agent_name": agent_name,
        "model_used": model_used,
        "action": action.value,
        "details": details,
        "status": status
    }

    os.makedirs("logs", exist_ok=True)
    with open("logs/experiment_data.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")