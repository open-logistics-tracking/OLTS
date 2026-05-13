# Roadmap

## v0.1 — 映射表先行（2026-05 → 2026-06）

**形态**：状态码字典 + 承运商映射表（CSV）。不写 schema、不写 API spec、不写 SDK。

| 周 | 任务 | 产出 |
|---|---|---|
| W1 | ULSC 字典 v0.1 定稿 + 仓库骨架 | `ulsc/ulsc.csv`（32 码）、`README` / `ROADMAP` / `MAPPING_FORMAT` |
| W2 | 国内 5 家映射 | `mappings/cn/{yto,zto,sf,jdl,ems}.csv` |
| W3 | 国际 4 家映射 | `mappings/intl/{dhl,fedex,ups,usps}.csv`（含清关码验证） |
| W4 | 国内剩余 5 家 + 验证脚本 + 首发文章 | `mappings/cn/{sto,yunda,jtexpress,cainiao,deppon}.csv`、`tools/validate.py`、`posts/why-olts.md` |

## v0.2 — 从映射凝结 Schema（2026 Q3）

把 W2–W4 在映射中积累的字段共识抽出为 JSON Schema：

- `TrackingEvent` JSON Schema（事件实体）
- `Shipment` JSON Schema（运单实体）
- 时间字段：ISO 8601 + 时区偏移强制
- 地址字段：ISO 3166-1 alpha-2 国家码 + 行政区 + 自由文本
- Python 参考实现：`oltrack-py`（承运商响应 → OLTS 事件）

## v0.5 — API 规范（2026 Q4）

- OpenAPI 3.0 轨迹查询接口（`GET /tracking/{tracking_number}`）
- 订阅/推送接口（Webhook + AsyncAPI）
- 数据质量评价框架（完整度 / 时效性 / 一致性）
- TypeScript SDK：`@oltrack/sdk`

## v1.0 — 稳定版（2027 H1）

- 规范全面稳定，承诺向后兼容
- 多语言 SDK（Python / TypeScript / Java / Go）
- 申请中物联团体标准立项（T/CFLP）
- 建立技术指导委员会（TSC）

## v2.0+ — 国家标准路径（2028+）

- 推动 GB/T 立项
- 与 GS1 EPCIS / UN/CEFACT / IATA ONE Record 完成互操作映射
