import type { Location, Shipment, TrackingEvent, UlscCode } from "../types.js";
import { event, shipment } from "../normalize.js";

/**
 * Subset of DHL event:ric → UlscCode mapping (from mappings/intl/dhl.csv).
 *
 * v0.5 MVP: inline ~25 most common combinations. v1.0 will auto-generate
 * the full 282-row table at build time.
 */
const DHL_RAW_TO_ULSC: Record<string, UlscCode> = {
  // status:* (top-level statusCode)
  "status:pre-transit": "order_created",
  "status:transit": "in_transit",
  "status:delivered": "delivered",
  "status:failure": "exception",
  "status:unknown": "exception",
  // event:ric — common ones from parcel-de
  "PCKDU:PUBCR": "picked_up",
  "PCKDU:PFLOC": "picked_up",
  "DLVRD:ACCPT": "delivered",
  "DLVRD:ACCDM": "damaged",
  "DLVRD:CUSTM": "customs_declared",
  "DLVRD:NGHBR": "signed_by_third_party",
  "DLVRD:SERPT": "delivery_to_locker",
  "DLVRD:HNDTC": "transferred_to_carrier",
  "DLVRF:NTORD": "refused",
  "DLVRF:DMGED": "damaged",
  "MVARR:NRQRD": "arrived_at_hub",
  "MVDPT:NRQRD": "departed_from_hub",
  "ULFMV:OARRV": "arrived_at_hub",
  "INFCL:NRQRD": "in_transit",
  "INFCL:OARRV": "arrived_at_hub",
  "SRTED:NRQRD": "in_transit",
  "ICPRC:NRQRD": "customs_declared",
  "ICPRC:OARRV": "customs_declared",
  "RSDCP:OARRV": "customs_released",
  "HLDCU:NORSN": "customs_held",
  "CNRFC:HDFCT": "awaiting_pickup",
  "RETRN:RFUSD": "return_initiated",
};

interface DhlAddress {
  addressLocality?: string;
  countryCode?: string;
  postalCode?: string;
}

interface DhlEvent {
  timestamp: string;
  statusCode?: string;
  status?: string;  // 在 events[] 里 status 通常是 event:ric form
  description?: string;
  remark?: string;
  location?: { address?: DhlAddress };
  pieceId?: string;
}

interface DhlShipment {
  trackingNumber: string;
  service?: string;
  origin?: { address?: DhlAddress };
  destination?: { address?: DhlAddress };
  estimatedTimeOfDelivery?: string;
  events?: DhlEvent[];
}

interface DhlResponse {
  shipments?: DhlShipment[];
}


function parseLocation(loc?: { address?: DhlAddress }): Location | undefined {
  if (!loc) return undefined;
  const addr = loc.address ?? {};
  const out: Location = {};
  if (addr.addressLocality) {
    out.name = addr.addressLocality;
    // addressLocality is "CITY - STATE - COUNTRY"; first segment 当 city
    const parts = addr.addressLocality.split("-").map((p) => p.trim());
    if (parts[0]) out.city = parts[0];
  }
  if (addr.countryCode) out.countryCode = addr.countryCode;
  if (addr.postalCode) out.postalCode = addr.postalCode;
  return Object.keys(out).length > 0 ? out : undefined;
}


export function normalizeEvent(ev: DhlEvent): TrackingEvent {
  // Prefer event-level event:ric in `status`, fall back to statusCode 加 "status:" 前缀
  let carrierEventCode: string;
  if (ev.status && ev.status.includes(":")) {
    carrierEventCode = ev.status;
  } else if (ev.statusCode) {
    carrierEventCode = `status:${ev.statusCode}`;
  } else {
    throw new Error("DHL event missing both status and statusCode");
  }

  const oltsCode = DHL_RAW_TO_ULSC[carrierEventCode];
  if (!oltsCode) {
    throw new Error(
      `unknown DHL raw code ${carrierEventCode}; extend DHL_RAW_TO_ULSC or fall back to mappings/intl/dhl.csv lookup`
    );
  }

  return event({
    carrierCode: "dhl",
    carrierEventCode,
    eventTime: ev.timestamp,
    oltsCode,
    description: ev.description ?? ev.remark,
    location: parseLocation(ev.location),
    pieceId: ev.pieceId,
  });
}


export function normalizeResponse(raw: DhlResponse): TrackingEvent[] {
  const shipments = raw.shipments ?? [];
  if (shipments.length === 0) return [];
  const events = shipments[0]!.events ?? [];
  return events.map(normalizeEvent);
}


export function normalizeToShipment(raw: DhlResponse): Shipment {
  const shipments = raw.shipments ?? [];
  if (shipments.length === 0) throw new Error("DHL response has no shipments");
  const sh = shipments[0]!;

  const events = (sh.events ?? []).map(normalizeEvent);
  const origin = sh.origin?.address?.countryCode
    ? { countryCode: sh.origin.address.countryCode }
    : undefined;
  const destination = sh.destination?.address?.countryCode
    ? { countryCode: sh.destination.address.countryCode }
    : undefined;

  return shipment({
    trackingNumber: sh.trackingNumber,
    carrierCode: "dhl",
    events,
    service: sh.service,
    origin,
    destination,
    estimatedDelivery: sh.estimatedTimeOfDelivery,
  });
}
