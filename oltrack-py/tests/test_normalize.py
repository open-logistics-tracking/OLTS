"""End-to-end normalization tests using upstream OLTS v0.2 examples."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from oltrack import UlscCategory, UlscCode, lookup, normalize
from oltrack.adapters import dhl, sf
from oltrack.ulsc import ALL_CODES, category_of, is_valid, reload_from_csv

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "examples" / "v0.2"


def test_ulsc_dict_matches_csv():
    """Hardcoded ULSC enum must match ulsc/ulsc.csv exactly (drift detector)."""
    csv_codes = reload_from_csv(REPO_ROOT / "ulsc" / "ulsc.csv")
    assert csv_codes == ALL_CODES


def test_is_valid_and_category():
    assert is_valid("delivered")
    assert is_valid("customs_held")
    assert not is_valid("not_a_real_code")
    assert category_of("delivered") == UlscCategory.DELIVERY
    assert category_of(UlscCode.CUSTOMS_HELD) == UlscCategory.CUSTOMS


def test_lookup_known_codes():
    assert lookup("sf", "opcode:30") == "picked_up"
    assert lookup("sf", "opcode:160") == "delivered"
    assert lookup("dhl", "DLVRD:ACCPT") == "delivered"
    assert lookup("ups", "F4") == "delivered"
    assert lookup("yto", "GOT") == "picked_up"


def test_lookup_unknown_raises():
    with pytest.raises(KeyError):
        lookup("sf", "nonexistent_code")


def test_normalize_event_minimal():
    e = normalize.event(
        carrier="sf",
        carrier_event_code="opcode:160",
        event_time="2024-06-04T18:42:11+08:00",
    )
    assert e["oltsCode"] == "delivered"
    assert e["carrierCode"] == "sf"
    assert e["eventTime"] == "2024-06-04T18:42:11+08:00"
    # Optional fields not set
    assert "description" not in e
    assert "location" not in e


def test_normalize_event_full():
    e = normalize.event(
        carrier="dhl",
        carrier_event_code="DLVRD:ACCPT",
        event_time="2024-06-04T03:17:00+02:00",
        description="Delivered",
        location={"city": "Frankfurt", "countryCode": "DE"},
    )
    assert e["oltsCode"] == "delivered"
    assert e["location"]["countryCode"] == "DE"


def test_normalize_event_explicit_code_overrides_mapping():
    """Caller can override the auto-derived olts_code."""
    e = normalize.event(
        carrier="sf",
        carrier_event_code="opcode:160",
        event_time="2024-06-04T18:42:11+08:00",
        olts_code="signed_by_third_party",  # explicit override
    )
    assert e["oltsCode"] == "signed_by_third_party"


def test_sf_adapter_normalize_response():
    raw = {
        "apiResultCode": "A0000",
        "msgData": {
            "waybillNo": "SF1234567890",
            "expressStatus": 6,
            "routeResps": [
                {
                    "acceptTime": "2024-06-04 18:42:11",
                    "acceptAddress": "北京朝阳CBD营业部",
                    "remark": "客户签收",
                    "opcode": "160",
                    "operatorPhone": "139****5678",
                }
            ],
        },
    }
    events = sf.normalize_response(raw)
    assert len(events) == 1
    assert events[0]["oltsCode"] == "delivered"
    assert events[0]["eventTime"] == "2024-06-04T18:42:11+08:00"
    assert events[0]["carrierEventCode"] == "opcode:160"
    assert events[0]["location"]["name"] == "北京朝阳CBD营业部"


def test_sf_adapter_error_response():
    with pytest.raises(ValueError):
        sf.normalize_response({"apiResultCode": "E001", "apiErrorMsg": "bad sig"})


def test_dhl_adapter_normalize_response():
    raw = {
        "shipments": [{
            "trackingNumber": "0034988765432",
            "service": "express",
            "origin": {"address": {"countryCode": "CN"}},
            "destination": {"address": {"countryCode": "DE"}},
            "events": [
                {
                    "timestamp": "2024-06-04T03:17:00+02:00",
                    "statusCode": "transit",
                    "status": "DLVRD:CUSTM",
                    "description": "Handed over to customs",
                    "location": {"address": {"addressLocality": "Frankfurt", "countryCode": "DE"}},
                }
            ],
        }],
    }
    events = dhl.normalize_response(raw)
    assert len(events) == 1
    assert events[0]["oltsCode"] == "customs_declared"
    assert events[0]["location"]["countryCode"] == "DE"


def test_dhl_normalize_to_shipment_currentStatus_derived():
    """Shipment.currentStatus should auto-derive from last event's oltsCode."""
    raw = {
        "shipments": [{
            "trackingNumber": "TEST123",
            "service": "express",
            "events": [
                {"timestamp": "2024-06-01T10:00:00Z", "status": "PCKDU:PUBCR"},
                {"timestamp": "2024-06-04T03:17:00+02:00", "status": "DLVRD:ACCPT"},
            ],
        }],
    }
    shipment_dict = dhl.normalize_to_shipment(raw)
    assert shipment_dict["currentStatus"] == "delivered"
    assert len(shipment_dict["events"]) == 2


