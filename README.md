# OLTS — Open Logistics Tracking Schema

> 开放物流轨迹数据规范 · v0.1.0

中国主流快递企业的物流轨迹 API 在字段命名、状态码、签名方式上完全碎片化：对接 3 家以上承运商，技术适配成本就呈指数增长。OLTS 提供一份开放的、由社区维护的统一规范，让上下游系统只需一次对接。

## v0.1 当前状态

v0.1 不是 schema，是一份**状态码字典 + 承运商映射表**。先把碎片化的状态码归一到 32 个统一码上。完整 JSON Schema / OpenAPI 规范在 v0.2 及之后推出（见 [ROADMAP](./ROADMAP.md)）。

```
14 mapping files    1761 raw status codes    12 carriers    ULSC 32/32 used
```

| 交付物 | 状态 |
|---|---|
| ULSC 统一状态码字典（32 个码，7 大类） | ✅ v0.1 |
| 国内承运商映射（10 家） | ✅ 全部完成 |
| 国际承运商映射（4 家，含清关节点） | ✅ 全部完成 |
| 映射格式规范（CSV） | ✅ [MAPPING_FORMAT.md](./MAPPING_FORMAT.md) |
| Python 校验脚本 | ✅ [tools/validate.py](./tools/validate.py) |
| 首发文章草稿 | ✅ [posts/why-olts.md](./posts/why-olts.md) |

## 承运商覆盖

### 国内 10 家

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

### 国际 4 家

| 承运商 | 文件 | raw codes |
|---|---|---:|
| DHL | [`mappings/intl/dhl.csv`](./mappings/intl/dhl.csv) | 287 |
| FedEx | [`mappings/intl/fedex.csv`](./mappings/intl/fedex.csv) | 49 |
| UPS | [`mappings/intl/ups.csv`](./mappings/intl/ups.csv) | 774 |
| USPS | [`mappings/intl/usps.csv`](./mappings/intl/usps.csv) | 145 |

详细进度 / 数据来源见 [`mappings/README.md`](./mappings/README.md)。

## 命名约定

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

## 校验

```bash
python3 tools/validate.py
```

校验所有映射文件的 ULSC 引用合法性、CSV 字段数、carrier_code 唯一性。CI-ready，无第三方依赖。

## 为什么需要这个

项目背景见 3 份调研报告：

- [国内快递开放平台 API 对比分析](./快递企业开放平台API对比分析报告.md)：10 家 API 的认证、字段、状态码全维度对比
- [国际物流轨迹格式调研](./国际物流轨迹格式调研报告.md)：DHL/FedEx/UPS/USPS/IATA/海关清关节点
- [标准空白点分析](./物流轨迹数据规范空白点分析报告.md)：国内外 15+ 标准的覆盖与空白

更长版本见首发文章 [《为什么中国物流需要一个开源轨迹标准》](./posts/why-olts.md)。

## 快速参与

- 看一眼 [ULSC 字典](./ulsc/ulsc.csv)，发现缺码或歧义请提 Issue
- 看 [映射格式规范](./MAPPING_FORMAT.md)，按格式 PR 一家承运商的映射或细化现有映射
- UPS `mappings/intl/ups.csv` 中 426 条规则化分类标"automated rule-based classification; awaiting community review"——社区贡献者可逐条审查 PR 精确映射

## 路线图（节选）

- **v0.1（已完成）**: ULSC 字典 + 12 家承运商映射表 + Python 校验
- **v0.2（2026 Q3）**: 从映射凝结 `TrackingEvent` JSON Schema
- **v0.5（2026 Q4）**: OpenAPI 3.0 轨迹查询/推送接口规范
- **v1.0（2027 H1）**: 稳定版 + 多语言 SDK + 申请中物联团体标准立项

完整 [ROADMAP](./ROADMAP.md)。

## 许可

- 文档与字典数据：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- 代码与工具：[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)

详见 [`LICENSE-DOCS`](./LICENSE-DOCS) 文件级覆盖说明。
