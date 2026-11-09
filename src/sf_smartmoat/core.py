"""SmartMoat core — score the human moat, plan to widen it.

A role is a list of tasks. Each task has `agent_exposure` in [0, 1]: how much
of it an AI agent could do today. The role's exposure is the mean exposure of
its tasks, weighted by `hours` (time spent per week) when tasks give it; the
moat is 1 - exposure.

    profiles = load_profiles("roles.json")   # {"profiles": [{"role": ..., "tasks": [...]}, ...]}
    s = score("paralegal", profiles)
    plan_for("paralegal", profiles)           # moves that name your own tasks

`MoatScore.percentile` is the moat as a whole percentage (0-99), kept under
that name for compatibility; it is not a rank against other people.
"""
from __future__ import annotations

import json
import os

from .models import MoatScore, Plan, Task

_GENERAL_MOVES = ["Double down on the high-judgment tasks agents can't own.",
                  "Move up the trust/relationship layer of your role.",
                  "Learn to orchestrate the agents doing your old tasks.",
                  "Own an outcome, not a task.",
                  "Publish your judgment so it compounds into reputation."]


def _profiles():
    """The sample profiles shown by `--demo`."""
    p = os.path.join(os.path.dirname(__file__), "..", "..", "demo", "role_task_profiles.json")
    try:
        return json.load(open(p))["data"]["profiles"]
    except Exception:
        return [{"role": "analyst", "tasks": [{"task": "t1", "agent_exposure": .8, "human_moat": .2}]}]


def _validate(profiles) -> list[dict]:
    if isinstance(profiles, dict):
        profiles = profiles.get("profiles") or profiles.get("data", {}).get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("expected a non-empty list of profiles, or {\"profiles\": [...]}")
    seen = set()
    for p in profiles:
        role = p.get("role") if isinstance(p, dict) else None
        if not isinstance(role, str) or not role:
            raise ValueError("every profile needs a 'role' name")
        if role in seen:
            raise ValueError(f"role {role!r} appears twice")
        seen.add(role)
        tasks = p.get("tasks")
        if not isinstance(tasks, list) or not tasks:
            raise ValueError(f"role {role!r}: needs at least one task")
        for t in tasks:
            e = t.get("agent_exposure") if isinstance(t, dict) else None
            if not isinstance(e, (int, float)) or not 0 <= e <= 1:
                raise ValueError(f"role {role!r}: each task needs agent_exposure between 0 and 1")
            h = t.get("hours", 1)
            if not isinstance(h, (int, float)) or h < 0:
                raise ValueError(f"role {role!r}: hours must be a non-negative number")
    return profiles


def load_profiles(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return _validate(json.load(fh))


def _pick(role, profiles):
    if profiles is None:
        profs = _profiles()
        # The demo falls back to its first sample profile for an unknown role.
        return next((p for p in profs if p["role"] == role), profs[0])
    profs = _validate(profiles)
    if role is None:
        return profs[0]
    for p in profs:
        if p["role"] == role:
            return p
    raise ValueError(f"no profile for role {role!r}; have: {', '.join(p['role'] for p in profs)}")


def _exposure(tasks) -> float:
    weights = [t.get("hours", 1) for t in tasks]
    total = sum(weights)
    if total == 0:
        return round(sum(t["agent_exposure"] for t in tasks) / len(tasks), 2)
    return round(sum(t["agent_exposure"] * w for t, w in zip(tasks, weights)) / total, 2)


def score(role: str = None, profiles=None) -> MoatScore:
    """Score one role. With `profiles`, an unknown role is an error."""
    prof = _pick(role, profiles)
    exp = _exposure(prof["tasks"])
    moat = round(1 - exp, 2)
    return MoatScore(exp, moat, min(99, int(moat * 100)))


def tasks(role: str = None, profiles=None) -> list[Task]:
    """The role's tasks, most exposed first."""
    prof = _pick(role, profiles)
    out = [Task(t.get("task", f"task {i + 1}"), t["agent_exposure"],
                round(t.get("human_moat", 1 - t["agent_exposure"]), 2))
           for i, t in enumerate(prof["tasks"])]
    return sorted(out, key=lambda t: -t.agent_exposure)


def plan(s: MoatScore) -> Plan:
    """General moves; fewer when the moat is already wide (never fewer than three)."""
    return Plan(_GENERAL_MOVES[: max(3, 5 - int(s.moat * 3))])


def plan_for(role: str = None, profiles=None) -> Plan:
    """Moves that name the role's own tasks, then the general moves."""
    ts = tasks(role, profiles)
    moves = []
    exposed = [t for t in ts if t.agent_exposure >= 0.6]
    defended = [t for t in sorted(ts, key=lambda t: -t.human_moat) if t.human_moat >= 0.6]
    if exposed:
        moves.append("Hand off or redesign first: " + ", ".join(t.name for t in exposed[:3]) + ".")
    if defended:
        moves.append("Invest in what agents can't do yet: " + ", ".join(t.name for t in defended[:3]) + ".")
    return Plan(moves + plan(score(role, profiles)).moves)
