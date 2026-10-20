# 高压 / 隔离 / 安规 — 规则索引

23 条。⚠ = 来源之间有分歧。全文见 `rules.md`，用 `grep -n "<规则ID>" rules.md` 定位。

## 架构与选型（architecture）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HVS-ARC-001 | 先划分电压域：ELV/SELV 与危险电压 | must | medium | bom_check(partial) |
| HVS-ARC-002 | 每道隔离边界定义绝缘类型 | must | medium | review(manual) |
| HVS-ARC-006 | 锂电池包必须有电芯级保护 IC | must | medium | bom_check(partial) |
| HVS-ARC-003 | 查表前先确定五个输入参数 | should | high | review(manual) |
| HVS-ARC-004 | 海拔超过 2000 m 时间隙要乘修正系数 | should | medium | geometry_script(full) |
| HVS-ARC-005 | 隔离器件按额定值、封装爬电与 CTI 综合选型 | should | high | bom_check(partial) |

## 符号封装库（library）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HVS-LIB-001 | 高压器件封装库要校核焊盘间距与爬电 | should | low | geometry_script(partial) |

## 原理图（schematic）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HVS-SCH-001 | 电池输出串联保险丝或自恢复保险丝 | must | medium | bom_check(partial) |
| HVS-SCH-002 | 市电输入：保险丝必须配额定电压与分断能力，MOV 要受保护 | must | medium | bom_check(partial) |
| HVS-SCH-003 | 跨隔离栅的电容必须是安规 Y 电容 | must | low | bom_check(full) |

## 网表与约束（netlist）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HVS-NET-001 | 隔离两侧用独立网络名和网络类，让 DRC 能识别 | should | medium | netlist_diff(full) |

## 叠层与规则（stackup）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HVS-STK-001 | 板材 CTI 按数据手册定材料组 | should | medium | review(manual) |
| HVS-STK-002 | 低压（非安规）间距按 IPC-2221B 表设 DRC | should | medium | drc(full) |

## 分区规划（floorplan）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HVS-FLR-001 | 定义隔离栅禁布区，任何层都不得有铜跨越 | must | high | drc(full) |
| HVS-FLR-002 | 危险电压铜皮与板边、安装孔、外壳可触及件也要满足间距 | should | medium | drc(full) |

## 器件布局（placement）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HVS-PLC-001 | 焊盘不得缩短隔离器件封装的爬电与间隙 | must | high | geometry_script(full) |

## 布线（routing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HVS-RTE-001 | 按表取爬电距离，加强绝缘加倍 ⚠ | must | medium | drc(full) |
| HVS-RTE-002 | 开槽延长爬电距离，槽宽大于 1 mm 且不削弱板子 | should | high | geometry_script(partial) |
| HVS-RTE-003 | 电气间隙由瞬态过压定，单独核对，爬电不得小于间隙 | should | low | drc(full) |

## 平面与铺铜（plane_pour）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HVS-PLN-001 | 铺铜、热焊盘也受 HV 网络类间距约束 | should | medium | drc(full) |

## 出图与制造（manufacturing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HVS-MFG-001 | 涂覆或阻焊能否缩小间距要按标准确认 | consider | low | review(manual) |

## 签核验证（verification）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HVS-VER-001 | 用 KiCad 的 creepage 与 clearance 规则做 DRC | must | medium | drc(full) |
| HVS-VER-002 | 耐压测试：型式试验与出厂试验分开，夹具把两侧引脚各并联 | should | medium | bench(manual) |
