#!/usr/bin/env python3
"""Validate OLTS v0.2 JSON Schemas and all example instances.

Runs two checks:
  1. Each schema in schemas/v0.2/ is syntactically valid (Draft 2020-12).
  2. Each example in examples/v0.2/ validates against its target schema.

Naming convention used to route an example to its schema:
  *-event.json    → tracking-event.json
  *-shipment.json → shipment.json

Run from repo root:

    python3 tools/validate_schemas.py

Exits 0 on success, 1 on any error. CI-ready, no fragile globs.

Requires: jsonschema >= 4.18 (uses `referencing` library, not the
deprecated RefResolver).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry
from referencing.jsonschema import DRAFT202012


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "schemas" / "v0.2"
EXAMPLE_DIR = REPO_ROOT / "examples" / "v0.2"

SCHEMAS = {
    "tracking-event.json": SCHEMA_DIR / "tracking-event.json",
    "shipment.json":       SCHEMA_DIR / "shipment.json",
}

# Map example filename suffix → schema basename used for $ref resolution.
EXAMPLE_ROUTES = [
    ("-shipment.json", "shipment.json"),
    ("-event.json",    "tracking-event.json"),
]

PII_PATTERNS = [
    ("mainland China mobile phone", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")),
    ("mainland China ID number", re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)")),
]


def build_registry(schemas: dict[str, dict]) -> Registry:
    """Register each schema under both its filename and its $id so $ref
    expressions like 'tracking-event.json' and the full $id URL both resolve."""
    resources: list[tuple[str, object]] = []
    for filename, schema in schemas.items():
        resources.append((filename, DRAFT202012.create_resource(schema)))
        if "$id" in schema:
            resources.append((schema["$id"], DRAFT202012.create_resource(schema)))
    return Registry().with_resources(resources)


def iter_strings(value: object, path: str = ""):
    """Yield (json_pointer, string_value) pairs from nested JSON data."""
    if isinstance(value, str):
        yield path or "/", value
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            yield from iter_strings(item, f"{path}/{idx}")
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from iter_strings(item, f"{path}/{key}")


def pii_errors(instance: object) -> list[str]:
    """Detect obvious unmasked personal data in public examples."""
    errors: list[str] = []
    for pointer, text in iter_strings(instance):
        for label, pattern in PII_PATTERNS:
            if pattern.search(text):
                errors.append(f"{label} at {pointer}: {text!r}")
    return errors


def main() -> int:
    # Phase 1: load schemas + syntactic check
    loaded: dict[str, dict] = {}
    syntax_errors: list[str] = []
    for name, path in SCHEMAS.items():
        if not path.is_file():
            syntax_errors.append(f"{name}: missing at {path}")
            continue
        with path.open() as f:
            schema = json.load(f)
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as e:
            syntax_errors.append(f"{name}: schema syntax error — {e}")
            continue
        loaded[name] = schema
        print(f"✅ schema {name} syntactically valid")

    if syntax_errors:
        for e in syntax_errors:
            print(f"❌ {e}", file=sys.stderr)
        return 1

    # Phase 2: validate examples
    registry = build_registry(loaded)
    example_files = sorted(EXAMPLE_DIR.glob("*.json"))
    if not example_files:
        print(f"⚠ no examples found under {EXAMPLE_DIR}")
        return 0

    instance_errors = 0
    for path in example_files:
        rel = path.relative_to(REPO_ROOT)
        # Route by filename suffix
        target = None
        for suffix, schema_name in EXAMPLE_ROUTES:
            if path.name.endswith(suffix):
                target = schema_name
                break
        if target is None:
            print(f"⚠ {rel}: unrecognized suffix, skipping (rename to *-event.json or *-shipment.json)")
            continue

        with path.open() as f:
            instance = json.load(f)
        validator = Draft202012Validator(loaded[target], registry=registry)
        errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
        if errors:
            instance_errors += len(errors)
            for e in errors[:5]:
                loc = "/".join(str(p) for p in e.path) or "(root)"
                print(f"❌ {rel} → {target}: {e.message} at /{loc}", file=sys.stderr)
        else:
            print(f"✅ example {rel} validates against {target}")

        pii = pii_errors(instance)
        if pii:
            instance_errors += len(pii)
            for e in pii[:5]:
                print(f"❌ {rel}: possible unmasked PII — {e}", file=sys.stderr)

    if instance_errors:
        print(f"\nFAILED: {instance_errors} instance validation error(s)", file=sys.stderr)
        return 1

    print(f"\nOK — all {len(loaded)} schemas + {len(example_files)} examples valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
