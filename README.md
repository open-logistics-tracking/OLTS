# OLTS — Open Logistics Tracking Schema

> 开放物流轨迹数据规范 · v0.1.0-dev

中国主流快递企业的物流轨迹 API 在字段命名、状态码、签名方式上完全碎片化：对接 3 家以上承运商，技术适配成本就呈指数增长。OLTS 旨在提供一份开放的、由社区维护的统一规范，让上下游系统只需一次对接。

## v0.1 当前阶段：映射表先行

v0.1 不是 schema，是一份**状态码字典 + 承运商映射表**。先把碎片化的状态码归一到 32 个统一码上，覆盖国内 10 家 + 国际 4 家主流承运商。完整 JSON Schema / OpenAPI 规范在 v0.2 及之后推出（见 [ROADMAP](./ROADMAP.md)）。

| 交付物 | 状态 |
|---|---|
| ULSC 统一状态码字典（32 个码，7 大类） | ✅ v0.1 草案 |
| 国内承运商映射（圆通/中通/申通/韵达/顺丰/京东/邮政/极兔/菜鸟/德邦） | ⏳ W2–W4 |
| 国际承运商映射（DHL / FedEx / UPS / USPS，含清关节点） | ⏳ W3 |
| 映射格式规范（CSV） | ✅ 草案 |
| 验证脚本（Python） | ⏳ W4 |

## 命名约定

所有统一码采用 `lowercase_underscore` 风格（OpenAPI / JSON Schema 友好）：

```
picked_up         arrived_at_hub        out_for_delivery
in_transit        customs_released      delivered
```

## 为什么需要这个

这个项目从 3 份调研报告出发：

- [国内快递开放平台 API 对比分析](./快递企业开放平台API对比分析报告.md)：圆通/中通/顺丰等 10 家 API 的认证、字段、状态码全维度对比
- [国际物流轨迹格式调研](./国际物流轨迹格式调研报告.md)：DHL/FedEx/UPS/USPS/IATA/海关清关节点
- [标准空白点分析](./物流轨迹数据规范空白点分析报告.md)：国内外 15+ 标准的覆盖与空白

## 快速参与

- 看一眼 [ULSC 字典](./ulsc/ulsc.csv)，发现缺码或歧义请提 Issue
- 看 [映射格式规范](./MAPPING_FORMAT.md)，按格式 PR 一家承运商的映射

## 许可

- 文档与字典数据：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- 代码与工具：[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)
