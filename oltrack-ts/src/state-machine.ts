/**
 * ULSC state-machine validator.
 *
 * Transitions are inlined from `ulsc/transitions.csv` (kept in sync manually).
 * Implicit rule: `A → A` (same code) is always valid — carriers commonly emit
 * multiple events with the same code at different hubs.
 */

import type { UlscCode } from "./types.js";
import { ULSC_CODES } from "./ulsc.js";

export type TransitionKind = "normal" | "exception" | "universal";

export interface Transition {
  from: UlscCode | "*";
  to: UlscCode;
  kind: TransitionKind;
  note?: string;
}

/** Terminal states: under normal conditions no further events expected. */
export const TERMINAL_CODES: ReadonlySet<UlscCode> = new Set<UlscCode>([
  "delivered",
  "returned_to_sender",
  "order_cancelled",
  "lost",
  "signed_by_third_party",
]);

/** Exceptional states: may continue or terminate. */
export const EXCEPTIONAL_CODES: ReadonlySet<UlscCode> = new Set<UlscCode>([
  "damaged",
  "exception",
  "refused",
  "address_issue",
  "recipient_unavailable",
  "pickup_failed",
  "delivery_attempted",
  "customs_held",
]);

/** Inlined from ulsc/transitions.csv. Keep ordering identical for diff-ability. */
export const TRANSITIONS: readonly Transition[] = [
  { from: "order_created", to: "label_printed", kind: "normal", note: "生成面单" },
  { from: "order_created", to: "pickup_scheduled", kind: "normal", note: "预约揽收" },
  { from: "order_created", to: "order_cancelled", kind: "normal", note: "交接前取消" },
  { from: "order_created", to: "picked_up", kind: "normal", note: "跳过面单/预约直接揽收" },
  { from: "label_printed", to: "pickup_scheduled", kind: "normal" },
  { from: "label_printed", to: "picked_up", kind: "normal", note: "跳过预约直接揽收" },
  { from: "pickup_scheduled", to: "picked_up", kind: "normal", note: "揽收成功" },
  { from: "pickup_scheduled", to: "pickup_failed", kind: "normal", note: "揽收失败" },
  { from: "pickup_scheduled", to: "order_cancelled", kind: "normal" },
  { from: "pickup_failed", to: "pickup_scheduled", kind: "normal", note: "重新约" },
  { from: "pickup_failed", to: "order_cancelled", kind: "normal", note: "放弃" },
  { from: "picked_up", to: "arrived_at_hub", kind: "normal", note: "首站到件" },
  { from: "picked_up", to: "in_transit", kind: "normal", note: "通用运输态" },
  { from: "picked_up", to: "transferred_to_carrier", kind: "normal", note: "转交末端承运商" },
  { from: "arrived_at_hub", to: "departed_from_hub", kind: "normal" },
  { from: "arrived_at_hub", to: "in_transit", kind: "normal" },
  { from: "arrived_at_hub", to: "customs_declared", kind: "normal", note: "跨境段进入清关" },
  { from: "departed_from_hub", to: "arrived_at_hub", kind: "normal", note: "多 hub 跳跃" },
  { from: "departed_from_hub", to: "arrived_at_destination", kind: "normal", note: "直达目的地" },
  { from: "departed_from_hub", to: "in_transit", kind: "normal" },
  { from: "in_transit", to: "arrived_at_hub", kind: "normal" },
  { from: "in_transit", to: "arrived_at_destination", kind: "normal" },
  { from: "in_transit", to: "transferred_to_carrier", kind: "normal" },
  { from: "transferred_to_carrier", to: "arrived_at_hub", kind: "normal" },
  { from: "transferred_to_carrier", to: "in_transit", kind: "normal" },
  { from: "customs_declared", to: "customs_inspection", kind: "normal" },
  { from: "customs_declared", to: "customs_released", kind: "normal", note: "直接放行" },
  { from: "customs_declared", to: "customs_held", kind: "normal" },
  { from: "customs_inspection", to: "customs_released", kind: "normal" },
  { from: "customs_inspection", to: "customs_held", kind: "normal" },
  { from: "customs_held", to: "customs_duty_paid", kind: "normal", note: "补缴关税" },
  { from: "customs_held", to: "customs_released", kind: "normal", note: "经处理放行" },
  { from: "customs_duty_paid", to: "customs_released", kind: "normal" },
  { from: "customs_released", to: "clearance_completed", kind: "normal" },
  { from: "clearance_completed", to: "in_transit", kind: "normal", note: "清关后续运" },
  { from: "clearance_completed", to: "arrived_at_destination", kind: "normal", note: "清关后即达" },
  { from: "arrived_at_destination", to: "out_for_delivery", kind: "normal" },
  { from: "arrived_at_destination", to: "delivery_to_locker", kind: "normal" },
  { from: "arrived_at_destination", to: "awaiting_pickup", kind: "normal" },
  { from: "out_for_delivery", to: "delivered", kind: "normal", note: "签收" },
  { from: "out_for_delivery", to: "delivery_attempted", kind: "normal" },
  { from: "out_for_delivery", to: "signed_by_third_party", kind: "normal", note: "他人代签" },
  { from: "out_for_delivery", to: "refused", kind: "normal" },
  { from: "out_for_delivery", to: "delivery_to_locker", kind: "normal", note: "改投自提柜" },
  { from: "delivery_attempted", to: "out_for_delivery", kind: "normal", note: "重派" },
  { from: "delivery_attempted", to: "delivery_to_locker", kind: "normal" },
  { from: "delivery_attempted", to: "awaiting_pickup", kind: "normal" },
  { from: "delivery_attempted", to: "recipient_unavailable", kind: "normal" },
  { from: "delivery_attempted", to: "address_issue", kind: "normal" },
  { from: "delivery_attempted", to: "return_initiated", kind: "normal", note: "多次失败启动退回" },
  { from: "delivery_to_locker", to: "awaiting_pickup", kind: "normal" },
  { from: "delivery_to_locker", to: "delivered", kind: "normal", note: "用户取走" },
  { from: "awaiting_pickup", to: "delivered", kind: "normal" },
  { from: "awaiting_pickup", to: "return_initiated", kind: "normal", note: "超时未取" },
  { from: "refused", to: "return_initiated", kind: "normal" },
  { from: "recipient_unavailable", to: "out_for_delivery", kind: "normal", note: "联系上重派" },
  { from: "recipient_unavailable", to: "return_initiated", kind: "normal" },
  { from: "address_issue", to: "out_for_delivery", kind: "normal", note: "改地址重派" },
  { from: "address_issue", to: "return_initiated", kind: "normal" },
  { from: "return_initiated", to: "in_return_transit", kind: "normal" },
  { from: "in_return_transit", to: "returned_to_sender", kind: "normal" },
  { from: "damaged", to: "return_initiated", kind: "normal" },
  { from: "damaged", to: "exception", kind: "normal" },
  { from: "exception", to: "in_transit", kind: "normal", note: "异常解决回主流程" },
  { from: "exception", to: "return_initiated", kind: "normal", note: "异常导致退回" },
  { from: "delivered", to: "return_initiated", kind: "exception", note: "RMA 客户发起退货" },
  { from: "*", to: "exception", kind: "universal", note: "任意态 → 通用异常" },
  { from: "*", to: "damaged", kind: "universal", note: "任意态 → 包裹损坏发现" },
  { from: "*", to: "lost", kind: "universal", note: "任意态 → 包裹丢失发现" },
];

