# 圆通速递 (yto)

> [`mappings/cn/yto.csv`](../../mappings/cn/yto.csv) — 11 raw status codes

## 数据来源

### 1. 调研报告 §2.1

- **URL**: ../../快递企业开放平台API对比分析报告.md
- **抓取日期**: 2026-05
- **内容**: 11 个 raw scanType (GOT/ARRIVAL/DEPARTURE/SENT_SCAN/INBOUND/SIGNED/FAILED/FORWARDING/TMS_RETURN/AIRSEND/AIRPICK)，公开调研整理
- **版权**: CC BY 4.0（本仓库整理）

## 重新抓取流程

本 repo 仅在 `mappings/cn/yto.csv` 中保留映射后的精简数据；原始文档不入库（避免版权/隐私问题及大文件膨胀）。

社区贡献者若要核验或扩展映射，需自行从上述来源重新获取最新文档（多数承运商需登录其开放平台）。

## 数据更新方式

映射 CSV 头部 `# Source:` 注释块已记录原始数据来源、抓取日期、字段命名空间约定。`mappings/cn/yto.csv` 是事实上的"已经做完归一化"的版本，直接使用即可。
