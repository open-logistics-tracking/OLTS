import { describe, expect, it } from "vitest";
import { categoryOf, event, isValidUlscCode, shipment } from "../src/index.js";
import { normalizeResponse, normalizeToShipment } from "../src/adapters/sf.js";

describe("ulsc", () => {
  it("isValidUlscCode accepts known codes", () => {
    expect(isValidUlscCode("delivered")).toBe(true);
    expect(isValidUlscCode("customs_held")).toBe(true);
  });
  it("isValidUlscCode rejects unknown codes", () => {
    expect(isValidUlscCode("not_a_real_code")).toBe(false);
  });
  it("categoryOf returns correct category", () => {
    expect(categoryOf("delivered")).toBe("delivery");
    expect(categoryOf("customs_held")).toBe("customs");
    expect(categoryOf("returned_to_sender")).toBe("return");
  });
});

describe("event()", () => {
  it("builds minimal event", () => {
    const e = event({
      eventTime: "2024-06-04T18:42:11+08:00",
      oltsCode: "delivered",
    });
    expect(e.oltsCode).toBe("delivered");
    expect(e.eventTime).toBe("2024-06-04T18:42:11+08:00");
    expect(e.description).toBeUndefined();
    expect(e.location).toBeUndefined();
  });
  it("omits empty location/operator", () => {
    const e = event({
      eventTime: "2024-06-04T18:42:11+08:00",
      oltsCode: "delivered",
      location: {}, // empty
      operator: {}, // empty
    });
    expect(e.location).toBeUndefined();
    expect(e.operator).toBeUndefined();
  });
});

describe("shipment()", () => {
  it("auto-derives currentStatus from last event", () => {
    const ship = shipment({
      trackingNumber: "SF1234567890",
      events: [
        event({ eventTime: "2024-06-03T09:15:00+08:00", oltsCode: "picked_up" }),
        event({ eventTime: "2024-06-04T18:42:11+08:00", oltsCode: "delivered" }),
      ],
    });
    expect(ship.currentStatus).toBe("delivered");
    expect(ship.events).toHaveLength(2);
  });
  it("explicit currentStatus overrides auto-derive", () => {
    const ship = shipment({
      trackingNumber: "SF1234567890",
      events: [event({ eventTime: "2024-06-04T18:42:11+08:00", oltsCode: "delivered" })],
      currentStatus: "exception",
    });
    expect(ship.currentStatus).toBe("exception");
  });
});

describe("sf adapter", () => {
  it("normalizes a single routeResps[] item", () => {
    const events = normalizeResponse({
      apiResultCode: "A0000",
      msgData: {
        waybillNo: "SF1234567890",
        routeResps: [
          {
            acceptTime: "2024-06-04 18:42:11",
            acceptAddress: "北京朝阳CBD营业部",
            remark: "客户签收",
            opcode: "160",
            operatorPhone: "139****5678",
          },
        ],
      },
    });
    expect(events).toHaveLength(1);
    expect(events[0]!.oltsCode).toBe("delivered");
    expect(events[0]!.eventTime).toBe("2024-06-04T18:42:11+08:00");
    expect(events[0]!.carrierEventCode).toBe("opcode:160");
    expect(events[0]!.location?.name).toBe("北京朝阳CBD营业部");
  });
  it("throws on API error response", () => {
    expect(() =>
      normalizeResponse({ apiResultCode: "E001", apiErrorMsg: "bad sig" })
    ).toThrow(/SF API error/);
  });
  it("throws on unknown opcode", () => {
    expect(() =>
      normalizeResponse({
        apiResultCode: "A0000",
        msgData: {
          waybillNo: "SF1234567890",
          routeResps: [{ acceptTime: "2024-06-04 18:42:11", opcode: "99999" }],
        },
      })
    ).toThrow(/unknown SF opcode/);
  });
  it("normalizeToShipment returns a Shipment", () => {
    const ship = normalizeToShipment({
      apiResultCode: "A0000",
      msgData: {
        waybillNo: "SF1234567890",
        expressStatus: 6,
        routeResps: [
          { acceptTime: "2024-06-03 09:15:00", opcode: "30" },
          { acceptTime: "2024-06-04 18:42:11", opcode: "160" },
        ],
      },
    });
    expect(ship.trackingNumber).toBe("SF1234567890");
    expect(ship.carrierCode).toBe("sf");
    expect(ship.currentStatus).toBe("delivered");
    expect(ship.events).toHaveLength(2);
    expect(ship.metadata?.expressStatus).toBe(6);
  });
});
