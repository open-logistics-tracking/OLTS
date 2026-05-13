# 京东物流 (jdl)

> [`mappings/cn/jdl.csv`](../../mappings/cn/jdl.csv) — 75 raw status codes

## 数据来源

### 1. open.jdl.com 一级订单状态文档（2024-08-14 更新）

- **URL**: https://open.jdl.com/#/open-business-document/access-guide/267/54018
- **抓取日期**: 2026-05
- **内容**: 12 个一级订单状态码（status:100-700）
- **版权**: 需登录京东物流开放平台

### 2. open.jdl.com 节点编码文档（2024-01-03 更新）

- **URL**: https://open.jdl.com/#/open-business-document/access-guide/267/54128
- **抓取日期**: 2026-05
- **内容**: 事件级 state 节点编码
- **版权**: 需登录

### 3. open.jdl.com 全程跟踪查询（2023-04-19 更新）

- **URL**: https://open.jdl.com/#/open-business-document/access-guide/442/55086
- **抓取日期**: 2026-05
- **内容**: state → category 完整映射表（60+ 条事件码）
- **版权**: 需登录

## 重新抓取流程

本 repo 仅在 `mappings/cn/jdl.csv` 中保留映射后的精简数据；原始文档不入库（避免版权/隐私问题及大文件膨胀）。

社区贡献者若要核验或扩展映射，需自行从上述来源重新获取最新文档（多数承运商需登录其开放平台）。

## 数据更新方式

映射 CSV 头部 `# Source:` 注释块已记录原始数据来源、抓取日期、字段命名空间约定。`mappings/cn/jdl.csv` 是事实上的"已经做完归一化"的版本，直接使用即可。
