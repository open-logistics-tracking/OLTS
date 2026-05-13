"""Adapter for 京东物流 / JD Logistics (open.jdl.com).

JDL exposes two-tier status codes (mappings/cn/jdl.csv):
  - status:N — 一级订单分类 (12 个)
  - state:N — 节点编码 (63 个)

Reference response shape:

    {
      "code": "1000",
      "data": {
        "traces": [
          {
            "state": 200001,
            "operationTitle": "配送员完成揽收",
            "operationTime": "2024-06-03 11:05:00",
            "operationRemark": "客户在前台",
            "city": "北京",
            "operatorPhone": "186****1234",
            "category": 420
          },
          ...
        ]
      }
    }
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
    state = item["state"]
    raw_code = f"state:{state}"
    location: dict[str, Any] = {}
    if city := item.get("city"):
        location["city"] = city

    operator: dict[str, Any] = {}
    if phone := item.get("operatorPhone"):
        operator["phone"] = phone

    metadata: dict[str, Any] = {}
    if category := item.get("category"):
        metadata["status"] = category  # 关联到一级订单分类
    if remark := item.get("operationRemark"):
        metadata["operationRemark"] = remark

    return normalize.event(
        carrier="jdl",
        carrier_event_code=raw_code,
        event_time=_isoformat_local(item["operationTime"]),
        description=item.get("operationTitle"),
        location=location or None,
        operator=operator or None,
        metadata=metadata or None,
    )


def normalize_response(raw: dict[str, Any]) -> list[dict[str, Any]]:
    if raw.get("code") != "1000":
        raise ValueError(f"JDL API error: {raw.get('message', raw.get('code'))}")
    traces = (raw.get("data") or {}).get("traces", [])
    return [normalize_event(t) for t in traces]


def normalize_to_shipment(raw: dict[str, Any]) -> dict[str, Any]:
    data = raw.get("data") or {}
    waybill_no = data.get("waybillNo") or data.get("orderNo")
    if not waybill_no:
        raise ValueError("JDL response missing waybillNo / orderNo")
    events = normalize_response(raw)
    return normalize.shipment(
        tracking_number=waybill_no,
        events=events,
        carrier="jdl",
    )
