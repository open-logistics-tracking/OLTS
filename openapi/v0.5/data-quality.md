# OLTS v0.5 数据质量评价框架

> v0.5.0-dev · 待社区评审

OLTS 是一个**质量比覆盖更重要**的规范——映射不齐全可以后补，但数据
本身不一致会让消费方失去信任。本文规定 4 个评价维度、15 个具体 metric、
计算方法、推荐阈值。

适用对象:
- OLTS 实现方（聚合平台 / 品牌方中台 / SaaS 厂商）暴露的轨迹服务
- 想衡量"我们的归一化做得有多好"的运维 / 数据团队
- 想给 OLTS 提 PR 提升映射精度的社区贡献者

## 4 维度

| 维度 | 关注 | 谁负责 |
|---|---|---|
| **完整度** Completeness | 字段填充率 | 映射 + 数据源 |
| **时效性** Timeliness | 事件延迟 | 数据 pipeline |
| **一致性** Consistency | Schema 合规 + 逻辑合理 | 映射 + 规范 |
| **准确性** Accuracy | 映射对错 | 映射 + 抽样审查 |

---

## 完整度 Completeness

| ID | Metric | 推荐阈值 |
|---|---|---|
| **M1** | `% events with timezone offset in eventTime` | ≥ 99% |
| **M2** | `% events with location.countryCode` (国际段) | ≥ 95% |
| **M3** | `% events with non-empty description` | ≥ 90% |
| **M4** | `% events with location (any field)` | ≥ 85% |
| **M5** | `% shipments with both origin AND destination` | ≥ 80% |

### M1 — Timezone 完整度

```sql
SELECT
  COUNT(*) FILTER (WHERE event_time::text ~ '[+-][0-9]{2}:[0-9]{2}$') * 100.0
  / COUNT(*) AS m1_pct
FROM olts_events
WHERE event_time > now() - interval '7 days';
```

国内承运商通常返回不含 timezone offset 的时间——实现方应在 ingest 时
附加本地时区（见 v0.2 Schema 设计原则 #3）。M1 < 99% 通常意味着 ingest
中遗漏了某些 carrier。

### M2 — countryCode 完整度（仅国际段）

```sql
SELECT
  COUNT(*) FILTER (WHERE location->>'countryCode' ~ '^[A-Z]{2}$') * 100.0
  / COUNT(*) AS m2_pct
FROM olts_events e
WHERE e.carrier_code IN ('dhl', 'fedex', 'ups', 'usps');
```

---

## 时效性 Timeliness

| ID | Metric | 推荐阈值 |
|---|---|---|
| **M6** | Median latency: ingest_time - event_time | < 5 min |
| **M7** | p95 latency: ingest_time - event_time | < 30 min |
| **M8** | Webhook delivery latency (push - publish) median | < 5 s |
| **M9** | `% events delivered to subscribers within 60s` | ≥ 95% |

### M6 / M7 — Ingest latency

```sql
SELECT
  percentile_cont(0.50) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (ingest_time - event_time)))
    AS m6_median_seconds,
  percentile_cont(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (ingest_time - event_time)))
    AS m7_p95_seconds
FROM olts_events
WHERE event_time > now() - interval '24 hours';
```

不同承运商基础延迟差异大: SF 推送多在 2-5 min；UPS 查询型 API 可能 10-30 min。
建议按 carrier_code 分别 tracking。

---

## 一致性 Consistency

| ID | Metric | 推荐阈值 |
|---|---|---|
| **M10** | `% events where olts_code is in ULSC dict` | 100% (硬约束) |
| **M11** | `% raw codes that map to unique olts_code` (no ambiguity) | 100% |
| **M12** | `% events ordered chronologically within shipment` | ≥ 99% |
| **M13** | `% transitions matching valid state machine` | ≥ 95% |

### M10 — ULSC 字典合规

```sql
SELECT
  COUNT(*) FILTER (WHERE olts_code IN (
    SELECT code FROM ulsc_dict
  )) * 100.0 / COUNT(*) AS m10_pct
FROM olts_events;
```

