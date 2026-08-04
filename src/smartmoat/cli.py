"""SmartMoat CLI — run `smartmoat --demo`."""
import os, sys, json
from . import core
from ._version import __version__


def _demo_dir():
    return os.path.join(os.path.dirname(__file__), "..", "..", "demo")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--version" in argv:
        print(f"SmartMoat {__version__}"); return 0
    demo = "--demo" in argv or not argv
    print(f"\n🦔 SmartMoat {__version__}  ·  IAIso §6 · Workforce")
    result = core_demo()
    print(result)
    print(f"\nBacked by IAIso §6 · Workforce · part of the Smart* family · https://smarttasks.cloud\n")
    return 0


def core_demo() -> str:
    return _DEMO()


def _DEMO():
    s = core.score()
    pl = core.plan(s)
    out = [f"human moat: {s.moat}  (agent exposure {s.exposure}, ~{s.percentile}th percentile)",
           "plan to widen it:"]
    for i, m in enumerate(pl.moves, 1):
        out.append(f"  {i}. {m}")
    return "\n".join(out)

if __name__ == "__main__":
    sys.exit(main())
