#!/usr/bin/env python3
"""OLTS mapping validator.

Validates that all carrier mapping CSV files in ``mappings/`` are well-formed
and that every ``olts_code`` reference points to a code defined in
``ulsc/ulsc.csv``.

Run from the repo root:

    python3 tools/validate.py

Exits 0 on success, 1 on any validation error. Output is intentionally terse
so it can be wired into CI as a hard gate.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ULSC_PATH = REPO_ROOT / "ulsc" / "ulsc.csv"
MAPPINGS_DIR = REPO_ROOT / "mappings"


def load_ulsc() -> set[str]:
    """Return the set of valid OLTS status codes from ulsc/ulsc.csv."""
    codes: set[str] = set()
    with ULSC_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or "code" not in reader.fieldnames:
            raise SystemExit(f"ulsc.csv missing 'code' column: {reader.fieldnames}")
        for row in reader:
            code = (row.get("code") or "").strip()
            if code:
                codes.add(code)
    return codes


def iter_mapping_files() -> list[Path]:
    """Find all mapping CSVs under mappings/, sorted for deterministic output."""
    return sorted(
        p for p in MAPPINGS_DIR.rglob("*.csv") if p.is_file()
    )


def validate_file(path: Path, ulsc_codes: set[str]) -> tuple[int, list[str]]:
    """Validate one carrier mapping CSV.

    Returns (row_count, errors). ``row_count`` excludes header and comment
    lines so the caller can produce aggregate stats.
    """
    errors: list[str] = []
    rel = path.relative_to(REPO_ROOT)
    row_count = 0
    seen_codes: set[str] = set()

    # Filter out comment lines (# prefix) before handing to csv.reader, so
    # MAPPING_FORMAT.md's convention of `# Source: ...` headers is honored.
    with path.open(newline="", encoding="utf-8") as f:
        non_comment = [ln for ln in f if not ln.lstrip().startswith("#") and ln.strip()]

    reader = csv.reader(non_comment)
    rows = list(reader)
    if not rows:
        # Pure placeholder file — header may be in the comment block. Tolerated.
        return 0, errors

    header = [h.strip() for h in rows[0]]
    expected = ["carrier_code", "carrier_name", "olts_code", "notes"]
    if header != expected:
        errors.append(f"{rel}: header is {header}, expected {expected}")
        return 0, errors

    for lineno, row in enumerate(rows[1:], start=2):
        if len(row) != 4:
            errors.append(f"{rel}:{lineno}: NF={len(row)}, expected 4 — {row}")
            continue
        carrier_code, carrier_name, olts_code, _notes = (c.strip() for c in row)
        if not carrier_code:
            errors.append(f"{rel}:{lineno}: empty carrier_code")
            continue
        if not carrier_name:
            errors.append(f"{rel}:{lineno}: empty carrier_name for {carrier_code!r}")
        # Per MAPPING_FORMAT.md: 同一 carrier_code 在一个映射文件里只能出现一次
        if carrier_code in seen_codes:
            errors.append(f"{rel}:{lineno}: duplicate carrier_code {carrier_code!r}")
        seen_codes.add(carrier_code)
        if olts_code and olts_code not in ulsc_codes:
            errors.append(
                f"{rel}:{lineno}: olts_code {olts_code!r} not in ulsc/ulsc.csv"
            )
        row_count += 1

    return row_count, errors


def main() -> int:
    if not ULSC_PATH.is_file():
        print(f"ERROR: {ULSC_PATH} not found", file=sys.stderr)
        return 1

    ulsc_codes = load_ulsc()
    files = iter_mapping_files()

    total_rows = 0
    all_errors: list[str] = []
    per_file_counts: list[tuple[str, int]] = []

    for path in files:
        rows, errors = validate_file(path, ulsc_codes)
        total_rows += rows
        all_errors.extend(errors)
        per_file_counts.append((str(path.relative_to(REPO_ROOT)), rows))

    # Coverage stats: which ULSC codes are actually used by any mapping
    used_codes: set[str] = set()
    for path in files:
        with path.open(newline="", encoding="utf-8") as f:
            non_comment = [ln for ln in f if not ln.lstrip().startswith("#") and ln.strip()]
        for row in csv.reader(non_comment):
            if len(row) >= 3 and row[2].strip() not in ("", "olts_code"):
                used_codes.add(row[2].strip())

    print(f"ulsc dictionary: {len(ulsc_codes)} codes")
    print(f"mapping files:   {len(files)} files, {total_rows} total carrier codes")
    print(f"ulsc coverage:   {len(used_codes & ulsc_codes)}/{len(ulsc_codes)} used")
    unused = sorted(ulsc_codes - used_codes)
    if unused:
        print(f"ulsc unused:     {', '.join(unused)}")

    print()
    print("per-file row counts:")
    for name, rows in per_file_counts:
        print(f"  {name}: {rows}")

    if all_errors:
        print()
        print(f"VALIDATION FAILED — {len(all_errors)} error(s):", file=sys.stderr)
        for e in all_errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    print()
    print("OK — all mappings valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
