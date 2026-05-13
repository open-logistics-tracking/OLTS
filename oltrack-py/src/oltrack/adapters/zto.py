"""Adapter for 中通快递 / ZTO Express (japi.zto.com).

Reference response shape (from open.zto.com docs):

    {
      "status": true,
      "result": [
        {
          "billCode": "73100059800035",
          "scanType": "签收",
          "scanDate": 1676429769000,
          "scanSite": {"name": "...", "city": "...", "prov": "..."},
          "preOrNextSite": {...},
          "signMan": "李四",
          "operateUser": "...",
          "desc": "..."
        },
        ...
      ]
    }

ZTO scanType 三种命名空间（中文 / 英文 / 数字），CSV 用原始码直接保留。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from oltrack import normalize


def _ms_to_isoformat(ms: int) -> str:
    """Convert millisecond epoch (ZTO's scanDate format) to ISO 8601 with UTC offset."""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()


def normalize_event(item: dict[str, Any]) -> dict[str, Any]:
    raw_code = item["scanType"]  # 中文 / 英文 / 数字 都直接用
    site = item.get("scanSite", {}) or {}
    location: dict[str, Any] = {}
    if name := site.get("name"):
        location["name"] = name
    if city := site.get("city"):
        location["city"] = city
    if prov := site.get("prov"):
        location["state"] = prov

    operator: dict[str, Any] = {}
    if name := item.get("operateUser"):
        operator["name"] = name
    if phone := item.get("operateUserPhone"):
        operator["phone"] = phone

    metadata: dict[str, Any] = {}
    if sign_man := item.get("signMan"):
        metadata["signMan"] = sign_man
    if next_site := item.get("preOrNextSite"):
        if next_name := next_site.get("name"):
            metadata["nextSiteName"] = next_name

    scan_date = item["scanDate"]
    event_time = _ms_to_isoformat(int(scan_date)) if isinstance(scan_date, (int, float)) else str(scan_date)

    return normalize.event(
        carrier="zto",
        carrier_event_code=raw_code,
        event_time=event_time,
        description=item.get("desc"),
        location=location or None,
        operator=operator or None,
        metadata=metadata or None,
    )


def normalize_response(raw: dict[str, Any]) -> list[dict[str, Any]]:
    if not raw.get("status"):
        raise ValueError(f"ZTO API error: {raw.get('message', raw.get('statusCode'))}")
    return [normalize_event(i) for i in raw.get("result", [])]


def normalize_to_shipment(raw: dict[str, Any]) -> dict[str, Any]:
    items = raw.get("result", [])
    if not items:
        raise ValueError("ZTO response has empty result[]")
    bill_code = items[0].get("billCode")
    if not bill_code:
        raise ValueError("ZTO response missing billCode")
    events = [normalize_event(i) for i in items]
    return normalize.shipment(
        tracking_number=bill_code,
        events=events,
        carrier="zto",
    )
