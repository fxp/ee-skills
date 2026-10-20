# 高速数字 — 规则索引

52 条。⚠ = 来源之间有分歧。全文见 `rules.md`，用 `grep -n "<规则ID>" rules.md` 定位。

## 架构与选型（architecture）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HSD-ARC-002 | 按接口确定差分/单端目标阻抗与公差 ⚠ | must | high | tline_calc(partial) |
| HSD-ARC-001 | 按边沿长度 1/6 判断走线是否需按传输线处理 ⚠ | should | high | geometry_script(partial) |
| HSD-ARC-003 | 高速接口板按速率确定最少层数 ⚠ | should | medium | review(manual) |
| HSD-ARC-004 | DDR3 点对点驱动、走线、ODT 阻抗三者匹配 ⚠ | should | high | si_sim(partial) |
| HSD-ARC-005 | 选定 DDR 地址/命令拓扑（树形或 fly-by）并写入约束 ⚠ | should | high | si_sim(partial) |

## 原理图（schematic）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HSD-SCH-002 | LVDS 接收端用 100 Ω（±2%）差分端接电阻 | must | high | bom_check(full) |
| HSD-SCH-004 | 按协议决定是否串联隔直电容及其值和封装 ⚠ | must | high | bom_check(full) |
| HSD-SCH-006 | USB-C 受电设备在 CC1、CC2 各接 5.1 kΩ 下拉 | must | high | erc(full) |
| HSD-SCH-009 | DDR3 的 Vref 与 VTT 用 1% 分压并就近去耦 | must | high | erc(full) |
| HSD-SCH-010 | 按总线电容和模式计算 I2C 上拉电阻窗口 | must | high | bom_check(partial) |
| HSD-SCH-001 | 单端输出在驱动端串联 Rs = Z0 − Ro | should | high | erc(partial) |
| HSD-SCH-003 | 原生 USB 数据线预留串联电阻与对地电容位 ⚠ | should | high | erc(partial) |
| HSD-SCH-005 | 按接口速率选择 ESD 器件的电容、工作电压与等级 | should | high | bom_check(partial) |
| HSD-SCH-007 | USB VBUS 加 TVS，钳位电压低于下游耐压并按 PD 电压档选型 | should | high | bom_check(partial) |
| HSD-SCH-008 | 以太网磁件侧按规范配置 Bob Smith 端接与 49.9 Ω 上拉 ⚠ | should | high | bom_check(partial) |
| HSD-SCH-011 | 连接器引脚分配保证差分对相邻同排并配回流地针 | should | high | erc(partial) |

## 网表与约束（netlist）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HSD-NET-001 | 差分对网络按同基名加 P/N 或 +/- 后缀命名 | must | high | netlist_diff(full) |
| HSD-NET-002 | DDR 信号分网络类与字节通道，限定可交换范围 | should | high | netlist_diff(full) |
| HSD-NET-003 | 在 .kicad_dru 中为高速网络类写长度/偏斜/间距规则 ⚠ | should | high | drc(full) |
| HSD-NET-004 | 把走线失配预算化为时序裕量的 1% | should | high | geometry_script(partial) |

## 叠层与规则（stackup）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HSD-STK-001 | 高速线紧邻完整 GND 参考面，外层微带优先 ⚠ | must | high | geometry_script(full) |
| HSD-STK-002 | 用板厂实际叠层参数计算阻抗，写明受控线所在层 ⚠ | should | medium | tline_calc(partial) |
| HSD-STK-003 | 长距离高速差分对对抗玻纤编织偏斜 | consider | high | geometry_script(partial) |

## 分区规划（floorplan）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HSD-FLR-001 | 以太网前端分区：PHY、磁件、RJ45 的距离与隔离 ⚠ | should | medium | geometry_script(full) |
| HSD-FLR-002 | DDR 通道专用走线区，SDRAM 与 SoC 同面 | should | high | geometry_script(partial) |

