# FedEx (fedex)

> [`mappings/intl/fedex.csv`](../../mappings/intl/fedex.csv) — 49 raw status codes

## 数据来源

### 1. Shopify active_shipping FedEx TRACKING_STATUS_CODES

- **URL**: https://github.com/Shopify/active_shipping/blob/master/lib/active_shipping/carriers/fedex.rb
- **抓取日期**: 2026-05
- **内容**: 30 个核心 ScanEvent 2 字母事件码（AA/AD/AF/AR/AP/CA/CH/DE/DL/DP/DR/DS/DY/EA/ED/EO/EP/FD/HL/IT/LO/OC/OD/PF/PL/PU/RS/SE/SF/SP/TR）
- **版权**: Apache 2.0（active_shipping 开源库）

### 2. FedEx Track API OpenAPI 3.0 spec

- **URL**: https://developer.fedex.com/api/en-us/catalog/track/docs.html
- **抓取日期**: 2026-05
- **内容**: 14 个 ServiceCommitMessage.type + 4 个 notificationEventTypes（commit:* / notif:* 前缀）
- **版权**: 需登录 FedEx Developer Portal

## 重新抓取流程

本 repo 仅在 `mappings/intl/fedex.csv` 中保留映射后的精简数据；原始文档不入库（避免版权/隐私问题及大文件膨胀）。

社区贡献者若要核验或扩展映射，需自行从上述来源重新获取最新文档（多数承运商需登录其开放平台）。

## 数据更新方式

映射 CSV 头部 `# Source:` 注释块已记录原始数据来源、抓取日期、字段命名空间约定。`mappings/intl/fedex.csv` 是事实上的"已经做完归一化"的版本，直接使用即可。
