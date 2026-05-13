# 菜鸟 (cainiao)

> [`mappings/cn/cainiao.csv`](../../mappings/cn/cainiao.csv) — 14 raw status codes

## 数据来源

### 1. 调研报告 §2.6 菜鸟速递开放平台

- **URL**: http://edi-daily.xpm.cainiao.com/ext/gateway/ediPracticeTrace/ediStandardPracticeTrace/api
- **抓取日期**: 2026-05
- **内容**: 接口 TMS_PRACTICE_TRACE_INFO，13 个核心 status（00-13）+ 14-26 扩展范围（未细化）
- **版权**: 调研报告 CC BY 4.0；接口文档需登录菜鸟开放平台

## 重新抓取流程

本 repo 仅在 `mappings/cn/cainiao.csv` 中保留映射后的精简数据；原始文档不入库（避免版权/隐私问题及大文件膨胀）。

社区贡献者若要核验或扩展映射，需自行从上述来源重新获取最新文档（多数承运商需登录其开放平台）。

## 数据更新方式

映射 CSV 头部 `# Source:` 注释块已记录原始数据来源、抓取日期、字段命名空间约定。`mappings/cn/cainiao.csv` 是事实上的"已经做完归一化"的版本，直接使用即可。
