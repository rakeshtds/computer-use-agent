"""The plan -> act -> observe loop, with the SAFETY.md guardrails enforced.

Usage:
    python -m agent.loop "Open the browser and search for the weather" \
        [--planner mock|vision] [--max-steps 25]

Guardrails: pyautogui fail-safe (mouse to top-left corner), a STOP file check
before every step, a hard step budget, and operator confirmation for any
sensitive action (submit/send/pay/delete/...). Every action is logged to
actions.log as JSONL.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import actions  # noqa: E402
from agent.planner import MockPlanner, VisionLLMPlanner  # noqa: E402

SENSITIVE_WORDS = ("submit", "send", "pay", "buy", "delete", "confirm order", "post", "purchase")
STOP_FILE = "STOP"
LOG_FILE = "actions.log"


def is_sensitive(action: dict) -> bool:
    text = f"{action.get('type', '')} {action.get('text', '')} {action.get('reason', '')}".lower()
    return any(word in text for word in SENSITIVE_WORDS)


def confirm(action: dict) -> bool:
    """Ask the operator before a sensitive action. Default is NO on empty input."""
    print(f"\nSensitive action proposed: {json.dumps(action)}")
    answer = input("Execute it? [y/N] ").strip().lower()
    return answer == "y"


def log_action(entry: dict) -> None:
    with open(LOG_FILE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def run(task: str, planner, max_steps: int = 25) -> int:
    history: list[dict] = []
    for step in range(1, max_steps + 1):
        if os.path.exists(STOP_FILE):
            print(f"STOP file found before step {step}; aborting.")
            return 2
        shot = actions.screenshot(f"step_{step:02d}.png")
        action = planner.next_action(task, shot, history)
        action["step"] = step
        print(f"Step {step}: {json.dumps(action)}")
        log_action(action)
        if action.get("type") == "done":
            print(f"Finished: {action.get('reason', '')}")
            return 0
        if is_sensitive(action) and not confirm(action):
            print("Operator declined; skipping action.")
            history.append({**action, "skipped": True})
            continue
        try:
            actions.execute(action)
        except Exception as exc:  # e.g. pyautogui FailSafeException on emergency stop
            print(f"Action failed / emergency stop at step {step}: {exc}")
            return 3
        history.append(action)
    print(f"Step budget ({max_steps}) exhausted; stopping.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Computer-use agent")
    parser.add_argument("task")
    parser.add_argument("--planner", choices=["mock", "vision"], default="mock")
    parser.add_argument("--max-steps", type=int, default=25)
    args = parser.parse_args()
    planner = MockPlanner() if args.planner == "mock" else VisionLLMPlanner()
    return run(args.task, planner, max_steps=args.max_steps)


if __name__ == "__main__":
    raise SystemExit(main())
