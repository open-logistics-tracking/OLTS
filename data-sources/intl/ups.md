# UPS (ups)

> [`mappings/intl/ups.csv`](../../mappings/intl/ups.csv) — 774 raw status codes

## 数据来源

### 1. rocketshipit PHP UPS API docs

- **URL**: https://docs.rocketshipit.com/php/1-0/tracking-parameters.html
- **抓取日期**: 2026-05
- **内容**: 774 个 2 字符状态码（AA-ZZ 字母 + 0-9 数字系列）；业内常用第三方文档站，整理自 UPS Track Web Service Developer Guide 官方表
- **版权**: 第三方整理；UPS 状态码本身是 UPS Tracking API 公开返回值

### 2. UPS-API/api-documentation GitHub 仓库

- **URL**: https://github.com/UPS-API/api-documentation
- **抓取日期**: 2026-05
- **内容**: OpenAPI YAML spec（Tracking.yaml / UPSTrackAlert*.yaml 等）
- **版权**: Apache 2.0（UPS-API 官方 GitHub repo）

## 重新抓取流程

本 repo 仅在 `mappings/intl/ups.csv` 中保留映射后的精简数据；原始文档不入库（避免版权/隐私问题及大文件膨胀）。

社区贡献者若要核验或扩展映射，需自行从上述来源重新获取最新文档（多数承运商需登录其开放平台）。

## 数据更新方式

映射 CSV 头部 `# Source:` 注释块已记录原始数据来源、抓取日期、字段命名空间约定。`mappings/intl/ups.csv` 是事实上的"已经做完归一化"的版本，直接使用即可。
