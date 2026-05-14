# 为什么中国物流需要一个开源轨迹标准

> 2026-05 · updated for OLTS v0.5-dev

## TL;DR

物流轨迹数据在中国是事实上的"通天塔"：承运商 API 在字段命名、状态码、时间格式、签名算法上高度碎片化。对接 3 家以上承运商，成本就不再只是写 HTTP client，而是反复做同一件事：**把每家的轨迹事件翻译成自己业务能理解的统一状态**。

OLTS（**Open Logistics Tracking Schema**）的路线很务实：先把状态码归一，再沉淀 schema、接口规范和参考 SDK。当前仓库已经包含：

```
14 carriers   |   14 mapping files   |   1761 raw codes   |   ULSC 32/32 used
2 JSON Schemas   |   28 examples   |   OpenAPI/AsyncAPI   |   oltrack-py + @oltrack/sdk
```

项目入口：[OpenLogisticsTrackingSchema](../README.md)

---

## 一、痛点是真实的

电商、品牌中台、物流 SaaS 对接 3 家以上承运商时，技术成本指数增长。原因不是"接口数量多"，而是**每家都用不同概念表达同一件事**：

| 维度 | 圆通 | 中通 | 顺丰 | 京东 |
|---|---|---|---|---|
| 时间字段 | `upload_Time` | `scanDate` / `opTime` | `acceptTime` | `operationTime` |
| 状态字段 | `infoContent` | `scanType` | `opcode` | `state` |
| 状态值类型 | 英文缩写 | 中文 / 英文 / 数字三套 | 数字 | 6 位数字 |
| 签名算法 | Base64(MD5(...)) | MD5/SHA256 可选 | HMAC-SHA256 | APPKEY+APPSECRET |

国际段更复杂。DHL Parcel DE 一个 event 配多个 RIC 子原因码，形成数百个组合；USPS Pub 199 同时有域内事件码和国际邮件 UPU 标准码；UPS 的 status code 表规模更大，当前映射收录 **774 条**。

### 行业成本量化（粗估）

对接 1 家承运商**轨迹接口**的工程成本：

| 阶段 | 人天 |
|---|---:|
| 读文档 + 注册 + 申请 sandbox 凭证 | 2 |
| 实现签名算法（每家都不一样） | 2 |
| 字段归一化（时间 / 状态 / 地址） | 3 |
| 状态码映射（业务侧统一态） | 2 |
| 异常处理 + 监控 + 重试 | 3 |
| 接入测试 + 上线 | 2 |
| **每家小计** | **14 人天** |

对接 6 家：约 80 人天。整个行业反复做同一套状态映射和字段归一化，这不是算法问题，是**协调成本问题**。

## 二、为什么不等团体标准

中物联 **GB/T 45815-2025** 定义了物流数据交换的框架，但它不解决这些落地问题：

- 每个扫描事件用什么状态码
- 状态码之间的语义关系
- 各家承运商 raw code 怎么映射到统一码
- 消费方接口如何返回统一后的轨迹事件

国际上 IATA ONE Record、UN/CEFACT BRS、GS1 EPCIS 都有可借鉴的设计，但没有一个能直接覆盖中国快递的"扫描节点级"颗粒度和国内承运商状态码体系。

OLTS 的定位不是替代标准化机构，而是把事实上的行业经验先整理成可运行、可验证、可社区维护的开放资料。

## 三、OLTS 做什么

OLTS 分三层推进：

1. **v0.1：统一状态码与映射表**
   [`ulsc/ulsc.csv`](../ulsc/ulsc.csv) 定义 32 个 ULSC 统一码，覆盖预下单、揽收、运输、清关、派送、异常、退回 7 大类；[`mappings/`](../mappings/) 维护各承运商 raw code 到 ULSC 的映射。

2. **v0.2：JSON Schema 与示例**
   [`TrackingEvent`](../schemas/v0.2/tracking-event.json) 描述单个轨迹事件，[`Shipment`](../schemas/v0.2/shipment.json) 描述完整运单；[`examples/v0.2/`](../examples/v0.2/) 提供 28 个脱敏/合成示例。

3. **v0.5：消费方 API 与 SDK MVP**
   [`openapi/v0.5/tracking.yaml`](../openapi/v0.5/tracking.yaml) 定义查询接口，[`webhook.md`](../openapi/v0.5/webhook.md) 和 [`asyncapi.yaml`](../openapi/v0.5/asyncapi.yaml) 定义推送契约；[`oltrack-py`](../oltrack-py/) 与 [`@oltrack/sdk`](../oltrack-ts/) 提供参考实现。

OLTS 不做的事也很明确：

- 不替你调用承运商 API
- 不统一上游承运商鉴权 / 签名 / 限流
- 不保存真实运单数据
- 不把承运商原始 PDF / YAML 文档 mirror 进仓库

## 四、现在长什么样

**14 家承运商、14 个映射文件、1761 条 raw codes**，全部通过字典 + CSV 字段双重校验：

```bash
python3 tools/validate.py
```

### 国内 10 家

