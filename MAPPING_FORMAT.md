# Carrier Mapping Format

每家承运商一个 CSV 文件，路径：

- `mappings/cn/<carrier>.csv` — 国内承运商
- `mappings/intl/<carrier>.csv` — 国际承运商

## CSV 列定义

| 列名 | 必填 | 说明 |
|---|:---:|---|
| `carrier_code` | ✅ | 承运商原始状态码（如圆通 `GOT`、DHL `transit`） |
| `carrier_name` | ✅ | 承运商原始描述（中文或英文，原样保留） |
| `olts_code` | ✅ | 映射到的 ULSC 统一码（必须出现在 [`ulsc/ulsc.csv`](./ulsc/ulsc.csv) 内） |
| `notes` | ❌ | 映射决策备注，特别是有歧义或多对一时的处理依据 |

## 示例（节选自圆通速递）

```csv
carrier_code,carrier_name,olts_code,notes
GOT,已揽收,picked_up,
ARRIVAL,已收入,arrived_at_hub,
DEPARTURE,已发出,departed_from_hub,
SENT_SCAN,派件,out_for_delivery,
INBOUND,自提柜入柜,delivery_to_locker,
SIGNED,签收成功,delivered,
FAILED,签收失败,delivery_attempted,
FORWARDING,转寄,in_transit,
TMS_RETURN,退回,returned_to_sender,客户拒收后退回
AIRSEND,航空发货,departed_from_hub,运输模式信息归入事件 notes 字段
AIRPICK,航空提货,arrived_at_hub,
```

## 映射原则

1. **保守映射**：拿不准的码，先映射到最接近的通用码（`in_transit` / `exception`），在 `notes` 里记录原始含义
2. **一对多禁止**：同一个 `carrier_code` 在一个映射文件里只能出现一次
3. **多对一允许**：多个 `carrier_code` 映射到同一个 `olts_code` 很常见——这正是统一码的价值
4. **缺失即缺失**：找不到合适的 `olts_code` 不要硬塞，去 [`ulsc/ulsc.csv`](./ulsc/ulsc.csv) 仓库提 Issue 提议新增

## 文件命名约定

### 国内承运商（拼音首字母缩写）

| 承运商 | 文件名 |
|---|---|
| 圆通速递 | `yto.csv` |
| 中通快递 | `zto.csv` |
| 申通快递 | `sto.csv` |
| 韵达速递 | `yunda.csv` |
| 顺丰速运 | `sf.csv` |
| 京东物流 | `jdl.csv` |
| 中国邮政 | `ems.csv` |
| 极兔速递 | `jtexpress.csv` |
| 菜鸟 | `cainiao.csv` |
| 德邦快递 | `deppon.csv` |

### 国际承运商

| 承运商 | 文件名 |
|---|---|
| DHL | `dhl.csv` |
| FedEx | `fedex.csv` |
| UPS | `ups.csv` |
| USPS | `usps.csv` |

## 数据来源标注

每个映射文件顶部建议加一行注释说明数据来源：

```csv
# Source: 圆通速递开放平台官方文档 v2.x（2026-05 调研）
# Reviewer: @<github_handle>
carrier_code,carrier_name,olts_code,notes
...
```

注释行以 `#` 开头，验证脚本会自动跳过。
