# 精密模拟 / 传感器前端（analog）— 规则全文

垂直领域 · 46 条规则 · 由 `catalog/*.yaml` 生成，请改 YAML 不要改本文件。用 `grep -n "<规则ID>" rules.md` 定位单条，不要整份读。

环节分布：架构与选型 10，符号封装库 1，原理图 13，网表与约束 1，叠层与规则 1，分区规划 2，器件布局 4，布线 5，平面与铺铜 3，出图与制造 1，签核验证 5

## 架构与选型（architecture）

<a id="ANA-ARC-003"></a>
#### ANA-ARC-003 · 核对电流检测增益档和输出量程
`must` · 可信度 `high` · 适用: current_sense, ina199, esp32c3_adc · 标签: cat-feeder

**规则** 用数据手册的型号后缀与增益对照表算满量程输出 Vout_fs = Imax * Rshunt * G，要求 Vout_fs 同时不超过放大器输出上摆幅（V+ 减最大 0.2 V）和 ADC 能保证精度的量程；型号后缀与增益的对应关系必须以数据手册为准，不能凭记忆。

**依据** INA199 的 x1/x2/x3 后缀分别是 50/100/200 V/V；如果增益被记错，满量程输出会饱和或超出 ADC 的精确区间，整个测量失效。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ina199_gain_x1_x2_x3` | qualitative V/V | INA199x1 = 50，INA199x2 = 100，INA199x3 = 200（数据手册 Table 7-1 与 §6.5） |
| `output_swing_to_vplus_max_drop` | <= 0.2 V | INA199，RL = 10 kohm，-40 到 125 degC 时 Swing to V+ 最大值（典型 0.05 V） |
| `esp32c3_adc_total_error_atten0_to_2` | <= 10 mV | ESP32-C3 校准后总误差，量程 0 到 750/1050/1300 mV |
| `esp32c3_adc_total_error_atten3` | <= 35 mV | ESP32-C3 校准后总误差，量程 0 到 2500 mV |

**验证**
- `bom_check`（full）· 脚本：读 BOM 的放大器完整型号、R_shunt 阻值、Imax，查数据手册增益表 — 计算 Vout_fs；要求 Vout_fs <= V+ - 0.2 V 且 <= 选定 ADC 衰减档的量程；同时检查原理图注释中写的增益与数据手册表一致
- `spice`（partial）· ngspice：理想受控源建模放大器，DC 扫描 Iin 到 1.2*Imax — 输出在 Imax 之内必须是线性的，不能进入饱和或超出 ADC 量程

**来源分歧** 示例板（猫咪喂食器）的原理图备注曾把 INA199A2 写成 50 V/V（1 V/A，0 到 2 A 对应 0 到 2.0 V）。数据手册里 x2 是 100 V/V（x1 才是 50 V/V），配 20 mohm 分流电阻是 2 V/A，2 A 时理论 4 V，超过 3.3 V 供电和 ADC 量程。型号后缀与增益的对应很容易记混，必须以数据手册为准。

**来源**
- [INA199 datasheet (SBOS469H)](https://www.ti.com/lit/ds/symlink/ina199.pdf) — Texas Instruments, datasheet, §6.5 Electrical Characteristics; Table 7-1
- [ESP32-C3 Series Datasheet](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, §5.5 ADC Characteristics, Table 5-6 ADC Calibration Results

<a id="ANA-ARC-001"></a>
#### ANA-ARC-001 · 选型前先做误差预算（失调/漂移/增益/容差）
`should` · 可信度 `high` · 适用: current_sense, bridge_sensor, adc_frontend, op_amp · 标签: cat-feeder

**规则** 在选放大器、分流电阻、增益电阻之前，先把失调、失调温漂、增益误差、电阻容差/温漂、基准误差、噪声列成预算表，按最坏情况和 RSS 两种方式求和，并让每一项不超过总误差目标分到的份额。

**依据** 失调类误差与被测电流大小无关，会在小信号端主导误差；增益类误差与信号成比例。不先量化各项，就无法判断该换更好的器件还是放宽要求。

| 参数 | 判据 | 备注 |
|---|---|---|
| `per_term_error_target` | <= 0.1 % | SLYT762 的示例：满量程 ±50 mV 的分流检测，每一项误差贡献不超过 ±0.1%。数值随系统要求缩放，不是通用阈值 |
| `amp_offset_for_example` | <= 100 uV | 同一示例要求放大器失调 ≤ 100 uV |
| `amp_offset_drift_for_example` | <= 1 uV/degC | 同一示例要求失调温漂 ≤ 1 uV/degC |
| `gain_resistor_tc_for_example` | <= 10 ppm/degC | 同一示例要求增益电阻和分流电阻容差 0.1%、温漂 ≤ 10 ppm/degC |

**验证**
- `bom_check`（partial）· Python/表格脚本：读取 BOM 里每个模拟器件的数据手册最大/最小值（Vos、dVos/dT、增益误差、电阻容差和 TCR、基准精度） — 按最坏情况（全部取极限）和 RSS 两种方式求和，折算到满量程的百分比以及最小工作电流点的百分比；任何单项超过分配份额或总和超过目标即不通过
- `spice`（partial）· ngspice：容差 Monte Carlo + 温度扫描（.temp / .options temp） — 对关键传递函数（Vout/Iin 或 码值/Vin）做 ≥ 200 次 Monte Carlo，并在 -40/25/85 degC 各一轮，统计 3-sigma 误差并与预算表对账

**来源**
- [Selecting amplifiers for shunt-based current sensing in 3-phase motor drives (SLYT762)](https://www.ti.com/lit/pdf/slyt762) — Texas Instruments, app_note, Accuracy / error example
- [AN1177 Op Amp Precision Design: DC Errors](https://ww1.microchip.com/downloads/en/appnotes/01177a.pdf) — Microchip, app_note, Process and Environmental Variations (worst case vs RSS)

<a id="ANA-ARC-002"></a>
#### ANA-ARC-002 · 按失调与量程选分流电阻阻值
`should` · 可信度 `high` · 适用: current_sense, ina199, shunt · 标签: cat-feeder

**规则** 分流电阻的满量程压降要足够大，使放大器失调（INA199 最大 ±150 uV）在最小关心电流处仍远小于信号；同时压降乘以增益后不能超过放大器输出摆幅和 ADC 量程，且 I2R 功耗在电阻额定值内。

**依据** 失调是与电流无关的绝对误差，小电流时占比最大；压降大又会增加分流电阻功耗和发热。INA199 是零漂移结构，数据手册称在约 10 mV 满量程下就能达到传统 100 mV 满量程的精度。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ina199_vos_max` | <= 150 uV | INA199 输入失调最大值（典型 ±5 uV），温漂最大 0.5 uV/degC |
| `full_scale_sense_voltage` | >= 10 mV | 数据手册原话是 on the order of 10 mV 即可达到与 100 mV 相当的精度；上限由输出摆幅决定，例：3.3 V 供电的 INA199A1 可用 60 mV |

**验证**
- `bom_check`（partial）· 脚本：从网表取 R_shunt、放大器型号（增益）、Imin/Imax、V+ — 算 Vsense_min = Imin*R_shunt，要求 Vos_max/Vsense_min 小于预算分给失调的份额；算 Vsense_max*G <= V+ - 0.2 V；算 Imax^2*R_shunt 小于电阻额定功率的降额值（按电阻数据手册）
- `spice`（partial）· ngspice：DC 扫描 Iin — 对 Vos 取 ±最大值，扫描 Imin 到 Imax，记录输出相对理想值的误差曲线，小电流端误差必须在预算内

**来源分歧** SLYT762 说电机驱动里分流压降通常 ±25 到 ±250 mV，INA199 手册说 10 mV 量级就够。两者针对的放大器失调不同（零漂移 vs 普通），按所选放大器的失调反推，不要套用固定数值。示例板（猫咪喂食器）的 20 mohm 分流电阻在 100 mA 时只有 2 mV，最坏失调 150 uV 就是 7.5%（典型 5 uV 约 0.25%），需要在固件里做零点校准。

