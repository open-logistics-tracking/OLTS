# `transitions.csv` — ULSC 状态转移矩阵

68 条合法转移定义，配合 `state-machine.md` 使用。SDK 加载本文件实现 validator。

## 字段

| 字段 | 含义 |
|---|---|
| `from_code` | 源 ULSC 码；`*` 表示任意态（universal 转移） |
| `to_code` | 目标 ULSC 码 |
| `kind` | `normal`（常规合法）/ `exception`（例外允许，需业务上下文）/ `universal`（任意态可达） |
| `note` | 业务说明，可空 |

## 隐式规则（不在 CSV 中）

- **同码重复合法**：`A → A` 永远合法（多承运商同状态推多条事件，如多次 `in_transit` 描述不同 hub）。SDK 在校验前短路。
- **terminal 状态**：`delivered` / `returned_to_sender` / `order_cancelled` / `lost` / `signed_by_third_party` 不应有出向转移（除少量 `exception kind` 允许，例如 RMA 的 `delivered → return_initiated`）。

## 验证

```bash
python -c "
import csv
from oltrack.ulsc import ALL_CODES
with open('ulsc/transitions.csv') as f:
    rows = list(csv.DictReader(f))
for r in rows:
    if r['from_code'] != '*' and r['from_code'] not in ALL_CODES:
        print('BAD from:', r)
    if r['to_code'] not in ALL_CODES:
        print('BAD to:', r)
print(f'{len(rows)} rows, all referenced codes valid')
"
```

## SDK 用法

```python
from oltrack.state_machine import is_valid_transition, next_states, is_terminal

is_valid_transition("picked_up", "arrived_at_hub")  # True
is_valid_transition("delivered", "picked_up")        # False
is_valid_transition("delivered", "return_initiated", context={"rma": True})  # True
next_states("out_for_delivery")  # {'delivered', 'delivery_attempted', ...}
is_terminal("delivered")  # True
```

```typescript
import { isValidTransition, nextStates, isTerminal } from "@oltrack/sdk";

isValidTransition("picked_up", "arrived_at_hub");  // true
isValidTransition("delivered", "return_initiated", { rma: true });  // true
nextStates("out_for_delivery");  // Set { 'delivered', 'delivery_attempted', ... }
isTerminal("delivered");  // true
```
