# Computer-Use Agent

Give it a task in plain language; it screenshots the desktop, plans the next step with a vision LLM, and clicks, types and scrolls in a loop — plan → act → observe — until the task is done or its step budget runs out.

## Features

- Observe-act loop: screenshot → vision-LLM planner → one typed action (`click`, `type`, `key`, `scroll`, `wait`) → repeat
- Planner interface with two backends: a deterministic **mock planner** (safe demo, no desktop control beyond a screenshot) and a **vision LLM planner** (any OpenAI-compatible vision model)
- Safety rails first-class (see `SAFETY.md`): pyautogui fail-safe corner stop, `STOP` file check, hard step budget, and operator confirmation for sensitive actions (submit/send/pay/delete…)
- Full JSONL audit log of every planned and executed action with the planner's reasoning
- Action delay after each step so a supervising human can intervene

## Architecture

`agent/loop.py` owns the control loop and guardrails. `agent/planner.py` turns (task, screenshot, history) into the next action dict. `agent/actions.py` executes actions through pyautogui behind a small typed interface.

## Tech Stack

Python 3.11 · pyautogui · Pillow · vision LLM (OpenAI-compatible)

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...     # only needed for the vision planner
```

> Read `SAFETY.md` before the first real (non-mock) run. Start supervised.

## Usage

```bash
# Safe demo: proves the loop, touches nothing
python -m agent.loop "Demo task" --planner mock

# Real run (supervised!)
python -m agent.loop "Open the browser and check tomorrow's weather in Toronto" \
    --planner vision --max-steps 25

# Emergency stop at any time: mouse to the top-left corner, or
touch STOP
```

## Example Output

```
Step 1: {"type": "wait", "seconds": 1, "reason": "Observing the screen", "step": 1}
Step 2: {"type": "done", "reason": "Demo complete", "step": 2}
Finished: Demo complete
```

## Project Structure

```
agent/loop.py      Control loop + guardrail enforcement + action log
agent/planner.py   Mock planner and vision-LLM planner
agent/actions.py   pyautogui action execution + screenshots
SAFETY.md          Guardrails, operator rules, known limits
```

## Roadmap

- Accessibility-tree grounding as an alternative to raw pixel coordinates
- Per-application action policies (allowlist of apps the agent may drive)
- Dry-run replay: re-plan from recorded screenshots without executing

---

An original implementation built for portfolio purposes. Sample data is synthetic.
