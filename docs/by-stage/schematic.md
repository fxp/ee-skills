# 原理图（schematic）

114 条规则 · 由 `catalog/*.yaml` 生成。详情见各领域文件。

## 通用 / 数模混合 MCU 板

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [GEN-SCH-004](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-004) | 为每个输入定义确定电平，不允许悬空 | must | high | erc (partial) |
| [GEN-SCH-005](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-005) | 执行器驱动脚在上电和复位期间必须保持关断 | must | high | erc (full) |
| [GEN-SCH-006](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-006) | strapping / boot 引脚按手册配置且不加冲突负载 | must | high | erc (partial) |
| [GEN-SCH-007](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-007) | 复位 / 使能引脚不得悬空并满足上电时序 | must | high | spice (partial) |
| [GEN-SCH-015](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-015) | 从数据手册典型电路出发并遵守元件限制说明 | must | high | spice (partial) |
| [GEN-SCH-001](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-001) | 按功能块组织原理图，页间只用层次标签连接 | should | medium | erc (full) |
| [GEN-SCH-002](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-002) | 电源轨用统一的电源符号并规范命名 | should | medium | erc (full) |
| [GEN-SCH-003](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-003) | 每个电源引脚（对）都画出规定值的去耦电容 | should | high | erc (partial) |
| [GEN-SCH-008](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-008) | 未用引脚按手册处理并显式标注 | should | high | erc (full) |
| [GEN-SCH-009](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-009) | 晶体负载电容按公式计算并留出杂散电容 | should | high | tline_calc (full) |
| [GEN-SCH-010](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-010) | 为每个可编程器件引出调试 / 烧录接口 | should | medium | erc (partial) |
| [GEN-SCH-011](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-011) | 在原理图中为电源轨和关键信号预留测试点 | should | medium | erc (full) |
| [GEN-SCH-012](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-012) | 全部元件完成标注，位号唯一且稳定 | should | high | erc (full) |
| [GEN-SCH-013](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-013) | 可选件和调试件标记 DNP 并保证属性两边一致 | should | high | bom_check (full) |
| [GEN-SCH-014](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-014) | 每个对外连接器线路都要有保护决策 | should | medium | erc (partial) |
| [GEN-SCH-016](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-016) | 关键位置标注容差、耐压和取值依据 | should | medium | bom_check (partial) |
| [GEN-SCH-017](../../skills/ee-general-pcb/references/rules.md#GEN-SCH-017) | I2C 上拉电阻按上升时间和灌电流计算 | should | high | tline_calc (full) |

## 电源与功率

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [PWR-SCH-007](../../skills/ee-power/references/rules.md#PWR-SCH-007) | AMS1117 输出用满足 ESR 窗口的钽电容 | must | high | bom_check (partial) |
| [PWR-SCH-012](../../skills/ee-power/references/rules.md#PWR-SCH-012) | 电机两端并联续流二极管并核算额定值 | must | medium | netlist_diff (full) |
| [PWR-SCH-001](../../skills/ee-power/references/rules.md#PWR-SCH-001) | 保险丝（PPTC）放在 TVS 上游 | should | medium | review (partial) |
| [PWR-SCH-002](../../skills/ee-power/references/rules.md#PWR-SCH-002) | 提供真正串联的反接保护，并核算反接时的应力 | should | medium | spice (partial) |
| [PWR-SCH-003](../../skills/ee-power/references/rules.md#PWR-SCH-003) | PPTC 按最高环境温度下的保持电流选型 | should | medium | bom_check (partial) |
| [PWR-SCH-004](../../skills/ee-power/references/rules.md#PWR-SCH-004) | TVS 按击穿电压、钳位电压、峰值电流三条选型 | should | high | bom_check (full) |
| [PWR-SCH-005](../../skills/ee-power/references/rules.md#PWR-SCH-005) | 线缆热插拔的输入端抑制陶瓷电容谐振过冲 | should | medium | spice (partial) |
| [PWR-SCH-006](../../skills/ee-power/references/rules.md#PWR-SCH-006) | 陶瓷电容按直流偏置、温度、公差降额后再核算 | should | high | bom_check (partial) |
| [PWR-SCH-008](../../skills/ee-power/references/rules.md#PWR-SCH-008) | 限制 LDO 输出端并联的小陶瓷旁路电容 | should | high | spice (partial) |
| [PWR-SCH-009](../../skills/ee-power/references/rules.md#PWR-SCH-009) | 降压输出电容按有效电容和穿越频率阻抗核算 | should | high | bom_check (full) |
| [PWR-SCH-010](../../skills/ee-power/references/rules.md#PWR-SCH-010) | 降压输入电容核算纹波有效值并并联高频旁路电容 | should | medium | bom_check (full) |
| [PWR-SCH-011](../../skills/ee-power/references/rules.md#PWR-SCH-011) | 电机 MOSFET 栅极加下拉电阻和串联电阻 | should | high | erc (full) |
| [PWR-SCH-013](../../skills/ee-power/references/rules.md#PWR-SCH-013) | 有刷电机接线端并联 0.1 uF 陶瓷电容 | should | medium | review (partial) |
| [PWR-SCH-014](../../skills/ee-power/references/rules.md#PWR-SCH-014) | 上电复位时序：电源稳定后再使能，慢速斜坡加监控芯片 | should | high | spice (full) |
| [PWR-SCH-015](../../skills/ee-power/references/rules.md#PWR-SCH-015) | 电源上的磁珠/LC 滤波器按偏置降额并阻尼 | should | medium | bom_check (full) |
| [PWR-SCH-016](../../skills/ee-power/references/rules.md#PWR-SCH-016) | 反馈分压与基准容差下的输出电压最坏情况 | should | medium | spice (full) |

## 低功耗 / 电池

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [LPW-SCH-005](../../skills/ee-low-power/references/rules.md#LPW-SCH-005) | 掉电域的信号要隔离，防止经 I/O 二极管反向供电 | must | high | bom_check (partial) |
| [LPW-SCH-006](../../skills/ee-low-power/references/rules.md#LPW-SCH-006) | 使能与栅极控制线在复位和深睡期间要有确定电平 | must | high | bom_check (full) |
| [LPW-SCH-012](../../skills/ee-low-power/references/rules.md#LPW-SCH-012) | 一次性锂电池的反向充电电流不得超过 1 µA | must | high | spice (partial) |
| [LPW-SCH-001](../../skills/ee-low-power/references/rules.md#LPW-SCH-001) | 核算常开轨上每条电阻支路的静态电流（V/R） | should | high | bom_check (partial) |
| [LPW-SCH-002](../../skills/ee-low-power/references/rules.md#LPW-SCH-002) | 睡眠期 GPIO 电平与外部上下拉必须一致 | should | medium | netlist_diff (partial) |
| [LPW-SCH-003](../../skills/ee-low-power/references/rules.md#LPW-SCH-003) | 未用引脚不得悬空，按芯片规定处理 | should | high | erc (partial) |
| [LPW-SCH-004](../../skills/ee-low-power/references/rules.md#LPW-SCH-004) | 外部逻辑 IC 的输入不得悬空或长期处于半电平 | should | high | erc (full) |
| [LPW-SCH-007](../../skills/ee-low-power/references/rules.md#LPW-SCH-007) | 电池电压监测不要用常通分压 | should | low | spice (partial) |
| [LPW-SCH-008](../../skills/ee-low-power/references/rules.md#LPW-SCH-008) | 指示灯是睡眠电流大户，要由 GPIO 驱动并在睡眠中熄灭 | should | medium | bom_check (full) |
| [LPW-SCH-009](../../skills/ee-low-power/references/rules.md#LPW-SCH-009) | 外设用自带掉电模式或断电，并保证睡眠中保持该状态（HX711） | should | high | netlist_diff (partial) |
| [LPW-SCH-010](../../skills/ee-low-power/references/rules.md#LPW-SCH-010) | INA199 没有关断脚，睡眠预算要含其 Iq 与 1 MΩ 泄漏路径 | should | high | bom_check (partial) |
| [LPW-SCH-011](../../skills/ee-low-power/references/rules.md#LPW-SCH-011) | 电池反接保护用低压降 FET，不用串联二极管 | should | high | bom_check (full) |
| [LPW-SCH-013](../../skills/ee-low-power/references/rules.md#LPW-SCH-013) | 缓慢升降或不稳定的电源要用电压监控器复位 | should | high | bench (partial) |
| [LPW-SCH-014](../../skills/ee-low-power/references/rules.md#LPW-SCH-014) | 常开轨和备份轨上的大电容要计漏电，优先低漏电类型 | should | medium | bom_check (partial) |

## 射频与天线

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [RF-SCH-001](../../skills/ee-rf/references/rules.md#RF-SCH-001) | 在天线馈点预留 π/T 匹配焊盘 | should | high | erc (partial) |
| [RF-SCH-002](../../skills/ee-rf/references/rules.md#RF-SCH-002) | 射频器件用 C0G、高 Q、SRF 不低于 2 倍工作频率 | should | high | bom_check (partial) |
| [RF-SCH-003](../../skills/ee-rf/references/rules.md#RF-SCH-003) | 射频线上可能有直流时串联隔直电容 | should | high | erc (partial) |
| [RF-SCH-004](../../skills/ee-rf/references/rules.md#RF-SCH-004) | 差分射频口经与芯片匹配的巴伦接天线 | should | high | netlist_diff (partial) |
| [RF-SCH-005](../../skills/ee-rf/references/rules.md#RF-SCH-005) | 发射链路保留谐波滤波并用 S21/谐波实测验收 | should | high | spice (partial) |
| [RF-SCH-006](../../skills/ee-rf/references/rules.md#RF-SCH-006) | 射频电源脚分级去耦并串 LC 隔离 | should | high | bom_check (partial) |
| [RF-SCH-007](../../skills/ee-rf/references/rules.md#RF-SCH-007) | 模组 3V3 脚旁放 10 µF + 0.1 µF，扛住发射电流尖峰 | should | high | spice (partial) |
| [RF-SCH-008](../../skills/ee-rf/references/rules.md#RF-SCH-008) | 预留传导测试口，射频线上不加探针测试点 | should | high | geometry_script (partial) |

## 音频

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [AUD-SCH-014](../../skills/ee-audio/references/rules.md#AUD-SCH-014) | 自举电容按数据手册的容量、介质和耐压选 | must | high | erc (full) |
| [AUD-SCH-001](../../skills/ee-audio/references/rules.md#AUD-SCH-001) | 信号通路电容用 C0G 或薄膜，慎用 X7R/X5R | should | high | bom_check (partial) |
| [AUD-SCH-002](../../skills/ee-audio/references/rules.md#AUD-SCH-002) | 按实际输入阻抗和有效容量核算 AC 耦合转折频率 | should | high | spice (partial) |
| [AUD-SCH-003](../../skills/ee-audio/references/rules.md#AUD-SCH-003) | 运放驱动容性负载时加隔离电阻并留相位裕度 | should | high | spice (partial) |
| [AUD-SCH-004](../../skills/ee-audio/references/rules.md#AUD-SCH-004) | 音频端口加 RF 低通：输入、BTL 输出和电源入口 | should | high | spice (partial) |
| [AUD-SCH-005](../../skills/ee-audio/references/rules.md#AUD-SCH-005) | 驻极体话筒偏置电阻、耦合电容和中点偏置滤波 | should | high | spice (partial) |
| [AUD-SCH-006](../../skills/ee-audio/references/rules.md#AUD-SCH-006) | 模拟 MEMS 话筒供电去耦、RF 滤波和耦合电容 | should | high | review (manual) |
| [AUD-SCH-007](../../skills/ee-audio/references/rules.md#AUD-SCH-007) | Codec 模拟电源独立稳压并滤波，MICBIAS 噪声同源 | should | high | spice (partial) |
| [AUD-SCH-008](../../skills/ee-audio/references/rules.md#AUD-SCH-008) | Codec 线路输出接 Class-D 输入前加 RC 低通 | should | high | spice (partial) |
| [AUD-SCH-009](../../skills/ee-audio/references/rules.md#AUD-SCH-009) | 抑制 pop/click：匹配输入网络、RC≤1 ms、使能时序 | should | high | spice (partial) |
| [AUD-SCH-010](../../skills/ee-audio/references/rules.md#AUD-SCH-010) | 耳机输出：隔直电容容量，或无电容架构的接线 | should | high | erc (partial) |
| [AUD-SCH-011](../../skills/ee-audio/references/rules.md#AUD-SCH-011) | Class-D 输出 LC 滤波器按二阶 Butterworth 设计 | should | high | spice (partial) |
| [AUD-SCH-012](../../skills/ee-audio/references/rules.md#AUD-SCH-012) | LC 滤波器电感和电容选型：线性度与降额 | should | high | bom_check (partial) |
| [AUD-SCH-013](../../skills/ee-audio/references/rules.md#AUD-SCH-013) | 免滤波 Class-D 的磁珠 EMI 滤波：电感性元件在前，禁止仅用电容 | should | high | spice (partial) |
| [AUD-SCH-015](../../skills/ee-audio/references/rules.md#AUD-SCH-015) | Class-D 电源引脚分级去耦和大容量电容 | should | high | bom_check (partial) |
| [AUD-SCH-016](../../skills/ee-audio/references/rules.md#AUD-SCH-016) | 平衡线路输入选高 CMRR 的差分接收器 | consider | medium | spice (partial) |

## 精密模拟 / 传感器前端

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [ANA-SCH-001](../../skills/ee-analog/references/rules.md#ANA-SCH-001) | SAR ADC 输入 RC：C ≥ 20 倍采样电容，用 C0G | should | high | bom_check (full) |
| [ANA-SCH-002](../../skills/ee-analog/references/rules.md#ANA-SCH-002) | Σ-Δ ADC 差分输入：Cdiff ≥ 10 × Ccm，R < 1 kΩ | should | high | bom_check (full) |
| [ANA-SCH-003](../../skills/ee-analog/references/rules.md#ANA-SCH-003) | INA199 输入滤波：串联电阻 ≤ 10 Ω | should | high | bom_check (full) |
| [ANA-SCH-004](../../skills/ee-analog/references/rules.md#ANA-SCH-004) | REF 接地时给零电流区留死区余量 | should | high | spice (partial) |
| [ANA-SCH-005](../../skills/ee-analog/references/rules.md#ANA-SCH-005) | INA199 输出到 ADC 引脚：先串电阻再接 100 nF | should | medium | spice (partial) |
| [ANA-SCH-006](../../skills/ee-analog/references/rules.md#ANA-SCH-006) | 放大器输入保护：按手册限流（1–10 mA），注意钳位漏电 | should | medium | bom_check (partial) |
| [ANA-SCH-007](../../skills/ee-analog/references/rules.md#ANA-SCH-007) | HX711 的数字电源跟随 MCU，模拟电源去耦 | should | high | review (manual) |
| [ANA-SCH-008](../../skills/ee-analog/references/rules.md#ANA-SCH-008) | HX711 输入共模电压要落在允许范围内 | should | high | bom_check (partial) |
| [ANA-SCH-009](../../skills/ee-analog/references/rules.md#ANA-SCH-009) | NTC 热敏电阻：限制激励避免自热 | should | high | bom_check (full) |
| [ANA-SCH-011](../../skills/ee-analog/references/rules.md#ANA-SCH-011) | 未使用的运放通道接成跟随器 | should | medium | erc (partial) |
| [ANA-SCH-013](../../skills/ee-analog/references/rules.md#ANA-SCH-013) | 外部基准：先带限滤波，再用大电容去耦 | should | high | bom_check (partial) |
| [ANA-SCH-010](../../skills/ee-analog/references/rules.md#ANA-SCH-010) | 热电偶前端：参考结与冷端传感器同处等温块 | consider | medium | review (manual) |
| [ANA-SCH-012](../../skills/ee-analog/references/rules.md#ANA-SCH-012) | 模拟电源与数字电源之间加滤波 | consider | high | review (manual) |

## 高速数字

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HSD-SCH-002](../../skills/ee-high-speed/references/rules.md#HSD-SCH-002) | LVDS 接收端用 100 Ω（±2%）差分端接电阻 | must | high | bom_check (full) |
| [HSD-SCH-004](../../skills/ee-high-speed/references/rules.md#HSD-SCH-004) | 按协议决定是否串联隔直电容及其值和封装 | must | high | bom_check (full) |
| [HSD-SCH-006](../../skills/ee-high-speed/references/rules.md#HSD-SCH-006) | USB-C 受电设备在 CC1、CC2 各接 5.1 kΩ 下拉 | must | high | erc (full) |
| [HSD-SCH-009](../../skills/ee-high-speed/references/rules.md#HSD-SCH-009) | DDR3 的 Vref 与 VTT 用 1% 分压并就近去耦 | must | high | erc (full) |
| [HSD-SCH-010](../../skills/ee-high-speed/references/rules.md#HSD-SCH-010) | 按总线电容和模式计算 I2C 上拉电阻窗口 | must | high | bom_check (partial) |
| [HSD-SCH-001](../../skills/ee-high-speed/references/rules.md#HSD-SCH-001) | 单端输出在驱动端串联 Rs = Z0 − Ro | should | high | erc (partial) |
| [HSD-SCH-003](../../skills/ee-high-speed/references/rules.md#HSD-SCH-003) | 原生 USB 数据线预留串联电阻与对地电容位 | should | high | erc (partial) |
| [HSD-SCH-005](../../skills/ee-high-speed/references/rules.md#HSD-SCH-005) | 按接口速率选择 ESD 器件的电容、工作电压与等级 | should | high | bom_check (partial) |
| [HSD-SCH-007](../../skills/ee-high-speed/references/rules.md#HSD-SCH-007) | USB VBUS 加 TVS，钳位电压低于下游耐压并按 PD 电压档选型 | should | high | bom_check (partial) |
| [HSD-SCH-008](../../skills/ee-high-speed/references/rules.md#HSD-SCH-008) | 以太网磁件侧按规范配置 Bob Smith 端接与 49.9 Ω 上拉 | should | high | bom_check (partial) |
| [HSD-SCH-011](../../skills/ee-high-speed/references/rules.md#HSD-SCH-011) | 连接器引脚分配保证差分对相邻同排并配回流地针 | should | high | erc (partial) |

## EMC / ESD / 浪涌

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [EMC-SCH-008](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-008) | TVS 按 VRWM、VBR、VC、IPP、电容选型 | must | high | bom_check (partial) |
| [EMC-SCH-009](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-009) | 所有用户可触及端口和电源入口都要有 ESD 路径 | must | high | geometry_script (partial) |
| [EMC-SCH-001](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-001) | MCU 输出/时钟脚串联阻尼电阻 | should | high | geometry_script (partial) |
| [EMC-SCH-002](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-002) | EN/复位类敏感脚：短走线加 RC，不加大电容 | should | high | erc (partial) |
| [EMC-SCH-004](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-004) | 磁珠按直流偏置降额，不看 100 MHz 标称阻抗 | should | high | bom_check (partial) |
| [EMC-SCH-005](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-005) | 磁珠要在噪声频段呈电阻性，且与电容的 LC 需阻尼 | should | high | spice (full) |
| [EMC-SCH-006](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-006) | 出机壳的线在连接器处加小电容到机壳/屏蔽地 | should | high | geometry_script (partial) |
| [EMC-SCH-010](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-010) | 保险丝与 TVS 的先后顺序要显式决定 | should | medium | review (manual) |
| [EMC-SCH-012](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-012) | 电机端子并联陶瓷电容（跨端子 + 对外壳） | should | medium | spice (partial) |
| [EMC-SCH-013](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-013) | 感性负载必须有续流/钳位路径 | should | medium | spice (full) |
| [EMC-SCH-003](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-003) | IC 供电用磁珠 + 旁路电容做 π 型滤波 | consider | high | spice (partial) |
| [EMC-SCH-007](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-007) | 线缆共模电流大时用共模扼流圈或磁环 | consider | medium | bom_check (partial) |
| [EMC-SCH-011](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-011) | GDT/MOV/TVS/保险丝各司其职并配合使用 | consider | medium | spice (partial) |
| [EMC-SCH-014](../../skills/ee-emc-esd/references/rules.md#EMC-SCH-014) | 连接器金属壳/机壳地与信号地的连接方式要显式决定 | consider | medium | review (manual) |

## 高压 / 隔离 / 安规

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HVS-SCH-001](../../skills/ee-hv-safety/references/rules.md#HVS-SCH-001) | 电池输出串联保险丝或自恢复保险丝 | must | medium | bom_check (partial) |
| [HVS-SCH-002](../../skills/ee-hv-safety/references/rules.md#HVS-SCH-002) | 市电输入：保险丝必须配额定电压与分断能力，MOV 要受保护 | must | medium | bom_check (partial) |
| [HVS-SCH-003](../../skills/ee-hv-safety/references/rules.md#HVS-SCH-003) | 跨隔离栅的电容必须是安规 Y 电容 | must | low | bom_check (full) |

## 可制造 / 可装配 / 可测试

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [DFM-SCH-001](../../skills/ee-dfm/references/rules.md#DFM-SCH-001) | 原理图符号里带 LCSC 料号字段和 DNP 标记 | should | medium | bom_check (full) |
| [DFM-SCH-002](../../skills/ee-dfm/references/rules.md#DFM-SCH-002) | 在原理图里预留固件下载与调试入口 | should | medium | erc (partial) |
