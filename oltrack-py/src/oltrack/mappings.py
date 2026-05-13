"""Load carrier mapping CSVs into an in-memory ``(carrier, raw_code) → olts_code`` dict.

Mappings are loaded lazily from the OLTS repo's ``mappings/`` directory. By
default we search relative to this module's location going up the tree until
we find ``mappings/``. Override with :func:`set_mappings_root` for non-standard
layouts.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional


# Cache: { (carrier, raw_code): olts_code }
_CACHE: dict[tuple[str, str], str] = {}
# Cache: { carrier: { raw_code: (carrier_name, olts_code, notes) } }
_DETAIL_CACHE: dict[str, dict[str, tuple[str, str, str]]] = {}

_mappings_root: Optional[Path] = None


def _default_root() -> Path:
    """Search upward from this file for a directory containing ``mappings/``."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "mappings").is_dir() and (parent / "ulsc" / "ulsc.csv").is_file():
            return parent / "mappings"
    raise RuntimeError(
        "Could not auto-locate the OLTS mappings/ directory. "
        "Call set_mappings_root(path) explicitly."
    )


def set_mappings_root(path: str | Path) -> None:
    """Override the mappings root location. Resets caches."""
    global _mappings_root
    _mappings_root = Path(path)
    _CACHE.clear()
    _DETAIL_CACHE.clear()


def _root() -> Path:
    global _mappings_root
    if _mappings_root is None:
        _mappings_root = _default_root()
    return _mappings_root


def _load_carrier(carrier: str) -> dict[str, tuple[str, str, str]]:
    """Load a single carrier's mapping CSV into the detail cache."""
    if carrier in _DETAIL_CACHE:
        return _DETAIL_CACHE[carrier]
    root = _root()
    # Search both cn/ and intl/
    for region in ("cn", "intl"):
        path = root / region / f"{carrier}.csv"
        if path.is_file():
            entries: dict[str, tuple[str, str, str]] = {}
            with path.open(newline="", encoding="utf-8") as f:
                reader = csv.reader(
                    (line for line in f if not line.lstrip().startswith("#") and line.strip())
                )
                header = next(reader, None)
                if header != ["carrier_code", "carrier_name", "olts_code", "notes"]:
                    raise ValueError(f"unexpected header in {path}: {header}")
                for row in reader:
                    if len(row) != 4:
                        continue
                    carrier_code, carrier_name, olts_code, notes = (c.strip() for c in row)
                    if carrier_code:
                        entries[carrier_code] = (carrier_name, olts_code, notes)
                        _CACHE[(carrier, carrier_code)] = olts_code
            _DETAIL_CACHE[carrier] = entries
            return entries
    raise FileNotFoundError(
        f"No mapping CSV found for carrier {carrier!r} under {root}/cn/ or {root}/intl/"
    )


def lookup(carrier: str, raw_code: str) -> str:
    """Return the ULSC code for ``raw_code`` under ``carrier``.

    Raises KeyError if the code is unknown for that carrier (don't silently
    map to 'exception' — let the caller decide).
    """
    key = (carrier, raw_code)
    if key not in _CACHE:
        _load_carrier(carrier)
    if key not in _CACHE:
        raise KeyError(f"unknown raw code {raw_code!r} for carrier {carrier!r}")
    return _CACHE[key]


def details(carrier: str, raw_code: str) -> tuple[str, str, str]:
    """Return ``(carrier_name, olts_code, notes)`` for a raw code."""
    if carrier not in _DETAIL_CACHE:
        _load_carrier(carrier)
    return _DETAIL_CACHE[carrier][raw_code]


def all_carriers() -> list[str]:
    """List all carriers with mapping CSVs in the repo."""
    root = _root()
    result: list[str] = []
    for region in ("cn", "intl"):
        d = root / region
        if d.is_dir():
            result.extend(sorted(p.stem for p in d.glob("*.csv")))
    return result
