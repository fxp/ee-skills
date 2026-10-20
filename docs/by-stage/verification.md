# 签核验证（verification）

61 条规则 · 由 `catalog/*.yaml` 生成。详情见各领域文件。

## 通用 / 数模混合 MCU 板

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [GEN-VER-001](../../skills/ee-general-pcb/references/rules.md#GEN-VER-001) | ERC 零违规，例外逐条带理由，禁止整类静音 | must | high | erc (full) |
| [GEN-VER-008](../../skills/ee-general-pcb/references/rules.md#GEN-VER-008) | 下单前按固定门禁逐项签核 | must | medium | erc (full) |
| [GEN-VER-002](../../skills/ee-general-pcb/references/rules.md#GEN-VER-002) | 按类别理解 ERC 违规，PWR_FLAG 只放在真实电源源头 | should | high | erc (partial) |
| [GEN-VER-003](../../skills/ee-general-pcb/references/rules.md#GEN-VER-003) | 打开默认被忽略的 ERC 检查 | should | high | erc (full) |
| [GEN-VER-004](../../skills/ee-general-pcb/references/rules.md#GEN-VER-004) | 布局前由第二人对照数据手册做原理图评审 | should | high | review (manual) |
| [GEN-VER-006](../../skills/ee-general-pcb/references/rules.md#GEN-VER-006) | 把仿真与实测对照并记录模型的适用范围 | should | medium | spice (partial) |
| [GEN-VER-007](../../skills/ee-general-pcb/references/rules.md#GEN-VER-007) | 首次上电按步骤逐轨进行并限流 | should | medium | bench (manual) |
| [GEN-VER-009](../../skills/ee-general-pcb/references/rules.md#GEN-VER-009) | EDA 文件进版本控制，忽略缓存并给下单版本打标签 | should | medium | review (full) |
| [GEN-VER-005](../../skills/ee-general-pcb/references/rules.md#GEN-VER-005) | 布局前只仿真数据手册答不了的关键块 | consider | medium | spice (partial) |

## 电源与功率

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [PWR-VER-001](../../skills/ee-power/references/rules.md#PWR-VER-001) | 开关电源环路增益相位裕量与穿越频率签核 | must | high | spice (full) |
| [PWR-VER-002](../../skills/ee-power/references/rules.md#PWR-VER-002) | 负载阶跃响应与 LDO 稳定性的 SPICE 与实测 | must | high | spice (full) |
| [PWR-VER-004](../../skills/ee-power/references/rules.md#PWR-VER-004) | 电机启动/堵转期间核算电源轨跌落与欠压余量 | must | medium | spice (full) |
| [PWR-VER-003](../../skills/ee-power/references/rules.md#PWR-VER-003) | 上电浪涌电流与热插拔电压过冲仿真 | should | medium | spice (full) |
| [PWR-VER-005](../../skills/ee-power/references/rules.md#PWR-VER-005) | PDN 目标阻抗与电容网络反谐振检查 | should | medium | pi_sim (partial) |
| [PWR-VER-006](../../skills/ee-power/references/rules.md#PWR-VER-006) | 以正确探测方法测量 SW 节点振铃并核对余量 | should | high | spice (partial) |
| [PWR-VER-007](../../skills/ee-power/references/rules.md#PWR-VER-007) | 估算效率与损耗预算并与热限比较 | consider | medium | bom_check (full) |

## 低功耗 / 电池

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [LPW-VER-003](../../skills/ee-low-power/references/rules.md#LPW-VER-003) | 在真实板、真实固件、真实电压下验收睡眠电流 | must | high | bench (partial) |
| [LPW-VER-005](../../skills/ee-low-power/references/rules.md#LPW-VER-005) | 无线突发时在负载端实测电压跌落与纹波 | must | high | bench (partial) |
| [LPW-VER-001](../../skills/ee-low-power/references/rules.md#LPW-VER-001) | 选对测睡眠电流的仪表：burden 电压、量程与分辨率 | should | high | bench (manual) |
| [LPW-VER-002](../../skills/ee-low-power/references/rules.md#LPW-VER-002) | 平均电流用整个占空周期的累计电荷来测 | should | high | bench (partial) |
| [LPW-VER-004](../../skills/ee-low-power/references/rules.md#LPW-VER-004) | 睡眠电流要在高低温下复测，并按最坏温度做预算 | should | high | bench (partial) |
| [LPW-VER-006](../../skills/ee-low-power/references/rules.md#LPW-VER-006) | 电池寿命模型要与实测对账，厂商工具只作初估 | consider | medium | bom_check (partial) |

## 射频与天线

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [RF-VER-001](../../skills/ee-rf/references/rules.md#RF-VER-001) | 天线端回波损耗 S11 <= -10 dB 覆盖整个工作频段 | should | high | bench (full) |
| [RF-VER-002](../../skills/ee-rf/references/rules.md#RF-VER-002) | 用 VNA 测天线：校准到参考面，在最终外壳和手持下复测 | should | high | bench (manual) |
| [RF-VER-003](../../skills/ee-rf/references/rules.md#RF-VER-003) | 板子回来后用 Smith 圆图调 π 匹配网络 | should | high | spice (partial) |
| [RF-VER-004](../../skills/ee-rf/references/rules.md#RF-VER-004) | 定制 PCB 天线先做电磁仿真再投板 | should | medium | em_sim (partial) |
| [RF-VER-005](../../skills/ee-rf/references/rules.md#RF-VER-005) | 用传导口预扫发射功率、谐波与杂散 | should | high | bench (manual) |
| [RF-VER-006](../../skills/ee-rf/references/rules.md#RF-VER-006) | 在最终产品上实测吞吐量与通信距离 | should | high | bench (manual) |
| [RF-VER-007](../../skills/ee-rf/references/rules.md#RF-VER-007) | 用 SPICE/S 参数先仿匹配网络（含元件寄生） | consider | medium | spice (partial) |

## 音频

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [AUD-VER-002](../../skills/ee-audio/references/rules.md#AUD-VER-002) | Class-D 扬声器输出必须差分测量，输出端不接地 | must | high | review (manual) |
| [AUD-VER-001](../../skills/ee-audio/references/rules.md#AUD-VER-001) | 按规范测 THD+N/SNR，并用 FFT 交叉验证 | should | high | bench (partial) |
| [AUD-VER-003](../../skills/ee-audio/references/rules.md#AUD-VER-003) | 用 ngspice 仿真耦合、偏置网络和滤波器的 AC 与噪声 | should | medium | spice (partial) |
| [AUD-VER-004](../../skills/ee-audio/references/rules.md#AUD-VER-004) | 向电源注入纹波测 PSRR 和电源耦合 | should | high | bench (partial) |
| [AUD-VER-005](../../skills/ee-audio/references/rules.md#AUD-VER-005) | 静态本底 FFT：查工频谐波、217 Hz 和开关频率成分 | should | medium | bench (partial) |
| [AUD-VER-006](../../skills/ee-audio/references/rules.md#AUD-VER-006) | Class-D 辐射预扫：最长喇叭线与最终磁珠/滤波器配置 | should | high | emc_precompliance (manual) |

## 精密模拟 / 传感器前端

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [ANA-VER-003](../../skills/ee-analog/references/rules.md#ANA-VER-003) | 稳定性签核：环路增益 + 阶跃，覆盖角点条件 | must | high | spice (partial) |
| [ANA-VER-005](../../skills/ee-analog/references/rules.md#ANA-VER-005) | 实测 HX711 的 PD_SCK 时序，别触发掉电 | must | high | bench (partial) |
| [ANA-VER-001](../../skills/ee-analog/references/rules.md#ANA-VER-001) | SPICE 做最坏情况 + Monte Carlo + 温度扫描对账 | should | medium | spice (partial) |
| [ANA-VER-002](../../skills/ee-analog/references/rules.md#ANA-VER-002) | SPICE 噪声分析：积分噪声与 LSB 对比 | should | medium | spice (partial) |
| [ANA-VER-004](../../skills/ee-analog/references/rules.md#ANA-VER-004) | 输入短路噪声实测与有效分辨率 | should | high | bench (partial) |

## 高速数字

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HSD-VER-002](../../skills/ee-high-speed/references/rules.md#HSD-VER-002) | 出板前用自定义规则跑 DRC，并核对长度口径 | must | high | drc (full) |
| [HSD-VER-001](../../skills/ee-high-speed/references/rules.md#HSD-VER-001) | 布线后按实际线宽间距逐段复算受控线阻抗 | should | medium | geometry_script (partial) |
| [HSD-VER-003](../../skills/ee-high-speed/references/rules.md#HSD-VER-003) | 用传输线模型仿真端接，并联合 IBIS 做高速总线 SI 仿真 | should | high | spice (partial) |
| [HSD-VER-005](../../skills/ee-high-speed/references/rules.md#HSD-VER-005) | 签核前对高速 IC 电源轨做 PDN 阻抗仿真 | should | medium | pi_sim (partial) |
| [HSD-VER-004](../../skills/ee-high-speed/references/rules.md#HSD-VER-004) | 用 TDR/VNA 实测阻抗与 S 参数，脚本化后处理 | consider | medium | em_sim (partial) |

## EMC / ESD / 浪涌

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [EMC-VER-002](../../skills/ee-emc-esd/references/rules.md#EMC-VER-002) | ESD 测试：金属壳打壳体接触放电，绝缘件打空气放电 | must | high | bench (manual) |
| [EMC-VER-001](../../skills/ee-emc-esd/references/rules.md#EMC-VER-001) | 用 LISN 做传导发射预兼容，两根线分别扫 | should | medium | emc_precompliance (manual) |
| [EMC-VER-003](../../skills/ee-emc-esd/references/rules.md#EMC-VER-003) | ESD 仿真：IEC 枪模型 + TVS + 寄生电感估算 VESD | should | high | spice (partial) |
| [EMC-VER-004](../../skills/ee-emc-esd/references/rules.md#EMC-VER-004) | EFT 抗扰测试：双极性、每端口不少于 1 分钟 | should | high | bench (manual) |
| [EMC-VER-005](../../skills/ee-emc-esd/references/rules.md#EMC-VER-005) | 电机启停/堵转时在板上抓供电、EN 和采样 | should | medium | bench (manual) |
| [EMC-VER-006](../../skills/ee-emc-esd/references/rules.md#EMC-VER-006) | 样机阶段逐个拆装滤波件，只保留有实测收益的 | consider | medium | bom_check (partial) |

## 高压 / 隔离 / 安规

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [HVS-VER-001](../../skills/ee-hv-safety/references/rules.md#HVS-VER-001) | 用 KiCad 的 creepage 与 clearance 规则做 DRC | must | medium | drc (full) |
| [HVS-VER-002](../../skills/ee-hv-safety/references/rules.md#HVS-VER-002) | 耐压测试：型式试验与出厂试验分开，夹具把两侧引脚各并联 | should | medium | bench (manual) |

## 热设计

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [THM-VER-001](../../skills/ee-thermal/references/rules.md#THM-VER-001) | 由外壳温度推结温用 ψJT，不用 θJC | should | high | bench (manual) |
| [THM-VER-002](../../skills/ee-thermal/references/rules.md#THM-VER-002) | 测外壳温度的方法要避免热电偶散热误差 | should | high | bench (manual) |
| [THM-VER-004](../../skills/ee-thermal/references/rules.md#THM-VER-004) | 在最坏工况、盖好外壳后做稳态热测试 | should | medium | bench (manual) |
| [THM-VER-003](../../skills/ee-thermal/references/rules.md#THM-VER-003) | MOSFET 结温可用体二极管压降法做电学测量 | consider | medium | bench (manual) |
| [THM-VER-005](../../skills/ee-thermal/references/rules.md#THM-VER-005) | 先用热阻网络手算，再决定是否做 FEM | consider | high | thermal_sim (partial) |

## 可制造 / 可装配 / 可测试

| ID | 规则 | 级别 | 可信度 | 最强验证 |
|---|---|---|---|---|
| [DFM-VER-001](../../skills/ee-dfm/references/rules.md#DFM-VER-001) | 用板厂能力而不是 EDA 默认值跑 DRC | must | high | drc (full) |
| [DFM-VER-003](../../skills/ee-dfm/references/rules.md#DFM-VER-003) | 下单前核对 CPL 与板文件的几何一致 | must | medium | geometry_script (full) |
| [DFM-VER-002](../../skills/ee-dfm/references/rules.md#DFM-VER-002) | 用独立查看器重新读一遍出图结果 | should | medium | geometry_script (partial) |
