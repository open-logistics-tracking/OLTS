# @oltrack/sdk — OLTS TypeScript SDK

> v0.5.0-dev · Node.js 18+ · Apache 2.0

把承运商原生轨迹响应**归一化**成 [OLTS](https://github.com/open-logistics-tracking/OpenLogisticsTrackingSchema) `TrackingEvent` / `Shipment`，提供完整 TypeScript 类型。

零运行时依赖。Tree-shaking 友好的 ESM 模块。

## 安装

```bash
# npm
npm install @oltrack/sdk

# pnpm
pnpm add @oltrack/sdk

# yarn
yarn add @oltrack/sdk
```

> 注意: v0.5.0-dev 还未发布到 npm。当前从源码安装：
> ```bash
> git clone https://github.com/open-logistics-tracking/OpenLogisticsTrackingSchema
> cd OpenLogisticsTrackingSchema/oltrack-ts
> npm install && npm run build
> npm link
> ```

## 快速使用

```typescript
import { event, shipment, isValidUlscCode } from "@oltrack/sdk";
import { normalizeResponse, normalizeToShipment } from "@oltrack/sdk/adapters/sf";

// 1) 直接拿到承运商响应后归一化
const events = normalizeResponse(sfApiResponse);
// events 是 TrackingEvent[]，完整 OLTS v0.2 类型

// 2) 单事件构造
const ev = event({
  carrierCode: "sf",
  carrierEventCode: "opcode:160",
  eventTime: "2024-06-04T18:42:11+08:00",
  oltsCode: "delivered",  // 类型受 UlscCode union 约束，IDE 自动补全
});

// 3) 完整运单
const ship = normalizeToShipment(sfApiResponse);
// currentStatus 自动从最后事件的 oltsCode 派生

// 4) 类型守卫
if (isValidUlscCode(maybeCode)) {
  // maybeCode 在这里被收窄成 UlscCode 类型
}
```

## 设计原则

1. **零运行时依赖** — `package.json` 的 `dependencies = {}`
2. **类型完整** — `TrackingEvent` / `Shipment` / 32 个 ULSC codes 全部
   作为字符串字面量 union types，IDE 自动补全 + 编译时检查
3. **Adapter per-carrier** — 一家一文件（`adapters/sf.ts`），按需 import
   不会拉入其他承运商代码（tree-shake 友好）
4. **ESM-only** — 仅发布 ESM (`"type": "module"`)，Node 18+ 原生支持
5. **不发起 HTTP** — 让消费者用自己喜欢的 HTTP client，结果传给 adapter

## Adapter 覆盖

| Adapter | 文件 | 状态 |
|---|---|---|
| 顺丰 sf | `src/adapters/sf.ts` | ✅ MVP（10 个核心 opcode 内联）|
| DHL | `src/adapters/dhl.ts` | ✅ MVP（25 个核心 event:ric 内联）|
| 其他 10 家 | — | ⏳ 等社区贡献 |

每个 adapter 暴露 3 个函数：
- `normalizeEvent(rawItem) → TrackingEvent` (单事件)
- `normalizeResponse(rawApiResponse) → TrackingEvent[]` (完整响应 → 事件数组)
- `normalizeToShipment(rawApiResponse) → Shipment` (完整响应 → 运单对象)

## 构建 & 测试

```bash
npm install
npm run typecheck   # tsc --noEmit
npm run build       # tsc → dist/
npm test            # vitest run
```

预期: 17 个测试全部通过（ulsc 类型守卫 / category / event / shipment auto-derive / sf+dhl adapter 正向 + 错误响应 + 未知码 + shipment 构造）。

## 与 oltrack-py 对比

| 维度 | oltrack-py | @oltrack/sdk |
|---|---|---|
| 数据源 | 运行时读 `mappings/*.csv` | 内联部分常用映射（v0.5 MVP）|
| ULSC enum | Python Enum + frozenset | TypeScript union + Set |
| Adapter | sf + dhl + yto + zto + jdl + ups | sf + dhl（MVP） |
| Schema 校验 | optional jsonschema | 暂无（计划用 [ajv](https://ajv.js.org/)）|
| 测试 | pytest 18 个 | vitest 17 个 |

## v1.0 计划

- 自动从 JSON Schema 生成 TypeScript 类型（`json-schema-to-typescript`）
- 自动从 OpenAPI spec 生成 HTTP client（`openapi-typescript-fetch`）
- 自动从 `mappings/*.csv` 在 build 时生成完整映射常量
- 多承运商 adapter
- ajv schema 校验集成
