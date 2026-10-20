# EMC / ESD / 浪涌 — 规则索引

46 条。⚠ = 来源之间有分歧。全文见 `rules.md`，用 `grep -n "<规则ID>" rules.md` 定位。

## 架构与选型（architecture）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| EMC-ARC-002 | ESD 目标等级按产品标准定，不靠 IC 的 HBM/CDM | must | high | bom_check(partial) |
| EMC-ARC-001 | 按源—路径—受害者拆解每个 EMC 问题 | should | high | review(manual) |
| EMC-ARC-003 | 按端口确定 EFT 与浪涌等级和性能判据 | should | high | review(manual) |
| EMC-ARC-004 | 边沿速率与时钟频率取满足时序的最慢值 | should | high | si_sim(partial) |
| EMC-ARC-005 | 展频时钟只降峰值不降总能量，先评估时序 | consider | medium | emc_precompliance(manual) |

## 原理图（schematic）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| EMC-SCH-008 | TVS 按 VRWM、VBR、VC、IPP、电容选型 | must | high | bom_check(partial) |
| EMC-SCH-009 | 所有用户可触及端口和电源入口都要有 ESD 路径 | must | high | geometry_script(partial) |
| EMC-SCH-001 | MCU 输出/时钟脚串联阻尼电阻 ⚠ | should | high | geometry_script(partial) |
| EMC-SCH-002 | EN/复位类敏感脚：短走线加 RC，不加大电容 | should | high | erc(partial) |
| EMC-SCH-004 | 磁珠按直流偏置降额，不看 100 MHz 标称阻抗 ⚠ | should | high | bom_check(partial) |
| EMC-SCH-005 | 磁珠要在噪声频段呈电阻性，且与电容的 LC 需阻尼 | should | high | spice(full) |
| EMC-SCH-006 | 出机壳的线在连接器处加小电容到机壳/屏蔽地 | should | high | geometry_script(partial) |
| EMC-SCH-010 | 保险丝与 TVS 的先后顺序要显式决定 ⚠ | should | medium | review(manual) |
| EMC-SCH-012 | 电机端子并联陶瓷电容（跨端子 + 对外壳） ⚠ | should | medium | spice(partial) |
| EMC-SCH-013 | 感性负载必须有续流/钳位路径 | should | medium | spice(full) |
| EMC-SCH-003 | IC 供电用磁珠 + 旁路电容做 π 型滤波 | consider | high | spice(partial) |
| EMC-SCH-007 | 线缆共模电流大时用共模扼流圈或磁环 | consider | medium | bom_check(partial) |
| EMC-SCH-011 | GDT/MOV/TVS/保险丝各司其职并配合使用 | consider | medium | spice(partial) |
| EMC-SCH-014 | 连接器金属壳/机壳地与信号地的连接方式要显式决定 ⚠ | consider | medium | review(manual) |

## 叠层与规则（stackup）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| EMC-STK-001 | 两层板：栅格化地 + 电源地叠放，逼近四层效果 | should | high | geometry_script(partial) |
| EMC-STK-002 | 20H 规则有争议，不当作强制规则 ⚠ | consider | medium | em_sim(partial) |

## 分区规划（floorplan）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| EMC-FLR-003 | 连接器到 TVS 之间划 ESD 入口禁布区 | must | high | geometry_script(full) |
| EMC-FLR-001 | 按功能分区，高速逻辑靠电源入口，模拟远离 | should | high | geometry_script(partial) |
| EMC-FLR-002 | 连接器集中在板边一侧，ESD 敏感电路放中央 | should | high | geometry_script(partial) |
| EMC-FLR-004 | 电机/继电器/驱动区与 MCU 和模拟采样区分开 | should | medium | geometry_script(partial) |
| EMC-FLR-005 | MCU 靠稳压器，稳压器靠供电入口，地在三者间单点参考 ⚠ | should | medium | geometry_script(partial) |
| EMC-FLR-006 | 线缆屏蔽层 360° 端接到壳体，禁用长辫子 | consider | low | review(manual) |

## 器件布局（placement）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| EMC-PLC-001 | TVS 紧靠连接器引脚，被保护 IC 远离 TVS | must | high | geometry_script(full) |
| EMC-PLC-002 | 阻尼电阻贴驱动脚，I/O 旁路电容贴连接器 | should | high | geometry_script(partial) |
| EMC-PLC-003 | 去耦电容贴电源脚，回路面积最小 | should | high | geometry_script(full) |
| EMC-PLC-004 | 电机抑制电容和续流件贴电机/感性负载 | should | medium | geometry_script(partial) |

## 布线（routing）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| EMC-RTE-001 | 每条快速信号下方保持连续回流路径 | must | high | geometry_script(full) |
| EMC-RTE-003 | ESD 入口走线直通 TVS，无 stub、无过孔、拐角 ≤45° | must | high | geometry_script(full) |
| EMC-RTE-004 | TVS 地脚接同层地铺铜，紧邻过孔缝合到相邻地层 | must | high | geometry_script(full) |
| EMC-RTE-002 | 不跨平面分割/槽走线，必须跨时加缝合电容 | should | high | geometry_script(full) |
| EMC-RTE-005 | 快沿/时钟走线要短，超过阈值要端接 | should | high | geometry_script(full) |
| EMC-RTE-006 | ESD 路径和快沿线避免 90° 拐角（有条件） ⚠ | consider | medium | geometry_script(full) |

## 平面与铺铜（plane_pour）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| EMC-PLN-001 | 两层板地铺铜栅格化，消除只有一端连接的地岛 | should | high | geometry_script(full) |
| EMC-PLN-003 | 机壳/屏蔽地铜区：宽、短、至少两颗螺丝 | should | high | geometry_script(partial) |
| EMC-PLN-002 | 板边地环与缝合过孔间距小于 λ/20 ⚠ | consider | low | geometry_script(full) |

## 签核验证（verification）

| ID | 标题 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| EMC-VER-002 | ESD 测试：金属壳打壳体接触放电，绝缘件打空气放电 | must | high | bench(manual) |
| EMC-VER-001 | 用 LISN 做传导发射预兼容，两根线分别扫 | should | medium | emc_precompliance(manual) |
| EMC-VER-003 | ESD 仿真：IEC 枪模型 + TVS + 寄生电感估算 VESD | should | high | spice(partial) |
| EMC-VER-004 | EFT 抗扰测试：双极性、每端口不少于 1 分钟 | should | high | bench(manual) |
| EMC-VER-005 | 电机启停/堵转时在板上抓供电、EN 和采样 | should | medium | bench(manual) |
| EMC-VER-006 | 样机阶段逐个拆装滤波件，只保留有实测收益的 | consider | medium | bom_check(partial) |
