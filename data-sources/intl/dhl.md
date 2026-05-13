# DHL (dhl)

> [`mappings/intl/dhl.csv`](../../mappings/intl/dhl.csv) — 287 raw status codes

## 数据来源

### 1. DHL Tracking Unified API OpenAPI spec

- **URL**: https://developer.dhl.com/api-reference/shipment-tracking
- **抓取日期**: 2026-05
- **内容**: 5 个顶层 StatusCode（pre-transit/transit/delivered/failure/unknown）
- **版权**: 需登录 DHL Developer Portal 获取 spec

### 2. DHL Parcel DE 官方 ICE event/RIC 完整组合表

- **URL**: https://developer.dhl.com
- **抓取日期**: 2026-05
- **内容**: parcel_de_ice_event_ric_combinations_July_2024.csv，282 唯一 event:ric 组合
- **版权**: DHL Parcel DE 官方文档；非商用引用使用

## 重新抓取流程

本 repo 仅在 `mappings/intl/dhl.csv` 中保留映射后的精简数据；原始文档不入库（避免版权/隐私问题及大文件膨胀）。

社区贡献者若要核验或扩展映射，需自行从上述来源重新获取最新文档（多数承运商需登录其开放平台）。

## 数据更新方式

映射 CSV 头部 `# Source:` 注释块已记录原始数据来源、抓取日期、字段命名空间约定。`mappings/intl/dhl.csv` 是事实上的"已经做完归一化"的版本，直接使用即可。
