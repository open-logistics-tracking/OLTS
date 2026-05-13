"""Top-level normalization entry points.

Adapters in :mod:`oltrack.adapters` provide carrier-specific parsing of raw
API responses into TrackingEvent dicts. This module provides a single-event
helper for callers who have already done the parsing.
"""

from __future__ import annotations

from typing import Any, Optional

from oltrack.mappings import lookup


def event(
    *,
    carrier: str,
    carrier_event_code: str,
    event_time: str,
    description: Optional[Any] = None,
    location: Optional[dict[str, Any]] = None,
    operator: Optional[dict[str, Any]] = None,
    piece_id: Optional[str] = None,
    transport: Optional[dict[str, Any]] = None,
    is_logical_event: bool = False,
    notes: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
    olts_code: Optional[str] = None,
) -> dict[str, Any]:
    """Build a single OLTS TrackingEvent dict.

    If ``olts_code`` is not supplied, looks it up from the carrier mapping.

    Args:
        carrier: Carrier slug (e.g. 'sf', 'dhl').
        carrier_event_code: Raw event code as returned by the carrier API.
        event_time: ISO 8601 timestamp with timezone offset.
        olts_code: Optional explicit ULSC code; if omitted, derived from
            carrier+carrier_event_code via mappings/.

    Returns:
        A dict shaped to the OLTS v0.2 TrackingEvent JSON Schema. Omits any
        optional fields the caller didn't provide.
    """
    if olts_code is None:
        olts_code = lookup(carrier, carrier_event_code)

    out: dict[str, Any] = {
        "eventTime": event_time,
        "carrierCode": carrier,
        "carrierEventCode": carrier_event_code,
        "oltsCode": olts_code,
    }
    if description is not None:
        out["description"] = description
    if location:
        out["location"] = location
    if operator:
        out["operator"] = operator
    if piece_id:
        out["pieceId"] = piece_id
    if transport:
        out["transport"] = transport
    if is_logical_event:
        out["isLogicalEvent"] = True
    if notes:
        out["notes"] = notes
    if metadata:
        out["metadata"] = metadata
    return out


def shipment(
    *,
    tracking_number: str,
    events: list[dict[str, Any]],
    carrier: Optional[str] = None,
    **extras: Any,
) -> dict[str, Any]:
    """Build a Shipment dict wrapping a list of normalized events.

    ``extras`` accepts any of the optional Shipment fields (service,
    currentStatus, origin, destination, pieces, weight, dimensions,
    declaredValue, isReturn, metadata).
    """
    out: dict[str, Any] = {
        "trackingNumber": tracking_number,
        "events": events,
    }
    if carrier:
        out["carrierCode"] = carrier
    # currentStatus auto-derive: take the last event's oltsCode
    if "currentStatus" not in extras and events:
        out["currentStatus"] = events[-1]["oltsCode"]
    for k in ("service", "currentStatus", "origin", "destination",
              "estimatedDelivery", "actualDelivery", "pieces",
              "weight", "dimensions", "declaredValue", "isReturn", "metadata"):
        if k in extras and extras[k] is not None:
            out[k] = extras[k]
    return out
