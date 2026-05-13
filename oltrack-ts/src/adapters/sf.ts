import type { TrackingEvent, UlscCode } from "../types.js";
import { event, shipment } from "../normalize.js";

/**
 * Subset of SF opcode → UlscCode mapping (from mappings/cn/sf.csv).
 *
 * In v0.5 MVP we inline a partial map for the most common codes. v1.0 will
 * auto-generate the full table from mappings/cn/sf.csv at build time.
 */
const SF_OPCODE_TO_ULSC: Record<string, UlscCode> = {
  "10": "order_created",
  "30": "picked_up",
  "50": "in_transit",
  "60": "arrived_at_hub",
  "70": "departed_from_hub",
  "80": "arrived_at_destination",
  "100": "out_for_delivery",
  "160": "delivered",
  "161": "signed_by_third_party",
  "170": "refused",
};

interface SfRouteResp {
  acceptTime: string;
  acceptAddress?: string;
  remark?: string;
  opcode: string;
  opcodeDesc?: string;
  operatorPhone?: string;
  routeFrom?: string;
  routeTo?: string;
  latitude?: string;
  longitude?: string;
}

interface SfResponse {
  apiResultCode?: string;
  apiErrorMsg?: string;
  msgData?: {
    waybillNo?: string;
    expressStatus?: number;
    routeResps?: SfRouteResp[];
  };
}

const TZ_OFFSET = "+08:00"; // Asia/Shanghai

function parseSfTime(s: string): string {
  // "2024-06-04 18:42:11" → "2024-06-04T18:42:11+08:00"
  return `${s.replace(" ", "T")}${TZ_OFFSET}`;
}

export function normalizeEvent(route: SfRouteResp): TrackingEvent {
  const code = SF_OPCODE_TO_ULSC[route.opcode];
  if (!code) {
    throw new Error(
      `unknown SF opcode ${route.opcode}; extend SF_OPCODE_TO_ULSC or fall back to full mappings/cn/sf.csv lookup`
    );
  }
  const carrierEventCode = `opcode:${route.opcode}`;
  const location = route.acceptAddress ? { name: route.acceptAddress } : undefined;
  const operator = route.operatorPhone ? { phone: route.operatorPhone } : undefined;
  const metadata: Record<string, unknown> = {};
  if (route.routeFrom) metadata.routeFrom = route.routeFrom;
  if (route.routeTo) metadata.routeTo = route.routeTo;

  return event({
    carrierCode: "sf",
    carrierEventCode,
    eventTime: parseSfTime(route.acceptTime),
    oltsCode: code,
    description: route.remark ?? route.opcodeDesc,
    location,
    operator,
    metadata: Object.keys(metadata).length > 0 ? metadata : undefined,
  });
}

export function normalizeResponse(raw: SfResponse): TrackingEvent[] {
  if (raw.apiResultCode !== "A0000") {
    throw new Error(`SF API error: ${raw.apiErrorMsg ?? raw.apiResultCode}`);
  }
  const routes = raw.msgData?.routeResps ?? [];
  return routes.map(normalizeEvent);
}

export function normalizeToShipment(raw: SfResponse) {
  const msg = raw.msgData ?? {};
  if (!msg.waybillNo) throw new Error("SF response missing waybillNo");
  const events = normalizeResponse(raw);
  return shipment({
    trackingNumber: msg.waybillNo,
    carrierCode: "sf",
    events,
    metadata: msg.expressStatus !== undefined ? { expressStatus: msg.expressStatus } : undefined,
  });
}
