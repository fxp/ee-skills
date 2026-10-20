# 架构与选型（architecture）

79 条规则 · 由 `catalog/*.yaml` 生成。详情见各领域文件。

## 通用 / 数模混合 MCU 板

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [GEN-ARC-007](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-007) | 按电源轨做功耗预算并计入峰值电流 | must | high | bom_check (full) |
| [GEN-ARC-009](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-009) | 核对每条数字链路的电平兼容与过压 | must | high | review (partial) |
| [GEN-ARC-001](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-001) | 需求逐条分配到设计元素并指定验证方法 | should | medium | review (partial) |
| [GEN-ARC-002](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-002) | 按产品等级对元件电压 / 电流 / 功率降额 | should | high | bom_check (partial) |
| [GEN-ARC-003](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-003) | 陶瓷电容按直流偏压后的有效容值取值 | should | high | bom_check (partial) |
| [GEN-ARC-004](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-004) | 选型时核对生命周期并为关键件备好替代料 | should | medium | bom_check (partial) |
| [GEN-ARC-005](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-005) | 封装与器件选择要匹配贴片厂的库和工艺 | should | high | bom_check (full) |
| [GEN-ARC-006](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-006) | MCU / 模块选型前做引脚预算并剔除受限引脚 | should | high | review (partial) |
| [GEN-ARC-008](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-008) | 先定上电时序与复位释放条件 | should | high | spice (partial) |
| [GEN-ARC-010](../../skills/ee-general-pcb/references/rules.md#GEN-ARC-010) | 连接器按触点数与温度折算电流并防插错 | should | medium | bom_check (partial) |

## 电源与功率

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [PWR-ARC-002](../../skills/ee-power/references/rules.md#PWR-ARC-002) | 按最坏耗散核算 LDO 结温（SOT-223 AMS1117） | must | high | bom_check (full) |
| [PWR-ARC-003](../../skills/ee-power/references/rules.md#PWR-ARC-003) | LDO 输入电压保持高于压差并留裕量 | must | high | spice (partial) |
| [PWR-ARC-006](../../skills/ee-power/references/rules.md#PWR-ARC-006) | 3.3 V 栅极驱动选用逻辑电平 MOSFET | must | high | bom_check (partial) |
| [PWR-ARC-001](../../skills/ee-power/references/rules.md#PWR-ARC-001) | 3.3 V 主电源按模块峰值电流留足裕量 | should | high | bom_check (partial) |
| [PWR-ARC-004](../../skills/ee-power/references/rules.md#PWR-ARC-004) | 全陶瓷输出场合选「陶瓷稳定」型 LDO | should | high | bom_check (partial) |
| [PWR-ARC-005](../../skills/ee-power/references/rules.md#PWR-ARC-005) | 降压电感按纹波比与峰值电流选型 | should | high | bom_check (full) |
| [PWR-ARC-007](../../skills/ee-power/references/rules.md#PWR-ARC-007) | 电机 MOSFET 按堵转电流核算导通损耗和结温 | should | high | bom_check (full) |

## 低功耗 / 电池

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [LPW-ARC-012](../../skills/ee-low-power/references/rules.md#LPW-ARC-012) | 无线突发电流下电源内阻不能把电压拉到下限以下 | must | high | bom_check (full) |
| [LPW-ARC-001](../../skills/ee-low-power/references/rules.md#LPW-ARC-001) | 先建立分状态的平均电流与电荷预算 | should | high | bom_check (partial) |
| [LPW-ARC-002](../../skills/ee-low-power/references/rules.md#LPW-ARC-002) | 用输入端折算公式核算常开轨待机电流 | should | high | bom_check (partial) |
| [LPW-ARC-003](../../skills/ee-low-power/references/rules.md#LPW-ARC-003) | 按真实负载曲线、终止电压和温度降额电池容量 | should | high | bom_check (partial) |
| [LPW-ARC-004](../../skills/ee-low-power/references/rules.md#LPW-ARC-004) | 全板最高的最低工作电压决定电池终止电压 | should | high | bom_check (full) |
| [LPW-ARC-005](../../skills/ee-low-power/references/rules.md#LPW-ARC-005) | 按实际待机负载选稳压器，而不是只看标称 Iq | should | high | bom_check (partial) |
| [LPW-ARC-006](../../skills/ee-low-power/references/rules.md#LPW-ARC-006) | 线性稳压器的 Iq 是睡眠电流的下限 | should | high | bom_check (partial) |
| [LPW-ARC-007](../../skills/ee-low-power/references/rules.md#LPW-ARC-007) | 用负载开关划分电源域，切断高漏电子系统 | should | high | bom_check (partial) |
| [LPW-ARC-008](../../skills/ee-low-power/references/rules.md#LPW-ARC-008) | 按唤醒源与保持内容选 MCU 睡眠模式（ESP32-C3） | should | high | netlist_diff (full) |
| [LPW-ARC-011](../../skills/ee-low-power/references/rules.md#LPW-ARC-011) | RTC 备份与超级电容容量必须计入漏电 | should | high | bom_check (partial) |
| [LPW-ARC-009](../../skills/ee-low-power/references/rules.md#LPW-ARC-009) | Wi-Fi 保持连接还是深睡重连，按平均电流预算选 | consider | high | bench (partial) |
| [LPW-ARC-010](../../skills/ee-low-power/references/rules.md#LPW-ARC-010) | 睡眠预算要计入 Flash 待机电流 | consider | high | bom_check (partial) |
| [LPW-ARC-013](../../skills/ee-low-power/references/rules.md#LPW-ARC-013) | 定时唤醒精度要求决定 RTC 慢时钟来源 | consider | medium | bench (partial) |

## 射频与天线

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [RF-ARC-002](../../skills/ee-rf/references/rules.md#RF-ARC-002) | 按法规限值选功率、天线增益与杂散抑制 | must | high | review (partial) |
| [RF-ARC-004](../../skills/ee-rf/references/rules.md#RF-ARC-004) | 不要改动预认证模组的天线与匹配配置 | must | high | bom_check (partial) |
| [RF-ARC-001](../../skills/ee-rf/references/rules.md#RF-ARC-001) | 用 Friis 公式做链路预算并留衰落余量 | should | medium | review (partial) |
| [RF-ARC-003](../../skills/ee-rf/references/rules.md#RF-ARC-003) | 优先选预认证射频模组，量大再做分立射频 | should | medium | bom_check (partial) |
| [RF-ARC-006](../../skills/ee-rf/references/rules.md#RF-ARC-006) | GNSS 无源天线馈线不超过 10 cm，更长用有源天线 | should | high | geometry_script (full) |
| [RF-ARC-005](../../skills/ee-rf/references/rules.md#RF-ARC-005) | 按频段、面积、高度和成本选天线类型 | consider | high | review (manual) |

## 音频

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [AUD-ARC-001](../../skills/ee-audio/references/rules.md#AUD-ARC-001) | 按功率、负载和损耗反推 Class-D 供电电压与限流 | should | high | bom_check (partial) |
| [AUD-ARC-003](../../skills/ee-audio/references/rules.md#AUD-ARC-003) | 音频指标带测试条件立项（THD+N、SNR、PSRR） | should | high | bench (partial) |
| [AUD-ARC-004](../../skills/ee-audio/references/rules.md#AUD-ARC-004) | Codec 的 MCLK 取 256×fs 常用频率，避开内部 PLL | should | high | bom_check (partial) |
| [AUD-ARC-002](../../skills/ee-audio/references/rules.md#AUD-ARC-002) | 按功率、散热、续航和 EMI 预算选 Class-D 或线性功放 | consider | medium | review (manual) |

## 精密模拟 / 传感器前端

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [ANA-ARC-003](../../skills/ee-analog/references/rules.md#ANA-ARC-003) | 核对电流检测增益档和输出量程 | must | high | bom_check (full) |
| [ANA-ARC-001](../../skills/ee-analog/references/rules.md#ANA-ARC-001) | 选型前先做误差预算（失调/漂移/增益/容差） | should | high | bom_check (partial) |
| [ANA-ARC-002](../../skills/ee-analog/references/rules.md#ANA-ARC-002) | 按失调与量程选分流电阻阻值 | should | high | bom_check (partial) |
| [ANA-ARC-005](../../skills/ee-analog/references/rules.md#ANA-ARC-005) | 放大器带宽/建立时间要小于最短导通时间 | should | high | spice (partial) |
| [ANA-ARC-006](../../skills/ee-analog/references/rules.md#ANA-ARC-006) | 运放相位裕度目标 ≥ 45°，容性负载用隔离电阻 | should | high | spice (partial) |
| [ANA-ARC-007](../../skills/ee-analog/references/rules.md#ANA-ARC-007) | ESP32-C3 内置 ADC 的误差与使用边界 | should | high | bench (partial) |
| [ANA-ARC-009](../../skills/ee-analog/references/rules.md#ANA-ARC-009) | 称重电桥：排查引线电阻对比例测量的破坏 | should | high | bench (manual) |
| [ANA-ARC-010](../../skills/ee-analog/references/rules.md#ANA-ARC-010) | 运放选型：偏置电流、源阻抗与温度 | should | medium | bom_check (partial) |
| [ANA-ARC-004](../../skills/ee-analog/references/rules.md#ANA-ARC-004) | 按系统约束选择分流电阻位置 | consider | high | spice (partial) |
| [ANA-ARC-008](../../skills/ee-analog/references/rules.md#ANA-ARC-008) | HX711 按需选数据率，并丢弃建立期数据 | consider | high | bench (partial) |

## 高速数字

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HSD-ARC-002](../../skills/ee-high-speed/references/rules.md#HSD-ARC-002) | 按接口确定差分/单端目标阻抗与公差 | must | high | tline_calc (partial) |
| [HSD-ARC-001](../../skills/ee-high-speed/references/rules.md#HSD-ARC-001) | 按边沿长度 1/6 判断走线是否需按传输线处理 | should | high | geometry_script (partial) |
| [HSD-ARC-003](../../skills/ee-high-speed/references/rules.md#HSD-ARC-003) | 高速接口板按速率确定最少层数 | should | medium | review (manual) |
| [HSD-ARC-004](../../skills/ee-high-speed/references/rules.md#HSD-ARC-004) | DDR3 点对点驱动、走线、ODT 阻抗三者匹配 | should | high | si_sim (partial) |
| [HSD-ARC-005](../../skills/ee-high-speed/references/rules.md#HSD-ARC-005) | 选定 DDR 地址/命令拓扑（树形或 fly-by）并写入约束 | should | high | si_sim (partial) |

## EMC / ESD / 浪涌

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [EMC-ARC-002](../../skills/ee-emc-esd/references/rules.md#EMC-ARC-002) | ESD 目标等级按产品标准定，不靠 IC 的 HBM/CDM | must | high | bom_check (partial) |
| [EMC-ARC-001](../../skills/ee-emc-esd/references/rules.md#EMC-ARC-001) | 按源—路径—受害者拆解每个 EMC 问题 | should | high | review (manual) |
| [EMC-ARC-003](../../skills/ee-emc-esd/references/rules.md#EMC-ARC-003) | 按端口确定 EFT 与浪涌等级和性能判据 | should | high | review (manual) |
| [EMC-ARC-004](../../skills/ee-emc-esd/references/rules.md#EMC-ARC-004) | 边沿速率与时钟频率取满足时序的最慢值 | should | high | si_sim (partial) |
| [EMC-ARC-005](../../skills/ee-emc-esd/references/rules.md#EMC-ARC-005) | 展频时钟只降峰值不降总能量，先评估时序 | consider | medium | emc_precompliance (manual) |

## 高压 / 隔离 / 安规

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HVS-ARC-001](../../skills/ee-hv-safety/references/rules.md#HVS-ARC-001) | 先划分电压域：ELV/SELV 与危险电压 | must | medium | bom_check (partial) |
| [HVS-ARC-002](../../skills/ee-hv-safety/references/rules.md#HVS-ARC-002) | 每道隔离边界定义绝缘类型 | must | medium | review (manual) |
| [HVS-ARC-006](../../skills/ee-hv-safety/references/rules.md#HVS-ARC-006) | 锂电池包必须有电芯级保护 IC | must | medium | bom_check (partial) |
| [HVS-ARC-003](../../skills/ee-hv-safety/references/rules.md#HVS-ARC-003) | 查表前先确定五个输入参数 | should | high | review (manual) |
| [HVS-ARC-004](../../skills/ee-hv-safety/references/rules.md#HVS-ARC-004) | 海拔超过 2000 m 时间隙要乘修正系数 | should | medium | geometry_script (full) |
| [HVS-ARC-005](../../skills/ee-hv-safety/references/rules.md#HVS-ARC-005) | 隔离器件按额定值、封装爬电与 CTI 综合选型 | should | high | bom_check (partial) |

## 热设计

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [THM-ARC-001](../../skills/ee-thermal/references/rules.md#THM-ARC-001) | 数据手册的 θJA 只对它的测试板成立 | must | high | thermal_sim (partial) |
| [THM-ARC-002](../../skills/ee-thermal/references/rules.md#THM-ARC-002) | 在最高环境温度下算每个发热件的结温 | must | high | thermal_sim (full) |
| [THM-ARC-003](../../skills/ee-thermal/references/rules.md#THM-ARC-003) | 线性稳压器的功耗按最坏输入电压和最大电流算 | must | high | thermal_sim (full) |
| [THM-ARC-006](../../skills/ee-thermal/references/rules.md#THM-ARC-006) | MOSFET 导通损耗按热态 Rds(on) 算 | must | high | thermal_sim (full) |
| [THM-ARC-004](../../skills/ee-thermal/references/rules.md#THM-ARC-004) | 2 层板上预期 θJA 比 4 层测试板的数据差 | should | medium | thermal_sim (partial) |
| [THM-ARC-008](../../skills/ee-thermal/references/rules.md#THM-ARC-008) | 铝电解电容按本体温度算寿命并远离热源 | should | medium | bom_check (partial) |
| [THM-ARC-005](../../skills/ee-thermal/references/rules.md#THM-ARC-005) | 高海拔使用时放大 θJA | consider | high | thermal_sim (full) |
| [THM-ARC-007](../../skills/ee-thermal/references/rules.md#THM-ARC-007) | 电机堵转 / 启动的脉冲要对照 MOSFET SOA | consider | low | spice (partial) |

## 可制造 / 可装配 / 可测试

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [DFM-ARC-001](../../skills/ee-dfm/references/rules.md#DFM-ARC-001) | 按所选 JLC 贴片档位的能力边界选型 | must | high | bom_check (partial) |
| [DFM-ARC-004](../../skills/ee-dfm/references/rules.md#DFM-ARC-004) | 器件必须耐受 JLC 回流峰值并核对 MSL | must | medium | bom_check (partial) |
| [DFM-ARC-002](../../skills/ee-dfm/references/rules.md#DFM-ARC-002) | 优先选 JLC 基础库 / Preferred 器件 | should | medium | bom_check (partial) |
| [DFM-ARC-003](../../skills/ee-dfm/references/rules.md#DFM-ARC-003) | 下单前核对每个料号的库存与封装匹配 | should | medium | bom_check (partial) |
| [DFM-ARC-005](../../skills/ee-dfm/references/rules.md#DFM-ARC-005) | 默认按 IPC Class 2 订板，Class 3 另行评估 | consider | medium | review (manual) |
