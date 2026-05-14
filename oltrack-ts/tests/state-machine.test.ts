import { describe, expect, it } from "vitest";
import {
  TERMINAL_CODES,
  TRANSITIONS,
  classify,
  isTerminal,
  isValidTransition,
  nextStates,
  previousStates,
  validateEventSequence,
} from "../src/state-machine.js";

describe("isValidTransition basic", () => {
  it("accepts a normal transition", () => {
    expect(isValidTransition("picked_up", "arrived_at_hub").valid).toBe(true);
  });

  it("rejects a transition out of terminal state", () => {
    const r = isValidTransition("delivered", "picked_up");
    expect(r.valid).toBe(false);
    expect(r.reason).toContain("terminal");
  });

  it("treats same-code repeats as valid", () => {
    const r = isValidTransition("in_transit", "in_transit");
    expect(r.valid).toBe(true);
    expect(r.reason).toContain("same code");
  });

  it("flags unknown from_code", () => {
    const r = isValidTransition("not_real", "delivered");
    expect(r.valid).toBe(false);
    expect(r.reason).toContain("unknown from_code");
  });

  it("flags unknown to_code", () => {
    const r = isValidTransition("picked_up", "not_real");
    expect(r.valid).toBe(false);
    expect(r.reason).toContain("unknown to_code");
  });
});

describe("universal transitions", () => {
  it("any state -> exception is valid", () => {
    expect(isValidTransition("picked_up", "exception").valid).toBe(true);
    expect(isValidTransition("delivered", "exception").valid).toBe(true);
    expect(isValidTransition("out_for_delivery", "damaged").valid).toBe(true);
    expect(isValidTransition("in_transit", "lost").valid).toBe(true);
  });
});

describe("exception-kind transitions", () => {
  it("rejects delivered -> return_initiated without context", () => {
    const r = isValidTransition("delivered", "return_initiated");
    expect(r.valid).toBe(false);
    expect(r.reason.toLowerCase()).toContain("exception");
  });

  it("accepts delivered -> return_initiated with rma context", () => {
    const r = isValidTransition("delivered", "return_initiated", { rma: true });
    expect(r.valid).toBe(true);
  });
});

describe("classification", () => {
  it.each([
    "delivered",
    "returned_to_sender",
    "lost",
    "order_cancelled",
    "signed_by_third_party",
  ])("%s is terminal", (code) => {
    expect(isTerminal(code)).toBe(true);
    expect(classify(code)).toBe("terminal");
  });

  it.each(["damaged", "exception", "refused"])("%s is exceptional", (code) => {
    expect(isTerminal(code)).toBe(false);
    expect(classify(code)).toBe("exceptional");
  });

  it.each(["picked_up", "in_transit", "out_for_delivery"])("%s is active", (code) => {
    expect(classify(code)).toBe("active");
  });
});

describe("nextStates / previousStates", () => {
  it("nextStates includes universal targets", () => {
    const nxt = nextStates("picked_up");
    expect(nxt.has("arrived_at_hub")).toBe(true);
    expect(nxt.has("exception")).toBe(true);
    expect(nxt.has("damaged")).toBe(true);
    expect(nxt.has("lost")).toBe(true);
  });

  it("nextStates excludes self", () => {
    expect(nextStates("picked_up").has("picked_up")).toBe(false);
  });

  it("nextStates of terminal state is universal-only", () => {
    const nxt = nextStates("delivered");
    expect(nxt).toEqual(new Set(["exception", "damaged", "lost"]));
  });

  it("previousStates of delivered includes the obvious paths", () => {
    const prev = previousStates("delivered");
    expect(prev.has("out_for_delivery")).toBe(true);
    expect(prev.has("delivery_to_locker")).toBe(true);
    expect(prev.has("awaiting_pickup")).toBe(true);
  });
});

describe("validateEventSequence", () => {
  it("returns empty for happy path", () => {
    const seq = [
      "order_created",
      "picked_up",
      "arrived_at_hub",
      "departed_from_hub",
      "arrived_at_destination",
      "out_for_delivery",
      "delivered",
    ];
    expect(validateEventSequence(seq)).toEqual([]);
  });

  it("returns empty for cross-border path", () => {
    const seq = [
      "picked_up",
      "arrived_at_hub",
      "customs_declared",
      "customs_held",
      "customs_duty_paid",
      "customs_released",
      "clearance_completed",
      "arrived_at_destination",
      "out_for_delivery",
      "delivered",
    ];
    expect(validateEventSequence(seq)).toEqual([]);
  });

  it("repeated in_transit is allowed", () => {
    const seq = ["picked_up", "in_transit", "in_transit", "in_transit", "arrived_at_destination"];
    expect(validateEventSequence(seq)).toEqual([]);
  });

  it("flags illegal regression and reports index", () => {
    const seq = ["delivered", "picked_up"];
    const invalid = validateEventSequence(seq);
    expect(invalid).toHaveLength(1);
    expect(invalid[0]!.index).toBe(1);
    expect(invalid[0]!.from).toBe("delivered");
    expect(invalid[0]!.to).toBe("picked_up");
  });
});

describe("data integrity", () => {
  it("TRANSITIONS table has the expected shape and count", () => {
    expect(TRANSITIONS.length).toBeGreaterThanOrEqual(60);
    for (const t of TRANSITIONS) {
      expect(t.kind === "normal" || t.kind === "exception" || t.kind === "universal").toBe(true);
    }
  });

  it("TERMINAL_CODES are all in ULSC dictionary", async () => {
    const { ULSC_CODES } = await import("../src/ulsc.js");
    for (const c of TERMINAL_CODES) {
      expect(ULSC_CODES.has(c)).toBe(true);
    }
  });
});
