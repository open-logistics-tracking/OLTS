# 顺丰速运 (sf)

> [`mappings/cn/sf.csv`](../../mappings/cn/sf.csv) — 20 raw status codes

## 数据来源

### 1. 调研报告 §2.5 顺丰开放平台 v2.1

- **URL**: https://api.sf-express.com/route/v2.1/query
- **抓取日期**: 2026-05
- **内容**: 含 expressStatus（10 整体状态码）+ opcode（10 事件级操作码）两套
- **版权**: 调研报告 CC BY 4.0；接口文档需登录顺丰开放平台

## 重新抓取流程

本 repo 仅在 `mappings/cn/sf.csv` 中保留映射后的精简数据；原始文档不入库（避免版权/隐私问题及大文件膨胀）。

社区贡献者若要核验或扩展映射，需自行从上述来源重新获取最新文档（多数承运商需登录其开放平台）。

## 数据更新方式

映射 CSV 头部 `# Source:` 注释块已记录原始数据来源、抓取日期、字段命名空间约定。`mappings/cn/sf.csv` 是事实上的"已经做完归一化"的版本，直接使用即可。
