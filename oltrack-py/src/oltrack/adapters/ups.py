"""Adapter for UPS Tracking API (onlinetools.ups.com).

Reference response shape:

    {
      "trackResponse": {
        "shipment": [{
          "package": [{
            "trackingNumber": "1Z...",
            "currentStatus": {"description": "Delivered"},
            "statusCode": "011",
            "statusDescription": "Delivered",
            "activity": [
              {
                "date": "20240612",
                "time": "183000",
                "gmtDate": "20240612",
                "gmtTime": "230000",
                "gmtOffset": "-04:00",
                "location": {"address": {"city": "Atlanta", "stateProvince": "GA", "country": "US"}},
                "status": {"code": "F4", "description": "...", "statusCode": "011", "type": "D"}
              }
            ]
          }]
        }]
      }
    }
"""

from __future__ import annotations

from typing import Any

from oltrack import normalize


def _ups_time(activity: dict[str, Any]) -> str:
    """Combine UPS gmtDate + gmtTime + gmtOffset into ISO 8601."""
    gmt_date = activity.get("gmtDate") or activity.get("date")
    gmt_time = activity.get("gmtTime") or activity.get("time")
    gmt_offset = activity.get("gmtOffset", "+00:00")
    if not gmt_date or not gmt_time:
        raise ValueError(f"UPS activity missing date/time: {activity}")
    # gmtDate "20240612" → "2024-06-12"; gmtTime "230000" → "23:00:00" (HHMMSS)
    date_iso = f"{gmt_date[:4]}-{gmt_date[4:6]}-{gmt_date[6:8]}"
    time_str = gmt_time.zfill(6)
    time_iso = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
    return f"{date_iso}T{time_iso}{gmt_offset}"


def normalize_event(activity: dict[str, Any]) -> dict[str, Any]:
    status = activity.get("status", {})
    raw_code = status.get("code")
    if not raw_code:
        raise ValueError(f"UPS activity missing status.code: {activity}")

    addr = (activity.get("location") or {}).get("address", {}) or {}
    location: dict[str, Any] = {}
    if city := addr.get("city"):
        location["city"] = city
    if state := addr.get("stateProvince"):
        location["state"] = state
    if country := addr.get("country"):
        location["countryCode"] = country
    if postal := addr.get("postalCode"):
        location["postalCode"] = postal

    metadata: dict[str, Any] = {}
    if status_code := status.get("statusCode"):
        metadata["statusCode"] = status_code
    if status_type := status.get("type"):
        metadata["statusType"] = status_type
    is_logical = activity.get("logicalScan") is True

    return normalize.event(
        carrier="ups",
        carrier_event_code=raw_code,
        event_time=_ups_time(activity),
        description=status.get("description"),
        location=location or None,
        is_logical_event=is_logical,
        metadata=metadata or None,
    )


def normalize_response(raw: dict[str, Any]) -> list[dict[str, Any]]:
    shipments = (raw.get("trackResponse") or {}).get("shipment", [])
    if not shipments:
        return []
    package = shipments[0].get("package", [])
    if not package:
        return []
    activities = package[0].get("activity", [])
    return [normalize_event(a) for a in activities]


def normalize_to_shipment(raw: dict[str, Any]) -> dict[str, Any]:
    shipments = (raw.get("trackResponse") or {}).get("shipment", [])
    if not shipments:
        raise ValueError("UPS response has no shipment")
    package = shipments[0].get("package", [])
    if not package:
        raise ValueError("UPS response shipment[0].package is empty")
    pkg = package[0]
    tracking_no = pkg.get("trackingNumber")
    if not tracking_no:
        raise ValueError("UPS package missing trackingNumber")
    events = [normalize_event(a) for a in pkg.get("activity", [])]
    weight = None
    if w := pkg.get("weight"):
        weight = {"value": float(w["weight"]), "unit": w.get("unitOfMeasurement", "LBS").rstrip("S")}
    return normalize.shipment(
        tracking_number=tracking_no,
        events=events,
        carrier="ups",
        service=(pkg.get("service") or {}).get("description"),
        weight=weight,
    )
