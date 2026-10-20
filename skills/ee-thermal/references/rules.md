# 热设计（thermal）— 规则全文

横向领域 · 28 条规则 · 由 `catalog/*.yaml` 生成，请改 YAML 不要改本文件。用 `grep -n "<规则ID>" rules.md` 定位单条，不要整份读。

环节分布：架构与选型 8，符号封装库 1，叠层与规则 3，器件布局 2，布线 5，平面与铺铜 3，出图与制造 1，签核验证 5

## 架构与选型（architecture）

<a id="THM-ARC-001"></a>
#### THM-ARC-001 · 数据手册的 θJA 只对它的测试板成立
`must` · 可信度 `high` · 适用: all-ics, ldo, mosfet · 标签: cat-feeder

**规则** 不要把数据手册的 θJA 直接代入自己的板子算结温；每次引用 θJA 都记下它的测试板条件（JESD51 的 1s / 2s2p、尺寸、铜厚、气流），再用实测或建模得到自己板子的有效 θJA（θJA,effective）。

**依据** θJA 不是封装的固有属性。JEDEC 静止空气下 70–95% 的热量经测试板散出，测试板就是散热器；板子设计对 θJA 的影响强度约 100%，远大于环境温度（7%）和功耗（3%）。

| 参数 | 判据 | 备注 |
|---|---|---|
| `heat_fraction_through_pcb` | 70 … 95 % | JEDEC 静止空气测试里经测试板散出的比例 |
| `theta_ja_1s_vs_2s2p_variation` | <= 50 % | 同一封装仅因 1s 与 2s2p 测试板不同，θJA 可差到约 50% |

**验证**
- `review`（manual）· BOM 器件热数据表 — 对每个功耗 > 0.1 W 的器件，表中记录 θJA 值及其测试板条件（来自数据手册脚注）；没有条件说明的 θJA 标记为不可信
- `thermal_sim`（partial）· 热阻网络估算（见 THM-VER-005）或实测 — 得到自己板子的 θJA,effective 并用于 THM-ARC-002 的结温计算

