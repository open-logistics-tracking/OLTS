# OLTS — Open Logistics Tracking Schema

> 开放物流轨迹数据规范
>
> v0.1.0 ✅ 已发布 · v0.2.0-dev ✅ 主体完成 · v0.5.0-dev 🚧 启动中

中国主流快递企业的物流轨迹 API 在字段命名、状态码、签名方式上完全碎片化：对接 3 家以上承运商，技术适配成本就呈指数增长。OLTS 提供一份开放的、由社区维护的统一规范，让上下游系统只需一次对接。

```
12 carriers   |   14 mapping files   |   1761 raw codes   |   ULSC 32/32 used
2 schemas     |   16 examples         |   oltrack-py MVP   |   OpenAPI 3.1 spec
```

---

## v0.1 — 状态码字典 + 承运商映射表 ✅

把碎片化的状态码归一到 32 个 ULSC 统一码上。覆盖国内 10 家 + 国际 4 家承运商。

| 交付物 | 状态 | 入口 |
|---|---|---|
| ULSC 字典（32 码，7 大类） | ✅ | [ulsc/ulsc.csv](./ulsc/ulsc.csv) |
| 国内 10 家映射 | ✅ | [mappings/cn/](./mappings/cn/) |
| 国际 4 家映射 | ✅ | [mappings/intl/](./mappings/intl/) |
| 映射格式规范 | ✅ | [MAPPING_FORMAT.md](./MAPPING_FORMAT.md) |
| 数据来源元数据 | ✅ | [data-sources/](./data-sources/) |
| CSV 校验脚本 | ✅ | `python3 tools/validate.py` |
| 首发文章 | ✅ | [posts/why-olts.md](./posts/why-olts.md) |

### 承运商覆盖

**国内 10 家** — 10/10 ✅

| 承运商 | 文件 | raw codes |
|---|---|---:|
| 圆通速递 | [`mappings/cn/yto.csv`](./mappings/cn/yto.csv) | 11 |
| 中通快递 | [`mappings/cn/zto.csv`](./mappings/cn/zto.csv) | 24 |
| 申通快递 | [`mappings/cn/sto.csv`](./mappings/cn/sto.csv) | 29 |
| 韵达速递 | [`mappings/cn/yunda.csv`](./mappings/cn/yunda.csv) | 26 |
| 顺丰速运 | [`mappings/cn/sf.csv`](./mappings/cn/sf.csv) | 20 |
| 京东物流 | [`mappings/cn/jdl.csv`](./mappings/cn/jdl.csv) | 75 |
| 中国邮政 | [`mappings/cn/ems.csv`](./mappings/cn/ems.csv) | 237 |
| 极兔速递 | [`mappings/cn/jtexpress.csv`](./mappings/cn/jtexpress.csv) | 46 |
| 菜鸟 | [`mappings/cn/cainiao.csv`](./mappings/cn/cainiao.csv) | 14 |
| 德邦快递 | [`mappings/cn/deppon.csv`](./mappings/cn/deppon.csv) | 24 |

**国际 4 家** — 4/4 ✅

| 承运商 | 文件 | raw codes |
|---|---|---:|
| DHL | [`mappings/intl/dhl.csv`](./mappings/intl/dhl.csv) | 287 |
| FedEx | [`mappings/intl/fedex.csv`](./mappings/intl/fedex.csv) | 49 |
| UPS | [`mappings/intl/ups.csv`](./mappings/intl/ups.csv) | 774 |
| USPS | [`mappings/intl/usps.csv`](./mappings/intl/usps.csv) | 145 |

详细进度 / 数据来源见 [`mappings/README.md`](./mappings/README.md) 和 [`data-sources/`](./data-sources/)。

### ULSC 命名约定

统一码采用 `lowercase_underscore` 风格（OpenAPI / JSON Schema 友好）：

```
order_created            picked_up                arrived_at_hub
departed_from_hub        in_transit               out_for_delivery
delivery_to_locker       awaiting_pickup          delivered
customs_declared         customs_held             customs_released
exception                damaged                  lost
refused                  return_initiated         returned_to_sender
```

