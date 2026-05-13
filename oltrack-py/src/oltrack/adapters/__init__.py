"""Carrier-specific adapters that parse raw API responses into OLTS events.

Each adapter exposes:

    def normalize_response(raw_response: dict) -> list[dict]:
        '''Parse one carrier API response into a list of TrackingEvent dicts.'''

    def normalize_to_shipment(raw_response: dict) -> dict:
        '''Parse a full response into a Shipment dict (with events[] inside).'''

Currently shipped: sf (顺丰), dhl (DHL).
"""

from oltrack.adapters import sf, dhl

__all__ = ["sf", "dhl"]
