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