7 大类：`pre_shipment` / `pickup` / `transit` / `customs` / `delivery` / `exception` / `return`。完整字典见 [`ulsc/ulsc.csv`](./ulsc/ulsc.csv)。

### 映射校验

```bash
python3 tools/validate.py
```

校验 ULSC 引用合法性、CSV 字段数、carrier_code 唯一性。CI-ready，无第三方依赖。

---

## v0.2 — JSON Schema + Python 参考实现 🚧

从 v0.1 映射经验中凝结字段共识，给出可机器消费的 Schema 和 Python SDK MVP。

| 交付物 | 状态 | 入口 |
|---|---|---|
| `TrackingEvent` JSON Schema Draft 2020-12 | ✅ Draft 1 | [schemas/v0.2/tracking-event.json](./schemas/v0.2/tracking-event.json) |
| `Shipment` JSON Schema Draft 2020-12 | ✅ Draft 1 | [schemas/v0.2/shipment.json](./schemas/v0.2/shipment.json) |
| Examples（事件级，12 家） | ✅ | [examples/v0.2/](./examples/v0.2/)`*-event.json` |
| Examples（运单级，2 家示范） | ✅ | [examples/v0.2/](./examples/v0.2/)`*-shipment.json` |
| Schema 校验工具（含 examples） | ✅ | `python3 tools/validate_schemas.py` |
| Python 参考实现 `oltrack-py` | ✅ MVP | [oltrack-py/](./oltrack-py/) |

### Schemas

**TrackingEvent** — 单个轨迹事件实体：

```json
{
  "eventTime": "2024-06-04T18:42:11+08:00",
  "carrierCode": "sf",
  "carrierEventCode": "opcode:160",
  "oltsCode": "delivered",
  "description": "客户签收",
  "location": { "city": "北京", "countryCode": "CN" },
  "operator": { "name": "李师傅", "phone": "139****5678" }
}
```

**Shipment** — 运单容器（含 events[]、origin、destination、pieces 等）：

```json
{
  "trackingNumber": "SF1234567890",
  "carrierCode": "sf",
  "service": "顺丰特快",
  "currentStatus": "delivered",
  "origin": { "city": "上海", "countryCode": "CN" },
  "destination": { "city": "北京", "countryCode": "CN" },
  "events": [ /* TrackingEvent[] */ ]
}
```

设计原则见 [`schemas/v0.2/README.md`](./schemas/v0.2/README.md)。

### Python 参考实现 `oltrack-py`

零运行时依赖。映射数据从 `mappings/*/*.csv` 直接加载。

```python
from oltrack import normalize, lookup, UlscCode
from oltrack.adapters import sf, dhl

# 把承运商响应归一化成 TrackingEvent dicts
events = sf.normalize_response(sf_raw_response)

# 单事件归一化
event = normalize.event(
    carrier="sf",
    carrier_event_code="opcode:160",
    event_time="2024-06-04T18:42:11+08:00",
)
assert event["oltsCode"] == UlscCode.DELIVERED

# 查表
assert lookup("sf", "opcode:30") == "picked_up"
assert lookup("ups", "F4") == "delivered"
```

完整指南：[`oltrack-py/README.md`](./oltrack-py/README.md)

**当前 adapter 覆盖**：

| Adapter | 文件 | 状态 |
|---|---|---|
| 顺丰 sf | `oltrack-py/src/oltrack/adapters/sf.py` | ✅ Reference impl |
| DHL | `oltrack-py/src/oltrack/adapters/dhl.py` | ✅ Reference impl |
| 其他 10 家（yto/zto/sto/yunda/jdl/ems/jtexpress/cainiao/deppon/fedex/ups/usps） | — | ⏳ 等社区贡献 |

```bash
cd oltrack-py
python3 -m pytest tests/ -v   # 12 passed
```

### Schema 校验

```bash
python3 tools/validate_schemas.py
# OK — all 2 schemas + 16 examples valid
```

---


## v0.5 — HTTP 接口规范 🚧

把 OLTS 归一化数据通过 HTTP 暴露给上游消费者。OpenAPI 3.1 spec，响应 schema $ref 到 v0.2 JSON Schemas。

