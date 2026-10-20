# 音频（audio）— 规则全文

垂直领域 · 43 条规则 · 由 `catalog/*.yaml` 生成，请改 YAML 不要改本文件。用 `grep -n "<规则ID>" rules.md` 定位单条，不要整份读。

环节分布：架构与选型 4，符号封装库 1，原理图 16，网表与约束 1，叠层与规则 1，分区规划 3，器件布局 3，布线 5，平面与铺铜 2，出图与制造 1，签核验证 6

## 架构与选型（architecture）

<a id="AUD-ARC-001"></a>
#### AUD-ARC-001 · 按功率、负载和损耗反推 Class-D 供电电压与限流
`should` · 可信度 `high` · 适用: class-d, speaker-amplifier, btl

**规则** 用目标无削波功率、扬声器阻抗、回路总串联电阻 R_T（负载 + 输出管 RDS(on) + 电感 DCR + 走线与电源内阻，按最高结温取值）和最大占空比 M_max 反推最低 PVCC： BTL 时 Vcc(min) = sqrt(2·P·R_T²/R_load)/M_max，标称电压再除以 (1 - 电源容差)；并要求芯片过流阈值 ≥ Vcc(min)·M_max/R_T。

**依据** Class-D 的输出摆幅受供电电压和占空比上限约束，实际无削波功率低于理想值；限流过低会在峰值处提前削波、抬高失真，供电不足则达不到 THD+N=10% 的标称功率。

| 参数 | 判据 | 备注 |
|---|---|---|
| `btl_unclipped_power` | qualitative | P = (Vcc·M_max)²/(2·R_T²)·R_load（EDN）；TPA3116D2 数据手册 Eq.2 写作 P = (R_L/(R_L+2·R_S)·V_P)²/(2·R_L)，R_S 含 RDS(on) 与滤波器电阻 |
| `power_10pct_thd_over_unclipped` | == 1.25 ratio | TPA3116D2 数据手册：POUT(10% THD) = 1.25 × POUT(unclipped)；核算无削波功率时不要拿 10% THD 功率当目标 |
| `supply_voltage_nominal` | qualitative | Vcc(nom) = Vcc(min)/(1 - 容差)。EDN 示例：50 W / 8 Ω、R_T = 8.3 Ω、M_max = 88%、±5% 容差，得 Vcc(min) = 33.3 V、标称 35.1 V；按 Eq.4 代入同一组数重算限流 ≥ 33.34×0.88/8.3 ≈ 3.53 A（EDN 原文印的是 3.72 A，与其自身输入不自洽，以公式为准；示例数字，不是通用阈值） |

**验证**
- `bom_check`（partial）· Python 小脚本或表格，读 BOM 与数据手册参数 — 输入目标功率、最小负载阻抗、RDS(on)@Tj_max、电感 DCR、电源最低电压与容差、器件 M_max，按上式算 Vcc(min) 与 I_limit(min)； 通过判据：实际最低 PVCC ≥ Vcc(min)，器件过流阈值 ≥ I_limit(min)。
- `bench`（manual）· 音频分析仪 + 可调电源 + 假负载 — 把 PVCC 调到设计最低值、负载取最小标称阻抗，扫 1 kHz 的 THD+N-功率曲线，确认目标功率出现在削波拐点之前

