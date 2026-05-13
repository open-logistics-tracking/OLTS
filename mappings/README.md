# Carrier Mappings

承运商原始状态码到 ULSC 统一码的映射表。参见 [../MAPPING_FORMAT.md](../MAPPING_FORMAT.md) 了解 CSV 格式。

## 进度

### 国内（`cn/`）

| 承运商 | 文件 | 状态 | 数据来源 |
|---|---|---|---|
| 圆通速递 | `yto.csv` | ✅ W2（11 条） | 调研报告 §2.1 |
| 中通快递 | `zto.csv` | 🟡 W2 部分（3 条） | 调研报告 §2.2（原报告标注"推断"，待补） |
| 顺丰速运 | `sf.csv` | ✅ W2（20 条 = 10 status + 10 opcode） | 调研报告 §2.5 |
| 京东物流 | `jdl.csv` | ✅ W2 补缺（75 条 = 12 status + 63 state） | open.jdl.com 官方文档（用户登录后提供，2024-08-14 / 2024-01-03 / 2023-04-19 三份合并） |
| 中国邮政 | `ems.csv` | ✅ W2 补缺（235 条 = 195 opcode + 24 signed + 16 unsigned） | api.ems.com.cn 协议客户开放平台官方文档（用户登录后提供）|
| 申通快递 | `sto.csv` | ✅ W4 补缺（29 条 = 15 国内 + 14 国际） | open.sto.cn 物流详情接口文档（用户登录提供）|
| 韵达速递 | `yunda.csv` | 🟡 W4 partial（2 条） | 调研报告 §2.3（仅 GOT/SIGNED） |
| 极兔速递 | `jtexpress.csv` | ✅ W4 补缺（46 条 = 14 scanType + 32 problemType） | openapi.jtexpress.com.cn 物流接口文档（用户登录提供）|
| 菜鸟 | `cainiao.csv` | ✅ W4（13 核心 + 14-26 扩展范围未细化） | 调研报告 §2.6 |
| 德邦快递 | `deppon.csv` | ✅ W4 补缺（24 条 = 9 订单级 + 15 轨迹级） | dpopen.deppon.com 订单+轨迹接口文档（用户登录提供）|

### 国际（`intl/`）

| 承运商 | 文件 | 状态 | 数据来源 |
|---|---|---|---|
| DHL | `dhl.csv` | ✅ W3（287 条 = 5 status + 282 event:ric） | DHL Unified Tracking API + DHL Parcel DE 官方 ICE event/RIC 完整组合表 |
| FedEx | `fedex.csv` | ✅ W3（48 条 = 30 ScanEvent + 14 commit + 4 notif） | Shopify active_shipping FedEx TRACKING_STATUS_CODES (开源 Ruby 库) + OpenAPI enum |
| UPS | `ups.csv` | ✅ W3（774 条，规则化分类） | rocketshipit.com PHP UPS API docs（整理自 UPS Track Web Service 官方表）|
| USPS | `usps.csv` | ✅ W3（122 条 = 72 域内 G-4 + 50 国际 G-5） | USPS Pub 199 Appendix G-4 (2019 v20 PDF) + G-5 (v34 PDF)，infor/usps/ 本地 |

## 贡献新承运商

欢迎超出上述清单的承运商映射 PR（如顺丰国际、嘉里大通、UPS Mail Innovations 等）。提交前请确保：

1. 数据来自承运商官方文档或公开 API 响应样例（不要凭印象写）
2. 在文件顶部以 `#` 注释标明来源和调研日期
3. 通过 `tools/validate.py`（W4 提供）的字典校验
