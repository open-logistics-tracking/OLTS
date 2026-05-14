"""ULSC state-machine validator.

Loads ``ulsc/transitions.csv`` from the OLTS repo root (relative path) at
import time and exposes:

- :func:`is_valid_transition` — check if a (from, to) pair is allowed
- :func:`next_states` — set of states reachable from a given code
- :func:`previous_states` — set of states that can transition into a given code
- :func:`is_terminal` — whether a state is normally terminal
- :func:`classify` — terminal / exceptional / active

Implicit rule: ``A → A`` (same code) is always considered valid (carriers often
emit multiple events with the same olts_code at different hubs).

CSV row with ``from_code = "*"`` defines a universal transition (any state
to the listed target). These are typically ``exception`` / ``damaged`` / ``lost``.

Rows with ``kind = "exception"`` require ``context`` to mark the exception
explicitly (e.g. ``context={"rma": True}`` for ``delivered → return_initiated``).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

from oltrack.ulsc import ALL_CODES

# Terminal states: under normal conditions no further events expected.
TERMINAL_CODES: frozenset[str] = frozenset({
    "delivered",
    "returned_to_sender",
    "order_cancelled",
    "lost",
    "signed_by_third_party",
})

# Exceptional states: may continue or terminate depending on outcome.
EXCEPTIONAL_CODES: frozenset[str] = frozenset({
    "damaged",
    "exception",
    "refused",
    "address_issue",
    "recipient_unavailable",
    "pickup_failed",
    "delivery_attempted",
    "customs_held",
})


@dataclass(frozen=True)
class Transition:
    from_code: str  # may be "*" for universal
    to_code: str
    kind: str  # "normal" | "exception" | "universal"
    note: str = ""


def _default_csv_path() -> Path:
    """Locate ``ulsc/transitions.csv`` by walking up from this file."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "ulsc" / "transitions.csv"
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "ulsc/transitions.csv not found in any parent of "
        f"{here}. Pass an explicit path to load_transitions()."
    )


def load_transitions(path: str | Path | None = None) -> list[Transition]:
    """Load and return transitions from a CSV file."""
    csv_path = Path(path) if path else _default_csv_path()
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [
            Transition(
                from_code=row["from_code"].strip(),
                to_code=row["to_code"].strip(),
                kind=row.get("kind", "normal").strip() or "normal",
                note=(row.get("note") or "").strip(),
            )
            for row in reader
            if row.get("from_code")
        ]


_TRANSITIONS: list[Transition] = load_transitions()

# Index for fast lookup. Key is (from, to). Value is the Transition.
# Universal entries are also exposed via _UNIVERSAL_TARGETS.
_INDEX: dict[tuple[str, str], Transition] = {
    (t.from_code, t.to_code): t for t in _TRANSITIONS
}
_UNIVERSAL_TARGETS: frozenset[str] = frozenset(
    t.to_code for t in _TRANSITIONS if t.from_code == "*"
)


def is_terminal(code: str) -> bool:
    """Return True if ``code`` is normally a terminal state."""
    return code in TERMINAL_CODES


def classify(code: str) -> str:
    """Return ``"terminal"``, ``"exceptional"``, or ``"active"``."""
    if code in TERMINAL_CODES:
        return "terminal"
    if code in EXCEPTIONAL_CODES:
        return "exceptional"
    return "active"


def next_states(code: str) -> set[str]:
    """Return the set of states reachable from ``code`` via *normal* transitions.

    Includes universal targets (``exception`` / ``damaged`` / ``lost``).
    Excludes ``exception``-kind entries (those require explicit context).
    Does not include ``code`` itself (same-code repetition is allowed but
    not a real transition).
    """
    out = {
        t.to_code for t in _TRANSITIONS
        if t.from_code == code and t.kind == "normal"
    }
    out |= _UNIVERSAL_TARGETS
    return out


def previous_states(code: str) -> set[str]:
    """Return the set of states that can normally transition into ``code``."""
    out = {
        t.from_code for t in _TRANSITIONS
        if t.to_code == code and t.kind == "normal" and t.from_code != "*"
    }
    if code in _UNIVERSAL_TARGETS:
        out |= ALL_CODES
    return out


def is_valid_transition(
    from_code: str,
    to_code: str,
    context: Mapping[str, object] | None = None,
) -> tuple[bool, str]:
    """Validate a transition. Returns ``(is_valid, reason)``.

    ``reason`` is a short human-readable note: empty on success, or an
    explanation if the transition is rejected.

    Rules:
    1. ``from == to`` → valid (same-code repetition).
    2. Both codes must be valid ULSC codes.
    3. Direct match in transitions table → valid (with optional context check
       for ``kind == "exception"``).
    4. Universal target (``*`` row) → valid.
    5. Otherwise → invalid.
    """
    if from_code == to_code:
        return True, "same code repeats are allowed"

    if from_code not in ALL_CODES:
        return False, f"unknown from_code: {from_code!r}"
    if to_code not in ALL_CODES:
        return False, f"unknown to_code: {to_code!r}"

    direct = _INDEX.get((from_code, to_code))
    if direct is not None:
        if direct.kind == "exception":
            if not context:
                return False, (
                    f"transition {from_code} → {to_code} is exceptional "
                    f"({direct.note or 'requires context'}); pass context="
                    "{...} to mark the exception explicitly"
                )
            return True, f"exceptional ({direct.note})" if direct.note else "exceptional"
        return True, direct.note

    if to_code in _UNIVERSAL_TARGETS:
        return True, f"universal target ({to_code})"

    if from_code in TERMINAL_CODES:
        return False, f"{from_code} is terminal; cannot transition further"

    return False, f"no valid transition {from_code} → {to_code}"


def validate_event_sequence(
    codes: Iterable[str],
    *,
    context: Mapping[str, object] | None = None,
) -> list[tuple[int, str, str, str]]:
    """Validate a chronological code sequence. Returns list of invalid steps:
    ``(index, from_code, to_code, reason)``. Empty list = all valid.

    ``index`` is the position of ``to_code`` in the input sequence.
    """
    seq = list(codes)
    invalid: list[tuple[int, str, str, str]] = []
    for i in range(1, len(seq)):
        prev, curr = seq[i - 1], seq[i]
        ok, reason = is_valid_transition(prev, curr, context=context)
        if not ok:
            invalid.append((i, prev, curr, reason))
    return invalid


__all__ = [
    "Transition",
    "TERMINAL_CODES",
    "EXCEPTIONAL_CODES",
    "load_transitions",
    "is_terminal",
    "classify",
    "next_states",
    "previous_states",
    "is_valid_transition",
    "validate_event_sequence",
]