**来源**
- [Understanding Class-D amplifier power supply requirements](https://www.edn.com/understanding-class-d-amplifier-power-supply-requirements/) — EDN, blog, Eq.1-4 及 BTL 50 W 示例
- [TPA3116D2 / TPA3118D2 / TPA3130D2 datasheet (SLOS708G)](https://www.ti.com/lit/ds/symlink/tpa3116d2.pdf) — Texas Instruments, datasheet, §7.3.4 PLIMIT Operation, Eq.2
- [How to Choose a Class-D Audio Amplifier (SLOA290)](https://www.ti.com/lit/SLOA290) — Texas Instruments, vendor_guide, §2-§4

<a id="AUD-ARC-003"></a>
#### AUD-ARC-003 · 音频指标带测试条件立项（THD+N、SNR、PSRR）
`should` · 可信度 `high` · 适用: codec, preamp, speaker-amplifier

**规则** 立项时为 THD+N、SNR、动态范围、PSRR 各给出带条件的目标：测试频率、电平、增益、负载和测量带宽（默认 20 kHz 平坦、不加权）；功率指标要写明是 1% 还是 10% THD+N、峰值还是连续。

**依据** THD+N 把噪声也算进去，随带宽、电平和负载变化；不写条件的数字无法验证，也无法在器件之间比较。

| 参数 | 判据 | 备注 |
|---|---|---|
| `measurement_bandwidth` | 20 … 22 kHz | Rane：首选 20 kHz 或 22 kHz、平坦；80 kHz 可用于研发/产线暴露高频问题，必须随结果注明 |
| `spec_conditions` | qualitative | 至少写明：频率、电平、增益（前级写最大增益）、负载、带宽/加权、功率点（1% 或 10% THD+N） |

**验证**
- `review`（manual）· 需求文档评审 — 逐条检查每个音频指标是否带齐上述条件；没有条件的指标退回补写
- `bench`（partial）· 音频分析仪或声卡 — 按指标中写明的条件原样复测，结果与目标对比

**来源**
- [RaneNote 145: Audio Specifications](https://www.ranecommercial.com/legacy/note145.html) — Rane, vendor_guide
- [How to Choose a Class-D Audio Amplifier (SLOA290)](https://www.ti.com/lit/SLOA290) — Texas Instruments, vendor_guide, §2, §5

<a id="AUD-ARC-004"></a>
#### AUD-ARC-004 · Codec 的 MCLK 取 256×fs 常用频率，避开内部 PLL
`should` · 可信度 `high` · 适用: codec, i2s, mclk

**规则** 优先提供 256×fs 的主时钟（48 kHz 用 12.288 MHz，44.1 kHz 用 11.2896 MHz）以绕开 codec 内部 PLL；必须用 PLL 时严格按数据手册的 PLL 输入范围和最高内部时钟限制配置。

**依据** PLL 参数越界会让 codec 噪声增大甚至产生失真，使用 256×fs 时钟还能省电流。

| 参数 | 判据 | 备注 |
|---|---|---|
| `mclk_over_fs` | == 256 ratio | 12.288 MHz@48 kHz，11.2896 MHz@44.1 kHz（SLAA749） |
| `pll_clkin_over_p` | qualitative | TLV320AIC3254 示例：D=0 时 PLL_CLKIN/P 在 512 kHz-20 MHz，D≠0 时在 10-20 MHz，且 PLL_CLK 不超过器件上限；具体以所用 codec 手册为准 |

**验证**
- `bom_check`（partial）· 脚本：读晶振/时钟源频率与 codec 采样率表 — 计算 MCLK/fs，若 ≠ 256 则检查所选 PLL 分频系数满足手册范围与内部时钟上限
- `bench`（manual）· 音频分析仪 — PLL 开/关两种配置下测空载本底噪声与 THD+N，确认无劣化

**来源**
- [Common Noise Issues in Audio Codecs (SLAA749)](https://www.ti.com/lit/an/slaa749/slaa749.pdf) — Texas Instruments, app_note, §2.2

<a id="AUD-ARC-002"></a>
#### AUD-ARC-002 · 按功率、散热、续航和 EMI 预算选 Class-D 或线性功放
`consider` · 可信度 `medium` · 适用: class-d, class-ab, headphone-amplifier, speaker-amplifier

**规则** 功率较大、靠电池或散热受限时选 Class-D（峰值效率可达约 90%）；仅为耳机或线路级小功率、且对开关噪声敏感时可选线性（AB / DirectPath）放大器。选 Class-D 即同时规划输出滤波器、层数和 EMC 预算。

**依据** Class-D 把损耗从功率级转成约 10% 的热量和 PWM 载波辐射，在低输出功率时效率最差；线性放大器没有调制，不产生开关谐波但发热大。

| 参数 | 判据 | 备注 |
|---|---|---|
| `switching_frequency` | 200 … 1500 kHz | SLOA290：通常 200 kHz-1.5 MHz，个别车载器件到 2.1 MHz；频率越高对滤波器要求不同，也可能落入 AM 频段（540-1600 kHz） |
| `class_d_peak_efficiency` | qualitative | SLOA290：效率最高约 90%，但随输出功率下降，低功率时最差；以数据手册效率-功率曲线为准 |

**验证**
- `review`（manual）· 架构评审清单 — 列出目标功率、电池/散热预算、EMC 目标、是否有 AM/DAB 收音机共存要求，对照所选器件的效率曲线与待机电流判断
- `bench`（manual）· 功率计 + 假负载 — 在典型使用功率（而非满功率）下测整机输入功率与输出功率，算效率与待机电流

**来源**
- [How to Choose a Class-D Audio Amplifier (SLOA290)](https://www.ti.com/lit/SLOA290) — Texas Instruments, vendor_guide, §2, §6, §7
- [TPA6132A2 25-mW DirectPath stereo headphone amplifier (SLOS597A)](https://www.ti.com/lit/ds/slos597a/slos597a.pdf) — Texas Instruments, datasheet, §8.1

## 符号封装库（library）

<a id="AUD-LIB-001"></a>
#### AUD-LIB-001 · MEMS 话筒封装库带声孔与垫圈尺寸
`should` · 可信度 `high` · 适用: mems-microphone, bottom-port, top-port

**规则** 底部声孔（zero-height）MEMS 话筒的封装库里放一个非金属化（unplated）PCB 声孔，孔径取规格书给定范围；顶部声孔型号则在外壳/垫圈侧留声路，垫圈孔径比话筒声孔至少大 0.5 mm。

**依据** 声孔直径、镀铜和垫圈对位决定频响与是否漏声；孔内镀铜会让焊料爬入堵孔，垫圈孔过小则对位公差造成漏气和回声。

| 参数 | 判据 | 备注 |
|---|---|---|
| `pcb_acoustic_hole_diameter_mini_zero_height` | 0.4 … 0.9 mm | Knowles Mini/SPK/SPA/SPY 零高度型号推荐范围，声孔本身 0.25 mm；其他型号以规格书为准 |
| `pcb_acoustic_hole_diameter_ultra_mini_zero_height` | 0.3 … 0.6 mm | Knowles Ultra Mini 零高度 |
| `gasket_hole_oversize` | >= 0.5 mm | 垫圈孔径比话筒顶部声孔至少大 0.5 mm，用于吸收 x-y 公差 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 遍历话筒封装的钻孔，确认存在 NPTH（非金属化）声孔，孔径落在上述范围；声孔周围无其他铜或过孔占用
- `review`（manual）· 封装评审 — 对照所选话筒规格书的推荐焊盘与声孔尺寸，核对 3D/机械对位

**来源**
- [SiSonic Design Guide, AN16 Rev 3.0](https://media.digikey.com/pdf/data%20sheets/knowles%20acoustics%20pdfs/sisonic_design_guide.pdf) — Knowles, app_note, §3.2, Table 4

## 原理图（schematic）

<a id="AUD-SCH-014"></a>
#### AUD-SCH-014 · 自举电容按数据手册的容量、介质和耐压选
`must` · 可信度 `high` · 适用: class-d, h-bridge, bootstrap

**规则** 每个高边自举引脚（BSxx）跨接到对应输出（OUTxx）的陶瓷电容按数据手册选值：TPA3116D2 为 220 nF、X5R 或更好、额定 ≥16 V；该电容只连这两个节点。

**依据** 全 NMOS 桥的高边靠自举电容充当浮动电源维持栅源电压，容量或耐压不足会使高边无法可靠导通。

| 参数 | 判据 | 备注 |
|---|---|---|
| `bootstrap_capacitance` | == 220 nF | TPA3116D2；其他器件按各自手册 |
| `bootstrap_voltage_rating` | >= 16 V | §7.3.6 写 ≥16 V，§8.2.2.5 的设计示例用 25 V X5R |
| `bootstrap_dielectric` | qualitative | X5R 或更好 |

**验证**
- `erc`（full）· KiCad 网表脚本 — 对每个 BSPx/BSNx 引脚，检查网络上仅有一个电容，另一端接到同通道的 OUTxx；容量/介质/额定电压与手册一致
- `bom_check`（full）· BOM 检查 — 电容规格（C、介质、V）满足上述参数，并计入直流偏压降额

**来源**
- [TPA3116D2 / TPA3118D2 / TPA3130D2 datasheet (SLOS708G)](https://www.ti.com/lit/ds/symlink/tpa3116d2.pdf) — Texas Instruments, datasheet, §7.3.6, §8.2.2.5
- [PCB Layout Guidelines for TAS2xxx Series Class-D Non-boosted Audio Amplifier (SLAA902)](https://www.ti.com/lit/pdf/slaa902) — Texas Instruments, app_note, §2.6

<a id="AUD-SCH-001"></a>
#### AUD-SCH-001 · 信号通路电容用 C0G 或薄膜，慎用 X7R/X5R
`should` · 可信度 `high` · 适用: ac-coupling, active-filter, line-input, preamp

**规则** 音频信号通路上承受明显交流电压的耦合/滤波电容用 C0G(NP0) 或薄膜；容量大时用 SMT 薄膜，或用已保证正偏压的钽/电解。必须用 X7R/X5R 时加大容量和/或提高串联阻抗，把高通转折频率压到通带以下约两个十年。

**依据** 高 K 钛酸钡介质的介电常数随电场下降，信号电压使电容随之变化并调制电流，失真在 -3 dB 转折频率附近最大且随电平上升；C0G 在整个工作温度范围内容量变化小于 ±30 ppm（EDN），其滤波器实验中失真在测量底噪以下，没有这个现象。

| 参数 | 判据 | 备注 |
|---|---|---|
| `c0g_practical_max_capacitance` | <= 1 uF | TI：C0G/NP0 不易买到大于 1 µF 的值，大容量耦合需要薄膜或其他方案 |
| `hpf_corner_below_passband` | >= 2 decade | 仅当不得不用 MLCC 时的经验做法（电容大 100 倍）；TI 实测：4.7 µF X7R 0805 在 2.5 kΩ 输入时失真从约 400 Hz 起，峰值在约 13 Hz 的 -3 dB 点 |
| `polarized_cap_dc_bias` | qualitative | 钽/电解做耦合时必须保证正偏压；无偏压或反偏时失真显著变差 |

**验证**
- `bom_check`（partial）· 脚本：用网表识别信号通路网络上的电容 — 对串联在音频通路、或在有源滤波器反馈/接地支路上的电容，检查介质为 C0G/NP0/薄膜；报出 X5R/X7R/Y5V 及其容量与封装，由评审确认例外
- `bench`（manual）· 音频分析仪 — 1 Vrms 下扫 20 Hz-20 kHz 的 THD+N，再做 500 Hz 的电平扫描；失真随电平上升说明是无源器件（通常是电容）引入

**来源分歧** 部分论坛意见认为转折频率在个位数 Hz 时 X7R 的失真会被放大器自身失真淹没；TI 实测（1 Vrms、4.7 µF X7R）和 EDN 的滤波器实验都测到可辨失真， 因此默认避免。对成本敏感且信号电平很低的通路可降级为 consider，但应保留 THD+N 实测。

**来源**
- [Selecting Capacitors to Minimize Distortion in Audio Applications (SLYT796)](https://www.ti.com/lit/pdf/slyt796) — Texas Instruments, app_note
- [Signal distortion from high-K ceramic capacitors](https://www.edn.com/signal-distortion-from-high-k-ceramic-capacitors/) — EDN, blog
- [Single-Supply, Electret Microphone Pre-Amplifier Reference Design (TIDU765)](https://www.ti.com/lit/pdf/tidu765) — Texas Instruments, app_note, §3.1
- [AN1767 Solutions for Radio Frequency Electromagnetic Interference in Amplifier Circuits](http://ww1.microchip.com/downloads/en/appnotes/00001767a.pdf) — Microchip, app_note, External Filters

<a id="AUD-SCH-002"></a>
#### AUD-SCH-002 · 按实际输入阻抗和有效容量核算 AC 耦合转折频率
`should` · 可信度 `high` · 适用: ac-coupling, class-d, headphone-amplifier, codec

**规则** 转折频率 fc = 1/(2π·R_in·C_in)，R_in 取器件在所选增益下的真实输入阻抗（含 ±容差），C_in 取计入容差和直流偏压降额后的有效容量，并核对 fc 低于所需低频下限（如 20 Hz）。

**依据** 输入阻抗常随增益变化（TPA3116D2 在 20-36 dB 增益间为 60 kΩ-9 kΩ，且 ±20%），陶瓷电容在偏压下容量大幅下降，按标称值算会让低频提前衰减。

| 参数 | 判据 | 备注 |
|---|---|---|
| `hpf_corner_frequency` | <= 20 Hz | 以产品低频下限为准；示例：TPA6132A2 +6 dB 增益时 R_in = 13.2 kΩ，20 Hz 需 C ≥ 0.6 µF，取 0.68 µF X5R；TIDU765 的 R1 = 13.7 kΩ、5 Hz 取 2.2 µF |
| `input_resistance_tolerance` | qualitative | TPA3116D2 输入电阻公差 ±20%，最小值按 ≥ 7.2 kΩ 计算；用最坏情况核算 fc |

**验证**
- `spice`（partial）· ngspice：.ac dec 20 1 100k — 用 R_in 的最大/最小值和电容容差/偏压降额后的有效容量各跑一次，读 -3 dB 点，要求最坏情况仍低于所需低频下限
- `bom_check`（partial）· 脚本：由 BOM 取电容值、封装、额定电压，按厂家 C-V 曲线降额 — 有效容量 = 标称值 ×(1 - 容差) × 偏压降额，代入 fc 公式，与要求对比

**来源**
- [TPA6132A2 25-mW DirectPath stereo headphone amplifier (SLOS597A)](https://www.ti.com/lit/ds/slos597a/slos597a.pdf) — Texas Instruments, datasheet, §9.2.1.2.1
- [TPA3116D2 / TPA3118D2 / TPA3130D2 datasheet (SLOS708G)](https://www.ti.com/lit/ds/symlink/tpa3116d2.pdf) — Texas Instruments, datasheet, §7.3.2
- [Power supply decoupling and audio signal filtering for the Class-D audio power amplifier (SLYT199)](https://www.ti.com/lit/pdf/slyt199) — Texas Instruments, app_note, Input filter, Eq.5

<a id="AUD-SCH-003"></a>
#### AUD-SCH-003 · 运放驱动容性负载时加隔离电阻并留相位裕度
`should` · 可信度 `high` · 适用: opamp, line-output, headphone-amplifier, cable-load

**规则** 运放输出直接带线缆、大滤波电容或参考电容时，在输出与负载电容之间串联隔离电阻 R_ISO（或做环内 R + Cf 补偿），阻值按数据手册的开环输出阻抗 R_O、GBW 和 C_load 估算，并用 SPICE 确认环路相位裕度 ≥ 45°。

**依据** 输出电容与运放开环输出电阻形成额外极点，使环路相位逼近 180° 而振荡；R_ISO 把输出与反馈节点隔开。音频输出需要低输出阻抗时，环内补偿比环外电阻更合适。

| 参数 | 判据 | 备注 |
|---|---|---|
| `phase_margin` | >= 45 deg | TI 以 45° 为常用下限，稳定电路在 AOL 与 1/β 交点处应有 20 dB/dec 闭合速率与 45°-90° 裕度 |

**验证**
- `spice`（partial）· ngspice / TINA-TI：带 R_O 的运放宏模型 + R_ISO + C_load — 断开反馈环做 AC 扫描（或注入法），读 AOL·β 单位增益处相位裕度 ≥ 45°；再做小信号阶跃，输出无持续振铃
- `bench`（manual）· 示波器 + 方波发生器 — 接真实线缆/负载电容，输出端 1 kHz 小幅方波，看过冲与振铃是否衰减

**来源**
- [Determine Optimal Isolation Resistance for Driving Capacitive Load (SBOA418)](https://www.ti.com/lit/pdf/sboa418) — Texas Instruments, app_note, §2-§3
- [Ask The Applications Engineer-25: Op Amps Driving Capacitive Loads](https://www.analog.com/en/resources/analog-dialogue/articles/ask-the-applications-engineer-25.html) — Analog Devices, app_note
- [Ask The Application Engineer-32: Practical Techniques to Avoid Instability Due to Capacitive Loading](https://www.analog.com/en/resources/analog-dialogue/articles/techniques-to-avoid-instability-capacitive-loading.html) — Analog Devices, app_note

<a id="AUD-SCH-004"></a>
#### AUD-SCH-004 · 音频端口加 RF 低通：输入、BTL 输出和电源入口
`should` · 可信度 `high` · 适用: opamp, line-input, btl-amplifier, wireless-coexistence

**规则** 每个音频输入（及模拟 BTL 功放输出、话筒线、电源入口）放 RF 低通：反相运放级的滤波电容接在两个等值电阻之间而不是直接接反相输入端，滤波带宽取信号带宽的 20-30 倍以上，电容用 NP0/C0G 或薄膜的低电感贴片。

**依据** 放大器输入的 ESD 二极管和 PN 结会对 RF 包络整流，把 GSM 的 217 Hz 帧率等突发调制变成带内失调和 buzz；音频走线在 2.4 GHz 附近长度约 3 cm 就是有效天线。

| 参数 | 判据 | 备注 |
|---|---|---|
| `filter_bandwidth_over_signal_bandwidth` | >= 20 ratio | AN1767：为减小信号损失，滤波带宽至少为信号带宽的 20 或 30 倍 |
| `rf_shunt_capacitor` | 10 … 39 pF | SNAA033D：自谐振在 900/1800 MHz 附近的 10-39 pF 对音频影响可忽略；每个对 RF 敏感的输入、输出、电源引脚各放一只 |
| `btl_output_lowpass_cutoff` | == 1 MHz | SNAA033D 案例：输出端磁珠 + 电容二阶低通，-3 dB 点 1 MHz，buzz 下降 30 dB（案例值，需按实际器件复核） |

**验证**
- `spice`（partial）· ngspice：.ac — 仿真 RC/磁珠+C 滤波后的响应，确认音频带内衰减可忽略、20-30 倍带宽以外开始衰减；反相级确认电容位置不在反相输入端上
- `bench`（manual）· 手机/Wi-Fi/BLE 发射源靠近 + 音频分析仪 FFT — 在最坏情况放置发射源，查 FFT 里 217 Hz 及谐波或无线包速率的音调，对比加/去滤波两种状态
- `review`（manual）· 原理图评审 — 逐个音频输入/输出/话筒/电源入口检查是否有 RF 滤波，滤波电容靠近放大器引脚而不是连接器侧

**来源**
- [AN1767 Solutions for Radio Frequency Electromagnetic Interference in Amplifier Circuits](http://ww1.microchip.com/downloads/en/appnotes/00001767a.pdf) — Microchip, app_note, Classical solution for EMI reduction: External Filters
- [AN-1496 Noise, TDMA Noise, and Suppression Techniques (SNAA033D)](https://www.ti.com/lit/an/snaa033d/snaa033d.pdf) — Texas Instruments, app_note
- [GSM RFI Suppression with EMI Filters](https://www.johansondielectrics.com/tech-notes/gsm-rfi-suppression-with-emi-filters/) — Johanson Dielectrics, vendor_guide
- [AN-CS002 CODEC Printed Circuit Board Layout Considerations](https://www.digikey.com/Site/Global/Layouts/DownloadPdf.ashx?pdfUrl=09748F6FB2B14376BFA057A887CFD3EF) — Nuvoton, app_note, item C

<a id="AUD-SCH-005"></a>
#### AUD-SCH-005 · 驻极体话筒偏置电阻、耦合电容和中点偏置滤波
`should` · 可信度 `high` · 适用: electret-microphone, preamp, single-supply

**规则** 偏置电阻 R1 = (Vcc - V_mic)/I_mic，取略小于计算值以容忍电源变化；R1 与耦合电容组成高通 fc = 1/(2π·R1·C)；运放中点偏置分压处并电容，使分压电阻并联值与该电容的 RC 角频率低于 20 Hz。

**依据** R1 的热噪声和电源噪声会直接进入话筒通路，R1 越大越利于降低噪声增益和减小所需耦合电容；偏置滤波角频率低于音频带才不会让噪声落入带内。

| 参数 | 判据 | 备注 |
|---|---|---|
| `bias_network_lowpass_corner` | < 20 Hz | TIDU765：R3 = R5 = 100 kΩ、C6 = 2.2 µF 时约 1.4 Hz |
| `coupling_cap_hpf_corner_example` | == 5 Hz | TIDU765 示例：R1 = 13.7 kΩ，5 Hz 角频率对应 C = 2.2 µF（公式 C = 1/(2π·R1·fc)）；产品低频下限不同则重算 |

**验证**
- `spice`（partial）· ngspice：压控电流源 + 噪声电流源建模话筒 — .ac 核对 fc；.noise 在 20 Hz-20 kHz 积分得到输入参考噪声，与 ARC 噪声预算对比；偏置网络 RC 角频率 < 20 Hz
- `bench`（manual）· 示波器 + 音频分析仪 — 静音环境测输出本底并在偏置电源上叠加小幅噪声，验证电源抑制

**来源**
- [Single-Supply, Electret Microphone Pre-Amplifier Reference Design (TIDU765)](https://www.ti.com/lit/pdf/tidu765) — Texas Instruments, app_note, §2.2, §2.3, §4

<a id="AUD-SCH-006"></a>
#### AUD-SCH-006 · 模拟 MEMS 话筒供电去耦、RF 滤波和耦合电容
`should` · 可信度 `high` · 适用: mems-microphone, codec-input

**规则** 模拟 MEMS 话筒不需要上拉偏置电阻；VDD 就近并 0.1-10 µF，电源噪声大时串磁珠并在芯片侧对地加 10-100 pF RF 电容；输出经 0.1-1.0 µF 隔直电容接 codec（codec 自偏置时），话筒输出与 VDD 走线不得平行而中间无地。

**依据** MEMS 话筒 PSRR 典型只有约 50 dB：10 mV rms 的电源噪声会变成约 30 µV rms 的输出，高于 11 µV rms 的本底噪声，相当于约 46 dB SPL 的声音输入。

| 参数 | 判据 | 备注 |
|---|---|---|
| `supply_decoupling` | 0.1 … 10 uF | Knowles 图 28 中的 Cpwr |
| `rf_shunt_capacitor` | 10 … 100 pF | Crf，靠近器件、RF 特性好的电容；放在磁珠的 codec 一侧 |
| `coupling_capacitor` | 0.1 … 1.0 uF | 与 codec 输入阻抗形成高通，目标 3 dB 点低于 100 Hz；codec 输入需外部直流偏置时参考 codec 手册 |

**验证**
- `review`（manual）· 原理图评审 — 核对 V+ 去耦、磁珠/RF 电容位置和 codec 输入偏置方式是否与话筒、codec 手册一致
- `bench`（manual）· 音频分析仪 — 静音环境测本底，再在话筒电源上注入已知小幅噪声（如 10 mV rms）看输出，核对约 50 dB 的 PSRR

**来源**
- [SiSonic Design Guide, AN16 Rev 3.0](https://media.digikey.com/pdf/data%20sheets/knowles%20acoustics%20pdfs/sisonic_design_guide.pdf) — Knowles, app_note, §4.1, §4.4, §4.6, Figure 28

<a id="AUD-SCH-007"></a>
#### AUD-SCH-007 · Codec 模拟电源独立稳压并滤波，MICBIAS 噪声同源
`should` · 可信度 `high` · 适用: codec, micbias, ldo

**规则** Codec 的 AVDD（及由它派生的 MICBIAS）由独立的低噪声稳压源或带 LC/磁珠滤波的支路供电，不与数字或功率级共用未滤波的轨；电源含高频噪声时在入口加低通/EMI 滤波。

**依据** MICBIAS 可直接选为 AVDD，AVDD 的噪声于是直接加到话筒信号上；codec 内部所有模拟处理都以该电源为基准。

| 参数 | 判据 | 备注 |
|---|---|---|
| `codec_supply_decoupling_small` | == 0.1 uF | 与 IC 同层、尽量靠近电源引脚（见 AUD-PLC-002） |
| `codec_supply_decoupling_bulk` | == 10 uF | 同上 |

**验证**
- `spice`（partial）· ngspice：LDO 输出阻抗/PSRR 宏模型 + 滤波器 — 对 AVDD 滤波支路做 AC 扫描，读 217 Hz、1 kHz、20 kHz 与开关频率处的纹波衰减，与 codec 的 PSRR 规格叠加评估
- `bench`（manual）· 示波器（20 MHz 带宽限制与全带宽各一次）+ 音频分析仪 — 测 AVDD/MICBIAS 噪声；在 AVDD 上注入纹波时看 ADC FFT 本底的变化
- `review`（manual）· 原理图评审 — 确认 AVDD、DVDD、IOVDD、PVDD 各自来源和滤波路径，没有未滤波的数字/功率轨直接供电给 AVDD

**来源**
- [Common Noise Issues in Audio Codecs (SLAA749)](https://www.ti.com/lit/an/slaa749/slaa749.pdf) — Texas Instruments, app_note, §2.3
- [AN-CS002 CODEC Printed Circuit Board Layout Considerations](https://www.digikey.com/Site/Global/Layouts/DownloadPdf.ashx?pdfUrl=09748F6FB2B14376BFA057A887CFD3EF) — Nuvoton, app_note, items A, G

<a id="AUD-SCH-008"></a>
#### AUD-SCH-008 · Codec 线路输出接 Class-D 输入前加 RC 低通
`should` · 可信度 `high` · 适用: codec, class-d, line-output

**规则** Codec 线路输出驱动外部 Class-D 功放输入时，在两者之间加 RC 低通滤除 Σ-Δ 带外噪声；TI 示例为 1 kΩ + 4.7 nF，极点约 33 kHz。

**依据** Σ-Δ 转换器的带外噪声虽然听不到，但 Class-D 放大后会抬高噪声和谐波，影响可听频段。

| 参数 | 判据 | 备注 |
|---|---|---|
| `series_resistor` | == 1 kOhm | TI 示例；需与功放输入阻抗一起算分压 |
| `shunt_capacitor` | == 4.7 nF | C0G/NP0 为宜（见 AUD-SCH-001） |
| `lowpass_pole` | == 33 kHz | TI 原文写 33 kHz（SLAA749）；按 1/(2π·1 kΩ·4.7 nF) 实算为 ≈33.9 kHz，33 为原文取整。TI 称对音频应用合适；高采样率/超声应用需上移 |

**验证**
- `spice`（partial）· ngspice：.ac — 含功放输入阻抗的实际 -3 dB 点，确认 20 kHz 处衰减在可接受范围，带外噪声被抑制
- `bench`（manual）· 音频分析仪（宽带 FFT，到 100 kHz 以上） — 有无该滤波两种状态下比较 Class-D 输出的带外噪声和 THD+N

**来源**
- [Common Noise Issues in Audio Codecs (SLAA749)](https://www.ti.com/lit/an/slaa749/slaa749.pdf) — Texas Instruments, app_note, §2.4, Figure 4

<a id="AUD-SCH-009"></a>
#### AUD-SCH-009 · 抑制 pop/click：匹配输入网络、RC≤1 ms、使能时序
`should` · 可信度 `high` · 适用: class-d, headphone-amplifier, ac-coupling

**规则** 差分输入两端阻抗相同，输入网络 RC 时间常数尽量不超过约 1 ms，使耦合电容在上电窗口内充满；功放使能晚于音源稳定，关断（或进入 shutdown）先于音源和电源掉电。

**依据** 耦合电容没充满时对元件失配更敏感，会在启动时产生 pop；音源还在建立或已关闭时放大器仍使能，会把音源的瞬变直接放大。

| 参数 | 判据 | 备注 |
|---|---|---|
| `input_rc_time_constant` | <= 1 ms | TPA3116D2：使耦合电容在 10 ms 上电时间内充满 |
| `enable_sequence` | qualitative | TPA6132A2：音源激活并稳定后再使能功放，掉电时先关功放再关音源；TPA3116D2：断电前先拉低 SDZ 进入 shutdown |

**验证**
- `spice`（partial）· ngspice：.tran — 模拟上电时输入耦合电容经 R_in 充向偏置点的过程，确认 5×(R·C) 小于上电窗口，输出偏移无台阶
- `bench`（manual）· 示波器（AC 耦合，输出端直接探测）+ 耳听 — 分别对上电、断电、SDZ/EN 开关、MUTE 切换抓输出瞬态，并在各种音源状态下重复；记录峰值并与产品要求比较
- `review`（manual）· 固件时序评审 — 核对使能 GPIO 的上电/掉电顺序与音源（codec、DAC）启动时序是否符合上述规则

**来源**
- [TPA3116D2 / TPA3118D2 / TPA3130D2 datasheet (SLOS708G)](https://www.ti.com/lit/ds/symlink/tpa3116d2.pdf) — Texas Instruments, datasheet, §7.3.3, §7.3.7
- [TPA6132A2 25-mW DirectPath stereo headphone amplifier (SLOS597A)](https://www.ti.com/lit/ds/slos597a/slos597a.pdf) — Texas Instruments, datasheet, §8.3.2

<a id="AUD-SCH-010"></a>
#### AUD-SCH-010 · 耳机输出：隔直电容容量，或无电容架构的接线
`should` · 可信度 `high` · 适用: headphone-amplifier, line-output, 3.5mm-jack

**规则** 单电源耳机输出用隔直电容时 C_out = 1/(2π·fc·R_L)（16 Ω 负载、20 Hz 至少约 500 µF）；可用 DirectPath/双极性输出的放大器取消电容。以 VCOM 为参考的 capless 型放大器不得把耳机插座套筒接地。

**依据** 大隔直电容占面积、增加高度，且开关机时充放电会产生 pop；capless 输出以中点电压为参考，套筒接地会产生大电流，也不能接非耳机附件。

| 参数 | 判据 | 备注 |
|---|---|---|
| `dc_block_cap_16ohm_20hz` | >= 500 uF | TPA6132A2 手册：16 Ω 耳机、20 Hz 截止至少 500 µF |

**验证**
- `erc`（partial）· KiCad ERC / 网表脚本 — 对 capless 型号，检查插座 SLEEVE/SGND 网络不连接系统 GND；对带电容型号，检查 C_out 满足公式
- `spice`（partial）· ngspice：.ac — 含耳机阻抗范围（16-32 Ω）的 -3 dB 点

**来源**
- [TPA6132A2 25-mW DirectPath stereo headphone amplifier (SLOS597A)](https://www.ti.com/lit/ds/slos597a/slos597a.pdf) — Texas Instruments, datasheet, §8.3.1, Eq.1-2

<a id="AUD-SCH-011"></a>
#### AUD-SCH-011 · Class-D 输出 LC 滤波器按二阶 Butterworth 设计
`should` · 可信度 `high` · 适用: class-d, lc-filter, btl

**规则** LC 滤波器取 Q = 0.707 的二阶 Butterworth：单端等效 L = √2·R_L/ω0、C = 1/(√2·R_L·ω0)；截止频率远高于 20 kHz、远低于开关频率，不允许明显峰化，并按扬声器阻抗的变化范围复核。

**依据** 欠阻尼滤波器在高频产生可听的刺耳峰值，还可能触发功放过流保护；过阻尼则吃掉高频音频内容。负载阻抗决定阻尼比，所以必须在阻抗范围内核算。

| 参数 | 判据 | 备注 |
|---|---|---|
| `q_factor` | == 0.707 ratio | SLAA701B Eq.5-6 的前提 |
| `example_corner_4ohm_30khz` | qualitative | SLYT199 表 1：4 Ω、fc = 30 kHz，每路 L = 15 µH，差分 C = 0.94 µF（老器件 TPA005D14） |
| `example_corner_tpa32xx` | == 73 kHz | SLAA701B：7 µH + 0.68 µF（或 10 µH + 0.47 µF）得 72.9/73.4 kHz，用于 600 kHz 开关频率的 TPA32xx；Type-1（AD 调制）与 Type-2（BD 调制）滤波器拓扑不同，按器件调制方式选 |

**验证**
- `spice`（partial）· ngspice：.ac，负载用 R_e + L_e 的扬声器模型，并扫 R_L 的最小/最大值 — 读 -3 dB 点与峰值：峰化小于约 1 dB、通带平坦到 20 kHz；在开关频率及其 ±10% 带内无谐振
- `bench`（manual）· 音频分析仪 / 网络分析 — 实际扬声器负载下扫频响，看高频有无峰化，并确认过流保护不被误触发

**来源**
- [Class-D LC Filter Design (SLAA701B, formerly SLOA119)](https://www.ti.com/lit/pdf/sloa119) — Texas Instruments, app_note, §1.3, §1.5（73 kHz 示例在 §1.5）
- [Power supply decoupling and audio signal filtering for the Class-D audio power amplifier (SLYT199)](https://www.ti.com/lit/pdf/slyt199) — Texas Instruments, app_note, Output filter, Table 1

<a id="AUD-SCH-012"></a>
#### AUD-SCH-012 · LC 滤波器电感和电容选型：线性度与降额
`should` · 可信度 `high` · 适用: class-d, lc-filter, inductor, film-capacitor

**规则** 电感的饱和电流必须高于直流 + 交流峰值电流并留裕度（不同厂家的 Isat 常定义在电感下降 30% 甚至更多，用到 Isat 会严重劣化 THD），选屏蔽、低 DCR 型；电容用金属化薄膜，用陶瓷时按电压降额，高功率输出时选额定电压 >150 V（推荐 250 V）、低 ESR。

**依据** 电感随电流饱和使电感量下降，阻抗越低的负载电流越大，失真越高；陶瓷电容 C ≈ C_rated·(1 - V/V_rated)，会让滤波器截止频率漂移，并带来电压系数失真。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ceramic_rated_voltage_min` | > 150 V | SLAA701B §1.5：用陶瓷电容时额定电压 > 150 V 为强制，推荐 250 V（针对 TPA32xx 一类高功率 Class-D；5 V 级低功率器件不套用该数值，属本库的补充说明） |
| `capacitor_low_frequency_esr_peak` | <= 1 Ohm | SLAA701B：低频峰值 ESR 建议不超过 1 Ω，频率越高越低 |
| `film_capacitor_dvdt_min` | >= 100 V/us | SLAA701B：50 Vpp、73 kHz 角频率约 23 V/µs，建议额定 dv/dt 取 100 V/µs 以留余量 |
| `inductance_change_1a_to_20a_good_examples` | <= 1.55 percent | SLAA701B 表 1-6：Würth 7443630700 为 0.94%，74436301000 为 1.38%，Coilcraft MA5173-AE 为 1.16%，MA5172-AE 为 1.55%（600 kHz 测试信号下的电感量平均变化，非通用门限） |

**验证**
- `bom_check`（partial）· 脚本：读电感 Isat（含对应 ΔL% 定义）、DCR 与峰值电流 — 峰值电流 = 峰值输出电压/R_L 加纹波，要求 Isat 对应的电感下降定义明确且峰值电流远低于它；电容额定电压、ESR、dv/dt 对照上述参数
- `bench`（manual）· 音频分析仪 — 在最低阻抗负载下，对不同电感型号测 THD+N-功率曲线并比较

**来源**
- [Class-D LC Filter Design (SLAA701B, formerly SLOA119)](https://www.ti.com/lit/pdf/sloa119) — Texas Instruments, app_note, §1.4.1, §1.5
- [Power supply decoupling and audio signal filtering for the Class-D audio power amplifier (SLYT199)](https://www.ti.com/lit/pdf/slyt199) — Texas Instruments, app_note, Component selection

<a id="AUD-SCH-013"></a>
#### AUD-SCH-013 · 免滤波 Class-D 的磁珠 EMI 滤波：电感性元件在前，禁止仅用电容
`should` · 可信度 `high` · 适用: class-d, filter-free, ferrite-bead

**规则** Filter-free 器件为过 EMC 时，每路输出先串铁氧体磁珠（或小电感），再接小电容到地；不得只用电容做输出滤波。滤波截止频率落在 1.5-10 MHz，磁珠额定电流留裕度，更换磁珠后重做 EMC 与 THD+N。

**依据** 输出边沿 dV/dt 约 0.7-2 V/ns，直接接电容会产生 I = C·dV/dt 的电流尖峰（250 pF × 2 V/ns ≈ 0.5 A），可能触发过流保护并增大损耗；磁珠还会影响 THD+N 并在高电流下饱和。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ferrite_lc_corner` | 1.5 … 10 MHz | 下限来自 SLAA901/SLAA920（≥1.5 MHz，有利于减少本底噪声与误触发），上限来自 SLOA145（磁珠与电容构成的 LC 谐振应小于 10 MHz）；以器件手册为准 |
| `bead_dc_current_fraction_of_rating` | <= 0.6 ratio | SLOA145：低频最大电流应为额定 DC 电流的 30%-60%，避免电感量大幅下降 |
| `capacitor_only_filter` | qualitative | SLAA901：永远不建议只用电容；若用，容量取满足发射标准的最小值，且留 10-20% 的陶瓷工艺公差余量 |

**验证**
- `spice`（partial）· ngspice：磁珠模型（R、L、并联 C）+ 输出电容 — AC 扫描找谐振点是否在 1.5-10 MHz；瞬态里 C·dV/dt 的尖峰电流低于器件过流阈值（含 ±20% 电容公差）
- `emc_precompliance`（manual）· 近场探头 + 频谱仪 / 预合规辐射扫描 — 30 MHz-1 GHz，最长实际扬声器线缆下，对比有无磁珠及不同磁珠型号
- `bench`（manual）· 音频分析仪 — 更换磁珠前后测 THD+N，磁珠在环外时高频失真会明显上升

**来源分歧** 低功率老器件用磁珠即可：SLOA145 图 5 为磁珠 + 1 nF，SLOA216 只给磁珠滤波、未给电容值；较新的智能功放（SLAA901、SLAA920）强调电感性元件在前且截止频率不低于 1.5 MHz。 两者并不矛盾，参数取并集区间，具体仍以所用器件手册和实测为准。

**来源**
- [Filter-Free Class-D Audio Amplifiers (SLOA145)](https://www.ti.com/lit/pdf/sloa145) — Texas Instruments, app_note, §3 Ferrite Bead Filters, Table 2
- [Limitations of Capacitor Only EMI Filters on Class-D Amplifiers (SLAA901)](https://www.ti.com/lit/pdf/slaa901) — Texas Instruments, app_note, §3
- [TAS2563 Schematic and Layout Guidelines (SLAA920)](https://www.ti.com/lit/an/slaa920/slaa920.pdf) — Texas Instruments, app_note, §2.8
- [TPA3140D2 Design Considerations for EMC (SLOA216)](https://www.ti.com/lit/an/sloa216/sloa216.pdf) — Texas Instruments, app_note, §3.2

<a id="AUD-SCH-015"></a>
#### AUD-SCH-015 · Class-D 电源引脚分级去耦和大容量电容
`should` · 可信度 `high` · 适用: class-d, pvcc, decoupling

**规则** 每个 PVCC 引脚配 220 pF-1 nF 的高频陶瓷和 100 nF-1 µF 的中频陶瓷（X5R 或更好），每侧另放 ≥100 µF 低 ESR 大电容；大电容按 C ≥ I_peak·T_D·D_max/V_ripple、ESR ≤ V_ripple/I_peak 核算。

**依据** Class-D 的脉冲电流需要低阻抗电压源，PVCC 纹波会直接变成失真；纹波通常由 ESR 而不是容量主导。

| 参数 | 判据 | 备注 |
|---|---|---|
| `hf_decoupling_capacitor` | 220 … 1000 pF | TPA3116D2 §10.1；SLOA216 对 TPA3140D2 建议 1 nF |
| `mf_decoupling_capacitor` | 0.1 … 1 uF | 同上；SLOA216 建议 0.1 µF |
| `bulk_capacitor` | >= 100 uF | TPA3116D2：每侧一个 100 µF/50 V 的低 ESR 电容；他处以 ESR 公式复核 |
| `bulk_esr_limit` | qualitative | SLYT199：ESR ≤ V_ripple/I_peak，并再留 30%-50% 余量（温度、ESL、老化） |

**验证**
- `bom_check`（partial）· 脚本：按 PVCC 引脚统计去耦电容 — 每个 PVCC 引脚旁都有高频、中频陶瓷；大电容容量与 ESR 满足上述公式（I_peak 取峰值功率对应的峰值电流，见 SLYT199 Eq.2）
- `pi_sim`（partial）· PDN 阻抗仿真（含电容 ESL/ESR、安装电感） — 在开关频率及其谐波处 PDN 阻抗低于由允许纹波/峰值电流得到的目标
- `bench`（manual）· 示波器（短接地弹簧探头） — 满功率下测 PVCC 引脚处纹波和开关过冲

**来源**
- [TPA3116D2 / TPA3118D2 / TPA3130D2 datasheet (SLOS708G)](https://www.ti.com/lit/ds/symlink/tpa3116d2.pdf) — Texas Instruments, datasheet, §8.2.2.3-§8.2.2.4, §10.1
- [Power supply decoupling and audio signal filtering for the Class-D audio power amplifier (SLYT199)](https://www.ti.com/lit/pdf/slyt199) — Texas Instruments, app_note, Power supply decoupling, Eq.2-4
- [TPA3140D2 Design Considerations for EMC (SLOA216)](https://www.ti.com/lit/an/sloa216/sloa216.pdf) — Texas Instruments, app_note, §3.1

<a id="AUD-SCH-016"></a>
#### AUD-SCH-016 · 平衡线路输入选高 CMRR 的差分接收器
`consider` · 可信度 `medium` · 适用: balanced-input, line-receiver, pro-audio

**规则** 专业线路输入选激光修调的平衡线路接收器 IC（典型 CMRR 约 90 dB）或高共模输入阻抗/变压器方案；用分立运放差分级时需要四颗高度匹配的电阻，并评估源阻抗不平衡的影响。

**依据** 差分级的 CMRR 取决于电阻比例匹配；源端两路阻抗不平衡时，低共模输入阻抗会把共模转成差模，真实系统里的 CMRR 远低于实验室指标。

| 参数 | 判据 | 备注 |
|---|---|---|
| `internal_resistor_ratio_match` | qualitative | EDN/THAT：激光修调接收器内部电阻比例修调到约 0.005%，同片电阻匹配典型 0.5%（THAT1286 例），CMRR 约 90 dB；未修调需外部匹配电阻 |

**验证**
- `spice`（partial）· ngspice 蒙特卡洛 — 电阻公差取 1%、0.1% 以及源阻抗失配（例如 0-600 Ω）时，在 60 Hz 和 1 kHz 处的 CMRR 分布
- `bench`（manual）· 信号发生器 + 音频分析仪 — 共模注入 1 Vrms，接入有失配的源阻抗，读差分输出，CMRR = 20·log(V_cm/V_out·增益)

**来源**
- [Audio line receiver impedance balancing using a 2nd diff amp](https://edn.com/Home/PrintView?contentItemId=4406013) — EDN, blog
- [THAT 1200 Series balanced line receiver datasheet](https://www.thatcorp.com/datashts/THAT_1200-Series_Datasheet.pdf) — THAT Corporation, datasheet
- [RaneNote 110: Sound System Interconnection](https://www.ranecommercial.com/legacy/note110.html) — Rane, vendor_guide

## 网表与约束（netlist）

<a id="AUD-NET-001"></a>
#### AUD-NET-001 · Class-D 输出、自举、Vsense 和电源分别设网络类
`should` · 可信度 `medium` · 适用: class-d, tas2xxx, net-class

**规则** 为 Class-D 输出（OUT_P/OUT_N）、自举、Vsense、功率与模拟电源、模拟输入和 I2S 时钟分别建 net class 并绑定约束：输出每路线宽 ≥30 mil（0.762 mm）并在两层并联、两路等长；Vsense 6 mil 差分；AVDD/VDD/IOVDD 用 20-30 mil 星形分发。

**依据** 这些网络的电流、开关特性和敏感度差异很大，不在网表阶段区分，后面的 DRC 和布线约束就无法自动检查。

| 参数 | 判据 | 备注 |
|---|---|---|
| `class_d_output_trace_width` | >= 0.762 mm | 30 mil，每层；两层并联等效 60 mil（SLAA902 §2.7）；表 3：30 mil/1 oz/62 mil FR4 约 3.18 A、9.68 mΩ/inch |
| `vsense_trace_width` | == 0.152 mm | 6 mil 足够，且最好差分（SLAA902 §2.5） |
| `avdd_vdd_iovdd_trace_width` | 0.508 … 0.762 mm | 20-30 mil，从 PMIC/电源源头星形连接（SLAA902 §2） |

**验证**
- `drc`（full）· KiCad 自定义规则 (.kicad_dru) + 网络类 — 对 OUT*、BST*、VSNS* 等网络类设最小线宽与间距约束；DRC 报告中无违规
- `netlist_diff`（full）· 脚本：读网表与网络类分配 — 所有连接 Class-D OUT/BST/VSNS 引脚的网络必须属于对应网络类，未分配即为失败

**来源**
- [PCB Layout Guidelines for TAS2xxx Series Class-D Non-boosted Audio Amplifier (SLAA902)](https://www.ti.com/lit/pdf/slaa902) — Texas Instruments, app_note, §2, §2.5, §2.7, §3 Table 3
- [PCB Layout Guidelines for TAS2xxx Series Class-D Boosted Audio Amplifier (SLAA896)](https://www.ti.com/lit/an/slaa896/slaa896.pdf) — Texas Instruments, app_note, §2.6, §2.8

## 叠层与规则（stackup）

<a id="AUD-STK-001"></a>
#### AUD-STK-001 · 含 Class-D 的音频板用 4-6 层，第二层整层做地
`should` · 可信度 `high` · 适用: class-d, codec, multilayer

**规则** 含 Class-D 或高性能 codec 的音频板优先 4-6 层，紧邻顶层的第二层整层做地、不走信号；两层板时底层几乎全做地，并把底层信号线缩到最短。

**依据** 紧邻器件的完整地层提供最短回流路径、减小环路电感，并为开关网络与其他信号之间提供屏蔽。

| 参数 | 判据 | 备注 |
|---|---|---|
| `layer_count` | 4 … 6 layers | TI SLAA902/SLAA896 的推荐；两层板为降级方案 |
| `gnd_layer_index` | == 2 layer | 紧邻顶层（SLAA920 §2.3：顶层下一层必须专用于地） |

**验证**
- `drc`（partial）· KiCad 叠层设置 + 脚本 — 读取叠层定义，第二层类型为 plane/zone 且网络为 GND；Class-D 与 codec 器件投影区内第二层无非 GND 铜、无切割
- `review`（manual）· 叠层评审 — 对照 Class-D 器件手册的叠层建议，核对层数、过孔类型（树脂塞孔）与板厂能力

**来源**
- [PCB Layout Guidelines for TAS2xxx Series Class-D Non-boosted Audio Amplifier (SLAA902)](https://www.ti.com/lit/pdf/slaa902) — Texas Instruments, app_note, §2
- [TAS2563 Schematic and Layout Guidelines (SLAA920)](https://www.ti.com/lit/an/slaa920/slaa920.pdf) — Texas Instruments, app_note, §2.3, §2.11
- [Circuit board layout guidelines for Class-D amplifiers](https://www.edn.com/circuit-board-layout-guidelines-for-class-d-amplifiers/) — EDN, blog, ground plane

## 分区规划（floorplan）

<a id="AUD-FLR-001"></a>
#### AUD-FLR-001 · 音频板分区：模拟输入、数字、Class-D 功率级各占一区
`should` · 可信度 `high` · 适用: codec, class-d, microphone, mixed-signal

**规则** 把板分成模拟输入区（连接器、话筒、前级、codec 模拟侧）、数字区（MCU、I2S、I2C）和 Class-D 功率级加滤波器三个区；输入连接器紧邻前级，话筒及其走线远离天线、PA、电机、开关电源、扬声器和功率级滤波电感。

**依据** 数字回流和开关电流只会在布线越界时才闯入模拟区；功率级滤波电感的磁场、开关节点的电场都会耦合进输入级和话筒这类小信号。

| 参数 | 判据 | 备注 |
|---|---|---|
| `analog_input_to_class_d_inductor_distance` | maximize | 无出处数值；SLYT199 只要求输入与输出（尤其是电感）分离以减小磁耦合，EDN 要求低压输入电路远离输出侧功率电路。用基线距离对比 |

**验证**
- `review`（manual）· 布局规划评审清单 — 检查三个区的划分、连接器位置、话筒与噪声源（天线、电机、DC-DC、扬声器）的距离，以及声孔是否可用
- `geometry_script`（partial）· pcbnew (KiCad bundled Python)，参见 ee-pcb-verify 的 geometry 检查器 — 计算模拟输入/话筒器件到 Class-D 滤波电感、开关节点的最短距离并输出报告，用于版本间回归比较

**来源**
- [Power supply decoupling and audio signal filtering for the Class-D audio power amplifier (SLYT199)](https://www.ti.com/lit/pdf/slyt199) — Texas Instruments, app_note, Inputs and outputs
- [SiSonic Design Guide, AN16 Rev 3.0](https://media.digikey.com/pdf/data%20sheets/knowles%20acoustics%20pdfs/sisonic_design_guide.pdf) — Knowles, app_note, §3.1
- [AN-CS002 CODEC Printed Circuit Board Layout Considerations](https://www.digikey.com/Site/Global/Layouts/DownloadPdf.ashx?pdfUrl=09748F6FB2B14376BFA057A887CFD3EF) — Nuvoton, app_note, items B, E
- [Partitioning and Layout of a Mixed-Signal PCB](https://www.eetimes.com/partitioning-and-layout-of-a-mixed-signal-pcb-3/) — EE Times (Henry Ott), paper

<a id="AUD-FLR-002"></a>
#### AUD-FLR-002 · 定 AGND/DGND 策略：默认单一地平面分区，按 codec 手册例外
`should` · 可信度 `high` · 适用: codec, adc, dac, mixed-signal

**规则** 默认用整块连续地平面并按模拟/数字/功率分区布线，codec 的 AGND、DGND 引脚都接到该平面；仅当 codec 手册明确要求拆地时才拆，且只在一处用 0 Ω 或窄桥连接，所有跨区信号从桥上经过。

**依据** 回流电流沿信号线正下方的参考平面走，拆地后信号线跨缝会增大环路并带来辐射与串扰；数字电流混入模拟地的真正原因通常是布线越界，而不是平面本身。

| 参数 | 判据 | 备注 |
|---|---|---|
| `split_plane_bridge_count` | == 1 count | 仅在手册要求拆地时适用，桥位于 codec 下方，桥宽按 Ott 建议与器件同宽 |

**验证**
- `review`（manual）· 对照 codec 数据手册 Layout 章节 — 记录手册的 AGND/DGND 要求（单平面 / 拆地 + 单点），并在设计文档里写明采用哪种及理由
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 若有拆地：统计穿越分割缝的信号走线数，除桥上以外必须为 0；若单平面：检查模拟区内无数字走线
- `bench`（manual）· 音频分析仪 — Ott 的 A/B 做法：拆地版与每隔约 1/2 英寸用 0 Ω 跳线桥接的版本对比本底噪声与 EMC 预扫，择优

**来源分歧** TI SLAA749 对 codec 建议拆成模拟、数字两块地并用 0 Ω 电阻或窄线连接，且模拟引脚/走线只放在模拟侧；Henry Ott、Nuvoton AN-CS002 和 ADI MT-031 主张单一连续地平面 （ADI 要求把转换器的 AGND/DGND 都接模拟地），TI 的 Class-D 文档 SLYT199 也认为整块地平面效果不差于其他方案。取舍： 默认单平面 + 严格分区布线；codec 手册明确要求拆地时服从手册并保证单点桥接；两种做法的共同要求是信号线不得跨越分割缝。

**来源**
- [Partitioning and Layout of a Mixed-Signal PCB](https://www.eetimes.com/partitioning-and-layout-of-a-mixed-signal-pcb-3/) — EE Times (Henry Ott), paper
- [Common Noise Issues in Audio Codecs (SLAA749)](https://www.ti.com/lit/an/slaa749/slaa749.pdf) — Texas Instruments, app_note, §2.1
- [AN-CS002 CODEC Printed Circuit Board Layout Considerations](https://www.digikey.com/Site/Global/Layouts/DownloadPdf.ashx?pdfUrl=09748F6FB2B14376BFA057A887CFD3EF) — Nuvoton, app_note, item H
- [MT-031 Grounding Data Converters and Solving the Mystery of AGND and DGND](https://www.analog.com/mt-031?doc=cn288.pdf) — Analog Devices, app_note

<a id="AUD-FLR-003"></a>
#### AUD-FLR-003 · 平衡接口屏蔽接机壳，信号地与机壳单点连接
`should` · 可信度 `medium` · 适用: balanced-input, xlr, pro-audio, chassis-ground

**规则** 平衡音频连接器的屏蔽层（XLR pin 1）在进入外壳处接机壳而不是信号地，信号地与机壳每台设备只在一处相连，使屏蔽电流不流经音频地；板载插座只能接信号地时，用短线接到最近的机壳点。

**依据** 屏蔽上感应的电流会调制其端接点的地电位，而音频信号以该地为参考，于是变成嗡声和 buzz（所谓 pin 1 问题）。

| 参数 | 判据 | 备注 |
|---|---|---|
| `signal_ground_to_chassis_connections` | == 1 count | Rane note 151：每台设备一点 |

**验证**
- `review`（manual）· 连接器/机壳连接评审 — 检查每个平衡连接器屏蔽的去向，信号地—机壳连接点数量，并避免使用地线断开(ground lift)开关
- `bench`（manual）· 音频分析仪 FFT — 与另一台设备互联后查 50/60 Hz 及其谐波；分别断开某条地连接来定位环路

**来源**
- [RaneNote 151: Grounding and Shielding Audio Devices](https://www.ranecommercial.com/legacy/note151.html) — Rane, vendor_guide
- [RaneNote 110: Sound System Interconnection](https://www.ranecommercial.com/legacy/note110.html) — Rane, vendor_guide

## 器件布局（placement）

<a id="AUD-PLC-001"></a>
#### AUD-PLC-001 · Class-D 去耦与自举电容紧贴引脚并控制回路电感
`must` · 可信度 `high` · 适用: class-d, qfn, tas2xxx, pvdd

**规则** 最小的去耦电容放在引脚 1 mm 以内、顶层同层，较大者紧随其后；去耦电容地端用多个过孔就近接地层；自举电容以星形接到 OUT 引脚而不是挂在粗的输出走线上，并按数据手册给的回路电感预算复核。

**依据** 开关电流在寄生电感上产生的电压尖峰直接变成 EMI 和性能劣化，哪怕几个 nH 也足以让器件工作异常。

| 参数 | 判据 | 备注 |
|---|---|---|
| `smallest_decap_to_pin_distance` | <= 1 mm | SLAA902/SLAA896 §2.3；EDN 给出 100 nF 在 2 mm 以内 |
| `bulk_cap_distance` | <= 30 mm | EDN：大电容离功放不超过 30 mm，并以星形连接 |
| `pvdd_pgnd_loop_inductance_total` | <= 900 pH | TAS2770 (SLAA902 表 2) 的包含电容 ESL 的总回路预算；PVDD-PGND 900 pH（即本参数）、VDD-GND 900 pH，另有 BST-OUT 1400 pH、VBAT-GND 1000 pH、DREG-GND 1050 pH。TAS2562 (SLAA896)：VBST-BGND 750 pH，GREG-PVDD 800 pH。只对所列型号有效 |
| `vbat_pin_to_decap_inductance` | < 500 pH | TAS2563 (SLAA920)：VBAT 引脚到去耦电容的寄生电感 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python)，参见 ee-pcb-verify 的 geometry 检查器 — 对每个 Class-D 电源/自举引脚找最近的去耦/自举电容焊盘，测焊盘中心距并确认同层；最小电容 ≤1 mm（具体型号以手册为准）
- `em_sim`（partial）· FastHenry / openEMS / Elmer 做回路电感提取 — 沿 引脚 → 电容 → 过孔 → GND 引脚 的环路提取电感，总值不超过器件手册的预算

**来源**
- [PCB Layout Guidelines for TAS2xxx Series Class-D Non-boosted Audio Amplifier (SLAA902)](https://www.ti.com/lit/pdf/slaa902) — Texas Instruments, app_note, §2.3, Table 2, §2.6
- [PCB Layout Guidelines for TAS2xxx Series Class-D Boosted Audio Amplifier (SLAA896)](https://www.ti.com/lit/an/slaa896/slaa896.pdf) — Texas Instruments, app_note, §2.3, Table 2
- [TAS2563 Schematic and Layout Guidelines (SLAA920)](https://www.ti.com/lit/an/slaa920/slaa920.pdf) — Texas Instruments, app_note, §2.2, §2.4
- [Circuit board layout guidelines for Class-D amplifiers](https://www.edn.com/circuit-board-layout-guidelines-for-class-d-amplifiers/) — EDN, blog, placement order, bypass

<a id="AUD-PLC-002"></a>
#### AUD-PLC-002 · Codec 去耦与 VREF/VAG 参考电容紧贴引脚
`should` · 可信度 `high` · 适用: codec, adc, dac, vref

**规则** Codec 每个供电引脚的 0.1 µF（及 10 µF）去耦与 VREF/VAG/CM 参考电容用最短走线接引脚、与 IC 同层；双面板上可直接放在芯片下方引脚之间，电容地端就近过孔接模拟地。

**依据** VAG/VREF 是 codec 内部所有模拟处理的参考，其上的噪声会原样进入转换结果；走线的电感和电阻会让去耦失效。

| 参数 | 判据 | 备注 |
|---|---|---|
| `decap_to_pin_trace_length` | minimize | 无 codec 级别的数值出处；Class-D 手册给的 ≤1 mm 可作为基线 |
| `codec_decoupling_values` | qualitative | 0.1 µF + 10 µF（SLAA749）；VDD、VAG、VREF 到 VSS 的 0.1 µF 陶瓷（AN-CS002） |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 对每个 AVDD/VREF/VAG 引脚找去耦电容焊盘，报告焊盘间距、是否同层、过孔到地层的数量，并与基线比较
- `review`（manual）· 布局评审 — 对照 codec 手册布局示例核对电容位置

**来源**
- [Common Noise Issues in Audio Codecs (SLAA749)](https://www.ti.com/lit/an/slaa749/slaa749.pdf) — Texas Instruments, app_note, §2.3
- [AN-CS002 CODEC Printed Circuit Board Layout Considerations](https://www.digikey.com/Site/Global/Layouts/DownloadPdf.ashx?pdfUrl=09748F6FB2B14376BFA057A887CFD3EF) — Nuvoton, app_note, items A, F

<a id="AUD-PLC-003"></a>
#### AUD-PLC-003 · 输出滤波器紧靠功放，电感相互隔开并远离输入
`should` · 可信度 `high` · 适用: class-d, lc-filter, ferrite-filter

**规则** 铁氧体/LC 滤波器与 EMC 缓冲电路放在紧靠输出引脚处，使“输出 → 磁珠/电感 → 电容 → GND”的电流环最小；非屏蔽电感彼此相距 ≥7.5 mm（尤其是通道之间），输出滤波器靠近扬声器接口并远离输入电路。

**依据** 输出电流环的大小决定它作为天线的效率；电感的磁场耦合进相邻通道和输入级会引入串扰与失真。

| 参数 | 判据 | 备注 |
|---|---|---|
| `unshielded_inductor_spacing` | >= 7.5 mm | EDN；屏蔽电感可更近，但 SLYT199 建议用屏蔽电感以减小串扰 |
| `filter_loop_area` | minimize | TPA3116D2 §10.1：输出经磁珠和滤波电容回 GND 的电流环要小而紧 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 测每路 OUT 引脚到滤波器第一个元件的路径长度，计算 OUT-L-C-GND 环路面积；非屏蔽电感中心距 ≥7.5 mm；滤波器到扬声器连接器距离
- `emc_precompliance`（manual）· 近场探头 — 沿输出环路和电感上方扫描，对比改动前后的近场峰值

**来源**
- [TPA3116D2 / TPA3118D2 / TPA3130D2 datasheet (SLOS708G)](https://www.ti.com/lit/ds/symlink/tpa3116d2.pdf) — Texas Instruments, datasheet, §10.1
- [PCB Layout Guidelines for TAS2xxx Series Class-D Non-boosted Audio Amplifier (SLAA902)](https://www.ti.com/lit/pdf/slaa902) — Texas Instruments, app_note, §2.7
- [Circuit board layout guidelines for Class-D amplifiers](https://www.edn.com/circuit-board-layout-guidelines-for-class-d-amplifiers/) — EDN, blog, output filters
- [TPA3140D2 Design Considerations for EMC (SLOA216)](https://www.ti.com/lit/an/sloa216/sloa216.pdf) — Texas Instruments, app_note, §3.1

## 布线（routing）

<a id="AUD-RTE-002"></a>
#### AUD-RTE-002 · 开关网络与其他信号在相邻层不平行重叠
`must` · 可信度 `high` · 适用: class-d, switching-node, multilayer

**规则** Class-D 输出、自举、Vsense（及升压 SW）这类持续开关的网络，在相邻层不得与其他信号线平行重叠，除非中间隔有完整地层；同层也要和其他信号保持距离。

**依据** 开关边沿通过层间电容耦合到相邻层信号，进入模拟或数字通路成为噪声；中间的地层把耦合截断。

| 参数 | 判据 | 备注 |
|---|---|---|
| `adjacent_layer_parallel_overlap_without_ground` | == 0 mm | SLAA902 §2.4 的图 4-6；允许的情形：交叉很短，或中间有地层 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 对开关网络类的每段铜，在相邻层查找非 GND 网络的铜段，计算平行重叠长度；中间无完整地层时必须为 0

**来源**
- [PCB Layout Guidelines for TAS2xxx Series Class-D Non-boosted Audio Amplifier (SLAA902)](https://www.ti.com/lit/pdf/slaa902) — Texas Instruments, app_note, §2.4, Figures 4-6
- [PCB Layout Guidelines for TAS2xxx Series Class-D Boosted Audio Amplifier (SLAA896)](https://www.ti.com/lit/an/slaa896/slaa896.pdf) — Texas Instruments, app_note, §2.4

<a id="AUD-RTE-001"></a>
#### AUD-RTE-001 · Class-D 输出走线宽、短、成对并等长
`should` · 可信度 `high` · 适用: class-d, btl, speaker-output

**规则** OUT+ 与 OUT- 各用 ≥30 mil 线宽、两层并联（每路等效 60 mil），尽量短；两路并行、间距最小以缩小环路面积，长度/电阻互相匹配，不同声道的输出线不要并排。

**依据** 输出线和扬声器线是最大的发射源；两路布线电阻不一致会让 THD+N 劣化，宽线还要承载峰值电流且不引入失真。

| 参数 | 判据 | 备注 |
|---|---|---|
| `output_trace_width_per_layer` | >= 0.762 mm | 30 mil，两层并联（SLAA902/SLAA896）；1 oz、62 mil FR4 下 30 mil 约 9.68 mΩ/inch、可载约 3.18 A |
| `output_pair_length_mismatch` | minimize | SLAA902：为获得最佳 THD+N，两路输出长度匹配；无数值出处 |
| `low_power_output_trace_current` | >= 0.7 A | SLYT199（TPA005D14，约 2 W 器件）：至少 0.7 A rms、峰值 1 A；仅作低功率器件参考 |

**验证**
- `drc`（full）· KiCad DRC（网络类最小线宽） — 输出网络线宽 ≥0.762 mm，并检查是否在两层均有走线
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 测 OUT_P、OUT_N 到滤波器之间走线长度差，并测两线并行段的平均间距；报告超出基线的项

**来源**
- [PCB Layout Guidelines for TAS2xxx Series Class-D Non-boosted Audio Amplifier (SLAA902)](https://www.ti.com/lit/pdf/slaa902) — Texas Instruments, app_note, §2.7, §3 Table 3
- [Circuit board layout guidelines for Class-D amplifiers](https://www.edn.com/circuit-board-layout-guidelines-for-class-d-amplifiers/) — EDN, blog, output filters
- [TPA3140D2 Design Considerations for EMC (SLOA216)](https://www.ti.com/lit/an/sloa216/sloa216.pdf) — Texas Instruments, app_note, §3.1

<a id="AUD-RTE-003"></a>
#### AUD-RTE-003 · 音频输入走线短、过完整地、远离开关与 RF
`should` · 可信度 `high` · 适用: audio-input, microphone, codec-input

**规则** 耦合电容到放大器输入的走线尽量短；音频走线在完整地平面上方，和时钟、射频、动态大电流走线保持距离，内层音频线两侧用带足够过孔的地线隔离；不让含 RF 或动态电流的走线从音频元件下方穿过，也不与其平行。

**依据** 小信号输入走线是接收天线，会拾取 RF、时钟谐波和开关噪声；地线 + 过孔围栏充当法拉第屏蔽。

| 参数 | 判据 | 备注 |
|---|---|---|
| `input_trace_length` | minimize | 无统一数值出处，SLYT199 要求从耦合电容到放大器输入尽量短 |
| `parallel_run_with_noisy_nets` | minimize | SNAA033D：避免与含 RF 或大动态电流的走线平行，间距尽量大 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 对音频输入网络类，测与时钟/开关/射频网络类的最小间距与平行段长度；检查线下方参考层为完整 GND
- `bench`（manual）· 音频分析仪 FFT + 近场探头 — 空载输入本底，查时钟、开关频率谐波和无线突发频率在音频带内的混叠产物

**来源**
- [Power supply decoupling and audio signal filtering for the Class-D audio power amplifier (SLYT199)](https://www.ti.com/lit/pdf/slyt199) — Texas Instruments, app_note, Inputs and outputs
- [AN-1496 Noise, TDMA Noise, and Suppression Techniques (SNAA033D)](https://www.ti.com/lit/an/snaa033d/snaa033d.pdf) — Texas Instruments, app_note
- [AN-CS002 CODEC Printed Circuit Board Layout Considerations](https://www.digikey.com/Site/Global/Layouts/DownloadPdf.ashx?pdfUrl=09748F6FB2B14376BFA057A887CFD3EF) — Nuvoton, app_note, items B, C, D
- [SiSonic Design Guide, AN16 Rev 3.0](https://media.digikey.com/pdf/data%20sheets/knowles%20acoustics%20pdfs/sisonic_design_guide.pdf) — Knowles, app_note, §4.6

<a id="AUD-RTE-004"></a>
#### AUD-RTE-004 · 差分音频信号成对对称走线，并铺在模拟地之上
`should` · 可信度 `high` · 适用: differential-input, microphone, line-input

**规则** 差分话筒/线路输入的两根线并行等长、对称布局，两路滤波与耦合元件对称，间距约一倍线宽并走在模拟地平面之上；单端源接差分输入时，未用输入端经与信号端同值的电容在信号源处交流接地，使两个输入端看到的阻抗相同。

**依据** 差分接收只有在两根线拾取的噪声相同、阻抗相同时才抵消共模；不对称会把共模转成差模。

| 参数 | 判据 | 备注 |
|---|---|---|
| `pair_spacing` | == 1 trace_width | Knowles 图 28：差分走线相距一个线宽，并在模拟地平面上方（仅为该话筒应用图的标注） |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 测差分对两线的长度差、平均间距，以及两路上滤波元件的位置对称性；参考层完整性
- `bench`（manual）· 信号发生器 + 音频分析仪 — 共模注入测实际 CMRR，对比对称布局与不对称版本

**来源**
- [SiSonic Design Guide, AN16 Rev 3.0](https://media.digikey.com/pdf/data%20sheets/knowles%20acoustics%20pdfs/sisonic_design_guide.pdf) — Knowles, app_note, §4.6, Figure 28
- [AN-CS002 CODEC Printed Circuit Board Layout Considerations](https://www.digikey.com/Site/Global/Layouts/DownloadPdf.ashx?pdfUrl=09748F6FB2B14376BFA057A887CFD3EF) — Nuvoton, app_note, item F
- [TPA3116D2 / TPA3118D2 / TPA3130D2 datasheet (SLOS708G)](https://www.ti.com/lit/ds/symlink/tpa3116d2.pdf) — Texas Instruments, datasheet, §7.3.7

<a id="AUD-RTE-005"></a>
#### AUD-RTE-005 · I2S/MCLK 时钟点对点、短、远离模拟引脚
`should` · 可信度 `medium` · 适用: i2s, mclk, codec

**规则** MCLK/BCLK/LRCK 从源到 codec 点对点走最短、下方为完整地，远离模拟输入、参考和 MICBIAS 走线，不留 stub；边沿快或线较长时在驱动端串小电阻阻尼反射。

**依据** 时钟翻转是 codec 内数字噪声耦合到模拟侧的主要根源；数字线本身也要当传输线对待，否则变成辐射源并污染电源与地。

| 参数 | 判据 | 备注 |
|---|---|---|
| `series_damping_resistor` | qualitative | 无厂商出处的数值；常见经验是几十欧，应以示波器或 SI 仿真在实际走线上确定，很短的线可省略 |
| `clock_trace_length` | minimize | 越短越好；MCLK 为 24.576 MHz 级时边沿很快，需考虑反射 |

**验证**
- `si_sim`（partial）· 传输线/IBIS 仿真 — 对 MCLK、BCLK 的驱动器 + 走线 + 接收器仿真，过冲/振铃在接收器输入范围内，边沿不过快
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 测时钟网络长度、与模拟网络类的最小间距和平行长度，检查其下方参考层无分割
- `bench`（manual）· 示波器 + 音频分析仪 — 测 MCLK 过冲/振铃，并比较时钟走线改动前后的 codec 本底噪声

**来源**
- [Common Noise Issues in Audio Codecs (SLAA749)](https://www.ti.com/lit/an/slaa749/slaa749.pdf) — Texas Instruments, app_note, §2.1
- [AN-CS002 CODEC Printed Circuit Board Layout Considerations](https://www.digikey.com/Site/Global/Layouts/DownloadPdf.ashx?pdfUrl=09748F6FB2B14376BFA057A887CFD3EF) — Nuvoton, app_note, item D

## 平面与铺铜（plane_pour）

<a id="AUD-PLN-001"></a>
#### AUD-PLN-001 · 器件下方保持完整地层，地引脚强连接，大电流回流不经输入地
`should` · 可信度 `high` · 适用: class-d, codec, ground-plane

**规则** Codec 与 Class-D 下方保持完整无割裂的地层（紧邻顶层）；所有地引脚（GND/PGND/AGND）在器件下方先短接再用多个过孔接地层，避免多重地环；每个电路的去耦、滤波电容接该电路最近的地引脚，输出滤波电容等大电流回流不得流经输入级的地连接。

**依据** 不同电源的回流路径由不同地引脚承担，任何一个地引脚连得弱都会在该电路里抬高地电位；大电流回流经过输入级的地连接，会把输出电流直接注入输入。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ground_pin_parasitic_inductance` | <= 150 pH | TAS2563 (SLAA920 §2.11) 对 BGND/GND/PGND 的建议，仅对该器件系列有效；TAS2xxx 其他型号以各自手册为准 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 对每个 GND/PGND 引脚统计到地层的过孔数及距离；检查输出滤波电容地端连接到 PGND 而不经 AGND/输入地
- `em_sim`（partial）· openEMS / Elmer / FastHenry — 提取 PGND → 滤波电容地 → PGND 回流路径，确认不穿越输入地网络；地引脚寄生电感不超过手册预算

**来源**
- [PCB Layout Guidelines for TAS2xxx Series Class-D Non-boosted Audio Amplifier (SLAA902)](https://www.ti.com/lit/pdf/slaa902) — Texas Instruments, app_note, §2.2
- [TAS2563 Schematic and Layout Guidelines (SLAA920)](https://www.ti.com/lit/an/slaa920/slaa920.pdf) — Texas Instruments, app_note, §2.11
- [Power supply decoupling and audio signal filtering for the Class-D audio power amplifier (SLYT199)](https://www.ti.com/lit/pdf/slyt199) — Texas Instruments, app_note, Ground plane
- [Circuit board layout guidelines for Class-D amplifiers](https://www.edn.com/circuit-board-layout-guidelines-for-class-d-amplifiers/) — EDN, blog, ground plane and vias

<a id="AUD-PLN-002"></a>
#### AUD-PLN-002 · 信号线不得跨越或切割地平面
`should` · 可信度 `high` · 适用: mixed-signal, codec, ground-plane

**规则** 任何信号线都不得跨越地平面的分割缝，也不得在同层把地铜割断；若必须拆地，所有跨区信号都走在单点桥上，保证回流在其正下方，数字回流留在数字区。

**依据** 高频回流沿信号线正下方的参考平面走，跨缝使环路变大，辐射与串扰剧增；切割地平面使模拟区的地回流被迫绕行。

| 参数 | 判据 | 备注 |
|---|---|---|
| `signals_crossing_ground_split` | == 0 count | 桥上通过的信号除外 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 提取 GND 铜区轮廓，找出缝隙和被走线切割的位置，数每条信号线与缝隙/切割的相交次数；桥以外必须为 0

**来源**
- [Partitioning and Layout of a Mixed-Signal PCB](https://www.eetimes.com/partitioning-and-layout-of-a-mixed-signal-pcb-3/) — EE Times (Henry Ott), paper
- [AN-1496 Noise, TDMA Noise, and Suppression Techniques (SNAA033D)](https://www.ti.com/lit/an/snaa033d/snaa033d.pdf) — Texas Instruments, app_note

## 出图与制造（manufacturing）

<a id="AUD-MFG-001"></a>
#### AUD-MFG-001 · MEMS 话筒工艺：声孔不镀铜、钢网破环、回流后禁水洗
`should` · 可信度 `high` · 适用: mems-microphone, smt-assembly

**规则** 底部声孔话筒的 PCB 声孔做成非金属化孔，焊盘钢网用破环图形，防止焊料/助焊剂进孔；钢网厚度 0.127-0.178 mm，回流不超过 3 次，回流后禁止水洗、超声清洗和刷板，也不得对声孔抽真空或插入物体。

**依据** 声孔被焊料或助焊剂堵塞会让频响和灵敏度失常；清洗剂、超声和真空会直接损坏 MEMS 膜片。

| 参数 | 判据 | 备注 |
|---|---|---|
| `stencil_thickness` | 0.127 … 0.178 mm | Knowles 推荐范围 |
| `reflow_passes` | <= 3 count | Knowles：保证 3 次，建议不超过 3 次 |

**验证**
- `review`（manual）· 制造说明（fab notes / 贴片工艺卡） — 在装配备注中写明：声孔 NPTH、禁水洗、禁超声、禁刷板、禁抽真空于声孔，以及回流次数限制
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 检查话筒焊盘钢网图形是否为破环（对底部声孔型），声孔为 NPTH

**来源**
- [SiSonic Design Guide, AN16 Rev 3.0](https://media.digikey.com/pdf/data%20sheets/knowles%20acoustics%20pdfs/sisonic_design_guide.pdf) — Knowles, app_note, §3.5, §5.1, §5.3

## 签核验证（verification）

<a id="AUD-VER-002"></a>
#### AUD-VER-002 · Class-D 扬声器输出必须差分测量，输出端不接地
`must` · 可信度 `high` · 适用: class-d, btl, test-fixture

**规则** BTL Class-D 的两个输出端对地都有以 PVCC/2 为中心的共模电压，测量用差分探头或平衡输入，且测量设备的共模抑制能力要高于输出级供电的一半；负端（黑端）绝不能接地或机壳；负载使用 4-8 Ω 假负载。

**依据** 把一个输出端接地等于短路桥臂，会损坏功放或仪器；非差分测量还会得到错误的失真与功率数值。

| 参数 | 判据 | 备注 |
|---|---|---|
| `measurement_cmrr_vs_supply` | qualitative | SLAA114：测量设备共模抑制需大于输出级供电电压的一半 |

**验证**
- `review`（manual）· 测试夹具与流程检查表 — 确认使用平衡输入或差分探头、假负载，黑端未接地/机壳，分析仪输入为浮地或平衡

**来源**
- [Digital Audio Measurements (SLAA114)](https://www.ti.com/lit/pdf/slaa114) — Texas Instruments, app_note, How should the balanced speaker output be handled?

<a id="AUD-VER-001"></a>
#### AUD-VER-001 · 按规范测 THD+N/SNR，并用 FFT 交叉验证
`should` · 可信度 `high` · 适用: class-d, codec, amplifier

**规则** 报告 THD+N 时带上频率、电平、增益、负载和测量带宽（默认 20 kHz 平坦、不加权）；Class-D 或 Σ-Δ 输出在分析仪前加 20 kHz 带宽限制（AES17 滤波器）或无源低通；用陷波法和 FFT 后处理两种方法互相核对。

**依据** PWM 与噪声整形的带外成分会使分析仪输入过载或让带宽限制滤波器放在链路太靠后，测出错误的 THD+N；FFT 能分解谐波、噪声整形、嗡声和互调。

| 参数 | 判据 | 备注 |
|---|---|---|
| `measurement_bandwidth` | 20 … 22 kHz | Rane 145；开关放大器见 SLAA114 |
| `fft_length` | == 16384 samples | SLAA114 示例：fs = 44.1 kHz、Blackman-Harris 窗，bin 宽 2.69165 Hz，20 Hz-20 kHz 对应 bin 7-7430 |
| `blackman_harris_window_correction` | == 0.761 ratio | V_rms,noise = K·sqrt(sum(V_bin²))，窗修正 K（Hanning 0.8165，Hamming 0.8566，Bartlett 0.8660，无窗 1.0） |

**验证**
- `bench`（partial）· 音频分析仪（AP 等，带 AES17 滤波器）或高质量声卡 + 差分输入 — 按指标中的条件测 THD+N；同时抓 FFT 并按上式后处理得 20 Hz-20 kHz 噪声和 2-7 次谐波，两者误差应在仪器不确定度内

**来源**
- [Digital Audio Measurements (SLAA114)](https://www.ti.com/lit/pdf/slaa114) — Texas Instruments, app_note, How to Perform Measurements on a TDAA; FFT post-processing
- [RaneNote 145: Audio Specifications](https://www.ranecommercial.com/legacy/note145.html) — Rane, vendor_guide
- AES17 Standard method for digital audio engineering: Measurement of digital audio equipment（AES17 §4.2.1.1（经 TI SLAA114 引用）） — Audio Engineering Society, standard

<a id="AUD-VER-003"></a>
#### AUD-VER-003 · 用 ngspice 仿真耦合、偏置网络和滤波器的 AC 与噪声
`should` · 可信度 `medium` · 适用: preamp, ac-coupling, microphone, lc-filter

**规则** 对每个模拟音频块（耦合高通、话筒偏置网络、前级、Class-D LC 滤波器）跑 .ac 与 .noise：核对转折频率、偏置分压低通小于 20 Hz、20 Hz-20 kHz 积分的输入参考噪声，以及 LC 滤波器在负载阻抗范围内的 Q 和峰化。

**依据** 这些网络的角频率和噪声由少数几个 R、C 决定，设计阶段仿真比等样板更快发现多数错误。

| 参数 | 判据 | 备注 |
|---|---|---|
| `bias_network_lowpass_corner` | < 20 Hz | TIDU765 |
| `noise_integration_band` | 20 … 20000 Hz | 与 ARC-003 的测量带宽一致 |

**验证**
- `spice`（partial）· ngspice：.ac dec 20 1 1Meg；.noise v(out) Vin dec 20 10 100k — 读 -3 dB 点、峰值、inoise_total/onoise_total（noise2 图），与设计值和噪声预算对比；.noise 的参考源需带 AC 幅度

**来源**
- [Ngspice User's Manual (.NOISE analysis)](https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml) — ngspice, tool_doc
- [Single-Supply, Electret Microphone Pre-Amplifier Reference Design (TIDU765)](https://www.ti.com/lit/pdf/tidu765) — Texas Instruments, app_note, §4
- [Determine Optimal Isolation Resistance for Driving Capacitive Load (SBOA418)](https://www.ti.com/lit/pdf/sboa418) — Texas Instruments, app_note, §2

<a id="AUD-VER-004"></a>
#### AUD-VER-004 · 向电源注入纹波测 PSRR 和电源耦合
`should` · 可信度 `high` · 适用: class-d, codec, mems-microphone, ldo

**规则** 输入交流接地，在 PVCC/AVDD 上叠加 200 mVpp 纹波，分别取 217 Hz、1 kHz、开关频率等频点，用 FFT 读输出该频点幅度并换算 PSRR，和数据手册对比。

**依据** 电源纹波与负载电流脉冲会耦合进输出（GSM 的 217 Hz 就是电源和地纹波耦合的典型例子），不在板上实测就不知道布局与去耦是否达标。

| 参数 | 判据 | 备注 |
|---|---|---|
| `injected_ripple` | == 200 mVpp | TPA3116D2 数据手册 PSRR 测试条件（1 kHz，增益 20 dB，输入交流接地） |
| `ripple_rejection_target` | <= -70 dB | TPA3116D2 典型值；按所选器件手册替换 |

**验证**
- `bench`（partial）· 信号发生器 + 电源叠加（耦合变压器或 Bias-T）+ 音频分析仪 FFT — 输入端短接/交流接地，在电源叠加纹波，读输出该频点幅度，PSRR = 20·log(V_out/V_ripple)（折算增益）；达到手册指标
- `spice`（partial）· ngspice：.ac — 对电源滤波网络与放大器 PSRR 宏模型扫频，预估纹波传递

**来源**
- [TPA3116D2 / TPA3118D2 / TPA3130D2 datasheet (SLOS708G)](https://www.ti.com/lit/ds/symlink/tpa3116d2.pdf) — Texas Instruments, datasheet, §6.6 AC Electrical Characteristics, KSVR
- [SiSonic Design Guide, AN16 Rev 3.0](https://media.digikey.com/pdf/data%20sheets/knowles%20acoustics%20pdfs/sisonic_design_guide.pdf) — Knowles, app_note, §4.1
- [AN-1496 Noise, TDMA Noise, and Suppression Techniques (SNAA033D)](https://www.ti.com/lit/an/snaa033d/snaa033d.pdf) — Texas Instruments, app_note

<a id="AUD-VER-005"></a>
#### AUD-VER-005 · 静态本底 FFT：查工频谐波、217 Hz 和开关频率成分
`should` · 可信度 `medium` · 适用: class-d, codec, preamp, grounding

**规则** 输入短路并端接、功放静音，做 FFT：50/60 Hz 及其谐波指向地环路或电源，217 Hz 及谐波指向 TDMA/无线突发，开关频率及边带指向滤波或去耦不足；用改变接地连接（断开或接入某条地线）来区分来源。

**依据** 不同来源在频谱上有不同特征，先看频谱再动手能快速定位而不是靠盲改。

| 参数 | 判据 | 备注 |
|---|---|---|
| `fft_span` | qualitative | 音频带内用 20 Hz-20 kHz；Class-D 需另外用宽带（到 1 MHz 以上）观察开关成分，注意分析仪过载（见 VER-001） |

**验证**
- `bench`（partial）· 音频分析仪 / 声卡 FFT + 示波器 — 空载本底下找峰值：50/60 Hz×n、217 Hz×n、开关频率；再做接地改动实验，记录哪个峰随之变化

**来源**
- [RaneNote 110: Sound System Interconnection](https://www.ranecommercial.com/legacy/note110.html) — Rane, vendor_guide, troubleshooting
- [AN-1496 Noise, TDMA Noise, and Suppression Techniques (SNAA033D)](https://www.ti.com/lit/an/snaa033d/snaa033d.pdf) — Texas Instruments, app_note
- [Digital Audio Measurements (SLAA114)](https://www.ti.com/lit/pdf/slaa114) — Texas Instruments, app_note, FFT analysis

<a id="AUD-VER-006"></a>
#### AUD-VER-006 · Class-D 辐射预扫：最长喇叭线与最终磁珠/滤波器配置
`should` · 可信度 `high` · 适用: class-d, filter-free, ferrite-bead

**规则** 用最终的磁珠或 LC 滤波器、最长实际扬声器线缆（如 1 m）和典型输出功率预扫 30 MHz-1 GHz 辐射与传导发射；更换磁珠型号后重测；扬声器线与电源线分开放置。

**依据** PWM 输出谐波延伸到数百 MHz，输出走线和喇叭线是最大发射源；磁珠的阻抗特性随型号差异大，不同批次/型号的结果不能互相代替。

| 参数 | 判据 | 备注 |
|---|---|---|
| `fcc_class_b_limit_30_88mhz` | <= 40 dBuV/m | 3 m；88-216 MHz 为 43，216-960 MHz 为 46（SLOA145 表 1 写作 213-960 MHz），960 MHz 以上 54 |
| `speaker_cable_length_no_lc_filter` | <= 1 m | TPA3140D2 配磁珠、扩频时 EVM 测试的线长（SLOA216）；老 TPA2000D2 EVM 在无滤波时 8 英寸以内可过 FCC/CE |

**验证**
- `emc_precompliance`（manual）· 近场探头 + 频谱仪，或 3 m 法预扫 — 30 MHz-1 GHz 辐射预扫，加 150 kHz-30 MHz 传导预扫；相对限值留足余量（SLOA216 的 EVM 余量多数大于 10 dB）

**来源**
- [Filter-Free Class-D Audio Amplifiers (SLOA145)](https://www.ti.com/lit/pdf/sloa145) — Texas Instruments, app_note, §3, Table 1
- [TPA3140D2 Design Considerations for EMC (SLOA216)](https://www.ti.com/lit/an/sloa216/sloa216.pdf) — Texas Instruments, app_note, §2.1, §3.3, §4
- [Filterless Class D simplifies audio amplifier design](https://www.eetimes.com/filterless-class-d-simplifies-audio-amplifier-design/) — EE Times, blog