低于 100% 就是 bug——OLTS Schema 强制 `oltsCode` 在 ULSC 32 码内。
检查 ingest 代码是否绕过了 enum 校验。

### M11 — 映射无歧义

```sql
-- 检查同一 (carrier, raw_code) 是否映射到多个 olts_code
SELECT carrier_code, raw_code, COUNT(DISTINCT olts_code) AS distinct_olts
FROM olts_mappings
GROUP BY carrier_code, raw_code
HAVING COUNT(DISTINCT olts_code) > 1;
```

期待 0 行结果。如果有，需要补充 carrier 上下文消歧（如 SF opcode:161
代签 vs 快递柜签收，文档中合并；mapping CSV 选了一个，notes 说明）。

### M13 — 状态机合理性

定义合法转移图（部分示例）：

```
order_created   → pickup_scheduled | picked_up | order_cancelled
pickup_scheduled → picked_up | pickup_failed | order_cancelled
picked_up       → arrived_at_hub | in_transit | departed_from_hub | ...
arrived_at_hub  → departed_from_hub | in_transit | customs_declared | ...
departed_from_hub → arrived_at_hub | arrived_at_destination | in_transit
out_for_delivery → delivered | delivery_attempted | exception | ...
delivered       → (terminal; exceptional: return_initiated)
returned_to_sender → (terminal)
```

完整状态机定义见后续 v0.5 spec（M13 实现可以宽松一些——只在
明显违反时报警，如 `delivered → picked_up`）。

---

## 准确性 Accuracy

| ID | Metric | 推荐阈值 |
|---|---|---|
| **M14** | 人工抽样审核命中率（随机 100 条 / 月） | ≥ 95% 映射正确 |
| **M15** | 客诉中"状态显示错误"占比 | ≤ 0.1% |

### M14 — 抽样审核流程

1. 每月随机抽 100 个映射后事件
2. 找原始 carrier 响应（raw code + 描述）
3. 由懂业务的人评判 olts_code 是否合理
4. 不合理的 → 提 GitHub Issue 修改 mapping
5. 命中率作为长期 metric tracking

UPS `mappings/intl/ups.csv` 中 346 条 `automated rule-based classification`
标注的码，是 M14 的天然抽样池。

### M15 — 客诉关联

如果 OLTS 输出直接展示给最终用户（C 端），"状态显示错误" 应该 < 0.1%。
更高比率通常意味着上游 mapping 有误。

---

## /health/data-quality 端点提议

实现方可暴露一个内省端点，返回最近 7 天的 metric 快照：

```http
GET /health/data-quality
Content-Type: application/json
```

```json
{
  "windowDays": 7,
  "totalEvents": 8294031,
  "computedAt": "2026-05-13T08:00:00+08:00",
  "metrics": {
    "M1_timezone_pct": 99.7,
    "M2_country_code_pct": 96.2,
    "M3_description_pct": 91.4,
    "M6_median_latency_seconds": 187,
    "M7_p95_latency_seconds": 1290,
    "M10_ulsc_dict_pct": 100.0,
    "M13_state_machine_pct": 98.7
  },
  "thresholdViolations": [
    {
      "metric": "M2_country_code_pct",
      "value": 96.2,
      "threshold": 95.0,
      "severity": "warning"
    }
  ]
}
```

建议绑定 Prometheus / Grafana / 钉钉告警。

---

## v0.5 vs v1.0

| 范围 | v0.5 (draft) | v1.0 (稳定) |
|---|---|---|
| Metric 定义 | ✅ 15 个 | 可能新增 |
| 推荐阈值 | ✅ 初版 | 行业实践调整 |
| SQL 示例 | ✅ PostgreSQL | + ClickHouse / BigQuery |
| 完整状态机 | ⏳ | ✅ |
| Reference impl | ⏳ | ✅ Python or Go |
| Prometheus exporter | ⏳ | ✅ |

## 反馈

提 Issue 或 PR 调整 metric 定义 / 阈值 / SQL 实现。
