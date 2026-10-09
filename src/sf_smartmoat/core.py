"""SmartMoat core — score the human moat, plan to widen it."""
import json, os
from .models import Task, MoatScore, Plan

def _profiles():
    p = os.path.join(os.path.dirname(__file__), "..", "..", "demo", "role_task_profiles.json")
    try:
        return json.load(open(p))["data"]["profiles"]
    except Exception:
        return [{"role": "analyst", "tasks": [{"task": "t1", "agent_exposure": .8, "human_moat": .2}]}]

def score(role: str = None) -> MoatScore:
    profs = _profiles()
    prof = next((p for p in profs if p["role"] == role), profs[0])
    exp = round(sum(t["agent_exposure"] for t in prof["tasks"]) / len(prof["tasks"]), 2)
    moat = round(1 - exp, 2)
    pct = min(99, int(moat * 100))
    return MoatScore(exp, moat, pct)

def plan(s: MoatScore) -> Plan:
    moves = ["Double down on the high-judgment tasks agents can't own.",
             "Move up the trust/relationship layer of your role.",
             "Learn to orchestrate the agents doing your old tasks.",
             "Own an outcome, not a task.",
             "Publish your judgment so it compounds into reputation."]
    return Plan(moves[: max(3, 5 - int(s.moat * 3))])
