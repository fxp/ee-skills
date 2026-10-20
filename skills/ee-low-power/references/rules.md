# 低功耗 / 电池（low_power）— 规则全文

垂直领域 · 40 条规则 · 由 `catalog/*.yaml` 生成，请改 YAML 不要改本文件。用 `grep -n "<规则ID>" rules.md` 定位单条，不要整份读。

环节分布：架构与选型 13，符号封装库 1，原理图 14，网表与约束 1，器件布局 1，布线 2，出图与制造 2，签核验证 6

## 架构与选型（architecture）

<a id="LPW-ARC-012"></a>
#### LPW-ARC-012 · 无线突发电流下电源内阻不能把电压拉到下限以下
`must` · 可信度 `high` · 适用: esp32-c3, wifi, ble, battery, ldo · 标签: cat-feeder

**规则** 对每个电源（电池、LDO、5 V 输入）校核 V_open − I_peak × (R_int + R_path) − ΔV_ripple ≥ V_min。ESP32-C3 要求外部电源在 3.0–3.6 V 下至少能给 500 mA，Wi-Fi TX 峰值 276–335 mA，TX 时纹波峰值应小于 80 mV（802.11n MCS7）或 120 mV（11 Mbps）。CR2032 一类高内阻电池不能直接给 Wi-Fi 射频供电。

**依据** 电池内阻（随放电快速上升，TI 测得 30 mA 峰值时可承受的内阻上限约 30 Ω）乘以射频电流就是压降。电压掉到 3.0 V 以下会触发复位或掉电，电源纹波还会直接恶化 TX 性能。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esp32c3_external_supply_current_min` | >= 500 mA | 原理图检查表 Power Supply；模块数据手册表 6-2 IVDD 最小值 0.5 A |
| `esp32c3_supply_voltage_range` | 3.0 … 3.6 V | 数据手册表 5-2 |
| `esp32c3_wifi_tx_peak_current` | == 335 mA | 表 5-7：802.11b 1 Mbps @21 dBm 峰值，100% 占空；MCS7 为 276 mA |
| `tx_ripple_peak_mcs7` | < 80 mV | 802.11n MCS7 发射时 |
| `tx_ripple_peak_11mbps` | < 120 mV | 11 Mbps 发射时 |
| `coin_cell_internal_resistance_limit_30mA_peak` | <= 30 ohm | SWRA349：30 mA 峰值负载下电路能承受的电池内阻上限约 30 Ω（15 mA 约 60 Ω），属 BLE 级别负载，Wi-Fi 的 300 mA 级峰值远超此范围 |

**验证**
- `spice`（partial）· ngspice/LTspice：电池（V_open + R_int）+ 路径电阻 + 去耦电容 + 突发电流源（TX 脉冲波形） — 最坏情况（低温、老化高内阻、低电量）下负载端电压最小值 ≥ 3.0 V，TX 期间纹波峰值满足上表；电容复充时间小于睡眠间隔
- `bom_check`（full）· Python — R_int_max × I_peak < V_open_min − V_min，其中 R_int 取电池寿命末期值；LDO 取其最大输出电流（AMS1117 限流 900–1500 mA）是否 ≥ 500 mA

**来源**
- [Schematic Checklist - ESP32-C3 - ESP Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, Power Supply
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, Tables 5-2, 5-7
- [ESP32-C3-WROOM-02 Datasheet](https://documentation.espressif.com/esp32-c3-wroom-02_datasheet_en.pdf) — Espressif, datasheet, Table 6-2 Recommended Operating Conditions
- [ESP32-C3 Wireless Adventure: Guidelines for Power Supply Design](https://espressif.github.io/esp32-c3-book-en/chapter_5/5.3/5.3.5.html) — Espressif, vendor_guide
- [SWRA349 Coin cells and peak current draw](https://www.ti.com/lit/wp/swra349/swra349.pdf) — Texas Instruments, app_note, §3 Testing peak currents

<a id="LPW-ARC-001"></a>
#### LPW-ARC-001 · 先建立分状态的平均电流与电荷预算
`should` · 可信度 `high` · 适用: battery, iot, duty-cycled · 标签: cat-feeder

**规则** 选型前把整机拆成状态（深睡、唤醒启动、传感、无线 TX/RX、电机等），用 I_avg = Σ(I_state × t_state) / T 计算平均电流和每周期电荷，并找出占比最大的状态；占空比极低时，睡眠态电荷往往超过发射态。

**依据** 电池寿命取决于电荷的时间积分而不是峰值电流。TI 案例里 6 小时一次、10 µA 的测量期，其电荷是 250 mA × 0.4 s 发射期的两倍以上，所以优化重点在待机而不是峰值。

| 参数 | 判据 | 备注 |
|---|---|---|
| `standby_to_tx_charge_ratio_case_study` | > 2 ratio | SLVAER8A 案例：10 µA × 21600 s 与 250 mA × 0.4 s 两段的输入电荷比约 2.16；只是示例，不是阈值 |

**验证**
- `bom_check`（partial）· Python 或电子表格能量预算脚本（输入：每个状态的电流、时长、每日事件数；输出：I_avg、各状态电荷占比、电池寿命） — Q_cycle = Σ I_state × t_state；I_avg = Q_cycle / T；寿命 = 修正后电池容量 / I_avg。列出电荷占比 > 20% 的状态逐个审查，占比数值是评审用的经验线，不是出处数值
- `bench`（partial）· Joulescope JS220 / Nordic PPK2 / Qoitech Otii，覆盖完整占空周期 — 实测一个完整周期的累计电荷，与模型对比；偏差大于仪表精度（PPK2 平均值 ±10%）时回查哪个状态被低估

**来源**
- [SLVAER8A Extending Battery Life With Low Quiescent Current and Dynamic Voltage Scaling](https://www.ti.com/lit/an/slvaer8a/slvaer8a.pdf) — Texas Instruments, app_note, §2 Case Study, Table 2-2
- [Overcoming Low-IQ Challenges in Low-Power Applications (SLYY203)](https://www.ti.com/lit/pdf/slyy203) — Texas Instruments, app_note, Equation 2
- [High pulse drain impact on CR2032 coin cell battery capacity](https://devzone.nordicsemi.com/cfs-file/__key/communityserver-discussions-components-files/4/0842.High-pulse-drain-impact-on-CR2032-coin-cell-battery-capacity.pdf) — Nordic Semiconductor / Energizer, app_note, Summary item 5

<a id="LPW-ARC-002"></a>
#### LPW-ARC-002 · 用输入端折算公式核算常开轨待机电流
`should` · 可信度 `high` · 适用: battery, ldo, buck, boost, always-on-rail · 标签: cat-feeder

**规则** 常开轨的电池侧待机电流按 I_standby = I_Q,VIN + I_leak + (V_OUT / (V_IN·η)) × (I_Q,VOUT + I_FB + I_LOAD) 计算，寿命 = 容量 / (I_standby + I_电池自放电)；不能只拿稳压器数据手册上的 Iq 代表整条轨。

**依据** 稳压器 Iq 只是其中一项：反馈分压、电容和二极管漏电、VOUT 端的 Iq 与负载都要折算到输入端。TI 的例子里 TPS61099 的 VIN 侧 400 nA 与 VOUT 侧 600 nA 并不能直接相加，实际无负载输入电流约 1.3 µA。一次性锂电池自身也有自放电。

| 参数 | 判据 | 备注 |
|---|---|---|
| `coin_cell_self_discharge` | == 1 %/year | Energizer CR2032 数据手册 ~1%/年；按 235 mAh 约合 0.27 µA（自行折算） |

**验证**
- `bom_check`（partial）· 能量预算脚本（见 LPW-NET-001） — 对常开轨逐项求 I_standby；VOUT 侧电流除以 (V_IN·η/V_OUT) 折算到输入；η 取待机负载点的数据手册效率曲线值；寿命公式里加上电池自放电项
- `bench`（manual）· Joulescope / PPK2 / SMU 串在电池与整板之间 — 整板进入最低睡眠态后测电池侧电流，与脚本计算值比较，差值需能被某项已知漏电解释

**来源**
- [Overcoming Low-IQ Challenges in Low-Power Applications (SLYY203)](https://www.ti.com/lit/pdf/slyy203) — Texas Instruments, app_note, Equations 1 and 2 (p.4)
- [3 Quiescent-current (Iq) Specifications to Understand (SSZT118)](https://www.ti.com/lit/pdf/sszt118) — Texas Instruments, app_note
- [Energizer CR2032 product datasheet](https://data.energizer.com/pdfs/cr2032.pdf) — Energizer, datasheet

<a id="LPW-ARC-003"></a>
#### LPW-ARC-003 · 按真实负载曲线、终止电压和温度降额电池容量
`should` · 可信度 `high` · 适用: coin-cell, primary-lithium, battery

**规则** 不要直接使用数据手册标称容量（Energizer CR2032：235 mAh，条件 15 kΩ、21 °C、到 2.0 V）；用你的脉冲/连续负载、FEP 终止电压和工作温度下的有效容量，寿命 = 修正容量 / 最坏工作模式下的 I_avg。

**依据** 电池内阻造成瞬时压降，化学极化又随脉冲时长累积，高倍率下可用容量显著下降。Energizer 与 Nordic 的测试：500 µA 以下可用约 240 mAh，2.5 mA 连续放电到 2.0 V 只剩 175 mAh，30 mA 脉冲每 10 ms 一次约 125 mAh。TI 实测六家 CR2032 供应商，个别品牌只有标称的约 50%。

| 参数 | 判据 | 备注 |
|---|---|---|
| `cr2032_capacity_continuous_2p5mA_fep2p0` | == 175 mAh | Energizer/Nordic 图 3：2.5 mA 连续、FEP 2.0 V |
| `cr2032_capacity_30mA_pulse_10ms_period_fep2p0` | == 125 mAh | Energizer/Nordic 图 5(A)：30 mA 脉冲每 10 ms 一次 |
| `cr2032_operating_temperature` | -30 … 60 degC | Energizer 数据手册工作温度；容量仅在 21 °C 标称，没有给低温降额 |
| `capacity_loss_peak_15_to_30mA` | == 9 % | SWRA349：峰值 15 mA 升到 30 mA 的平均有效容量损失，六家供应商平均 |

**验证**
- `bench`（manual）· 可编程电阻网络/电子负载按真实脉冲曲线放电（参考 SWRA349 的开关电阻网络），恒温箱 −10 / 25 / 45 °C — 记录电池端电压降到 FEP 时的累计 mAh，取最差样品作为设计容量
- `bom_check`（partial）· 能量预算脚本 — 容量查表（负载电流、FEP、温度三维）取最差值；寿命 = 修正容量 / 最坏模式 I_avg，其中最坏模式取电池寿命内可能进入的最短脉冲周期

**来源分歧** Energizer/Nordic 给出峰值 < 30 mA 且 FEP ≤ 2.0 V 时约 175–185 mAh；TI SWRA349 实测发现部分品牌/无牌电池只有标称的约 50%，且电池间离散大。取舍：设计按最差供应商或实测样品降额，不要信任单一厂商曲线；低温下内阻更高，SWRA349 只作了「可能更严重」的推测，需要自己实测。

**来源**
- [High pulse drain impact on CR2032 coin cell battery capacity](https://devzone.nordicsemi.com/cfs-file/__key/communityserver-discussions-components-files/4/0842.High-pulse-drain-impact-on-CR2032-coin-cell-battery-capacity.pdf) — Nordic Semiconductor / Energizer, app_note, Figures 3, 5, 9; Summary
- [SWRA349 Coin cells and peak current draw](https://www.ti.com/lit/wp/swra349/swra349.pdf) — Texas Instruments, app_note, §3, §5
- [Energizer CR2032 product datasheet](https://data.energizer.com/pdfs/cr2032.pdf) — Energizer, datasheet

<a id="LPW-ARC-004"></a>
#### LPW-ARC-004 · 全板最高的最低工作电压决定电池终止电压
`should` · 可信度 `high` · 适用: battery, coin-cell

**规则** 汇总电池轨上所有器件的最低工作电压，取最大者作为 FEP（功能终止电压），用它来读取电池可用容量；即使该器件在无线发射脉冲期间处于空闲，也要计入。

**依据** Energizer/Nordic 的数据：FEP 2.0 V 时峰值 ≤ 30 mA 可得 175–185 mAh；FEP 提高到 2.4 V，峰值 10 mA 仍有约 175 mAh，30 mA 峰值只剩约 100 mAh。空闲器件在电压过低时配置也可能丢失，所以同样会限定 FEP。

| 参数 | 判据 | 备注 |
|---|---|---|
| `cr2032_capacity_fep2p4_30mA_peak` | == 100 mAh | Energizer/Nordic 图 9：FEP 2.4 V、峰值约 30 mA、25 ms 周期 |
| `esp32c3_min_supply_voltage` | >= 3.0 V | ESP32-C3 VDDA/VDD3P3/VDD3P3_RTC 推荐范围 3.0–3.6 V（数据手册表 5-2），因此不能让 CR2032 放电到 2.0 V 再维持射频 |

**验证**
- `bom_check`（full）· Python：读 BOM + 器件参数表（LPW-LIB-001 的 V_min_operating 字段） — FEP = max(各器件 V_min)，输出决定 FEP 的器件；FEP 必须 ≤ 电池在最坏负载、最低温度下的预期电压
- `review`（manual）· 评审清单 — 确认每个电池轨器件的 V_min 取自数据手册推荐工作范围而非绝对最大值

**来源**
- [High pulse drain impact on CR2032 coin cell battery capacity](https://devzone.nordicsemi.com/cfs-file/__key/communityserver-discussions-components-files/4/0842.High-pulse-drain-impact-on-CR2032-coin-cell-battery-capacity.pdf) — Nordic Semiconductor / Energizer, app_note, Battery capacity vs. peak currents; Figure 9
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, Table 5-2 Recommended Operating Conditions

<a id="LPW-ARC-005"></a>
#### LPW-ARC-005 · 按实际待机负载选稳压器，而不是只看标称 Iq
`should` · 可信度 `high` · 适用: buck, boost, buck-boost, ldo, battery · 标签: cat-feeder

**规则** 稳压器以「目标待机负载点的电池侧输入电流」选型：Iq 只是无负载、不开关、已使能状态下的开销，需同时看无负载输入电流曲线、目标负载点效率，并确认 power-save 模式已使能；睡眠态负载为几十 µA 以上时 Iq 的影响迅速减弱。

**依据** TI 指出 IQ 不等于无负载输入电流：TPS61221 的 IQ 为 0.5 µA（VIN）+5 µA（VOUT），但 1.2 V→3.3 V 时无负载输入电流约 20 µA。TPS62120 带 100 µA 待机负载时效率只有 60%，IQ 不再是主导。另一方面，IQ 从 300 nA 降到 75 nA 在 TI 的案例里让寿命延长 9%。

| 参数 | 判据 | 备注 |
|---|---|---|
| `example_buck_iq_typ` | == 60 nA | TPS62840 工作 IQ 典型值；1 µA 负载（3.6 V→1.8 V）效率 80%，数据手册首页 |
| `iq_reduction_case_life_gain` | == 9 % | SLVAER8A：IQ 75 nA 对 300 nA，寿命延长 9%（固定系统电压，6 h 10 µA + 0.4 s 250 mA 的负载曲线） |

**验证**
- `bom_check`（partial）· Python 读器件参数表 + 数据手册效率曲线数字化数据 — I_in = V_out × I_out / (V_in × η(I_out))，在睡眠负载点与 TX 负载点分别计算；记录 Iq 的测试条件（是否开关、VIN、VOUT、温度）
- `spice`（partial）· 厂商 PSpice/TINA 模型（含 power-save） — 无负载与待机负载下的稳态输入电流平均值，与数据手册曲线对照
- `bench`（manual）· Joulescope / SMU — 把负载固定在待机电流（电子负载或实际睡眠 MCU）测输入电流，换算效率

**来源**
- [IQ: What it is, what it isn't, and how to use it (SLYT412)](https://www.ti.com/lit/an/slyt412/slyt412.pdf) — Texas Instruments, app_note, What IQ is / What IQ isn't / How to use IQ
- [SLVAER8A Extending Battery Life With Low Quiescent Current and Dynamic Voltage Scaling](https://www.ti.com/lit/an/slvaer8a/slvaer8a.pdf) — Texas Instruments, app_note, Table 2-1, Table 2-2
- [TPS62840 1.8-V to 6.5-V, 750-mA, 60-nA IQ Step-Down Converter](https://www.ti.com/lit/ds/symlink/tps62840.pdf) — Texas Instruments, datasheet

<a id="LPW-ARC-006"></a>
#### LPW-ARC-006 · 线性稳压器的 Iq 是睡眠电流的下限
`should` · 可信度 `high` · 适用: ldo, battery, esp32-c3, always-on-rail · 标签: cat-feeder

**规则** 把 LDO 的静态电流计入睡眠预算：AMS1117-3.3 典型 5 mA、最大 10 mA，比 ESP32-C3 深睡 5 µA 高三个数量级。睡眠电流或待机能耗有要求时，改用 µA/nA 级 Iq 的 LDO（如 TPS7A02 25 nA）或开关稳压器，或用 EN/负载开关把该稳压器断开。

**依据** LDO 的静态电流与输出负载无关，直接叠加在 MCU 之上。以 AMS1117 的 5 mA 为底，整板睡眠电流不可能低于这个值，所以 MCU 深睡的 5 µA 毫无意义。市面开发板深睡电流远高于芯片数据手册值，常见原因就是 AMS1117 一类的 LDO、电源 LED 和 USB 串口桥。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ams1117_quiescent_current_typ` | == 5 mA | AMS1117 固定电压版，VIN ≤ 12 V，IOUT = 0 mA；最大 10 mA。AMS1117 另标最小负载电流 5 mA 典型、10 mA 最大（可调版） |
| `ams1117_quiescent_current_max` | <= 10 mA | 同上。另一个版本和 JLCPCB 博客写 11 mA 最大，见 conflicts |
| `esp32c3_deep_sleep_current_typ` | == 5 uA | ESP32-C3 数据手册表 5-9：RTC 定时器 + RTC 内存 |
| `tps7a02_iq_typ` | == 25 nA | TPS7A02 典型 IQ（关断 3 nA 典型），数据手册首页，可作为替换参照 |

