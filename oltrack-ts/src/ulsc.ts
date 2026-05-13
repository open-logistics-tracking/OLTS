import type { UlscCategory, UlscCode } from "./types.js";

/** 32 ULSC v0.1 codes as a frozen set, runtime-checkable. */
export const ULSC_CODES: ReadonlySet<UlscCode> = new Set<UlscCode>([
  "order_created", "order_cancelled", "label_printed",
  "pickup_scheduled", "picked_up", "pickup_failed",
  "arrived_at_hub", "departed_from_hub", "in_transit",
  "transferred_to_carrier", "arrived_at_destination",
  "customs_declared", "customs_held", "customs_inspection",
  "customs_released", "customs_duty_paid", "clearance_completed",
  "out_for_delivery", "delivery_attempted", "delivered",
  "delivery_to_locker", "awaiting_pickup", "signed_by_third_party",
  "exception", "damaged", "lost",
  "address_issue", "recipient_unavailable", "refused",
  "return_initiated", "in_return_transit", "returned_to_sender",
]);

/** Category of each ULSC code. */
export const CATEGORY: Record<UlscCode, UlscCategory> = {
  order_created: "pre_shipment",
  order_cancelled: "pre_shipment",
  label_printed: "pre_shipment",
  pickup_scheduled: "pickup",
  picked_up: "pickup",
  pickup_failed: "pickup",
  arrived_at_hub: "transit",
  departed_from_hub: "transit",
  in_transit: "transit",
  transferred_to_carrier: "transit",
  arrived_at_destination: "transit",
  customs_declared: "customs",
  customs_held: "customs",
  customs_inspection: "customs",
  customs_released: "customs",
  customs_duty_paid: "customs",
  clearance_completed: "customs",
  out_for_delivery: "delivery",
  delivery_attempted: "delivery",
  delivered: "delivery",
  delivery_to_locker: "delivery",
  awaiting_pickup: "delivery",
  signed_by_third_party: "delivery",
  exception: "exception",
  damaged: "exception",
  lost: "exception",
  address_issue: "exception",
  recipient_unavailable: "exception",
  refused: "exception",
  return_initiated: "return",
  in_return_transit: "return",
  returned_to_sender: "return",
};

/** Type guard for runtime validation. */
export function isValidUlscCode(code: string): code is UlscCode {
  return ULSC_CODES.has(code as UlscCode);
}

export function categoryOf(code: UlscCode): UlscCategory {
  return CATEGORY[code];
}
