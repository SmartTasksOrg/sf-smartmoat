"""UML data objects for SmartMoat — the diagram in the README is these classes."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class Task:
    name: str
    agent_exposure: float
    human_moat: float

@dataclass
class MoatScore:
    exposure: float
    moat: float
    percentile: int

@dataclass
class Plan:
    moves: list[str]