def test_validate_against_schema_optional():
    """If jsonschema is installed, output should validate against v0.2 schema."""
    pytest.importorskip("jsonschema")
    pytest.importorskip("referencing")
    from jsonschema import Draft202012Validator
    from referencing import Registry
    from referencing.jsonschema import DRAFT202012

    schema = json.loads((REPO_ROOT / "schemas" / "v0.2" / "tracking-event.json").read_text())
    ship_schema = json.loads((REPO_ROOT / "schemas" / "v0.2" / "shipment.json").read_text())
    registry = Registry().with_resources([
        ("tracking-event.json", DRAFT202012.create_resource(schema)),
        (schema["$id"], DRAFT202012.create_resource(schema)),
        ("shipment.json", DRAFT202012.create_resource(ship_schema)),
        (ship_schema["$id"], DRAFT202012.create_resource(ship_schema)),
    ])

    e = normalize.event(
        carrier="sf",
        carrier_event_code="opcode:30",
        event_time="2024-06-03T09:15:00+08:00",
        description="揽收成功",
    )
    Draft202012Validator(schema, registry=registry).validate(e)


# ---- New adapters: yto / zto / jdl / ups ----

def test_yto_adapter():
    from oltrack.adapters import yto
    raw = {
        "param": [
            {
                "waybill_No": "YT123456789",
                "upload_Time": "2024-06-04 18:42:11",
                "infoContent": "SIGNED",
                "processInfo": "客户签收",
                "city": "北京",
                "district": "朝阳区",
                "weight": 1.5,
            }
        ]
    }
    events = yto.normalize_response(raw)
    assert len(events) == 1
    assert events[0]["oltsCode"] == "delivered"
    assert events[0]["carrierEventCode"] == "SIGNED"
    assert events[0]["eventTime"] == "2024-06-04T18:42:11+08:00"
    assert events[0]["location"]["city"] == "北京"
    assert events[0]["metadata"]["weight"] == 1.5

    ship = yto.normalize_to_shipment(raw)
    assert ship["trackingNumber"] == "YT123456789"
    assert ship["currentStatus"] == "delivered"


def test_zto_adapter():
    from oltrack.adapters import zto
    # ZTO uses ms epoch for scanDate
    raw = {
        "status": True,
        "message": "请求成功",
        "result": [
            {
                "billCode": "73100059800035",
                "scanType": "签收",
                "scanDate": 1676429769000,  # 2023-02-15 02:56:09 UTC
                "scanSite": {"name": "金华浦江县", "city": "金华", "prov": "浙江"},
                "signMan": "李四",
                "desc": "客户签收",
            }
        ]
    }
    events = zto.normalize_response(raw)
    assert len(events) == 1
    assert events[0]["oltsCode"] == "delivered"
    assert events[0]["carrierEventCode"] == "签收"
    # ZTO ms epoch parsed to UTC
    assert events[0]["eventTime"].startswith("2023-02-15T")
    assert events[0]["location"]["name"] == "金华浦江县"
    assert events[0]["metadata"]["signMan"] == "李四"


def test_zto_adapter_error():
    from oltrack.adapters import zto
    with pytest.raises(ValueError, match="ZTO API error"):
        zto.normalize_response({"status": False, "statusCode": "E403", "message": "参数校验失败"})


def test_jdl_adapter():
    from oltrack.adapters import jdl
    raw = {
        "code": "1000",
        "data": {
            "waybillNo": "JD0123456789",
            "traces": [
                {
                    "state": 200001,
                    "operationTitle": "配送员完成揽收",
                    "operationTime": "2024-06-03 11:05:00",
                    "operationRemark": "客户在前台",
                    "city": "北京",
                    "operatorPhone": "186****1234",
                    "category": 420,
                }
            ],
        },
    }
    events = jdl.normalize_response(raw)
    assert len(events) == 1
    assert events[0]["oltsCode"] == "picked_up"
    assert events[0]["carrierEventCode"] == "state:200001"
    assert events[0]["eventTime"] == "2024-06-03T11:05:00+08:00"
    assert events[0]["metadata"]["status"] == 420

    ship = jdl.normalize_to_shipment(raw)
    assert ship["trackingNumber"] == "JD0123456789"


def test_jdl_adapter_error():
    from oltrack.adapters import jdl
    with pytest.raises(ValueError, match="JDL API error"):
        jdl.normalize_response({"code": "2001", "message": "没有权限"})


def test_ups_adapter():
    from oltrack.adapters import ups
    raw = {
        "trackResponse": {
            "shipment": [{
                "package": [{
                    "trackingNumber": "1Z999AA10123456784",
                    "service": {"description": "UPS Ground"},
                    "weight": {"weight": "5.5", "unitOfMeasurement": "LBS"},
                    "activity": [
                        {
                            "date": "20240612",
                            "time": "183000",
                            "gmtDate": "20240612",
                            "gmtTime": "230000",
                            "gmtOffset": "-04:00",
                            "location": {
                                "address": {
                                    "city": "Atlanta",
                                    "stateProvince": "GA",
                                    "country": "US",
                                    "postalCode": "30303"
                                }
                            },
                            "status": {
                                "code": "F4",
                                "description": "Package/shipment delivered",
                                "statusCode": "011",
                                "type": "D"
                            }
                        }
                    ]
                }]
            }]
        }
    }
    events = ups.normalize_response(raw)
    assert len(events) == 1
    assert events[0]["oltsCode"] == "delivered"
    assert events[0]["carrierEventCode"] == "F4"
    assert events[0]["eventTime"] == "2024-06-12T23:00:00-04:00"
    assert events[0]["location"]["countryCode"] == "US"
    assert events[0]["metadata"]["statusCode"] == "011"

    ship = ups.normalize_to_shipment(raw)
    assert ship["trackingNumber"] == "1Z999AA10123456784"
    assert ship["service"] == "UPS Ground"
    assert ship["weight"]["value"] == 5.5
    assert ship["weight"]["unit"] == "LB"
