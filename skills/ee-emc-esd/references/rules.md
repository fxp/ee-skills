# EMC / ESD / 浪涌（emc_esd）— 规则全文

横向领域 · 46 条规则 · 由 `catalog/*.yaml` 生成，请改 YAML 不要改本文件。用 `grep -n "<规则ID>" rules.md` 定位单条，不要整份读。

环节分布：架构与选型 5，原理图 14，叠层与规则 2，分区规划 6，器件布局 4，布线 6，平面与铺铜 3，签核验证 6

## 架构与选型（architecture）

<a id="EMC-ARC-002"></a>
#### EMC-ARC-002 · ESD 目标等级按产品标准定，不靠 IC 的 HBM/CDM
`must` · 可信度 `high` · 适用: usb-c, connector, button, external-interface · 标签: cat-feeder

**规则** 需求里为每个用户可触及端口写明 IEC 61000-4-2 目标等级（接触/空气放电 kV）。IC 数据手册的 HBM/CDM 额定值只说明产线可制造性，不能当作整机 ESD 保护；用户可触及端口必须有板级保护器件，且保护器件自身的 IEC 61000-4-2 等级不低于目标等级。

**依据** IEC 61000-4-2 脉冲上升更快（8 kV 接触放电标称首峰 30 A、上升约 0.8 ns）、持续更长、能量远高于 HBM/CDM；TI 指出只有 HBM/CDM 额定值的器件很可能撑不过真实使用中的重复放电。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esd_contact_test_voltage` | 2 … 8 kV | IEC 61000-4-2 Table 1：等级 1–4 的接触放电 = 2 / 4 / 6 / 8 kV |
| `esd_air_test_voltage` | 2 … 15 kV | IEC 61000-4-2 Table 1：等级 1–4 的空气放电 = 2 / 4 / 8 / 15 kV |
| `esd_first_peak_current_level4` | == 30 A | Table 3：8 kV 等级首峰 30 A（±15%），上升时间 0.8 ns（±25%），30 ns 处 16 A，60 ns 处 8 A |
| `esd_gun_series_resistance` | == 330 ohm | Table 2 注 3：放电电阻典型值 330 Ω |
| `esd_gun_storage_capacitance` | == 150 pF | Table 2 注 2：Cd + Cs 典型值 150 pF |

**验证**
- `review`（manual）· 需求文档 / 测试计划 — 每个外部端口都列有接触/空气放电目标等级；未列出的端口视为不通过
- `bom_check`（partial）· BOM 脚本，读 TVS 数据手册参数表 — 每个端口保护器件的 IEC 61000-4-2 接触/空气等级 ≥ 该端口目标等级，且额定值来自数据手册的 IEC 项而非 HBM/CDM 项

**来源**
- [IEC 61000-4-2 Ed.2.0 (2008) ESD immunity test](https://www.itu.int/en/ITU-D/Technology/Documents/Events2016/CI_Training_ARB_Tunis_April16/Session8/IEC_61000-4-2_2008.pdf) — IEC (copy hosted by ITU), standard, Table 1, Table 2, Table 3
- [ESD Fundamentals Part 2: IEC 61000-4-2 Rating (SSZT871)](https://www.ti.com/lit/pdf/sszt871) — Texas Instruments, app_note

<a id="EMC-ARC-001"></a>
#### EMC-ARC-001 · 按源—路径—受害者拆解每个 EMC 问题
`should` · 可信度 `high` · 适用: mcu-board · 标签: cat-feeder

**规则** 对每个发射或抗扰问题先写出噪声源（哪个引脚/开关节点/时钟）、耦合路径（共模/差模、传导/辐射、公共阻抗、环路）和受害者，优先在源头压低（降边沿速率、缩回路、限频）；翻转速率低于 50 kHz 的引脚不必列入 EMI 滤波清单。

**依据** SZZA009 把 MCU 板 RF 噪声来源按重要性排为 I/O 引脚、供电系统（稳压器与旁路电容）、振荡器；噪声沿最低阻抗路径回到源头，所以控制回路形状与阻抗就能控制传播，公共阻抗是最常见的共模来源。

| 参数 | 判据 | 备注 |
|---|---|---|
| `emi_relevant_toggle_rate` | > 50 kHz | SZZA009 §1.3：只需关注翻转速率高于 50 kHz 的引脚，低于该速率的引脚贡献可忽略 |

**验证**
- `review`（manual）· EMC 风险登记表（自建表格） — 对每个 > 50 kHz 的周期性网络（时钟、PWM、SPI/I2C、开关节点）写出 source / path / victim 三栏与采取的措施；任何一栏为空即不通过
- `emc_precompliance`（manual）· 近场探头 + 频谱仪 — 对登记表中前 3 个噪声源做近场扫描，确认实测峰值频率与预期谐波（n×f_clk、n×f_PWM）对应，且措施后峰值下降

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §1.1, §1.3, §1.4, §1.5

<a id="EMC-ARC-003"></a>
#### EMC-ARC-003 · 按端口确定 EFT 与浪涌等级和性能判据
`should` · 可信度 `high` · 适用: power-port, signal-port, motor, relay · 标签: cat-feeder

**规则** 为每个电源口、信号/控制口在需求里写明 IEC 61000-4-4（EFT/burst）与 IEC 61000-4-5（浪涌）的等级和性能判据（A/B/C），并据此选择保护架构；板上继电器、电机等感性负载既是 EFT 类干扰的源，也要被当作受害者检查。

**依据** EFT 模拟感性负载切断、继电器触点抖动等开关瞬变，特点是幅度高、上升时间短（5 ns）、重复频率高、能量低；浪涌模拟开关和雷击瞬变，用 1.2/50 µs 开路电压 / 8/20 µs 短路电流组合波、发生器等效内阻 2 Ω。两者的保护手段不同（EFT 靠滤波与布局，浪涌靠能量吸收器件）。

| 参数 | 判据 | 备注 |
|---|---|---|
| `eft_test_voltage_signal_ports` | 0.25 … 2 kV | IEC 61000-4-4 Table 1：等级 1–4 的信号/控制口 = 0.25 / 0.5 / 1 / 2 kV |
| `eft_test_voltage_power_ports` | 0.5 … 4 kV | IEC 61000-4-4 Table 1：等级 1–4 的电源口与 PE = 0.5 / 1 / 2 / 4 kV；重复频率 5 kHz 或 100 kHz，由产品标准定 |
| `surge_test_voltage_line_to_ground` | 0.5 … 4 kV | IEC 61000-4-5 Table 1：等级 1–4 的线—地 = 0.5 / 1 / 2 / 4 kV |
| `surge_test_voltage_line_to_line` | 0.5 … 2 kV | IEC 61000-4-5 Table 1：等级 2–4 的线—线 = 0.5 / 1 / 2 kV（等级 1 无线—线项） |
| `surge_generator_effective_impedance` | == 2 ohm | IEC 61000-4-5 §6.2.1 与 Table 3：0.5 kV 开路 ↔ 0.25 kA 短路，即 2 Ω |

**验证**
- `review`（manual）· 需求文档 / 测试计划 — 每个端口有 EFT 等级、浪涌等级、重复频率和性能判据；电源口和带长线缆的口与产品标准逐项对照
- `bench`（manual）· EFT/surge 发生器 + 耦合夹/CDN（认证实验室） — 按 IEC 61000-4-4 §8.3 / 61000-4-5 §8.3 的测试计划：两种极性、每端口不少于 1 min（EFT），浪涌从低等级逐级打到规定等级

**来源**
- [IEC 61000-4-4 Ed.3.0 (2012) Electrical fast transient/burst immunity test](https://www.itu.int/en/ITU-D/Technology/Documents/Events2016/CI_Training_ARB_Tunis_April16/Session8/IEC_61000-4-4_2012.pdf) — IEC (copy hosted by ITU), standard, §4, §5 Table 1, §6.2
- [IEC 61000-4-5 Ed.3.0 (2014) Surge immunity test](https://www.itu.int/en/ITU-D/Technology/Documents/Events2016/CI_Training_ARB_Tunis_April16/Session8/IEC_61000-4-5_2014.pdf) — IEC (copy hosted by ITU), standard, §5 Table 1, §6.2, Table 3
- [Electric Fast Transient (EFT) Application Note](https://www.maxlinear.com/appnote/electric%20fast%20transient%20application%20note_301anr00.pdf) — MaxLinear, app_note

<a id="EMC-ARC-004"></a>
#### EMC-ARC-004 · 边沿速率与时钟频率取满足时序的最慢值
`should` · 可信度 `high` · 适用: mcu, clock, gpio, pwm · 标签: cat-feeder

**规则** 对每条时钟、高速 GPIO、PWM 网络，把频率和驱动强度/边沿速率降到时序刚好满足的程度，输出端预留串联电阻位置；能降频就降频，能缩短走线或电缆就缩短。

**依据** 差模辐射来自信号—回流环路，随边沿速率和频率上升；SZZA009 要求差模噪声降到「最慢允许的上升/下降时间、最小必要频率」，TI SNLA302 的开工清单也先问「能否用更低的频率」。Espressif 建议在 SPI 线上留 0 Ω 位置以调驱动强度、降低 RF 干扰。

**验证**
- `review`（manual）· 网络清单表（自建）：频率、驱动强度、上升时间 — 每条 > 50 kHz 网络都记录频率、驱动强度设置、20–80% 上升时间；高于时序所需者要写出理由
- `si_sim`（partial）· ngspice / IBIS 仿真 — 用 IBIS 或驱动阻抗 + 串联 R + 走线电容估算接收端上升时间，确认时序裕量仍满足且上升时间不比必需值快 2 倍以上（2 倍为经验取值）
- `emc_precompliance`（manual）· 近场探头 + 频谱仪 — 比较降低驱动强度/频率前后的近场峰值，目标是主谐波下降

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.4.3, §2.5.1
- [High-Speed Layout Guidelines for Reducing EMI for LVDS SerDes Designs (SNLA302)](https://www.ti.com/lit/pdf/snla302) — Texas Instruments, app_note, §1 开工清单
- [ESP32-C3 Hardware Design Guidelines - Schematic Checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, Flash (SPI)

<a id="EMC-ARC-005"></a>
#### EMC-ARC-005 · 展频时钟只降峰值不降总能量，先评估时序
`consider` · 可信度 `medium` · 适用: clock-oscillator, switching-regulator, pll

**规则** 对固定频率的时钟或开关电源，可启用展频（SSC，优先下展），调制深度须在抖动/时序预算内；收益要按实际测试的 RBW 和检波器评估，不能直接套用厂商 dB 数。

**依据** 展频把窄带能量摊到更宽频带，总能量不变，只降低峰值；调制频率约取等于测试 RBW 才最有效，调制过大会增加输出纹波与周期抖动。低频时偏移量受系统约束，峰值降幅不会优于 10·log(RBW/2Δf)。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ssc_peak_reduction` | 7 … 20 dB | Diodes AN-11 称辐射降 7–20 dB，取决于调制深度；属厂商宣称值，需按自己的 RBW 实测 |

**验证**
- `emc_precompliance`（manual）· 频谱仪（与认证相同的 RBW 与检波器） — SSC 开/关各扫一次，比较峰值与准峰值降幅，并确认被调制的接口（USB、ADC 采样时钟等）在抖动与时序上仍满足规格

