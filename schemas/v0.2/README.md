# OLTS v0.2 Schemas

JSON Schema 实体定义，从 v0.1 mapping 经验中凝结。

## 现状

| Schema | 文件 | 状态 |
|---|---|---|
| `TrackingEvent` | [tracking-event.json](./tracking-event.json) | ✅ Draft 1 |
| `Shipment`      | (planned)                                    | ⏳ 计划中 |

## 设计原则

### 1. 最小必填、最大可选

`TrackingEvent` 只要求 `eventTime` 和 `oltsCode` 两个字段。其他字段全部可选——让承运商按能力提供，让消费方按需消费。

### 2. ULSC 字典作为枚举

`oltsCode` 字段用 `$defs/UlscCode` 引用，强制必须是 ULSC 32 码之一。字典定义在 [ulsc/ulsc.csv](../../ulsc/ulsc.csv)。

未来字典扩展（v0.2+ 新增码），schema 同步更新 enum。

### 3. 时间强制 ISO 8601 + 时区

`eventTime` 用 `format: date-time`。但实际国内承运商时间多无时区——消费方 SHOULD 在接收时附加承运商所在时区，例如：

```python
# 顺丰返回 "2024-06-03 11:38:00"
parsed = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")
parsed = parsed.replace(tzinfo=ZoneInfo("Asia/Shanghai"))
event["eventTime"] = parsed.isoformat()  # "2024-06-03T11:38:00+08:00"
```

### 4. 地址结构化但可降级

`location` 全部子字段可选。承运商只返回"江苏省南京市玄武区"自由文本时，把它放进 `location.city`/`state`，不强求 ISO 3166 国家码。

### 5. piece-level vs shipment-level

DHL/UPS API 支持子包裹级事件，国内承运商基本是整票级。`pieceId` 字段可选——存在时表示该事件属于某个 piece，不存在时是 shipment-level event。

### 6. 多语言描述

`description` 接受单字符串或 BCP 47 语言 tag 字典。早期场景多数是中文单字符串，跨境业务用字典形态：

```json
{
  "description": {
    "zh": "您的快件已离开上海浦东国际机场",
    "en": "Your shipment has departed from Shanghai Pudong International Airport"
  }
}
```

### 7. metadata 逃生舱

`metadata: { additionalProperties: true }` 故意允许任意扩展字段。让消费方写 metadata 兜底而非污染顶层 schema。

## 校验

```bash
pip install jsonschema
python3 -c "
import json
from jsonschema import Draft202012Validator
schema = json.load(open('schemas/v0.2/tracking-event.json'))
Draft202012Validator.check_schema(schema)
print('Schema valid')
"
```

实例校验：

```python
from jsonschema import validate
validate(instance=event_obj, schema=schema)
```

## examples/

参见 [examples/v0.2/](../../examples/v0.2/) — 3 个真实事件实例覆盖国内、国际、清关、签收等典型场景。

## 路线

- v0.2: `TrackingEvent` ✅ + `Shipment` ⏳
- v0.5: 含 schema 的 OpenAPI 3.0 接口规范
- v1.0: 稳定版，承诺向后兼容

完整见 [ROADMAP.md](../../ROADMAP.md)。
