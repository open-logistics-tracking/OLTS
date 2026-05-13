/**
 * OLTS v0.2 type definitions.
 *
 * These types are hand-written to match `schemas/v0.2/tracking-event.json`
 * and `shipment.json`. v1.0 plans to auto-generate from JSON Schema; for
 * v0.5 MVP we maintain by hand and keep them in sync via tests against
 * schema/example pairs.
 */

/** 32 ULSC v0.1 codes. Equivalent to UlscCode Enum in oltrack-py. */
export type UlscCode =
  | "order_created"
  | "order_cancelled"
  | "label_printed"
  | "pickup_scheduled"
  | "picked_up"
  | "pickup_failed"
  | "arrived_at_hub"
  | "departed_from_hub"
  | "in_transit"
  | "transferred_to_carrier"
  | "arrived_at_destination"
  | "customs_declared"
  | "customs_held"
  | "customs_inspection"
  | "customs_released"
  | "customs_duty_paid"
  | "clearance_completed"
  | "out_for_delivery"
  | "delivery_attempted"
  | "delivered"
  | "delivery_to_locker"
  | "awaiting_pickup"
  | "signed_by_third_party"
  | "exception"
  | "damaged"
  | "lost"
  | "address_issue"
  | "recipient_unavailable"
  | "refused"
  | "return_initiated"
  | "in_return_transit"
  | "returned_to_sender";

export type UlscCategory =
  | "pre_shipment"
  | "pickup"
  | "transit"
  | "customs"
  | "delivery"
  | "exception"
  | "return";

export type TransportMode = "AIR" | "SEA" | "RAIL" | "ROAD" | "MULTIMODAL" | "UNKNOWN";
export type WeightUnit = "KG" | "LB" | "G" | "OZ";
export type DimensionUnit = "CM" | "IN" | "M" | "MM";

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface Location {
  name?: string;
  city?: string;
  state?: string;
  country?: string;
  /** ISO 3166-1 alpha-2 */
  countryCode?: string;
  postalCode?: string;
  coordinates?: Coordinates;
}

export interface Operator {
  name?: string;
  phone?: string;
  code?: string;
}

export interface Transport {
  mode?: TransportMode;
  vehicleNumber?: string;
  operatingCarrier?: string;
}

/** Localized description by BCP 47 language tag. */
export type LocalizedDescription = Record<string, string>;

/**
 * OLTS v0.2 TrackingEvent.
 *
 * Required: eventTime, oltsCode. All other fields optional — providers
 * fill what they can; consumers handle missing data.
 */
export interface TrackingEvent {
  /** ISO 8601 with timezone offset, e.g. "2024-06-04T18:42:11+08:00" */
  eventTime: string;
  /** Carrier slug matching mappings/ directory (e.g. "sf", "dhl") */
  carrierCode?: string;
  /** Raw event code from carrier API */
  carrierEventCode?: string;
  /** Normalized ULSC code (32 values) */
  oltsCode: UlscCode;
  description?: string | LocalizedDescription;
  location?: Location;
  operator?: Operator;
  pieceId?: string;
  transport?: Transport;
  isLogicalEvent?: boolean;
  notes?: string;
  metadata?: Record<string, unknown>;
}

export interface Weight {
  value: number;
  unit: WeightUnit;
}

export interface Dimensions {
  length: number;
  width: number;
  height: number;
  unit: DimensionUnit;
}

export interface Address {
  name?: string;
  company?: string;
  phone?: string;
  addressLines?: string[];
  city?: string;
  state?: string;
  country?: string;
  /** ISO 3166-1 alpha-2 */
  countryCode?: string;
  postalCode?: string;
}

export interface Piece {
  pieceId: string;
  weight?: Weight;
  dimensions?: Dimensions;
}

export interface DeliveryWindow {
  /** ISO 8601 date-time */
  from: string;
  /** ISO 8601 date-time */
  through: string;
}

export interface DeclaredValue {
  amount: number;
  /** ISO 4217 currency code */
  currency: string;
}

/**
 * OLTS v0.2 Shipment — container with events[].
 *
 * Required: trackingNumber, events (≥1).
 */
export interface Shipment {
  trackingNumber: string;
  carrierCode?: string;
  service?: string;
  currentStatus?: UlscCode;
  origin?: Address;
  destination?: Address;
  /** Either an ISO 8601 date string or a {from, through} window */
  estimatedDelivery?: string | DeliveryWindow;
  /** ISO 8601 date-time */
  actualDelivery?: string;
  pieces?: Piece[];
  events: TrackingEvent[];
  weight?: Weight;
  dimensions?: Dimensions;
  declaredValue?: DeclaredValue;
  isReturn?: boolean;
  metadata?: Record<string, unknown>;
}