**来源**
- [Application Note 11 - EMI Reduction Techniques](https://www.diodes.com/assets/App-Note-Files/AN011-P.pdf) — Diodes Inc. (Pericom), app_note
- [EMI Reduction Technique, Dual Random Spread Spectrum (SNVA974)](https://www.ti.com/lit/pdf/snva974) — Texas Instruments, app_note, §2.1–§2.3

## 原理图（schematic）

<a id="EMC-SCH-008"></a>
#### EMC-SCH-008 · TVS 按 VRWM、VBR、VC、IPP、电容选型
`must` · 可信度 `high` · 适用: tvs, esd-diode, usb, power-input · 标签: cat-feeder

**规则** TVS 的 VRWM 须不低于线路最大工作电压（含容差）；VBR 高于最大电源电压；在设计的 IPP 下 VC 须低于被保护器件的绝对最大值（再叠加布局电感的附加压降）；IPP 与脉冲功率须大于威胁电流；信号线的电容满足带宽预算；过零信号用双向器件；器件自身的 IEC 61000-4-2 等级不低于目标。

**依据** VRWM 超出会造成漏电和误钳位；VC 取决于击穿电压加动态电阻与电感项；TVS 在威胁电流超过 IPP 时先短路失效。双向器件的工作电压范围通常对称（如 ±3.6 V、±5.5 V），单向器件仅正向但负向钳位更好。

| 参数 | 判据 | 备注 |
|---|---|---|
| `tvs_vrwm_vs_max_operating_voltage` | qualitative | VRWM > 最大工作电压（Vishay Table 1：stand-off > operating） |
| `tvs_vc_vs_protected_abs_max` | qualitative | VC@IPP < 被保护器件绝对最大额定（TI SSZT363）；来源未给统一裕量，由设计者定 |

**验证**
- `bom_check`（partial）· BOM 脚本 + 数据手册参数表 — 对每个 TVS 比较 VRWM ≥ V_max_op、VBR > V_supply_max、VC@IPP < 被保护引脚 Abs.Max（含 2 倍布局电感项）、IEC 等级 ≥ 目标；任何一条不满足即失败
- `spice`（partial）· ngspice + 厂商 TVS 模型 — 加 IEC 61000-4-2 8 kV 电流源（见 EMC-VER-003），读被保护引脚峰值电压

**来源**
- [ESD Packaging and Layout Guide (SLVAEX9B)](https://www.ti.com/lit/pdf/slvaex9) — Texas Instruments, app_note, §1.1–§1.5
- [Selecting TVS Diodes in Hot-swap and ORing Applications (SSZT363)](https://www.ti.com/lit/pdf/sszt363) — Texas Instruments, app_note
- [Failure Modes and Fusing of TVS Devices (AN 88440)](https://www.vishay.com/docs/88440/failurem.pdf) — Vishay, app_note, Table 1

<a id="EMC-SCH-009"></a>
#### EMC-SCH-009 · 所有用户可触及端口和电源入口都要有 ESD 路径
`must` · 可信度 `high` · 适用: usb-c, button, connector, power-input · 标签: cat-feeder

**规则** 每个用户可触及的连接器引脚（USB-C 的 VBUS/CC/D±、电机、传感器口）、按键和外露导体都要有板级 ESD 路径；金属壳连接器的放电打在壳体上，壳体必须有低阻抗路径到地；主电源入口加 ESD 二极管和不小于 10 µF 的电容。

**依据** IEC 61000-4-2 对带金属壳的连接器只对壳体做接触放电，对塑料壳连接器的引脚做空气放电；放电电流因此首先进入壳体接地路径，再经 PCB 地流向各器件。Espressif 建议在主电源入口加 ESD 二极管与至少 10 µF 电容。

**验证**
- `geometry_script`（partial）· 读网表的脚本 — 枚举连接器上每个信号/电源网络及按键网络，要求连通图上从连接器焊盘出发一跳内存在 TVS/ESD 阵列焊盘；金属壳焊盘必须连到地/机壳网络
- `review`（manual）· ESD 路径评审清单 — 对每个端口画出放电电流路径（接触点→壳体/TVS→地→返回），确认不穿过敏感电路

**来源**
- [IEC 61000-4-2 Ed.2.0 (2008) ESD immunity test](https://www.itu.int/en/ITU-D/Technology/Documents/Events2016/CI_Training_ARB_Tunis_April16/Session8/IEC_61000-4-2_2008.pdf) — IEC (copy hosted by ITU), standard, §8.3.2, Table 4
- [ESP32-C3 Hardware Design Guidelines - Schematic Checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, Power Supply
- [ESD Fundamentals Part 2: IEC 61000-4-2 Rating (SSZT871)](https://www.ti.com/lit/pdf/sszt871) — Texas Instruments, app_note

<a id="EMC-SCH-001"></a>
#### EMC-SCH-001 · MCU 输出/时钟脚串联阻尼电阻
`should` · 可信度 `high` · 适用: mcu, gpio, uart, spi · 标签: cat-feeder

**规则** MCU 数字输出脚串联 50–100 Ω、输入脚串联 35–50 Ω，电阻贴近芯片；不要加在晶振脚上。ESP32-C3 的 U0TXD 串 499 Ω，SPI 线预留 0 Ω 位置用于调驱动和抑制干扰。如同时加对地小电容，输出脚的电容放在电阻的接收端侧，输入脚的电容放在 MCU 侧。

**依据** CMOS 输出欠阻尼，串联电阻同时抑制振铃并降低差模边沿能量，是 SZZA009 为 MCU 系统首选的端接方式；电阻放在芯片端能让大部分走线处于被阻尼的一侧。

| 参数 | 判据 | 备注 |
|---|---|---|
| `series_r_output` | 50 … 100 ohm | SZZA009 §2.2.5：每个输出脚；系统要求更大串联电阻时用更大值 |
| `series_r_input` | 35 … 50 ohm | SZZA009 §2.2.5：每个输入脚 |
| `pin_bypass_cap` | == 1000 pF | SZZA009 §2.2.5：仅当信号需要的边沿不快于 100 ns 时才加；与电阻二选一时只保留电阻 |
| `uart_tx_series_r` | == 499 ohm | Espressif ESP32-C3 原理图清单：U0TXD 串 499 Ω 抑制谐波 |

**验证**
- `geometry_script`（partial）· 读 .kicad_sch/.kicad_pcb 网表的脚本 — 对离开 PCB 的 MCU 输出网络（接到连接器的网络），沿连通图查找 MCU 引脚到连接器之间的串联电阻，缺失则报错；再量电阻焊盘到 MCU 引脚焊盘的距离并列出最远者供审阅
- `si_sim`（partial）· ngspice — 加入驱动阻抗 + 串联 R + 走线/负载电容，确认接收端上升时间满足接口时序

**来源分歧** SZZA009 的阻值针对 5 V CMOS MCU 的低速 GPIO。高速接口（数十 MHz 的 SPI、USB）的阻值必须由时序和阻抗决定，Espressif 给 USB D+/D− 的起始值是 22/33 Ω。取舍：低速 GPIO 用 SZZA009 区间作缺省，高速接口按器件手册。

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.2.5, §2.4.3
- [ESP32-C3 Hardware Design Guidelines - Schematic Checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, UART / SPI / USB

<a id="EMC-SCH-002"></a>
#### EMC-SCH-002 · EN/复位类敏感脚：短走线加 RC，不加大电容
`should` · 可信度 `high` · 适用: esp32-c3, reset, enable · 标签: cat-feeder

**规则** 复位/EN、中断和晶振类对程序流有决定性影响的引脚按抗扰优先设计：CHIP_EN 走线尽量短并加 RC 延时（参考 10 kΩ + 1 µF），不得悬空；GPIO9 等 strapping 脚不加大电容；晶振脚不加串联滤波。

**依据** 外场耦合到高阻输入后被整流成直流偏移，可使输入越过阈值，若是复位则器件反复复位，若是晶振则失去时钟；SZZA009 指出最关键的抗扰脚是晶振、复位、中断和分支输入。Espressif 明确要求 CHIP_EN 走线尽量短以免外部干扰引起重启。

| 参数 | 判据 | 备注 |
|---|---|---|
| `chip_en_rc_r` | == 10 kohm | Espressif 推荐 RC 延时示例，需按实际上电时序调整 |
| `chip_en_rc_c` | == 1 uF | 同上 |
| `chip_en_low_level_max` | <= 0.825 V | 手册给 VIL_nRST 范围上限 0.25×VDD，3.3 V 供电时 0.825 V；EN 电压低于该值会被当作低电平（复位），噪声毛刺不得使 EN 跌到此值以下 |

**验证**
- `erc`（partial）· KiCad ERC + 网络检查脚本 — CHIP_EN 网络有上拉电阻和对地电容，且无悬空；strapping 脚（GPIO9）上无 ≥ 100 nF 电容
- `geometry_script`（partial）· pcbnew Python — 输出 CHIP_EN 走线总长，并检查它与电机/开关节点网络的最小间距，供评审
- `bench`（manual）· 示波器（≥ 200 MHz） — 在 ESD 枪打 USB 壳体、电机启停/堵转时抓 EN 与 3V3，确认毛刺不跨过 VIL 门限、无复位

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.2.5, §2.6.2
- [ESP32-C3 Hardware Design Guidelines - Schematic Checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, Chip Power-up and Reset Timing; Strapping Pins

<a id="EMC-SCH-004"></a>
#### EMC-SCH-004 · 磁珠按直流偏置降额，不看 100 MHz 标称阻抗
`should` · 可信度 `high` · 适用: ferrite-bead, power-filter

**规则** 用于供电滤波的铁氧体磁珠，要在厂商 DC-bias 曲线上读取实际工作电流下、噪声频率处的阻抗；没有曲线时让工作电流不超过额定电流的约 20%。

**依据** 数据手册通常只给零偏置、100 MHz 的阻抗；负载电流使磁芯趋于饱和，电感随之下降。ADI 的例子里，50% 额定电流时电感最多下降 90%，20% 额定电流时 6 A 磁珠电感剩约 30%、3 A 磁珠剩约 15%。额定电流是温升限值，不是滤波的工作点。

| 参数 | 判据 | 备注 |
|---|---|---|
| `bead_operating_current_fraction` | <= 20 % | ADI AN-1368：约 20% 额定直流电流；该值针对其举例的 TDK MPZ1608 / Würth 742 792 系列，以所选型号的 DC-bias 曲线为准 |

**验证**
- `bom_check`（partial）· BOM 脚本 + 厂商曲线（Murata SimSurfing / TDK SEAT / Würth REDEXPERT） — 对每个磁珠，在 I_load 下读目标频率处阻抗 Z_bias，要求 Z_bias ≥ 滤波需求；无曲线时要求 I_load ≤ 0.2 × I_rated
- `bench`（manual）· 网络分析仪 + 偏置 T 或在线测量 — 带实际负载电流测磁珠插入损耗，与零偏置结果对比

**来源分歧** Renesas AN-805 称接近额定值时阻抗「可能减半」，ADI AN-1368 的曲线显示 50% 额定电流时电感最多降 90%，Abracon 白皮书的例子是 300 mA 偏置下 100 MHz 阻抗由 650 Ω 降到约 110 Ω。降幅与型号相关；结论一致：零偏置阻抗偏乐观。取舍：采用更保守的 ADI 数据并读所选型号的实际曲线。

**来源**
- [AN-1368 Ferrite Bead Demystified for power-supply filtering (mirror copy)](https://docs.ampnuts.ru/analog.com.datasheet/adp5070/related_data/AN-1368.pdf) — Analog Devices, app_note, DC Bias Current Considerations, Figure 7
- [AN-805 Recommended Ferrite Beads](https://www.renesas.com/en/document/apn/805-recommended-ferrite-beads) — Renesas, app_note
- [Ferrite Beads Basic Operations and Key Parameters](https://abracon.com/uploads/resources/Ferrite-Beads-White-Paper.pdf) — Abracon, vendor_guide, DC bias

<a id="EMC-SCH-005"></a>
#### EMC-SCH-005 · 磁珠要在噪声频段呈电阻性，且与电容的 LC 需阻尼
`should` · 可信度 `high` · 适用: ferrite-bead, dc-dc, ic-supply

**规则** 选磁珠时看 Z/R/X 随频率曲线，保证要滤除的噪声频率落在以电阻分量为主的频段；磁珠与去耦电容构成的低通 LC 谐振频率若落在磁珠仍呈电感的区域，必须加阻尼（磁珠自身 DCR、串联电阻或并联 RC），并仿真确认无谐振峰。

**依据** 磁珠在低频是高 Q 电感，只有在电阻区才真正把噪声转成热；与高 Q 电容组成的欠阻尼滤波器会在谐振点放大噪声而不是衰减，常恰好落在 DC-DC 开关频率附近。

| 参数 | 判据 | 备注 |
|---|---|---|
| `lc_resonance_typical_range` | 0.1 … 10 MHz | ADI AN-1368：典型磁珠滤波器的 LC 谐振频率范围；开关频率 300 kHz–5 MHz 时需额外阻尼 |
| `bead_resistive_region_start` | 20 … 30 MHz | ADI AN-1368 对 TDK MPZ1608S101A 的实例：约 20–30 MHz 以上电阻分量才显著；其他型号请读自己的曲线 |

**验证**
- `spice`（full）· ngspice / LTspice，磁珠 R‖L‖C 模型，含 DCR 与负载电流下的电感 — AC 扫描 IC 侧电压对输入噪声的传递函数，任何频点增益不得 > 0 dB（无放大），并列出谐振频率
- `bench`（manual）· 示波器 / 频谱仪 — 在开关频率及其谐波处测滤波前后纹波，确认衰减而非放大

**来源**
- [AN-1368 Ferrite Bead Demystified for power-supply filtering (mirror copy)](https://docs.ampnuts.ru/analog.com.datasheet/adp5070/related_data/AN-1368.pdf) — Analog Devices, app_note, LC Resonance Effect, Damping Methods
- [AN-805 Recommended Ferrite Beads](https://www.renesas.com/en/document/apn/805-recommended-ferrite-beads) — Renesas, app_note

<a id="EMC-SCH-006"></a>
#### EMC-SCH-006 · 出机壳的线在连接器处加小电容到机壳/屏蔽地
`should` · 可信度 `high` · 适用: connector, cable, io-port · 标签: cat-feeder

**规则** 每根离开外壳的信号线，在连接器处加对机壳/屏蔽地的旁路电容（值小于 1000 pF，典型约 470 pF）或 RC/磁珠滤波，并按优先级从离开外壳的线、离开本板的线、板内高阻线逐级覆盖；电容必须不破坏该信号所需的边沿。

**依据** 电容既滤掉板内向外传的噪声，也把线缆外部拾取的噪声和 ESD 能量旁路到屏蔽/机壳；小于 1000 pF 是为了在 50–500 MHz 保持低 ESR，SMD 比带引线电容好（带引线电容约 80 MHz 即自谐振）。

| 参数 | 判据 | 备注 |
|---|---|---|
| `io_filter_cap_max` | < 1000 pF | SZZA009 §2.5.5 / §3.3：应小于 1000 pF，更可能取 470 pF 左右 |
| `chassis_connection_length_to_width` | <= 3 ratio | SZZA009 §3.3：到机壳的连接是 RF 路径，长宽比 3:1 |
| `leaded_cap_self_resonance` | == 80 MHz | SZZA009 §1.2：带引线电容约 80 MHz 自谐振，之后呈感性 |

**验证**
- `geometry_script`（partial）· pcbnew Python — 对每个连接器信号网络确认存在 R/C/磁珠滤波件，且电容另一端接到 chassis/shield 网络；量该连接铜皮的长/宽 ≤ 3
- `spice`（partial）· ngspice — RC 拐点与信号边沿/带宽对比，确认信号完整性不受损

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §1.2, §2.2.5, §2.5.4, §2.5.5, §3.3, Figure 13

<a id="EMC-SCH-010"></a>
#### EMC-SCH-010 · 保险丝与 TVS 的先后顺序要显式决定
`should` · 可信度 `medium` · 适用: power-input, usb-vbus, tvs, fuse, pptc · 标签: cat-feeder

**规则** 直流电源输入上，串联的保险丝/PPTC 放在 TVS 之前，使 TVS 失效短路后的跟随电流被切断，TVS 紧邻被保护电路并放在保险丝（串联电感/电阻）之后；纯信号线不加保险丝，TVS 直接放在连接器处。

**依据** TVS 失效首选模式是短路，之后会把电源的工作电流导向地，成为安全隐患；Vishay 建议在电源与数据线上都在 TVS 之前串联熔断元件，板级保护时保险丝紧靠 TVS。TI 热插拔文章也指出 TVS 的最佳位置是在输入串联电感（如保险丝）之后。

**验证**
- `review`（manual）· 原理图评审 — 每个 DC 电源输入：连接器 → 保险丝/PPTC → TVS → 稳压；保险丝 I²t 低于 TVS 短路后可承受值（见 Vishay Fig.3），保持电流 ≥ 正常负载
- `bench`（manual）· 限流电源 + 示波器 — 故障注入：升压到 TVS 击穿并短路，确认保险丝先于走线/PCB 过热断开；再做 IEC 8 kV 接触放电确认钳位与保险丝不动作

**来源分歧** Vishay AN 88440 与 TI SSZT363 主张保险丝在前。TI E2E 上的一条放大器论坛回答（仅见搜索摘要，未打开）主张连接器 → TVS（无限流电阻）→ 电子保险丝 → EMI 滤波的顺序，理由是 ESD 电流应先到 TVS；另一条 TI E2E 的 ISO1044 线程（仅见搜索摘要）称 TVS 放在保险丝后，因为放在连接器处的 TVS 遇到它无法承受的过压时会失效短路。取舍：电源口按安全优先——保险丝在前；若担心保险丝引线电感影响 ESD 钳位，选低电感（贴片）保险丝并让 TVS 紧邻其后；信号线无保险丝，不存在该冲突。

**来源**
- [Failure Modes and Fusing of TVS Devices (AN 88440)](https://www.vishay.com/docs/88440/failurem.pdf) — Vishay, app_note
- [Selecting TVS Diodes in Hot-swap and ORing Applications (SSZT363)](https://www.ti.com/lit/pdf/sszt363) — Texas Instruments, app_note
- [TPD1E6B06: Placement of TVS Diode and Fuse with ISO1044](https://e2e.ti.com/support/interface-group/interface/f/interface-forum/1433757/tpd1e6b06-placement-of-tvs-diode-and-fuse-with-iso1044) — TI E2E, forum
- [The correct order of TVS, filters and clamp diodes](https://e2e.ti.com/support/amplifiers/f/amplifiers-forum/911201/the-correct-order-of-tvs-filters-and-clamp-diodes) — TI E2E, forum

<a id="EMC-SCH-012"></a>
#### EMC-SCH-012 · 电机端子并联陶瓷电容（跨端子 + 对外壳）
`should` · 可信度 `medium` · 适用: brushed-dc-motor, h-bridge, low-side-mosfet · 标签: cat-feeder

**规则** 刷式直流电机在电机壳体处焊 1–3 个无极性陶瓷电容：一个跨两端子，另两个分别从两端子到电机外壳；用 PWM 驱动时要使电容与电机电感的谐振频率远离 PWM 频率，并检查驱动器电流尖峰。

**依据** 电刷换向产生宽带电弧噪声，高频电流经引线辐射；跨接电容给高频噪声提供短路路径而不影响电机功率，到外壳的电容进一步减小电刷电弧并降低辐射。电容过大与电机电感谐振，或在 PWM 下增加开关损耗。

| 参数 | 判据 | 备注 |
|---|---|---|
| `motor_terminal_cap_pololu` | == 0.1 uF | Pololu：1–3 个 0.1 µF 陶瓷电容，越靠近电机壳体越好，双向控制不要用极性电容 |
| `motor_terminal_cap_pmd_range` | 0.0001 … 0.1 uF | Precision Microdrives AB-005：100 pF–100 nF，取决于电机尺寸；用 PWM 时通常 10–100 pF |

**验证**
- `spice`（partial）· ngspice，电机用 R‖L + 反电势模型 — 扫 Ce，求 f_r 并确认与 PWM 频率相差一个数量级以上（一个数量级为经验取值）；检查开关管峰值电流
- `emc_precompliance`（manual）· 近场探头 / 电流探头夹在电机引线上 — 加装电容前后比较 30–300 MHz 的噪声峰值，目标下降

**来源分歧** Pololu 建议 0.1 µF；Precision Microdrives 针对小型振动电机用 PWM 驱动时建议 10–100 pF，并要求谐振频率 f_r = 1/(2π√(Lm·Ce)) 远离 PWM 频率。差别来自电机尺寸与驱动方式。取舍：本板 5 V、堵转 1.2 A 的减速电机，先按 Pololu 的 0.1 µF 起步，再用示波器看驱动器/ MOSFET 电流尖峰与 PWM 边沿，必要时降到更小值。

**来源**
- [Dealing with Motor Noise (Pololu 3pi / Orangutan motor driver note, §9)](https://www.pololu.com/docs/0J15/9) — Pololu, vendor_guide
- [AB-005: EMC (EMI) for Vibe Motors](https://www.precisionmicrodrives.com/ab-005) — Precision Microdrives, app_note

<a id="EMC-SCH-013"></a>
#### EMC-SCH-013 · 感性负载必须有续流/钳位路径
`should` · 可信度 `medium` · 适用: relay, solenoid, brushed-dc-motor, h-bridge · 标签: cat-feeder

**规则** 每个由开关管控制的感性负载（继电器线圈、电磁阀、直流电机）必须在关断时有续流路径：二极管反并联在负载上并贴近负载，或由 H 桥的体二极管/慢衰减提供；需要快速释放的继电器可在二极管上串 Zener 或电阻，但必须核对开关管 Vds 和元件功率。

**依据** 电流不能瞬间归零，V = L·di/dt 会在开关管上产生尖峰；例如 10 nH、50 A 在数十 ns 内关断就可产生 50 V 的叠加电压。续流二极管把负载电压限制在二极管正向压降，但会延迟继电器释放。

| 参数 | 判据 | 备注 |
|---|---|---|
| `freewheel_diode_clamp_voltage` | 0.7 … 1.5 V | Wikipedia Flyback diode：电感电压被限制在二极管正向压降，约 0.7–1.5 V；肖特基更低，但会进一步延长继电器释放时间 |

**验证**
- `erc`（partial）· KiCad 网络脚本 — 对每个被开关管（MOSFET/BJT/驱动 IC 输出）驱动的线圈/电机节点，确认存在二极管反并联或驱动 IC 内部体二极管（见数据手册）
- `spice`（full）· ngspice — 仿真关断瞬态，读开关管 Vds 峰值，须低于其 Vds 额定并留裕量
- `bench`（manual）· 示波器 + 差分探头 — 在电机启动、堵转、反转时抓开关管漏极电压，峰值不超过器件额定

**来源**
- [Flyback diode](https://en.wikipedia.org/wiki/Flyback_diode) — Wikipedia, blog
- [DRV8833 Dual H-Bridge Motor Driver](https://www.ti.com/lit/ds/symlink/drv8833.pdf) — Texas Instruments, datasheet, §8 recirculation current, fast/slow decay
- [Selecting TVS Diodes in Hot-swap and ORing Applications (SSZT363)](https://www.ti.com/lit/pdf/sszt363) — Texas Instruments, app_note

<a id="EMC-SCH-003"></a>
#### EMC-SCH-003 · IC 供电用磁珠 + 旁路电容做 π 型滤波
`consider` · 可信度 `high` · 适用: mcu, ldo-output, ic-supply

**规则** 对高噪声 IC 的供电，在 +V 上串一个铁氧体磁珠（只加在电源线、不加在地线），旁路电容（0.1 µF 或 0.01 µF）放在磁珠的 IC 一侧，磁珠电源侧再并一个 1000 pF 电容构成 π 型滤波；四层板可省 1000 pF 但原理图先画上，EMI 测试后再删。

**依据** IC 开关电流应由旁路电容供给而不是电源走线；磁珠阻止 RF 电流从电源线路获取，迫使 IC 只用磁珠内侧的储能，从而把 RF 噪声留在芯片附近。

| 参数 | 判据 | 备注 |
|---|---|---|
| `bypass_cap_inside_bead` | 0.01 … 0.1 uF | SZZA009 §2.2.4：0.1 µF 或 0.01 µF，放在磁珠的 IC 侧 |
| `bypass_cap_outside_bead` | == 1000 pF | SZZA009 §2.2.4：磁珠外侧，接微控制器地；若该点噪声大，它可能把噪声耦回 +V |

**验证**
- `spice`（partial）· ngspice AC 扫描，磁珠用 R‖L‖C 模型 — 在负载电流下扫 100 kHz–1 GHz，检查 IC 侧电源阻抗与磁珠—电容谐振峰（峰值须低于 0 dB 增益，见 EMC-SCH-005）
- `emc_precompliance`（manual）· 近场探头 + 频谱仪 — 拆装 1000 pF 与磁珠做对比扫描，只保留有实测收益的元件

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.2.4, Figure 9

<a id="EMC-SCH-007"></a>
#### EMC-SCH-007 · 线缆共模电流大时用共模扼流圈或磁环
`consider` · 可信度 `medium` · 适用: cable, motor-leads, connector · 标签: cat-feeder

**规则** 当电流探头或近场扫描显示线缆共模电流是主要发射源时，在连接器入口加共模扼流圈，或给整条线缆套铁氧体磁环；扼流圈须在问题频段有足够共模阻抗、额定电流大于工作电流，且不得损伤差分信号完整性。电机引线也适用。

**依据** 共模噪声的错误在板上的公共阻抗，线缆只是天线；能在源头降低公共阻抗最好，否则用磁环/扼流圈阻断共模电流。扼流圈对差模电流理想上无影响，但磁芯在大工作电流下会饱和。

| 参数 | 判据 | 备注 |
|---|---|---|
| `cm_choke_impedance_at_problem_frequency` | maximize | 按实测共模电流的峰值频率选型；来源未给具体阻抗数值 |

**验证**
- `emc_precompliance`（manual）· 电流探头（夹在线缆上）+ 频谱仪 — 加扼流圈前后测线缆共模电流谱，目标频点下降；差分信号眼图/时序不退化
- `bom_check`（partial）· BOM 脚本 — 扼流圈额定电流 ≥ 工作电流 × 1.0 且在该电流下的共模阻抗曲线可查

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.5.1
- [AB-005: EMC (EMI) for Vibe Motors](https://www.precisionmicrodrives.com/ab-005) — Precision Microdrives, app_note
- [High-Speed Layout Guidelines for Reducing EMI for LVDS SerDes Designs (SNLA302)](https://www.ti.com/lit/pdf/snla302) — Texas Instruments, app_note, §3

<a id="EMC-SCH-011"></a>
#### EMC-SCH-011 · GDT/MOV/TVS/保险丝各司其职并配合使用
`consider` · 可信度 `medium` · 适用: mains-port, long-cable-port, surge

**规则** 长线缆或市电口的浪涌保护按角色分层：GDT/MOV 承担大电流，TVS 作低钳位的后级，保险丝/PPTC 限制故障电流。GDT 在带电电源线上有续流风险，应选电源专用型号或串联 MOV；MOV 会因多次浪涌劣化并热失控，须选带热保护的 MOV 或加前级保险丝；TVS 不得超过其 IPP。保险丝的额定电压和分断能力必须高于系统故障源。

**依据** GDT 击穿后形成电弧，导通续流时可能无法熄灭而过热；MOV 劣化后漏电升高并持续自热；TVS 钳位最低但耐浪涌能力有限（Littelfuse 用 1500 W 的 SMCJ 在 6 kV/3 kA 浪涌下演示过应力失效，并提醒走线也要按电流选宽度，否则会先熔断）。IEC 61000-4-5 的发生器等效内阻为 2 Ω，所以 0.5 kV 开路电压对应约 250 A 短路电流，选 IPP 时要按此估算威胁电流。

| 参数 | 判据 | 备注 |
|---|---|---|
| `surge_short_circuit_current_per_open_circuit_voltage` | == 0.5 kA/kV | IEC 61000-4-5 Table 3：0.5 kV ↔ 0.25 kA，1 kV ↔ 0.5 kA，2 kV ↔ 1 kA，4 kV ↔ 2 kA（发生器输出端，2 Ω） |

**验证**
- `spice`（partial）· ngspice，1.2/50 µs–8/20 µs 组合波源（Rs = 2 Ω）+ 保护网络模型 — 在目标等级下读各级器件峰值电流与残压，确认 TVS 电流 < IPP、MOV/GDT 电流 < 其 8/20 µs 额定，被保护节点残压 < 绝对最大值
- `bench`（manual）· 浪涌发生器 — 从低等级逐级打到规定等级，每级后复测 TVS 漏电和 MOV 参考电压是否漂移

**来源**
- [GDTs, MOVs & Fuses: Selecting the Appropriate Circuit Protection Component](https://www.ieee.li/pdf/viewgraphs/selecting_the_appropriate_circuit_protection_component.pdf) — Littelfuse, vendor_guide
- [IEC 61000-4-5 Ed.3.0 (2014) Surge immunity test](https://www.itu.int/en/ITU-D/Technology/Documents/Events2016/CI_Training_ARB_Tunis_April16/Session8/IEC_61000-4-5_2014.pdf) — IEC (copy hosted by ITU), standard, §6.2.1, Table 3

<a id="EMC-SCH-014"></a>
#### EMC-SCH-014 · 连接器金属壳/机壳地与信号地的连接方式要显式决定
`consider` · 可信度 `medium` · 适用: usb-c, shielded-connector · 标签: cat-feeder

**规则** 对金属壳连接器（如 USB-C），原理图里明确选择一种方式并说明理由：壳体直接低电感接信号地；壳体接机壳地、机壳地经 R‖C 或磁珠接信号地；或悬空。无机壳地可用时优先直接接地，并预留 0 Ω 与 R/C 位置以便调试。

**依据** TI 指出 TVS 的地与数字/模拟地之间隔以电感的机壳地对 ESD 很有效，但会让高速信号跨越多个地平面而很难布线，所以很多设计用同一个地；若没有机壳接地，紧耦合的多层地平面能让被保护 IC 处的地偏移保持较小。SZZA009 则要求有一个把稳压器、MCU、电池负极和机壳/屏蔽连起来的单点参考。

**验证**
- `review`（manual）· 原理图评审 — 每个金属壳连接器的壳体网络有明确去向（直接地 / RC / 磁珠），并预留可换件的焊盘
- `bench`（manual）· ESD 枪（接触放电打壳体）+ 示波器 — 4 kV 接触放电打 USB 壳体，观察 EN、3V3 与 USB 链路有无复位/掉线；换不同的壳体接法对比

**来源分歧** SLVA680：分离的机壳地 ESD 效果很好但布线难，很多设计用公共地；SZZA009：屏蔽层接单点参考；论坛（仅见搜索摘要，未打开）转述的 USB 做法有三种：1 MΩ 并 4.7 nF 接信号地（据称来自 Cypress 与 Atmel AVR1017 §3.3.3）、壳体直接接地（据称为 Intel 做法）、经磁珠接地；另有一条 Linux 内核邮件列表报告把壳体经 1 MΩ‖1 nF 接保护地后 USB 不稳定，改为直接接 GND 后消失。取舍：本板塑料外壳、无保护地，采用壳体直接接信号地且 TVS 地紧邻，并保留 R/C 焊盘，因为在没有机壳地时分离地没有 ESD 收益。

**来源**
- [ESD Protection Layout Guide (SLVA680A)](https://www.ti.com/lit/pdf/slva680) — Texas Instruments, app_note, §1, §2.4
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.2.1, §3.2
- [USB device cable shield connection - grounding it or not?](https://forum.allaboutcircuits.com/threads/usb-device-cable-shield-connection-grounding-it-or-not.58811/) — All About Circuits forum, forum

## 叠层与规则（stackup）

<a id="EMC-STK-001"></a>
#### EMC-STK-001 · 两层板：栅格化地 + 电源地叠放，逼近四层效果
`should` · 可信度 `high` · 适用: two-layer, mcu-board · 标签: cat-feeder

**规则** 没有整层地平面的两层板，要靠布局模拟四层板的效果：地做成栅格或整片并多点过孔互连，信号回流紧贴信号线下方，电源走线正对地线，MCU 下方做一块地岛并向器件外延伸约 1/4 英寸，去耦电容与晶振的地接到这块地岛；IC 到电压源的电源/地走线长宽比不超过 3:1。

**依据** SZZA009 称做到这些后，两层板可达到四层板约 95% 的效果；回流路径紧贴信号线是缩小环路面积、控制辐射的最有效手段。需要更严格的发射或高速接口时再升到四层（信号/地/电源/信号）。

| 参数 | 判据 | 备注 |
|---|---|---|
| `power_ground_trace_length_to_width` | <= 3 ratio | SZZA009 §2.1.1：两层板上 IC 与电压源之间的电源/地走线 |
| `mcu_ground_island_extension` | >= 6.35 mm | SZZA009 §2.1.3：地岛延伸出器件轮廓约 1/4 英寸（6.35 mm）；该数值为英制换算 |

**验证**
- `geometry_script`（partial）· pcbnew Python — 采样每条周期性信号走线，检查走线下方（对层）或其两侧 1 mm 内是否有地铜；记录无地覆盖的长度占比，目标占比越低越好；检查电源走线与对应地走线是否上下重叠
- `emc_precompliance`（manual）· 近场探头 + 频谱仪 — 对比改版前后近场峰值

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.1.1–§2.1.4

<a id="EMC-STK-002"></a>
#### EMC-STK-002 · 20H 规则有争议，不当作强制规则
`consider` · 可信度 `medium` · 适用: multilayer, power-plane · 标签: cat-feeder

**规则** 不要把「电源平面缩进地平面 20H」作为必选项；只有在电源平面夹在两个地层之间、边沿 < 1 ns 的高速板上，且不影响过孔和供电连续性时，才考虑缩进，实用缩进量 0.5–1 mm，四周均匀。两层板没有电源平面，本规则不适用。

**依据** 20H 的出发点是让边缘的边沿场被包住（H 为电源—地层间距）。Shim 和 Hubing 在两块 7"×9" 板上实测并建模，结论是近场虽更集中，但实现 20H 的板在谐振频率处辐射略高（模型约高 2–3 dB，实测峰值相差不到 1 dB，估算 TM10 模式约 +3.6 dB）。板厂文章称 20H 约保留 70% 边缘场、100H 约 98%，但均无实测依据，并承认只在特定条件下有效。

| 参数 | 判据 | 备注 |
|---|---|---|
| `power_plane_setback_practical` | 0.5 … 1 mm | PCBWay 文章的折衷建议：电源平面比地平面各边缩进约 0.5–1 mm；非来自测量 |
| `setback_20h_for_1p6mm_two_layer` | == 32 mm | 20 × 1.6 mm 的换算；说明 20H 在常见层距下并不现实 |

**验证**
- `em_sim`（partial）· openEMS / 腔体模型，对比有无缩进的板辐射功率 — 对 TM10/TM01 谐振频率附近的辐射功率做对比；若缩进后更高则不采用
- `emc_precompliance`（manual）· 近场探头 / 暗室 — A/B 两版实测，同一 RBW 比较谐振频点峰值

**来源分歧** 支持方：Montrose 的书与多家板厂文章（PCBWay 等）称 20H 能把约 70% 边缘电场约束在板内；反对方：Clemson/Missouri-Rolla 的 Shim & Hubing 论文用测试板和 EMAP5 数值模型得出 20H 不降低辐射反而略升。取舍：以有实测数据的论文为准，将 20H 降为 consider；板边辐射改用地环 + 缝合过孔和让快速信号远离板边处理。

**来源**
- [20-H Rule Modeling and Measurements (Shim, Hubing)](https://cecas.clemson.edu/cvel/pdf/EMCS01-939.pdf) — Clemson CVEL / University of Missouri-Rolla, paper
- [Why Should Power Planes Be Smaller Than Ground Planes in PCB Design?](https://www.pcbway.com/blog/PCB_Design_Layout/Why_Should_Power_Planes_Be_Smaller_Than_Ground_Planes_in_PCB_Design_351dcc7f.html) — PCBWay, blog

## 分区规划（floorplan）

<a id="EMC-FLR-003"></a>
#### EMC-FLR-003 · 连接器到 TVS 之间划 ESD 入口禁布区
`must` · 可信度 `high` · 适用: tvs, connector · 标签: cat-feeder

**规则** 从连接器引脚到 TVS 这段是 ESD 电流和辐射最强的区域，当作禁布区：禁止布入未受保护的走线或器件，已受保护的线也不要与未受保护线并行相邻；过孔穿过的各层同理。

**依据** ESD 在这段产生很大的 dI/dt，会辐射并感应到邻近走线，感应电流若进入没有 TVS 的线路可直接损坏器件或把干扰带进内部。

**验证**
- `geometry_script`（full）· pcbnew Python — 取每个连接器引脚焊盘到对应 TVS 焊盘之间的走线包络，向外扩 2 mm（2 mm 为经验值，来源未给）；包络内不得出现不属于该受保护网络的铜（走线、过孔、焊盘），否则报错
- `drc`（partial）· KiCad 自定义规则 (.kicad_dru)，intersectsArea() 条件 — 为每个 ESD 入口绘制规则区，写 (rule ... (constraint disallow track via) (condition "A.intersectsArea('esd_zone')")) 并对非受保护网络生效

**来源**
- [ESD Protection Layout Guide (SLVA680A)](https://www.ti.com/lit/pdf/slva680) — Texas Instruments, app_note, §2.2
- [ESD Packaging and Layout Guide (SLVAEX9B)](https://www.ti.com/lit/pdf/slvaex9) — Texas Instruments, app_note, §2.2
- [Board design considerations for TVS diodes (ESD protection diodes)](https://toshiba.semicon-storage.com/ap-en/semiconductor/knowledge/faq/diode_tvs-diodes/board-design-considerations-for-tvs-diodes-esd-protection-diodes.html) — Toshiba, vendor_guide

<a id="EMC-FLR-001"></a>
#### EMC-FLR-001 · 按功能分区，高速逻辑靠电源入口，模拟远离
`should` · 可信度 `high` · 适用: mcu-board · 标签: cat-feeder

**规则** 把同类功能放在一起：高速逻辑与 MCU 靠近电源入口/稳压器，慢速器件次之，模拟电路最远；振荡器环路远离模拟、低速信号和连接器；成品里不要让线束折叠到振荡器或 MCU 上方。

**依据** 这样高速逻辑污染其他信号线的机会最小；线缆会把拾取到的噪声带到别处。

**验证**
- `geometry_script`（partial）· pcbnew Python — 分别量 MCU/时钟、模拟采样（INA199、ADC 输入）、连接器之间的质心距离与路径，输出分区报告供评审
- `review`（manual）· 布局评审 — 高速、慢速、模拟、I/O 各占一个连续区域且 I/O 不穿过高速区

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.3, Figure 10

<a id="EMC-FLR-002"></a>
#### EMC-FLR-002 · 连接器集中在板边一侧，ESD 敏感电路放中央
`should` · 可信度 `high` · 适用: connector, high-speed, esd · 标签: cat-feeder

**规则** 把所有连接器和外接线放在 PCB 同一条边（或同一区域）；ESD 敏感电路放在板中央，远离板边、外接线、连接器和电源入口；噪声线、快速线不要布在板外缘。

**依据** 外部线缆是主要的辐射天线和 ESD 入口，集中放置让保护与滤波集中在一处；板边的走线更容易辐射，也离放电点更近。

**验证**
- `geometry_script`（partial）· pcbnew Python — 求所有连接器焊盘的外接矩形与它们所在板边；要求连接器分布在 ≤ 2 条相邻板边；列出距板边最近的 MCU/ADC 焊盘及其距离；记录所有时钟/PWM 网络走线到 Edge.Cuts 的最小距离

**来源**
- [High-Speed Layout Guidelines for Reducing EMI for LVDS SerDes Designs (SNLA302)](https://www.ti.com/lit/pdf/snla302) — Texas Instruments, app_note, §2, §3
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.4.1

<a id="EMC-FLR-004"></a>
#### EMC-FLR-004 · 电机/继电器/驱动区与 MCU 和模拟采样区分开
`should` · 可信度 `medium` · 适用: motor, relay, h-bridge, shunt-amplifier · 标签: cat-feeder

**规则** 把电机驱动、继电器及其驱动器、电机接口放在板的一个区域，与 MCU、复位、晶振和电流检测放大器（INA199 一类）等敏感电路分开，大电流地与数字地分开走到单点；非噪声线远离继电器、继电器驱动器和连接器；电机引线走线短而粗，远离逻辑线。

**依据** 电机驱动的开关电流、电刷电弧噪声和续流尖峰都经公共阻抗和空间耦合进入逻辑与采样电路；SZZA009 要求把高功率地与数字地隔离，并让非噪声线远离继电器及其驱动器。

**验证**
- `geometry_script`（partial）· pcbnew Python — 计算电机驱动网络铜（开关节点、电机输出、VM）与 MCU/INA199 输入/EN/晶振网络之间的最小距离及并行长度，输出供评审；任何敏感网络与开关节点并行长度大于 10 mm 的标红（10 mm 为经验阈值）
- `bench`（manual）· 示波器 — 电机启停/堵转时观察 INA199 输出和 ADC 读数是否被噪声污染

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.1.5, §2.4.1
- [Dealing with Motor Noise (Pololu, §9)](https://www.pololu.com/docs/0J15/9) — Pololu, vendor_guide

<a id="EMC-FLR-005"></a>
#### EMC-FLR-005 · MCU 靠稳压器，稳压器靠供电入口，地在三者间单点参考
`should` · 可信度 `medium` · 适用: mcu-board · 标签: cat-feeder

**规则** MCU 紧挨稳压器，稳压器紧挨电源入口，三者之间用宽地铜或整片地连成一个参考点，屏蔽/机壳也接在这个点；高速或大面积数字区仍用连续地平面，不为单点而拆分。

**依据** 单点参考让 RF 电流只在最短路径上流动，避免多点菊花链产生的公共阻抗耦合；SZZA009 称最佳方案是一个把稳压器地、MCU 地、电池负极和机壳/屏蔽连在一起的单点。

**验证**
- `geometry_script`（partial）· pcbnew Python — 计算电源入口连接器、稳压器、MCU 之间的直线距离与铜连接宽度；输出并要求这三者的路径总长最短且连接宽度符合长宽比 ≤ 3

**来源分歧** SZZA009 面向低频微控制器板，建议对产生 RF 的器件用单点、其余用多点；SLLA284 与 SNLA302 面向高速接口，要求连续实心的地/电源平面且不要切割。取舍：在连续地平面（或栅格地）上，用器件摆放的顺序（电源入口 → 稳压器 → MCU）形成事实上的参考点，不靠切割地线实现单点。

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.2.1, §2.2.2, §2.3, §3.2
- [Digital Isolator Design Guide (SLLA284)](https://www.ti.com/lit/pdf/slla284) — Texas Instruments, app_note, §4.2, §4.6

<a id="EMC-FLR-006"></a>
#### EMC-FLR-006 · 线缆屏蔽层 360° 端接到壳体，禁用长辫子
`consider` · 可信度 `low` · 适用: shielded-cable, connector

**规则** 带屏蔽层的线缆，屏蔽层沿圆周 360° 端接到连接器金属壳/机壳，而不是用长辫子（pigtail）接到 PCB 地；确需辫子时尽量短并记录。屏蔽应当像一块断点最少、阻抗最小的 RF 导电面。

**依据** 辫子带来额外电感，使屏蔽层的转移阻抗在高频升高。搜索结果中的二手资料给出的量级：25 mm 辫子约 25 nH，而 360° 端接小于 1 nH；In Compliance 一文称即便 5 mm 辫子在 1 MHz–1 GHz 也比 360° 端接差 10–20 dB（本次未能打开原文，数值仅供参考）。

**验证**
- `review`（manual）· 机械/线束评审 — 屏蔽线缆的端接图纸为 360° 压接或背壳，而非单根引出线
- `emc_precompliance`（manual）· 电流探头 + 近场探头 — 比较屏蔽层端接前后线缆共模电流谱

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §3.2
- [Getting the Best EMC from Shielded Cables Up to 2.8 GHz, Part 1](https://incompliancemag.com/getting-the-best-emc-from-shielded-cables-up-to-2-8-ghz-part-1/) — In Compliance Magazine, blog

## 器件布局（placement）

<a id="EMC-PLC-001"></a>
#### EMC-PLC-001 · TVS 紧靠连接器引脚，被保护 IC 远离 TVS
`must` · 可信度 `high` · 适用: tvs, esd-diode, connector · 标签: cat-feeder

**规则** TVS 放在设计规则允许的离连接器最近处，被保护 IC 离 TVS 的距离要明显大于 TVS 离连接器的距离，使 L4（TVS 到 IC）远大于 L1（连接器到 TVS），ESD 电流被「导向」TVS。

**依据** 在 8 kV 接触放电下 dI/dt 约 4×10^10 A/s，0.25 nH 就产生约 10 V；布局电感把钳位变成摆设：ROHM 仿真中连接器到二极管 52 nH、到 IC 91 nH 的错误布局使首峰 3.4 kV 完全没被钳位，改为 1 nH 后首峰降到 107 V。Toshiba 称放在连接器附近比放在 IC 附近可使首峰钳位电压低近 10 V。

| 参数 | 判据 | 备注 |
|---|---|---|
| `tvs_to_connector_pin_distance` | minimize | SLVA680：尽量近，来源未给距离；AtlasPCB 博客称 10 mm 内（低可信度，单一来源） |
| `tvs_to_ic_distance_vs_tvs_to_connector` | > 1 ratio | 被保护 IC 到 TVS 的路径长度应大于 TVS 到连接器的路径长度（L4 >> L1） |

**验证**
- `geometry_script`（full）· pcbnew Python — 对每个 ESD 保护网络：测连接器焊盘→TVS 信号焊盘的走线路径长度 d1，TVS 信号焊盘→被保护 IC 引脚的路径长度 d4，要求 d4 > d1，并输出 d1（越短越好，建议 d1 ≤ 10 mm 作评审阈值，该阈值为经验值）
- `spice`（partial）· ngspice，见 EMC-VER-003 — 把 d1、d4 换算成电感后仿真首峰电压

**来源**
- [ESD Protection Layout Guide (SLVA680A)](https://www.ti.com/lit/pdf/slva680) — Texas Instruments, app_note, §2.1
- [PCB Layout for TVS Diodes (No.66AN067E)](https://fscdn.rohm.com/en/products/databook/applinote/discrete/diodes/pcb_layout_for_tvs_diodes_an-e.pdf) — ROHM, app_note
- [Board design considerations for TVS diodes (ESD protection diodes)](https://toshiba.semicon-storage.com/ap-en/semiconductor/knowledge/faq/diode_tvs-diodes/board-design-considerations-for-tvs-diodes-esd-protection-diodes.html) — Toshiba, vendor_guide
- [PCB ESD Protection Design - AtlasPCB](https://www.atlaspcb.com/blog/pcb-esd-protection-tvs-guard-ring-layout/) — AtlasPCB, blog

<a id="EMC-PLC-002"></a>
#### EMC-PLC-002 · 阻尼电阻贴驱动脚，I/O 旁路电容贴连接器
`should` · 可信度 `high` · 适用: mcu, connector, filter · 标签: cat-feeder

**规则** 串联阻尼电阻及其 RC/LC 滤波件放在驱动（噪声源）引脚旁；到机壳/屏蔽地的 I/O 旁路电容和共模滤波件放在连接器处，噪声先被滤掉再进入板内。

**依据** 噪声源侧的电阻让整条走线处于被阻尼的一侧；连接器处的旁路电容则让线缆拾取的噪声和板内传出的噪声在入口就被引到机壳，不在板上形成长环路。

| 参数 | 判据 | 备注 |
|---|---|---|
| `series_damping_r_to_driver_pin_distance` | minimize | SZZA009：电阻尽量靠近微控制器；Espressif：RC/LC 靠近芯片或模块引脚。来源未给毫米阈值 |

**验证**
- `geometry_script`（partial）· pcbnew Python — 对 EMC-SCH-001 找到的串联 R，量其与 MCU 引脚焊盘的距离；对 EMC-SCH-006 的 I/O 电容，量其与连接器焊盘的距离，并列出最远者

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.2.5, §3.3
- [ESP32-C3 Hardware Design Guidelines - Schematic Checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, SPI

<a id="EMC-PLC-003"></a>
#### EMC-PLC-003 · 去耦电容贴电源脚，回路面积最小
`should` · 可信度 `high` · 适用: decoupling, mcu, ic-supply · 标签: cat-feeder

**规则** 去耦电容放在被供电的 IC 引脚旁，电容—电源脚—地脚构成的回路面积最小；电容的电源端直接连到电源脚，地端用不少于两个过孔（有平面时）或短而宽的地铜接地；去耦回路走线长宽比不超过 3:1；用 SMD 电容。

**依据** IC 开关电流应由本地电容供给，回路电感越小，高频电流越不会向电源走线上跑；带引线电容约 80 MHz 即自谐振，之后呈感性。

| 参数 | 判据 | 备注 |
|---|---|---|
| `decoupling_trace_length_to_width` | <= 3 ratio | SZZA009 §2.2.4：旁路回路走线的长宽比 |
| `decoupling_cap_ground_vias` | >= 2 count | TI SLLA284 §4.6：地端经两个过孔接地平面（用于有平面的板；两层板用短而宽的地铜代替） |

**验证**
- `geometry_script`（full）· pcbnew Python — 对每个电源引脚找最近的去耦电容，量电容电源焊盘—电源脚、电容地焊盘—地脚（或最近地过孔）的距离，并估算回路面积；回路面积最小排序，最差 3 个输出供评审；检查连接走线长宽比 ≤ 3
- `pi_sim`（partial）· PDN 阻抗仿真（如 openEMS / 解析模型） — 在 10–500 MHz 检查 IC 处 PDN 阻抗，包含电容 ESL 和过孔电感

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §1.2, §2.2.4
- [Digital Isolator Design Guide (SLLA284)](https://www.ti.com/lit/pdf/slla284) — Texas Instruments, app_note, §4.6 item 10
- [ESP32-C3 Hardware Design Guidelines - PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, Decoupling Capacitors

<a id="EMC-PLC-004"></a>
#### EMC-PLC-004 · 电机抑制电容和续流件贴电机/感性负载
`should` · 可信度 `medium` · 适用: brushed-dc-motor, relay, solenoid · 标签: cat-feeder

**规则** 电机的跨端子电容和对外壳电容焊在电机壳体上（越近越好）；PCB 上若还有一组，放在电机连接器焊盘旁；续流二极管物理上尽量靠近被开关的感性负载。

**依据** 电刷电弧噪声在电机壳体处产生，电容离电机越近越能在噪声进入引线前将其旁路；二极管靠近电感可缩小流过高压尖峰的电路范围、降低辐射。

| 参数 | 判据 | 备注 |
|---|---|---|
| `motor_cap_to_motor_distance` | minimize | Pololu：尽量靠近电机壳体；PMD：尽量靠近电机；来源未给毫米数 |

**验证**
- `review`（manual）· 装配图/线束图评审 — 电机壳上的电容在线束图中有明确焊接位置和尺寸；PCB 上有对应预留焊盘
- `geometry_script`（partial）· pcbnew Python — 续流二极管焊盘到被钳位线圈/电机连接器焊盘的距离，输出并列最远者

**来源**
- [Dealing with Motor Noise (Pololu, §9)](https://www.pololu.com/docs/0J15/9) — Pololu, vendor_guide
- [AB-005: EMC (EMI) for Vibe Motors](https://www.precisionmicrodrives.com/ab-005) — Precision Microdrives, app_note
- [Flyback diode](https://en.wikipedia.org/wiki/Flyback_diode) — Wikipedia, blog

## 布线（routing）

<a id="EMC-RTE-001"></a>
#### EMC-RTE-001 · 每条快速信号下方保持连续回流路径
`must` · 可信度 `high` · 适用: clock, pwm, spi, uart, switch-node · 标签: cat-feeder

**规则** 每条周期性或快边沿信号（时钟、PWM、SPI/UART、开关节点）都必须有紧贴其下方（或紧邻）的连续地回流路径，回路面积最小；两层板上让地铜或地走线紧贴信号走线。

**依据** 信号电流沿最低阻抗路径回到源头；信号与回流围成的环路就是天线，辐射随环路面积增大直到边长达到 1/4 波长。SZZA009 称在信号下方布置回流是减小环路面积最有效的办法，其中构造地栅格是布局规划之后最重要的事。

| 参数 | 判据 | 备注 |
|---|---|---|
| `signal_loop_area` | minimize | 来源未给阈值；以覆盖率和面积相对排序评估 |
| `quarter_wave_at_300mhz` | == 25 cm | SZZA009 §1.4.1：300 MHz 时 1/4 λ ≈ 25 cm（空气）；1 MHz 时 75 m |

**验证**
- `geometry_script`（full）· pcbnew Python — 沿每条目标走线按 0.5 mm 步进取样点，判断对层或同层 1 mm 内是否有地铜（填充区已填充）；输出无地覆盖长度占比及位置，快速网络目标 100% 覆盖
- `em_sim`（partial）· openEMS / Elmer，或 2.5D 环路电感提取 — 提取关键网络的环路电感，作为相对比较量

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §1.4, §1.4.1, §2.1.4
- [Digital Isolator Design Guide (SLLA284)](https://www.ti.com/lit/pdf/slla284) — Texas Instruments, app_note, §4.5, Figure 4-8

<a id="EMC-RTE-003"></a>
#### EMC-RTE-003 · ESD 入口走线直通 TVS，无 stub、无过孔、拐角 ≤45°
`must` · 可信度 `high` · 适用: tvs, esd, connector · 标签: cat-feeder

**规则** 受保护线从连接器直接走到 TVS 的保护引脚，不要有分叉（stub）；连接器到 TVS 之间不换层；必须换层时先经 TVS 再过孔；拐角用圆弧，做不到则不大于 45°。

**依据** stub 或过孔的电感与 TVS 钳位并联，使被保护 IC 吃掉主要电流并多出 L·dI/dt 的压降；90° 拐角在 8 kV 时电场极高（SLVA680 估计至少 7 kV，半径小于约 2.6 mm 会电离空气）并有更强的串扰耦合。

| 参数 | 判据 | 备注 |
|---|---|---|
| `tvs_path_corner_angle` | <= 45 deg | SLVA680 §2.2：圆弧优先，最大 45° |
| `tvs_stub_length` | == 0 mm | SLVA680 §2.1：L2 stub 不应存在 |
| `vias_between_connector_and_tvs` | == 0 count | SLVA680 §2.3：尽量无过孔；必须有时 TVS 先接，过孔后置（Case 1 最佳，Case 3 可接受，Case 2 应避免） |

**验证**
- `geometry_script`（full）· pcbnew Python — 对每个 ESD 保护网络建走线连通图：连接器焊盘到 TVS 信号焊盘之间过孔数 = 0；该路径上除 TVS 外没有其他分支；各线段拐角 ≤ 45°

**来源**
- [ESD Protection Layout Guide (SLVA680A)](https://www.ti.com/lit/pdf/slva680) — Texas Instruments, app_note, §2.1–§2.3
- [ESD Packaging and Layout Guide (SLVAEX9B)](https://www.ti.com/lit/pdf/slvaex9) — Texas Instruments, app_note, §2.1–§2.3
- [Board design considerations for TVS diodes (ESD protection diodes)](https://toshiba.semicon-storage.com/ap-en/semiconductor/knowledge/faq/diode_tvs-diodes/board-design-considerations-for-tvs-diodes-esd-protection-diodes.html) — Toshiba, vendor_guide

<a id="EMC-RTE-004"></a>
#### EMC-RTE-004 · TVS 地脚接同层地铺铜，紧邻过孔缝合到相邻地层
`must` · 可信度 `high` · 适用: tvs, esd-diode, two-layer · 标签: cat-feeder

**规则** TVS 的地脚直接接到同层地铺铜，并在紧邻地脚处打过孔与相邻地层缝合（有多个地层时尽量都连）；过孔孔径和焊盘取大；地平面在该过孔附近不得被割断；被保护 IC 的接地不依赖长的地细线。连接到大地的机壳螺丝柱尽量靠近 TVS 地和连接器屏蔽。

**依据** 被保护节点的电压 VESD = VBR + IESD·RDYN + (L2+L3)·dIESD/dt，L3（TVS 到地）是最主要的寄生项；8 kV 时 dIESD/dt ≈ 4×10^10 A/s，0.25 nH 就产生 10 V。两层板没有内层地，可用顶层地铺铜与底层地铺铜用紧邻过孔缝合。阳极侧同样要求，地平面应优先位于二极管正下方。

| 参数 | 判据 | 备注 |
|---|---|---|
| `tvs_ground_via_adjacent_to_pad` | >= 1 count | SLVA680 §2.4：地脚旁紧邻 1 个缝合过孔，图 2-8 示例用 4 个；AtlasPCB（低可信度）建议每个 TVS 阵列至少 2 个 |
| `esd_overshoot_per_nh` | == 40 V/nH | 由 SLVA680 的 dI/dt = 30 A/0.8 ns ≈ 4×10^10 A/s 换算：每 1 nH 约 40 V |

**验证**
- `geometry_script`（full）· pcbnew Python — 对每个 TVS 的地焊盘，量到最近地过孔的距离（目标 ≤ 焊盘间距的 1 倍，经验值）并统计 2 mm 内地过孔数；检查该焊盘是否直接连入同层地铺铜而非走细线（走线宽度 ≥ 0.5 mm 或直接铺铜）
- `spice`（partial）· ngspice，L = 0.2·l·(ln(2l/(w+t)) + 0.2235·(w+t)/l + 0.5) nH（ROHM 公式，l、w、t 单位 mm） — 用该公式把地回路几何换成电感，代入 EMC-VER-003 的仿真，被保护引脚峰值须低于 Abs.Max

**来源**
- [ESD Protection Layout Guide (SLVA680A)](https://www.ti.com/lit/pdf/slva680) — Texas Instruments, app_note, §2.1, §2.4, Figure 2-8
- [ESD Packaging and Layout Guide (SLVAEX9B)](https://www.ti.com/lit/pdf/slvaex9) — Texas Instruments, app_note, §2.4
- [PCB Layout for TVS Diodes (No.66AN067E)](https://fscdn.rohm.com/en/products/databook/applinote/discrete/diodes/pcb_layout_for_tvs_diodes_an-e.pdf) — ROHM, app_note

<a id="EMC-RTE-002"></a>
#### EMC-RTE-002 · 不跨平面分割/槽走线，必须跨时加缝合电容
`should` · 可信度 `high` · 适用: multilayer, ground-plane, slot

**规则** 信号不要跨过地平面分割、槽或空洞；确实无法避免时，在跨越处尽量近的位置放不大于 1 µF 的缝合电容为高频电流提供回路。分割地平面时，连到 MCU 的信号必须完全位于数字地之上。

**依据** 跨分割会迫使高频回流绕过分割，面积增大，造成过量辐射、串扰和延时；长槽还会聚焦槽天线辐射。

| 参数 | 判据 | 备注 |
|---|---|---|
| `stitching_cap_max` | <= 1 uF | SNLA302 §3：1 µF 或更小，尽量靠近平面跨越处 |

**验证**
- `geometry_script`（full）· pcbnew Python — 对每条走线的各段，检查其正下方参考层是否被分割线/槽/反焊盘阵列切断；有则列出，并确认附近 ≤ 1 µF 缝合电容

**来源**
- [High-Speed Layout Guidelines for Reducing EMI for LVDS SerDes Designs (SNLA302)](https://www.ti.com/lit/pdf/snla302) — Texas Instruments, app_note, §3 Use a continuous ground plane
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.1.7

<a id="EMC-RTE-005"></a>
#### EMC-RTE-005 · 快沿/时钟走线要短，超过阈值要端接
`should` · 可信度 `high` · 适用: clock, fast-edge, two-layer · 标签: cat-feeder

**规则** 时钟和快边沿走线尽量短；两层板上的快沿信号走线超过约 100 mm（4 英寸）会成为调频波段的辐射问题；超过约 300 mm（1 英尺）、去往出机壳的线缆、或出现振铃时要端接，MCU 系统优先用串联端接。

**依据** 走线长度超过约 1/50 波长（消费/汽车两层板、无屏蔽）开始成为有效天线，FCC 限值下是 1/10 波长；串联端接功耗低、元件少，代价是增加延迟。CMOS 是欠阻尼的，必须防振铃与过冲。

| 参数 | 判据 | 备注 |
|---|---|---|
| `trace_length_fm_band_concern` | > 101.6 mm | SZZA009 §2.4.2：4 英寸以上的走线对 FM 波段噪声可能构成问题（两层、无屏蔽的汽车/消费应用，1/50 波长准则） |
| `trace_length_termination_required` | > 304.8 mm | SZZA009 §2.4.3：走线超过 1 英尺、去往出机壳线缆、或有任何振铃时用某种端接 |

**验证**
- `geometry_script`（full）· pcbnew Python — 量每条时钟/快沿网络的走线总长，超过 101.6 mm 报警，超过 304.8 mm 要求存在串联端接电阻（由 EMC-SCH-001 检查）
- `si_sim`（partial）· ngspice / IBIS — 看接收端振铃和过冲，确认端接后单调

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.4.2, §2.4.3

<a id="EMC-RTE-006"></a>
#### EMC-RTE-006 · ESD 路径和快沿线避免 90° 拐角（有条件）
`consider` · 可信度 `medium` · 适用: esd, fast-edge

**规则** 在 ESD 入口走线和边沿快的差分/时钟线上用 45° 或圆弧拐角；对低速、慢边沿的普通信号，不必为拐角牺牲布线空间。

**依据** SLVA680 的仿真显示 8 kV ESD 下 90° 拐角电场集中、串扰耦合在 ESD 频段明显高于 45°和圆弧；TI SNLA302 与 SLLA284 也推荐避免直角（辐射和阻抗不连续）。

**验证**
- `geometry_script`（full）· pcbnew Python — 对 ESD 入口网络和被标记为快沿的网络，列出所有拐角角度，> 45° 者报警；其他网络仅统计不判失败

**来源分歧** 「90° 一定有害」流传很广，但来源里的依据是 ESD 瞬态与吉赫兹级差分线；本研究未读到针对低速板的实测证据，常见的反面说法（慢边沿下影响可忽略）未经核实。取舍：只对 ESD 路径与快边沿线要求，其他情况降为参考。

**来源**
- [ESD Protection Layout Guide (SLVA680A)](https://www.ti.com/lit/pdf/slva680) — Texas Instruments, app_note, §2.2, Figure 2-3, Figure 2-4
- [High-Speed Layout Guidelines for Reducing EMI for LVDS SerDes Designs (SNLA302)](https://www.ti.com/lit/pdf/snla302) — Texas Instruments, app_note, §3
- [Digital Isolator Design Guide (SLLA284)](https://www.ti.com/lit/pdf/slla284) — Texas Instruments, app_note, §4.6 item 2

## 平面与铺铜（plane_pour）

<a id="EMC-PLN-001"></a>
#### EMC-PLN-001 · 两层板地铺铜栅格化，消除只有一端连接的地岛
`should` · 可信度 `high` · 适用: two-layer, ground-pour · 标签: cat-feeder

**规则** 两层板上尽量扩展地走线并铺满地铜，顶层与底层的地铜在走线交叉处用过孔连接；每块地铜至少两点接地，使其成为栅格中的导体而不是孤立的屏蔽片；不要出现仅一端连接的地走线或地岛。

**依据** 只在一点接地的铜皮只是屏蔽，不是回流导体；栅格化地让每条信号线下方都有回流，同时降低 MCU 到稳压器的阻抗。SZZA009 称这是两层板最关键的设计技巧，用到所能容纳的所有过孔。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ground_fill_connection_points` | >= 2 count | SZZA009 §2.2.3：地铜连接两点或以上才算栅格的一部分 |

**验证**
- `geometry_script`（full）· pcbnew Python（已填充的 zone 多边形） — 对每块地 zone 统计与其他地铜（经过孔/焊盘）的独立连接点数，少于 2 或为孤立岛者报错；DRC 另开「未连接铜皮」检查
- `drc`（full）· kicad-cli pcb drc — 确保 DRC 中不存在孤岛/未连接铜皮警告，或明确豁免

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.2.3, Figure 7, Figure 8

<a id="EMC-PLN-003"></a>
#### EMC-PLN-003 · 机壳/屏蔽地铜区：宽、短、至少两颗螺丝
`should` · 可信度 `high` · 适用: connector, chassis-ground, mounting-hole · 标签: cat-feeder

**规则** 在连接器附近做一块与屏蔽/机壳相连的大面积地铜，作为 I/O 旁路电容和 TVS 地的返回点；到机壳的连接用宽铜（长宽比 ≤ 3:1），并用至少两颗螺丝牢固接地；机壳接地螺丝尽量靠近 TVS 地脚和连接器屏蔽。

**依据** 噪声和 ESD 通过旁路电容到机壳再离开，路径阻抗越低，被保护 IC 处的地偏移越小；窄线会升高阻抗，使滤波失效。

| 参数 | 判据 | 备注 |
|---|---|---|
| `chassis_bonding_screws` | >= 2 count | SZZA009 §2.5.5：最好两颗或更多螺丝 |
| `chassis_connection_length_to_width` | <= 3 ratio | SZZA009 §2.5.5 / §3.3 |

**验证**
- `geometry_script`（partial）· pcbnew Python — 取与连接器屏蔽相连的地铜区，统计其中接地的安装孔数 ≥ 2（有机壳时），测最近安装孔到 TVS 地焊盘的距离并列出；测该铜区到主地的连接宽度与长度比 ≤ 3

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.5.4, §2.5.5, §3.3, Figure 13
- [ESD Protection Layout Guide (SLVA680A)](https://www.ti.com/lit/pdf/slva680) — Texas Instruments, app_note, §2.4, Figure 2-8

<a id="EMC-PLN-002"></a>
#### EMC-PLN-002 · 板边地环与缝合过孔间距小于 λ/20
`consider` · 可信度 `low` · 适用: board-edge, via-stitching

**规则** 需要抑制板边辐射或做过孔围栏时，缝合过孔间距小于最高关注频率波长的 1/20，槽与开孔的直径同样小于 λ/20；高速信号与噪声线不要靠近板边。

**依据** 间距接近 λ/2 的缝隙或槽就成为有效的槽天线；λ/20 是把缝隙「电气上看不见」的常用准则，FR-4 中 1 GHz 的 λ 约 18 cm，对应小于 9 mm。

| 参数 | 判据 | 备注 |
|---|---|---|
| `stitching_via_spacing_at_1ghz` | < 9 mm | ProtoExpress：1 GHz 时（FR-4 λ≈18 cm）应小于 9 mm；按自己最高关注频率重算 |

**验证**
- `geometry_script`（full）· pcbnew Python — 沿板边地环统计相邻缝合过孔的中心距，最大值 < λ/20（λ 按 f_max 与 εr 估算，f_max 由需求给定）
- `emc_precompliance`（manual）· 近场探头 — 沿板边扫描，有无地环两版对比

**来源分歧** AtlasPCB 博客给出的防护环参数（线宽 ≥ 0.5 mm、过孔间距 ≤ 5 mm、按 300 MHz ESD 频率）自身与 λ/20 换算不一致（300 MHz 的 λ/20 约 50 mm），仅作低可信度参考。板边处理与 20H 缩进（EMC-STK-002）的优劣在文献里也无定论。取舍：用 λ/20 作为间距上限，按需要取更密，并用近场对比验证收益。

**来源**
- [7 PCB Design Guidelines for EMI and EMC](https://www.protoexpress.com/blog/7-pcb-design-tips-solve-emi-emc-issues/) — Sierra Circuits / Proto Express, blog
- [PCB ESD Protection Design - AtlasPCB](https://www.atlaspcb.com/blog/pcb-esd-protection-tvs-guard-ring-layout/) — AtlasPCB, blog
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.4.1, §3.4

## 签核验证（verification）

<a id="EMC-VER-002"></a>
#### EMC-VER-002 · ESD 测试：金属壳打壳体接触放电，绝缘件打空气放电
`must` · 可信度 `high` · 适用: usb-c, button, connector, enclosure · 标签: cat-feeder

**规则** ESD 抗扰测试只打正常使用中人可触及的点和面；带金属壳的连接器接触放电只打壳体（不打引脚），塑料壳连接器的引脚只做空气放电；每个选定点在最敏感极性下至少 10 次单次放电，间隔初值 1 s；空气放电要覆盖到规定等级以下的所有等级，接触放电只打规定等级。

**依据** IEC 61000-4-2 §8.3.2 明确了可触及点、排除项和 Table 4 的六种连接器情形；放电电流因此首先进入壳体，再经 PCB 地到各器件，所以壳体到地路径的阻抗决定通过与否。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esd_discharges_per_point` | >= 10 count | §8.3.2：每个预选点在最敏感极性下至少 10 次单次放电；同步电路更多 |
| `esd_interval_between_discharges` | >= 1 s | §8.3.2：推荐初值 1 s，必要时更长以判定系统失效 |

**验证**
- `bench`（manual）· ESD 枪（IEC 61000-4-2）+ 水平/垂直耦合板 — 按测试计划打：USB-C 金属壳（接触）、塑料件缝隙与按键（空气）；记录每点结果、是否复位、是否通信中断、是否自动恢复
- `emc_precompliance`（manual）· 小型 ESD 笔/枪 + 示波器探 EN、3V3、USB — 开发阶段先用较低电平（2–4 kV）摸底，找出薄弱点后再提高

**来源**
- [IEC 61000-4-2 Ed.2.0 (2008) ESD immunity test](https://www.itu.int/en/ITU-D/Technology/Documents/Events2016/CI_Training_ARB_Tunis_April16/Session8/IEC_61000-4-2_2008.pdf) — IEC (copy hosted by ITU), standard, §5, §8.3.2, Table 4

<a id="EMC-VER-001"></a>
#### EMC-VER-001 · 用 LISN 做传导发射预兼容，两根线分别扫
`should` · 可信度 `medium` · 适用: dc-input, switching-regulator, brushed-motor · 标签: cat-feeder

**规则** 传导发射预兼容必须通过 LISN 测量，LISN 串在电源与被测板之间；分别扫 Line1 和 Line2 取较差者；用电池作安静的电源并串联保险丝，LISN 接频谱仪的 50 Ω 输入，切换通道或电源开关前先拆下频谱仪输入。

**依据** LISN 提供一致的源阻抗和测量阻抗，使结果可重复；它同时用隔直电容保护频谱仪，但开关切换的阶跃会通过隔直电容耦合到输入端，可能损坏频谱仪。电池是低阻源，必须串保险丝防火。

| 参数 | 判据 | 备注 |
|---|---|---|
| `conducted_measurement_span` | 0.01 … 30 MHz | TI AN-2162：监管测试的测量频率范围为 10 kHz 至 30 MHz（具体起点以适用标准为准） |
| `lisn_blocking_capacitor` | == 0.1 uF | AN-2162 所述 LISN 的隔直电容 |

**验证**
- `emc_precompliance`（manual）· DC LISN + 频谱仪 + 电池电源 + 保险丝 — 分别扫 Line1/Line2，记录准峰值与平均值曲线，与目标限值（见适用产品标准）比较；电机运行（启动、稳态、堵转）各扫一次

**来源**
- [AN-2162 Simple Success With Conducted EMI From DC-DC Converters (SNVA489C)](https://www.ti.com/lit/pdf/snva489) — Texas Instruments, app_note, §6 LISN, §7

<a id="EMC-VER-003"></a>
#### EMC-VER-003 · ESD 仿真：IEC 枪模型 + TVS + 寄生电感估算 VESD
`should` · 可信度 `high` · 适用: tvs, esd, spice · 标签: cat-feeder

**规则** 布局完成后用 SPICE 仿真：IEC 61000-4-2 枪模型（150 pF / 330 Ω，8 kV）+ TVS 模型 + 由几何换算的寄生电感，读被保护引脚首峰电压并要求低于其 Abs.Max；寄生电感按 L = 0.2·l·(ln(2l/(w+t)) + 0.2235·(w+t)/l + 0.5) nH（l、w、t 单位 mm）估算。

**依据** 首峰电压由 VBR、动态电阻和 L·dI/dt 决定，布局电感往往比器件本身更重要。ROHM 的仿真里 52 nH + 91 nH 的错误布局首峰 3.4 kV，TVS 完全没起作用；寄生电感降到 1 nH 后首峰降到 107 V。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esd_gun_series_resistance` | == 330 ohm | IEC 61000-4-2 Table 2 注 3 |
| `esd_gun_storage_capacitance` | == 150 pF | IEC 61000-4-2 Table 2 注 2 |
| `rohm_example_bad_layout_peak` | == 3400 V | ROHM 仿真：连接器—二极管 52 nH、连接器—IC 91 nH，首峰约 3.4 kV，二极管未钳位 |
| `rohm_example_good_layout_peak` | == 107 V | ROHM 仿真：寄生电感 1 nH，首峰约 107 V；该值取决于所用 TVS 型号 |

**验证**
- `spice`（partial）· ngspice / LTspice + 厂商 TVS SPICE 模型 — 电压源 8 kV 经 330 Ω、150 pF 接到连接器节点；在连接器→TVS→IC 的路径上串入几何换算的电感；输出 IC 引脚电压峰值，要求 < Abs.Max，并要求仿真首峰电流与 30 A / 0.8 ns 校准波形一致

**来源**
- [PCB Layout for TVS Diodes (No.66AN067E)](https://fscdn.rohm.com/en/products/databook/applinote/discrete/diodes/pcb_layout_for_tvs_diodes_an-e.pdf) — ROHM, app_note, Eq.(1)–(2), Figures 4–10
- [ESD Protection Layout Guide (SLVA680A)](https://www.ti.com/lit/pdf/slva680) — Texas Instruments, app_note, §2.1
- [IEC 61000-4-2 Ed.2.0 (2008) ESD immunity test](https://www.itu.int/en/ITU-D/Technology/Documents/Events2016/CI_Training_ARB_Tunis_April16/Session8/IEC_61000-4-2_2008.pdf) — IEC (copy hosted by ITU), standard, Table 2, Table 3

<a id="EMC-VER-004"></a>
#### EMC-VER-004 · EFT 抗扰测试：双极性、每端口不少于 1 分钟
`should` · 可信度 `high` · 适用: power-port, signal-port

**规则** EFT/burst 抗扰测试要有测试计划，写明测试类型、等级、耦合方式、极性（两种极性都要）、每端口的测试时长（不少于 1 min，且不少于被测设备被充分运行并作出响应所需的时间）、重复频率（5 kHz 或 100 kHz）和被测端口。

**依据** 脉冲波形为 5 ns 上升、50 ns 宽度（50 Ω 负载），突发为 5 kHz 时 15 ms、100 kHz 时 0.75 ms，周期 300 ms；能量低但上升快、重复率高，典型失效是复位、通信误码，而不是器件损坏。

| 参数 | 判据 | 备注 |
|---|---|---|
| `eft_test_duration_per_port` | >= 1 min | IEC 61000-4-4 §8.3 |
| `eft_burst_duration_5khz` | == 15 ms | ±3 ms；100 kHz 时 0.75 ms ±0.15 ms；突发周期 300 ms ±60 ms；脉冲上升 5 ns ±1.5 ns，宽度 50 ns ±15 ns（50 Ω 负载） |

**验证**
- `bench`（manual）· EFT 发生器 + 容性耦合夹（信号线）/ CDN（电源） — 对电源口和信号线分别打；开发阶段在电机运行状态下重复，观察复位、掉线、ADC 异常

**来源**
- [IEC 61000-4-4 Ed.3.0 (2012) Electrical fast transient/burst immunity test](https://www.itu.int/en/ITU-D/Technology/Documents/Events2016/CI_Training_ARB_Tunis_April16/Session8/IEC_61000-4-4_2012.pdf) — IEC (copy hosted by ITU), standard, §6.2, §8.3

<a id="EMC-VER-005"></a>
#### EMC-VER-005 · 电机启停/堵转时在板上抓供电、EN 和采样
`should` · 可信度 `medium` · 适用: brushed-dc-motor, esp32-c3, shunt-amplifier · 标签: cat-feeder

**规则** 电机启动、稳态、堵转、反转（含软件触发的反转清堵）时，用示波器同时抓 5 V 输入、3V3、CHIP_EN、电机端子和 INA199 输出，验证无欠压复位、EN 毛刺不进入复位区、采样噪声在软件滤波能力内；整套波形作为回归基线。

**依据** 刷式电机的电刷换向、PWM 和堵转电流使供电和地出现 L·dI/dt 尖峰；SZZA009 指出最敏感的是复位、晶振和中断类脚，而 Espressif 明确 EN 线短才能避免外部干扰引起重启。这些问题在 EFT/ESD 认证前可以先用本测试暴露。

| 参数 | 判据 | 备注 |
|---|---|---|
| `chip_en_low_level_max` | <= 0.825 V | Espressif：VIL_nRST 上限 0.25×VDD（3.3 V 时 0.825 V）；毛刺的最低值须不低于此，否则可能触发复位 |

**验证**
- `bench`（manual）· 示波器（≥ 4 通道，≥ 200 MHz，带宽不要限到 20 MHz 以免漏掉高频尖峰） — 每种电机工况抓 20 次以上；记录 3V3 最低值（须高于模组最低工作电压）、EN 最小值、MCU 复位计数（读 reset reason），全部无异常

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.6.2
- [ESP32-C3 Hardware Design Guidelines - Schematic Checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, Chip Power-up and Reset Timing
- [Electric Fast Transient (EFT) Application Note](https://www.maxlinear.com/appnote/electric%20fast%20transient%20application%20note_301anr00.pdf) — MaxLinear, app_note

<a id="EMC-VER-006"></a>
#### EMC-VER-006 · 样机阶段逐个拆装滤波件，只保留有实测收益的
`consider` · 可信度 `medium` · 适用: filter, prototype, emc-tuning · 标签: cat-feeder

**规则** 首批样机上，把 I/O 滤波电阻、电容、磁珠逐个拆掉或加回，在近场/预兼容环境下记录每个件对发射的贡献；量产只保留有实测收益的元件，其余改为不贴（DNP），并保留焊盘便于后续整改。

**依据** SZZA009 指出这些规则会增加元件和占板面积，量产常不被接受；在屏蔽室里花一两小时逐个移除滤波件，就能确定哪些必需。Espressif 也建议为 SPI、USB 预留 0 Ω 与 RC 位置，初始不贴。

**验证**
- `emc_precompliance`（manual）· 近场探头 + 频谱仪（或暗室） — 表格记录：元件位号、拆除后各问题频点的变化量（dB）；决定保留/DNP，保留的写出收益
- `bom_check`（partial）· BOM 变体管理 — DNP 元件在 BOM 与装配文件中的状态一致，焊盘保留

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.2.5
- [ESP32-C3 Hardware Design Guidelines - Schematic Checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, SPI; USB

