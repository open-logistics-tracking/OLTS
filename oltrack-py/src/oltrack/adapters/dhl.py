"""Adapter for DHL Tracking Unified API (api-eu.dhl.com).

Reference response shape (per mappings/intl/dhl.csv source):

    {
      "shipments": [{
        "shipmentId": "0034988765432",
        "trackingNumber": "0034988765432",
        "service": "express",
        "status": {
          "statusCode": "delivered",
          "status": "Delivered",
          "timestamp": "2024-06-04T03:17:00+02:00"
        },
        "estimatedTimeOfDelivery": "2024-06-05",
        "origin": {"address": {"countryCode": "CN"}},
        "destination": {"address": {"countryCode": "DE"}},
        "events": [
          {
            "timestamp": "2024-06-04T03:17:00+02:00",
            "statusCode": "transit",
            "status": "DLVRD:CUSTM",  // carrier_event_code form
            "description": "Handed over to customs",
            "location": {"address": {"addressLocality": "FRANKFURT - DE", "countryCode": "DE"}}
          },
          ...
        ]
      }]
    }

DHL exposes both a top-level StatusCode (5 values) and event-level event:ric
codes. We use the event-level when available, falling back to the statusCode
prefix.
"""

from __future__ import annotations

from typing import Any

from oltrack import normalize


def _parse_location(loc: dict[str, Any]) -> dict[str, Any]:
    """Parse DHL location subobject into OLTS Location."""
    if not loc:
        return {}
    address = loc.get("address", {}) if isinstance(loc, dict) else {}
    out: dict[str, Any] = {}
    if addr_loc := address.get("addressLocality"):
        out["name"] = addr_loc
        # addressLocality is often "CITY - STATE - COUNTRY"; take first as city
        parts = [p.strip() for p in addr_loc.split("-")]
        if parts:
            out["city"] = parts[0]
    if cc := address.get("countryCode"):
        out["countryCode"] = cc
    if pc := address.get("postalCode"):
        out["postalCode"] = pc
    return out


def normalize_event(event_obj: dict[str, Any]) -> dict[str, Any]:
    """Convert one events[] item to an OLTS TrackingEvent."""
    # Prefer event-level event:ric code in `status`; fall back to statusCode with "status:" prefix
    raw_status = event_obj.get("status")
    if raw_status and ":" in raw_status:
        carrier_event_code = raw_status
    else:
        carrier_event_code = f"status:{event_obj.get('statusCode', 'unknown')}"

    location = _parse_location(event_obj.get("location") or {})
    return normalize.event(
        carrier="dhl",
        carrier_event_code=carrier_event_code,
        event_time=event_obj["timestamp"],
        description=event_obj.get("description") or event_obj.get("remark"),
        location=location or None,
        piece_id=event_obj.get("pieceId"),
        metadata={k: v for k, v in event_obj.items()
                  if k in ("statusDetailed", "nextSteps") and v},
    )


def normalize_response(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse a DHL Tracking Unified API response into a flat list of events."""
    shipments = raw.get("shipments", [])
    if not shipments:
        return []
    return [normalize_event(e) for e in shipments[0].get("events", [])]


def normalize_to_shipment(raw: dict[str, Any]) -> dict[str, Any]:
    """Parse a full DHL response into an OLTS Shipment dict."""
    shipments = raw.get("shipments", [])
    if not shipments:
        raise ValueError("DHL response has no shipments")
    sh = shipments[0]
    events = [normalize_event(e) for e in sh.get("events", [])]
    origin_addr = (sh.get("origin") or {}).get("address", {})
    dest_addr = (sh.get("destination") or {}).get("address", {})
    origin = {"countryCode": origin_addr["countryCode"]} if origin_addr.get("countryCode") else None
    destination = {"countryCode": dest_addr["countryCode"]} if dest_addr.get("countryCode") else None

    return normalize.shipment(
        tracking_number=sh["trackingNumber"],
        events=events,
        carrier="dhl",
        service=sh.get("service"),
        origin=origin,
        destination=destination,
        estimatedDelivery=sh.get("estimatedTimeOfDelivery"),
    )
