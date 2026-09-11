"""Walk jobs/ and write results.csv with one row per trial.

Reads each trial's result.json. Harbor exits 0 even when trials fail, so the
reward in result.json is the only reliable pass/fail signal.
"""

import csv
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JOBS = ROOT / "jobs"
OUTPUT = ROOT / "results.csv"

COLUMNS = [
    "task",
    "agent",
    "model",
    "trial",
    "reward",
    "agent_setup_s",
    "agent_execution_s",
    "verifier_s",
    "input_tokens",
    "output_tokens",
    "cost_usd",
    "transcript_path",
]


def seconds(timing):
    if not timing or not timing.get("started_at") or not timing.get("finished_at"):
        return ""
    started = datetime.fromisoformat(timing["started_at"].replace("Z", "+00:00"))
    finished = datetime.fromisoformat(timing["finished_at"].replace("Z", "+00:00"))
    return round((finished - started).total_seconds(), 1)


def transcript(trial_dir):
    agent_dir = trial_dir / "agent"
    candidates = [agent_dir / "trajectory.json"]
    candidates += sorted((agent_dir / "sessions").rglob("*.jsonl"))
    candidates += [agent_dir / "oracle.txt"]
    for path in candidates:
        if path.is_file():
            return str(path.relative_to(ROOT))
    return ""


def blank_if_none(value):
    return "" if value is None else value


def row(result_path):
    result = json.loads(result_path.read_text())
    agent_config = result.get("config", {}).get("agent", {})
    agent_result = result.get("agent_result") or {}
    rewards = (result.get("verifier_result") or {}).get("rewards") or {}
    # A trial that crashed or timed out before verification has no reward; count it as a fail.
    reward = rewards.get("reward", 0.0)
    return {
        "task": result.get("task_name", ""),
        "agent": agent_config.get("name", ""),
        "model": agent_config.get("model_name") or "",
        "trial": result.get("trial_name", ""),
        "reward": reward,
        "agent_setup_s": seconds(result.get("agent_setup")),
        "agent_execution_s": seconds(result.get("agent_execution")),
        "verifier_s": seconds(result.get("verifier")),
        "input_tokens": blank_if_none(agent_result.get("n_input_tokens")),
        "output_tokens": blank_if_none(agent_result.get("n_output_tokens")),
        "cost_usd": blank_if_none(agent_result.get("cost_usd")),
        "transcript_path": transcript(result_path.parent),
    }


def main():
    # Trial dirs sit one level below each job dir; the job-level result.json is a summary.
    rows = [row(path) for path in sorted(JOBS.glob("*/*/result.json"))]
    with OUTPUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} trial(s) to {OUTPUT.name}")


if __name__ == "__main__":
    main()
