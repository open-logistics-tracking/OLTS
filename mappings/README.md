# Carrier Mappings

承运商原始状态码到 ULSC 统一码的映射表。参见 [../MAPPING_FORMAT.md](../MAPPING_FORMAT.md) 了解 CSV 格式。

## 进度

### 国内（`cn/`）

| 承运商 | 文件 | 状态 | 数据来源 |
|---|---|---|---|
| 圆通速递 | `yto.csv` | ⏳ W2 | 圆通开放平台文档 |
| 中通快递 | `zto.csv` | ⏳ W2 | 中通开放平台文档 |
| 顺丰速运 | `sf.csv` | ⏳ W2 | 顺丰丰桥/开放平台 |
| 京东物流 | `jdl.csv` | ⏳ W2 | 京东物流开放平台 |
| 中国邮政 | `ems.csv` | ⏳ W2 | EMS 开放平台 |
| 申通快递 | `sto.csv` | ⏳ W4 | 申通开放平台 |
| 韵达速递 | `yunda.csv` | ⏳ W4 | 韵达开放平台 |
| 极兔速递 | `jtexpress.csv` | ⏳ W4 | 极兔开放平台 |
| 菜鸟 | `cainiao.csv` | ⏳ W4 | 菜鸟开放平台 |
| 德邦快递 | `deppon.csv` | ⏳ W4 | 德邦开放平台 |

### 国际（`intl/`）

| 承运商 | 文件 | 状态 | 数据来源 |
|---|---|---|---|
| DHL | `dhl.csv` | ⏳ W3 | DHL Unified Tracking API |
| FedEx | `fedex.csv` | ⏳ W3 | FedEx Track API |
| UPS | `ups.csv` | ⏳ W3 | UPS Tracking API |
| USPS | `usps.csv` | ⏳ W3 | USPS Tracking API |

## 贡献新承运商

欢迎超出上述清单的承运商映射 PR（如顺丰国际、嘉里大通、UPS Mail Innovations 等）。提交前请确保：

1. 数据来自承运商官方文档或公开 API 响应样例（不要凭印象写）
2. 在文件顶部以 `#` 注释标明来源和调研日期
3. 通过 `tools/validate.py`（W4 提供）的字典校验
