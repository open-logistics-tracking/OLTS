# 申通快递 (sto)

> [`mappings/cn/sto.csv`](../../mappings/cn/sto.csv) — 29 raw status codes

## 数据来源

### 1. open.sto.cn 物流详情接口

- **URL**: https://open.sto.cn/#/help/wxlrw3
- **抓取日期**: 2026-05
- **内容**: STO_TRACE_PLATFORM_PUSH + STO_TRACE_QUERY_COMMON，含国内中文 scanType + 国际 Action Code
- **版权**: 需登录申通开放平台后获取

## 重新抓取流程

本 repo 仅在 `mappings/cn/sto.csv` 中保留映射后的精简数据；原始文档不入库（避免版权/隐私问题及大文件膨胀）。

社区贡献者若要核验或扩展映射，需自行从上述来源重新获取最新文档（多数承运商需登录其开放平台）。

## 数据更新方式

映射 CSV 头部 `# Source:` 注释块已记录原始数据来源、抓取日期、字段命名空间约定。`mappings/cn/sto.csv` 是事实上的"已经做完归一化"的版本，直接使用即可。
