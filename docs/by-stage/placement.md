# 器件布局（placement）

41 条规则 · 由 `catalog/*.yaml` 生成。详情见各领域文件。

## 通用 / 数模混合 MCU 板

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [GEN-PLC-002](../../skills/ee-general-pcb/references/rules.md#GEN-PLC-002) | 每个电源引脚一个去耦电容，小容值最近 | should | high | geometry_script (full) |
| [GEN-PLC-003](../../skills/ee-general-pcb/references/rules.md#GEN-PLC-003) | 去耦电容地焊盘就近接地，用过孔或直连地铜 | should | high | geometry_script (full) |
| [GEN-PLC-004](../../skills/ee-general-pcb/references/rules.md#GEN-PLC-004) | 电源电流必须穿过去耦电容焊盘再到引脚 | should | medium | geometry_script (partial) |
| [GEN-PLC-005](../../skills/ee-general-pcb/references/rules.md#GEN-PLC-005) | 电源入口和稳压器处放大电容，模块进线前放 10 µF | should | medium | geometry_script (full) |
| [GEN-PLC-006](../../skills/ee-general-pcb/references/rules.md#GEN-PLC-006) | 晶振贴近 MCU，走线短且对称，周围有地环 | should | high | geometry_script (full) |
| [GEN-PLC-009](../../skills/ee-general-pcb/references/rules.md#GEN-PLC-009) | ESD / TVS 器件紧靠连接器，保护对象放得更远 | should | high | geometry_script (full) |
| [GEN-PLC-001](../../skills/ee-general-pcb/references/rules.md#GEN-PLC-001) | 先放固定件，再放 MCU 链，最后放去耦与外围 | consider | low | review (manual) |
| [GEN-PLC-007](../../skills/ee-general-pcb/references/rules.md#GEN-PLC-007) | 晶振周围留出隔离区，不放无关元件 | consider | medium | geometry_script (full) |
| [GEN-PLC-008](../../skills/ee-general-pcb/references/rules.md#GEN-PLC-008) | 串联电阻靠近驱动端放置 | consider | medium | geometry_script (full) |

## 电源与功率

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [PWR-PLC-001](../../skills/ee-power/references/rules.md#PWR-PLC-001) | 先识别开关热回路，输入电容紧贴 IC 并最小化环路 | must | high | geometry_script (partial) |
| [PWR-PLC-003](../../skills/ee-power/references/rules.md#PWR-PLC-003) | 续流二极管与 IC 同层，短而宽直连 SW 和 GND | must | high | geometry_script (full) |
| [PWR-PLC-002](../../skills/ee-power/references/rules.md#PWR-PLC-002) | 高频旁路电容紧贴 VIN/GND，大电容可稍远 | should | high | geometry_script (full) |
| [PWR-PLC-004](../../skills/ee-power/references/rules.md#PWR-PLC-004) | 电感靠近 IC 但不必比输入电容更近，SW 铜皮最小 | should | high | geometry_script (partial) |
| [PWR-PLC-006](../../skills/ee-power/references/rules.md#PWR-PLC-006) | 升压变换器先放输出电容，再放电感和输入电容 | should | high | geometry_script (partial) |
| [PWR-PLC-007](../../skills/ee-power/references/rules.md#PWR-PLC-007) | LDO 输入输出电容靠近引脚，负载走线宽 | should | medium | geometry_script (partial) |
| [PWR-PLC-005](../../skills/ee-power/references/rules.md#PWR-PLC-005) | RC 缓冲电路跨接在 SW 与 GND 引脚上并按振铃频率定值 | consider | high | spice (partial) |

## 低功耗 / 电池

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [LPW-PLC-001](../../skills/ee-low-power/references/rules.md#LPW-PLC-001) | 突发负载的大电容放在电池或电源入口侧，按总电荷定容 | should | high | spice (partial) |

## 射频与天线

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [RF-PLC-001](../../skills/ee-rf/references/rules.md#RF-PLC-001) | 匹配网络紧贴芯片 RF 脚和天线馈点，元件相互靠近 | should | high | geometry_script (partial) |
| [RF-PLC-002](../../skills/ee-rf/references/rules.md#RF-PLC-002) | 射频电源脚去耦：小值最近、同层、各自接地过孔 | should | high | geometry_script (full) |

## 音频

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [AUD-PLC-001](../../skills/ee-audio/references/rules.md#AUD-PLC-001) | Class-D 去耦与自举电容紧贴引脚并控制回路电感 | must | high | geometry_script (full) |
| [AUD-PLC-002](../../skills/ee-audio/references/rules.md#AUD-PLC-002) | Codec 去耦与 VREF/VAG 参考电容紧贴引脚 | should | high | geometry_script (partial) |
| [AUD-PLC-003](../../skills/ee-audio/references/rules.md#AUD-PLC-003) | 输出滤波器紧靠功放，电感相互隔开并远离输入 | should | high | geometry_script (partial) |

## 精密模拟 / 传感器前端

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [ANA-PLC-001](../../skills/ee-analog/references/rules.md#ANA-PLC-001) | 分流电阻紧贴电流检测放大器 | should | high | geometry_script (full) |
| [ANA-PLC-002](../../skills/ee-analog/references/rules.md#ANA-PLC-002) | 电流检测放大器的旁路电容贴脚且不打孔 | should | high | geometry_script (full) |
| [ANA-PLC-003](../../skills/ee-analog/references/rules.md#ANA-PLC-003) | ADC 基准与电源电容贴近引脚的距离上限 | should | high | geometry_script (full) |
| [ANA-PLC-004](../../skills/ee-analog/references/rules.md#ANA-PLC-004) | 匹配电阻同向、紧邻，沿等温线排布 | consider | high | geometry_script (full) |

## 高速数字

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HSD-PLC-001](../../skills/ee-high-speed/references/rules.md#HSD-PLC-001) | 连接器侧保护链按 ESD、共模滤波、隔直电容的顺序放置 | should | high | geometry_script (partial) |
| [HSD-PLC-002](../../skills/ee-high-speed/references/rules.md#HSD-PLC-002) | 差分对上的隔直电容和 ESD 焊盘对称放置并挖空参考面 | should | high | geometry_script (partial) |
| [HSD-PLC-003](../../skills/ee-high-speed/references/rules.md#HSD-PLC-003) | 端接电阻按类型放在驱动端或接收端，stub 尽量短 | should | high | geometry_script (full) |
| [HSD-PLC-004](../../skills/ee-high-speed/references/rules.md#HSD-PLC-004) | 高速 IC 每个电源脚就近去耦，小电容最近，过孔贴焊盘 | should | high | geometry_script (full) |

## EMC / ESD / 浪涌

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [EMC-PLC-001](../../skills/ee-emc-esd/references/rules.md#EMC-PLC-001) | TVS 紧靠连接器引脚，被保护 IC 远离 TVS | must | high | geometry_script (full) |
| [EMC-PLC-002](../../skills/ee-emc-esd/references/rules.md#EMC-PLC-002) | 阻尼电阻贴驱动脚，I/O 旁路电容贴连接器 | should | high | geometry_script (partial) |
| [EMC-PLC-003](../../skills/ee-emc-esd/references/rules.md#EMC-PLC-003) | 去耦电容贴电源脚，回路面积最小 | should | high | geometry_script (full) |
| [EMC-PLC-004](../../skills/ee-emc-esd/references/rules.md#EMC-PLC-004) | 电机抑制电容和续流件贴电机/感性负载 | should | medium | geometry_script (partial) |

## 高压 / 隔离 / 安规

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HVS-PLC-001](../../skills/ee-hv-safety/references/rules.md#HVS-PLC-001) | 焊盘不得缩短隔离器件封装的爬电与间隙 | must | high | geometry_script (full) |

## 热设计

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [THM-PLC-001](../../skills/ee-thermal/references/rules.md#THM-PLC-001) | 热源与怕热元件分开放 | should | medium | geometry_script (partial) |
| [THM-PLC-002](../../skills/ee-thermal/references/rules.md#THM-PLC-002) | 外壳内的环境温度和空气流动要按实际假设 | should | medium | bench (manual) |

## 可制造 / 可装配 / 可测试

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [DFM-PLC-002](../../skills/ee-dfm/references/rules.md#DFM-PLC-002) | 封装 courtyard 不得重叠 | must | low | drc (full) |
| [DFM-PLC-001](../../skills/ee-dfm/references/rules.md#DFM-PLC-001) | 元件间距满足 JLC 最小间距表 | should | medium | geometry_script (partial) |
| [DFM-PLC-003](../../skills/ee-dfm/references/rules.md#DFM-PLC-003) | 放置 3 个不对称的全局 MARK 点 | should | high | geometry_script (full) |
| [DFM-PLC-004](../../skills/ee-dfm/references/rules.md#DFM-PLC-004) | 细间距器件旁加局部 MARK 点 | consider | medium | geometry_script (partial) |
