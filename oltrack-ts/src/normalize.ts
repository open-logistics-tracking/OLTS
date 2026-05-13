import type { Shipment, TrackingEvent, UlscCode } from "./types.js";

/**
 * Build a TrackingEvent dict from individual fields.
 *
 * The caller MUST supply oltsCode — unlike the Python implementation,
 * the TS SDK doesn't bundle the CSV mappings inline (they live in the
 * repo's mappings/*.csv and would be a build-time dependency).
 *
 * Adapters in `adapters/*` know their carrier's raw_code → olts_code
 * mapping at compile time.
 */
export function event(input: {
  eventTime: string;
  oltsCode: UlscCode;
  carrierCode?: string;
  carrierEventCode?: string;
  description?: string | Record<string, string>;
  location?: TrackingEvent["location"];
  operator?: TrackingEvent["operator"];
  pieceId?: string;
  transport?: TrackingEvent["transport"];
  isLogicalEvent?: boolean;
  notes?: string;
  metadata?: Record<string, unknown>;
}): TrackingEvent {
  const ev: TrackingEvent = {
    eventTime: input.eventTime,
    oltsCode: input.oltsCode,
  };
  if (input.carrierCode) ev.carrierCode = input.carrierCode;
  if (input.carrierEventCode) ev.carrierEventCode = input.carrierEventCode;
  if (input.description) ev.description = input.description;
  if (input.location && Object.keys(input.location).length > 0) ev.location = input.location;
  if (input.operator && Object.keys(input.operator).length > 0) ev.operator = input.operator;
  if (input.pieceId) ev.pieceId = input.pieceId;
  if (input.transport) ev.transport = input.transport;
  if (input.isLogicalEvent) ev.isLogicalEvent = true;
  if (input.notes) ev.notes = input.notes;
  if (input.metadata && Object.keys(input.metadata).length > 0) ev.metadata = input.metadata;
  return ev;
}

/**
 * Build a Shipment dict wrapping a list of events.
 * `currentStatus` auto-derives from last event's oltsCode if not explicitly set.
 */
export function shipment(input: {
  trackingNumber: string;
  events: TrackingEvent[];
  carrierCode?: string;
  service?: string;
  currentStatus?: UlscCode;
  origin?: Shipment["origin"];
  destination?: Shipment["destination"];
  estimatedDelivery?: Shipment["estimatedDelivery"];
  actualDelivery?: string;
  pieces?: Shipment["pieces"];
  weight?: Shipment["weight"];
  dimensions?: Shipment["dimensions"];
  declaredValue?: Shipment["declaredValue"];
  isReturn?: boolean;
  metadata?: Record<string, unknown>;
}): Shipment {
  const ship: Shipment = {
    trackingNumber: input.trackingNumber,
    events: input.events,
  };
  if (input.carrierCode) ship.carrierCode = input.carrierCode;
  if (input.service) ship.service = input.service;
  // Auto-derive currentStatus from last event if not explicitly set
  if (input.currentStatus) {
    ship.currentStatus = input.currentStatus;
  } else if (input.events.length > 0) {
    ship.currentStatus = input.events[input.events.length - 1]!.oltsCode;
  }
  if (input.origin) ship.origin = input.origin;
  if (input.destination) ship.destination = input.destination;
  if (input.estimatedDelivery) ship.estimatedDelivery = input.estimatedDelivery;
  if (input.actualDelivery) ship.actualDelivery = input.actualDelivery;
  if (input.pieces && input.pieces.length > 0) ship.pieces = input.pieces;
  if (input.weight) ship.weight = input.weight;
  if (input.dimensions) ship.dimensions = input.dimensions;
  if (input.declaredValue) ship.declaredValue = input.declaredValue;
  if (input.isReturn) ship.isReturn = true;
  if (input.metadata && Object.keys(input.metadata).length > 0) ship.metadata = input.metadata;
  return ship;
}
