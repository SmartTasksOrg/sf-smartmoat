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
