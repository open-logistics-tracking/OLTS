"""ULSC dictionary — 32 OLTS standard status codes, 7 categories.

Codes are exposed both as a typed Enum (for IDE autocomplete) and as a plain
str constant. Use whichever fits your context; both compare equal to the
string form because UlscCode subclasses str.

Source of truth: ``ulsc/ulsc.csv`` in the OLTS repo root. This module hardcodes
the v0.1 dictionary for fast import without filesystem reads. When the CSV is
updated, regenerate this module via tools (see :func:`reload_from_csv`).
"""

from __future__ import annotations

import csv
from enum import Enum
from pathlib import Path


class UlscCategory(str, Enum):
    """7 top-level categories of the ULSC dictionary."""
    PRE_SHIPMENT = "pre_shipment"
    PICKUP = "pickup"
    TRANSIT = "transit"
    CUSTOMS = "customs"
    DELIVERY = "delivery"
    EXCEPTION = "exception"
    RETURN = "return"


class UlscCode(str, Enum):
    """The 32 ULSC v0.1 codes. UlscCode subclasses str so comparisons work
    transparently with raw string olts_code values (e.g. from JSON dicts)."""

    # pre_shipment (3)
    ORDER_CREATED = "order_created"
    ORDER_CANCELLED = "order_cancelled"
    LABEL_PRINTED = "label_printed"

    # pickup (3)
    PICKUP_SCHEDULED = "pickup_scheduled"
    PICKED_UP = "picked_up"
    PICKUP_FAILED = "pickup_failed"

    # transit (5)
    ARRIVED_AT_HUB = "arrived_at_hub"
    DEPARTED_FROM_HUB = "departed_from_hub"
    IN_TRANSIT = "in_transit"
    TRANSFERRED_TO_CARRIER = "transferred_to_carrier"
    ARRIVED_AT_DESTINATION = "arrived_at_destination"

    # customs (6)
    CUSTOMS_DECLARED = "customs_declared"
    CUSTOMS_HELD = "customs_held"
    CUSTOMS_INSPECTION = "customs_inspection"
    CUSTOMS_RELEASED = "customs_released"
    CUSTOMS_DUTY_PAID = "customs_duty_paid"
    CLEARANCE_COMPLETED = "clearance_completed"

    # delivery (6)
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERY_ATTEMPTED = "delivery_attempted"
    DELIVERED = "delivered"
    DELIVERY_TO_LOCKER = "delivery_to_locker"
    AWAITING_PICKUP = "awaiting_pickup"
    SIGNED_BY_THIRD_PARTY = "signed_by_third_party"

    # exception (6)
    EXCEPTION = "exception"
    DAMAGED = "damaged"
    LOST = "lost"
    ADDRESS_ISSUE = "address_issue"
    RECIPIENT_UNAVAILABLE = "recipient_unavailable"
    REFUSED = "refused"

    # return (3)
    RETURN_INITIATED = "return_initiated"
    IN_RETURN_TRANSIT = "in_return_transit"
    RETURNED_TO_SENDER = "returned_to_sender"


# Authoritative category mapping (matches ulsc/ulsc.csv)
CATEGORY: dict[UlscCode, UlscCategory] = {
    UlscCode.ORDER_CREATED: UlscCategory.PRE_SHIPMENT,
    UlscCode.ORDER_CANCELLED: UlscCategory.PRE_SHIPMENT,
    UlscCode.LABEL_PRINTED: UlscCategory.PRE_SHIPMENT,
    UlscCode.PICKUP_SCHEDULED: UlscCategory.PICKUP,
    UlscCode.PICKED_UP: UlscCategory.PICKUP,
    UlscCode.PICKUP_FAILED: UlscCategory.PICKUP,
    UlscCode.ARRIVED_AT_HUB: UlscCategory.TRANSIT,
    UlscCode.DEPARTED_FROM_HUB: UlscCategory.TRANSIT,
    UlscCode.IN_TRANSIT: UlscCategory.TRANSIT,
    UlscCode.TRANSFERRED_TO_CARRIER: UlscCategory.TRANSIT,
    UlscCode.ARRIVED_AT_DESTINATION: UlscCategory.TRANSIT,
    UlscCode.CUSTOMS_DECLARED: UlscCategory.CUSTOMS,
    UlscCode.CUSTOMS_HELD: UlscCategory.CUSTOMS,
    UlscCode.CUSTOMS_INSPECTION: UlscCategory.CUSTOMS,
    UlscCode.CUSTOMS_RELEASED: UlscCategory.CUSTOMS,
    UlscCode.CUSTOMS_DUTY_PAID: UlscCategory.CUSTOMS,
    UlscCode.CLEARANCE_COMPLETED: UlscCategory.CUSTOMS,
    UlscCode.OUT_FOR_DELIVERY: UlscCategory.DELIVERY,
    UlscCode.DELIVERY_ATTEMPTED: UlscCategory.DELIVERY,
    UlscCode.DELIVERED: UlscCategory.DELIVERY,
    UlscCode.DELIVERY_TO_LOCKER: UlscCategory.DELIVERY,
    UlscCode.AWAITING_PICKUP: UlscCategory.DELIVERY,
    UlscCode.SIGNED_BY_THIRD_PARTY: UlscCategory.DELIVERY,
    UlscCode.EXCEPTION: UlscCategory.EXCEPTION,
    UlscCode.DAMAGED: UlscCategory.EXCEPTION,
    UlscCode.LOST: UlscCategory.EXCEPTION,
    UlscCode.ADDRESS_ISSUE: UlscCategory.EXCEPTION,
    UlscCode.RECIPIENT_UNAVAILABLE: UlscCategory.EXCEPTION,
    UlscCode.REFUSED: UlscCategory.EXCEPTION,
    UlscCode.RETURN_INITIATED: UlscCategory.RETURN,
    UlscCode.IN_RETURN_TRANSIT: UlscCategory.RETURN,
    UlscCode.RETURNED_TO_SENDER: UlscCategory.RETURN,
}

ALL_CODES: frozenset[str] = frozenset(code.value for code in UlscCode)


def is_valid(code: str) -> bool:
    """Return True if ``code`` is one of the 32 ULSC codes."""
    return code in ALL_CODES


def category_of(code: str | UlscCode) -> UlscCategory:
    """Return the category of a given OLTS code."""
    if not isinstance(code, UlscCode):
        code = UlscCode(code)
    return CATEGORY[code]


def reload_from_csv(path: str | Path) -> set[str]:
    """Reload the dictionary from a `ulsc/ulsc.csv` file. Useful for asserting
    that this module matches the CSV after a v0.2+ dictionary update.

    Returns the set of codes found in the CSV. Compare with :data:`ALL_CODES`
    to detect drift.
    """
    csv_path = Path(path)
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["code"].strip() for row in reader if row.get("code")}
