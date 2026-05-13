"""Carrier-specific adapters that parse raw API responses into OLTS events.

Each adapter exposes:

    def normalize_event(item: dict) -> dict:
        '''Parse one event item from the carrier API.'''

    def normalize_response(raw_response: dict) -> list[dict]:
        '''Parse one carrier API response into a list of TrackingEvent dicts.'''

    def normalize_to_shipment(raw_response: dict) -> dict:
        '''Parse a full response into a Shipment dict (with events[] inside).'''

Currently shipped: sf (顺丰), dhl (DHL), yto (圆通), zto (中通),
jdl (京东物流), ups (UPS). Other carriers welcome via PR.
"""

from oltrack.adapters import dhl, jdl, sf, ups, yto, zto

__all__ = ["dhl", "jdl", "sf", "ups", "yto", "zto"]