**来源**
- [SPRA953 Semiconductor and IC Package Thermal Metrics](https://www.ti.com/lit/an/spra953d/spra953d.pdf) — Texas Instruments, app_note, §1 RθJA, §1.1 Usage, Table 1-1
- [AN-2020 Thermal Design By Insight, Not Hindsight](https://www.ti.com/lit/an/snva419c/snva419c.pdf) — Texas Instruments, app_note, §2
- [AO3400A 30V N-Channel MOSFET datasheet](https://www.aosmd.com/res/data_sheets/AO3400A.pdf) — Alpha and Omega Semiconductor, datasheet, Thermal Characteristics, note A
- JESD51 series (Methods for measuring thermal characteristics of IC packages)（JEDEC JESD51-1, -2, -5, -6, -7） — JEDEC, standard

<a id="THM-ARC-002"></a>
#### THM-ARC-002 · 在最高环境温度下算每个发热件的结温
`must` · 可信度 `high` · 适用: ldo, mosfet, all-ics · 标签: cat-feeder

**规则** 对每个功耗显著的器件按 Tj = Ta,max + P × θJA,effective 计算结温，Ta,max 取外壳内最高环境（不是室温），Tj 必须低于数据手册允许的最高结温并留设计余量；数据手册的额定功率 / 电流是在 25 °C 下给的，要按 Ta,max 降额。热关断阈值只是保护，不是设计余量。

**依据** 可靠性取决于结温而不是环境温度；功率额定值随环境温度升高而下降。例如 AO3400A 的 PD 在 25 °C 为 1.4 W，70 °C 降为 0.9 W；AMS1117 的结温上限为 125 °C，而热关断在约 165 °C 才触发。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ams1117_tj_max` | <= 125 °C | 数据手册：最高结温不得超过 125 °C |
| `ams1117_thermal_shutdown` | == 165 °C | 保护阈值，不作为设计余量 |
| `ao3400a_tj_max` | <= 150 °C |  |
| `ao3400a_pd_25c` | == 1.4 W | 基于 θJA ≤ 10 s 值与 1 in² 2 oz 铜板 |
| `ao3400a_pd_70c` | == 0.9 W |  |
| `tj_design_margin` | qualitative | 余量取多少没有统一规定；邻近元件的额定温度可能比器件本身更严（见 THM-PLC-001） |

**验证**
- `thermal_sim`（full）· Python 脚本：器件功耗表 + θJA,effective + Ta,max — 对每个器件计算 Tj，要求 Tj ≤ Tj,max − 余量；列出余量最小的 3 个器件
- `bench`（manual）· 热电偶 / 热像仪（见 THM-VER-001、THM-VER-002） — 在 Ta,max 与最大负载下实测外壳温度并换算 Tj，与计算值相差应能解释

**来源**
- [SPRA953 Semiconductor and IC Package Thermal Metrics](https://www.ti.com/lit/an/spra953d/spra953d.pdf) — Texas Instruments, app_note, §6, §7 (operating temperature definitions)
- [AMS1117 datasheet](https://www.handsontec.com/dataspecs/AMS1117.pdf) — Advanced Monolithic Systems, datasheet, Absolute Maximum Ratings; Thermal Considerations
- [AO3400A 30V N-Channel MOSFET datasheet](https://www.aosmd.com/res/data_sheets/AO3400A.pdf) — Alpha and Omega Semiconductor, datasheet, Absolute Maximum Ratings
- [AN-1028 Maximum Power Enhancement Techniques for Power Packages](https://www.ti.com/lit/pdf/snva036) — Texas Instruments, app_note, §2 Theory, eq. 1

<a id="THM-ARC-003"></a>
#### THM-ARC-003 · 线性稳压器的功耗按最坏输入电压和最大电流算
`must` · 可信度 `high` · 适用: ldo, ams1117, sot-223 · 标签: cat-feeder

**规则** LDO（含 AMS1117）的功耗 PD = (Vin − Vout) × Iout，取最高输入电压与最大负载电流；由 (Tj,max − Ta,max)/PD 得到允许的 θJA，大于板子能实现的 θJA 时，加铜皮、降低输入电压（前级降压 / 压降电阻）或换开关稳压器。

**依据** LDO 把压差全部变成热。AMS1117 在 SOT-223 上数据手册 θJA 约 90 °C/W（46 到 >90 °C/W，取决于铜皮和安装），结温上限 125 °C，裕量很容易被吃光。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ams1117_theta_jc_tab` | == 15 °C/W | 结到散热片（tab） |
| `ams1117_sot223_theta_ja_datasheet` | == 90 °C/W | 带星号：可从 46 变到 >90，取决于铜皮和安装方式 |
| `ams1117_theta_ja_best_case` | >= 45 °C/W | 数据手册称总热阻可低至 45 °C/W，需要大的 PCB 并至少一层铜皮散热 |

**验证**
- `thermal_sim`（full）· Python / 表格 — PD = (Vin_max − Vout) × Iout_max；θJA,needed = (125 − Ta,max)/PD；要求 θJA,needed ≥ 板子 θJA,effective（见 THM-PLN-001 的铜皮面积表）
- `bench`（manual）· 热电偶贴 tab / 热像仪 — 在最高输入电压、最大负载（Wi-Fi 峰值）下实测 tab 温度，再按 Tj = Ttab + PD × 15 °C/W 估算结温

**来源分歧** 不同厂家的 AMS1117 / 1117 系列数据手册给出的 SOT-223 θJA 差别很大（88、117、136、150 °C/W 都出现过）。以所选料号对应厂家的数据手册为准，并按自己板子的铜皮面积估算；不要用一个通用数字。

**来源**
- [AMS1117 datasheet](https://www.handsontec.com/dataspecs/AMS1117.pdf) — Advanced Monolithic Systems, datasheet, Absolute Maximum Ratings; Thermal Considerations
- [Understanding Thermal Characteristic of SOT-223 Package (AN044)](https://www.richtek.com/Design%20Support/Technical%20Document/AN044?sc_lang=en) — Richtek, app_note

<a id="THM-ARC-006"></a>
#### THM-ARC-006 · MOSFET 导通损耗按热态 Rds(on) 算
`must` · 可信度 `high` · 适用: mosfet, motor-driver, ao3400a · 标签: cat-feeder

**规则** MOSFET 导通损耗 P = I² × Rds(on)，Rds(on) 取工作结温下、与实际栅压对应的最大值（不是 25 °C 典型值）；数据手册给出的热阻（以及与之关联的电流、功耗额定值）基于其测试板，换板后重新核算。

**依据** Rds(on) 随结温上升（AO3400A VGS = 10 V：25 °C 时典型 18 mΩ、最大 26.5 mΩ，125 °C 时典型 28 mΩ、最大 38 mΩ）；其 θJA 是在 1 in² 2 oz 铜 FR-4 板上测的（稳态典型 100、最大 125 °C/W），功耗额定值由该热阻推出（5.7 A 的连续电流额定值与之关联）。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ao3400a_rds_on_hot_over_cold` | 1.43 … 1.56 x | 由数据手册 125 °C 与 25 °C 的最大 / 典型值之比推出（38/26.5、28/18） |
| `ao3400a_rds_on_vgs_2p5v_max` | <= 48 mOhm | 25 °C，VGS = 2.5 V，ID = 3 A；栅极由 3.3 V 驱动时，按 2.5 V 行取保守值 |
| `ao3400a_theta_ja_steady_max` | == 125 °C/W | 稳态最大，1 in² 2 oz 铜 FR-4 板 |

**验证**
- `thermal_sim`（full）· Python 脚本：I²·Rds(on)(Tj) 与 Tj = Ta + P·θJA 迭代 — 例：2 A、热态 Rds(on) 约 48 mΩ × 1.4 ≈ 67 mΩ → P ≈ 0.27 W；θJA 125 °C/W 时温升约 34 °C；叠加 Ta,max 后 Tj < 150 °C 并有余量
- `bom_check`（manual）· 器件数据手册表 — 数据手册热阻所依赖的测试板（铜面积、铜厚）与自己板子对比，不一致时降额

**来源**
- [AO3400A 30V N-Channel MOSFET datasheet](https://www.aosmd.com/res/data_sheets/AO3400A.pdf) — Alpha and Omega Semiconductor, datasheet, Electrical Characteristics RDS(ON); Thermal Characteristics notes A, D
- [AN-1028 Maximum Power Enhancement Techniques for Power Packages](https://www.ti.com/lit/pdf/snva036) — Texas Instruments, app_note, §2, Appendix A

<a id="THM-ARC-004"></a>
#### THM-ARC-004 · 2 层板上预期 θJA 比 4 层测试板的数据差
`should` · 可信度 `medium` · 适用: 2-layer, qfn, exposed-pad, sot-223 · 标签: cat-feeder

**规则** 数据手册的 θJA 来自 4 层高 K 板（JEDEC 2s2p / JESD51-7）时，2 层板上的有效 θJA 预期更高；没有 1s 值可用时，计算按 θJA 增大约 30–50% 取悲观值，并用实测修正。

**依据** TI 称裸露焊盘封装的 θJA 基于带过孔的 4 层高 K 板；JEDEC 1s 与 2s2p 对同一封装可差约 50%，而 4 层内部地平面可把一块设计良好的 2 层板再改善最多约 30%。

| 参数 | 判据 | 备注 |
|---|---|---|
| `theta_ja_penalty_2layer_vs_2s2p` | 1.3 … 1.5 x | 由 30% 与 50% 两个来源数字推出，并非原文直接给出的倍数；confidence 因而取 medium |

**验证**
- `thermal_sim`（partial）· 热阻网络估算（THM-VER-005）或实测 — 对 2 层板上的主要发热件，用悲观 θJA（数据手册值 × 1.3–1.5）重算 THM-ARC-002，仍满足 Tj 限值，或改用 1s / 实测值

**来源**
- [SLUA271 QFN and SON PCB Attachment](https://www.ti.com/lit/an/slua271d/slua271d.pdf) — Texas Instruments, app_note, §3.4
- [SPRA953 Semiconductor and IC Package Thermal Metrics](https://www.ti.com/lit/an/spra953d/spra953d.pdf) — Texas Instruments, app_note, §1.2 Test Card Impact
- [AN-2020 Thermal Design By Insight, Not Hindsight](https://www.ti.com/lit/an/snva419c/snva419c.pdf) — Texas Instruments, app_note, §3.1

<a id="THM-ARC-008"></a>
#### THM-ARC-008 · 铝电解电容按本体温度算寿命并远离热源
`should` · 可信度 `medium` · 适用: electrolytic-capacitor, bulk-capacitor · 标签: cat-feeder

**规则** 估算电解电容的寿命时用电容本体的实际温度（局部环境温度加纹波电流自热），而不是整机环境温度；工作温度每降低 10 °C，寿命大约翻倍；选额定温度高一档（如 105 °C）的型号，并避免放在 LDO、MOSFET、电感等热源旁。

**依据** 非固态铝电解电容的电解液蒸发遵循 Arrhenius 规律，寿命强烈依赖芯子温度，纹波电流自热又会进一步抬高芯子温度；「10 °C 法则」是各厂家通用的估算方法。

| 参数 | 判据 | 备注 |
|---|---|---|
| `life_doubling_per_delta_t` | == 10 °C | 寿命每降 10 °C 翻倍（10-degree rule）；来自二手资料对各厂家方法的归纳 |

**验证**
- `bom_check`（partial）· 电容数据手册寿命曲线 / 厂商寿命计算器（如 TDK AlCap） — 输入局部环境温度、纹波电流与额定纹波比，得到的预期寿命满足产品寿命要求
- `bench`（manual）· 热电偶贴电容外壳 — 满载稳态时电容外壳温度比额定上限低至少 10–20 °C（具体按寿命目标）

**来源分歧** 没能读到 Nichicon / Panasonic / Rubycon 等厂家的原版寿命文档（均无法获取），翻倍规则的出处只有 Wikipedia 对各厂家方法的归纳；TDK 文档确认了 Arrhenius 关系和芯子温度决定寿命，但页面里没有直接写出 10 °C 翻倍的数字。

**来源**
- [Aluminum electrolytic capacitors: General technical information](https://www.tdk-electronics.tdk.com/blob/185386/download/4/pdf-generaltechnicalinformation.pdf) — TDK Electronics (EPCOS), vendor_guide, §4 Ripple current / §5 Useful life
- [Electrolytic capacitor (Lifetime and the 10-degree rule)](https://en.wikipedia.org/wiki/Electrolytic_capacitor) — Wikipedia, blog, Lifetime

<a id="THM-ARC-005"></a>
#### THM-ARC-005 · 高海拔使用时放大 θJA
`consider` · 可信度 `high` · 适用: altitude

**规则** 产品可能在高海拔使用时，把海平面测得 / 给出的 θJA 乘以海拔系数：3000 ft 约 1.1、5000 ft 约 1.14、7000 ft 约 1.17、8350 ft 约 1.2。

**依据** 空气变稀使对流散热变差；IBM 的研究显示 8000 ft 处器件会比海平面热约 20%。

| 参数 | 判据 | 备注 |
|---|---|---|
| `altitude_factor_3000ft` | == 1.1 x |  |
| `altitude_factor_5000ft` | == 1.14 x |  |
| `altitude_factor_7000ft` | == 1.17 x |  |
| `altitude_factor_8350ft` | == 1.2 x |  |

**验证**
- `thermal_sim`（full）· 热阻网络估算脚本 — 把 θJA,effective 乘上目标海拔系数后重算 Tj，仍满足 THM-ARC-002

**来源**
- [SPRA953 Semiconductor and IC Package Thermal Metrics](https://www.ti.com/lit/an/spra953d/spra953d.pdf) — Texas Instruments, app_note, §1.5 Altitude, Table 1-2

<a id="THM-ARC-007"></a>
#### THM-ARC-007 · 电机堵转 / 启动的脉冲要对照 MOSFET SOA
`consider` · 可信度 `low` · 适用: mosfet, motor-driver, ao3400a · 标签: cat-feeder

**规则** 对电机堵转、启动冲击等脉冲电流，在 MOSFET 的 SOA 曲线上按脉宽和电压核对工作点；注意 SOA 曲线是单脉冲、在其测试板热阻下得到的，重复脉冲或换板要降额。

**依据** SOA 曲线基于特定板的结到环境热阻和 Tj,max；板子散热更差、脉冲重复时，实际可用区域更小。

**验证**
- `review`（manual）· 数据手册 SOA 曲线 + 电机堵转电流测量 — 在示波器上测堵转电流与持续时间，落在 SOA 曲线对应脉宽的下方并有余量；固件应有限流或超时保护
- `spice`（partial）· ngspice + 厂商 MOSFET 热子电路模型（如有） — 堵转瞬态下 Tj 峰值 < Tj,max

**来源分歧** 本库只读到该数据手册对 SOA 曲线的脚注（单脉冲、基于其热阻测试板），没有找到关于电机类负载 SOA 评估方法的更权威来源，因此 confidence 为 low。

**来源**
- [AO3400A 30V N-Channel MOSFET datasheet](https://www.aosmd.com/res/data_sheets/AO3400A.pdf) — Alpha and Omega Semiconductor, datasheet, Thermal Characteristics note F (SOA curve)

## 符号封装库（library）

<a id="THM-LIB-001"></a>
#### THM-LIB-001 · 带裸露焊盘的封装必须有等大的散热焊盘并焊在板上
`must` · 可信度 `high` · 适用: qfn, son, powerpad, exposed-pad, module · 标签: cat-feeder

**规则** 所有带裸露散热焊盘（QFN、SON、PowerPAD、模块底部地焊盘）的封装，PCB 上的散热焊盘做成与封装裸露焊盘等大（TQFP 类按数据手册的最大尺寸）；散热焊盘与引脚焊盘间距 ≥ 0.2 mm；该焊盘必须焊接到板上，不能省略。

**依据** 数据手册的热性能以焊接状态为前提，不焊接则热量排不出去，影响性能和可靠性。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ep_land_to_lead_pad_gap` | >= 0.2 mm | TI：经验表明 0.2 mm 对大多数设计足够，防桥连 |
| `chip_ground_pad_min_vias` | >= 9 pcs | Espressif 对芯片底部地焊盘的要求（至少 9 个地过孔）；模块的地焊盘以模块规格书为准 |

**验证**
- `geometry_script`（partial）· pcbnew Python — 对每个带 EP 的封装，PCB 上散热焊盘面积与数据手册裸露焊盘面积之比在 0.95–1.0；与最近引脚焊盘间距 ≥ 0.2 mm；该焊盘有网络（通常 GND）且连接到铜皮

**来源**
- [SLUA271 QFN and SON PCB Attachment](https://www.ti.com/lit/an/slua271d/slua271d.pdf) — Texas Instruments, app_note, §3.4 Exposed Pad PCB Design
- [SLMA002 PowerPAD Thermally Enhanced Package](https://www.ti.com/lit/an/slma002h/slma002h.pdf) — Texas Instruments, app_note, §2.4 Thermal Vias; Summary
- [ESP32-C3 Hardware Design Guidelines: PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, Ground pad / thermal pad (EPAD)

## 叠层与规则（stackup）

<a id="THM-STK-001"></a>
#### THM-STK-001 · 按功耗选铜厚
`consider` · 可信度 `high` · 适用: power, 2-layer · 标签: cat-feeder

**规则** 对 DC-DC 类功率器件，铜厚至少 1 oz；功耗 > 3 W 用 2 oz；> 6 W 用 4 oz。2 层板上用 2 oz 替代 1 oz 可让 θJA 下降约 25%（同一块 3×3 in 板 28.3 → 21.2 °C/W）。

**依据** 铜的横向热阻与厚度成反比，更厚的铜把热量更快铺开；JLC 的 2 层板外层可选 1、2、2.5、3.5、4.5 oz，但线宽线距限制随铜厚变大。

| 参数 | 判据 | 备注 |
|---|---|---|
| `copper_min_for_dcdc` | >= 1 oz |  |
| `copper_2oz_for_power_over` | > 3 W |  |
| `copper_4oz_for_power_over` | > 6 W |  |

**验证**
- `thermal_sim`（partial）· 热阻网络估算（THM-VER-005） — 比较 1 oz 与 2 oz 时的 θCu 和 θJA,effective，确认选择满足 THM-ARC-002

**来源分歧** AN-2020 的铜厚阈值是针对 DC-DC 转换器写的，LDO 和 MOSFET 直接套用属于类比。猫咪喂食器功率小（<1 W），1 oz 通常足够。

**来源**
- [AN-2020 Thermal Design By Insight, Not Hindsight](https://www.ti.com/lit/an/snva419c/snva419c.pdf) — Texas Instruments, app_note, §3.3 Rule 3: Copper Thickness
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, Board Thickness and Copper; Traces and Spacing

<a id="THM-STK-002"></a>
#### THM-STK-002 · 需要更低热阻时优先加内层地平面
`consider` · 可信度 `high` · 适用: 2-layer, 4-layer, exposed-pad · 标签: cat-feeder

**规则** 2 层板热裕量不足时，改用 4 层板，把裸露焊盘通过过孔连到内层地和底层地；4 层板的内层地平面可让一块设计良好的 2 层板再改善最多约 30%。

**依据** 内层地平面是大面积横向导热层，缩短到板边的热路径；单靠 2 层板的铜面积很难做到。

| 参数 | 判据 | 备注 |
|---|---|---|
| `improvement_with_internal_planes` | <= 30 % | 「最多约」，来自 TI 对 2 层与 4 层的比较 |

**验证**
- `thermal_sim`（manual）· 热阻网络估算或 FEM — 2 层方案 Tj 余量不足 THM-ARC-002 要求时，估算 4 层方案并比较成本

**来源**
- [AN-2020 Thermal Design By Insight, Not Hindsight](https://www.ti.com/lit/an/snva419c/snva419c.pdf) — Texas Instruments, app_note, §3.1
- [AN-1520 A Guide to Board Layout for Best Thermal Resistance for Exposed Packages](https://www.ti.com/lit/an/snva183b/snva183b.pdf) — Texas Instruments, app_note, §6 PCB Design Recommendations

<a id="THM-STK-003"></a>
#### THM-STK-003 · 用板面积规则做第一遍可行性检查
`consider` · 可信度 `high` · 适用: power, feasibility · 标签: cat-feeder

**规则** 自然对流、无散热器、两面实铜、热量能传到板边的条件下，每 1 W 耗散约需要 15.29 cm²（2.37 in²）板面积才能让温升限制在 40 °C；已知 θJC 时用 板面积(cm²) ≈ 500 / (θJA − θJC) 估算最小板面积。

**依据** 这是 TI 从热阻网络推出的经验规则，用于在布局之前判断板子的尺寸和封装能否承受目标功耗。

| 参数 | 判据 | 备注 |
|---|---|---|
| `board_area_per_watt_40c_rise` | >= 15.29 cm2/W | 两面实铜、自然对流、外壳不阻碍对流 |
| `board_area_coefficient` | == 500 °C·cm2/W | 板面积 ≈ 500 /(θJA − θJC) |

**验证**
- `thermal_sim`（full）· Python 脚本 — Σ 板上耗散功率 × 15.29 cm²/W 与板面积比较；局部大功耗件用 θJA − θJC 公式估算它需要的铜面积

**来源**
- [AN-2020 Thermal Design By Insight, Not Hindsight](https://www.ti.com/lit/an/snva419c/snva419c.pdf) — Texas Instruments, app_note, §3.1 Rule 1: Board Size, eq. 9–10

## 器件布局（placement）

<a id="THM-PLC-001"></a>
#### THM-PLC-001 · 热源与怕热元件分开放
`should` · 可信度 `medium` · 适用: electrolytic-capacitor, crystal, temperature-sensor, ldo, mosfet · 标签: cat-feeder

**规则** 把 LDO、MOSFET、分流电阻、整流 / 续流二极管等发热件与电解电容、晶振、温度传感器、精密基准等怕热元件分开放置，不要相邻堆叠；邻近元件的额定温度要计入允许的局部温度，必要时据此压低发热件的结温目标。

**依据** 电解电容寿命随温度指数下降；邻近元件的额定温度会限制可接受的结温（TI 的例子：选用 100 °C 额定电容并因其靠近转换器，把结温目标压到 90 °C）；AMS1117 数据手册也指出热阻会受板上其它元件的热相互作用影响。

| 参数 | 判据 | 备注 |
|---|---|---|
| `hot_to_sensitive_distance` | maximize | 没有找到权威来源给出具体距离；以热仿真 / 实测的局部温度为准 |

**验证**
- `geometry_script`（partial）· pcbnew Python — 给定「发热件」与「怕热件」位号清单，输出每个怕热件到最近发热件的距离，并按距离排序供评审；距离最近的 3 对要有热估算或实测支持
- `thermal_sim`（manual）· 简易 FEM / 热阻网络 — 估算怕热件处的局部温度，加纹波自热后满足其额定温度与寿命要求

**来源分歧** 晶振和精密器件需要远离热源的说法流传很广，但本库没找到给出具体距离的一手来源；这里只写方向性规则，具体距离留给仿真或实测。

**来源**
- [AN-2020 Thermal Design By Insight, Not Hindsight](https://www.ti.com/lit/an/snva419c/snva419c.pdf) — Texas Instruments, app_note, §2.1 Example: Calculating Your Required θJA
- [AMS1117 datasheet](https://www.handsontec.com/dataspecs/AMS1117.pdf) — Advanced Monolithic Systems, datasheet, Thermal Considerations
- [Aluminum electrolytic capacitors: General technical information](https://www.tdk-electronics.tdk.com/blob/185386/download/4/pdf-generaltechnicalinformation.pdf) — TDK Electronics (EPCOS), vendor_guide, §4–5

<a id="THM-PLC-002"></a>
#### THM-PLC-002 · 外壳内的环境温度和空气流动要按实际假设
`should` · 可信度 `medium` · 适用: enclosure, airflow · 标签: cat-feeder

**规则** 密闭或半密闭外壳里，用靠近发热件的空气温度作为环境温度，而不是室温；经验面积规则（THM-STK-003）假设外壳不阻碍板子两面的自然对流，如果板子贴壁、灌封或被遮挡，不能直接套用。

**依据** 对流和辐射散热依赖周围空气；不同标准对「环境温度」测点的定义也不同（NEBS 取进风口，AEC 取器件下方，JEDEC 取板前的气流）。有气流时所需板面积可减半，没有时反之。

| 参数 | 判据 | 备注 |
|---|---|---|
| `airflow_board_area_reduction` | <= 50 % | 有气流通常最多可把所需板面积减半 |

**验证**
- `bench`（manual）· 热电偶放在发热件旁（离板面 ≥ 1 cm）的空气中，外壳盖好 — 满载稳态时记录局部空气温度，作为 Ta,max 的依据并代入 THM-ARC-002

**来源**
- [AN-2020 Thermal Design By Insight, Not Hindsight](https://www.ti.com/lit/an/snva419c/snva419c.pdf) — Texas Instruments, app_note, §3.1 Rule 1: Board Size
- [SPRA953 Semiconductor and IC Package Thermal Metrics](https://www.ti.com/lit/an/spra953d/spra953d.pdf) — Texas Instruments, app_note, §7 Ambient Air Temperature

## 布线（routing）

<a id="THM-RTE-005"></a>
#### THM-RTE-005 · 散热过孔要实连到尽可能多的层，不用热焊盘
`must` · 可信度 `high` · 适用: exposed-pad, thermal-via

**规则** 散热焊盘下的过孔与内层 / 底层地平面之间做完整环形连接，不使用热焊盘（花焊盘）；把过孔连到尽可能多的铜层，底层地要尽量完整；封装焊盘本身也要连到顶层的大面积地铜。

**依据** 热焊盘的目的是增加热阻以便焊接，用在散热路径上会显著抬高热阻；热量必须从过孔进入大面积铜才能铺开。

**验证**
- `drc`（full）· KiCad 自定义规则 zone_connection — 散热焊盘及其内的过孔 zone_connection = solid，所连的每个铜层都有对应的铜皮覆盖
- `geometry_script`（partial）· pcbnew Python — 统计每个散热过孔连接的铜层数，要求 ≥ 2；检查底层 GND 铜皮在散热过孔下方连续

**来源分歧** 与可焊接性冲突，见 DFM-PLN-002：热焊盘利于焊接，实连利于散热。散热路径上取实连。

**来源**
- [SLMA002 PowerPAD Thermally Enhanced Package](https://www.ti.com/lit/an/slma002h/slma002h.pdf) — Texas Instruments, app_note, §2.4
- [AN-2020 Thermal Design By Insight, Not Hindsight](https://www.ti.com/lit/an/snva419c/snva419c.pdf) — Texas Instruments, app_note, §3.2
- [AN-1520 A Guide to Board Layout for Best Thermal Resistance for Exposed Packages](https://www.ti.com/lit/an/snva183b/snva183b.pdf) — Texas Instruments, app_note, §6, §7

<a id="THM-RTE-001"></a>
#### THM-RTE-001 · 大电流走线按 IPC-2152 的温升来定宽
`should` · 可信度 `low` · 适用: trace, motor-driver, power-input · 标签: cat-feeder

**规则** 大电流走线（电机、电源入口）先定温升预算，再按 IPC-2152 的曲线（区分内层 / 外层、考虑相邻铜平面与板厚）确定线宽，而不是只用旧的 IPC-2221 经验图；同一电流下内层要比外层更宽。

**依据** IPC-2152 专门针对导体载流能力，包含内外层、铜平面距离、板厚、铜厚等修正；仅用旧图容易偏保守或偏乐观。线宽决定铜的 I²R 发热和温升。

| 参数 | 判据 | 备注 |
|---|---|---|
| `trace_temp_rise_budget` | minimize °C | 没有统一规定，由产品和邻近元件的额定温度决定 |

**验证**
- `tline_calc`（full）· IPC-2152 计算器 / 载流计算脚本 — 输入电流、铜厚、内 / 外层、温升预算，求最小线宽；板上对应网络的最窄处（含焊盘颈缩、过孔）不得小于该宽度
- `bench`（manual）· 热像仪 / 热电偶 — 满载稳态下走线温升不超过预算

**来源分歧** 只读到 IPC-2152 公开的目录页（确认了内外层、铜平面、降额等章节存在），没有读到图表本身；JLC 博客给了约 10 °C 温升的近似表，其数字比 IPC-2221 的图略乐观（例如 5 A、1 oz 外层写约 100 mil），因此不把它们当作参数。线宽要用 IPC-2152 计算器核算。

**来源**
- [IPC-2152 Standard for Determining Current-Carrying Capacity in Printed Board Design (table of contents)](https://www.electronics.org/TOC/IPC-2152.pdf) — IPC, standard, §5 Conductor sizing charts; Appendix A.2 Derating, A.4.6 Copper planes
- [PCB Design Rules and Guidelines: A Complete Best Practices Guide (copper current table, approx. 10 °C rise)](https://jlcpcb.com/blog/pcb-design-rules-best-practices) — JLCPCB, vendor_guide

<a id="THM-RTE-002"></a>
#### THM-RTE-002 · 散热过孔的孔径、间距与数量
`should` · 可信度 `high` · 适用: qfn, son, powerpad, exposed-pad · 标签: cat-feeder

**规则** 裸露焊盘下的散热过孔钻孔 ≤ 0.33 mm（13 mil）、以约 1.0–1.2 mm 间距排成阵列并尽量排满；焊盘小、过孔数量受限时，把过孔放在焊盘外围，且不要在小焊盘封装上改用 0.2 mm 的小孔（比 0.33 mm 孔使 θJA 增加约 15–25%）。小芯片 5–9 个过孔通常够用，边际收益递减。

**依据** 过孔是焊盘热量进入内层 / 底层铜皮的主要路径；孔径小可减少焊料沿孔壁流失，但太小会增加热阻。

| 参数 | 判据 | 备注 |
|---|---|---|
| `thermal_via_drill_max` | <= 0.33 mm | TI SLMA002：0.33 mm 及以下，1 oz 表面铜 + 孔壁电镀时效果好 |
| `thermal_via_drill_start` | == 0.3 mm | TI SLUA271：起始值 |
| `thermal_via_pitch` | 1.0 … 1.2 mm | SLUA271 约 1.0 mm；AN-1520 仿真用 1.2 mm；AN-2020 用 1 mm |
| `small_die_via_count` | 5 … 9 pcs | 小芯片通常足够 |
| `theta_ja_penalty_0p2mm_via_small_pad` | 15 … 25 % | 最多 4 个过孔的小焊盘；大焊盘（≥ 9 个）一般 < 10% |

**验证**
- `geometry_script`（full）· pcbnew Python — 统计每个裸露焊盘内的过孔数量、钻孔径、最近邻间距；孔径 ≤ 0.33 mm、间距在 1.0–1.2 mm，数量接近焊盘能容纳的最大值；孔径同时不低于板厂过孔下限

**来源**
- [SLMA002 PowerPAD Thermally Enhanced Package](https://www.ti.com/lit/an/slma002h/slma002h.pdf) — Texas Instruments, app_note, §2.4 Thermal Vias
- [SLUA271 QFN and SON PCB Attachment](https://www.ti.com/lit/an/slua271d/slua271d.pdf) — Texas Instruments, app_note, §3.4.1
- [AN-1520 A Guide to Board Layout for Best Thermal Resistance for Exposed Packages](https://www.ti.com/lit/an/snva183b/snva183b.pdf) — Texas Instruments, app_note, §5.2, §6
- [AN-2020 Thermal Design By Insight, Not Hindsight](https://www.ti.com/lit/an/snva419c/snva419c.pdf) — Texas Instruments, app_note, §3.2 Rule 2: Thermal Vias

<a id="THM-RTE-004"></a>
#### THM-RTE-004 · 散热过孔的封盖方式要避免焊料流失和空洞
`should` · 可信度 `high` · 适用: exposed-pad, thermal-via, qfn, powerpad

**规则** 散热焊盘上的过孔必须有明确的处理方式：从元件面用阻焊盖住（阻焊盘径 = 孔径 + 0.1 mm 以上），或者塞/填平；不要只从背面盖油，否则空洞增加；使用 OSP 表面处理时 TI 发现不盖油也能得到可重复的结果。把选择写进制造说明。

**依据** 开口过孔把焊料吸走，使焊盘处缺焊料而出现空洞；背面盖油会困住空气和助焊剂放气；二者都使有效焊接面积下降（见 THM-MFG-001）。

| 参数 | 判据 | 备注 |
|---|---|---|
| `via_mask_cap_over_hole` | >= 0.1 mm | 盖油阻焊直径比孔径大的量（TI 两份文档均提到） |

**验证**
- `review`（manual）· 制造说明 + JLC 下单页「过孔覆盖」选项 — 确认散热过孔的覆盖方式与 TI 建议一致；2 层板在 JLC 上若选「盖油」，Gerber 中阻焊层对该孔的盖油环 ≥ 孔径 + 0.1 mm
- `geometry_script`（partial）· pcbnew Python — 对散热焊盘内的过孔，检查其阻焊边距设置为（通过 tented 或负边距）不开窗，或者标记为 filled

**来源分歧** TI 两份文档都偏好从元件面盖油；SLUA271 补充说 OSP 面不盖油也可重复。JLC 的 2 层板标准服务难以做焊盘内填平盖帽（见 DFM-RTE-002）。取舍：按所选表面处理和板厂能力选择，并用 X 光结果验证。

**来源**
- [SLMA002 PowerPAD Thermally Enhanced Package](https://www.ti.com/lit/an/slma002h/slma002h.pdf) — Texas Instruments, app_note, §2.4 Thermal Vias
- [SLUA271 QFN and SON PCB Attachment](https://www.ti.com/lit/an/slua271d/slua271d.pdf) — Texas Instruments, app_note, §3.4.1, Figure 3-4
- [Via Covering: Tented, Untented, Plugged, Epoxy-Filled and Copper-epoxy-filled](https://jlcpcb.com/help/article/pcb-via-covering) — JLCPCB, vendor_guide

<a id="THM-RTE-003"></a>
#### THM-RTE-003 · 用过孔阵列的并联热阻核算而不是凭感觉
`consider` · 可信度 `high` · 适用: thermal-via, exposed-pad · 标签: cat-feeder

**规则** 过孔阵列的热阻按单孔热阻除以数量估算：12 mil（0.3 mm）孔、孔壁 0.5 oz 镀铜、板厚 1.6 mm 约 261 °C/W；孔壁镀到 1 oz 约 140 °C/W；8 mil 完全填铜约 128 °C/W。把该值纳入总热阻，并与热预算比较。

**依据** 单个过孔热阻很高，数量才是关键；4×4 共 16 个 12 mil 过孔约 16.3 °C/W，填孔可再降一半，但 PCB 成本可能增加到 2–3 倍，而 1 oz 孔壁镀铜只增加约 10–20%。

| 参数 | 判据 | 备注 |
|---|---|---|
| `via_theta_12mil_0p5oz` | == 261 °C/W | 单孔，板厚 0.165 cm，孔壁 0.00175 cm |
| `via_theta_12mil_1oz` | == 140 °C/W | 单孔 |
| `via_theta_8mil_filled` | == 128 °C/W | 单孔，镀满封闭 |
| `jlc_avg_hole_plating` | == 18 um | JLC 公布的平均孔铜约等于 0.5 oz 镀铜，因此取 261 °C/W 作基准 |

**验证**
- `thermal_sim`（full）· Python：R_array = R_via / N，再与铜皮横向热阻串联 — R_array ≤ 热预算中分给过孔的份额；需要时说明为什么不用更多过孔或更厚镀铜

**来源**
- [AN-2020 Thermal Design By Insight, Not Hindsight](https://www.ti.com/lit/an/snva419c/snva419c.pdf) — Texas Instruments, app_note, §3.2, §3.2.1, Table 1
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, Drilling: Average hole plating

## 平面与铺铜（plane_pour）

<a id="THM-PLN-001"></a>
#### THM-PLN-001 · SOT-223 的散热铜面积要按目标 θJA 来定
`should` · 可信度 `high` · 适用: sot-223, ams1117, ldo, dpak · 标签: cat-feeder

**规则** SOT-223（AMS1117 一类）按目标 θJA 给 tab 配铜：以 (Tj,max − Ta,max)/PD 反推所需 θJA，再查铜面积表；不要只靠封装自带的 16 mm² 焊盘：按 Richtek 的 135 °C/W、Tj,max = 125 °C、Ta,max = 70 °C 推算，它最多只能耗散约 0.4 W（由 Richtek 数值推出）。

**依据** 铜面积从 16 mm² 增加到 2500 mm²，θJA 可从 135 降到 50 °C/W（Richtek 数据）；TI 的 2 oz 测试里 0.0123–1 in² 使 RθJA 从约 110 降到 40 °C/W。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ams1117_theta_ja_2500_2500_2500` | == 55 °C/W | AMS1117 表 1：顶层 2500 mm² / 背面 2500 mm² / 板 2500 mm²，1/16 英寸 FR-4，1 oz |
| `ams1117_theta_ja_1000_2500_2500` | == 55 °C/W | 顶层 1000 mm²，背面 2500 mm² |
| `ams1117_theta_ja_225_2500_2500` | == 65 °C/W | 顶层 225 mm²，背面 2500 mm² |
| `ams1117_theta_ja_100_2500_2500` | == 80 °C/W | 顶层 100 mm²，背面 2500 mm² |
| `ams1117_theta_ja_1000_1000_1000` | == 60 °C/W | 顶层 1000 mm²，背面 1000 mm²，板 1000 mm² |
| `ams1117_theta_ja_1000_0_1000` | == 65 °C/W | 顶层 1000 mm²，背面 0 |
| `richtek_theta_ja_16mm2` | == 135 °C/W | 标准焊盘 16 mm²，2 oz 板 |
| `richtek_theta_ja_100mm2` | == 107 °C/W |  |
| `richtek_theta_ja_2500mm2` | == 50 °C/W |  |
| `ti_sot223_pad_for_1p3w` | >= 0.066 in2 | 约 43 mm²，2 oz，约 1.3 W；TI 测试板 4.5 × 5 in |

**验证**
- `geometry_script`（partial）· pcbnew Python：统计与 tab 焊盘直接相连的铜面积（顶层 / 底层，经过孔相连的底层面积另计） — 取表中与实际 (顶 / 底 / 板面积) 最接近且偏保守的一行的 θJA，代入 THM-ARC-003 的 PD 和 Tj 计算
- `bench`（manual）· 热电偶 / 热像仪 — 在最大负载实测 tab 温度并与计算对比

**来源分歧** 三个来源的测试板不同（AMS：1/16 英寸 FR-4，1 oz；Richtek：表中标 2 oz；TI：4.5×5 in，2 oz），数值不能混用；AMS1117 表是粗略指南，数据手册自己说需要实验确定。

**来源**
- [AMS1117 datasheet](https://www.handsontec.com/dataspecs/AMS1117.pdf) — Advanced Monolithic Systems, datasheet, Thermal Considerations, Table 1
- [Understanding Thermal Characteristic of SOT-223 Package (AN044)](https://www.richtek.com/Design%20Support/Technical%20Document/AN044?sc_lang=en) — Richtek, app_note
- [AN-1028 Maximum Power Enhancement Techniques for Power Packages](https://www.ti.com/lit/pdf/snva036) — Texas Instruments, app_note, §3 Result, Figure 3–4

<a id="THM-PLN-002"></a>
#### THM-PLN-002 · 散热铜优先放在元件面，再用过孔连到背面
`should` · 可信度 `high` · 适用: sot-223, dpak, so-8, ldo, mosfet · 标签: cat-feeder

**规则** 功率封装的散热铜皮优先放在元件面并与焊盘直接相连；要进一步降低热阻时，再用多个过孔把它连到背面铜皮；散热铜不一定要和器件的 tab 在电气上同网络。

**依据** TI 的 SOT-223 实验中，铜全部放在顶面比放在底面或两面各一半的 RθJA 低 10–15 °C/W；PCB 材料在铜层之间的 L/A 比很小，所以背面或内层的地平面也能有效传热。

| 参数 | 判据 | 备注 |
|---|---|---|
| `top_side_copper_benefit` | 10 … 15 °C/W | 相比铜在底面或两面平分，同一面积 |

**验证**
- `geometry_script`（partial）· pcbnew Python — 功率件焊盘在元件面直接连接的铜面积 ≥ 设计目标，并存在 ≥ 2 个连到背面铜的过孔

**来源**
- [AN-1028 Maximum Power Enhancement Techniques for Power Packages](https://www.ti.com/lit/pdf/snva036) — Texas Instruments, app_note, §3 Result
- [AMS1117 datasheet](https://www.handsontec.com/dataspecs/AMS1117.pdf) — Advanced Monolithic Systems, datasheet, Thermal Considerations

<a id="THM-PLN-003"></a>
#### THM-PLN-003 · 别在散热铜皮上垂直于热流切口
`should` · 可信度 `high` · 适用: power, zone, exposed-pad

**规则** 发热件周围的散热铜皮保持连续；不得不穿过铜皮的走线 / 缝隙尽量沿热量的辐射方向走，不要垂直于热流方向切断铜皮；封装旁的铜皮尽量向外延伸。

**依据** TI 的热像对比：垂直于热流的宽切口使同样功耗的板子温度高出 5.5 °C，平行于热流的切口只高 1.5 °C；把靠近封装的走线尽量延伸可使热阻再降约 10%（约 2 °C/W）。

| 参数 | 判据 | 备注 |
|---|---|---|
| `perpendicular_cut_temp_rise` | == 5.5 °C | TI 实验：垂直切口 |
| `parallel_cut_temp_rise` | == 1.5 °C | TI 实验：平行切口 |

**验证**
- `geometry_script`（partial）· pcbnew Python — 以发热件焊盘为中心，统计半径 15 mm 内顶层 / 底层铜皮被走线或槽切断的弧长；切口方向与径向夹角 > 45° 的列出供评审
- `bench`（manual）· 热像仪 — 对比有 / 无该切口的两版板温度分布

**来源**
- [AN-2020 Thermal Design By Insight, Not Hindsight](https://www.ti.com/lit/an/snva419c/snva419c.pdf) — Texas Instruments, app_note, §3.4 Rule 4: Avoid Breaks in the Thermal Path
- [AN-1520 A Guide to Board Layout for Best Thermal Resistance for Exposed Packages](https://www.ti.com/lit/an/snva183b/snva183b.pdf) — Texas Instruments, app_note, §5.2

## 出图与制造（manufacturing）

<a id="THM-MFG-001"></a>
#### THM-MFG-001 · 裸露焊盘的焊接面积与空洞要有上限并用 X 光验证
`should` · 可信度 `high` · 适用: qfn, son, powerpad, exposed-pad

**规则** 裸露焊盘的焊接面积不低于焊盘面积的 50%（标准工艺通常 > 80%）；大功率应用中空洞率不超过 50%（25% 以内收益递减）；JLC 对 BGA / QFN / LGA 自动做 X 光并出报告，要查看报告并关注集中在电流 / 受力区域的空洞。

**依据** 空洞等同于缺少焊接面积：AN-1520 仿真显示焊接覆盖率降到 50 / 20 / 10 / 5% 时 θJA 增大约 4 / 13 / 19 / 34%，10% 左右是拐点；覆盖率大于 50% 时变化不到 5%。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ep_solder_area_min` | >= 50 % | TI SLMA002：最小焊接面积；标准工艺通常 > 80% |
| `ep_void_max_high_power` | <= 50 % | TI SLUA271 偏好的上限；JEDEC 高 K 板上 25% 为收益递减点 |
| `ep_void_diminishing_returns` | <= 25 % |  |
| `theta_ja_increase_at_50pct_coverage` | == 4 % | AN-1520 仿真，中心集中的焊接区域 |
| `theta_ja_increase_at_10pct_coverage` | == 19 % |  |

**验证**
- `bench`（manual）· JLC X-Ray Report（订单历史 → 生产进度）或自有 X 光 — 散热焊盘的焊接面积 ≥ 50%，最好 ≥ 75%；单个大空洞（例如 > 25% 焊点面积）或集中在电流路径上的空洞要说明或返工
- `thermal_sim`（full）· THM-ARC-002 计算 — 用 θJA 增加 4–19% 的悲观值重算 Tj，仍然满足限值

**来源分歧** TI 两份文档的空洞要求不同：SLMA002 要求焊接面积 ≥ 50%，SLUA271 要求空洞 ≤ 50%（两者等价），并说在 JEDEC 高 K 板上 25% 为收益递减点。JLC X 光指南只用「大于 25%」举例，并没有给出按封装区分的合格判据。

**来源**
- [SLMA002 PowerPAD Thermally Enhanced Package](https://www.ti.com/lit/an/slma002h/slma002h.pdf) — Texas Instruments, app_note, Assembly: solder joint inspection
- [SLUA271 QFN and SON PCB Attachment](https://www.ti.com/lit/an/slua271d/slua271d.pdf) — Texas Instruments, app_note, §4.4 Exposed-Pad Stencil Design
- [AN-1520 A Guide to Board Layout for Best Thermal Resistance for Exposed Packages](https://www.ti.com/lit/an/snva183b/snva183b.pdf) — Texas Instruments, app_note, §5.2
- [X-Ray Inspection Report Interpretation Guide](https://jlcpcb.com/help/article/x-ray-inspection-report-interpretation-guide) — JLCPCB, vendor_guide
- [PCB Assembly Capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) — JLCPCB, vendor_guide, Placement, Reflow, and Inspection (X-ray)

## 签核验证（verification）

<a id="THM-VER-001"></a>
#### THM-VER-001 · 由外壳温度推结温用 ψJT，不用 θJC
`should` · 可信度 `high` · 适用: plastic-package, all-ics

**规则** 想从实测的封装顶面中心温度推算结温时用 Tj = Tc + ψJT × P（塑封件的 ψJT 通常 0.5–2 °C/W），或由板温用 Tj = Tboard + ψJB × P；不要用 Tc + θJC × P，也不要用 θJA = θJC + θCA 的串联。

**依据** 塑封器件 60–95% 的热量经 PCB 散出而不是顶面，用 θJC（典型 4–15 °C/W）会高估结温；ψJT 是在与实际应用相近的热流分配下测的，更接近真实。

| 参数 | 判据 | 备注 |
|---|---|---|
| `psi_jt_plastic_typical` | 0.5 … 2 °C/W |  |
| `theta_jc_plastic_typical` | 4 … 15 °C/W |  |
| `heat_via_pcb_fraction` | 60 … 95 % | ψJB 文中为 75–95% |

**验证**
- `bench`（manual）· 热电偶 / 热像仪 + 数据手册 ψJT / ψJB — 测顶面中心温度 Tc，Tj = Tc + ψJT × P；与 THM-ARC-002 的计算结果对比

**来源**
- [SPRA953 Semiconductor and IC Package Thermal Metrics](https://www.ti.com/lit/an/spra953d/spra953d.pdf) — Texas Instruments, app_note, §2.2, §3, §5

<a id="THM-VER-002"></a>
#### THM-VER-002 · 测外壳温度的方法要避免热电偶散热误差
`should` · 可信度 `high` · 适用: thermal-measurement

**规则** 用热电偶测封装顶面温度时，用 36–40 号细线（J 或 K 型），位置在封装表面中心（±1 mm），热导环氧小珠 ≤ 2 × 2 mm，线沿封装对角线走到 PCB 并在板面上贴行至少 25 mm 再抬起，不用胶带直接贴；热像仪必须按表面发射率修正；红外测温枪视场最大约 4 mm 且不适合测 ψJB。

**依据** 粗线热电偶会把被测点「吸冷」，使环境到表面的温差少测 50% 以上，错误范围 5–50%；发射率未修正的红外读数也不可信。

| 参数 | 判据 | 备注 |
|---|---|---|
| `thermocouple_gauge_max_thickness` | >= 36 AWG | 36 号或更细（数字更大更细） |
| `epoxy_bead_max` | <= 2 mm | 2 × 2 mm 以内 |
| `wire_dress_length_on_pcb` | >= 25 mm |  |
| `center_placement_tolerance` | <= 1 mm |  |

**验证**
- `bench`（manual）· 细线热电偶 + 热像仪 — 测量方法记录满足上述要求；热像仪读数用已知温度的参考点（如热电偶测值）校准发射率

**来源**
- [SPRA953 Semiconductor and IC Package Thermal Metrics](https://www.ti.com/lit/an/spra953d/spra953d.pdf) — Texas Instruments, app_note, §3.1 Case Temperature Measurement; §5.1

<a id="THM-VER-004"></a>
#### THM-VER-004 · 在最坏工况、盖好外壳后做稳态热测试
`should` · 可信度 `medium` · 适用: thermal-verification, enclosure · 标签: cat-feeder

**规则** 热验证在最高环境温度（可用恒温箱或加热）、最高输入电压、最大负载（Wi-Fi 峰值 / 电机堵转）、外壳盖好的稳态下进行；记录环境温度的测点位置，并给出每个发热件的实测温度与计算结温的对照。

**依据** 热相互作用和外壳影响很难纯靠计算得到，AMS1117 数据手册也说明需要实验确定；环境温度测点不同会得到不同的「环境温度」，必须统一。

**验证**
- `bench`（manual）· 热电偶多通道记录仪 + 热像仪 — 稳态（温度变化 < 1 °C / 10 min）后记录发热件温度、局部空气温度；所有器件按 THM-VER-001 换算的 Tj ≤ Tj,max − 余量

**来源分歧** 稳态判据（温度变化 < 1 °C / 10 min）是本库的实用建议，不是来源规定的数值。

**来源**
- [AMS1117 datasheet](https://www.handsontec.com/dataspecs/AMS1117.pdf) — Advanced Monolithic Systems, datasheet, Thermal Considerations
- [SPRA953 Semiconductor and IC Package Thermal Metrics](https://www.ti.com/lit/an/spra953d/spra953d.pdf) — Texas Instruments, app_note, §7 Ambient Air Temperature

<a id="THM-VER-003"></a>
#### THM-VER-003 · MOSFET 结温可用体二极管压降法做电学测量
`consider` · 可信度 `medium` · 适用: mosfet, ao3400a · 标签: cat-feeder

**规则** 需要验证 MOSFET 实际结温时，可用体二极管压降法：先标定二极管压降随温度的斜率 K（功率 MOSFET 约 2.2 mV/°C），再在功率脉冲结束后约 30 µs 测量体二极管压降（小电流，TI 用 10 mA），由压降变化换算结温。

**依据** 结点温度无法直接用热电偶测量；体二极管压降是半导体结自身的温度传感器，是 JEDEC/MIL 方法的基础。

| 参数 | 判据 | 备注 |
|---|---|---|
| `body_diode_k_factor` | == 2.2 mV/°C | TI 称大多数功率 MOSFET 约此值；应逐器件标定 |
| `diode_sense_current` | == 10 mA | TI 测试用 |
| `measure_delay_after_pulse` | == 30 us |  |

**验证**
- `bench`（manual）· 可编程电源 + 示波器/数字万用表 + 恒温箱 — 标定 K；加功率脉冲后在 30 µs 内读体二极管压降；ΔVSD / K 得到 ΔTj

**来源**
- [AN-1028 Maximum Power Enhancement Techniques for Power Packages](https://www.ti.com/lit/pdf/snva036) — Texas Instruments, app_note, Appendix B Thermal Measurement

<a id="THM-VER-005"></a>
#### THM-VER-005 · 先用热阻网络手算，再决定是否做 FEM
`consider` · 可信度 `high` · 适用: thermal-sim · 标签: cat-feeder

**规则** 布局前后都用热阻网络做第一遍估算：把 1 cm 方块的铜横向热阻、FR-4 垂直热阻、过孔热阻和表面对流热阻搭成网络，估算 θCA 和板温；余量不足或几何复杂时再用 FEM。

**依据** 电阻网络计算快，足以决定板面积、是否需要气流或散热器；TI 推荐先用该模型，再用有限元做细化。

| 参数 | 判据 | 备注 |
|---|---|---|
| `theta_cu_1cm_square_1oz` | == 71.4 °C/W | 1 cm × 1 cm，1 oz 铜横向，λ = 4 W/(cm·°C) |
| `theta_sa_1cm_square_natural` | == 1000 °C/W | 1 cm² 板面到环境，自然对流 h = 0.001 W/(cm²·°C) |
| `theta_fr4_1cm_square` | == 13.9 °C/W | 1 cm² FR-4 厚 0.032 cm 垂直方向 |
| `theta_via_12mil` | == 261 °C/W | 同 THM-RTE-003 |

**验证**
- `thermal_sim`（partial）· Python 脚本搭建热阻网络（节点 = 1 cm 方块） — 输出每个发热件的 θJA,effective 与 Tj；与 THM-ARC-002 要求比较，并与实测 THM-VER-004 校准系数

**来源**
- [AN-2020 Thermal Design By Insight, Not Hindsight](https://www.ti.com/lit/an/snva419c/snva419c.pdf) — Texas Instruments, app_note, §1, §2, Table 1

