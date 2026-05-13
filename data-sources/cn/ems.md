# 中国邮政 EMS (ems)

> [`mappings/cn/ems.csv`](../../mappings/cn/ems.csv) — 237 raw status codes

## 数据来源

### 1. api.ems.com.cn 协议客户开放平台

- **URL**: https://api.ems.com.cn/amp-prod-api/f/amp/api/open
- **抓取日期**: 2026-05
- **内容**: 操作码（~195 条含 UPU EDA/EDB/EDC/EME 系列）+ 妥投代码（24 条）+ 未妥投代码（16 条）
- **版权**: 需登录中国邮政 EMS 协议客户开放平台

## 重新抓取流程

本 repo 仅在 `mappings/cn/ems.csv` 中保留映射后的精简数据；原始文档不入库（避免版权/隐私问题及大文件膨胀）。

社区贡献者若要核验或扩展映射，需自行从上述来源重新获取最新文档（多数承运商需登录其开放平台）。

## 数据更新方式

映射 CSV 头部 `# Source:` 注释块已记录原始数据来源、抓取日期、字段命名空间约定。`mappings/cn/ems.csv` 是事实上的"已经做完归一化"的版本，直接使用即可。
