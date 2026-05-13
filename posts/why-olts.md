# 为什么中国物流需要一个开源轨迹标准

> 草稿 · 2026-05 · 待打磨

## TL;DR

物流轨迹数据在中国是事实上的"通天塔"——10 家承运商、10 套字段命名、10 套状态码、10 套签名算法。

OLTS（Open Logistics Tracking Schema）想做一件务实的事：**先把状态码归一**。不发明新数据模型、不强推 schema、不绑架谁。一份 32 码的统一字典 + 一份覆盖 9 家承运商 1600+ raw codes 的映射表。

GitHub：[open-logistics-tracking/OpenLogisticsTrackingSchema](https://github.com/open-logistics-tracking/OpenLogisticsTrackingSchema)

License：文档/字典 CC BY 4.0，代码 Apache 2.0。

---

## 一、痛点是真实的

电商对接 3 家以上承运商时，技术成本指数增长。原因不是"对接量大"，而是**每家都用完全不同的概念**：

| 维度 | 圆通 | 中通 | 顺丰 | 京东 |
|---|---|---|---|---|
| 时间字段 | `upload_Time` | `opTime` | `acceptTime` | `operateTime` |
| 状态字段 | `infoContent` | `opCode` | `opcode` | `state` |
| 状态值类型 | 英文缩写 | 1 位数字 | 数字 | 6 位数字 |
| 签名算法 | Base64(MD5(...)) | MD5/SHA256 可选 | HMAC-SHA256 | APPKEY+APPSECRET |
| 时间格式 | `yyyy-MM-dd HH:mm:ss` | 同上 | 同上 | 同上 |

国际段更复杂。DHL Parcel DE 一个 event 配多个 RIC 子原因码，282 个组合。USPS Pub 199 Appendix G-4 有 70+ 域内事件码，G-5 还有 50+ 国际邮件 UPU 标准码。

对接每家承运商都要：
1. 读 100+ 页文档（不同语言、不同时代、不同更新节奏）
2. 看懂他们的状态体系
3. 在自己系统里建一套"统一状态" 然后写映射代码
4. 维护这套映射（承运商加新码时跟进）

**每家公司都重复一遍**。整个行业重复了几万遍。

这不是技术问题，是**协调成本问题**。

## 二、为什么不等团体标准

中物联 GB/T 45815-2025 刚发布（2025 年 7 月实施）——这是好事，定义了物流数据交换的**框架**。但它**不规定**：
- 每个事件类型用什么 code
- 状态码之间的语义关系
- 各家承运商的 raw code 怎么映射到统一码

这些是行业**事实上的协调缺口**。等标准化机构补完，可能要 3-5 年。

国际上类似 IATA ONE Record、UN/CEFACT BRS、GS1 EPCIS 都有可借鉴的设计，但没有一个直接适配中国快递的"扫描节点级"颗粒度。

## 三、OLTS 的范围（v0.1）

**只做一件事**：发布一份开源的、社区维护的"状态码归一字典 + 承运商映射表"。

不做：
- 新的 schema 提案（避免与 GB/T 45815 冲突）
- API 调用层抽象（每家签名算法太不同，硬统一只会引入新约束）
- SDK / 库（让消费者自己选语言生态）

做的：
- ULSC（Unified Logistics Status Codes）：32 个核心码，7 大类，覆盖国内+国际+清关全链路
- 每家承运商的 raw code → ULSC 映射 CSV（4 列：carrier_code / carrier_name / olts_code / notes）
- 一份 Python 校验脚本 + 一份 CSV 格式规范

## 四、v0.1 当前状态

9 家承运商、1600+ 条 raw codes 全部入库：

| 区域 | 承运商 | raw codes | 数据来源 |
|---|---|---:|---|
| 国内 | 圆通 yto | 11 | 调研报告 |
| 国内 | 中通 zto | 3 | 调研报告（覆盖薄） |
| 国内 | 顺丰 sf | 20 | 调研报告 (status + opcode 两套) |
| 国内 | 京东 jdl | 75 | open.jdl.com 官方文档 |
| 国内 | 邮政 ems | 237 | api.ems.com.cn 官方文档 (含 UPU 标准码) |
| 国内 | 菜鸟 cainiao | 13 | 调研报告 |
| 国际 | DHL | 287 | OpenAPI + Parcel DE ICE 官方表 |
| 国际 | FedEx | 49 | Shopify active_shipping 开源库 |
| 国际 | UPS | 774 | rocketshipit PHP UPS docs |
| 国际 | USPS | 145 | Pub 199 Appendix G-4 + G-5 |

ULSC 32 码 100% 启用（含损坏、丢失、地址异常、收件人不在等细分异常码）。

国内剩余 4 家（申通/韵达/极兔/德邦）等社区或官方数据贡献。

## 五、能贡献什么

如果你：

**对接过某家承运商**：你的真实 API 响应样本 + 状态码映射经验，是最珍贵的贡献。提 issue 或直接 PR 一份 `mappings/cn/<carrier>.csv` 增量。

**做物流数据服务**（聚合/分析/中台）：把你内部的 carrier→统一状态映射表脱敏后开源，可以省下整个行业重新发明的成本。

**维护开源运输库**（如 Python `shippo`、Node `easypost`、Go `goship`）：把内置的 status mapping 跟 OLTS 字典对齐，让用户可以无缝切换。

## 六、长期方向

- v0.2 (2026 Q3): 把映射经验凝结为 JSON Schema —— `TrackingEvent` / `Shipment` 实体定义
- v0.5 (2026 Q4): OpenAPI 3.0 接口规范（轨迹查询 + 推送 webhook）
- v1.0 (2027 H1): 稳定版 + 多语言 SDK + 申请中物联团体标准立项

但 v0.1 这个阶段，**只做映射表**。先把行业的"状态码协调成本"降下来，比什么都重要。

---

*作者：[@zhatrix](https://github.com/zhatrix)。这篇是 OLTS 首发文，欢迎转载，请保留链接。*
*意见、批评、PR 都来自这里：https://github.com/open-logistics-tracking/OpenLogisticsTrackingSchema*
