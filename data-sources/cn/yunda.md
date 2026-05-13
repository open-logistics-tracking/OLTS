# 韵达速递 (yunda)

> [`mappings/cn/yunda.csv`](../../mappings/cn/yunda.csv) — 26 raw status codes

## 数据来源

### 1. openapi.yundaex.com 物流轨迹接口

- **URL**: https://openapi.yundaex.com/openapi/outer/logictis/query
- **抓取日期**: 2026-05
- **内容**: 查询 + 订阅 + 推送三个接口，含 status (5 整体) + action (21 轨迹) 双层命名空间
- **版权**: 需联系韵达申请接口权限

## 重新抓取流程

本 repo 仅在 `mappings/cn/yunda.csv` 中保留映射后的精简数据；原始文档不入库（避免版权/隐私问题及大文件膨胀）。

社区贡献者若要核验或扩展映射，需自行从上述来源重新获取最新文档（多数承运商需登录其开放平台）。

## 数据更新方式

映射 CSV 头部 `# Source:` 注释块已记录原始数据来源、抓取日期、字段命名空间约定。`mappings/cn/yunda.csv` 是事实上的"已经做完归一化"的版本，直接使用即可。
