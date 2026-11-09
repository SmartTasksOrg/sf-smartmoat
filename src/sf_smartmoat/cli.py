"""SmartMoat CLI.

    sf-smartmoat --demo
    sf-smartmoat PROFILES.json [--role ROLE] [--json]

PROFILES.json: {"profiles": [{"role": "...", "tasks": [{"task": "...",
"agent_exposure": 0.8, "hours": 10}, ...]}]}. `hours` is optional.
"""
import argparse
import json
import os
import sys
from dataclasses import asdict

from . import core
from ._version import __version__

BANNER = f"\n🦔 SmartMoat {__version__}  ·  IAIso §6 · Workforce"
FOOTER = "\nBacked by IAIso §6 · Workforce · part of the Smart* family · https://smarttasks.cloud\n"


def _demo_dir():
    return os.path.join(os.path.dirname(__file__), "..", "..", "demo")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--version" in argv:
        print(f"SmartMoat {__version__}"); return 0
    if not argv or "--demo" in argv:
        print(BANNER); print(core_demo()); print(FOOTER); return 0

    ap = argparse.ArgumentParser(prog="sf-smartmoat")
    ap.add_argument("profiles", help="JSON file of role profiles")
    ap.add_argument("--role", default=None, help="role to score (default: the first)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    profiles = core.load_profiles(a.profiles)
    s = core.score(a.role, profiles)
    pl = core.plan_for(a.role, profiles)
    if a.json:
        print(json.dumps({"score": asdict(s), "tasks": [asdict(t) for t in core.tasks(a.role, profiles)],
                          "plan": pl.moves}, indent=2, ensure_ascii=False))
    else:
        print(f"human moat {s.moat:.0%} (agent exposure {s.exposure:.0%})")
        for i, m in enumerate(pl.moves, 1):
            print(f"  {i}. {m}")
    return 0


def core_demo() -> str:
    return _DEMO()


def _DEMO():
    s = core.score()
    pl = core.plan(s)
    out = [f"human moat: {s.moat}  (agent exposure {s.exposure}; sample profile)",
           "plan to widen it:"]
    for i, m in enumerate(pl.moves, 1):
        out.append(f"  {i}. {m}")
    return "\n".join(out)

if __name__ == "__main__":
    sys.exit(main())
