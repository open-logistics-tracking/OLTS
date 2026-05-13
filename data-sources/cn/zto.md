# 中通快递 (zto)

> [`mappings/cn/zto.csv`](../../mappings/cn/zto.csv) — 24 raw status codes

## 数据来源

### 1. japi.zto.com 物流轨迹查询接口文档

- **URL**: https://japi.zto.com/zto.merchant.waybill.track.query
- **抓取日期**: 2026-05
- **内容**: 官方接口 zto.merchant.waybill.track.query + zto.merchant.waybill.track.subsrcibe，含 scanType 三套命名空间（中文/英文/数字）
- **版权**: 需登录中通开放平台 ZOP 后获取

## 重新抓取流程

本 repo 仅在 `mappings/cn/zto.csv` 中保留映射后的精简数据；原始文档不入库（避免版权/隐私问题及大文件膨胀）。

社区贡献者若要核验或扩展映射，需自行从上述来源重新获取最新文档（多数承运商需登录其开放平台）。

## 数据更新方式

映射 CSV 头部 `# Source:` 注释块已记录原始数据来源、抓取日期、字段命名空间约定。`mappings/cn/zto.csv` 是事实上的"已经做完归一化"的版本，直接使用即可。
