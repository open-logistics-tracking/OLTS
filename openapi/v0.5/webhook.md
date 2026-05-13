# OLTS v0.5 Webhook 设计

> v0.5.0-dev · 待社区评审

OLTS 服务端把承运商推来的事件以 webhook 形式转发给业务订阅方。本文规定
**事件推送**层的契约：签名、幂等、重试、错误处理。

OpenAPI 那边的 `POST /tracking/subscriptions` 只描述"如何创建订阅"；
AsyncAPI ([`asyncapi.yaml`](./asyncapi.yaml)) 描述消息 schema；本文档
描述**传输层和操作语义**——HMAC、retries、DLQ。

## 概览

```
┌──────────┐  raw scan   ┌──────────┐    HMAC+POST    ┌──────────────┐
│ Carrier  ├────────────►│  OLTS    ├────────────────►│ Subscriber   │
│ Push API │             │ Gateway  │ X-OLTS-*        │ callbackUrl  │
└──────────┘             └──────────┘ headers         └──────────────┘
                              │           ▲                  │
                              │           │ 2xx ack          │
                              └───────────┴──── retry on 5xx │
                                          DLQ on max retries │
                                                             ▼
                                                       business
                                                       handler
```

## 推送请求

```http
POST /your-webhook-endpoint HTTP/1.1
Host: subscriber.example.com
Content-Type: application/json
X-OLTS-Event-Id: 01HF8K2X3Z9P4VY7QWERTYUIOP
X-OLTS-Event-Timestamp: 1717488131
X-OLTS-Signature: sha256=4f5a0e7c8b9d2e1f...
X-OLTS-Subscription-Id: sub_1a2b3c4d
X-OLTS-Delivery-Attempt: 1

{
  "eventTime": "2024-06-04T18:42:11+08:00",
  "carrierCode": "sf",
  "carrierEventCode": "opcode:160",
  "oltsCode": "delivered",
  "description": "客户签收",
  "location": { "city": "北京", "countryCode": "CN" }
}
```

Body 是一个 OLTS v0.2 [`TrackingEvent`](../../schemas/v0.2/tracking-event.json)
对象（**单个事件**，不是数组——批量会让重试和顺序变复杂）。

## Headers 规范

| Header | 必填 | 含义 |
|---|---|---|
| `X-OLTS-Event-Id` | ✅ | 全局唯一事件 ID。**幂等键**——subscriber 必须以此去重 |
| `X-OLTS-Event-Timestamp` | ✅ | Unix epoch seconds。早于 now-300s 的应拒绝（防重放） |
| `X-OLTS-Signature` | ✅ | HMAC-SHA256 签名，格式 `sha256=<hex>` |
| `X-OLTS-Subscription-Id` | ✅ | 订阅 ID，方便 subscriber 路由到正确的业务上下文 |
| `X-OLTS-Delivery-Attempt` | ✅ | 1-based 重试次数。1 表示首次投递；最大值见"重试"段 |
| `X-OLTS-Schema-Version` | ❌ | Event body 对应的 OLTS schema 版本（默认 `v0.2`） |

## 签名验证

**算法**：`HMAC-SHA256(secret, timestamp + "." + body)`，hex lowercase。

`secret` 是订阅时双方约定的密钥。`timestamp` 与 body 之间用 `.` 分隔，
防 length-extension。

**示例 (Python)**：

```python
import hmac, hashlib, time

def verify(secret: bytes, body: bytes, timestamp: str, signature: str) -> bool:
    # 1) 防重放
    if abs(int(timestamp) - time.time()) > 300:
        return False
    # 2) HMAC 比较
    payload = timestamp.encode() + b"." + body
    expected = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

**示例 (Node.js)**：

```javascript
import { createHmac, timingSafeEqual } from "crypto";

