# USPS (usps)

> [`mappings/intl/usps.csv`](../../mappings/intl/usps.csv) — 145 raw status codes

## 数据来源

### 1. USPS Pub 199 IMpb Implementation Guide (2019 v20)

- **URL**: https://postalpro.usps.com/pub199
- **抓取日期**: 2026-05
- **内容**: Appendix G-4: USPS Domestic Tracking Scan Events（72 个 2 位数字 event code）
- **版权**: USPS 公开文档（PostalPro 公开免费下载）

### 2. USPS Pub 199 IMpb Implementation Guide (v34, 2026-04-01)

- **URL**: https://postalpro.usps.com/pub199
- **抓取日期**: 2026-05
- **内容**: Appendix G-5: Scan Event Codes – International Mail（50+ 个 2 字符 alpha event code，含 UPU 标准节点）
- **版权**: USPS 公开文档；v34 已把 G-4 移到 PostalPro 单独 PDF

### 3. USPS Tracking V3 OpenAPI spec

- **URL**: https://developer.usps.com/trackingv3
- **抓取日期**: 2026-05
- **内容**: API schema 参考（不含 raw event codes，仅含 mailClass / itemShape / MailingEventType 等元数据 enum）
- **版权**: 需登录 USPS Developer Portal

## 重新抓取流程

本 repo 仅在 `mappings/intl/usps.csv` 中保留映射后的精简数据；原始文档不入库（避免版权/隐私问题及大文件膨胀）。

社区贡献者若要核验或扩展映射，需自行从上述来源重新获取最新文档（多数承运商需登录其开放平台）。

## 数据更新方式

映射 CSV 头部 `# Source:` 注释块已记录原始数据来源、抓取日期、字段命名空间约定。`mappings/intl/usps.csv` 是事实上的"已经做完归一化"的版本，直接使用即可。
