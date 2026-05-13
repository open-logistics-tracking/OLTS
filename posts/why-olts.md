# 为什么中国物流需要一个开源轨迹标准

> 2026-05

## TL;DR

物流轨迹数据在中国是事实上的"通天塔"——10 家承运商、10 套字段命名、10 套状态码、10 套签名算法。

OLTS（**Open Logistics Tracking Schema**）想做一件务实的事：**先把状态码归一**。不发明新数据模型、不强推 schema、不绑架谁。一份 32 码的统一字典 + 一份覆盖 **12 家承运商、1761 条 raw codes** 的开源映射表。

```
12 carriers   |   1761 raw codes   |   ULSC 32/32 used   |   CC BY 4.0 + Apache 2.0
```

GitHub：[open-logistics-tracking/OpenLogisticsTrackingSchema](https://github.com/open-logistics-tracking/OpenLogisticsTrackingSchema)

---

## 一、痛点是真实的

电商对接 3 家以上承运商时，技术成本指数增长。原因不是"对接量大"，而是**每家都用完全不同的概念**：

| 维度 | 圆通 | 中通 | 顺丰 | 京东 |
|---|---|---|---|---|
| 时间字段 | `upload_Time` | `opTime` | `acceptTime` | `operateTime` |
| 状态字段 | `infoContent` | `scanType` | `opcode` | `state` |
| 状态值类型 | 英文缩写 | 中文/英文/数字三套 | 数字 | 6 位数字 |
| 签名算法 | Base64(MD5(...)) | MD5/SHA256 可选 | HMAC-SHA256 | APPKEY+APPSECRET |

国际段更复杂。DHL Parcel DE 一个 event 配多个 RIC 子原因码，**282 个组合**。USPS Pub 199 Appendix G-4 有 70+ 域内事件码，G-5 还有 50+ 国际邮件 UPU 标准码。UPS 公开的 status code 表 **774 条**。

### 行业成本量化（粗估）

对接 1 家承运商**轨迹接口**的工程成本：

| 阶段 | 人天 |
|---|---:|
| 读文档 + 注册 + 申请 sandbox 凭证 | 2 |
| 实现签名算法（每家都不一样） | 2 |
| 字段归一化（时间/状态/地址） | 3 |
| 状态码映射（业务侧统一态） | 2 |
| 异常处理 + 监控 + 重试 | 3 |
| 接入测试 + 上线 | 2 |
| **每家小计** | **14 人天** |

对接 6 家：~80 人天。整个行业重复了几万遍。

这不是技术问题，是**协调成本问题**。

## 二、为什么不等团体标准

中物联 **GB/T 45815-2025**（2025-07 实施）定义了物流数据交换的**框架**。但它**不规定**：

- 每个事件类型用什么 code
- 状态码之间的语义关系
- 各家承运商的 raw code 怎么映射到统一码

这些是行业**事实上的协调缺口**。等标准化机构自上而下补完，3-5 年起步。

国际上 IATA ONE Record、UN/CEFACT BRS、GS1 EPCIS 都有可借鉴的设计，但没有一个直接适配中国快递的"扫描节点级"颗粒度。

## 三、OLTS 的范围（v0.1）

**只做一件事**：发布一份开源的、社区维护的"状态码归一字典 + 承运商映射表"。

不做：
- 新的 schema 提案（避免与 GB/T 45815 冲突）
- API 调用层抽象（每家签名算法太不同，硬统一只会引入新约束）
- SDK / 库（让消费者自己选语言生态）

做的：
- **ULSC**（Unified Logistics Status Codes）：32 个核心码，7 大类，覆盖国内+国际+清关全链路
- 每家承运商的 raw code → ULSC 映射 CSV（4 列：`carrier_code` / `carrier_name` / `olts_code` / `notes`）
- 一份 Python 校验脚本 (`tools/validate.py`) + 一份 CSV 格式规范

## 四、v0.1 现在长什么样

**12 家承运商、14 个映射文件、1761 条 raw codes**，全部通过字典 + CSV 字段双重校验：

### 国内 10 家

| 承运商 | raw codes | 数据来源 |
|---|---:|---|
| 圆通 yto | 11 | 圆通开放平台官方文档 |
| 中通 zto | 24 | japi.zto.com 接口文档 |
| 申通 sto | 29 | open.sto.cn 物流详情接口 |
| 韵达 yunda | 26 | openapi.yundaex.com 轨迹接口 |
| 顺丰 sf | 20 | 顺丰开放平台 v2.1（status + opcode 两套）|
| 京东 jdl | 75 | open.jdl.com 三份官方文档 |
| 邮政 ems | **237** | api.ems.com.cn 协议客户开放平台 |
| 极兔 jtexpress | 46 | openapi.jtexpress.com.cn |
| 菜鸟 cainiao | 14 | TMS_PRACTICE_TRACE_INFO 接口 |
| 德邦 deppon | 24 | dpopen.deppon.com（订单+轨迹两层）|

### 国际 4 家

| 承运商 | raw codes | 数据来源 |
|---|---:|---|
| DHL | **287** | DHL Unified API + Parcel DE ICE 官方表 |
| FedEx | 49 | Shopify active_shipping 开源库 + OpenAPI |
| UPS | **774** | rocketshipit PHP UPS docs（业内整理）|
| USPS | 145 | Pub 199 Appendix G-4（国内）+ G-5（国际）|

**ULSC 32 码 100% 启用**——含损坏、丢失、地址异常、收件人不在、待自提、清关扣留等细分异常码。

## 五、3 个典型对接场景

### 场景 A：腰部电商品牌方（年发件 100-1000 万）

正在自建物流中台，对接 3-5 家承运商。最痛的不是抓 API，是**每家都要自己造一套统一状态**。

OLTS 直接拿来用：

```sql
-- 在你的事件表里加一列 olts_code
ALTER TABLE shipment_events ADD COLUMN olts_code VARCHAR(40);

-- 用映射表批量更新
UPDATE shipment_events e
   SET olts_code = m.olts_code
  FROM (SELECT carrier_code, olts_code FROM ext.olts_mapping
         WHERE carrier = 'yto') m
 WHERE e.carrier = 'yto' AND e.raw_code = m.carrier_code;
```

省下来的：6 家 × 2 人天（"状态码映射"环节）= **12 人天**。

### 场景 B：跨境电商物流中台

国内段顺丰/京东 + 国际段 DHL/UPS + 清关节点。OLTS 的 ULSC 字典含 6 个清关码（`customs_declared` / `customs_held` / `customs_inspection` / `customs_released` / `customs_duty_paid` / `clearance_completed`），DHL/USPS/EMS 映射里都已经用上。

跨境前端不需要为每家承运商写一套"清关状态翻译"。

### 场景 C：物流 SaaS 厂商做对外开放接口

你给客户提供"统一物流接口"，背后接了 10+ 承运商。OLTS 给你一个**已经辩论过的**统一码字典——不用自己定义、不用自己说服客户、不用自己维护映射表。

把映射作为 git submodule 嵌入自己的服务：

```bash
git submodule add https://github.com/open-logistics-tracking/OpenLogisticsTrackingSchema vendor/olts
```

升级一行命令：`git submodule update --remote`。

## 六、能贡献什么

如果你：

**对接过某家承运商**：你的真实 API 响应样本 + 状态码映射经验，是最珍贵的贡献。
→ 提 Issue 描述场景，或直接 PR 一份 `mappings/cn/<carrier>.csv` 增量。

**做物流数据服务**（聚合/分析/中台）：把你内部的 carrier→统一状态映射表脱敏后开源。
→ PR 形式：每家一个 CSV，遵循 [`MAPPING_FORMAT.md`](https://github.com/open-logistics-tracking/OpenLogisticsTrackingSchema/blob/main/MAPPING_FORMAT.md)。

**维护开源运输库**（如 Python `shippo`、Node `easypost`、Go `goship`）：把内置 status mapping 跟 OLTS 字典对齐。
→ 你的库的用户可以零成本切换。

**审查 UPS 426 条 exception**：[`mappings/intl/ups.csv`](https://github.com/open-logistics-tracking/OpenLogisticsTrackingSchema/blob/main/mappings/intl/ups.csv) 中 346 条规则化分类标"automated rule-based classification; awaiting community review"。手工 spot review 一条改一条，PR 友好。
→ 这是 UPS 操作员/QA/数据分析师的"举手之劳"贡献。

**做 OLTS 适配验证**：拿真实运单跑一遍 OLTS 映射，反馈不对的地方。
→ 提 Issue，附原始响应（脱敏）+ 你认为应该映射到哪个 ULSC 码。

## 七、长期方向

| 版本 | 范围 | 时间 |
|---|---|---|
| **v0.1** ✅ | ULSC 字典 + 12 家映射表 + Python 校验 | 2026-05 完成 |
| **v0.2** | 从映射凝结 `TrackingEvent` JSON Schema + 时间/地址结构化 + Python 转换器 | 2026 Q3 |
| **v0.5** | OpenAPI 3.0 轨迹查询/推送接口 + 数据质量评价 + TypeScript SDK | 2026 Q4 |
| **v1.0** | 稳定版 + 多语言 SDK + 申请中物联团体标准立项 | 2027 H1 |
| **v2.0+** | GB/T 国家标准 + 与 GS1 EPCIS / UN/CEFACT / IATA ONE Record 互操作 | 2028+ |

但 v0.1 这个阶段，**只做映射表**。先把行业的"状态码协调成本"降下来，比什么都重要。

---

*作者：[@zhatrix](https://github.com/zhatrix)。这篇是 OLTS 首发文，欢迎转载，请保留 GitHub 链接。*

*意见、批评、PR 都来自这里：*
*https://github.com/open-logistics-tracking/OpenLogisticsTrackingSchema*
