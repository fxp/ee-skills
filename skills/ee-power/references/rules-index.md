# 电源与功率 — 规则索引

54 条。⚠ = 来源之间有分歧。全文见 `rules.md`，用 `grep -n "<规则ID>" rules.md` 定位。

## 架构与选型（architecture）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| PWR-ARC-002 | 按最坏耗散核算 LDO 结温（SOT-223 AMS1117） ⚠ | must | high | bom_check(full) |
| PWR-ARC-003 | LDO 输入电压保持高于压差并留裕量 | must | high | spice(partial) |
| PWR-ARC-006 | 3.3 V 栅极驱动选用逻辑电平 MOSFET | must | high | bom_check(partial) |
| PWR-ARC-001 | 3.3 V 主电源按模块峰值电流留足裕量 | should | high | bom_check(partial) |
| PWR-ARC-004 | 全陶瓷输出场合选「陶瓷稳定」型 LDO | should | high | bom_check(partial) |
| PWR-ARC-005 | 降压电感按纹波比与峰值电流选型 | should | high | bom_check(full) |
| PWR-ARC-007 | 电机 MOSFET 按堵转电流核算导通损耗和结温 | should | high | bom_check(full) |

## 符号封装库（library）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| PWR-LIB-001 | 1117 类 SOT-223 的散热 tab 必须接 VOUT | must | high | netlist_diff(full) |
| PWR-LIB-002 | 四端子开尔文分流电阻封装要分开力端与感测端 | should | high | netlist_diff(full) |

## 原理图（schematic）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| PWR-SCH-007 | AMS1117 输出用满足 ESR 窗口的钽电容 ⚠ | must | high | bom_check(partial) |
| PWR-SCH-012 | 电机两端并联续流二极管并核算额定值 | must | medium | netlist_diff(full) |
| PWR-SCH-001 | 保险丝（PPTC）放在 TVS 上游 ⚠ | should | medium | review(partial) |
| PWR-SCH-002 | 提供真正串联的反接保护，并核算反接时的应力 | should | medium | spice(partial) |
| PWR-SCH-003 | PPTC 按最高环境温度下的保持电流选型 | should | medium | bom_check(partial) |
| PWR-SCH-004 | TVS 按击穿电压、钳位电压、峰值电流三条选型 | should | high | bom_check(full) |
| PWR-SCH-005 | 线缆热插拔的输入端抑制陶瓷电容谐振过冲 | should | medium | spice(partial) |
| PWR-SCH-006 | 陶瓷电容按直流偏置、温度、公差降额后再核算 | should | high | bom_check(partial) |
| PWR-SCH-008 | 限制 LDO 输出端并联的小陶瓷旁路电容 ⚠ | should | high | spice(partial) |
| PWR-SCH-009 | 降压输出电容按有效电容和穿越频率阻抗核算 | should | high | bom_check(full) |
| PWR-SCH-010 | 降压输入电容核算纹波有效值并并联高频旁路电容 | should | medium | bom_check(full) |
| PWR-SCH-011 | 电机 MOSFET 栅极加下拉电阻和串联电阻 | should | high | erc(full) |
| PWR-SCH-013 | 有刷电机接线端并联 0.1 uF 陶瓷电容 | should | medium | review(partial) |
| PWR-SCH-014 | 上电复位时序：电源稳定后再使能，慢速斜坡加监控芯片 | should | high | spice(full) |
| PWR-SCH-015 | 电源上的磁珠/LC 滤波器按偏置降额并阻尼 | should | medium | bom_check(full) |
| PWR-SCH-016 | 反馈分压与基准容差下的输出电压最坏情况 | should | medium | spice(full) |

## 叠层与规则（stackup）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| PWR-STK-001 | 按电流选外层铜厚并确认板厂实际铜厚 | consider | medium | tline_calc(partial) |

## 分区规划（floorplan）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| PWR-FLR-001 | 电机/开关电源功率区与模拟、射频区分区 | should | medium | geometry_script(partial) |
| PWR-FLR-002 | 电源入口按防护、储能、稳压顺序布局 | should | high | geometry_script(partial) |

## 器件布局（placement）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| PWR-PLC-001 | 先识别开关热回路，输入电容紧贴 IC 并最小化环路 | must | high | geometry_script(partial) |
| PWR-PLC-003 | 续流二极管与 IC 同层，短而宽直连 SW 和 GND | must | high | geometry_script(full) |
| PWR-PLC-002 | 高频旁路电容紧贴 VIN/GND，大电容可稍远 | should | high | geometry_script(full) |
| PWR-PLC-004 | 电感靠近 IC 但不必比输入电容更近，SW 铜皮最小 | should | high | geometry_script(partial) |
| PWR-PLC-006 | 升压变换器先放输出电容，再放电感和输入电容 | should | high | geometry_script(partial) |
| PWR-PLC-007 | LDO 输入输出电容靠近引脚，负载走线宽 | should | medium | geometry_script(partial) |
| PWR-PLC-005 | RC 缓冲电路跨接在 SW 与 GND 引脚上并按振铃频率定值 ⚠ | consider | high | spice(partial) |

## 布线（routing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| PWR-RTE-001 | SW 节点铜皮只留够载流的最小面积 ⚠ | must | high | geometry_script(full) |
| PWR-RTE-002 | 热回路走线不经过孔，必须时并联多孔 ⚠ | must | high | geometry_script(full) |
| PWR-RTE-003 | 反馈线短、远离 SW 与电感，取样点在输出电容处 ⚠ | must | high | geometry_script(partial) |
| PWR-RTE-005 | 大电流走线按 IPC-2152 和温升目标定宽 ⚠ | must | high | geometry_script(full) |
| PWR-RTE-007 | 电流检测放大器输入走开尔文线接到分流电阻焊盘 | must | high | geometry_script(full) |
| PWR-RTE-004 | 自举电容回路短，IC 地引脚走线同样要短 | should | high | geometry_script(partial) |
| PWR-RTE-006 | 换层大电流路径按电流估算并联过孔数量 ⚠ | should | medium | geometry_script(full) |
| PWR-RTE-008 | 3.3 V 电源走线按 Espressif 最小线宽 | should | high | geometry_script(full) |

## 平面与铺铜（plane_pour）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| PWR-PLN-001 | 变换器热回路下方保持连续地平面 ⚠ | should | medium | geometry_script(partial) |
| PWR-PLN-002 | 信号地与功率地在 IC 地点单点汇合 ⚠ | should | high | netlist_diff(full) |
| PWR-PLN-003 | 降压 IC 散热焊盘用 0.3 mm 小孔阵列接地 | should | high | geometry_script(full) |
| PWR-PLN-004 | 电机电流回路用独立地铜，单点接到逻辑地 | should | medium | geometry_script(partial) |

## 签核验证（verification）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| PWR-VER-001 | 开关电源环路增益相位裕量与穿越频率签核 ⚠ | must | high | spice(full) |
| PWR-VER-002 | 负载阶跃响应与 LDO 稳定性的 SPICE 与实测 | must | high | spice(full) |
| PWR-VER-004 | 电机启动/堵转期间核算电源轨跌落与欠压余量 | must | medium | spice(full) |
| PWR-VER-003 | 上电浪涌电流与热插拔电压过冲仿真 | should | medium | spice(full) |
| PWR-VER-005 | PDN 目标阻抗与电容网络反谐振检查 ⚠ | should | medium | pi_sim(partial) |
| PWR-VER-006 | 以正确探测方法测量 SW 节点振铃并核对余量 | should | high | spice(partial) |
| PWR-VER-007 | 估算效率与损耗预算并与热限比较 | consider | medium | bom_check(full) |
