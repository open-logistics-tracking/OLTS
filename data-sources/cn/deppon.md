# 德邦快递 (deppon)

> [`mappings/cn/deppon.csv`](../../mappings/cn/deppon.csv) — 24 raw status codes

## 数据来源

### 1. dpopen.deppon.com 订单状态推送 + 标准轨迹接口

- **URL**: https://dpopen.deppon.com/
- **抓取日期**: 2026-05
- **内容**: 订单级 statusType（9 条 CANCEL/FAILGOT/GOBACK/GOT/INVALID/RECEIPTING/SHOUTCAR/SIGNFAILED/SIGNSUCCESS）+ 轨迹级 status（15 条）
- **版权**: 需登录德邦开放平台

## 重新抓取流程

本 repo 仅在 `mappings/cn/deppon.csv` 中保留映射后的精简数据；原始文档不入库（避免版权/隐私问题及大文件膨胀）。

社区贡献者若要核验或扩展映射，需自行从上述来源重新获取最新文档（多数承运商需登录其开放平台）。

## 数据更新方式

映射 CSV 头部 `# Source:` 注释块已记录原始数据来源、抓取日期、字段命名空间约定。`mappings/cn/deppon.csv` 是事实上的"已经做完归一化"的版本，直接使用即可。
