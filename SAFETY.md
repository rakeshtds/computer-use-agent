# Safety Guardrails — Computer-Use Agent

This agent can move the mouse and type on a real desktop, so the guardrails
are part of the product, not an afterthought. Read this before running it,
and see `agent/loop.py` for where each rule is enforced.

## Hard rules (enforced in code)

1. **Emergency stop:** pyautogui's fail-safe is always on — slam the mouse to
   the **top-left corner** of the screen to abort instantly. The loop also
   checks a `STOP` file in the working directory before every step.
2. **Step budget:** the loop stops after `MAX_STEPS` actions (default 25),
   whether or not the task looks finished.
3. **Confirm-before-submit:** any planned action whose description matches the
   sensitive list (`submit`, `send`, `pay`, `buy`, `delete`, `confirm order`,
   `post`) is **not executed automatically** — the agent pauses and asks the
   operator in the terminal. No answer within the prompt = skip.
4. **Action delay:** a fixed pause (default 0.6s) follows every action so a
   human watching can intervene.
5. **No credential handling:** the agent must never be given passwords, and
   the planner prompt forbids typing into password fields. If a login wall
   blocks the task, the agent stops and reports it.

## Operator rules

- Run it first in **mock mode** (`--planner mock`) to see the loop without
  touching the desktop.
- Watch the first real runs end-to-end; it is a supervised tool, not a
  background daemon.
- Use a dedicated desktop/VM for anything beyond trivial tasks.
- Review the JSONL action log (`actions.log`) after runs — every planned and
  executed action is recorded with its reasoning.

## Known limits

- Vision planners misread screens; coordinates can be wrong. The step budget
  and confirm list bound the damage, they do not eliminate it.
- The sensitive-action list is keyword-based: a "Place order" button phrased
  differently could slip past. Treat rule 3 as a filter, not a guarantee.
