# Data Sources

OLTS 映射 CSV 的**来源元数据目录**——记录每家承运商的状态码体系是从哪里抓取的、什么时候抓的、版权归属如何。

## 策略

本目录**不保留原始 PDF / YAML / JSON 文档**。原因：

1. **版权问题**：承运商开放平台文档大多是登录后获取，可能含 NDA / ToS 限制
2. **大文件膨胀**：USPS Pub 199 PDF 单文件就 8-10MB，UPS api-documentation 整套 ~5MB
3. **更新节奏不同步**：承运商文档时效性强，本 repo 不可能 mirror 最新版

OLTS 的 *官方产物* 是 `mappings/*/` 下的 CSV——已经做完归一化、字段约定固定的精简数据。原始来源仅作引用。

## 索引

### 国内 10 家

| 承运商 | 来源说明 |
|---|---|
| 圆通速递 | [cn/yto.md](./cn/yto.md) |
| 中通快递 | [cn/zto.md](./cn/zto.md) |
| 申通快递 | [cn/sto.md](./cn/sto.md) |
| 韵达速递 | [cn/yunda.md](./cn/yunda.md) |
| 顺丰速运 | [cn/sf.md](./cn/sf.md) |
| 京东物流 | [cn/jdl.md](./cn/jdl.md) |
| 中国邮政 | [cn/ems.md](./cn/ems.md) |
| 极兔速递 | [cn/jtexpress.md](./cn/jtexpress.md) |
| 菜鸟 | [cn/cainiao.md](./cn/cainiao.md) |
| 德邦快递 | [cn/deppon.md](./cn/deppon.md) |

### 国际 4 家

| 承运商 | 来源说明 |
|---|---|
| DHL | [intl/dhl.md](./intl/dhl.md) |
| FedEx | [intl/fedex.md](./intl/fedex.md) |
| UPS | [intl/ups.md](./intl/ups.md) |
| USPS | [intl/usps.md](./intl/usps.md) |

## 本仓库的原始文档存储

本仓库维护者本地的 `infor/` 目录（已 `.gitignore`）保存抓取过的原始 PDF / YAML，但不进入版本控制。

社区贡献者扩展映射时需自行从来源重新抓取——多数需登录对应承运商的开放平台。

## 版权与归属

- 本仓库只发布归一化后的映射表、必要短描述和来源元数据，不 mirror 承运商原始文档
- 我们对状态码到 ULSC 的**映射关系**承担作者权，本仓库以 CC BY 4.0 发布
- 来源文档（PDF/YAML 等）、商标和 API 条款仍属于原权利方；贡献者需确认提交内容可公开

## 反馈

发现来源链接失效 / 抓取日期太旧 / 版权归属不准确，请提 Issue。
