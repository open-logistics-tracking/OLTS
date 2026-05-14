# oltrack — OLTS reference implementation

> v0.2.0-dev · Python 3.10+ · Apache 2.0

把承运商原生轨迹响应**归一化**成 [OLTS](https://github.com/open-logistics-tracking/OpenLogisticsTrackingSchema) `TrackingEvent` / `Shipment` 字典。

零运行时依赖。映射数据从仓库的 `ulsc/ulsc.csv` 和 `mappings/*/*.csv` 直接加载。

## 安装

```bash
# 从源码（v0.2 还未发到 PyPI）
git clone https://github.com/open-logistics-tracking/OpenLogisticsTrackingSchema
cd OpenLogisticsTrackingSchema/oltrack-py
pip install -e .[dev]
```

## 快速使用

```python
from oltrack import normalize, UlscCode
from oltrack.adapters import sf

# 1) 直接拿到承运商响应后归一化
raw_response = sf_api.query(tracking_number="SF1234567890")
events = sf.normalize_response(raw_response)
# events 是 list[TrackingEvent dict]，可直接对 OLTS v0.2 schema 校验

# 2) 单事件归一化（手动喂 carrier raw code）
event = normalize.event(
    carrier="sf",
    carrier_event_code="opcode:160",
    event_time="2024-06-04T18:42:11+08:00",
    description="客户签收",
    location={"city": "北京", "countryCode": "CN"},
)
assert event["oltsCode"] == UlscCode.DELIVERED

# 3) 查询某家承运商 raw code 对应的 ULSC
from oltrack.mappings import lookup
print(lookup("sf", "opcode:30"))   # → "picked_up"
print(lookup("dhl", "DLVRD:ACCPT")) # → "delivered"
print(lookup("ups", "F4"))         # → "delivered"
```

## 设计原则

1. **零运行时依赖** — `dependencies = []`。Schema 校验为可选 dev extra。
2. **数据驱动** — `mappings.py` 直接读 `../mappings/*/*.csv`。不内嵌字典常量，CSV 是单一来源。
3. **Adapter-first** — `adapters/{carrier}.py` 一家一个文件。新增承运商 = 加一个文件 + 一行注册。
4. **最小 surface** — 公开 API 只有 3 个入口：`normalize.event()` / `normalize.shipment()` / `mappings.lookup()`。
5. **可选校验** — `oltrack.validate` 模块用 `jsonschema` 库对照 OLTS Schema 校验输出，但不是必须。

## Adapter 覆盖

当前内置：

| Adapter | 文件 | 状态 |
|---|---|---|
| 顺丰 sf | `adapters/sf.py` | ✅ Reference impl |
| DHL | `adapters/dhl.py` | ✅ Reference impl |
| 圆通 yto | `adapters/yto.py` | ✅ MVP |
| 中通 zto | `adapters/zto.py` | ✅ MVP |
| 京东物流 jdl | `adapters/jdl.py` | ✅ MVP |
| UPS | `adapters/ups.py` | ✅ MVP |

剩余 8 家（sto/yunda/ems/jtexpress/cainiao/deppon/fedex/usps）等社区贡献。
模板见 `adapters/sf.py` —— 通常 100-150 行：解析响应、字段重命名、调 `mappings.lookup()` 拿 olts_code、组装 TrackingEvent dict。

## 测试

```bash
cd oltrack-py
pip install -e .[dev]
pytest
```

测试 fixture 用上游仓库的 `examples/v0.2/*.json`（OLTS 官方 example），确保 normalize 输出与 Schema 一致。

## 当前不做

- ❌ 不发起 HTTP 请求（不接管承运商 API 调用）。让消费者用自己的 HTTP client 拿原始响应，传给 adapter normalize
- ❌ 不做签名 / 鉴权 / 限流 / 重试（每家承运商签名算法都不同）
- ❌ 不持久化（无数据库依赖；输入 raw response → 输出字典，由消费者持久化）

这是有意的范围限制：oltrack 只做"格式归一化"，让上下游各自负责自己的部分。