const INDEX = new Map<string, Transition>();
for (const t of TRANSITIONS) {
  INDEX.set(`${t.from} ${t.to}`, t);
}

const UNIVERSAL_TARGETS: ReadonlySet<UlscCode> = new Set<UlscCode>(
  TRANSITIONS.filter((t) => t.from === "*").map((t) => t.to),
);

export function isTerminal(code: string): boolean {
  return TERMINAL_CODES.has(code as UlscCode);
}

export type Classification = "terminal" | "exceptional" | "active";

export function classify(code: string): Classification {
  if (TERMINAL_CODES.has(code as UlscCode)) return "terminal";
  if (EXCEPTIONAL_CODES.has(code as UlscCode)) return "exceptional";
  return "active";
}

export function nextStates(code: string): Set<UlscCode> {
  const out = new Set<UlscCode>();
  for (const t of TRANSITIONS) {
    if (t.from === code && t.kind === "normal") out.add(t.to);
  }
  for (const u of UNIVERSAL_TARGETS) out.add(u);
  return out;
}

export function previousStates(code: string): Set<UlscCode> {
  const out = new Set<UlscCode>();
  for (const t of TRANSITIONS) {
    if (t.to === code && t.kind === "normal" && t.from !== "*") {
      out.add(t.from as UlscCode);
    }
  }
  if (UNIVERSAL_TARGETS.has(code as UlscCode)) {
    for (const c of ULSC_CODES) out.add(c);
  }
  return out;
}

export interface TransitionContext {
  rma?: boolean;
  [key: string]: unknown;
}

export interface ValidationResult {
  valid: boolean;
  reason: string;
}

export function isValidTransition(
  fromCode: string,
  toCode: string,
  context?: TransitionContext,
): ValidationResult {
  if (fromCode === toCode) {
    return { valid: true, reason: "same code repeats are allowed" };
  }
  if (!ULSC_CODES.has(fromCode as UlscCode)) {
    return { valid: false, reason: `unknown from_code: ${fromCode}` };
  }
  if (!ULSC_CODES.has(toCode as UlscCode)) {
    return { valid: false, reason: `unknown to_code: ${toCode}` };
  }

  const direct = INDEX.get(`${fromCode} ${toCode}`);
  if (direct !== undefined) {
    if (direct.kind === "exception") {
      if (!context || Object.keys(context).length === 0) {
        return {
          valid: false,
          reason: `transition ${fromCode} -> ${toCode} is exceptional (${direct.note ?? "requires context"}); pass a context object to mark the exception explicitly`,
        };
      }
      return { valid: true, reason: direct.note ? `exceptional (${direct.note})` : "exceptional" };
    }
    return { valid: true, reason: direct.note ?? "" };
  }

  if (UNIVERSAL_TARGETS.has(toCode as UlscCode)) {
    return { valid: true, reason: `universal target (${toCode})` };
  }

  if (TERMINAL_CODES.has(fromCode as UlscCode)) {
    return { valid: false, reason: `${fromCode} is terminal; cannot transition further` };
  }

  return { valid: false, reason: `no valid transition ${fromCode} -> ${toCode}` };
}

export interface InvalidStep {
  index: number;
  from: string;
  to: string;
  reason: string;
}

export function validateEventSequence(
  codes: readonly string[],
  context?: TransitionContext,
): InvalidStep[] {
  const invalid: InvalidStep[] = [];
  for (let i = 1; i < codes.length; i++) {
    const from = codes[i - 1]!;
    const to = codes[i]!;
    const r = isValidTransition(from, to, context);
    if (!r.valid) invalid.push({ index: i, from, to, reason: r.reason });
  }
  return invalid;
}
