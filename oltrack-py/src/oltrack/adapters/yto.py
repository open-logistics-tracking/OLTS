"""Adapter for 圆通速递 / YTO Express (圆通开放平台).

Reference response shape (from 调研报告 §2.1):

    {
      "param": [{
        "waybill_No": "YT...",
        "upload_Time": "2024-06-04 18:42:11",
        "infoContent": "SIGNED",
        "processInfo": "客户签收",
        "city": "北京",
        "district": "朝阳区",
        "weight": 1.5
      }, ...]
    }

YTO uses English mnemonics like GOT/SIGNED/FAILED for its status codes.
The adapter prefixes carrier_event_code with the raw mnemonic directly
(matching mappings/cn/yto.csv convention).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from oltrack import normalize

_SH_TZ = ZoneInfo("Asia/Shanghai")


def _isoformat_local(time_str: str) -> str:
    naive = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return naive.replace(tzinfo=_SH_TZ).isoformat()


def normalize_event(item: dict[str, Any]) -> dict[str, Any]:
    raw_code = item["infoContent"]
    location: dict[str, Any] = {}
    if city := item.get("city"):
        location["city"] = city
    if district := item.get("district"):
        location["state"] = district  # 区县归 state 字段
    metadata = {}
    if weight := item.get("weight"):
        metadata["weight"] = weight

    return normalize.event(
        carrier="yto",
        carrier_event_code=raw_code,
        event_time=_isoformat_local(item["upload_Time"]),
        description=item.get("processInfo"),
        location=location or None,
        metadata=metadata or None,
    )


def normalize_response(raw: dict[str, Any]) -> list[dict[str, Any]]:
    items = raw.get("param", [])
    return [normalize_event(i) for i in items]


def normalize_to_shipment(raw: dict[str, Any]) -> dict[str, Any]:
    items = raw.get("param", [])
    if not items:
        raise ValueError("YTO response has no param[]")
    waybill_no = items[0].get("waybill_No")
    if not waybill_no:
        raise ValueError("YTO response missing waybill_No")
    events = [normalize_event(i) for i in items]
    return normalize.shipment(
        tracking_number=waybill_no,
        events=events,
        carrier="yto",
    )
