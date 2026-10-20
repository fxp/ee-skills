# 布线（routing）

72 条规则 · 由 `catalog/*.yaml` 生成。详情见各领域文件。

## 通用 / 数模混合 MCU 板

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [GEN-RTE-002](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-002) | 信号线不得跨越参考平面的分割槽或缝隙 | must | high | geometry_script (full) |
| [GEN-RTE-001](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-001) | 每条信号线下方保持连续的回流参考铜 | should | medium | geometry_script (full) |
| [GEN-RTE-003](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-003) | 信号换层时在过孔旁放地过孔提供回流 | should | medium | geometry_script (partial) |
| [GEN-RTE-004](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-004) | 电源线与地线并行贴近，环路长宽比不超过 3:1 | should | high | geometry_script (full) |
| [GEN-RTE-005](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-005) | 电源分配单点或星形，别串成菊花链 | should | high | geometry_script (partial) |
| [GEN-RTE-008](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-008) | 快信号避免 T 形分支和长残桩 | should | high | geometry_script (full) |
| [GEN-RTE-009](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-009) | 敏感信号和时钟尽量不打过孔 | should | high | drc (full) |
| [GEN-RTE-010](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-010) | 干扰源与敏感线间距至少 3 倍线宽 | should | medium | drc (full) |
| [GEN-RTE-013](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-013) | 晶振下方不走信号，时钟走线周围用地包裹 | should | high | geometry_script (full) |
| [GEN-RTE-014](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-014) | 连接器先到 TVS 再到 IC，路径短直无桩无过孔 | should | high | geometry_script (full) |
| [GEN-RTE-006](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-006) | MCU 供电走线按厂商给的最小宽度 | consider | high | geometry_script (full) |
| [GEN-RTE-007](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-007) | 拐角默认用 45° 或圆弧，90° 并非一概有害 | consider | high | geometry_script (full) |
| [GEN-RTE-011](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-011) | 相邻走线层垂直布线，但 2 层板优先保证回流 | consider | medium | geometry_script (partial) |
| [GEN-RTE-012](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-012) | 噪声走线不放在板子最外沿 | consider | medium | geometry_script (full) |
| [GEN-RTE-015](../../skills/ee-general-pcb/references/rules.md#GEN-RTE-015) | 快速信号走线长度限制在约 1/50 波长以内 | consider | high | geometry_script (full) |

## 电源与功率

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [PWR-RTE-001](../../skills/ee-power/references/rules.md#PWR-RTE-001) | SW 节点铜皮只留够载流的最小面积 | must | high | geometry_script (full) |
| [PWR-RTE-002](../../skills/ee-power/references/rules.md#PWR-RTE-002) | 热回路走线不经过孔，必须时并联多孔 | must | high | geometry_script (full) |
| [PWR-RTE-003](../../skills/ee-power/references/rules.md#PWR-RTE-003) | 反馈线短、远离 SW 与电感，取样点在输出电容处 | must | high | geometry_script (partial) |
| [PWR-RTE-005](../../skills/ee-power/references/rules.md#PWR-RTE-005) | 大电流走线按 IPC-2152 和温升目标定宽 | must | high | geometry_script (full) |
| [PWR-RTE-007](../../skills/ee-power/references/rules.md#PWR-RTE-007) | 电流检测放大器输入走开尔文线接到分流电阻焊盘 | must | high | geometry_script (full) |
| [PWR-RTE-004](../../skills/ee-power/references/rules.md#PWR-RTE-004) | 自举电容回路短，IC 地引脚走线同样要短 | should | high | geometry_script (partial) |
| [PWR-RTE-006](../../skills/ee-power/references/rules.md#PWR-RTE-006) | 换层大电流路径按电流估算并联过孔数量 | should | medium | geometry_script (full) |
| [PWR-RTE-008](../../skills/ee-power/references/rules.md#PWR-RTE-008) | 3.3 V 电源走线按 Espressif 最小线宽 | should | high | geometry_script (full) |

## 低功耗 / 电池

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [LPW-RTE-002](../../skills/ee-low-power/references/rules.md#LPW-RTE-002) | 突发电流路径要核算走线与过孔的 IR 压降 | should | medium | geometry_script (full) |
| [LPW-RTE-001](../../skills/ee-low-power/references/rules.md#LPW-RTE-001) | nA 级高阻节点要短走线并用双面保护环 | consider | medium | geometry_script (partial) |

## 射频与天线

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [RF-RTE-001](../../skills/ee-rf/references/rules.md#RF-RTE-001) | 射频线按 50 Ω 设计，线宽（及间隙）全程恒定 | must | high | geometry_script (full) |
| [RF-RTE-005](../../skills/ee-rf/references/rules.md#RF-RTE-005) | 射频线下方参考地完整，其他走线不穿越、不并行靠近 | must | high | geometry_script (partial) |
| [RF-RTE-002](../../skills/ee-rf/references/rules.md#RF-RTE-002) | 射频线尽量短，无短截线、分支和测试点 | should | high | geometry_script (full) |
| [RF-RTE-003](../../skills/ee-rf/references/rules.md#RF-RTE-003) | 射频线拐弯用圆弧或 135° 折线，不画未切角的直角 | should | high | geometry_script (full) |
| [RF-RTE-004](../../skills/ee-rf/references/rules.md#RF-RTE-004) | 射频路径上不打过孔 | should | high | geometry_script (full) |

## 音频

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [AUD-RTE-002](../../skills/ee-audio/references/rules.md#AUD-RTE-002) | 开关网络与其他信号在相邻层不平行重叠 | must | high | geometry_script (full) |
| [AUD-RTE-001](../../skills/ee-audio/references/rules.md#AUD-RTE-001) | Class-D 输出走线宽、短、成对并等长 | should | high | drc (full) |
| [AUD-RTE-003](../../skills/ee-audio/references/rules.md#AUD-RTE-003) | 音频输入走线短、过完整地、远离开关与 RF | should | high | geometry_script (partial) |
| [AUD-RTE-004](../../skills/ee-audio/references/rules.md#AUD-RTE-004) | 差分音频信号成对对称走线，并铺在模拟地之上 | should | high | geometry_script (partial) |
| [AUD-RTE-005](../../skills/ee-audio/references/rules.md#AUD-RTE-005) | I2S/MCLK 时钟点对点、短、远离模拟引脚 | should | medium | si_sim (partial) |

## 精密模拟 / 传感器前端

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [ANA-RTE-001](../../skills/ee-analog/references/rules.md#ANA-RTE-001) | 分流电阻到放大器必须用开尔文（四线）走线 | must | high | geometry_script (full) |
| [ANA-RTE-002](../../skills/ee-analog/references/rules.md#ANA-RTE-002) | 两条 sense 线等长、等宽、同层并排 | should | high | geometry_script (full) |
| [ANA-RTE-003](../../skills/ee-analog/references/rules.md#ANA-RTE-003) | 模拟输入走线远离开关节点和数字信号 | should | high | drc (full) |
| [ANA-RTE-005](../../skills/ee-analog/references/rules.md#ANA-RTE-005) | 敏感模拟线下方保持连续的返回平面 | should | high | geometry_script (full) |
| [ANA-RTE-004](../../skills/ee-analog/references/rules.md#ANA-RTE-004) | 高阻抗节点用保护环，且不要覆盖阻焊 | consider | high | geometry_script (partial) |

## 高速数字

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HSD-RTE-002](../../skills/ee-high-speed/references/rules.md#HSD-RTE-002) | 按接口限定差分对内偏斜 | must | high | drc (full) |
| [HSD-RTE-005](../../skills/ee-high-speed/references/rules.md#HSD-RTE-005) | 高速线全程走在连续参考面上，远离参考面边缘和空洞 | must | high | geometry_script (full) |
| [HSD-RTE-012](../../skills/ee-high-speed/references/rules.md#HSD-RTE-012) | DDR3 地址/命令/控制线 fly-by 走线规则 | must | high | drc (partial) |
| [HSD-RTE-013](../../skills/ee-high-speed/references/rules.md#HSD-RTE-013) | DDR3 数据、DQS 与时钟对的匹配和过孔规则 | must | high | drc (full) |
| [HSD-RTE-001](../../skills/ee-high-speed/references/rules.md#HSD-RTE-001) | 差分对全程对称平行，未耦合段只允许出现在引出和连接器处 | should | high | drc (full) |
| [HSD-RTE-003](../../skills/ee-high-speed/references/rules.md#HSD-RTE-003) | 在失配发生处就近做局部蛇形补偿，几何满足间距要求 | should | high | geometry_script (partial) |
| [HSD-RTE-004](../../skills/ee-high-speed/references/rules.md#HSD-RTE-004) | 按接口取线对间距并避开时钟线，相邻层正交布线 | should | high | drc (full) |
| [HSD-RTE-006](../../skills/ee-high-speed/references/rules.md#HSD-RTE-006) | 换层过孔旁就近放地缝合过孔，且差分两线过孔对称 | should | high | geometry_script (full) |
| [HSD-RTE-007](../../skills/ee-high-speed/references/rules.md#HSD-RTE-007) | 控制过孔残桩 < 15 mil，反焊盘加大，通孔连接器从底层进线 | should | high | geometry_script (partial) |
| [HSD-RTE-008](../../skills/ee-high-speed/references/rules.md#HSD-RTE-008) | 限制每条高速线的过孔数，两线保持一致 | should | high | drc (full) |
| [HSD-RTE-009](../../skills/ee-high-speed/references/rules.md#HSD-RTE-009) | 高速线总长不超过接口与器件的限值 | should | high | drc (full) |
| [HSD-RTE-010](../../skills/ee-high-speed/references/rules.md#HSD-RTE-010) | 高速线少拐弯，拐角不小于 135° | should | high | geometry_script (full) |
| [HSD-RTE-011](../../skills/ee-high-speed/references/rules.md#HSD-RTE-011) | 高速差分线不放测试点，远离晶振、开关电源和磁性器件 | should | high | geometry_script (full) |
| [HSD-RTE-014](../../skills/ee-high-speed/references/rules.md#HSD-RTE-014) | 2 层板上的 FS USB 差分线：短、等长、下方整面地 | should | medium | tline_calc (partial) |

## EMC / ESD / 浪涌

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [EMC-RTE-001](../../skills/ee-emc-esd/references/rules.md#EMC-RTE-001) | 每条快速信号下方保持连续回流路径 | must | high | geometry_script (full) |
| [EMC-RTE-003](../../skills/ee-emc-esd/references/rules.md#EMC-RTE-003) | ESD 入口走线直通 TVS，无 stub、无过孔、拐角 ≤45° | must | high | geometry_script (full) |
| [EMC-RTE-004](../../skills/ee-emc-esd/references/rules.md#EMC-RTE-004) | TVS 地脚接同层地铺铜，紧邻过孔缝合到相邻地层 | must | high | geometry_script (full) |
| [EMC-RTE-002](../../skills/ee-emc-esd/references/rules.md#EMC-RTE-002) | 不跨平面分割/槽走线，必须跨时加缝合电容 | should | high | geometry_script (full) |
| [EMC-RTE-005](../../skills/ee-emc-esd/references/rules.md#EMC-RTE-005) | 快沿/时钟走线要短，超过阈值要端接 | should | high | geometry_script (full) |
| [EMC-RTE-006](../../skills/ee-emc-esd/references/rules.md#EMC-RTE-006) | ESD 路径和快沿线避免 90° 拐角（有条件） | consider | medium | geometry_script (full) |

## 高压 / 隔离 / 安规

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HVS-RTE-001](../../skills/ee-hv-safety/references/rules.md#HVS-RTE-001) | 按表取爬电距离，加强绝缘加倍 | must | medium | drc (full) |
| [HVS-RTE-002](../../skills/ee-hv-safety/references/rules.md#HVS-RTE-002) | 开槽延长爬电距离，槽宽大于 1 mm 且不削弱板子 | should | high | geometry_script (partial) |
| [HVS-RTE-003](../../skills/ee-hv-safety/references/rules.md#HVS-RTE-003) | 电气间隙由瞬态过压定，单独核对，爬电不得小于间隙 | should | low | drc (full) |

## 热设计

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [THM-RTE-005](../../skills/ee-thermal/references/rules.md#THM-RTE-005) | 散热过孔要实连到尽可能多的层，不用热焊盘 | must | high | drc (full) |
| [THM-RTE-001](../../skills/ee-thermal/references/rules.md#THM-RTE-001) | 大电流走线按 IPC-2152 的温升来定宽 | should | low | tline_calc (full) |
| [THM-RTE-002](../../skills/ee-thermal/references/rules.md#THM-RTE-002) | 散热过孔的孔径、间距与数量 | should | high | geometry_script (full) |
| [THM-RTE-004](../../skills/ee-thermal/references/rules.md#THM-RTE-004) | 散热过孔的封盖方式要避免焊料流失和空洞 | should | high | geometry_script (partial) |
| [THM-RTE-003](../../skills/ee-thermal/references/rules.md#THM-RTE-003) | 用过孔阵列的并联热阻核算而不是凭感觉 | consider | high | thermal_sim (full) |

## 可制造 / 可装配 / 可测试

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [DFM-RTE-002](../../skills/ee-dfm/references/rules.md#DFM-RTE-002) | 2 层板不要在 SMD 焊盘里放开口过孔 | must | medium | geometry_script (full) |
| [DFM-RTE-001](../../skills/ee-dfm/references/rules.md#DFM-RTE-001) | 片式元件两端的铜连接要热平衡 | should | medium | geometry_script (partial) |
| [DFM-RTE-003](../../skills/ee-dfm/references/rules.md#DFM-RTE-003) | QFN 1 脚旁保留走线与过孔禁区 | should | medium | review (manual) |
| [DFM-RTE-004](../../skills/ee-dfm/references/rules.md#DFM-RTE-004) | 过孔覆盖方式与孔径、间距要匹配 | should | high | drc (full) |
