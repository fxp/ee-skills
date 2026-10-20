# 低功耗 / 电池 — 规则索引

40 条。⚠ = 来源之间有分歧。全文见 `rules.md`，用 `grep -n "<规则ID>" rules.md` 定位。

## 架构与选型（architecture）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| LPW-ARC-012 | 无线突发电流下电源内阻不能把电压拉到下限以下 | must | high | bom_check(full) |
| LPW-ARC-001 | 先建立分状态的平均电流与电荷预算 | should | high | bom_check(partial) |
| LPW-ARC-002 | 用输入端折算公式核算常开轨待机电流 | should | high | bom_check(partial) |
| LPW-ARC-003 | 按真实负载曲线、终止电压和温度降额电池容量 ⚠ | should | high | bom_check(partial) |
| LPW-ARC-004 | 全板最高的最低工作电压决定电池终止电压 | should | high | bom_check(full) |
| LPW-ARC-005 | 按实际待机负载选稳压器，而不是只看标称 Iq | should | high | bom_check(partial) |
| LPW-ARC-006 | 线性稳压器的 Iq 是睡眠电流的下限 ⚠ | should | high | bom_check(partial) |
| LPW-ARC-007 | 用负载开关划分电源域，切断高漏电子系统 | should | high | bom_check(partial) |
| LPW-ARC-008 | 按唤醒源与保持内容选 MCU 睡眠模式（ESP32-C3） | should | high | netlist_diff(full) |
| LPW-ARC-011 | RTC 备份与超级电容容量必须计入漏电 | should | high | bom_check(partial) |
| LPW-ARC-009 | Wi-Fi 保持连接还是深睡重连，按平均电流预算选 | consider | high | bench(partial) |
| LPW-ARC-010 | 睡眠预算要计入 Flash 待机电流 | consider | high | bom_check(partial) |
| LPW-ARC-013 | 定时唤醒精度要求决定 RTC 慢时钟来源 | consider | medium | bench(partial) |

## 符号封装库（library）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| LPW-LIB-001 | 在符号或 BOM 里记录低功耗参数及其测试条件 | should | medium | bom_check(full) |

## 原理图（schematic）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| LPW-SCH-005 | 掉电域的信号要隔离，防止经 I/O 二极管反向供电 | must | high | bom_check(partial) |
| LPW-SCH-006 | 使能与栅极控制线在复位和深睡期间要有确定电平 | must | high | bom_check(full) |
| LPW-SCH-012 | 一次性锂电池的反向充电电流不得超过 1 µA | must | high | spice(partial) |
| LPW-SCH-001 | 核算常开轨上每条电阻支路的静态电流（V/R） | should | high | bom_check(partial) |
| LPW-SCH-002 | 睡眠期 GPIO 电平与外部上下拉必须一致 | should | medium | netlist_diff(partial) |
| LPW-SCH-003 | 未用引脚不得悬空，按芯片规定处理 ⚠ | should | high | erc(partial) |
| LPW-SCH-004 | 外部逻辑 IC 的输入不得悬空或长期处于半电平 ⚠ | should | high | erc(full) |
| LPW-SCH-007 | 电池电压监测不要用常通分压 | should | low | spice(partial) |
| LPW-SCH-008 | 指示灯是睡眠电流大户，要由 GPIO 驱动并在睡眠中熄灭 | should | medium | bom_check(full) |
| LPW-SCH-009 | 外设用自带掉电模式或断电，并保证睡眠中保持该状态（HX711） | should | high | netlist_diff(partial) |
| LPW-SCH-010 | INA199 没有关断脚，睡眠预算要含其 Iq 与 1 MΩ 泄漏路径 | should | high | bom_check(partial) |
| LPW-SCH-011 | 电池反接保护用低压降 FET，不用串联二极管 | should | high | bom_check(full) |
| LPW-SCH-013 | 缓慢升降或不稳定的电源要用电压监控器复位 | should | high | bench(partial) |
| LPW-SCH-014 | 常开轨和备份轨上的大电容要计漏电，优先低漏电类型 | should | medium | bom_check(partial) |

## 网表与约束（netlist）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| LPW-NET-001 | 用 BOM 加网表脚本核算常开轨漏电与 Iq 总和 | should | medium | bom_check(partial) |

## 器件布局（placement）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| LPW-PLC-001 | 突发负载的大电容放在电池或电源入口侧，按总电荷定容 | should | high | spice(partial) |

## 布线（routing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| LPW-RTE-002 | 突发电流路径要核算走线与过孔的 IR 压降 | should | medium | geometry_script(full) |
| LPW-RTE-001 | nA 级高阻节点要短走线并用双面保护环 | consider | medium | geometry_script(partial) |

## 出图与制造（manufacturing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| LPW-MFG-002 | 预留可单独测量睡眠电流的断点或测试点 | should | medium | bom_check(full) |
| LPW-MFG-001 | 对 nA 级高阻节点规定清洗与涂覆工艺并验证 | consider | medium | review(manual) |

## 签核验证（verification）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| LPW-VER-003 | 在真实板、真实固件、真实电压下验收睡眠电流 | must | high | bench(partial) |
| LPW-VER-005 | 无线突发时在负载端实测电压跌落与纹波 | must | high | bench(partial) |
| LPW-VER-001 | 选对测睡眠电流的仪表：burden 电压、量程与分辨率 | should | high | bench(manual) |
| LPW-VER-002 | 平均电流用整个占空周期的累计电荷来测 | should | high | bench(partial) |
| LPW-VER-004 | 睡眠电流要在高低温下复测，并按最坏温度做预算 | should | high | bench(partial) |
| LPW-VER-006 | 电池寿命模型要与实测对账，厂商工具只作初估 | consider | medium | bom_check(partial) |