function verify(secret, body, timestamp, signature) {
  if (Math.abs(parseInt(timestamp) - Date.now() / 1000) > 300) return false;
  const expected = "sha256=" + createHmac("sha256", secret)
    .update(timestamp + "." + body).digest("hex");
  return timingSafeEqual(Buffer.from(expected), Buffer.from(signature));
}
```

## 幂等

**Subscriber 必须以 `X-OLTS-Event-Id` 作为去重键。** 同一 event id 即使
被推送多次（重试 / 网络毛刺导致的 ACK 丢失），业务侧必须只处理一次。

实现常见模式:
- 数据库 unique index on `event_id`
- Redis `SETNX` with TTL（建议 7 天，覆盖最大重试窗口）
- 应用层 idempotency middleware (e.g. `idempotent` Python decorator)

## 响应约定

| 响应 | 含义 | OLTS Gateway 行为 |
|---|---|---|
| `2xx`（含 200/201/202/204） | ACK 成功 | 标记投递成功，不再重试 |
| `4xx`（除 408/429） | Subscriber 永久拒绝 | 不重试。10 分钟内 ≥3 次 4xx 触发**订阅自动暂停**+ 报警通知 |
| `408` `429` | 临时压力 | 按下方"重试"重试 |
| `5xx` | Subscriber 内部错误 | 按下方"重试"重试 |
| 超时（30s 无响应） | 网络问题 | 按下方"重试"重试 |

Subscriber **不应**在 body 中返回数据 — OLTS Gateway 只看状态码。

## 重试

Exponential backoff，base = 2 秒，jitter ±25%。

| 第 N 次重试 | 距上次延迟 | 累计耗时（约） |
|---:|---:|---:|
| 1 (首推) | 0 | 0s |
| 2 | 2s ±25% | ~2s |
| 3 | 4s | ~6s |
| 4 | 8s | ~14s |
| 5 | 16s | ~30s |
| 6 | 32s | ~62s |
| 7 | 64s | ~2 min |
| 8 | 128s (2 min) | ~4 min |
| 9 | 256s (4 min) | ~8 min |
| 10 | 512s (8.5 min) | ~17 min |
| 11 | 1024s (17 min) | ~34 min |
| 12 | 2048s (34 min) | ~68 min |
| 13 (最终) | 4096s (1.1 h) | ~2.2 h |

13 次重试后投递失败，事件进入 DLQ（dead letter queue）等运维处理。

`X-OLTS-Delivery-Attempt` 头部从 1 开始递增，方便 subscriber 看出这是第几次。

## DLQ（Dead Letter Queue）

13 次重试失败后:
- 事件标记为 `dead_letter`，不再自动重试
- 通过订阅控制台 UI / API 可以 **手动重新投递**
- 保留 30 天，之后自动归档
- 报警通知到订阅创建者（邮件或 webhook）

## Subscriber 实现建议

1. **快速 ACK**：webhook 处理函数应在 < 5s 内返回。重活通过消息队列异步处理。
2. **结构化日志**：记录 `X-OLTS-Event-Id` 让追溯定位变方便。
3. **幂等先行**：去重在所有业务逻辑前完成，幂等检查后才进入业务流。
4. **签名时间敏感**：本地时钟偏移 > 5min 会让所有 webhook 被拒；用 NTP 同步。
5. **多 subscription 用统一处理**：`X-OLTS-Subscription-Id` 让一个 endpoint
   能服务多个订阅，再按 sub_id 分发。

## 错误响应（GitHub Webhook 风格的扩展）

无强制要求，但建议 subscriber 4xx 响应携带:

```json
{
  "code": "INVALID_SIGNATURE",
  "message": "X-OLTS-Signature mismatch"
}
```

便于 OLTS Gateway 侧的诊断日志。

## TODO / Open Questions

- [ ] 批量推送支持？目前单事件即正确性高、重试简单；批量需要部分 ACK 协议
- [ ] mTLS 是否补 HMAC？金融级场景需要
- [ ] 推送顺序保证？同一 trackingNumber 的事件是否串行投递？
- [ ] 替换密钥时的 grace period 设计
