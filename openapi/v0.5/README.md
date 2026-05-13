# OLTS v0.5 OpenAPI 接口规范

> v0.5.0-dev · OpenAPI 3.1 · Apache 2.0

`tracking.yaml` 是 OLTS 的**消费方接口**规范——聚合平台、品牌中台、SaaS
厂商可以**对外暴露**这套接口，让自己的客户用统一字段消费 OLTS 归一化后
的轨迹数据。

## 范围

✅ 规范的:
- 查询接口的 URL、方法、参数、响应字段
- 响应数据用 OLTS v0.2 TrackingEvent / Shipment Schema（字典统一）
- 错误响应的结构（code + message + 可选 carrier 信息）
- Webhook 订阅的最小请求形态

❌ 不规范的:
- 上游承运商接入侧的鉴权 / 签名 / 限流（每家不一样，让消费者自己包）
- 服务端实现（OLTS 不提供 reference server；社区可以自行实现）
- 鉴权方案（用 Bearer Token / OAuth 2.0 / API Key 由实现方选）

## 接口

| 接口 | 用途 |
|---|---|
| `GET /tracking/{trackingNumber}` | 返回事件流（轻量，适合主页 timeline 展示） |
| `GET /tracking/{trackingNumber}/shipment` | 返回完整 Shipment 实体（含 origin/destination/pieces） |
| `POST /tracking/subscriptions` | 订阅 webhook 推送（v0.5 Draft，签名/重试待补） |

## 与 OLTS v0.2 关系

接口响应 schema 直接 `$ref` 到 `schemas/v0.2/tracking-event.json` 和
`shipment.json`。Schema 更新会自动反映到接口，不需要在两处维护。

Examples 也用 `examples/v0.2/*.json` 的 `externalValue` 引用，避免重复。

## v0.5 剩余工作

- ⏳ Webhook 设计完整化：签名（HMAC-SHA256）+ 幂等 + 重试退避策略
- ⏳ AsyncAPI 2.x spec for webhook 端（与 OpenAPI 互补）
- ⏳ 数据质量评价框架（完整度 / 时效性 / 一致性 metrics）
- ⏳ TypeScript SDK `@oltrack/sdk` 自动生成

## 校验

```bash
# 用 openapi-spec-validator
pip install openapi-spec-validator
openapi-spec-validator openapi/v0.5/tracking.yaml

# 或用 Swagger Editor / Redocly CLI 浏览预览
npx @redocly/cli preview-docs openapi/v0.5/tracking.yaml
```

## 路线

v0.5 spec 稳定后:
- 接入 OLTS reference server 项目（在独立 repo 维护）
- 自动生成多语言客户端 SDK（TypeScript / Python / Go / Java）
- 与 v1.0 OAS 一起申请中物联团体标准对接
