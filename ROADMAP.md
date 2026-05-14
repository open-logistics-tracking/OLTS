# Roadmap

## v0.1 — 映射表先行（2026-05 ✅ 已完成）

**形态**：状态码字典 + 承运商映射表（CSV）。不写 schema、不写 API spec、不写 SDK。

**交付**：14 家承运商（国内 10 + 国际 4）、14 个映射文件、1761 条 raw status codes、ULSC 32/32 全启用、Python 校验脚本、首发文章草稿。

| 周 | 任务 | 产出 |
|---|---|---|
| W1 | ULSC 字典 v0.1 定稿 + 仓库骨架 | `ulsc/ulsc.csv`（32 码）、`README` / `ROADMAP` / `MAPPING_FORMAT` |
| W2 | 国内 5 家映射 | `mappings/cn/{yto,zto,sf,jdl,ems}.csv` |
| W3 | 国际 4 家映射 | `mappings/intl/{dhl,fedex,ups,usps}.csv`（含清关码验证） |
| W4 | 国内剩余 5 家 + 验证脚本 + 首发文章 | `mappings/cn/{sto,yunda,jtexpress,cainiao,deppon}.csv`、`tools/validate.py`、`posts/why-olts.md` |

## v0.2 — 从映射凝结 Schema（2026 Q3，🚧 启动中）

把 v0.1 在映射中积累的字段共识抽出为 JSON Schema：

- ✅ `TrackingEvent` JSON Schema Draft 1 — [schemas/v0.2/tracking-event.json](./schemas/v0.2/tracking-event.json)
  - 必填: `eventTime` (ISO 8601) + `oltsCode` (ULSC 字典枚举)
  - 可选: `carrierCode` / `carrierEventCode` / `location` (结构化地址含 ISO 3166-1 alpha-2 国家码) /
    `operator` / `pieceId` / `transport` (mode + 车辆号) / `description` (单字符串或多语言字典) /
    `isLogicalEvent` / `notes` / `metadata` (兜底扩展)
- ✅ `Shipment` JSON Schema Draft 1 — [schemas/v0.2/shipment.json](./schemas/v0.2/shipment.json)
  - 必填: `trackingNumber` + `events[]`（≥1 个）
  - 可选: `carrierCode` / `service` / `currentStatus` / `origin` + `destination` (Address with ISO 3166) /
    `estimatedDelivery` (date 或 from-through 窗口) / `actualDelivery` / `pieces[]` (含 weight+dimensions) /
    `weight` / `dimensions` / `declaredValue` (ISO 4217) / `isReturn` / `metadata`
  - `events[].$ref` 引用 tracking-event.json 字典统一
- ✅ Python 参考实现：`oltrack-py`（承运商响应 → OLTS 事件转换器）

示例: [examples/v0.2/](./examples/v0.2/) — 28 个脱敏/合成事件与运单实例。

## v0.5 — API 规范（2026 Q4，✅ 主体完成）

- ✅ `OpenAPI 3.1` 轨迹查询接口骨架 — [openapi/v0.5/tracking.yaml](./openapi/v0.5/tracking.yaml)
  - `GET /tracking/{trackingNumber}` — 返回事件流 (TrackingEvent[])
  - `GET /tracking/{trackingNumber}/shipment` — 返回完整 Shipment 实体
  - `POST /tracking/subscriptions` — 订阅 webhook（签名/重试见配套规范）
  - 响应 schema $ref 到 v0.2 JSON Schema，字典统一
  - 错误响应规范（code + message + 可选 carrier 信息）
- ✅ Webhook 完整化（HMAC-SHA256 签名 + 幂等 + 13 次指数退避 + DLQ）—
  [openapi/v0.5/webhook.md](./openapi/v0.5/webhook.md)
- ✅ AsyncAPI 2.6 spec 互补 — [openapi/v0.5/asyncapi.yaml](./openapi/v0.5/asyncapi.yaml)
- ✅ 数据质量评价框架 4 维度 15 metric — [openapi/v0.5/data-quality.md](./openapi/v0.5/data-quality.md)
- ✅ TypeScript SDK MVP `@oltrack/sdk` — [oltrack-ts/](./oltrack-ts/)
  零依赖 ESM 包，完整 TypeScript 类型 (UlscCode 32 codes union /
  TrackingEvent / Shipment)，sf + dhl MVP adapters，vitest 17 测试

## v1.0 — 稳定版（2027 H1，🚧 准备中）

- ⏳ 规范全面稳定，承诺向后兼容（schema 字段不再破坏性变更）
- ⏳ 多语言 SDK（Python ✅ / TypeScript ✅ / Java ⏳ / Go ⏳ / Rust ⏳）
- ⏳ 申请中物联团体标准立项（T/CFLP）
- ⏳ 建立技术指导委员会（TSC）

### v1.0 准备工作（已启动）

- ✅ ULSC 状态转移图 — [ulsc/state-machine.md](./ulsc/state-machine.md)
  32 码合法转移定义 + Mermaid 可视化 + 校验函数提议（Python/TS）
  + 完整转移矩阵的 v1.0 计划 + 4 个边缘情况说明
- ⏳ `ulsc/transitions.csv` 32×32 矩阵化（自动化 validator 输入）
- ⏳ `oltrack.state_machine` / `@oltrack/sdk/state-machine` 实现
- ⏳ 中物联团体标准立项书草稿

## v2.0+ — 国家标准路径（2028+）

- 推动 GB/T 立项
- 与 GS1 EPCIS / UN/CEFACT / IATA ONE Record 完成互操作映射