**验证**
- `bom_check`（partial）· Python：遍历 BOM 中的 LDO/稳压器，读取 Iq_max（工作温度、VIN） — Σ Iq_max（常开稳压器）≤ 睡眠预算的 50%（比例为设计经验，不是出处数值）；超出则要求换件或增加断电路径
- `bench`（manual）· SMU 或 Joulescope 串在 5 V 输入端 — MCU 进入深睡后测 5 V 输入电流；该电流减去 MCU 实测值应落在 LDO 的 Iq 范围内

**来源分歧** AMS1117 不同厂商/版本的数据手册 Iq 不一致：本次读到的 Advanced Monolithic 版本为 5 mA 典型/10 mA 最大；JLCPCB 博客引用的是 5/11 mA；搜索结果里还看到个别克隆厂商的页面标得更低（未打开确认）。取舍：按 BOM 实际料号的数据手册取最大值做预算，并用实测校验。

**来源**
- [AMS1117 1A Low Dropout Voltage Regulator datasheet](https://www.rcscomponents.kiev.ua/datasheets/AMS1117-datasheet.PDF) — Advanced Monolithic Systems (distributor mirror), datasheet, Electrical Characteristics: Quiescent Current, Minimum Load Current
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, Table 5-9 Current Consumption in Low-Power Modes
- [TPS7A02 Nanopower IQ, 25-nA, 200-mA LDO](https://www.ti.com/lit/ds/symlink/tps7a02.pdf) — Texas Instruments, datasheet
- [ESP32 Power Consumption: Modes, Deep Sleep & Battery Life](https://jlcpcb.com/blog/esp32-power-consumption-explained) — JLCPCB, blog

<a id="LPW-ARC-007"></a>
#### LPW-ARC-007 · 用负载开关划分电源域，切断高漏电子系统
`should` · 可信度 `high` · 适用: load-switch, p-mosfet, power-gating, sensor, radio-module · 标签: cat-feeder

**规则** 把待机漏电或静态电流超出预算的子系统（无线模块、传感器、放大器、HX711 加称重桥这类模拟前端）放入可切断电源域，用关断电流低的负载开关或 P-MOS 高端开关断电，常开域只留 MCU、RTC 和唤醒电路。选型用 I_avg = D·(I_load + I_Q) + (1−D)·I_SD 比较，Iq 与 Isd 都随 VIN 和温度升高。

**依据** 许多模块即使在自己的关断模式下也有 mA 级漏电，负载开关能把它降到 µA 以下。TI 例：5 V 轨下模块待机漏电 1 mA，经负载开关降到 1 µA 以下，功耗降为千分之一；Nordic 也建议给高漏电传感器加 GPIO 控制的高端 P-MOS 来降低 SYSTEM_OFF 电流。

| 参数 | 判据 | 备注 |
|---|---|---|
| `example_load_switch_off_current_max` | <= 100 nA | TPS22916 关断电流 ISD：典型 10 nA，−40~85 °C 最大 100 nA；导通 IQ 典型 0.5 µA、最大 1 µA；ON 引脚带 750 kΩ 智能下拉 |
| `example_leakage_reduction_factor` | == 1000 x | SLVA652A §5.2：1 mA 待机漏电经负载开关降到 < 1 µA |

**验证**
- `bom_check`（partial）· Python 能量预算脚本 — 每个可切断域：ISD_max(Tmax, VIN) + 域内仍然上电器件的反灌电流 ≤ 该域的关断预算；对导通态占空比 D 高的域改比 Iq
- `bench`（manual）· Joulescope / SMU 串在电池侧 — 分别在域通电、域断电两种睡眠态下测整板电流，差值应与脚本预测一致

**来源**
- [SLVA652A Load Switches: Basics and Applications](https://www.ti.com/lit/an/slva652a/slva652a.pdf) — Texas Instruments, app_note, §2.3 Reduced Leakage Current, §5.2 Standby Power Savings
- [SLVA757 Quiescent Current vs Shutdown Current for Load Switch Power Consumption](https://www.ti.com/lit/pdf/slva757) — Texas Instruments, app_note, §4–§7
- [Optimizing Power on nRF52 Designs](https://devzone.nordicsemi.com/nordic/nordic-blog/b/blog/posts/optimizing-power-on-nrf52-designs) — Nordic Semiconductor, blog
- [TPS22916 Ultra-Low Leakage Load Switch](https://www.ti.com/lit/ds/symlink/tps22916.pdf) — Texas Instruments, datasheet

<a id="LPW-ARC-008"></a>
#### LPW-ARC-008 · 按唤醒源与保持内容选 MCU 睡眠模式（ESP32-C3）
`should` · 可信度 `high` · 适用: esp32-c3, mcu, wake-source, rtc · 标签: cat-feeder

**规则** 为每种场景在睡眠状态表里指定模式与唤醒源。ESP32-C3：Deep-sleep 约 5 µA，只保留 RTC 定时器和 RTC 内存，唤醒后 CPU 上下文丢失、重新走 bootloader；Light-sleep 约 130 µA，保留 CPU 与外设状态；Modem-sleep 13–28 mA。Deep-sleep 的 GPIO 唤醒只能用 GPIO0–GPIO5（VDD3P3_RTC 域），按键和传感器中断必须接在这些脚上；GPIO 唤醒信号至少保持 3 个 RTC 慢时钟周期。

**依据** 睡眠模式的电流差三个数量级，保持内容与唤醒延迟需要权衡。Light-sleep 下任意 GPIO 都可唤醒，但 Deep-sleep 下只有 RTC 域的 IO 可用，硬件连线选错就无法唤醒。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esp32c3_deep_sleep_current_typ` | == 5 uA | 数据手册表 5-9，RTC 定时器 + RTC 内存，3.3 V、25 °C |
| `esp32c3_light_sleep_current_typ` | == 130 uA | 同表，VDD_SPI 与 Wi-Fi 掉电，所有 GPIO 高阻 |
| `esp32c3_modem_sleep_current` | 13 … 28 mA | 表 5-8，80/160 MHz、CPU 空闲/运行、外设时钟关/开 |
| `deep_sleep_wake_gpio_set` | qualitative | GPIO0–GPIO5；其余 GPIO 只能在 Light-sleep 唤醒 |
| `gpio_wake_min_pulse` | >= 3 RTC slow-clock cycles | 约 7.4 µs（RC_SLOW ~136 kHz）或约 30.5 µs（XTAL32K） |

**验证**
- `netlist_diff`（full）· Python 读 KiCad 网表 XML 与睡眠状态表（YAML） — 每个标记为 deep_sleep_wake 的网络必须连到 ESP32-C3 的 GPIO0–GPIO5 引脚；否则判失败。再检查唤醒网络在睡眠期的静态电平与有效边沿方向一致
- `bench`（manual）· Joulescope / PPK2 — 分别在 Deep-sleep、Light-sleep、Modem-sleep 下测整板电流并与表 5-8、5-9 对照，实际唤醒一次验证 GPIO 脉宽下限

**来源**
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, Table 4-1, Tables 5-8 and 5-9, Table 2-1 (VDD3P3_RTC pins)
- [Sleep Modes - ESP32-C3 - ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/system/sleep_modes.html) — Espressif, vendor_guide, Wakeup sources; GPIO wakeup timing
- [GPIO - ESP32-C3 - ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/gpio.html) — Espressif, vendor_guide, Pad hold and sleep functions

<a id="LPW-ARC-011"></a>
#### LPW-ARC-011 · RTC 备份与超级电容容量必须计入漏电
`should` · 可信度 `high` · 适用: rtc, supercap, backup, always-on-rail

**规则** 备份时间按 t = C·ΔV / (I_load + I_leak) 计算，ΔV = 备份源电压 − 负载最低保持电压；超级电容漏电（µA 级）通常远大于 RTC 自身电流，必须相加；超级电容 ESR 在 nA 级负载下可忽略，但有突发电流时不能；并按电压和温度降额以保证寿命。

**依据** Abracon 例：RTC 最大 330 nA，超级电容漏电 4 µA，总放电电流 4.33 µA，漏电是备份能量损失的主因。Micro Crystal 也指出，大容量电容的漏电可轻易超过 RTC 的工作电流。超级电容标称寿命约 1000–2000 小时，降额后可到多年。

| 参数 | 判据 | 备注 |
|---|---|---|
| `supercap_leakage_example` | == 4 uA | Abracon 例；同一系列最佳情况 3 µA，RTC 负载最大 330 nA |
| `supercap_rated_life_hours` | 1000 … 2000 hours | 行业标称寿命，降额电压与温度后延长到数年 |
| `supercap_longevity_end_of_life` | qualitative | 容量下降 30% 或 ESR 升到 2 倍视为寿命终点（Abracon） |

**验证**
- `bom_check`（partial）· 电子表格/脚本 — C_min = (I_load + I_leak_max) × t_backup / (V_backup − V_min_RTC)，I_leak 取最高温度下数据手册值；再乘容量公差和寿命末期 70% 容量
- `bench`（manual）· 充满后断开主电源，用数据采集器记录 VBACKUP 衰减 — 在最高工作温度、24 h 以上保持，电压不低于 RTC 保持电压；首次上电的数十小时内漏电更高，需要稳定后再取值

**来源**
- [Using Supercapacitors as RTC Power Backup](https://abracon.com/uploads/resources/Abracon-Application-Note-Using-Supercapacitors-as-RTC-Power-Backup.pdf) — Abracon, app_note, Standard Capacitors vs. Supercapacitors; Capacitor Selection and Calculations
- [RV-1805-C3 Application Note: RTC Capacitor Backup](https://www.microcrystal.com/fileadmin/Media/Products/RTC/Whitepapers/RV-1805-C3_App-Note_Cap_Backup.pdf) — Micro Crystal, app_note, §3.2 Capacitor characteristics

<a id="LPW-ARC-009"></a>
#### LPW-ARC-009 · Wi-Fi 保持连接还是深睡重连，按平均电流预算选
`consider` · 可信度 `high` · 适用: esp32-c3, wifi, iot · 标签: cat-feeder

**规则** 联网设备按响应延迟与平均电流预算选策略：ESP32-C3 屏蔽箱实测，Modem-sleep 平均约 20–21 mA（开 DFS 约 10–11 mA）；Auto Light-sleep 平均 1.4 mA（DTIM1）、0.62 mA（DTIM3）、0.31 mA（DTIM10）；Deep-sleep 断开 Wi-Fi 约 4.8 µA。路由器 DTIM 越短越耗电。

**依据** 保持连接的代价比深睡高 2–3 个数量级。主要等待指令的设备适合 Auto Light-sleep，而 CPU 要持续运行的场景才用 Modem-sleep + DFS。

| 参数 | 判据 | 备注 |
|---|---|---|
| `auto_light_sleep_avg_current_dtim1` | == 1.4 mA | 160 MHz，屏蔽箱测量；DTIM3 0.62 mA，DTIM10 0.31 mA |
| `modem_sleep_avg_current_dtim1` | == 21.47 mA | 未开 DFS；开 DFS 为 11.35 mA |
| `deep_sleep_avg_current_wifi_disconnected` | == 4.8 uA | 与数据手册 5 µA 一致，但 Wi-Fi 连接断开 |

**验证**
- `bench`（partial）· Joulescope / PPK2，目标 AP，抓取至少 10 个 DTIM 周期以上的平均值 — 在目标路由器的真实 DTIM 设置下测平均电流，与预算比较；换路由器后复测，因为 DTIM 由 AP 决定
- `review`（manual）· 评审清单 — 确认应用不需要广播/多播包，否则 Max Modem 的 listen interval 会丢包

**来源**
- [Wi-Fi Low Power Guidance - ESP32-C3 - ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-guides/low-power-mode/low-power-mode-wifi.html) — Espressif, vendor_guide, Average Current by Mode; Application Tips

<a id="LPW-ARC-010"></a>
#### LPW-ARC-010 · 睡眠预算要计入 Flash 待机电流
`consider` · 可信度 `high` · 适用: esp32-c3, flash, light-sleep · 标签: cat-feeder

**规则** Light-sleep 下 SPI Flash 默认仍供电，待机约 10–30 µA；可配置 Deep Power-Down（常低于 1 µA，需要 Flash 支持）。esp_deep_sleep_start() 总会让 Flash 掉电；不建议在 Light-sleep 里直接断 Flash 供电，掉电时间可能超过 300 ms，滤波电容会让它更长。

**依据** Flash 的待机电流在 Light-sleep 的 130 µA 里占相当比例；Deep-sleep 路径由 ESP-IDF 处理，但 Light-sleep 需要显式选择 DPD。

| 参数 | 判据 | 备注 |
|---|---|---|
| `spi_flash_standby_current` | 10 … 30 uA | ESP-IDF 文档描述：保持 Flash 供电约 10–30 µA，常见乐鑫 SPI Flash 低于 30 µA |
| `spi_flash_dpd_current` | < 1 uA | 多数 Flash 的 DPD 电流，需查具体型号数据手册 |

**验证**
- `bom_check`（partial）· 读取模块/Flash 数据手册 — 确认 Flash 型号是否支持 DPD 命令，把 standby 与 DPD 电流写入器件参数表
- `bench`（manual）· Joulescope / PPK2 — Light-sleep 下开/关 CONFIG_ESP_SLEEP_SET_FLASH_DPD 各测一次，对比差值

**来源**
- [Sleep Modes - ESP32-C3 - ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/system/sleep_modes.html) — Espressif, vendor_guide, Flash in sleep; Minimizing power consumption

<a id="LPW-ARC-013"></a>
#### LPW-ARC-013 · 定时唤醒精度要求决定 RTC 慢时钟来源
`consider` · 可信度 `medium` · 适用: esp32-c3, rtc, deep-sleep · 标签: cat-feeder

**规则** 需要跨睡眠的定时精度（如喂食计划）时，明确 RTC 慢时钟来源：内部 RC 的精度较差、频率偏差较大，外部 32.768 kHz 晶振精度高但要占用 GPIO0/GPIO1（XTAL_32K_P/N）；对精度不敏感的场景，用内部 RC 并做周期校准或联网校时。

**依据** Deep-sleep 唤醒时间由 RTC 慢时钟计时。ESP-IDF 文档说明内部 RC 源精度和频偏都不如外部晶振；GPIO0、GPIO1 又是 Deep-sleep 可用的唤醒引脚，占用后要权衡引脚分配。

| 参数 | 判据 | 备注 |
|---|---|---|
| `rtc_slow_clock_rc_frequency` | qualitative | ESP-IDF 睡眠文档按约 136 kHz 估算周期，低功耗文档写约 150 kHz；以所用芯片版本的数据手册为准，且需要出厂校准或运行时校准 |

**验证**
- `bench`（partial）· 逻辑分析仪或示波器测 GPIO 翻转时间，Joulescope 记录唤醒时刻 — 连续 24 h 睡眠/唤醒周期，统计唤醒时间漂移，与应用允许误差对比；高/低温下各测一次
- `review`（manual）· 评审清单 — GPIO0/GPIO1 是否已被晶振占用，Deep-sleep 唤醒按键是否仍有可用的 RTC 域引脚

**来源**
- [Low Power Mode - SoC - ESP32-C3 - ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-guides/low-power-mode/low-power-mode-soc.html) — Espressif, vendor_guide, Recommended configuration: RTC slow clock
- [Sleep Modes - ESP32-C3 - ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/system/sleep_modes.html) — Espressif, vendor_guide, GPIO wakeup timing (RC_SLOW / XTAL32K periods)
- [Optimizing Power on nRF52 Designs](https://devzone.nordicsemi.com/nordic/nordic-blog/b/blog/posts/optimizing-power-on-nrf52-designs) — Nordic Semiconductor, blog, LFCLK crystal (nRF52 only; saves 2-10%)

## 符号封装库（library）

<a id="LPW-LIB-001"></a>
#### LPW-LIB-001 · 在符号或 BOM 里记录低功耗参数及其测试条件
`should` · 可信度 `medium` · 适用: library, bom, symbol

**规则** 为每个器件的符号/BOM 增加字段：Iq_typ、Iq_max、Isd（关断电流）、漏电、V_min_operating，以及对应条件（VIN、温度、是否无负载/不开关/使能）；Iq、地脚电流、无负载输入电流、关断电流是不同参数，不要混用。

**依据** 脚本核算（LPW-NET-001）依赖这些字段。TI 指出 Iq 的标准定义是无负载、不开关、已使能；开关式稳压器还有「开关 IQ」，LDO 则用地脚电流；Isd 与 Iq 都随 VIN 和温度变化，只记一个数字会让预算失真。

**验证**
- `bom_check`（full）· Python 检查 BOM/符号字段 — 所有常开轨上的有源器件和电容都必须有 Iq_max、Isd、V_min 字段和条件字符串；缺失即失败

**来源**
- [3 Quiescent-current (Iq) Specifications to Understand (SSZT118)](https://www.ti.com/lit/pdf/sszt118) — Texas Instruments, app_note
- [IQ: What it is, what it isn't, and how to use it (SLYT412)](https://www.ti.com/lit/an/slyt412/slyt412.pdf) — Texas Instruments, app_note, What IQ is
- [SLVA757 Quiescent Current vs Shutdown Current for Load Switch Power Consumption](https://www.ti.com/lit/pdf/slva757) — Texas Instruments, app_note, §3, §5

## 原理图（schematic）

<a id="LPW-SCH-005"></a>
#### LPW-SCH-005 · 掉电域的信号要隔离，防止经 I/O 二极管反向供电
`must` · 可信度 `high` · 适用: power-gating, load-switch, level-shifter, mixed-voltage · 标签: cat-feeder

**规则** 任何会被关断或可能先于其他域掉电的器件（负载开关后的模块、外部电压域的传感器、电平转换器）不得有来自常开域的信号去驱动它的 I/O：在断电前把信号驱动到低或高阻，用串联电阻限流，或选用带 Ioff/部分掉电保护的器件。

**依据** I/O 内部 ESD 二极管会把高于电源 0.3 V 以上的信号电压反灌到本已断电的电源轨，造成不可预期的行为，严重时损坏器件，还让负载开关的节能失效。TI 在电池供电场合明确警告：I/O 过压抬升电源电压可能导致电池爆炸或起火。

| 参数 | 判据 | 备注 |
|---|---|---|
| `backpower_pin_voltage_threshold` | > 0.3 V | SLAA689：电源为 0 V 时引脚电压高于 0.3 V 即可能经 ESD 二极管反向供电（MSP430 文档，原理对所有 CMOS 器件通用） |
| `esd_diode_continuous_current_max` | <= 2 mA | SLAA689 以 MSP430FR5969 为例，每引脚连续电流 ±2 mA；其他器件查各自绝对最大额定值 |

**验证**
- `bom_check`（partial）· Python 读网表 + 电源域标注（常开/可切） — 对每个可切域内的器件，列出连接到常开域驱动器的信号网络，检查是否有串联电阻、Ioff 属性（器件参数表字段）或睡眠前拉低的固件约束；无则报告
- `spice`（partial）· ngspice：可切轨设为 0 V，驱动源设为 VDD — 测从信号流入被断电域的电流及被断电轨的反向电压，要求被断电轨 < 0.3 V 且电流小于该域关断预算
- `bench`（manual）· 示波器/万用表 — 关断该域后测其轨电压，应接近 0 V，不应出现半电平

**来源**
- [SLAA689 ESD Diode Current Specification](https://www.ti.com/lit/pdf/slaa689) — Texas Instruments, app_note, §1, §3 (WARNING)
- [SLVA652A Load Switches: Basics and Applications](https://www.ti.com/lit/an/slva652a/slva652a.pdf) — Texas Instruments, app_note, §2.3

<a id="LPW-SCH-006"></a>
#### LPW-SCH-006 · 使能与栅极控制线在复位和深睡期间要有确定电平
`must` · 可信度 `high` · 适用: esp32-c3, mosfet-gate, load-switch, enable-pin, motor-driver · 标签: cat-feeder

**规则** MCU GPIO 控制的负载开关 EN、LDO EN、MOSFET 栅极（包括电机驱动管）、外设供电开关，都要有外部上拉/下拉到关断电平。ESP32-C3 复位和 Deep-sleep 期间数字 GPIO（6–21）为高阻，RTC GPIO（0–5）除非启用 hold 也是高阻；上电时部分引脚还有毛刺。需要在深睡中保持电平时，用 gpio_hold_en() + gpio_deep_sleep_hold_en()，并注意被保持为高电平的 LED 或负载会持续耗电。

**依据** 高阻的栅极或使能端会随漏电和干扰浮动，可能让电机管半导通或让外设意外上电，既耗电又有安全风险。乐鑫列出的上电毛刺：GPIO18 约 50 µs 高电平，MTCK、MTDO、GPIO10、U0RXD 约 5 ns 低电平。

| 参数 | 判据 | 备注 |
|---|---|---|
| `gpio18_powerup_high_glitch` | == 50000 ns | 原理图检查表 GPIO 一节；约值 |
| `other_pins_powerup_low_glitch` | == 5 ns | MTCK、MTDO、GPIO10、U0RXD |
| `gate_pull_resistor_value` | qualitative | 阻值（常见 10–100 kΩ）取决于栅极漏电与对关断电平的要求，数值为设计经验，不是出处数值；越大越省电，需不被漏电抬起 |

**验证**
- `bom_check`（full）· Python 读网表 — 找出所有 MOSFET 栅极、负载开关 EN 和 LDO EN 网络，检查是否有一个电阻连接到关断电平（N-MOS 到 GND、P-MOS 到源极），并在睡眠状态表里记录该网络的默认电平；缺失即失败
- `bench`（manual）· 示波器 + Joulescope — 上电复位、深睡进入与唤醒期间监视栅极和 EN 线，确认无意外脉冲；深睡中测其电平

**来源**
- [Sleep Modes - ESP32-C3 - ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/system/sleep_modes.html) — Espressif, vendor_guide, Pull-ups, pulldowns, and hold behavior
- [GPIO - ESP32-C3 - ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/gpio.html) — Espressif, vendor_guide, Pad hold and sleep functions
- [Schematic Checklist - ESP32-C3 - ESP Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, GPIO (power-up glitches)
- [ESP32-S3 Deep Sleep Power: vs C3 vs C6, Measured](https://www.qoitech.com/blog/esp32-s3-c3-c6-sleep-power-consumption/) — Qoitech, blog, gpio_deep_sleep_hold_en on GPIO10 (LED) raised deep-sleep current to 461 uA

<a id="LPW-SCH-012"></a>
#### LPW-SCH-012 · 一次性锂电池的反向充电电流不得超过 1 µA
`must` · 可信度 `high` · 适用: coin-cell, primary-lithium, battery, supercap

**规则** 不要给一次性锂电池（Li/MnO2 纽扣电池）反向充电：Energizer CR2032 规定最大反向充电电流为 1 µA。与电池并联的任何电源路径（备份电容或超级电容、外部电源 OR-ing、经 ESD 二极管灌入的 I/O 电流）都要有二极管/理想二极管/开关阻断，并按最坏情况核算电池端的反向电流。

**依据** 对一次电池充电可能导致漏液、过热甚至起火；TI 也提示电池供电系统里 I/O 过压把电源抬高可能令电池爆炸或燃烧。

| 参数 | 判据 | 备注 |
|---|---|---|
| `primary_cell_max_reverse_charge` | <= 1 uA | Energizer CR2032 数据手册 Max Rev Charge |

**验证**
- `spice`（partial）· ngspice：外部电源接入且高于电池，电池支路接 0 V 电流探针 — 全温度范围内电池支路的反向电流 ≥ −1 µA（含二极管反向漏电与体二极管）
- `bench`（manual）· µA 级电流表串联电池 — 外部电源接入、电池装入，测电池端电流方向和大小

**来源**
- [Energizer CR2032 product datasheet](https://data.energizer.com/pdfs/cr2032.pdf) — Energizer, datasheet, Specifications: Max Rev Charge
- [SLAA689 ESD Diode Current Specification](https://www.ti.com/lit/pdf/slaa689) — Texas Instruments, app_note, §3 WARNING

<a id="LPW-SCH-001"></a>
#### LPW-SCH-001 · 核算常开轨上每条电阻支路的静态电流（V/R）
`should` · 可信度 `high` · 适用: pull-up, voltage-divider, i2c, feedback-divider, always-on-rail · 标签: cat-feeder

**规则** 对常开轨上每个电阻支路按 I = V/R 计算睡眠期电流：对端在睡眠期被拉低或接地的上拉、分压器、反馈分压器。睡眠期会被拉低的线不接上拉，或把上拉接到可关断的轨，或取更大阻值；I2C 上拉取速度允许的最大值 R_p(max) = t_r / (0.8473 × C_b)。

**依据** 10 kΩ 上拉在 3.3 V 下被拉低时是 330 µA，比 ESP32-C3 的 5 µA 深睡大 60 倍；片内 45 kΩ 弱上拉对着外部低电平也有约 73 µA。几 µA 级的待机负载下，稳压器反馈分压器的电流也占可观比例（TI 的 TPS63900 用上电时读取的设置电阻来避免这一项）。

| 参数 | 判据 | 备注 |
|---|---|---|
| `i2c_fast_mode_rise_time_max` | <= 300 ns | SLVA689 表 2-1：Fast mode；标准模式 1000 ns，Fm+ 120 ns |
| `i2c_bus_capacitance_max` | <= 400 pF | 标准/快速模式；Fm+ 为 550 pF |
| `esp32c3_internal_pull_resistance` | == 45 kohm | 数据手册表 5-4，典型值，上拉和下拉相同 |

**验证**
- `bom_check`（partial）· Python 读 KiCad 网表 XML + BOM（阻值） — 对每个一端接常开轨的电阻，另一端若是 GND 或睡眠期被驱动/拉低的网络，累加 V_rail / R；输出贡献排名；比较总和与睡眠预算（见 LPW-NET-001）。静态分压器（轨到地）可全自动判定，GPIO 状态相关的需要睡眠状态表
- `spice`（partial）· ngspice .op — 把睡眠态的 GPIO 电平写成电压源，读轨电流

**来源**
- [SLVA689 I2C Bus Pullup Resistor Calculation](https://www.ti.com/lit/an/slva689/slva689.pdf) — Texas Instruments, app_note, §2 and §3 Speed Versus Power Trade-off
- [SLVAER8A Extending Battery Life With Low Quiescent Current and Dynamic Voltage Scaling](https://www.ti.com/lit/an/slvaer8a/slvaer8a.pdf) — Texas Instruments, app_note, §1 Introduction (feedback divider)
- [Overcoming Low-IQ Challenges in Low-Power Applications (SLYY203)](https://www.ti.com/lit/pdf/slyy203) — Texas Instruments, app_note, Equation 1 (I_FB term)
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, Table 5-4 DC Characteristics

<a id="LPW-SCH-002"></a>
#### LPW-SCH-002 · 睡眠期 GPIO 电平与外部上下拉必须一致
`should` · 可信度 `medium` · 适用: esp32-c3, stm32, gpio, always-on-rail · 标签: cat-feeder

**规则** 为每个 GPIO 建立睡眠状态表（输出高/低/高阻、内部上下拉、外部网络），保证 MCU 和外部电路在睡眠中不互相对抗：不要把引脚拉低去顶上拉，或拉高去顶下拉。ESP32-C3 默认启用睡眠内部电阻（ESP_SLEEP_GPIO_ENABLE_INTERNAL_RESISTORS），使用外部电阻时要关闭，低电平唤醒时要加外部上拉。

**依据** ESP-IDF 文档指出部分 IO 默认带内部上下拉，Deep-sleep 中若外部电路驱动它们，电流会增加。ST 的 AN4899 也提醒复用带上下拉的调试脚时不要对着拉。Deep-sleep 中数字 GPIO 是高阻，RTC GPIO 除非 hold 也是高阻，所以对外部电路的默认电平要靠硬件决定。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esp32c3_deep_sleep_digital_gpio_state` | qualitative | GPIO6–GPIO21 高阻；GPIO0–GPIO5（RTC IO）除非 hold 否则高阻（ESP-IDF 睡眠文档） |

**验证**
- `netlist_diff`（partial）· Python：睡眠状态表（YAML）+ KiCad 网表 XML — 对每个 GPIO 网络，列出外部电阻到哪个电源/地；若睡眠态驱动电平与外部电阻方向相反，或睡眠态为高阻且网络无外部拉电阻，则报告
- `bench`（manual）· Joulescope + 示波器/万用表测各 GPIO 睡眠电平 — 深睡中逐个测 GPIO 的电压是否等于状态表预期，且无半电平

**来源**
- [Sleep Modes - ESP32-C3 - ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/system/sleep_modes.html) — Espressif, vendor_guide, Pull-ups, pulldowns, and hold behavior
- [AN4899 STM32 GPIO configuration for hardware settings and low-power consumption](https://www.st.com/resource/en/application_note/dm00315319-stm32-gpio-configuration-for-hardware-settings-and-lowpower-consumption-stmicroelectronics.pdf) — STMicroelectronics, app_note, §6 Hardware guidelines (PDF 未能打开；内容见搜索结果与 ST 社区帖)
- [Recommended course of action for Unused pin of STM32 MCU (ST Community)](https://community.st.com/t5/stm32-mcus-products/recommended-course-of-action-for-unused-pin-of-stm32-mcu/td-p/582148) — STMicroelectronics community, forum

<a id="LPW-SCH-003"></a>
#### LPW-SCH-003 · 未用引脚不得悬空，按芯片规定处理
`should` · 可信度 `high` · 适用: mcu, esp32-c3, stm32, efm32, nrf52 · 标签: cat-feeder

**规则** 未用的 MCU 引脚不能让使能的输入缓冲悬空：ESP32-C3 复位后 GPIO2、GPIO8 是使能输入但无内部上下拉的高阻，未接电路时要外加上下拉或在软件里使能内部上下拉；STM32 设为模拟输入（或接地/电源，或输出低）；EFM32 设为 Disabled；nRF52 保持复位默认的断开输入缓冲。上电默认状态不同的引脚（调试脚）要按数据手册单独处理。

**依据** 悬空的输入缓冲会因噪声反复翻转，额外耗电；模拟/禁用模式关掉施密特触发器和输出驱动，消耗为零。ESP32-C3 每脚输入漏电最大 50 nA，22 个引脚全部悬空/漏电最坏也有 µA 量级。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esp32c3_gpio_input_leakage_max` | <= 50 nA | 数据手册表 5-4，I_IH/I_IL 每引脚最大值 |

**验证**
- `erc`（partial）· KiCad ERC（引脚未连接、输入未被驱动） — 对 MCU 引脚启用「未连接引脚」检查，未用脚必须放置 no-connect 标记并在固件配置表里有对应的处理方式
- `netlist_diff`（partial）· Python：对照固件 GPIO 初始化表与网表 — 网表中没有任何连接的 GPIO，在固件初始化表里必须是 analog/disabled/pull 之一；ESP32-C3 的 GPIO2、GPIO8 必须有外部或软件上下拉

**来源分歧** TI SCBA004 提到交流供电系统可用上拉解决悬空，但不推荐用于电池设备（电阻消耗电流），建议用 bus-hold；乐鑫检查表和 ST/Silicon Labs 的做法则是加上下拉或软件关输入。取舍：只要引脚不需要读，首选让输入缓冲关闭（模拟/Disabled/断开）；必须读且外部可能高阻时，用最大可行阻值的上下拉或 bus-hold，并确认对端不会长期对抗它。

**来源**
- [Schematic Checklist - ESP32-C3 - ESP Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, GPIO; Strapping Pins
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, Table 5-4
- [Recommended course of action for Unused pin of STM32 MCU (ST Community)](https://community.st.com/t5/stm32-mcus-products/recommended-course-of-action-for-unused-pin-of-stm32-mcu/td-p/582148) — STMicroelectronics community, forum
- [EFM32 Energy Optimization (mirror of Silicon Labs AN0027 §2.1 GPIO Leakage)](http://efm32.blogspot.com/2016/10/efm32-energy-optimization.html) — Silicon Labs EFM32 Playground (blog), blog
- [Optimizing Power on nRF52 Designs](https://devzone.nordicsemi.com/nordic/nordic-blog/b/blog/posts/optimizing-power-on-nrf52-designs) — Nordic Semiconductor, blog, Unused pins

<a id="LPW-SCH-004"></a>
#### LPW-SCH-004 · 外部逻辑 IC 的输入不得悬空或长期处于半电平
`should` · 可信度 `high` · 适用: cmos-logic, level-shifter, bus, open-drain

**规则** 外部 CMOS/BiCMOS 逻辑、缓冲、移位器的每个未用输入都要接到轨或地；会进入高阻的总线要有确定电平（电池设备优先用 bus-hold，而不是上拉电阻）。输入电压在 0.8–2 V 的阈值区停留时间长，会让 ICC 增加到每个输入几 mA。

**依据** 输入级在阈值区 P 管 N 管同时导通，形成 VCC 到 GND 的电流通路。TI 估算：18 位收发器的 36 个 I/O 悬空在阈值区时，VCC 电流可达 150–200 mA，约 1 W，造成过热。

| 参数 | 判据 | 备注 |
|---|---|---|
| `threshold_region` | 0.8 … 2.0 V | TTL 兼容 CMOS/BiCMOS 系列的阈值区；ICC 在 VI 约 1.5 V 达到峰值，每个输入可达几 mA |

**验证**
- `erc`（full）· KiCad ERC：输入引脚未被驱动、引脚未连接 — 所有逻辑 IC 的输入引脚类型必须有驱动源或显式的拉电阻；ERC 零警告
- `bom_check`（partial）· Python 读网表 — 对「只连接输入类引脚且无拉电阻」的网络报告；对三态总线报告有无 bus-hold 或拉电阻

**来源分歧** TI SCBA004 说用上拉确保定义电平适用于交流供电系统，电池设备不推荐，应使用 bus-hold；乐鑫、ST 等 MCU 文档则建议用上下拉。取舍见 LPW-SCH-003：器件带 bus-hold 时优先 bus-hold，否则用尽量大的电阻值并让对端不要长期对抗。

**来源**
- [SCBA004 Implications of Slow or Floating CMOS Inputs](https://www.ti.com/lit/pdf/scba004) — Texas Instruments, app_note, §1, §2, §5, §6

<a id="LPW-SCH-007"></a>
#### LPW-SCH-007 · 电池电压监测不要用常通分压
`should` · 可信度 `low` · 适用: battery-monitor, voltage-divider, adc, p-mosfet, n-mosfet

**规则** 电池或轨电压监测用可开关的分压：低端 N-MOS（或 GPIO 在采样时拉低、平时高阻），或高端 P-MOS 加小 N-MOS 驱动，仅在采样时导通；若必须常通，总阻值至少 MΩ 级并把它的电流计入预算。采样节点加小电容以满足 ADC 采样保持，并用串联电阻限制经保护二极管的电流。

**依据** 100 kΩ + 100 kΩ 分压接在 4.2 V 电池上就是 21 µA，比 ESP32-C3 深睡大四倍；Nordic 建议对高漏电的电路用 GPIO 控制的高端 P-MOS 开关切断。阻值过大又会因 ADC 源阻抗读低，所以要配合开关与滤波电容。

| 参数 | 判据 | 备注 |
|---|---|---|
| `divider_standby_current` | minimize uA | 关断状态应只剩开关漏电（nA 级）；具体上限取决于睡眠预算 |

**验证**
- `spice`（partial）· ngspice .op / .tran — 开关关断时电池侧电流 ≈ 开关漏电；开关导通后采样节点稳定时间 < 采样窗口，ADC 读数误差 < 目标精度
- `bench`（manual）· Joulescope + 示波器 — 采样前后测电池电流，确认关断态无分压电流；扫采样延时观察读数收敛

**来源**
- [Optimizing Power on nRF52 Designs](https://devzone.nordicsemi.com/nordic/nordic-blog/b/blog/posts/optimizing-power-on-nrf52-designs) — Nordic Semiconductor, blog, High-leakage sensors: GPIO-controlled high-side switch
- [M141 Switching & Protecting Electronics in Battery-Powered Systems (strobed UV/OV dividers)](https://www.analog.com/media/en/technical-documentation/technical-articles/m141_en-battery_power.pdf) — Analog Devices, app_note, (仅在搜索摘要中看到，PDF 抓取超时，未读原文)

<a id="LPW-SCH-008"></a>
#### LPW-SCH-008 · 指示灯是睡眠电流大户，要由 GPIO 驱动并在睡眠中熄灭
`should` · 可信度 `medium` · 适用: led, indicator, esp32-c3 · 标签: cat-feeder

**规则** 常亮的电源/状态 LED 要么去掉，要么由 MCU GPIO 驱动并在睡眠前熄灭，要么改成脉冲点亮；限流电阻按 I = (V_rail − Vf)/R 核算。避免用 gpio_hold 把 LED 引脚保持在会使 LED 导通的电平。

**依据** 3.3 V 轨、Vf 2.0 V、1 kΩ 限流的电源 LED 约 1.3 mA，是 ESP32-C3 深睡 5 µA 的 260 倍。多篇开发板测量文章都把电源 LED、LDO 和 USB 串口桥列为实测深睡电流远高于数据手册的主因；Qoitech 的测量里，对驱动 LED 的 GPIO 调用 gpio_deep_sleep_hold_en 后读数是 461 µA，去掉该调用后降到 41.6 µA。

| 参数 | 判据 | 备注 |
|---|---|---|
| `example_power_led_current` | == 1.3 mA | JLCPCB 博客例：(3.3 V − 2.0 V) / 1 kΩ |

**验证**
- `bom_check`（full）· Python 读网表 — 找出阳极/阴极经电阻连到常开轨且无晶体管/GPIO 控制的 LED 支路，I = (V_rail − Vf)/R 累加；有则报告
- `bench`（manual）· Joulescope — 睡眠中拆/断 LED 前后对比电流

**来源**
- [ESP32 Power Consumption: Modes, Deep Sleep & Battery Life](https://jlcpcb.com/blog/esp32-power-consumption-explained) — JLCPCB, blog
- [ESP32 Deep Sleep Current: What the Datasheet Says vs What You'll Actually Measure](https://hubble.com/community/guides/esp32-deep-sleep-current-what-the-datasheet-says-vs-what-you-ll-actually-measure/) — Hubble, blog
- [ESP32-S3 Deep Sleep Power: vs C3 vs C6, Measured](https://www.qoitech.com/blog/esp32-s3-c3-c6-sleep-power-consumption/) — Qoitech, blog

<a id="LPW-SCH-009"></a>
#### LPW-SCH-009 · 外设用自带掉电模式或断电，并保证睡眠中保持该状态（HX711）
`should` · 可信度 `high` · 适用: hx711, adc, sensor, load-cell · 标签: cat-feeder

**规则** 睡眠前把每个外设置于最低功耗态或断其电源。HX711 正常工作约 1.4 mA（模拟，含片内稳压器）+0.1 mA（数字），PD_SCK 保持高电平超过 60 µs 即进入掉电（合计小于 1 µA），拉低后复位并回到通道 A、增益 128；掉电时片内稳压器关闭，称重桥激励也随之关断。MCU 在深睡中 GPIO 是高阻，所以 PD_SCK 要靠外部上拉或 gpio_hold 保持在高电平，并确认所用模块板的默认电平。

**依据** 称重放大器是典型的常开大户：1.5 mA 相当于 ESP32-C3 深睡的 300 倍。掉电模式由 PD_SCK 控制，MCU 睡眠时如果该脚浮空或被拉低，HX711 会醒着。

| 参数 | 判据 | 备注 |
|---|---|---|
| `hx711_normal_analog_current` | == 1400 uA | 含片内稳压器，典型值；数字部分 100 µA |
| `hx711_power_down_current` | < 1 uA | 数据手册首页：power down < 1 µA（模拟 0.3 µA + 数字 0.2 µA） |
| `hx711_pd_sck_high_time` | > 60 us | PD_SCK 由低变高并保持高超过 60 µs 进入掉电 |

**验证**
- `netlist_diff`（partial）· Python 读网表 — HX711 的 PD_SCK 网络必须有睡眠期的确定高电平来源：外部上拉到 3V3，或 GPIO 在 RTC 域并启用 hold；否则判失败
- `bench`（manual）· Joulescope — 分别在 HX711 工作和掉电时测 3V3 轨电流，差值应约 1.4–1.5 mA；掉电中确认 DT/SCK 线上没有倒灌电流

**来源**
- [HX711 24-Bit Analog-to-Digital Converter for Weigh Scales](https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf) — Avia Semiconductor, datasheet, Features; Electrical characteristics; Reset and Power-Down, Fig.3
- [Sleep Modes - ESP32-C3 - ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/system/sleep_modes.html) — Espressif, vendor_guide, Pull-ups, pulldowns, and hold behavior

<a id="LPW-SCH-010"></a>
#### LPW-SCH-010 · INA199 没有关断脚，睡眠预算要含其 Iq 与 1 MΩ 泄漏路径
`should` · 可信度 `high` · 适用: ina199, current-sense, high-side-sense · 标签: cat-feeder

**规则** INA199 无 shutdown 引脚，IQ 典型 65 µA、最大 100 µA（−40~125 °C 最大 115 µA）；睡眠时要么由 GPIO/开关为其供电，要么把这段电流写进预算。其关断状态下，分流电阻两端各有略大于 1 MΩ 的路径通向 OUT 与 REF，泄漏约为共模电压/1 MΩ，具体取决于 REF 和输出下游处于地、有源还是高阻；上电时共模电压 ≥ 3 V 还会在每个输入端多出近恒定的约 25 µA。

**依据** 65–100 µA 的常开电流是深睡 5 µA 的 13–20 倍，也是 AMS1117 之外下一个大项。数据手册第 7.4.2 节专门说明了用逻辑门或晶体管开关给它供电，并要考虑关断时从分流回路漏出去的电流。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ina199_quiescent_current_typ` | == 65 uA | VSENSE = 0 mV，TA 25 °C；最大 100 µA，全温度范围最大 115 µA |
| `ina199_shutdown_input_path_resistance` | == 1 Mohm | 略大于 1 MΩ（1 MΩ 反馈电阻 + 5 kΩ 输入电阻）；共模 5 V 时约 5 µA 为自行折算 |
| `ina199_input_bias_when_powered_cm_above_3V` | == 25 uA | 每个输入端，近恒定且匹配；共模低于 2 V 时只剩 1 MΩ 电阻的影响 |

**验证**
- `bom_check`（partial）· Python 读网表 — 对每个 INA199，检查电源脚是否经开关/GPIO 供电；若常通，把 Iq_max 加入睡眠预算；对关断状态，累加 V_CM / 1 MΩ（两个输入）并检查 REF、OUT 下游是否有源
- `spice`（partial）· ngspice：INA199 关断状态用 1 MΩ 网络建模 — 在电机/负载电压下计算分流回路泄漏
- `bench`（manual）· Joulescope — INA199 供电开/关两种睡眠态测整板电流

**来源**
- [INA199 Bidirectional, Low- and High-Side Current Sense Amplifier (SBOS469H)](https://www.ti.com/lit/ds/symlink/ina199.pdf) — Texas Instruments, datasheet, §6 Electrical characteristics (IQ); §7.4.2 Shutting Down the INA199 Series

<a id="LPW-SCH-011"></a>
#### LPW-SCH-011 · 电池反接保护用低压降 FET，不用串联二极管
`should` · 可信度 `high` · 适用: battery, reverse-polarity, p-mosfet, n-mosfet

**规则** 电池路径上的反接保护优先用低 Rds(on) 的 N-MOS（地回路）或 P-MOS（电源路径），体二极管方向与正常电流同向；不要在低压电池路径上串二极管。要核算最低电池电压下的 Vgs、Rds(on)×I_peak 压降与电池寿命末期余量。

**依据** 串联二极管的压降缩小可用电压范围：TI 例，两节碱性电池 1.8 V 经 0.6 V 二极管只剩 1.2 V，后级升压效率也变差；肖特基的约 0.3 V 对 3 V 电池也是约 10% 的损失。小封装 FET 在 1.8–2.7 V 栅压下 Rds(on) 可到 50–85 mΩ。

| 参数 | 判据 | 备注 |
|---|---|---|
| `series_diode_drop_example` | == 0.6 V | SLVA139 例：1.8 V 电池包减去 0.6 V 余 1.2 V |
| `fet_rds_on_example_max` | <= 85 mohm | SLVA139 表 1 的 SOT-23 示例，PMOS 85 mΩ @2.7 V，NMOS 51–80 mΩ @1.8–2.7 V；器件较老，选型时看现行器件 |

**验证**
- `bom_check`（full）· Python — V_drop = I_peak × Rds(on)_max(Vgs_min, Tmax)，要求 V_battery_min − V_drop ≥ FEP；Vgs_min 取电池放电终点电压
- `spice`（partial）· ngspice — 反接电池（−3 V）下整板电流 < 1 µA 且无导通路径；正接时 FET 完全导通

**来源**
- [SLVA139 Reverse Current/Battery Protection Circuits](https://www.ti.com/lit/an/slva139/slva139.pdf) — Texas Instruments, app_note, Using a Diode; Using a FET; Table 1
- [nPM2100 + nRF54L15 capacitor bank design (Nordic DevZone)](https://devzone.nordicsemi.com/f/nordic-q-a/129254/npm2100-nrf54l15-capacitor-bank-design-for-cr2032-cr2450-and-ble-operation/571568) — Nordic Semiconductor DevZone, forum, Schottky ~300 mV drop wastes ~10% of a 3 V battery (community reply)

<a id="LPW-SCH-013"></a>
#### LPW-SCH-013 · 缓慢升降或不稳定的电源要用电压监控器复位
`should` · 可信度 `high` · 适用: esp32-c3, supervisor, reset, battery, brown-out · 标签: cat-feeder

**规则** 电源缓慢上升/下降（电池放电或充电中）、频繁通断或不稳定（光伏）时，仅靠 CHIP_EN 上的 RC 延时不够，应加阈值约 3.0 V 的电源监控芯片驱动复位；CHIP_EN 不得悬空。电源稳定后到 CHIP_EN 拉高至少 50 µs，复位低电平至少 50 µs；RC 参考 R = 10 kΩ、C = 1 µF。监控芯片自身的 Iq 要计入睡眠预算。

**依据** 乐鑫指出缓慢升降、频繁通断或不稳定电源下 RC 本身可能不足；电压缓慢爬过 ESP32-C3 的 3.0 V 下限时，复位时序得不到保证（半运行状态或写入中断属于推断的后果，需要用扫描测试确认）。

| 参数 | 判据 | 备注 |
|---|---|---|
| `supervisor_threshold` | == 3.0 V | 乐鑫检查表：阈值约 3.0 V 的电源监控芯片 |
| `chip_en_stable_time_min` | >= 50 us | tSTBL，电源稳定后到 CHIP_EN 拉高 |
| `chip_en_reset_time_min` | >= 50 us | tRST，CHIP_EN 低于 VIL_nRST |
| `chip_en_rc_delay` | qualitative | R = 10 kΩ，C = 1 µF，需按实际上电时序调整 |

**验证**
- `bench`（partial）· 可编程电源 + 示波器 — 以 1 mV/s 到 1 V/s 的斜率扫描电源上升/下降，反复循环 100 次，复位输出无抖动，重启后无 Flash/NVS 损坏
- `spice`（partial）· ngspice — RC + 监控器模型，慢斜率 VDD 下 CHIP_EN 在 VDD ≥ 3.0 V 且稳定 ≥ 50 µs 后才拉高

**来源**
- [Schematic Checklist - ESP32-C3 - ESP Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, Chip Power-up and Reset Timing
- [ESP32-C3-WROOM-02 Datasheet](https://documentation.espressif.com/esp32-c3-wroom-02_datasheet_en.pdf) — Espressif, datasheet, Peripheral Schematics: EN RC delay

<a id="LPW-SCH-014"></a>
#### LPW-SCH-014 · 常开轨和备份轨上的大电容要计漏电，优先低漏电类型
`should` · 可信度 `medium` · 适用: capacitor, always-on-rail, backup, bulk-capacitor · 标签: cat-feeder

**规则** 常开轨与备份轨上的大容量电容（铝电解、钽、超级电容、大容量 MLCC）要把绝缘电阻/漏电流纳入睡眠预算，µA 以下的系统优先低漏电类型；漏电要在实际电压、温度和长时间稳定后测量，不要靠短时 IR 测试，也不要随意通断大电容组。

**依据** 大容量电容的漏电可轻易超过 nA 级 RTC 的工作电流。MLCC 的 IR 测试受介质吸收影响，漏电下降很慢，短时测试偏悲观；Nordic 员工提醒电池侧电容必须是低漏电类型，并且切换电容组会从电池抽出很大的脉冲电流。

| 参数 | 判据 | 备注 |
|---|---|---|
| `capacitor_leakage_budget` | minimize uA | 量值取决于电容类型、电压和温度，需查所选电容的数据手册（IR 的 MΩ 或 ΩF 规格，或漏电流公式） |

**验证**
- `bom_check`（partial）· Python：器件参数表中增加 C_leak(V, T) 字段 — 对常开轨上所有 ≥ 10 µF 电容，取数据手册最大漏电并求和，计入 LPW-NET-001 的预算
- `bench`（manual）· SMU 或 Joulescope — 电容充到工作电压后稳定至少数小时，再测电压保持下的漏电；高温复测

**来源**
- [RV-1805-C3 Application Note: RTC Capacitor Backup](https://www.microcrystal.com/fileadmin/Media/Products/RTC/Whitepapers/RV-1805-C3_App-Note_Cap_Backup.pdf) — Micro Crystal, app_note, §3.2 Capacitor characteristics
- [nPM2100 + nRF54L15 capacitor bank design (Nordic DevZone)](https://devzone.nordicsemi.com/f/nordic-q-a/129254/npm2100-nrf54l15-capacitor-bank-design-for-cr2032-cr2450-and-ble-operation/571568) — Nordic Semiconductor DevZone, forum
- [Overcoming Low-IQ Challenges in Low-Power Applications (SLYY203)](https://www.ti.com/lit/pdf/slyy203) — Texas Instruments, app_note, Contributors to IQ

## 网表与约束（netlist）

<a id="LPW-NET-001"></a>
#### LPW-NET-001 · 用 BOM 加网表脚本核算常开轨漏电与 Iq 总和
`should` · 可信度 `medium` · 适用: netlist, bom, always-on-rail, budget · 标签: cat-feeder

**规则** 在网表上标注电源域（常开 / 可切断），用脚本遍历常开轨：器件 Iq/漏电（数据手册最大值，最高工作温度）、电阻支路 V/R、LED 支路、电容漏电、可能的反灌路径，求和后与睡眠预算比较，并输出前 10 名贡献者。每次改板都跑一次。

**依据** 芯片级 5 µA 与板级数十至数百 µA 的差距几乎全来自外围：稳压器 Iq、LED、上拉、分压器、外设。靠人工翻原理图容易漏项，脚本化后每次改板都能自动复核。TI 的输入端折算公式正是这种求和的数学形式。

| 参数 | 判据 | 备注 |
|---|---|---|
| `sleep_budget_margin` | qualitative | 预算余量由项目决定；建议至少预留一项未建模泄漏的空间（经验，不是出处数值） |

**验证**
- `bom_check`（partial）· Python：kicad-cli sch export netlist（XML）+ BOM CSV + 器件参数表（LPW-LIB-001 字段） — 1) 按网络类把每个器件分入常开/可切断域；2) 对每个器件取 Iq_max(Tmax)、漏电，对电阻取 V_rail/R（对端睡眠态为低/地时），对 LED 取 (V−Vf)/R；3) 求和 ≤ 预算；4) 输出 CSV 贡献表。例（示例板 rev B 的 BOM，fxp/cat-feeder）：ESP32-C3-WROOM-02 深睡 5 µA + AMS1117-3.3 Iq ≤ 10 mA + INA199 ≤ 100 µA + LED 支路 + 10 kΩ 上拉×5
- `bench`（manual）· Joulescope / PPK2 — 实测睡眠电流与脚本合计值之差必须能被某项未建模泄漏解释，否则补充模型

**来源**
- [Overcoming Low-IQ Challenges in Low-Power Applications (SLYY203)](https://www.ti.com/lit/pdf/slyy203) — Texas Instruments, app_note, Equation 1 and 'Contributors to IQ'
- [IQ: What it is, what it isn't, and how to use it (SLYT412)](https://www.ti.com/lit/an/slyt412/slyt412.pdf) — Texas Instruments, app_note
- [ESP32-S3 Deep Sleep Power: vs C3 vs C6, Measured](https://www.qoitech.com/blog/esp32-s3-c3-c6-sleep-power-consumption/) — Qoitech, blog, XIAO ESP32-C3 41.6 uA vs 5 uA datasheet

## 器件布局（placement）

<a id="LPW-PLC-001"></a>
#### LPW-PLC-001 · 突发负载的大电容放在电池或电源入口侧，按总电荷定容
`should` · 可信度 `high` · 适用: coin-cell, battery, bulk-capacitor, ble, wifi · 标签: cat-feeder

**规则** 为抑制无线 TX 对电池的峰值电流，在电池或电源入口侧并联低漏电低 ESR 的大电容，让电池只看到平均电流；就近放置，每个电容的地焊盘旁打地过孔。容量按总消耗的电荷而不是峰值定：C = ΔQ / (V_max − V_min)，ΔQ = Q_dis − (V_min / R_i) × t_tot，并校验复充时间 t = R_i × C × ln((V_p − V_min)/(V_p − V_max)) 小于睡眠时间。

**依据** SWRA349 例：R_i 取 1 kΩ、V_max 2.6 V、V_min 2.0 V，BLE 突发（8 mA×4 ms + 30 mA×1 ms）算出约 87 µF，复充约 169 ms；实际 BLE 可小 2–5 倍。并联电容让有效容量提升超过 40%（差的电池）。Nordic 员工的建议同样是把大电容放在 VBAT 侧以减小内阻损耗。ESP32-C3 参考设计在电源入口放 ESD 二极管和至少 10 µF。

| 参数 | 判据 | 备注 |
|---|---|---|
| `coin_cell_bulk_cap_example` | == 87 uF | SWRA349 附录 A 算例，高内阻 1 kΩ 假设；SWRA349 实测时用 100 µF |
| `power_entrance_capacitor_min` | >= 10 uF | 乐鑫 ESP32-C3 检查表：电源入口至少 10 µF，另加 ESD 二极管 |
| `capacitor_recharge_time_limit` | < 1 sleep_interval | 复充时间必须小于睡眠间隔 |

**验证**
- `spice`（partial）· ngspice/LTspice：电池 R_i（取寿命末期值）+ 电容 + 突发负载 — 负载端最低电压 ≥ V_min；睡眠间隔内电容电压恢复到 V_max 以上
- `geometry_script`（partial）· pcbnew Python（参见 ee-pcb-verify 的 geometry 检查器） — 量大电容正极焊盘到电池连接器/电源入口焊盘的走线长度，并算走线电阻，R_trace × I_peak 计入突发压降预算
- `bench`（manual）· 示波器测电池端和模块端电压 — TX 突发期间电池端电流脉冲峰值显著低于负载峰值，模块端电压满足 LPW-ARC-012

**来源**
- [SWRA349 Coin cells and peak current draw](https://www.ti.com/lit/wp/swra349/swra349.pdf) — Texas Instruments, app_note, §4, Appendix A
- [nPM2100 + nRF54L15 capacitor bank design (Nordic DevZone)](https://devzone.nordicsemi.com/f/nordic-q-a/129254/npm2100-nrf54l15-capacitor-bank-design-for-cr2032-cr2450-and-ble-operation/571568) — Nordic Semiconductor DevZone, forum
- [PCB Layout Design - ESP32-C3 - ESP Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, Power Supply

## 布线（routing）

<a id="LPW-RTE-002"></a>
#### LPW-RTE-002 · 突发电流路径要核算走线与过孔的 IR 压降
`should` · 可信度 `medium` · 适用: power-trace, burst-load, esp32-c3 · 标签: cat-feeder

**规则** 电源入口到模块供电脚的走线、过孔电阻与电池内阻、稳压器压降一同计入突发压降预算：V_droop = I_peak × (R_batt + R_trace + R_via + R_ESR)。乐鑫参考布局：3.3 V 主电源线宽不小于 25 mil，VDD3P3 不小于 20 mil，其他电源线 10 mil；主电源线换层至少 2 个过孔。

**依据** 按 R = ρL/(w·t) 自行计算，100 mm 长、0.25 mm 宽的 1 oz 铜线约 0.19 Ω，500 mA 突发就是约 0.1 V，对 3.0 V 的下限和 80 mV 的纹波限值是可观的占用。

| 参数 | 判据 | 备注 |
|---|---|---|
| `main_3v3_trace_width_min` | >= 25 mil | 乐鑫 ESP32-C3 布局指南的芯片级参考；模块设计可作为上限参考 |
| `vdd3p3_trace_width_min` | >= 20 mil | 同上 |
| `power_trace_layer_change_vias_min` | >= 2 pcs | 主电源线换层 |

**验证**
- `geometry_script`（full）· pcbnew Python（读取网络走线段/过孔，按铜厚与宽度算电阻） — 对 5 V 入口→稳压器→3V3→模块脚路径求 Σ R，I_peak = 500 mA 时压降 ≤ 预算（预算 = 3.0 V 下限余量 − 纹波限值，由 LPW-ARC-012 给出）
- `bench`（manual）· 示波器 + 4 线测量 — TX 突发期间测路径两端电压差，与计算值对比

**来源**
- [PCB Layout Design - ESP32-C3 - ESP Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, Power Supply: trace width, layer change
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, Table 5-2 (cumulative input current 0.5 A)

<a id="LPW-RTE-001"></a>
#### LPW-RTE-001 · nA 级高阻节点要短走线并用双面保护环
`consider` · 可信度 `medium` · 适用: high-impedance-node, guard-ring, sense-net

**规则** 对 nA 级及以下的高阻节点（MΩ 级分压器、保持电容节点、传感前端、备份电容）：走线尽量短，周围用连到同电位低阻点的保护环/保护线包围，保护环两面都做，并远离高压差网络和易污染的区域。

**依据** TI 的 AN-241 指出保护环能吸收来自板上其他点的漏电，使表面漏电几乎消除；单面保护效果有限，双面保护对体漏电只能降约一个数量级，取决于板厚和保护环宽度。绝缘材料、表面污染、清洗和涂层对结果的影响不亚于器件本身。

| 参数 | 判据 | 备注 |
|---|---|---|
| `bulk_leakage_reduction_double_sided_guard` | == 10 x | AN-241：双面保护环对体漏电约降一个数量级（约值，取决于板厚与环宽） |

**验证**
- `geometry_script`（partial）· pcbnew Python — 对标注为 HiZ 的网络，枚举其焊盘与走线周围的相邻铜：除保护网络外，邻接铜的最小间距须不小于板厂工艺下限且最好大于其余信号间距；检查保护环在顶底层是否闭合、是否与 HiZ 网络同电位
- `drc`（partial）· KiCad DRC 自定义规则（.kicad_dru） — 对 HiZ 网络类设置较大间距规则，具体数值由项目按 LPW-MFG-001 的工艺条件决定（不是出处数值）
- `bench`（manual）· SMU 或皮安表，做 85%RH 前后对比 — 测节点对相邻网络的漏电阻，保护环有无的对比

**来源**
- [AN-241 Working with High Impedance Op Amps (LM11)](https://www.ti.com/lit/an/snoa664/snoa664.pdf) — Texas Instruments / National Semiconductor, app_note, Electrical Guarding
- [Layout for Precision Op Amps](https://www.analog.com/en/technical-articles/layout-for-precision-op-amps.html) — Analog Devices, app_note, (仅在搜索摘要中看到，页面抓取超时，未读原文)

## 出图与制造（manufacturing）

<a id="LPW-MFG-002"></a>
#### LPW-MFG-002 · 预留可单独测量睡眠电流的断点或测试点
`should` · 可信度 `medium` · 适用: test-point, current-measurement, jumper · 标签: cat-feeder

**规则** 在电池/电源入口或 MCU 电源轨预留可串入电流表的跳线、0 Ω 焊盘或断点，以及可隔离其他电路的方法，使整板或 MCU 的睡眠电流可单独测量；调试口和串口桥要能断电。

**依据** Nordic 指出，与其他电路共用电源会让测量失去意义，应提供单独测 SoC 电流的方法；调试接口连接时外设会保持开启、增加电流。没有这类断点，板级睡眠验证（LPW-VER-003）只能靠拆件。

**验证**
- `review`（manual）· 原理图/PCB 评审 — 检查电源入口和 MCU 3V3 轨是否有串联断点；电源 LED、串口桥是否可断开；断点后寄生路径（USB 串口、调试器）不会反灌
- `bom_check`（full）· Python 读 BOM/网表 — 检查 3V3 主轨与 5 V 入口上是否存在标注为 CURRENT_BREAK 的跳线/测试点位号；缺失则报告

**来源**
- [Optimizing Power on nRF52 Designs](https://devzone.nordicsemi.com/nordic/nordic-blog/b/blog/posts/optimizing-power-on-nrf52-designs) — Nordic Semiconductor, blog, Measurement
- [EFM32 Energy Optimization (mirror of Silicon Labs AN0027 §4)](http://efm32.blogspot.com/2016/10/efm32-energy-optimization.html) — Silicon Labs EFM32 Playground (blog), blog, Measurement Tips: debugger effects

<a id="LPW-MFG-001"></a>
#### LPW-MFG-001 · 对 nA 级高阻节点规定清洗与涂覆工艺并验证
`consider` · 可信度 `medium` · 适用: cleaning, conformal-coating, flux-residue, high-impedance-node

**规则** 板上若有 nA 级以下的高阻节点（见 LPW-RTE-001），装配说明要明确清洗（去除助焊剂残留）和涂覆/灌封要求，并用清洗前后、高湿前后的漏电对比来验证；潮湿环境用涂层作防潮屏障。

**依据** TI 的 AN-241 指出，绝缘材料、表面污染、清洗工艺、表面涂层和灌封对高阻电路的影响不亚于元件本身，阻抗越高越重要。ADI 也建议清洁绝缘表面去除助焊剂残留，湿度大的环境加表面涂层。

**验证**
- `review`（manual）· 装配图纸/工艺文件评审 — 确认工艺文件有清洗与涂覆条款；与 SMT 厂商（如 JLC）确认其默认助焊剂类型和是否清洗，其默认工艺本次未查证
- `bench`（manual）· SMU/皮安表 + 恒温恒湿箱 — 测高阻节点对邻网络的漏电阻，清洗前后、25 °C/50%RH 与 40 °C/85%RH 各一次，比较是否满足睡眠预算

**来源**
- [AN-241 Working with High Impedance Op Amps (LM11)](https://www.ti.com/lit/an/snoa664/snoa664.pdf) — Texas Instruments / National Semiconductor, app_note, Reliability
- [Layout for Precision Op Amps](https://www.analog.com/en/technical-articles/layout-for-precision-op-amps.html) — Analog Devices, app_note, (仅在搜索摘要中看到，页面抓取超时，未读原文)

## 签核验证（verification）

<a id="LPW-VER-003"></a>
#### LPW-VER-003 · 在真实板、真实固件、真实电压下验收睡眠电流
`must` · 可信度 `high` · 适用: measurement, esp32-c3, firmware, board-level · 标签: cat-feeder

**规则** 芯片数据手册的 Deep-sleep 值只适用于芯片本身（3.3 V、25 °C、RTC 定时器加 RTC 内存）。验收值必须在目标板、目标固件、目标供电电压（使板载稳压器有足够裕量）下测量，并断开调试器和串口桥后重新上电；设定睡眠电流门限并保存测试日志。

**依据** Qoitech 实测 XIAO ESP32-C3 开发板 deep-sleep 为 41.6 µA（芯片 5 µA、Seeed 标称 44 µA），一次对驱动 LED 的 GPIO 调用 gpio_deep_sleep_hold_en 就让读数变成 461 µA；他们为让板载 LDO 工作把电源设在 3.8 V，而不是数据手册的 3.3 V。Nordic 与 Silicon Labs 都提醒调试接口连接或日志串口会增加电流。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esp32c3_deep_sleep_chip_typ` | == 5 uA | 数据手册表 5-9 |
| `example_board_level_deep_sleep` | == 41.6 uA | Qoitech 实测 XIAO ESP32-C3，板载 LDO、电池管理、USB 桥、Flash 等 |

**验证**
- `bench`（partial）· Joulescope/PPK2 + 脚本断言 — 刷入量产固件，断开调试器，上电后进入深睡，稳定若干秒后取至少 15 s 平均值，≤ 睡眠预算；输出 CSV 与固件版本、供电电压、温度一同归档

**来源**
- [ESP32-S3 Deep Sleep Power: vs C3 vs C6, Measured](https://www.qoitech.com/blog/esp32-s3-c3-c6-sleep-power-consumption/) — Qoitech, blog
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, §5.6 Current Consumption (3.3 V, 25 °C test condition)
- [Optimizing Power on nRF52 Designs](https://devzone.nordicsemi.com/nordic/nordic-blog/b/blog/posts/optimizing-power-on-nrf52-designs) — Nordic Semiconductor, blog, Debug mode, UART logging
- [EFM32 Energy Optimization (mirror of Silicon Labs AN0027 §4)](http://efm32.blogspot.com/2016/10/efm32-energy-optimization.html) — Silicon Labs EFM32 Playground (blog), blog, Measurement Tips: debugger effects

<a id="LPW-VER-005"></a>
#### LPW-VER-005 · 无线突发时在负载端实测电压跌落与纹波
`must` · 可信度 `high` · 适用: wifi, ble, burst-load, esp32-c3 · 标签: cat-feeder

**规则** 在最差电池状态（低温、老化高内阻、低电量）下，用示波器在模块供电脚测 TX 突发期间的最低电压和纹波：最低电压不低于 3.0 V（ESP32-C3 下限），TX 时纹波峰值低于 80 mV（MCS7）或 120 mV（11 Mbps）；复位/BOR 事件为 0。仿真时用电池内阻加电容加突发负载阶跃。

**依据** 电压跌落造成复位或掉电；电源纹波会直接恶化 TX 性能。Energizer 与 Nordic 也指出：大的电源瞬态正好出现在接收包期间时会破坏接收，表现为射频距离差而不稳定。

| 参数 | 判据 | 备注 |
|---|---|---|
| `min_rail_voltage_during_tx` | >= 3.0 V | ESP32-C3 推荐电压下限 |
| `tx_ripple_peak_mcs7` | < 80 mV | 802.11n MCS7 发射 |
| `tx_ripple_peak_11mbps` | < 120 mV | 11 Mbps 发射 |

**验证**
- `bench`（partial）· 示波器（带宽 ≥ 100 MHz，带 20 MHz 带宽限制与接地弹簧）+ 可调 V_bat/源阻抗的电池模拟器 — 触发在 TX 起点，记录 3V3 引脚最小电压与纹波峰值；遍历最差电源条件和各 TX 速率；记录复位次数
- `spice`（partial）· ngspice — 按 LPW-ARC-012 的模型，TX 阶跃下负载端最小电压满足上表

**来源**
- [Schematic Checklist - ESP32-C3 - ESP Hardware Design Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, Power Supply
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, Tables 5-2, 5-7
- [High pulse drain impact on CR2032 coin cell battery capacity](https://devzone.nordicsemi.com/cfs-file/__key/communityserver-discussions-components-files/4/0842.High-pulse-drain-impact-on-CR2032-coin-cell-battery-capacity.pdf) — Nordic Semiconductor / Energizer, app_note, Battery capacity vs. peak currents

<a id="LPW-VER-001"></a>
#### LPW-VER-001 · 选对测睡眠电流的仪表：burden 电压、量程与分辨率
`should` · 可信度 `high` · 适用: measurement, sleep-current, power-profiler · 标签: cat-feeder

**规则** 测睡眠电流要同时看三点：1) 串联仪表的压降（burden voltage）小到不影响被测电路（Joulescope 把分流电阻上的压降控制在约 20 mV，1 A 时总压降 25 mV；普通万用表压降大得多）；2) 分辨率和精度够用：PPK2 在 200 nA–50 µA 分辨率 0.2 µA、平均值精度 ±10%，极低静态电流下读数不准，nA 级用 Joulescope（最低 0.5 nA 分辨率）、Otii（0.4 nA 分辨率）或 SMU；3) 量程切换为先接通后断开，切换时间满足 t ≳ C·ΔV/ΔI。

**依据** 量程切换的压降和瞬态会让被测电路复位或读数偏高；低量程的分流电阻大（Joulescope 18 µA 量程为 1111 Ω），电流突增时压降随之增大。PPK2 的用户指南把测量范围写成 500 nA 到 1 A，同时说明能准确测到约 200 nA，指南内部也有不一致，nA 级结论需要用更高分辨率仪表复核。

| 参数 | 判据 | 备注 |
|---|---|---|
| `shunt_burden_voltage_target` | <= 20 mV | Joulescope JS220 的设计目标（分流电阻上的最大压降），可作为自选仪表的参考，不是标准值 |
| `ppk2_resolution_200nA_to_50uA` | == 0.2 uA | PPK2 用户指南表 8；精度 ±10% 读平均值，偏置 ±2% |
| `joulescope_js220_resolution` | == 0.5 nA | Joulescope JS220 用户指南；18 µA 量程分流电阻 1111 Ω |

**验证**
- `bench`（manual）· Joulescope JS220 / Nordic PPK2 / Qoitech Otii / SMU — 测前用已知电流源（如 1 µA、10 µA 的恒流源或精密电阻 + 电压源）校核仪表读数；记录量程切换点上是否出现复位或读数突变；仪表误差大于睡眠电流的 10% 时换更高分辨率仪表

**来源**
- [Joulescope JS220 User's Guide](https://download.joulescope.com/products/JS220/JS220-K000/users_guide/Joulescope%20JS220%20User's%20Guide.pdf) — Jetperch, tool_doc, §2, §7.5, §10.1 Ammeter and Autoranging
- [Power Profiler Kit II User Guide v1.0.1](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/7735/PPK2_User_Guide.pdf) — Nordic Semiconductor, tool_doc, §1, §8.3.2, §8.3.3
- [Optimizing Power on nRF52 Designs](https://devzone.nordicsemi.com/nordic/nordic-blog/b/blog/posts/optimizing-power-on-nrf52-designs) — Nordic Semiconductor, blog, Measurement (PPK readings inaccurate at very low static current)
- [ESP32-S3 Deep Sleep Power: vs C3 vs C6, Measured](https://www.qoitech.com/blog/esp32-s3-c3-c6-sleep-power-consumption/) — Qoitech, blog, Measurement setup (Otii Ace Pro, 0.4 nA resolution)

<a id="LPW-VER-002"></a>
#### LPW-VER-002 · 平均电流用整个占空周期的累计电荷来测
`should` · 可信度 `high` · 适用: measurement, duty-cycle, battery-life · 标签: cat-feeder

**规则** 测量窗口覆盖完整占空周期（睡眠、唤醒、联网、最长事件），用仪表的电荷/能量累计功能得出平均电流，并按状态分段积分；最坏模式（连接重建、报警、频繁短周期）也要测，电池寿命取最坏模式的平均电流。

**依据** 瞬时读数无法代表占空比极低的系统。Energizer 与 Nordic 指出，应用寿命周期内可能进入的最短脉冲周期才是寿命估算要用的模式，即使它只占很小比例，也会在电池容量接近耗尽时让系统复位。

**验证**
- `bench`（partial）· Joulescope / PPK2 / Otii，软件导出 CSV — 脚本按 GPIO 标记（睡眠/TX/传感）分段积分，输出每段电荷、总平均电流、最大电流、与 LPW-ARC-001 预算表逐项对比
- `review`（manual）· 评审清单 — 确认测试覆盖最坏模式（例如周期最短的连接事件、失联重连），并记录测试持续时间 ≥ 若干个完整周期

**来源**
- [High pulse drain impact on CR2032 coin cell battery capacity](https://devzone.nordicsemi.com/cfs-file/__key/communityserver-discussions-components-files/4/0842.High-pulse-drain-impact-on-CR2032-coin-cell-battery-capacity.pdf) — Nordic Semiconductor / Energizer, app_note, Battery capacity vs. pulse duty cycle; Summary items 3 and 5
- [Power Profiler Kit II User Guide v1.0.1](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/7735/PPK2_User_Guide.pdf) — Nordic Semiconductor, tool_doc, §1 (accumulative measurements: average, maximum, charge)
- [EFM32 Energy Optimization (mirror of Silicon Labs AN0027 §4)](http://efm32.blogspot.com/2016/10/efm32-energy-optimization.html) — Silicon Labs EFM32 Playground (blog), blog, energyAware Profiler time-span average

<a id="LPW-VER-004"></a>
#### LPW-VER-004 · 睡眠电流要在高低温下复测，并按最坏温度做预算
`should` · 可信度 `high` · 适用: measurement, temperature, leakage, battery-life

**规则** Iq、关断电流和漏电随温度和电压上升，常常是非线性的，睡眠预算用数据手册最大值（最高工作温度和存放温度），并在温箱里于最低、常温、最高温度各测一次睡眠电流。

**依据** TI 的 SLVA757 显示负载开关的 Iq 与 ISD 随温度和 VIN 增大（图 2–4，-40 到 105 °C）；SSZT118 提到货架或仓库的高温环境会加速电池自放电。TPS22916 的 ISD 典型 10 nA、−40~85 °C 最大 100 nA，相差十倍。

| 参数 | 判据 | 备注 |
|---|---|---|
| `example_isd_typ_vs_max_ratio` | == 10 x | TPS22916 ISD：典型 10 nA，−40~85 °C 最大 100 nA |

**验证**
- `bench`（partial）· 恒温箱 + Joulescope — −10 / 25 / 60 °C（或产品额定温度）各稳定 30 min 后测睡眠电流，对比预算；记录是否出现非线性拐点
- `spice`（partial）· ngspice 温度扫描 .step temp（使用带温度特性的器件模型） — 漏电类器件模型的 ISD 随温度变化趋势与数据手册曲线一致，总和满足预算

**来源**
- [SLVA757 Quiescent Current vs Shutdown Current for Load Switch Power Consumption](https://www.ti.com/lit/pdf/slva757) — Texas Instruments, app_note, §3, §5, §9 Key Takeaways
- [3 Quiescent-current (Iq) Specifications to Understand (SSZT118)](https://www.ti.com/lit/pdf/sszt118) — Texas Instruments, app_note, Shutdown Current
- [TPS22916 Ultra-Low Leakage Load Switch](https://www.ti.com/lit/ds/symlink/tps22916.pdf) — Texas Instruments, datasheet

<a id="LPW-VER-006"></a>
#### LPW-VER-006 · 电池寿命模型要与实测对账，厂商工具只作初估
`consider` · 可信度 `medium` · 适用: battery-life, modeling, spreadsheet, spice

**规则** 可用 TI Battery Lifetime Calculator、Nordic Online Power Profiler 等做初估，但模型必须覆盖转换器效率、电池内阻与容量降额、温度，并用实测对账；偏差超过仪表精度时回查模型假设。换到其他 SoC 时不要沿用别的芯片的工具结果。

**依据** Nordic 员工说明，Online Power Profiler 针对 nRF52832，用于 nRF52840 时可能有偏差，建议用 PPK 实测；TI 的 Battery Lifetime Calculator 能导入电池放电曲线、转换器参数和负载曲线，但仍是模型。

**验证**
- `bom_check`（partial）· Python/电子表格模型（效率曲线、电池曲线、负载曲线） — 模型与实测累计电荷偏差 ≤ 仪表精度的两倍，超出则输出差异项（哪个状态、哪个器件）
- `review`（manual）· 评审清单 — 确认模型使用的容量是降额后容量，使用的是最坏温度与最坏模式

**来源**
- [SLVAER8A Extending Battery Life With Low Quiescent Current and Dynamic Voltage Scaling](https://www.ti.com/lit/an/slvaer8a/slvaer8a.pdf) — Texas Instruments, app_note, §2 (Battery Lifetime Calculator)
- [Estimation of battery life while only advertising (Nordic DevZone)](https://devzone.nordicsemi.com/f/nordic-q-a/35072/estimation-of-battery-life-while-only-advertising) — Nordic Semiconductor DevZone, forum

