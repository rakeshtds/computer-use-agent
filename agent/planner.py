"""Planner interface: (task, screenshot, history) -> next action dict.

Two implementations:
- MockPlanner: deterministic script-free planner for demos/tests. It takes a
  screenshot, then finishes — enough to prove the loop end to end.
- VisionLLMPlanner: sends the screenshot to a vision-capable LLM and parses a
  JSON action. Any OpenAI-compatible vision endpoint works.
"""
from __future__ import annotations

import base64
import json
import os

PLANNER_PROMPT = """You control a desktop to complete this task: {task}
You are shown a screenshot. Reply with ONLY one JSON action:
{{"type": "click"|"double_click"|"type"|"key"|"scroll"|"wait"|"done",
  "x": int, "y": int, "text": "...", "key": "enter", "amount": -5,
  "reason": "one short sentence"}}
Use "done" when the task is complete. Never type passwords or into password
fields; if a login blocks you, reply {{"type": "done", "reason": "blocked by login"}}.
Previous actions: {history}
"""


class MockPlanner:
    """No-API demo planner: observes once, then declares the demo done."""

    def __init__(self):
        self.calls = 0

    def next_action(self, task: str, screenshot_path: str, history: list[dict]) -> dict:
        self.calls += 1
        if self.calls == 1:
            return {"type": "wait", "seconds": 1, "reason": "Mock planner: observing the screen"}
        return {"type": "done", "reason": "Mock planner: demo complete (use the vision planner for real tasks)"}


class VisionLLMPlanner:
    def __init__(self, model: str | None = None):
        self.model = model or os.environ.get("CUA_MODEL", "gpt-4o")

    def next_action(self, task: str, screenshot_path: str, history: list[dict]) -> dict:
        from openai import OpenAI

        with open(screenshot_path, "rb") as fh:
            image_b64 = base64.b64encode(fh.read()).decode()
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        history_text = "; ".join(f"{a.get('type')}: {a.get('reason', '')}" for a in history) or "(none)"
        response = client.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": PLANNER_PROMPT.format(task=task, history=history_text)},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
                ],
            }],
            temperature=0,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(raw)
