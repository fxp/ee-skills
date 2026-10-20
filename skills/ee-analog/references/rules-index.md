# 精密模拟 / 传感器前端 — 规则索引

46 条。⚠ = 来源之间有分歧。全文见 `rules.md`，用 `grep -n "<规则ID>" rules.md` 定位。

## 架构与选型（architecture）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| ANA-ARC-003 | 核对电流检测增益档和输出量程 ⚠ | must | high | bom_check(full) |
| ANA-ARC-001 | 选型前先做误差预算（失调/漂移/增益/容差） | should | high | bom_check(partial) |
| ANA-ARC-002 | 按失调与量程选分流电阻阻值 ⚠ | should | high | bom_check(partial) |
| ANA-ARC-005 | 放大器带宽/建立时间要小于最短导通时间 | should | high | spice(partial) |
| ANA-ARC-006 | 运放相位裕度目标 ≥ 45°，容性负载用隔离电阻 | should | high | spice(partial) |
| ANA-ARC-007 | ESP32-C3 内置 ADC 的误差与使用边界 | should | high | bench(partial) |
| ANA-ARC-009 | 称重电桥：排查引线电阻对比例测量的破坏 | should | high | bench(manual) |
| ANA-ARC-010 | 运放选型：偏置电流、源阻抗与温度 | should | medium | bom_check(partial) |
| ANA-ARC-004 | 按系统约束选择分流电阻位置 | consider | high | spice(partial) |
| ANA-ARC-008 | HX711 按需选数据率，并丢弃建立期数据 | consider | high | bench(partial) |

## 符号封装库（library）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| ANA-LIB-001 | 分流电阻用四端子封装并保留开尔文焊盘 | should | high | geometry_script(full) |

## 原理图（schematic）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| ANA-SCH-001 | SAR ADC 输入 RC：C ≥ 20 倍采样电容，用 C0G ⚠ | should | high | bom_check(full) |
| ANA-SCH-002 | Σ-Δ ADC 差分输入：Cdiff ≥ 10 × Ccm，R < 1 kΩ | should | high | bom_check(full) |
| ANA-SCH-003 | INA199 输入滤波：串联电阻 ≤ 10 Ω | should | high | bom_check(full) |
| ANA-SCH-004 | REF 接地时给零电流区留死区余量 | should | high | spice(partial) |
| ANA-SCH-005 | INA199 输出到 ADC 引脚：先串电阻再接 100 nF ⚠ | should | medium | spice(partial) |
| ANA-SCH-006 | 放大器输入保护：按手册限流（1–10 mA），注意钳位漏电 ⚠ | should | medium | bom_check(partial) |
| ANA-SCH-007 | HX711 的数字电源跟随 MCU，模拟电源去耦 | should | high | review(manual) |
| ANA-SCH-008 | HX711 输入共模电压要落在允许范围内 | should | high | bom_check(partial) |
| ANA-SCH-009 | NTC 热敏电阻：限制激励避免自热 | should | high | bom_check(full) |
| ANA-SCH-011 | 未使用的运放通道接成跟随器 | should | medium | erc(partial) |
| ANA-SCH-013 | 外部基准：先带限滤波，再用大电容去耦 | should | high | bom_check(partial) |
| ANA-SCH-010 | 热电偶前端：参考结与冷端传感器同处等温块 | consider | medium | review(manual) |
| ANA-SCH-012 | 模拟电源与数字电源之间加滤波 | consider | high | review(manual) |

## 网表与约束（netlist）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| ANA-NET-001 | 分流电阻的 sense 抽头用独立网络 | must | high | netlist_diff(full) |

## 叠层与规则（stackup）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| ANA-STK-001 | 给模拟信号层配一层完整的地 ⚠ | consider | medium | geometry_script(partial) |

## 分区规划（floorplan）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| ANA-FLR-001 | 把模拟区与数字/射频/开关区分开 | should | high | geometry_script(full) |
| ANA-FLR-002 | 精密元件远离热源和板边气流 | should | high | geometry_script(partial) |

## 器件布局（placement）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| ANA-PLC-001 | 分流电阻紧贴电流检测放大器 | should | high | geometry_script(full) |
| ANA-PLC-002 | 电流检测放大器的旁路电容贴脚且不打孔 | should | high | geometry_script(full) |
| ANA-PLC-003 | ADC 基准与电源电容贴近引脚的距离上限 | should | high | geometry_script(full) |
| ANA-PLC-004 | 匹配电阻同向、紧邻，沿等温线排布 | consider | high | geometry_script(full) |

## 布线（routing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| ANA-RTE-001 | 分流电阻到放大器必须用开尔文（四线）走线 | must | high | geometry_script(full) |
| ANA-RTE-002 | 两条 sense 线等长、等宽、同层并排 | should | high | geometry_script(full) |
| ANA-RTE-003 | 模拟输入走线远离开关节点和数字信号 | should | high | drc(full) |
| ANA-RTE-005 | 敏感模拟线下方保持连续的返回平面 | should | high | geometry_script(full) |
| ANA-RTE-004 | 高阻抗节点用保护环，且不要覆盖阻焊 ⚠ | consider | high | geometry_script(partial) |

## 平面与铺铜（plane_pour）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| ANA-PLN-001 | 整块地平面 + 分区走线，优先于分割 AGND/DGND ⚠ | should | high | geometry_script(partial) |
| ANA-PLN-002 | 转换器的 AGND/DGND 引脚在器件下方相连 ⚠ | should | medium | review(partial) |
| ANA-PLN-003 | 电机/大电流回路不穿过模拟地区 | consider | medium | geometry_script(partial) |

## 出图与制造（manufacturing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| ANA-MFG-001 | 出厂/首次上电做零点与增益两点校准 | should | high | bench(partial) |

## 签核验证（verification）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| ANA-VER-003 | 稳定性签核：环路增益 + 阶跃，覆盖角点条件 | must | high | spice(partial) |
| ANA-VER-005 | 实测 HX711 的 PD_SCK 时序，别触发掉电 | must | high | bench(partial) |
| ANA-VER-001 | SPICE 做最坏情况 + Monte Carlo + 温度扫描对账 | should | medium | spice(partial) |
| ANA-VER-002 | SPICE 噪声分析：积分噪声与 LSB 对比 | should | medium | spice(partial) |
| ANA-VER-004 | 输入短路噪声实测与有效分辨率 | should | high | bench(partial) |