| 承运商 | raw codes | 映射文件 |
|---|---:|---|
| 圆通 yto | 11 | [`mappings/cn/yto.csv`](../mappings/cn/yto.csv) |
| 中通 zto | 24 | [`mappings/cn/zto.csv`](../mappings/cn/zto.csv) |
| 申通 sto | 29 | [`mappings/cn/sto.csv`](../mappings/cn/sto.csv) |
| 韵达 yunda | 26 | [`mappings/cn/yunda.csv`](../mappings/cn/yunda.csv) |
| 顺丰 sf | 20 | [`mappings/cn/sf.csv`](../mappings/cn/sf.csv) |
| 京东 jdl | 75 | [`mappings/cn/jdl.csv`](../mappings/cn/jdl.csv) |
| 邮政 ems | 237 | [`mappings/cn/ems.csv`](../mappings/cn/ems.csv) |
| 极兔 jtexpress | 46 | [`mappings/cn/jtexpress.csv`](../mappings/cn/jtexpress.csv) |
| 菜鸟 cainiao | 14 | [`mappings/cn/cainiao.csv`](../mappings/cn/cainiao.csv) |
| 德邦 deppon | 24 | [`mappings/cn/deppon.csv`](../mappings/cn/deppon.csv) |

### 国际 4 家

| 承运商 | raw codes | 映射文件 |
|---|---:|---|
| DHL | 287 | [`mappings/intl/dhl.csv`](../mappings/intl/dhl.csv) |
| FedEx | 49 | [`mappings/intl/fedex.csv`](../mappings/intl/fedex.csv) |
| UPS | 774 | [`mappings/intl/ups.csv`](../mappings/intl/ups.csv) |
| USPS | 145 | [`mappings/intl/usps.csv`](../mappings/intl/usps.csv) |

数据来源和版权说明见 [`data-sources/`](../data-sources/)；映射格式见 [`MAPPING_FORMAT.md`](../MAPPING_FORMAT.md)。

## 五、3 个典型对接场景

### 场景 A：腰部电商品牌方（年发件 100-1000 万）

正在自建物流中台，对接 3-5 家承运商。最痛的不是抓 API，是每家都要自己造一套统一状态。

OLTS 可以直接作为映射表使用：

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

国内段顺丰 / 京东 + 国际段 DHL / UPS + 清关节点。OLTS 的 ULSC 字典含 6 个清关码：`customs_declared` / `customs_held` / `customs_inspection` / `customs_released` / `customs_duty_paid` / `clearance_completed`。DHL、USPS、EMS 等映射已经使用这些清关码。

跨境前端不需要为每家承运商写一套"清关状态翻译"。

### 场景 C：物流 SaaS 厂商做对外开放接口

你给客户提供"统一物流接口"，背后接了 10+ 承运商。OLTS 给你一个已经辩论过的统一码字典、JSON Schema 和消费方 HTTP 接口规范。

可以把映射作为 git submodule 嵌入自己的服务：

```bash
git submodule add https://github.com/open-logistics-tracking/olts vendor/olts
git submodule update --remote
```

如果你要对外暴露统一查询接口，可以直接参考 [`openapi/v0.5/`](../openapi/v0.5/)。

## 六、能贡献什么

如果你：

**对接过某家承运商**：你的脱敏 API 响应样本 + 状态码映射经验，是最珍贵的贡献。
→ 提 Issue 描述场景，或直接 PR 一份 `mappings/cn/<carrier>.csv` / `mappings/intl/<carrier>.csv` 增量。

**做物流数据服务**（聚合 / 分析 / 中台）：把内部 carrier → 统一状态映射表脱敏后开源。
→ PR 形式：每家一个 CSV，遵循 [`MAPPING_FORMAT.md`](../MAPPING_FORMAT.md)。

**维护开源运输库**（如 Python、Node、Go 物流 SDK）：把内置 status mapping 跟 ULSC 字典对齐。
→ 你的库的用户可以零成本获得统一状态码。

**审查 UPS 异常细化**：[`mappings/intl/ups.csv`](../mappings/intl/ups.csv) 中仍有大量规则化分类标记为 `automated rule-based classification; awaiting community review`。
→ 手工 spot review 一条改一条，PR 友好。

**做 OLTS 适配验证**：拿脱敏运单样本跑 [`oltrack-py`](../oltrack-py/) + schema 校验，反馈不对的映射。
→ 提 Issue 时请移除或脱敏运单号、手机号、姓名、详细地址、签收人、证件号、API token/header。

## 七、长期方向

| 版本 | 范围 | 状态 |
|---|---|---|
| **v0.1** | ULSC 字典 + 14 家映射表 + Python 校验 | ✅ 已完成 |
| **v0.2** | `TrackingEvent` / `Shipment` JSON Schema + 28 examples + Python 参考实现 | ✅ 主体完成 |
| **v0.5** | OpenAPI 3.1 查询接口 + Webhook + AsyncAPI + 数据质量评价 + TypeScript SDK MVP | ✅ 主体完成 |
| **v1.0** | 稳定版 + 状态转移图/矩阵 + 多语言 SDK + 团体标准立项准备 | 🚧 准备中 |
| **v2.0+** | GB/T 国家标准路径 + 与 GS1 EPCIS / UN/CEFACT / IATA ONE Record 互操作 | 规划中 |

当前更完整的路线见 [`ROADMAP.md`](../ROADMAP.md)。ULSC 状态转移图见 [`ulsc/state-machine.md`](../ulsc/state-machine.md)。

---

*作者：[@zhatrix](https://github.com/zhatrix)。欢迎转载，请保留项目链接。*

*意见、批评、PR 都来自这里：*
*https://github.com/open-logistics-tracking/olts*