**来源**
- [INA199 26-V, Bidirectional, Zero-Drift Current-Sense Amplifier datasheet (SBOS469H)](https://www.ti.com/lit/ds/symlink/ina199.pdf) — Texas Instruments, datasheet, §6.5 Electrical Characteristics, §7.3.2 Selecting RS
- [Selecting amplifiers for shunt-based current sensing in 3-phase motor drives (SLYT762)](https://www.ti.com/lit/pdf/slyt762) — Texas Instruments, app_note, offset is more critical at low current; shunt voltage typically ±25 to ±250 mV in motor drives

<a id="ANA-ARC-005"></a>
#### ANA-ARC-005 · 放大器带宽/建立时间要小于最短导通时间
`should` · 可信度 `high` · 适用: current_sense, pwm, motor_driver · 标签: cat-feeder

**规则** PWM 驱动下用低边分流检测时，放大器带宽和压摆率决定的建立时间必须小于低边开关的最短导通时间（对称采样时按其一半计），ADC 采样点放在导通窗口中央（SLYT762 Figure 2：低边分流的理想采样点在 PWM 中心）；如果不做逐周期采样，则用 RC 把 PWM 纹波滤到 ADC 分辨率以下后再平均（这一句是本库的工程补充，SLYT762 与 INA199 手册均未讨论，没有出处数值）。

**依据** 低边分流只在开关导通期间有电流，采样落在边沿附近会读到建立过程中的值。INA199 带宽仅 14 到 80 kHz、压摆率 0.4 V/us，PWM 频率高时尤其容易出错。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ina199_bandwidth_x1` | == 80 kHz | INA199x1，CLOAD = 10 pF；x2 = 30 kHz，x3 = 14 kHz |
| `ina199_slew_rate` | == 0.4 V/us | INA199 典型压摆率 |
| `settling_time_vs_min_on_time` | < 1 ratio | 建立时间 / 最短导通时间 < 1；SLYT762 建议对称采样时按最短导通时间的一半来要求，所以实际目标是比值 < 0.5 |

**验证**
- `spice`（partial）· ngspice：PULSE 电流源 + 放大器带宽/压摆限制的行为模型 — 加最短占空比的电流脉冲，读 ADC 采样时刻的输出，要求与稳态值差小于 0.5 LSB（或预算份额）
- `bench`（manual）· 示波器：同时看分流电阻两端（差分探头）、放大器输出、ADC 采样触发信号 — 在最小占空比和最大占空比下，确认采样触发落在输出已稳定的平台上

**来源**
- [Selecting amplifiers for shunt-based current sensing in 3-phase motor drives (SLYT762)](https://www.ti.com/lit/pdf/slyt762) — Texas Instruments, app_note, Placement No. 2: bandwidth and slew rate; ideal sampling at PWM center
- [INA199 datasheet (SBOS469H)](https://www.ti.com/lit/ds/symlink/ina199.pdf) — Texas Instruments, datasheet, §6.5 Frequency response

<a id="ANA-ARC-006"></a>
#### ANA-ARC-006 · 运放相位裕度目标 ≥ 45°，容性负载用隔离电阻
`should` · 可信度 `high` · 适用: op_amp, adc_driver, reference_buffer

**规则** 运放电路的环路增益相位裕度至少 45°，对过冲敏感的场合取 60°；驱动较大电容负载（如 ADC 基准或滤波电容）时，在运放输出与电容之间串隔离电阻 RISO，并按数据手册的 GBW 和开环输出阻抗 RO 计算，再用仿真确认。

**依据** 电容负载与运放开环输出阻抗形成额外极点，降低相位裕度；RISO 在环路里引入零点抵消该极点，把闭合速率拉回 20 dB/decade。RISO 越大相位裕度越高，但直流误差和建立时间变差。

| 参数 | 判据 | 备注 |
|---|---|---|
| `phase_margin_min` | >= 45 deg | 常用最低目标；要低过冲时取 60 deg |
| `rate_of_closure` | == 20 dB/decade | Aol 与 1/beta 交点处的闭合速率应为 20 dB/decade |

**验证**
- `spice`（partial）· ngspice/TINA：在反馈环里断环做 AC 分析（Aol*beta 的幅相图），再加小信号阶跃响应 — 读单位增益交点处相位裕度 >= 45 deg（目标 60 deg），阶跃响应过冲符合要求，且在最大电容负载和最差温度下都成立
- `bench`（manual）· 示波器 + 信号源：小信号方波阶跃 — 输出阶跃响应无持续振铃，过冲与仿真一致

**来源**
- [Determine Optimal Isolation Resistance for Driving Capacitive Load (SBOA418)](https://www.ti.com/lit/pdf/sboa418) — Texas Instruments, app_note, §1-§4, Equation 2
- [Do-it-yourself: Three Ways to Stabilize Op Amp Capacitive Loads (SSZT999)](https://www.ti.com/lit/pdf/sszt999) — Texas Instruments, app_note

<a id="ANA-ARC-007"></a>
#### ANA-ARC-007 · ESP32-C3 内置 ADC 的误差与使用边界
`should` · 可信度 `high` · 适用: esp32c3, adc_frontend · 标签: cat-feeder

**规则** 把 ESP32-C3 内置 ADC 当作约 12 位、总误差 ±10 mV（量程 ≤ 1300 mV）或 ±35 mV（量程 2500 mV）的粗测通道：只使用 ADC1（GPIO0 到 GPIO4），启用基于 eFuse 的 curve fitting 校准，把信号尽量放在低衰减档的精确区间，要求更高精度时改用外置 ADC。

**依据** ADC 参考电压设计值 1100 mV，芯片间实际在 1000 到 1200 mV；ADC2 在部分芯片版本上不可用且没有出厂校准；高电压端误差明显变大，Espressif 的实测在 2890 mV 附近约 50 mV。

| 参数 | 判据 | 备注 |
|---|---|---|
| `dnl_inl` | <= 12 LSB | DNL ±7 LSB，INL ±12 LSB，条件是外接 100 nF、直流输入、25 degC、Wi-Fi 关闭 |
| `adc_reference_spread` | 1000 … 1200 mV | 芯片间 ADC 参考电压范围，设计值 1100 mV |

**验证**
- `bench`（partial）· 可编程电压源/高精度万用表 + 固件 — 在量程内取 ≥ 5 个点（含 0.1 V、1.0 V、2.0 V），每点平均 ≥ 64 次采样，校准后误差必须落在数据手册给出的 ±10/±35 mV 内；Wi-Fi 开启状态下再测一遍，记录退化量
- `review`（manual）· 固件评审 — 确认使用 adc_cali_create_scheme_curve_fitting()；不在 ADC2 上做单次读；每个衰减档单独建校准句柄

**来源**
- [ESP32-C3 Series Datasheet](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, §4.2.2.1 SAR ADC; §5.5 ADC Characteristics
- [ADC Calibration Driver - ESP32-C3 (ESP-IDF)](https://docs.espressif.com/projects/esp-idf/en/v5.5.3/esp32c3/api-reference/peripherals/adc_calibration.html) — Espressif, tool_doc
- [Comparing ADC Performance of Espressif SoCs](https://developer.espressif.com/blog/2025/08/adc-performance/) — Espressif, blog

<a id="ANA-ARC-009"></a>
#### ANA-ARC-009 · 称重电桥：排查引线电阻对比例测量的破坏
`should` · 可信度 `high` · 适用: bridge_sensor, load_cell, hx711 · 标签: cat-feeder

**规则** 电桥用 ADC 的基准同时作为激励（比例测量）时，激励线上的电阻会让电桥实际电压低于 ADC 基准电压。引线很短时用四线接法；引线长或精度要求高时用六线接法并把 sense 线接到电桥端，或把 ADC 放到电桥旁边。HX711 模块没有 sense 引脚，激励线要尽量短、电阻低。

**依据** 激励电流在引线电阻上产生压降，破坏 Vout 与基准的比例关系，表现为与线长、温度相关的增益误差。sense 线几乎不载流，所以不引入类似的误差。

| 参数 | 判据 | 备注 |
|---|---|---|
| `example_lead_error` | == 0.6 % | TI 示例：5 V 激励、350 ohm 电桥，激励线每根 1 ohm 就产生 0.6% 的测量误差 |

**验证**
- `bench`（manual）· 称重传感器 + 标准砝码 + 万用表 — 在实际线长下测传感器端和 ADC 板端的激励电压，差值/激励电压超过误差预算份额则不通过；或用标准砝码在线长变化前后对比读数
- `review`（manual）· 接线评审 — 确认线长和线规：算 R_lead_total*I_excitation / V_excitation，对照预算

**来源**
- [A Basic Guide to Bridge Measurements (SBAA532A)](https://www.ti.com/lit/an/sbaa532a/sbaa532a.pdf) — Texas Instruments, app_note, §3.1 Ratiometric Measurements, §3.2 Four-Wire Bridge, §3.3 Six-Wire Bridge

<a id="ANA-ARC-010"></a>
#### ANA-ARC-010 · 运放选型：偏置电流、源阻抗与温度
`should` · 可信度 `medium` · 适用: op_amp, high_impedance

**规则** 源阻抗较高时优先选 CMOS/JFET 输入、低偏置电流的运放，并按最高工作温度的偏置电流算 IB 乘以两个输入端等效电阻带来的误差；双极型输入时让两个输入端看到的直流电阻相等。偏置电流在温度上升时显著增大。

**依据** CMOS 运放的偏置电流主要是 ESD 二极管反向漏电，温度每升高 10 degC 约翻倍；双极型输入的偏置电流在 -40 到 125 degC 间约有 4 倍变化。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esd_diode_leakage_doubling` | == 10 degC | ESD 二极管反向漏电约每升高 10 degC 翻一倍 |

**验证**
- `bom_check`（partial）· 脚本：读数据手册 IB(25 degC) 与 IB(Tmax) — 对每个运放输入节点算 (IB(Tmax))*(等效电阻) 并折算到输出；与失调预算份额对比
- `spice`（partial）· ngspice：在运放宏模型输入端加 IB 电流源，温度扫描 — 在 Tmin、25、Tmax 三个温度下比较输出直流误差

**来源**
- [AN1177 Op Amp Precision Design: DC Errors](https://ww1.microchip.com/downloads/en/appnotes/01177a.pdf) — Microchip, app_note, Input bias current section

<a id="ANA-ARC-004"></a>
#### ANA-ARC-004 · 按系统约束选择分流电阻位置
`consider` · 可信度 `high` · 适用: current_sense, motor_driver · 标签: cat-feeder

**规则** 低边分流（电阻在开关管源极与地之间）共模电压接近 0 V，可用非隔离的低成本放大器，但只在低边开关导通期间能测到电流；高边或串联在电机线上可连续测量，但需要高共模电压和高 CMRR 的放大器并要面对 PWM 共模瞬变。按是否需要连续电流、共模范围和成本选择。

**依据** 分流位置决定共模电压、是否有 PWM 共模瞬变、什么时候能采样。选错会导致采样窗口丢失或放大器过载。

**验证**
- `review`（manual）· 架构评审清单 — 列出：共模范围（含 -0.3 V/-0.1 V 地附近的下限）、是否需要电流连续采样、PWM 周期与最短导通时间、MCU 是否与功率地共地；确认所选放大器的共模范围覆盖实际共模电压
- `spice`（partial）· ngspice — 仿真分流两端对地电压随 PWM 变化，确认共模电压始终落在放大器共模范围内（INA199 版本 A 下限 GND-0.3 V，版本 B/C 下限 GND-0.1 V）

**来源**
- [Selecting amplifiers for shunt-based current sensing in 3-phase motor drives (SLYT762)](https://www.ti.com/lit/pdf/slyt762) — Texas Instruments, app_note, Table 1; Placement No. 2 low-side shunts
- [INA199 datasheet (SBOS469H)](https://www.ti.com/lit/ds/symlink/ina199.pdf) — Texas Instruments, datasheet, §6.5 common-mode input range

<a id="ANA-ARC-008"></a>
#### ANA-ARC-008 · HX711 按需选数据率，并丢弃建立期数据
`consider` · 可信度 `high` · 适用: hx711, bridge_sensor · 标签: cat-feeder

**规则** 称重这类慢信号选 10 SPS（RATE = 0）以获得更低噪声；上电、复位、切换通道或增益之后，固件丢弃建立时间内的转换结果（10 SPS 约 400 ms，80 SPS 约 50 ms）再取数。

**依据** HX711 在增益 128 时输入噪声 10 SPS 约 50 nV rms，80 SPS 约 90 nV rms；数据手册明确设定了建立时间，之前的输出不是有效数据。

| 参数 | 判据 | 备注 |
|---|---|---|
| `hx711_noise_10sps_gain128` | == 50 nV rms | RATE = 0，增益 128，输入噪声典型值；RATE = 1（80 SPS）为 90 nV rms |
| `hx711_settling_time_10sps` | == 400 ms | RATE = 0；RATE = DVDD 时 50 ms。适用于上电、复位、通道切换、增益切换 |

**验证**
- `bench`（partial）· 固件 + 串口日志 — 上电或切换增益后连续读 ≥ 20 个样本，确认前 400 ms（80 SPS 时 50 ms）内的样本被固件丢弃，之后的样本标准差落到数据手册噪声量级
- `review`（manual）· 固件评审 — 检查固件是否在 reset/增益切换后加了等待，且 RATE 引脚连接（模块上通常是焊盘或跳线）与固件假设的数据率一致

**来源**
- [HX711 24-Bit Analog-to-Digital Converter (ADC) for Weigh Scales](https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf) — Avia Semiconductor, datasheet, Table 2 Key Electrical Characteristics, note (1)

## 符号封装库（library）

<a id="ANA-LIB-001"></a>
#### ANA-LIB-001 · 分流电阻用四端子封装并保留开尔文焊盘
`should` · 可信度 `high` · 适用: shunt, current_sense · 标签: cat-feeder

**规则** 分流电阻的封装库要带独立的 sense 焊盘（四端子或带 Kelvin 的焊盘），sense 焊盘与大电流焊盘分属不同焊盘编号；焊盘尺寸与位置遵循电阻厂商数据手册的推荐焊盘图形。

**依据** 只有电流焊盘与 sense 焊盘分开，布线才能做到让大电流只流经电阻本体，sense 走线只测电阻两端电压。TI 的布局规则第三条就是按厂商推荐的封装、位置和焊盘设计来做。

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 遍历标注为 shunt 的封装，要求焊盘数 >= 4 或带独立 sense 焊盘；两个 sense 焊盘分别属于 CS_P/CS_N 网络，不与电流焊盘网络相同
- `review`（manual）· 对照电阻厂商数据手册 — 焊盘尺寸、间距与推荐图形一致

**来源**
- [Shunt Resistor Layout Considerations (TI Precision Labs - Current Sense Amplifiers)](https://www.ti.com/content/dam/videos/external-videos/en-us/4/3816841626001/6076326896001.mp4/subassets/current-sense-amplifiers-shunt-resistor-layout-presentation-quiz.pdf) — Texas Instruments, vendor_guide, Rule 3 - follow the resistor maker's guidelines
- [INA240 datasheet (SBOS662C)](https://www.ti.com/lit/ds/symlink/ina240.pdf) — Texas Instruments, datasheet, §9.3.2 Kelvin Connection from the Current-Sense Resistor

## 原理图（schematic）

<a id="ANA-SCH-001"></a>
#### ANA-SCH-001 · SAR ADC 输入 RC：C ≥ 20 倍采样电容，用 C0G
`should` · 可信度 `high` · 适用: sar_adc, adc_driver

**规则** SAR ADC 输入端的飞轮（charge-bucket）滤波电容 CFILT 取 ADC 内部采样电容 CSH 的 20 倍以上（SBOA443 式 7 与 ADS8860 手册的说法；例：CSH = 59 pF 则 CFILT >= 1180 pF，见 conflicts），介质用 C0G/NP0；串联电阻 RFILT 取使 RC 在采样时间内建立到 n 位精度的最大值，并留意它与放大器稳定性和失真的折中，电阻容差优于 1%。

**依据** 采样开关闭合时 CFILT 供应大部分充电电荷，放大器只补充一小部分，因此对放大器带宽的要求降低；C0G 在电压、频率、温度下容值稳定，不引入非线性失真。n 位建立需要 ln(2^n) 个时间常数。

| 参数 | 判据 | 备注 |
|---|---|---|
| `c_filt_over_c_sh` | >= 20 ratio | SBOA443 式 7（CFILT = 20 x CSH）在 4 V 量程、允许 100 mV 跌落的假设下推出；量程或允许跌落不同，比值要重算。SBOA443 表 4-2（ADS8860，CSH = 59 pF）给出下限 10 x = 590 pF、标称 20 x = 1180 pF、上限 30 x = 1770 pF，所以 >= 20 是标称值而不是 SBOA443 的绝对下限 |
| `time_constants_for_n_bit_settling` | qualitative | tau = t_acq / ln(2^n)；12 位约需 8.3 tau，16 位约需 11 tau |
| `rflt_example_ads8860` | <= 22 ohm | ADS8860（CSH = 59 pF）的示例，不是通用上限；RFLT 过大增加失真，过小影响放大器稳定 |
| `filter_resistor_tolerance` | < 1 % | ADS8860 要求两路输入电阻容差 < 1% 以保持平衡 |

**验证**
- `spice`（partial）· ngspice/TINA-TI：放大器 + RFILT + CFILT + ADC 采样开关与 CSH 的模型 — 在最大采样率下做瞬态，要求采样结束时输入节点距最终值 < 0.5 LSB，且放大器输出无振荡（相位裕度见 ANA-ARC-006）
- `bom_check`（full）· 脚本：读 ADC 数据手册 CSH 与 BOM 里的滤波电容 — C >= 20*CSH；介质字段为 C0G/NP0；电阻容差 <= 1%

**来源分歧** ADS8860 手册 §10.1.2.2 写“至少 20 倍采样电容”，同段又写 CSH = 59 pF 故 CFLT > 590 pF，而 590 pF 只是 10 倍（20 倍应为 1180 pF），手册自相矛盾。SBOA443 表 4-2 的 590 pF 也标为 CFILT,MIN = 10 x CSH。本条以 20 倍（1180 pF）为标称，590 pF 只当作绝对下限（审计更正）。

**来源**
- [Current Sense Amplifier Considerations for Driving SAR ADCs (SBOA443)](https://www.ti.com/lit/an/sboa443/sboa443.pdf) — Texas Instruments, app_note, §3.1 The Filter Capacitor, Eq. 7
- [ADS8860 16-bit 1-MSPS SAR ADC datasheet (SBAS569B)](https://www.ti.com/lit/ds/symlink/ads8860.pdf) — Texas Instruments, datasheet, §10.1.2.2 Charge-Kickback Filter; §12.1
- [TI Precision Labs - Driving SAR and Delta-Sigma ADC Inputs](https://www.ti.com/lit/ml/sprpeo2/sprpeo2.pdf) — Texas Instruments, vendor_guide

<a id="ANA-SCH-002"></a>
#### ANA-SCH-002 · Σ-Δ ADC 差分输入：Cdiff ≥ 10 × Ccm，R < 1 kΩ
`should` · 可信度 `high` · 适用: delta_sigma_adc, bridge_sensor, differential_input

**规则** Σ-Δ ADC 的差分输入做一阶 RC 低通时，差分电容 CDIFF 至少是两个共模电容 CCM 的 10 倍，滤波电阻 < 1 kohm，电容用 C0G，电阻用 0.1% 金属膜；若同时滤波基准，信号和基准滤波器的时间常数要匹配。

**依据** CCM1/CCM2 的失配会把共模噪声转换成差模噪声，CDIFF 大一个数量级可压低这种转换；滤波电阻上有输入电流，阻值大就带来增益误差。

| 参数 | 判据 | 备注 |
|---|---|---|
| `cdiff_over_ccm` | >= 10 ratio | ADS1115 数据手册 §9.2.2.6；TI Precision Labs 的建议是 CCM = CDIFF 的 1/10 |
| `filter_resistor_max` | < 1 kohm | ADS1115 的限制；INA199 输入端另有 10 ohm 限制，见 ANA-SCH-003 |

**验证**
- `bom_check`（full）· 脚本：识别 ADC 差分输入上的 RC 网络 — C_DIFF/C_CM >= 10；R 总和 < 1 kohm；C 介质为 C0G；两路输入电阻值相同
- `spice`（partial）· ngspice：AC 分析，CCM1/CCM2 取 ±5% 失配 — 在 1 kHz 到 1 MHz 范围内比较共模到差模转换（CMRR 劣化量）是否在预算内

**来源**
- [ADS1113/4/5 datasheet (SBAS444E)](https://www.ti.com/lit/ds/symlink/ads1115.pdf) — Texas Instruments, datasheet, §9.2.2.6 First-Order RC Filter Considerations; §11.1
- [TI Precision Labs - Driving SAR and Delta-Sigma ADC Inputs](https://www.ti.com/lit/ml/sprpeo2/sprpeo2.pdf) — Texas Instruments, vendor_guide, Σ-Δ input recommendations
- [ADS1235 datasheet (SBAS824)](https://www.ti.com/lit/ds/symlink/ads1235.pdf) — Texas Instruments, datasheet, §8.3.4.1 External Reference (match filter time constants)

<a id="ANA-SCH-003"></a>
#### ANA-SCH-003 · INA199 输入滤波：串联电阻 ≤ 10 Ω
`should` · 可信度 `high` · 适用: ina199, current_sense · 标签: cat-feeder

**规则** 在 INA199 输入引脚前加差分 RC 滤波时，两个串联电阻各不超过 10 ohm，并按内部输入电阻 RINT（±30% 容差）算增益误差：gain error = 100 - 100*1250*RINT/(1250*RS + 1250*RINT + RS*RINT)。如果要更强的滤波，改到放大器输出端做。

**依据** INA199 内部偏置网络使两个输入端的偏置电流在有差分电压时不相等，外部串联电阻会把这个不对称变成差分误差，表现为增益误差；RINT 随增益档为 20/10/5 kohm。

| 参数 | 判据 | 备注 |
|---|---|---|
| `series_resistor_max` | <= 10 ohm | INA199 §7.4.1；INA240 数据手册给出同样的 10 ohm |
| `gain_error_10ohm_x2` | == 0.89 % | INA199x2（RINT = 10 kohm），RS = 10 ohm 的增益误差；手册里 x1 的数值也写作 0.84% |
| `rint_by_gain` | qualitative | INA199x1 = 20 kohm，x2 = 10 kohm，x3 = 5 kohm；内部电阻容差 ±30% |

**验证**
- `bom_check`（full）· 脚本：从网表取输入串联电阻和电容 — 两个串联电阻相等且 <= 10 ohm；用上式算增益误差并计入预算
- `spice`（partial）· ngspice：INA199 用 RINT + 偏置电流源 + 理想放大器建模 — 扫描 RS = 0 到 20 ohm、RINT ±30%，输出对分流电压的增益偏差与公式一致

**来源**
- [INA199 datasheet (SBOS469H)](https://www.ti.com/lit/ds/symlink/ina199.pdf) — Texas Instruments, datasheet, §7.4.1 Input Filtering, Eq. 1-2, Tables 7-1/7-2
- [INA240 datasheet (SBOS662C)](https://www.ti.com/lit/ds/symlink/ina240.pdf) — Texas Instruments, datasheet, §9.1.1 Input Filtering
- [Current Sense Amplifiers: Input and Output Filtering](https://www.onsemi.com/company/news-media/blog/industrial/en-us/current-sense-amplifiers-input-and-output-filtering) — onsemi, blog

<a id="ANA-SCH-004"></a>
#### ANA-SCH-004 · REF 接地时给零电流区留死区余量
`should` · 可信度 `high` · 适用: ina199, unidirectional_current_sense · 标签: cat-feeder

**规则** 单向测量把 INA199 的 REF 接地时，输出最低只能到 GND + 5 mV（典型）至 GND + 50 mV（最大，RL = 10 kohm），而失调乘增益后可达 ±15 mV（增益 100）；因此固件对低于该值的读数要当作死区，或把 REF 偏置到摆幅余量之上，并在固件里做零点校准。

**依据** 输出级不能真正到达 0 V，负失调会被截断，低电流段读数与实际不线性。

| 参数 | 判据 | 备注 |
|---|---|---|
| `swing_to_gnd_typ` | == 5 mV | INA199，RL = 10 kohm 到 GND |
| `swing_to_gnd_max` | <= 50 mV | 同上，-40 到 125 degC 最大值 |

**验证**
- `bench`（manual）· 分流电阻开路/电机停转 + 万用表 + 固件 — 无电流时测 OUT 电压和 ADC 读数，记录零点；用 10 到 100 mA 小电流扫描，确认固件对死区以下数据的处理（报 0 或标记不可信）
- `spice`（partial）· ngspice：带 Vos 和输出摆幅钳位的行为模型 — Vos = ±150 uV 时输出相对理想值的误差曲线，找出可信的最小电流

**来源**
- [INA199 datasheet (SBOS469H)](https://www.ti.com/lit/ds/symlink/ina199.pdf) — Texas Instruments, datasheet, §6.5 Voltage output: Swing to GND; Figure 6-6

<a id="ANA-SCH-005"></a>
#### ANA-SCH-005 · INA199 输出到 ADC 引脚：先串电阻再接 100 nF
`should` · 可信度 `medium` · 适用: ina199, esp32c3_adc · 标签: cat-feeder

**规则** INA199 的最大容性负载是 1 nF（无持续振荡），而 ESP32-C3 ADC 引脚按 Espressif 建议要挂 100 nF；二者之间必须串一个电阻（RC 低通），电阻值用 SPICE/示波器确认无振铃，且 RC 转折频率高于被测电流带宽、低于 INA199 带宽。

**依据** 100 nF 直接接在输出缓冲上远超 1 nF 限制，会降低相位裕度甚至振荡；ESP32-C3 数据手册的 DNL/INL 指标也是在外接 100 nF 条件下给出的。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ina199_max_capacitive_load` | <= 1 nF | INA199 无持续振荡的最大容性负载 |
| `esp32_adc_pad_bypass` | == 100 nF | Espressif 文档建议的 ADC 输入端旁路电容（陶瓷） |

**验证**
- `spice`（partial）· ngspice/TINA-TI：INA199 官方宏模型 + Rs + 100 nF — 输出小信号阶跃响应无振铃、过冲 < 预算；Rs 取标称和 ±5%
- `bench`（manual）· 示波器：阶跃负载电流 + 探头接 OUT 与 ADC 引脚 — OUT 引脚无高频振荡，ADC 引脚的建立时间小于固件采样间隔

**来源分歧** 两个数据手册各自给出条件（1 nF 上限、100 nF 条件），本条把它们合并推出需要串电阻，具体阻值没有现成出处，所以只定性要求并要求仿真确认，confidence 为 medium。

**来源**
- [INA199 datasheet (SBOS469H)](https://www.ti.com/lit/ds/symlink/ina199.pdf) — Texas Instruments, datasheet, §6.5 Maximum capacitive load
- [ADC Calibration Driver - ESP32-C3 (ESP-IDF)](https://docs.espressif.com/projects/esp-idf/en/v5.5.3/esp32c3/api-reference/peripherals/adc_calibration.html) — Espressif, tool_doc
- [ESP32-C3 Series Datasheet](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, Table 5-5 ADC Characteristics (100 nF condition)

<a id="ANA-SCH-006"></a>
#### ANA-SCH-006 · 放大器输入保护：按手册限流（1–10 mA），注意钳位漏电
`should` · 可信度 `medium` · 适用: op_amp, current_sense, adc_frontend

**规则** 运放输入端有二极管钳位到电源轨时，输入电压可能超出电源轨 0.3 V 以上就要串电阻把电流限制在数据手册给出的值以内（各器件不同：OPA333 绝对最大表为 ±1 mA、同页脚注与 §7.3.2 为 10 mA，INA199 为 5 mA，数据手册之间与自身都不一致时取较严的值）；外加的钳位二极管/TVS 在最高工作温度下的漏电要和运放偏置电流、源阻抗一起算进误差。INA199 输入可耐 26 V，高于 26 V 的共模瞬变用齐纳型吸收器加小电阻。

**依据** ESD 二极管导通后的电流可能很大，不限流会损坏器件；二极管漏电随温度翻倍增长，高阻节点上外加钳位的漏电会直接变成失调。

| 参数 | 判据 | 备注 |
|---|---|---|
| `opa333_input_current_footnote` | <= 10 mA | OPA333 §6.1 注 (2)：输入端超出电源轨 0.3 V 以上时限流到 10 mA 或更小；§7.3.2 同样说瞬时过压在 10 mA 限流下可承受。注意同一表里 Signal input terminals 的电流绝对最大值写的是 ±1 mA（见下一条） |
| `opa333_input_current_abs_max` | <= 1 mA | OPA333 §6.1 绝对最大额定值表，Signal input terminals 电流 ±1 mA，比脚注的 10 mA 更严，数据手册自身不一致，设计取较严值 |
| `ina199_input_current_max` | <= 5 mA | INA199 §6.1：Input current into all pins 最大 5 mA；脚注 (3)：任一引脚电压超过额定值时需把该脚电流限制在 5 mA |
| `ina199_input_voltage_max` | <= 26 V | INA199 输入可承受，不论是否上电 |

**验证**
- `bom_check`（partial）· 脚本：读每个模拟输入器件的 absolute maximum 输入电流 — 按最大过压 (Vover - V_rail - 0.3 V)/R_series 算限流是否 <= 数据手册值
- `spice`（partial）· ngspice：钳位二极管模型 + 温度扫描 — 在 Tmax 下算外加钳位漏电在源阻抗上产生的误差，对照失调预算

**来源分歧** 没有读到专门讲外加钳位二极管/TVS 漏电的应用笔记，漏电随温度翻倍的说法来自 AN1177 对 ESD 二极管的描述，外加钳位器件要以其数据手册为准。

**来源**
- [OPA333/OPA2333 datasheet (SBOS351E)](https://www.ti.com/lit/ds/symlink/opa333.pdf) — Texas Instruments, datasheet, §6.1 note (2); §7.3.2 Input Voltage, Figure 18
- [INA199 datasheet (SBOS469H)](https://www.ti.com/lit/ds/symlink/ina199.pdf) — Texas Instruments, datasheet, §7.4.4; §9
- [AN1177 Op Amp Precision Design: DC Errors](https://ww1.microchip.com/downloads/en/appnotes/01177a.pdf) — Microchip, app_note

<a id="ANA-SCH-007"></a>
#### ANA-SCH-007 · HX711 的数字电源跟随 MCU，模拟电源去耦
`should` · 可信度 `high` · 适用: hx711, esp32c3 · 标签: cat-feeder

**规则** HX711 的 DVDD 与 MCU 使用同一电源（本板是 3.3 V），DOUT 的摆幅才与 MCU 匹配；不用片内稳压器时 VFB 接 AGND、BASE 悬空、VSUP 接 AVDD 或 DVDD 中较高者，AVDD 按数据手册 Fig.1 配 10 uF 去耦（Fig.1 里的 0.1 uF 接在 VBG 基准旁路脚上，且手册写明不用片内稳压器时该电容不需要，不是 AVDD 去耦）；模块若按 5 V 供电，需做电平转换后再接 ESP32-C3。

**依据** 数据手册要求 DVDD 与 MCU 同电源；ESP32-C3 的 GPIO 按 3.3 V 供电，DOUT 若是 5 V 电平可能超出其绝对最大额定值（以 ESP32-C3 数据手册为准，本条未核对该数值）。AVDD 同时决定激励电压和满量程（±0.5*AVDD/增益），其噪声直接进入测量。

| 参数 | 判据 | 备注 |
|---|---|---|
| `hx711_supply_range` | 2.6 … 5.5 V | AVDD、DVDD 均为 2.6 到 5.5 V |
| `hx711_psrr` | == 100 dB | 增益 128、10 SPS 条件下的电源抑制比 |

**验证**
- `review`（manual）· 原理图评审 — 追踪 HX711 模块的 DVDD/VCC 引脚网络，确认与 ESP32-C3 的 3V3 是同一网络；若是 5 V 则必须有电平转换
- `bench`（manual）· 示波器 + 万用表 — 上电状态下量 DOUT 空闲高电平，必须 <= MCU 的 3.3 V 供电；在 Wi-Fi 发射突发时观察 AVDD 纹波

**来源**
- [HX711 24-Bit Analog-to-Digital Converter (ADC) for Weigh Scales](https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf) — Avia Semiconductor, datasheet, Power Supply Options; Fig. 1; Table 2

<a id="ANA-SCH-008"></a>
#### ANA-SCH-008 · HX711 输入共模电压要落在允许范围内
`should` · 可信度 `high` · 适用: hx711, bridge_sensor · 标签: cat-feeder

**规则** HX711 差分输入的共模电压必须在 AGND + 1.2 V 到 AVDD - 1.3 V 之内；换用不同的 AVDD（5 V 或 3.3 V）时重新核对电桥共模点（通常是激励的一半）是否仍在这个窗口内。

**依据** 共模超出范围时 PGA 输入级失去线性，输出数据错误但不一定饱和，很难从读数上发现。

| 参数 | 判据 | 备注 |
|---|---|---|
| `hx711_cm_range_low_offset` | >= 1.2 V | 共模输入下限 = AGND + 1.2 V |
| `hx711_cm_range_high_offset` | <= 1.3 V | 共模输入上限 = AVDD - 1.3 V；AVDD = 3.3 V 时窗口 1.2 到 2.0 V，AVDD = 5 V 时窗口 1.2 到 3.7 V |

**验证**
- `bom_check`（partial）· 脚本/手算 — 共模电压 Vcm = 电桥中点电压 = AVDD/2（对称电桥）；检查 AGND + 1.2 <= Vcm <= AVDD - 1.3；若在输入端加了偏置或衰减网络，用实际网络算
- `bench`（manual）· 万用表 — 接上称重传感器，量 INA+ 和 INA- 对 AGND 的直流电压，两者都落在窗口内

**来源**
- [HX711 24-Bit Analog-to-Digital Converter (ADC) for Weigh Scales](https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf) — Avia Semiconductor, datasheet, Table 2 Key Electrical Characteristics: common mode input

<a id="ANA-SCH-009"></a>
#### ANA-SCH-009 · NTC 热敏电阻：限制激励避免自热
`should` · 可信度 `high` · 适用: thermistor, temperature_sensing

**规则** 用热敏电阻测温时，激励功率不能超过封装的耗散能力，保持电阻-温度（零功率）工作状态；恒流激励时电流通常低于 100 uA，最好 20 uA 左右；线性化网络的电阻用 1% 或更好的金属膜。

**依据** 热敏电阻通电自热后电阻下降，读数比实际温度偏高，且误差随气流和安装方式变化。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ntc_excitation_current` | < 100 uA | AN685 的建议：通常低于 100 uA，最好 20 uA（10 kohm NTC 示例）；以热敏电阻耗散常数为准重新验算 |

**验证**
- `bom_check`（full）· 脚本：由分压网络和热敏电阻在最低电阻点（最高温度）算功耗 — P = I^2*R_ntc(Tmax)；P/耗散常数(mW/degC) 得到自热温升，要求小于温度误差预算份额
- `bench`（manual）· 固定温度箱或恒温浴 + 万用表 — 在激励通/断两种状态下测同一温度点的阻值，差值应在预算内

**来源**
- [AN685 Thermistors in Single Supply Temperature Sensing Circuits](https://ww1.microchip.com/downloads/en/appnotes/00685b.pdf) — Microchip, app_note, Current-Over-Time Mode; excitation discussion for Figure 4

<a id="ANA-SCH-011"></a>
#### ANA-SCH-011 · 未使用的运放通道接成跟随器
`should` · 可信度 `medium` · 适用: op_amp, multi_channel

**规则** 多通道运放里不用的通道接成电压跟随器（输出接反相输入），同相输入接到共模范围内的固定电平（单电源可用等值电阻分压到中点）；如果该运放不是单位增益稳定的，就用两个电阻设成稳定的增益。

**依据** 悬空输入会让通道处于不确定的噪声状态；输入饱和后恢复慢，还可能耦合到同封装的其他通道；不满足单位增益稳定的运放接成跟随器会振荡。

**验证**
- `erc`（partial）· KiCad ERC + 自定义检查脚本（读网表） — 对多单元运放的每个单元检查：输出与反相输入同网（或经反馈电阻），同相输入不悬空，直流电平在数据手册共模范围内
- `review`（manual）· 原理图评审 — 确认该运放是否单位增益稳定，不稳定时用了增益网络

**来源**
- [The Unused Op Amp - what to do? (TI E2E, The Signal)](https://e2e.ti.com/blogs_/archives/b/thesignal/posts/the-unused-op-amp-what-to-do) — Texas Instruments, blog
- [Avoiding Noise and Power Problems with Unused Op Amps (AN1957)](https://www.analog.com/en/technical-articles/avoiding-noise-and-power-problems-with-unused-op-amps.html) — Analog Devices (Maxim), app_note

<a id="ANA-SCH-013"></a>
#### ANA-SCH-013 · 外部基准：先带限滤波，再用大电容去耦
`should` · 可信度 `high` · 适用: sar_adc, delta_sigma_adc, voltage_reference

**规则** 给 SAR ADC 外部基准时，基准输出先经截止频率几百 Hz 的低通滤波以去掉宽带噪声，再用基准缓冲器驱动 REF 脚；REF 脚按数据手册配大电容（ADS8860 为 10 uF 以上，X7R，不额外并联小电容）。Σ-Δ ADC 的基准输入跨接电容，且基准滤波的时间常数要与信号输入滤波匹配。

**依据** 多数基准的宽带输出噪声有几百 uV rms，不限带宽会直接劣化 ADC 噪声；转换期间 REF 脚有动态电流，需要足够的电容保持电压在 1 LSB 以内。

| 参数 | 判据 | 备注 |
|---|---|---|
| `reference_filter_cutoff` | qualitative | ADS8860 手册原文是 a few hundred hertz 量级的低通，没有给出精确数值 |
| `ads8860_cref` | 10 … 22 uF | ADS8860 推荐 10 uF 或更大，Recommended Operating Conditions 给出 10 到 22 uF；X7R、0805、额定电压 >= 10 V |

**验证**
- `bom_check`（partial）· 脚本：读 ADC 数据手册对 REF 去耦电容的要求 — REF 脚电容值、介质、额定电压满足手册；没有多个不同容值并联在 REF 上
- `spice`（partial）· ngspice/TINA-TI — 基准滤波器 + 缓冲器 + CREF + ADC 动态电流源：转换开始时 REF 电压跌落 < 1 LSB，缓冲器稳定

**来源**
- [ADS8860 datasheet (SBAS569B)](https://www.ti.com/lit/ds/symlink/ads8860.pdf) — Texas Instruments, datasheet, §10.1.1 ADC Reference Driver; §12.1 Layout Guidelines
- [ADS1235 datasheet (SBAS824)](https://www.ti.com/lit/ds/symlink/ads1235.pdf) — Texas Instruments, datasheet, §8.3.4.1 External Reference

<a id="ANA-SCH-010"></a>
#### ANA-SCH-010 · 热电偶前端：参考结与冷端传感器同处等温块
`consider` · 可信度 `medium` · 适用: thermocouple, temperature_sensing

**规则** 热电偶接到 PCB 铜走线时，铜与热电偶金属在板上形成的两个额外结必须保持同温，并紧邻绝对温度传感器（等温块）；用电路或固件把等温块温度折算后从信号里扣除。

**依据** 热电偶电压对应的是测量结与参考结的温差，铜-热电偶结的温度不知道就无法算出测量结的绝对温度。

**验证**
- `review`（manual）· 布局评审 — 确认热电偶端子、冷端传感器和输入走线在一个紧凑区域内，周围没有功率器件；用热成像或温度计比较端子间温差
- `bench`（manual）· 热成像仪/多点温度计 — 满载运行 10 分钟，两个热电偶端子之间的温差应小于冷端补偿误差预算对应的温度

**来源**
- [AN684 Single Supply Temperature Sensing with Thermocouples](https://ww1.microchip.com/downloads/en/appnotes/00684a.pdf) — Microchip, app_note, Thermocouple signal conditioning path; isothermal block

<a id="ANA-SCH-012"></a>
#### ANA-SCH-012 · 模拟电源与数字电源之间加滤波
`consider` · 可信度 `high` · 适用: mixed_signal, adc_frontend · 标签: cat-feeder

**规则** 混合信号板上，模拟电源和数字电源用 RC 或低 Q 铁氧体磁珠隔开，数字电源入口先接数字区，再经滤波或稳压给模拟区供电；转换器的数字供电脚在本地放去耦电容，让数字瞬态电流在本地小回路里流动。

**依据** 数字瞬态电流如果经模拟电源或模拟地返回，会叠加到敏感信号上；本地去耦把返回电流限制在小环路里。

**验证**
- `review`（manual）· 原理图评审 — 检查模拟电源节点（INA199 的 V+、ADC/HX711 的 AVDD、基准）是否经 RC/磁珠与 ESP32 的 3V3 隔开，或有足够的去耦；每个转换器的数字电源脚有本地电容
- `bench`（manual）· 示波器：交流耦合，20 MHz 带宽限制 — 在 Wi-Fi 发射突发时测模拟电源节点的纹波，与未开 Wi-Fi 时比较，增量应小于该节点的电源抑制预算

**来源**
- [Grounding in mixed-signal systems demystified, Part 1 (SLYT499)](https://www.ti.com/lit/an/slyt499/slyt499.pdf) — Texas Instruments, app_note, Figure 2: RC filter or ferrite bead between analog and digital supplies
- [Grounding in mixed-signal systems demystified, Part 2 (SLYT512)](https://www.ti.com/lit/an/slyt512/slyt512.pdf) — Texas Instruments, app_note, Multiple converters on a single PCB: power enters digital partition first

## 网表与约束（netlist）

<a id="ANA-NET-001"></a>
#### ANA-NET-001 · 分流电阻的 sense 抽头用独立网络
`must` · 可信度 `high` · 适用: current_sense, shunt · 标签: cat-feeder

**规则** 分流电阻到电流检测放大器输入的两条 sense 线必须是独立网络（如 CS_P、CS_N），只连接分流电阻的 sense 焊盘、放大器输入引脚和必要的滤波元件；不得与大电流的源极/地/电机网络在其他位置相连。

**依据** sense 线一旦在别处与载流网络短接，大电流就会流过它的走线电阻，产生本该由开尔文连接避免的误差；独立网络也是后续 DRC 约束它的前提。

**验证**
- `netlist_diff`（full）· Python 读网表（KiCad netlist/pcb） — 对网络 CS_P/CS_N 列出所有焊盘：必须只有 {shunt sense pad, amp IN+/IN-, 滤波 R/C 的焊盘}，不含功率网络的焊盘；原理图与 PCB 的网表一致
- `drc`（partial）· KiCad DRC + 自定义规则 (.kicad_dru) — 为 CS_P/CS_N 设网络类，限制走线宽度不小于工艺下限、间距大于与功率网络的最小间距

**来源**
- [INA199 datasheet (SBOS469H)](https://www.ti.com/lit/ds/symlink/ina199.pdf) — Texas Instruments, datasheet, §10.1 Layout Guidelines
- [Shunt Resistor Layout Considerations (TI Precision Labs - Current Sense Amplifiers)](https://www.ti.com/content/dam/videos/external-videos/en-us/4/3816841626001/6076326896001.mp4/subassets/current-sense-amplifiers-shunt-resistor-layout-presentation-quiz.pdf) — Texas Instruments, vendor_guide, Rule 2 - use Kelvin connections

## 叠层与规则（stackup）

<a id="ANA-STK-001"></a>
#### ANA-STK-001 · 给模拟信号层配一层完整的地
`consider` · 可信度 `medium` · 适用: precision_adc, mixed_signal · 标签: cat-feeder

**规则** 要求高精度的模拟电路（16 位以上或 μV 级信号）尽量用 4 层板，把整层作为不被信号走线打断的地平面，关键元件放顶层并用短过孔接到该地；2 层板做不到时，底层尽量作为连续地，信号走线仅在必要时占用，空白处铺地。

**依据** 完整的地平面为信号提供最低电感的返回路径，并降低对外界干扰的敏感度；2 层板的地被信号割裂得越多，返回路径越长。

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 统计底层（或地层）上非 GND 网络走线的总长度/面积和对模拟区地铜的割裂；输出地铜在模拟区下方的连续覆盖率
- `review`（manual）· 布局评审 — 确认模拟元件下方的地铜没有槽、没有信号线穿过

**来源分歧** ADS8860 建议至少 4 层，ADS1235 也说专用地层，但同时承认受设备限制时不一定可行。示例板（猫咪喂食器）是 2 层、测量精度要求不高（ESP32-C3 ADC 本身误差 ±10 到 ±35 mV），取舍是在 2 层上做到连续底层地并把电机回流路径单独处理（见 ANA-PLN-003）。

**来源**
- [ADS8860 datasheet (SBAS569B)](https://www.ti.com/lit/ds/symlink/ads8860.pdf) — Texas Instruments, datasheet, §12.1 Layout Guidelines (at least four layers recommended)
- [ADS1235 datasheet (SBAS824)](https://www.ti.com/lit/ds/symlink/ads1235.pdf) — Texas Instruments, datasheet, §11.1 Layout Guidelines (dedicate an entire layer to ground)
- [ADS1113/4/5 datasheet (SBAS444E)](https://www.ti.com/lit/ds/symlink/ads1115.pdf) — Texas Instruments, datasheet, §11.1 (fill void areas with ground)

## 分区规划（floorplan）

<a id="ANA-FLR-001"></a>
#### ANA-FLR-001 · 把模拟区与数字/射频/开关区分开
`should` · 可信度 `high` · 适用: mixed_signal, adc_frontend · 标签: cat-feeder

**规则** 板子分成模拟区和数字区：ADC、放大器、基准、模拟多路开关等放在模拟区；MCU、CPLD/FPGA、射频收发器（含 Wi-Fi 模组及其天线）、USB 收发器、开关稳压器放在数字区。转换器跨在两区的分界上，模拟信号只在模拟区走线，数字信号只在数字区走线（所有层）。

**依据** 数字部分的快速电流边沿和射频能量是对低电平模拟信号最主要的干扰源；只要走线纪律保持，数字回流电流会留在数字区地平面中，不会流进模拟区。

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 给元件打标签（analog/digital/RF），在板上画出两个分区多边形；统计：模拟标签元件是否全部在模拟区内、数字网络走线是否进入模拟区、模拟网络走线是否进入数字区，越界即不通过（跨界的转换器引脚除外）
- `review`（manual）· 布局评审 — 检查转换器朝向：数字引脚朝数字区，模拟引脚朝模拟区

**来源**
- [ADS1113/4/5 datasheet (SBAS444E)](https://www.ti.com/lit/ds/symlink/ads1115.pdf) — Texas Instruments, datasheet, §11.1 Layout Guidelines, Figure 11-1
- [Partitioning and Layout of a Mixed-Signal PCB (Henry Ott)](https://www.eetimes.com/partitioning-and-layout-of-a-mixed-signal-pcb-3/) — EE Times / Printed Circuit Design, paper
- [Grounding in mixed-signal systems demystified, Part 2 (SLYT512)](https://www.ti.com/lit/an/slyt512/slyt512.pdf) — Texas Instruments, app_note, Figure 4b partitioned plane

<a id="ANA-FLR-002"></a>
#### ANA-FLR-002 · 精密元件远离热源和板边气流
`should` · 可信度 `high` · 适用: precision_analog, thermocouple, matched_resistors · 标签: cat-feeder

**规则** 放大器输入电阻、匹配电阻对、基准、热电偶端子和冷端传感器放在远离稳压器、MOSFET、分流电阻等发热元件的位置，也远离板边和气流；热源产生的温度梯度要沿着这些元件的等温线方向，而不是穿过它们。

**依据** PCB 上元件焊点、铜走线与焊料形成许多塞贝克结，温度梯度会在其两端产生热电势：AN1258 的例子中 10 degC/inch 的梯度在一个 1206 电阻上产生约 38 uV。零漂运放的失调只有几 uV，这种热电势可以与之相当。

| 参数 | 判据 | 备注 |
|---|---|---|
| `example_gradient` | == 10 degC/inch | AN1258 的示例：梯度 10 degC/inch，1206 电阻两端约 -38 uV；PCB 结的塞贝克系数通常低于 ±100 uV/degC |
| `thermoelectric_voltage_per_degc` | >= 0.1 uV/degC | OPA333 手册：结两侧温度不同时的热电势可达 0.1 uV/degC 或更高，取决于材料 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 给精密元件和热源元件打标签；计算两类元件焊盘中心的最小距离、精密元件到板边的距离，距离阈值由热仿真给出（出处无固定数值）
- `thermal_sim`（partial）· 热阻网络估算或稳态热仿真 — 满载下读精密元件两端的温度差，乘以热电势系数 (<= 100 uV/degC 的上限) 对照失调预算
- `bench`（manual）· 热成像仪 + 万用表 — 满载运行直到温度稳定，记录精密元件区域温度梯度和输出漂移

**来源**
- [AN1258 Op Amp Precision Design: PCB Layout Techniques](https://ww1.microchip.com/downloads/en/appnotes/01258b.pdf) — Microchip, app_note, Thermocouple Junction Behavior; Preventing Large Thermoelectric Voltages
- [OPA333/OPA2333 datasheet (SBOS351E)](https://www.ti.com/lit/ds/symlink/opa333.pdf) — Texas Instruments, datasheet, §7.3 Feature Description

## 器件布局（placement）

<a id="ANA-PLC-001"></a>
#### ANA-PLC-001 · 分流电阻紧贴电流检测放大器
`should` · 可信度 `high` · 适用: current_sense, shunt · 标签: cat-feeder

**规则** 分流电阻放在电流检测放大器旁边，使两条 sense 走线尽量短；两条走线长度和位置对称。

**依据** sense 线上的电压很小，长走线易受电磁干扰；走线的寄生电阻和电容也会增加误差，两条走线电阻不一致时会因输入偏置电流产生失调。

| 参数 | 判据 | 备注 |
|---|---|---|
| `sense_trace_length` | minimize | TI 原文只要求 close / short，没有给数值；可用实测或仿真定出本板可接受的最大长度 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 测 CS_P、CS_N 两个网络的走线总长度，要求都不超过设计设定的上限，且两者长度差不超过设定的失配上限

**来源**
- [Shunt Resistor Layout Considerations (TI Precision Labs - Current Sense Amplifiers)](https://www.ti.com/content/dam/videos/external-videos/en-us/4/3816841626001/6076326896001.mp4/subassets/current-sense-amplifiers-shunt-resistor-layout-presentation-quiz.pdf) — Texas Instruments, vendor_guide, Rule 1 - be close to the current sense amplifier
- [INA199 datasheet (SBOS469H)](https://www.ti.com/lit/ds/symlink/ina199.pdf) — Texas Instruments, datasheet, §7.3.1 Basic Connections

<a id="ANA-PLC-002"></a>
#### ANA-PLC-002 · 电流检测放大器的旁路电容贴脚且不打孔
`should` · 可信度 `high` · 适用: ina199, current_sense · 标签: cat-feeder

**规则** 0.1 uF 旁路电容（INA199 §10.1 推荐值）放在放大器 V+ 与 GND 引脚旁边，同一层，二者之间不放过孔；噪声大或高阻抗电源可以再加去耦。

**依据** INA199 的电源旁路电容是稳定性要求；带过孔的连接增加电感，削弱去耦。

| 参数 | 判据 | 备注 |
|---|---|---|
| `bypass_capacitance` | == 0.1 uF | INA199 §10.1 文字明确写“TI recommends ... 0.1 uF”，Figure 7-1、8-1、8-3 的 CBYPASS 也是 0.1 uF。0.01–0.1 uF 这个范围在手册里出现两处：§7.4.5 的输入瞬态保护滤波电容文字，以及 Figure 7-4 与 Figure 7-7 里 V+ 引脚旁路电容的标注（所以它不只是输入滤波电容，也被标作电源旁路的可用范围）。本条取 §10.1 的明文推荐值 0.1 uF（二次审计更正：上一版更正称该范围“不是电源旁路电容”，与 Figure 7-4/7-7 不符） |
| `decap_to_pin_distance` | minimize | 原文是 as close as possible，没有数值 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 找出 V+ 引脚网络上最近的电容，量焊盘中心距，并检查电容焊盘到引脚焊盘的路径上是否有过孔；距离阈值按本板设定（建议 <= 3 mm）

**来源**
- [INA199 datasheet (SBOS469H)](https://www.ti.com/lit/ds/symlink/ina199.pdf) — Texas Instruments, datasheet, §7.3.1; §10.1
- [ADS1113/4/5 datasheet (SBAS444E)](https://www.ti.com/lit/ds/symlink/ads1115.pdf) — Texas Instruments, datasheet, §11.1 (no vias between bypass capacitors and the device)

<a id="ANA-PLC-003"></a>
#### ANA-PLC-003 · ADC 基准与电源电容贴近引脚的距离上限
`should` · 可信度 `high` · 适用: sar_adc, voltage_reference

**规则** SAR ADC 的 REF 去耦电容放在距引脚 0.1 inch（2.54 mm）以内，用多个接地过孔；AVDD/DVDD 去耦电容放在 0.2 inch（5.08 mm）以内；引脚到电容之间不放过孔；输入飞轮 RC 紧挨输入引脚。

**依据** 转换期间 REF 脚和电源脚有动态电流，电容与引脚之间的电感越小去耦越有效：ADS8860 的目标是 REF 回路电感 < 2 nH、电源回路 < 5 nH。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ref_cap_to_pin_distance` | <= 2.54 mm | ADS8860 §12.1：0.1 inch，对应电感 < 2 nH，使用 20 mil 走线和多个 15 mil 接地过孔 |
| `supply_cap_to_pin_distance` | <= 5.08 mm | ADS8860 §12.1：0.2 inch，对应电感 < 5 nH，20 mil 走线和 15 mil 接地过孔 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 对 REF、AVDD、DVDD 引脚找去耦电容，测焊盘中心距，分别 <= 2.54 mm、<= 5.08 mm；检查走线路径上无过孔

**来源**
- [ADS8860 datasheet (SBAS569B)](https://www.ti.com/lit/ds/symlink/ads8860.pdf) — Texas Instruments, datasheet, §12.1 Layout Guidelines

<a id="ANA-PLC-004"></a>
#### ANA-PLC-004 · 匹配电阻同向、紧邻，沿等温线排布
`consider` · 可信度 `high` · 适用: matched_resistors, op_amp, difference_amplifier

**规则** 决定增益或比例精度的匹配电阻（反馈/增益电阻、差分放大器电阻对）选相同封装，同方向、相邻放置，并让电流方向沿着温度等值线（与热源方向垂直）；不能保证时，用两个串联或并联且对齐的电阻代替单个电阻，使热电势相互抵消。

**依据** 电阻两端焊点和端帽金属不同，温度梯度会在电阻两端产生热电势；同向对齐的两颗电阻产生的热电势极性相反，可以抵消。

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 对标记为 matched 的电阻对：封装一致、旋转角相同、中心距 <= 设定上限、到热源的距离相等（差 <= 设定上限）
- `bench`（manual）· 热成像仪 + 万用表 — 按 AN1258 的做法，故意制造温度梯度（用热源元件），测输出变化，评价热电势残余

**来源**
- [AN1258 Op Amp Precision Design: PCB Layout Techniques](https://ww1.microchip.com/downloads/en/appnotes/01258b.pdf) — Microchip, app_note, Following Contour Lines; Cancellation of Thermoelectric Voltages

## 布线（routing）

<a id="ANA-RTE-001"></a>
#### ANA-RTE-001 · 分流电阻到放大器必须用开尔文（四线）走线
`must` · 可信度 `high` · 适用: current_sense, shunt, kelvin · 标签: cat-feeder

**规则** 放大器输入引脚到分流电阻的两条走线必须直接接在分流电阻的 sense 焊盘上，大电流只经过电阻本体和粗的负载走线；任何一条 sense 线不得借道载流走线，否则两个输入引脚之间会多出一段载流铜阻。

**依据** 分流电阻阻值很小，任何额外的载流铜阻都会直接叠加到测量电压上。TI 示例：1 oz、0.25 mm 长、0.6 mm 宽的铜走线约 193 uOhm，在 8 mohm 分流、10 A 时多出 1.93 mV，相对 80 mV 约 2.4% 的误差。

| 参数 | 判据 | 备注 |
|---|---|---|
| `example_trace_resistance` | == 193 uohm | TI 示例：1 oz 铜，0.25 mm 长，0.6 mm 宽 |
| `example_error` | == 2.4 % | 8 mohm 分流电阻、10 A、多出 1.93 mV（80 mV 的 2.4%） |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 读 CS_P/CS_N 网络的所有走线与过孔，确认它们在 PCB 上只连接到分流电阻的 sense 焊盘、放大器输入引脚和滤波元件的焊盘；并检查没有铜皮（灌铜）把 sense 焊盘与功率网络连起来
- `bench`（manual）· 已知直流电流源 + 四线万用表 — 用已知电流（如 1 A）测放大器输出，与 I*R_shunt*G 的差在增益误差预算内；差异超过预算要检查 sense 线是否借道载流铜

**来源**
- [Shunt Resistor Layout Considerations (TI Precision Labs - Current Sense Amplifiers)](https://www.ti.com/content/dam/videos/external-videos/en-us/4/3816841626001/6076326896001.mp4/subassets/current-sense-amplifiers-shunt-resistor-layout-presentation-quiz.pdf) — Texas Instruments, vendor_guide, Rule 2 - Kelvin connections, bad layout example
- [INA199 datasheet (SBOS469H)](https://www.ti.com/lit/ds/symlink/ina199.pdf) — Texas Instruments, datasheet, §10.1 Layout Guidelines
- [INA240 datasheet (SBOS662C)](https://www.ti.com/lit/ds/symlink/ina240.pdf) — Texas Instruments, datasheet, §9.3.2, Figure 9-7

<a id="ANA-RTE-002"></a>
#### ANA-RTE-002 · 两条 sense 线等长、等宽、同层并排
`should` · 可信度 `high` · 适用: differential_input, current_sense · 标签: cat-feeder

**规则** 两条差分输入走线（sense 线）用相同的长度、宽度和层，并排走，保持短，减小两线围成的环路面积；差分输入对要在测量源方向上保持匹配。

**依据** 走线电阻不一致，加上输入偏置电流，会产生失调；环路面积大则电感和拾取的干扰也大；并排走使共模干扰同时耦合到两条线，由放大器的 CMRR 抑制。

| 参数 | 判据 | 备注 |
|---|---|---|
| `sense_trace_length_mismatch` | minimize | 出处只要求 matched / avoid unbalanced，没有数值；可按 I_bias*delta_R 小于失调预算份额反推 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 对 CS_P 与 CS_N 网络：比较总长度（差 <= 设定值）、最小线宽（相同）、层（相同）、两线之间平均间距（<= 设定值），输出环路面积

**来源**
- [Shunt Resistor Layout Considerations (TI Precision Labs - Current Sense Amplifiers)](https://www.ti.com/content/dam/videos/external-videos/en-us/4/3816841626001/6076326896001.mp4/subassets/current-sense-amplifiers-shunt-resistor-layout-presentation-quiz.pdf) — Texas Instruments, vendor_guide, Rule 1 - avoid unbalanced traces
- [ADS1113/4/5 datasheet (SBAS444E)](https://www.ti.com/lit/ds/symlink/ads1115.pdf) — Texas Instruments, datasheet, §11.1 (differential inputs must be matched; reduce loop area)

<a id="ANA-RTE-003"></a>
#### ANA-RTE-003 · 模拟输入走线远离开关节点和数字信号
`should` · 可信度 `high` · 适用: adc_frontend, mixed_signal, current_sense · 标签: cat-feeder

**规则** 模拟输入、基准和滤波元件的走线不要与数字线（SPI/I2C/时钟/PWM 栅极）和开关节点（MOSFET 漏极、续流二极管、电机端子）平行相邻，也不要从其下方穿过；数字线的走线保持在数字区。

**依据** 数字边沿通过电容和互感耦合到高阻抗或小信号模拟线上，转换器的噪声性能会下降；ADC 的 CAP 脚、基准脚尤其敏感。

| 参数 | 判据 | 备注 |
|---|---|---|
| `min_distance_analog_to_digital` | maximize | 出处只要求 away / avoid，没有数值；本板可按线宽倍数设定并用 DRC 自定义规则强制 |

**验证**
- `drc`（full）· KiCad DRC 自定义规则 (.kicad_dru) — 为模拟网络类与数字/开关网络类设定更大的间距规则；DRC 不得有该规则的违例
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 对每条模拟网络走线，找到所有数字网络走线与它的平行段长度和最小间距；以及数字走线是否位于模拟元件焊盘的正下方（相邻层）

**来源**
- [ADS1235 datasheet (SBAS824)](https://www.ti.com/lit/ds/symlink/ads1235.pdf) — Texas Instruments, datasheet, §11.1 Layout Guidelines
- [ADS8860 datasheet (SBAS569B)](https://www.ti.com/lit/ds/symlink/ads8860.pdf) — Texas Instruments, datasheet, §12.1 (avoid crossing digital lines with the analog signal path)
- [ADS1113/4/5 datasheet (SBAS444E)](https://www.ti.com/lit/ds/symlink/ads1115.pdf) — Texas Instruments, datasheet, §11.1 (route digital lines away from analog lines)

<a id="ANA-RTE-005"></a>
#### ANA-RTE-005 · 敏感模拟线下方保持连续的返回平面
`should` · 可信度 `high` · 适用: analog, mixed_signal · 标签: cat-feeder

**规则** 敏感模拟信号走线下方紧邻的地平面不能有槽或分割，其他信号不要把返回电流挤到别处；必要时用的缝合过孔和过孔反焊盘不得阻断返回路径。

**依据** 高频电流沿电感最小的路径返回，也就是正下方；地被割开后返回路径变长，辐射和串扰增加，低电平模拟电流也更容易被干扰。

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 对每条模拟信号走线，沿走线取样，检查正下方（相邻参考层）是否有地铜覆盖，列出未覆盖段及其长度

**来源**
- [Grounding in mixed-signal systems demystified, Part 1 (SLYT499)](https://www.ti.com/lit/an/slyt499/slyt499.pdf) — Texas Instruments, app_note, Figures 4-5: distribution of return current
- [ADS1113/4/5 datasheet (SBAS444E)](https://www.ti.com/lit/ds/symlink/ads1115.pdf) — Texas Instruments, datasheet, §11.1 (provide good ground return paths)

<a id="ANA-RTE-004"></a>
#### ANA-RTE-004 · 高阻抗节点用保护环，且不要覆盖阻焊
`consider` · 可信度 `high` · 适用: high_impedance, photodiode, electrochemical_sensor

**规则** 对源阻抗很高、偏置电流很小的节点（如皮安级光电二极管、电化学传感器、高阻分压），用接在同电位低阻抗点上的保护环围住该节点和与它相连的所有顶层铜，保护环上不盖阻焊，两面板的两层都要做；通孔、飞线连接的高阻节点同样要围。不需要时（源阻抗低）不要多此一举。保护环要配合工艺：焊接后用异丙醇清洗残留并吹干，必要时涂覆阻湿涂层。

**依据** 表面污染（湿气、助焊剂残留、灰尘）让相邻不同电位的铜之间形成漏电通路：AN1258 给出的典型寄生电阻在低湿度洁净时约 1000 Gohm，高湿度污染时约 1 Gohm。保护环与敏感节点同电位，漏电电流流进保护环而不是进入敏感节点，可降低约 1000 倍。

| 参数 | 判据 | 备注 |
|---|---|---|
| `surface_leakage_resistance_clean` | == 1000 Gohm | AN1258 典型寄生电阻，低湿度、洁净 |
| `surface_leakage_resistance_humid` | == 1 Gohm | AN1258 典型寄生电阻，高湿度、污染 |
| `leakage_reduction_with_guard` | == 1000 ratio | AN1258 在单位增益缓冲器、同相放大器示例里给出的典型降低倍数 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 对标记为 high_Z 的网络，检查其顶层/底层焊盘与走线周围是否有保护环网络环绕，保护环的阻焊开窗存在；保护环网络由低阻抗源驱动（网表检查）
- `spice`（partial）· ngspice — 在高阻节点到相邻网络之间加 1 Gohm 到 1000 Gohm 的并联电阻，比较有无保护环时的输出误差
- `bench`（manual）· 皮安计/高阻表 — 清洗前后与高湿度条件下，测高阻节点对邻近网络的漏电流；AN1258 指出标准清洗工序不一定够，需额外用异丙醇清除某些清洗剂的残留

**来源分歧** TI E2E 的回复称板子干净并能长期保持干净时可能不需要保护环；AN1258 与 AN-241 则把保护环作为降低表面漏电的标准做法。取舍：对 pA 级节点做保护环并配合清洗/涂覆；对示例板（猫咪喂食器）的节点（INA199 输出、HX711 输入的低阻抗节点）没有必要。

**来源**
- [AN1258 Op Amp Precision Design: PCB Layout Techniques](https://ww1.microchip.com/downloads/en/appnotes/01258b.pdf) — Microchip, app_note, PCB Surface Leakage; Guard Rings; PCB Bulk Leakage
- [AN-241 Working with High Impedance Op Amps](https://www.ti.com/lit/an/snoa664/snoa664.pdf) — Texas Instruments (National Semiconductor), app_note, Electrical Guarding

## 平面与铺铜（plane_pour）

<a id="ANA-PLN-001"></a>
#### ANA-PLN-001 · 整块地平面 + 分区走线，优先于分割 AGND/DGND
`should` · 可信度 `high` · 适用: mixed_signal, adc_frontend · 标签: cat-feeder

**规则** 混合信号板默认用一块完整的地平面，按模拟/数字分区并严格约束走线（模拟信号只在模拟区、数字信号只在数字区，所有层）；只有在法规/隔离要求或已无法保证走线纪律时才分割地，分割时只在转换器下方一点相连并让所有跨越信号走在该桥上，且不要在多个位置连接两块地。

**依据** Ott 与 TI 指出：返回电流沿信号线正下方返回，数字电流不会进入分区的模拟区地；分割的地在走线跨越时有大环路和偶极子天线问题。

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 检查：地网络是否只有一个连通铜区域；分区边界上是否有信号线越界；若有分割地，检查所有跨越分割的信号线是否都经过唯一的桥
- `bench`（manual）· Ott 的验证方法：板上留跳线把分割地以约 1/2 inch 间隔连起来 — 分别在分割和连通两种状态下测噪声底和 EMC 预扫，结果取优

**来源分歧** ADI 的 Zumbahlen 文章和 MT-031 建议（单板单转换器时）把地分成模拟与数字，在转换器的 AGND/DGND 引脚处连成一点（星形地）；TI SLYT512 和 Ott 则优先用一块地分区走线，认为分割只有在转换器很多时会形成地环路。ADS1235 手册两边都兼顾：专用地层，必须分割时只在 ADC 处连接。取舍：示例板（猫咪喂食器）是 2 层板、单个内置 ADC，选一块地分区的做法，因为分割的 2 层板更难保证每个信号都有返回路径；ADI 两篇我只通过检索摘要看到，没有读到原文，所以 ADI 一方的细节以原文为准。

**来源**
- [Partitioning and Layout of a Mixed-Signal PCB (Henry Ott)](https://www.eetimes.com/partitioning-and-layout-of-a-mixed-signal-pcb-3/) — EE Times / Printed Circuit Design, paper
- [Grounding in mixed-signal systems demystified, Part 2 (SLYT512)](https://www.ti.com/lit/an/slyt512/slyt512.pdf) — Texas Instruments, app_note
- [ADS1235 datasheet (SBAS824)](https://www.ti.com/lit/ds/symlink/ads1235.pdf) — Texas Instruments, datasheet, §11.1 (if separation is necessary, join at the ADC; do not connect at multiple locations)
- [MT-031 Grounding Data Converters and Solving the Mystery of AGND and DGND](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf) — Analog Devices, app_note
- [Staying Well Grounded (Hank Zumbahlen)](https://www.analog.com/en/resources/analog-dialogue/articles/staying-well-grounded.html) — Analog Devices, paper

<a id="ANA-PLN-002"></a>
#### ANA-PLN-002 · 转换器的 AGND/DGND 引脚在器件下方相连
`should` · 可信度 `medium` · 适用: adc, dac, mixed_signal_ic

**规则** 带 AGND 和 DGND 两个引脚的转换器，数字电流小时当作模拟器件处理：两个引脚用最短引线接到同一块低阻抗的模拟地平面，数字电源脚在本地用电容去耦到地，使数字瞬态电流只在 VDig - 电容 - DGND 的小回路里流动；数字电流大时才把 DGND 接数字地，并准备跳线对比。

**依据** AGND/DGND 的名字描述的是芯片内部结构，不代表外部要分开；DGND 外部多一点阻抗，数字噪声就会经杂散电容更多地耦合到模拟电路。

**验证**
- `review`（partial）· 原理图与 PCB 评审 — 检查转换器的 AGND 和 DGND 焊盘是否通过过孔直接连到同一块地铜，没有串联磁珠或细走线（除非数据手册对高数字电流转换器另有要求）
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — AGND 焊盘与 DGND 焊盘之间的铜路径长度 <= 设定值；数字电源去耦电容的回路面积 <= 设定值

**来源分歧** TI SLYT499 对高数字电流的转换器（例如 Σ-Δ 的数字滤波器）给出另一种接法：AGND 脚接模拟地、DGND 脚接数字地，并用背靠背肖特基二极管把二者压差限制在 0.3 V 内。选哪种看转换器的数字电流大小和数据手册。MT-031 我只通过检索摘要看到，没读到原文，所以置信度为 medium。

**来源**
- [Grounding in mixed-signal systems demystified, Part 1 (SLYT499)](https://www.ti.com/lit/an/slyt499/slyt499.pdf) — Texas Instruments, app_note, Grounding data converters with low/high digital currents, Figures 2-3
- [MT-031 Grounding Data Converters and Solving the Mystery of AGND and DGND](https://www.analog.com/media/en/training-seminars/tutorials/MT-031.pdf) — Analog Devices, app_note

<a id="ANA-PLN-003"></a>
#### ANA-PLN-003 · 电机/大电流回路不穿过模拟地区
`consider` · 可信度 `medium` · 适用: current_sense, motor_driver, two_layer_board · 标签: cat-feeder

**规则** 电机和 MOSFET 的回流电流从分流电阻的地侧直接回到电源入口，不要穿过 INA199、HX711、ADC 的模拟参考地所在的铜区；放大器的 GND、ADC/HX711 的 AGND 取自同一个无大电流流过的安静地节点，与功率地只在一点相连（靠近分流电阻地侧焊盘或电源入口）。

**依据** 回流电流在地铜上产生 I*R 压降（例如 2 A 流过 10 mohm 的地铜就有 20 mV），ADC 以自己的地为参考，这个压降会直接叠加到读数上，大于 ESP32-C3 ADC 的 ±10 mV 误差。这是由物理量级推出的推理，不是原文的数值。

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 计算功率地回流路径（分流电阻地侧焊盘到电源入口）与模拟区多边形是否相交；估算两个参考点之间铜的直流电阻 R_gnd，乘以 Imax 对照 ADC 预算
- `spice`（partial）· ngspice — 在功率地回流路径上插入由铜面积算出的 R_gnd，仿真电机电流下 INA199 输出和 ADC 引脚相对 MCU 地的误差
- `bench`（manual）· 毫伏表或示波器 — 电机满载时，测分流电阻地侧焊盘与 ESP32 GND 焊盘之间的电压，应小于预算份额

**来源**
- [Selecting amplifiers for shunt-based current sensing in 3-phase motor drives (SLYT762)](https://www.ti.com/lit/pdf/slyt762) — Texas Instruments, app_note, Placement No. 2: GND bounce at low-side shunts
- [Grounding in mixed-signal systems demystified, Part 1 (SLYT499)](https://www.ti.com/lit/an/slyt499/slyt499.pdf) — Texas Instruments, app_note, digital currents outside the local loop must flow through the analog ground plane

## 出图与制造（manufacturing）

<a id="ANA-MFG-001"></a>
#### ANA-MFG-001 · 出厂/首次上电做零点与增益两点校准
`should` · 可信度 `high` · 适用: bridge_sensor, current_sense, hx711 · 标签: cat-feeder

**规则** 测量链的零点和增益误差在生产或首次上电时用已知输入校准：先在零输入（电机停、空秤）读偏移，再用已知量（标准砝码、已知电流）求增益，把系数保存在非易失存储里；校准点之外的线性度假设要在验证里确认。

**依据** 失调和增益误差是确定性的，校准比提高器件等级便宜；INA199 最大增益误差达 ±1.5%，HX711 称重传感器还有零点漂移和灵敏度偏差。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ina199_gain_error_max` | <= 1.5 % | INA199 版本 A/B，VSENSE = ±5 mV，-40 到 125 degC；版本 C 为 1% |

**验证**
- `bench`（partial）· 标准砝码 / 可编程直流电流源 / 固件 — 校准后在校准点之间的 ≥ 3 个点（如 25%、50%、75% 量程）上测量，误差落在预算内；记录零点和增益系数随温度的漂移
- `review`（manual）· 固件评审 — 校准流程是否分零点、增益两步；系数是否写入 NVS 并有校验；是否有恢复默认的路径

**来源**
- [A Basic Guide to Bridge Measurements (SBAA532A)](https://www.ti.com/lit/an/sbaa532a/sbaa532a.pdf) — Texas Instruments, app_note, §5.5 Calibration
- [INA199 datasheet (SBOS469H)](https://www.ti.com/lit/ds/symlink/ina199.pdf) — Texas Instruments, datasheet, §6.5 Gain error

## 签核验证（verification）

<a id="ANA-VER-003"></a>
#### ANA-VER-003 · 稳定性签核：环路增益 + 阶跃，覆盖角点条件
`must` · 可信度 `high` · 适用: op_amp, adc_driver, reference_buffer, current_sense · 标签: cat-feeder

**规则** 每个驱动电容负载或带反馈的运放/放大器级，在仿真中用环路增益（Aol 与 1/beta 的闭合速率、相位裕度）和小信号阶跃响应两种方式签核：相位裕度 >= 45 deg（目标 60 deg），闭合速率 20 dB/decade，覆盖最大电容、最差温度和元件容差。使用厂商提供的宏模型并确认其输出阻抗模型。

**依据** 电容负载造成的稳定性问题在台面上才发现代价高；阶跃响应的振铃与环路增益的裕度互为印证，只看一个可能漏掉问题。

| 参数 | 判据 | 备注 |
|---|---|---|
| `phase_margin_min` | >= 45 deg | 目标 60 deg 以获得较好的阻尼，见 ANA-ARC-006 |

**验证**
- `spice`（partial）· TINA-TI / ngspice：断环 AC 分析和 .tran 小信号阶跃 — 在最小/最大电容负载、-40 与 125 degC、RISO 容差 ±5% 的组合下，相位裕度 >= 45 deg 且阶跃响应无持续振铃
- `bench`（manual）· 示波器 + 方波发生器 — 实物上用小信号方波，观察输出振铃衰减次数与仿真对比

**来源**
- [Determine Optimal Isolation Resistance for Driving Capacitive Load (SBOA418)](https://www.ti.com/lit/pdf/sboa418) — Texas Instruments, app_note, §3 and §5: simulate with SPICE to verify; Figure 5-1 small-signal step response
- [ADS8860 datasheet (SBAS569B)](https://www.ti.com/lit/ds/symlink/ads8860.pdf) — Texas Instruments, datasheet, §10.1.2.2 (always verify stability and settling by SPICE)
- [Do-it-yourself: Three Ways to Stabilize Op Amp Capacitive Loads (SSZT999)](https://www.ti.com/lit/pdf/sszt999) — Texas Instruments, app_note

<a id="ANA-VER-005"></a>
#### ANA-VER-005 · 实测 HX711 的 PD_SCK 时序，别触发掉电
`must` · 可信度 `high` · 适用: hx711, firmware_interface · 标签: cat-feeder

**规则** 用逻辑分析仪在真实固件运行（含 Wi-Fi/BLE 活动）下抓 PD_SCK：读数期间每个高电平 ≤ 50 us、低电平 ≥ 0.2 us，脉冲数只能是 25、26 或 27，每个转换周期内不得有其他数目；PD_SCK 任何一次高电平持续超过 60 us 都会让 HX711 掉电并复位，复位后默认回到通道 A、增益 128。

**依据** 数据手册规定 PD_SCK 高电平保持超过 60 us 即进入掉电，ESP32 在 Wi-Fi 中断或任务调度下，如果读数期间被打断，会在读数中途让 SCK 停在高电平，导致数据错误或每次读数后都复位。

| 参数 | 判据 | 备注 |
|---|---|---|
| `pd_sck_high_time_max` | <= 50 us | T3，数据手册时序表的最大值 |
| `pd_sck_power_down_threshold` | > 60 us | PD_SCK 高电平超过 60 us 进入掉电；回到低电平后复位并回到通道 A 增益 128 |
| `pd_sck_pulses_per_conversion` | 25 … 27 pulses | 25 = 通道 A 增益 128，26 = 通道 B 增益 32，27 = 通道 A 增益 64 |

**验证**
- `bench`（partial）· 逻辑分析仪（≥ 8 MS/s）+ 固件跑 Wi-Fi 流量 — 抓 ≥ 1000 次读数，统计 PD_SCK 高电平最大宽度（要求 <= 50 us）和脉冲数；同时检查增益是否稳定（读数的建立时间没有周期性重启）
- `review`（manual）· 固件评审 — 读数的 24 个移位周期是否在关中断或临界区内完成，或用硬件外设（SPI/RMT）产生时序

**来源**
- [HX711 24-Bit Analog-to-Digital Converter (ADC) for Weigh Scales](https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf) — Avia Semiconductor, datasheet, Fig.2 timing and Table 3; Reset and Power-Down, Fig.3

<a id="ANA-VER-001"></a>
#### ANA-VER-001 · SPICE 做最坏情况 + Monte Carlo + 温度扫描对账
`should` · 可信度 `medium` · 适用: error_budget, op_amp, current_sense · 标签: cat-feeder

**规则** 把误差预算（ANA-ARC-001）里的每一项在 SPICE 里用实际容差建模：电阻容差与 TCR、放大器失调和偏置电流（带温度）、基准误差；跑最坏情况、Monte Carlo（高斯分布，3-sigma 对应容差）和 -40/25/85 degC 三个温度，仿真得到的总误差必须不超过预算。

**依据** 手算预算会漏掉元件间的相互作用（如输入串联电阻 + 偏置电流）；多数参数近似高斯分布，最坏情况过于悲观，RSS/Monte Carlo 给出统计上的合理范围。

| 参数 | 判据 | 备注 |
|---|---|---|
| `monte_carlo_runs` | >= 200 runs | 经验值，不是出处的数值；足以估计 3-sigma 的粗略范围，高良率要求时增加 |

**验证**
- `spice`（partial）· ngspice：用 .param + 随机函数（agauss/unif）或 .control 里的 repeat 循环；.temp / .options temp 做温度扫描 — N 次运行后，统计输出的均值和标准差，换算为满量程的百分比；同时用元件极限值跑一次最坏情况；两者都不超过预算
- `bom_check`（partial）· Python 脚本：与 SPICE 同参数的解析式 — 解析式的 RSS 结果与 Monte Carlo 的 1-sigma 偏差 < 20%，不一致时先查模型

**来源**
- [AN1177 Op Amp Precision Design: DC Errors](https://ww1.microchip.com/downloads/en/appnotes/01177a.pdf) — Microchip, app_note, Process and Environmental Variations: worst case vs RSS
- [Ngspice User's Manual](https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml) — ngspice, tool_doc, §18.5 Monte-Carlo Simulation; §18.2 random parameters; §13.6 Control Structures; §1.3.2 temperature

<a id="ANA-VER-002"></a>
#### ANA-VER-002 · SPICE 噪声分析：积分噪声与 LSB 对比
`should` · 可信度 `medium` · 适用: low_noise, adc_frontend, bridge_sensor

**规则** 用 SPICE 的 .noise 分析求输入参考噪声和输出噪声，对感兴趣的带宽积分得到 rms 噪声，与 ADC 的 1 LSB 或要求的有效分辨率比较；仿真前用 1 kohm 电阻在 25 degC 的热噪声（约 4 nV/rtHz，16e-18 V^2/Hz）核对仿真器输出单位。

**依据** 不同仿真器输出的是电压密度还是其平方，单位错一级会误判；电阻模型不含 1/f 噪声，运放宏模型的噪声参数必须正确，否则结果没有意义。

| 参数 | 判据 | 备注 |
|---|---|---|
| `reference_thermal_noise_1k_25c` | == 4 nV/rtHz | 1 kohm，25 degC；平方形式为 1.6e-17 V^2/Hz，用于核对仿真器输出单位 |

**验证**
- `spice`（partial）· ngspice：.noise V(out) Vin dec ... 后用 noise 绘图/积分 — 先用一个 1 kohm 电阻验证单位；然后对实际电路积分 fL 到 fH 的噪声（注意限带滤波器的等效噪声带宽 NPBW），结果 rms 值 <= 预算份额；用 effective resolution = log2(FSR/en_rms) 换算
- `bench`（manual）· 示波器或 ADC 数据采集：输入短路 — 把仿真噪声与 ANA-VER-004 的实测对比，差 > 2 倍时检查模型

**来源**
- [AN1228 Op Amp Precision Design: Random Noise](https://ww1.microchip.com/downloads/en/appnotes/01228a.pdf) — Microchip, app_note, Appendix B: Computer Aids (B.1 Noise Simulations)
- [Ngspice User's Manual](https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml) — ngspice, tool_doc, §1.2.7 Noise Analysis; §11.3.4 .NOISE
- [ADS1235 datasheet (SBAS824)](https://www.ti.com/lit/ds/symlink/ads1235.pdf) — Texas Instruments, datasheet, §7.1 Noise Performance, Eq. 1

<a id="ANA-VER-004"></a>
#### ANA-VER-004 · 输入短路噪声实测与有效分辨率
`should` · 可信度 `high` · 适用: adc, hx711, bridge_sensor, esp32c3_adc · 标签: cat-feeder

**规则** 把模拟输入接到被测系统的静态零点（ADC 输入短路，或传感器放在静止状态），以实际数据率采集至少几千个样本，算 rms 与峰峰值，按 effective resolution = log2(FSR/rms_noise) 与无闪烁分辨率 = log2(FSR/p-p noise) 求位数，与数据手册和预算对照。

**依据** 数据手册的 ADC 噪声通常就是输入短路下几千点或几秒数据的统计结果；短路测量把噪声来源限定在 ADC 和前端，便于逐段定位 PCB 带来的额外噪声。

| 参数 | 判据 | 备注 |
|---|---|---|
| `min_samples` | >= 1000 samples | SBAA532A 描述数据手册噪声表由几千个数据点或几秒数据统计而来；这里取 1000 作为下限的经验值，越多越好 |
| `hx711_noise_ref` | == 50 nV rms | HX711 增益 128、10 SPS 的数据手册噪声（折合到输入） |

**验证**
- `bench`（partial）· 固件采集 + Python 统计；对 HX711 把 INA+ 与 INA- 短接到共模电压 — 输入短路下采集 N >= 几千个样本（10 SPS 时约 10 分钟），算 rms 和 p-p；rms 不应超过数据手册噪声的约 2 倍，否则按 SBAA532A 的方法逐项排查：电源、地、数字耦合
- `bench`（partial）· 对 ESP32-C3 ADC：输入端经与实际电路相同的 RC 接到稳压的直流源 — 采集后分别算单次读数和 64 次平均读数的标准差，确认平均后的噪声小于预算；记录 Wi-Fi 开/关的差别

**来源**
- [A Basic Guide to Bridge Measurements (SBAA532A)](https://www.ti.com/lit/an/sbaa532a/sbaa532a.pdf) — Texas Instruments, app_note, §5.2.1 Noise in an ADC Data Sheet
- [ADS1235 datasheet (SBAS824)](https://www.ti.com/lit/ds/symlink/ads1235.pdf) — Texas Instruments, datasheet, §7.1 Noise Performance (effective and noise-free resolution)
- [HX711 24-Bit Analog-to-Digital Converter (ADC) for Weigh Scales](https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf) — Avia Semiconductor, datasheet, Table 2 input noise

