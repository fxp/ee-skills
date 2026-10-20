# 射频与天线 — 规则索引

45 条。⚠ = 来源之间有分歧。全文见 `rules.md`，用 `grep -n "<规则ID>" rules.md` 定位。

## 架构与选型（architecture）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| RF-ARC-002 | 按法规限值选功率、天线增益与杂散抑制 | must | high | review(partial) |
| RF-ARC-004 | 不要改动预认证模组的天线与匹配配置 | must | high | bom_check(partial) |
| RF-ARC-001 | 用 Friis 公式做链路预算并留衰落余量 | should | medium | review(partial) |
| RF-ARC-003 | 优先选预认证射频模组，量大再做分立射频 | should | medium | bom_check(partial) |
| RF-ARC-006 | GNSS 无源天线馈线不超过 10 cm，更长用有源天线 | should | high | geometry_script(full) |
| RF-ARC-005 | 按频段、面积、高度和成本选天线类型 | consider | high | review(manual) |

## 符号封装库（library）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| RF-LIB-001 | 天线/模组封装自带厂商禁布区并保持不改 | should | high | drc(full) |

## 原理图（schematic）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| RF-SCH-001 | 在天线馈点预留 π/T 匹配焊盘 | should | high | erc(partial) |
| RF-SCH-002 | 射频器件用 C0G、高 Q、SRF 不低于 2 倍工作频率 | should | high | bom_check(partial) |
| RF-SCH-003 | 射频线上可能有直流时串联隔直电容 | should | high | erc(partial) |
| RF-SCH-004 | 差分射频口经与芯片匹配的巴伦接天线 | should | high | netlist_diff(partial) |
| RF-SCH-005 | 发射链路保留谐波滤波并用 S21/谐波实测验收 | should | high | spice(partial) |
| RF-SCH-006 | 射频电源脚分级去耦并串 LC 隔离 | should | high | bom_check(partial) |
| RF-SCH-007 | 模组 3V3 脚旁放 10 µF + 0.1 µF，扛住发射电流尖峰 ⚠ | should | high | spice(partial) |
| RF-SCH-008 | 预留传导测试口，射频线上不加探针测试点 | should | high | geometry_script(partial) |

## 网表与约束（netlist）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| RF-NET-001 | 射频网络单独设网络类，线宽恒定、不分支 | should | medium | drc(full) |

## 叠层与规则（stackup）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| RF-STK-001 | 用板厂实际叠层算 50 Ω 线宽，并接受 Dk 与阻抗公差 ⚠ | should | high | tline_calc(partial) |
| RF-STK-002 | 50 Ω 馈线优先用带地共面波导（CPWG） | should | high | tline_calc(full) |
| RF-STK-003 | 分立射频优先 4 层；2 层板底层须为整块实心地 ⚠ | should | high | geometry_script(full) |

## 分区规划（floorplan）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| RF-FLR-001 | 天线放板边或板角，馈点贴近板边，辐射部分悬出板外 | must | high | geometry_script(partial) |
| RF-FLR-002 | 天线禁布区内所有铜层禁铜、禁线、禁件、禁螺丝 | must | high | drc(full) |
| RF-FLR-003 | 外壳内天线周围留净空，金属件远离天线 ⚠ | should | high | review(partial) |
| RF-FLR-004 | 天线远离晶振、高速时钟、开关电源、电机以及 USB/UART | should | medium | geometry_script(partial) |
| RF-FLR-005 | 单极类天线按厂商参考板提供足够的地平面 | should | high | geometry_script(partial) |
| RF-FLR-006 | 多天线或收发之间拉开距离、正交放置 | consider | high | em_sim(partial) |

## 器件布局（placement）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| RF-PLC-001 | 匹配网络紧贴芯片 RF 脚和天线馈点，元件相互靠近 | should | high | geometry_script(partial) |
| RF-PLC-002 | 射频电源脚去耦：小值最近、同层、各自接地过孔 | should | high | geometry_script(full) |

## 布线（routing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| RF-RTE-001 | 射频线按 50 Ω 设计，线宽（及间隙）全程恒定 | must | high | geometry_script(full) |
| RF-RTE-005 | 射频线下方参考地完整，其他走线不穿越、不并行靠近 | must | high | geometry_script(partial) |
| RF-RTE-002 | 射频线尽量短，无短截线、分支和测试点 | should | high | geometry_script(full) |
| RF-RTE-003 | 射频线拐弯用圆弧或 135° 折线，不画未切角的直角 ⚠ | should | high | geometry_script(full) |
| RF-RTE-004 | 射频路径上不打过孔 | should | high | geometry_script(full) |

## 平面与铺铜（plane_pour）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| RF-PLN-001 | 射频区地平面整块不分割，芯片底焊盘多打过孔 | must | high | drc(full) |
| RF-PLN-002 | 接地缝合过孔间距不超过 λ/20（按介质内波长） ⚠ | should | high | geometry_script(full) |
| RF-PLN-003 | 并联接地元件的地脚旁紧贴独立接地过孔 | should | high | geometry_script(partial) |
| RF-PLN-004 | 匹配区走线和焊盘到邻近地铜至少 0.5 mm | should | medium | drc(full) |
| RF-PLN-005 | 射频路径下的内层：按厂商参考叠层选实心地或整片禁布 ⚠ | should | medium | geometry_script(partial) |

## 出图与制造（manufacturing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| RF-MFG-001 | 下单前锁定叠层与阻抗要求，换板厂须重算射频线宽 | should | high | geometry_script(partial) |

## 签核验证（verification）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| RF-VER-001 | 天线端回波损耗 S11 <= -10 dB 覆盖整个工作频段 | should | high | bench(full) |
| RF-VER-002 | 用 VNA 测天线：校准到参考面，在最终外壳和手持下复测 | should | high | bench(manual) |
| RF-VER-003 | 板子回来后用 Smith 圆图调 π 匹配网络 | should | high | spice(partial) |
| RF-VER-004 | 定制 PCB 天线先做电磁仿真再投板 | should | medium | em_sim(partial) |
| RF-VER-005 | 用传导口预扫发射功率、谐波与杂散 | should | high | bench(manual) |
| RF-VER-006 | 在最终产品上实测吞吐量与通信距离 | should | high | bench(manual) |
| RF-VER-007 | 用 SPICE/S 参数先仿匹配网络（含元件寄生） | consider | medium | spice(partial) |
