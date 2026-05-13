"""Adapter for 顺丰速运 / SF Express Open Platform (api.sf-express.com).

Reference response shape from mappings/cn/sf.csv source notes:

    {
      "apiResultCode": "A0000",
      "msgData": {
        "waybillNo": "SF1234567890",
        "expressStatus": 6,
        "expressStatusDesc": "已签收",
        "originCode": "...",
        "destCode": "...",
        "routeResps": [
          {
            "acceptTime": "2024-06-04 18:42:11",
            "acceptAddress": "北京朝阳CBD营业部",
            "remark": "客户签收",
            "opcode": "160",
            "opcodeDesc": "客户签收",
            "operatorPhone": "139****5678",
            "routeFrom": "北京朝阳CBD营业部",
            "routeTo": ""
          },
          ...
        ]
      }
    }

The adapter maps each routeResps[] item to a TrackingEvent dict, prefixing
opcode with "opcode:" to match the mapping CSV convention.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from oltrack import normalize

_SH_TZ = ZoneInfo("Asia/Shanghai")


def _isoformat_local(time_str: str) -> str:
    """Parse "2024-06-04 18:42:11" and attach Asia/Shanghai timezone."""
    naive = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return naive.replace(tzinfo=_SH_TZ).isoformat()


def normalize_event(route_resp: dict[str, Any]) -> dict[str, Any]:
    """Convert one routeResps[] item to an OLTS TrackingEvent."""
    raw_code = f"opcode:{route_resp['opcode']}"
    location = {}
    if addr := route_resp.get("acceptAddress"):
        location["name"] = addr
    metadata: dict[str, Any] = {}
    if route_from := route_resp.get("routeFrom"):
        metadata["routeFrom"] = route_from
    if route_to := route_resp.get("routeTo"):
        metadata["routeTo"] = route_to

    operator = None
    if phone := route_resp.get("operatorPhone"):
        operator = {"phone": phone}

    return normalize.event(
        carrier="sf",
        carrier_event_code=raw_code,
        event_time=_isoformat_local(route_resp["acceptTime"]),
        description=route_resp.get("remark") or route_resp.get("opcodeDesc"),
        location=location or None,
        operator=operator,
        metadata=metadata or None,
    )


def normalize_response(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse a full SF response into a list of TrackingEvent dicts."""
    if raw.get("apiResultCode") != "A0000":
        raise ValueError(f"SF API error: {raw.get('apiErrorMsg', raw.get('apiResultCode'))}")
    msg = raw.get("msgData", {})
    routes = msg.get("routeResps", [])
    return [normalize_event(r) for r in routes]


def normalize_to_shipment(raw: dict[str, Any]) -> dict[str, Any]:
    """Parse a full SF response into an OLTS Shipment dict."""
    msg = raw.get("msgData", {})
    events = normalize_response(raw)
    return normalize.shipment(
        tracking_number=msg["waybillNo"],
        events=events,
        carrier="sf",
        metadata={"expressStatus": msg.get("expressStatus")} if msg.get("expressStatus") else None,
    )
