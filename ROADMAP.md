# Roadmap

## v0.1 — 映射表先行（2026-05 ✅ 已完成）

**形态**：状态码字典 + 承运商映射表（CSV）。不写 schema、不写 API spec、不写 SDK。

**交付**：12 家承运商（国内 10 + 国际 4）、14 个映射文件、1761 条 raw status codes、ULSC 32/32 全启用、Python 校验脚本、首发文章草稿。

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
- ⏳ Python 参考实现：`oltrack-py`（承运商响应 → OLTS 事件转换器）

示例: [examples/v0.2/](./examples/v0.2/) — sf / dhl / usps 三个真实事件实例。

## v0.5 — API 规范（2026 Q4，🚧 启动中）

- ✅ `OpenAPI 3.1` 轨迹查询接口骨架 — [openapi/v0.5/tracking.yaml](./openapi/v0.5/tracking.yaml)
  - `GET /tracking/{trackingNumber}` — 返回事件流 (TrackingEvent[])
  - `GET /tracking/{trackingNumber}/shipment` — 返回完整 Shipment 实体
  - `POST /tracking/subscriptions` — 订阅 webhook（Draft，签名/重试待补）
  - 响应 schema $ref 到 v0.2 JSON Schema，字典统一
  - 错误响应规范（code + message + 可选 carrier 信息）
- ✅ Webhook 完整化（HMAC-SHA256 签名 + 幂等 + 13 次指数退避 + DLQ）—
  [openapi/v0.5/webhook.md](./openapi/v0.5/webhook.md)
- ✅ AsyncAPI 2.6 spec 互补 — [openapi/v0.5/asyncapi.yaml](./openapi/v0.5/asyncapi.yaml)
- ✅ 数据质量评价框架 4 维度 15 metric — [openapi/v0.5/data-quality.md](./openapi/v0.5/data-quality.md)
- ⏳ TypeScript SDK：`@oltrack/sdk` 自动生成

## v1.0 — 稳定版（2027 H1）

- 规范全面稳定，承诺向后兼容
- 多语言 SDK（Python / TypeScript / Java / Go）
- 申请中物联团体标准立项（T/CFLP）
- 建立技术指导委员会（TSC）

## v2.0+ — 国家标准路径（2028+）

- 推动 GB/T 立项
- 与 GS1 EPCIS / UN/CEFACT / IATA ONE Record 完成互操作映射
