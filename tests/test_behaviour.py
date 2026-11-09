"""Behaviour of core.score and core.plan."""
import os
import types

from sf_smartmoat import core
from sf_smartmoat.models import MoatScore


def test_score_is_the_mean_exposure_and_its_complement():
    prof = core._profiles()[0]
    exp = round(sum(t["agent_exposure"] for t in prof["tasks"]) / len(prof["tasks"]), 2)
    s = core.score(prof["role"])
    assert s.exposure == exp and s.moat == round(1 - exp, 2)
    assert s.percentile == min(99, int(s.moat * 100))


def test_unknown_role_falls_back_to_the_first_profile():
    assert core.score("no-such-role") == core.score(core._profiles()[0]["role"])


def test_without_the_demo_file_a_built_in_profile_is_used(monkeypatch):
    fake_path = types.SimpleNamespace(join=lambda *a: "/nonexistent/role_task_profiles.json", dirname=os.path.dirname)
    monkeypatch.setattr(core, "os", types.SimpleNamespace(path=fake_path))
    s = core.score()
    assert (s.exposure, s.moat, s.percentile) == (0.8, 0.2, 20)


def test_a_wider_moat_gets_fewer_moves_but_never_fewer_than_three():
    n = lambda moat: len(core.plan(MoatScore(round(1 - moat, 2), moat, 0)).moves)
    assert n(0.0) == 5 and n(0.4) == 4 and n(0.7) == 3 and n(1.0) == 3


def test_moves_come_in_a_fixed_order():
    moves = core.plan(MoatScore(1.0, 0.0, 0)).moves
    assert moves[0].startswith("Double down") and moves[-1].startswith("Publish")


import json

import pytest

PROFILES = {"profiles": [
    {"role": "paralegal", "tasks": [
        {"task": "doc review", "agent_exposure": 0.9, "hours": 30},
        {"task": "client counsel", "agent_exposure": 0.1, "hours": 10}]},
    {"role": "nurse", "tasks": [{"task": "triage", "agent_exposure": 0.2}]}]}


def test_your_own_profiles_are_scored_and_weighted_by_hours():
    s = core.score("paralegal", PROFILES)
    assert s.exposure == 0.7 and s.moat == 0.3          # (0.9*30 + 0.1*10) / 40
    assert core.score("nurse", PROFILES).moat == 0.8


def test_an_unknown_role_in_your_profiles_is_an_error():
    with pytest.raises(ValueError, match="have: paralegal, nurse"):
        core.score("pilot", PROFILES)


@pytest.mark.parametrize("bad", [
    [], {"profiles": [{"role": "x", "tasks": []}]},
    {"profiles": [{"role": "x", "tasks": [{"agent_exposure": 1.5}]}]},
    {"profiles": [{"role": "x", "tasks": [{"agent_exposure": 0.5, "hours": -1}]}]},
    {"profiles": [{"role": "x", "tasks": [{"agent_exposure": 0.5}]}, {"role": "x", "tasks": [{"agent_exposure": 0.5}]}]},
])
def test_profiles_are_validated(bad):
    with pytest.raises(ValueError):
        core.score(None, bad)


def test_plan_for_names_your_tasks():
    moves = core.plan_for("paralegal", PROFILES).moves
    assert moves[0] == "Hand off or redesign first: doc review."
    assert moves[1] == "Invest in what agents can't do yet: client counsel."
    assert moves[2].startswith("Double down")


def test_cli_scores_a_file(tmp_path, capsys):
    from sf_smartmoat import cli
    f = tmp_path / "roles.json"
    f.write_text(json.dumps(PROFILES))
    assert cli.main([str(f), "--role", "paralegal", "--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["score"]["moat"] == 0.3 and out["tasks"][0]["name"] == "doc review"