## 器件布局（placement）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HSD-PLC-001 | 连接器侧保护链按 ESD、共模滤波、隔直电容的顺序放置 ⚠ | should | high | geometry_script(partial) |
| HSD-PLC-002 | 差分对上的隔直电容和 ESD 焊盘对称放置并挖空参考面 | should | high | geometry_script(partial) |
| HSD-PLC-003 | 端接电阻按类型放在驱动端或接收端，stub 尽量短 | should | high | geometry_script(full) |
| HSD-PLC-004 | 高速 IC 每个电源脚就近去耦，小电容最近，过孔贴焊盘 ⚠ | should | high | geometry_script(full) |

## 布线（routing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HSD-RTE-002 | 按接口限定差分对内偏斜 ⚠ | must | high | drc(full) |
| HSD-RTE-005 | 高速线全程走在连续参考面上，远离参考面边缘和空洞 | must | high | geometry_script(full) |
| HSD-RTE-012 | DDR3 地址/命令/控制线 fly-by 走线规则 ⚠ | must | high | drc(partial) |
| HSD-RTE-013 | DDR3 数据、DQS 与时钟对的匹配和过孔规则 | must | high | drc(full) |
| HSD-RTE-001 | 差分对全程对称平行，未耦合段只允许出现在引出和连接器处 | should | high | drc(full) |
| HSD-RTE-003 | 在失配发生处就近做局部蛇形补偿，几何满足间距要求 ⚠ | should | high | geometry_script(partial) |
| HSD-RTE-004 | 按接口取线对间距并避开时钟线，相邻层正交布线 ⚠ | should | high | drc(full) |
| HSD-RTE-006 | 换层过孔旁就近放地缝合过孔，且差分两线过孔对称 | should | high | geometry_script(full) |
| HSD-RTE-007 | 控制过孔残桩 < 15 mil，反焊盘加大，通孔连接器从底层进线 ⚠ | should | high | geometry_script(partial) |
| HSD-RTE-008 | 限制每条高速线的过孔数，两线保持一致 ⚠ | should | high | drc(full) |
| HSD-RTE-009 | 高速线总长不超过接口与器件的限值 ⚠ | should | high | drc(full) |
| HSD-RTE-010 | 高速线少拐弯，拐角不小于 135° | should | high | geometry_script(full) |
| HSD-RTE-011 | 高速差分线不放测试点，远离晶振、开关电源和磁性器件 ⚠ | should | high | geometry_script(full) |
| HSD-RTE-014 | 2 层板上的 FS USB 差分线：短、等长、下方整面地 ⚠ | should | medium | tline_calc(partial) |

## 平面与铺铜（plane_pour）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HSD-PLN-001 | 按目标阻抗法设计高速 IC 的电源分配网络 ⚠ | should | high | pi_sim(partial) |
| HSD-PLN-002 | 以太网磁件下无铜，机壳地与数字地隔离 ⚠ | should | high | geometry_script(full) |
| HSD-PLN-003 | 高速线两侧铺地时保持 3–5 倍线宽间隙，缝合需验证 ⚠ | consider | medium | drc(full) |

## 出图与制造（manufacturing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HSD-MFG-001 | 下单时声明阻抗控制层、目标值、公差和叠层 ⚠ | must | medium | bom_check(partial) |

## 签核验证（verification）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| HSD-VER-002 | 出板前用自定义规则跑 DRC，并核对长度口径 | must | high | drc(full) |
| HSD-VER-001 | 布线后按实际线宽间距逐段复算受控线阻抗 ⚠ | should | medium | geometry_script(partial) |
| HSD-VER-003 | 用传输线模型仿真端接，并联合 IBIS 做高速总线 SI 仿真 ⚠ | should | high | spice(partial) |
| HSD-VER-005 | 签核前对高速 IC 电源轨做 PDN 阻抗仿真 | should | medium | pi_sim(partial) |
| HSD-VER-004 | 用 TDR/VNA 实测阻抗与 S 参数，脚本化后处理 ⚠ | consider | medium | em_sim(partial) |