| 交付物 | 状态 | 入口 |
|---|---|---|
| OpenAPI 3.1 接口骨架 | ✅ Draft | [openapi/v0.5/tracking.yaml](./openapi/v0.5/tracking.yaml) |
| Webhook 签名 + 幂等 + 重试 | ⏳ | — |
| AsyncAPI 2.x 互补 spec | ⏳ | — |
| 数据质量评价框架 | ⏳ | — |
| TypeScript SDK 自动生成 | ⏳ | — |

定义 3 个接口（详见 [`openapi/v0.5/README.md`](./openapi/v0.5/README.md)）:

- `GET /tracking/{trackingNumber}` — 事件流（轻量）
- `GET /tracking/{trackingNumber}/shipment` — 完整 Shipment 实体
- `POST /tracking/subscriptions` — Webhook 订阅（Draft）

范围声明: v0.5 只规范"消费方接口"。承运商接入侧的鉴权 / 签名 / 限流由实现方包；服务端实现 OLTS 不提供 reference。

---

## 为什么需要这个

项目背景见 3 份调研报告：

- [国内快递开放平台 API 对比分析](./快递企业开放平台API对比分析报告.md)：10 家 API 的认证、字段、状态码全维度对比
- [国际物流轨迹格式调研](./国际物流轨迹格式调研报告.md)：DHL/FedEx/UPS/USPS/IATA/海关清关节点
- [标准空白点分析](./物流轨迹数据规范空白点分析报告.md)：国内外 15+ 标准的覆盖与空白

更长版本见首发文章 [《为什么中国物流需要一个开源轨迹标准》](./posts/why-olts.md)。

## 快速参与

- **提 ULSC 字典 Issue**：发现缺码或歧义？看 [`ulsc/ulsc.csv`](./ulsc/ulsc.csv) 后提 Issue
- **PR 一家承运商映射**：按 [`MAPPING_FORMAT.md`](./MAPPING_FORMAT.md) 写 CSV，欢迎细化或新增
- **审查 UPS 异常细化**：[`mappings/intl/ups.csv`](./mappings/intl/ups.csv) 中 346 条规则化分类标 `automated rule-based classification; awaiting community review`——逐条 spot review PR 友好
- **写 oltrack-py adapter**：模板见 [`oltrack-py/src/oltrack/adapters/sf.py`](./oltrack-py/src/oltrack/adapters/sf.py)，10 家剩余承运商各 80-120 行可搞定
- **OLTS 适配验证**：拿真实运单跑 oltrack-py + schema 校验，反馈不对的映射

## Repo 结构

```
ulsc/                    32 码字典定稿
mappings/                12 家承运商 raw_code → ULSC 映射 CSV
schemas/v0.2/            JSON Schema (TrackingEvent + Shipment)
examples/v0.2/           17 个 Schema 实例（覆盖 12 家）
oltrack-py/              Python 参考实现（零运行时依赖）
openapi/v0.5/            OpenAPI 3.1 接口规范
tools/                   validate.py (CSV) + validate_schemas.py (JSON Schema)
data-sources/            12 家承运商来源元数据 + 版权归属
posts/                   首发文章 + 后续文档
快递企业开放平台API对比分析报告.md     初期调研：国内 10 家
国际物流轨迹格式调研报告.md             初期调研：国际 + 清关节点
物流轨迹数据规范空白点分析报告.md       初期调研：标准空白点
```

## 路线图（节选）

- **v0.1（已完成）**: ULSC 字典 + 12 家承运商映射表 + Python 校验
- **v0.2（主体完成）**: TrackingEvent + Shipment JSON Schema + oltrack-py MVP
- **v0.5（启动中）**: OpenAPI 3.1 接口规范骨架；Webhook/AsyncAPI/SDK 待补
- **v1.0（2027 H1）**: 稳定版 + 多语言 SDK + 申请中物联团体标准立项

完整 [ROADMAP](./ROADMAP.md)。

## 许可

- 文档、字典数据、映射 CSV：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- 代码、Python 实现、校验脚本、Schema：[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)

详见 [`LICENSE-DOCS`](./LICENSE-DOCS) 文件级覆盖说明。
