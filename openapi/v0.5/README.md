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
| `POST /tracking/subscriptions` | 创建 webhook 订阅 |

## Webhook 推送规范

订阅创建后，OLTS Gateway 通过 HTTPS POST 把事件推到订阅方提供的
`callbackUrl`。完整规范见两份配套文档：

- [`webhook.md`](./webhook.md) — 传输层契约（HMAC-SHA256 签名 / 幂等 /
  指数退避重试 13 次 / DLQ / subscriber 实现建议 + Python/Node.js 验签
  reference impl）
- [`asyncapi.yaml`](./asyncapi.yaml) — AsyncAPI 2.6 消息 schema，定义
  3 个 channel（all / delivered / exception 过滤）+ 必传 headers
  + 引用 v0.2 TrackingEvent JSON Schema

## 与 OLTS v0.2 关系

接口响应 schema 直接 `$ref` 到 `schemas/v0.2/tracking-event.json` 和
`shipment.json`。Schema 更新会自动反映到接口，不需要在两处维护。

Examples 也用 `examples/v0.2/*.json` 的 `externalValue` 引用，避免重复。

## v0.5 剩余工作

- ✅ Webhook 设计完整化（HMAC-SHA256 签名 / 幂等 / 13 次指数退避 / DLQ）—— [webhook.md](./webhook.md)
- ✅ AsyncAPI 2.6 spec for webhook 端（与 OpenAPI 互补）—— [asyncapi.yaml](./asyncapi.yaml)
- ✅ 数据质量评价框架（4 维度 / 15 metric / SQL 示例）—— [data-quality.md](./data-quality.md)
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
