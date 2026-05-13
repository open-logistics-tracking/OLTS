# ULSC — Unified Logistics Status Codes

OLTS v0.1 的核心产物：**32 个统一物流状态码**，覆盖国内快递 + 国际物流 + 清关节点。

## 文件

- [`ulsc.csv`](./ulsc.csv) — 字典源数据（CSV，UTF-8）
- `ulsc.json` — 同一字典的 JSON 形态（v0.2 自动生成）
- [`state-machine.md`](./state-machine.md) — 32 码间合法转移图 + Mermaid 可视化 + 校验函数提议（v0.5→v1.0 过渡）

## 7 大类

| 类别 | 含义 | 码数 |
|---|---|---:|
| `pre_shipment` | 订单交接前 | 3 |
| `pickup` | 揽收 | 3 |
| `transit` | 运输中 | 5 |
| `customs` | 清关（国际段） | 6 |
| `delivery` | 派送 | 6 |
| `exception` | 异常 | 6 |
| `return` | 退回 | 3 |

## 设计原则

1. **粒度优先一致性**：宁可粗粒度统一，不为单一承运商加细分码。例如圆通 `AIRSEND`（航空发货）映射到 `departed_from_hub`，运输模式信息进事件的 `notes` 字段而非状态码。
2. **国际清关一等公民**：v0.1 即纳入 6 个清关码，国内承运商映射文件中允许全部为空（清关码对国内段不适用）。
3. **保留语义留白**：通用码 `in_transit` / `exception` 故意保留，避免承运商找不到合适映射时硬塞。
4. **命名风格**：`lowercase_underscore`，OpenAPI / JSON Schema 友好。

## 新增/修改流程

字典是公共词汇表，任何修改都会影响所有映射文件。流程：

1. 在 GitHub 提 Issue，说明：缺失场景 / 现有码为何不够 / 至少 2 家承运商的真实数据样例
2. 社区讨论 7 天
3. PR 同时修改 `ulsc.csv` + 所有受影响的映射文件

不接受"觉得应该有"的码——必须有真实承运商数据支撑。
