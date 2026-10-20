# 通用 / 数模混合 MCU 板（general）— 规则全文

垂直领域 · 103 条规则 · 由 `catalog/*.yaml` 生成，请改 YAML 不要改本文件。用 `grep -n "<规则ID>" rules.md` 定位单条，不要整份读。

环节分布：架构与选型 10，符号封装库 8，原理图 17，网表与约束 8，叠层与规则 8，分区规划 8，器件布局 9，布线 15，平面与铺铜 11，签核验证 9

## 架构与选型（architecture）

<a id="GEN-ARC-007"></a>
#### GEN-ARC-007 · 按电源轨做功耗预算并计入峰值电流
`must` · 可信度 `high` · 适用: power_tree, ldo, wireless_mcu · 标签: cat-feeder

**规则** 为每条电源轨建表：列出各负载的典型电流和峰值电流（如射频发射脉冲、电机启动），求和后加余量，与稳压器限流、输入源能力、 保险丝 / PPTC 保持电流和连接器额定值比较；线性稳压器还要算耗散 (Vin - Vout) x Iout 和结温。

**依据** 平均电流很小的无线 MCU 板，峰值电流可能是平均值的几十倍；电源只按平均值选就会在射频发射时掉压重启。 线性稳压器把压差全部转成热，结温超限会进入热关断。

| 参数 | 判据 | 备注 |
|---|---|---|
| `supply_output_current_min` | >= 500 mA | Espressif 对 ESP32-C3 单电源 3.3 V 方案的要求（原理图检查表 Power Supply） |
| `esp32c3_wifi_tx_peak_current` | == 335 mA | 数据手册 v2.4 Table 5-7，802.11b 1 Mbps @21 dBm，100% 占空比，3.3 V，25 degC |

**验证**
- `bom_check`（full）· 电源预算表 + 脚本 — 每条轨：sum(Ipeak_i) x (1 + 余量比例) <= 稳压器额定输出且 <= 输入源能力；线性稳压器 P = (Vin_max - Vout) x Iout， Tj = Tamb_max + P x theta_JA 必须小于 Tj_max（PD(max) = (TJmax - Tamb)/theta_JA）。余量比例由项目策略给定。
- `bench`（manual）· 功耗仪 / 示波器 + 电流探头 — 抓取联网、发射和电机启动时刻的输入电流波形，峰值不得超过预算表，电源轨最低电压不得低于器件最小工作电压。

**来源**
- [Schematic Checklist - ESP32-C3](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, Power Supply
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, 5.6 Current Consumption, Table 5-7
- [AMS1117 datasheet (UMW)，最大允许功耗公式](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5011/AMS1117.pdf) — UMW, datasheet, Absolute maximum ratings 脚注 1
- [pcb-checklist: schematic checklist（Power）](https://github.com/azonenberg/pcb-checklist/blob/master/schematic-checklist.md) — Andrew Zonenberg, blog

<a id="GEN-ARC-009"></a>
#### GEN-ARC-009 · 核对每条数字链路的电平兼容与过压
`must` · 可信度 `high` · 适用: digital_io, sensor_module, level_shift · 标签: cat-feeder

**规则** 对每条数字链路（含模块、传感器小板、外部连接器），在最坏电源电压下核对 VOH(min) >= VIH(min)、VOL(max) <= VIL(max)， 并确认驱动端高电平不会超过接收端的最大输入电压（VDD + 0.3 V 或绝对最大值）。模块用 5 V 供电时其输出可能是 5 V 电平，需要电平转换或改用 3.3 V 供电。

**依据** 阈值不满足时通信时好时坏，输入超压会通过 ESD 钳位二极管灌电流，累积损伤 IO。模块板上的电平由模块自己的供电轨决定，容易被忽视。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esp32c3_vih_min` | >= 0.75 x VDD | 数据手册 Table 5-4：高电平输入阈值下限 |
| `esp32c3_vil_max` | <= 0.25 x VDD | Table 5-4：低电平输入阈值上限 |
| `esp32c3_voh_min` | >= 0.8 x VDD | Table 5-4：输出高电平下限 |
| `esp32c3_vol_max` | <= 0.1 x VDD | Table 5-4：输出低电平上限 |
| `esp32c3_vih_abs_max_over_vdd` | <= 0.3 V | 输入电压上限为 VDD + 0.3 V（Table 5-4 的 VIH 最大值） |
| `i2c_vih_min` | >= 0.7 x VCC | TI SLVA689A 的 I2C 阈值定义；VIL 最大 0.3 x VCC |

**验证**
- `review`（partial）· 链路表（驱动端器件 / 电源轨 / VOH,VOL，接收端器件 / 电源轨 / VIH,VIL）+ 网表脚本 — 脚本从网表取每条信号网络的驱动端与接收端，按各器件所在电源轨的最小 / 最大电压代入阈值公式， VOH_min >= VIH_min、VOL_max <= VIL_max 且 V_drive_max <= V_receiver_max_input，任一不满足即失败。
- `bench`（manual）· 示波器 — 在最低和最高电源电压下抓信号电平，高电平 >= VIH_min 加余量，不得超过接收端最大输入电压。

**来源**
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, Table 5-4 DC Characteristics (3.3 V, 25 degC)
- [I2C Bus Pullup Resistor Calculation (SLVA689A)](https://www.ti.com/lit/pdf/slva689) — Texas Instruments, app_note, 2 Pullup Resistor Calculation

<a id="GEN-ARC-001"></a>
#### GEN-ARC-001 · 需求逐条分配到设计元素并指定验证方法
`should` · 可信度 `medium` · 适用: requirements, system

**规则** 画原理图之前，把每条需求（功能、电气、机械、环境）编号，并在需求矩阵里写明：来源、分配到的设计元素 （模块 / 器件 / 网络组）、验证方法（测试、分析、检查、演示之一）和通过判据。没有分配对象或没有验证方法的需求视为未完成。

**依据** 需求不落到具体元件上，就无法判断某个元件为什么存在、删掉会破坏什么；没有验证方法的需求无法在签核时关闭。 验证方法分为 test / analysis / inspection / demonstration 四类，是系统工程里通行的分法。

**验证**
- `review`（partial）· 需求矩阵（requirements.yaml 或表格）+ 自写校验脚本 — 脚本逐条检查：每个需求 ID 的 allocated_to、verify_method、acceptance 非空；allocated_to 引用的位号或功能块在 网表 / 原理图页名里真实存在；verify_method 属于 {test, analysis, inspection, demonstration}。 人工评审再确认判据是否可测。

**来源**
- [NASA Systems Engineering Handbook (NASA/SP-2016-6105 Rev 2), 验证 / 确认方法与附录中的需求验证矩阵示例](https://explorers.larc.nasa.gov/2023ESE/pdf_files/NASA04.%20SysEng%20Handbook%20(NASA_SP-2016-6105%20Rev%202).pdf) — NASA, textbook, Verification / Appendix D（需求验证矩阵样例；章节号未逐页核对）
- ISO/IEC/IEEE 29148:2011 Requirements engineering（需求可追溯性）（ISO/IEC/IEEE 29148:2011，traceability 相关条款） — ISO/IEC/IEEE, standard

<a id="GEN-ARC-002"></a>
#### GEN-ARC-002 · 按产品等级对元件电压 / 电流 / 功率降额
`should` · 可信度 `high` · 适用: resistor, capacitor, mosfet, ic, inductor, connector · 标签: cat-feeder

**规则** 在选型阶段确定降额策略（每类元件的最大应力 / 额定值），并对每个元件用实际最坏工作点的电压、电流、功耗和结温核对。 NASA 的通用参考值见 parameters；商用产品可以放宽，但放宽要有记录并给出理由。

**依据** 元件失效率随电应力、热应力降低而下降；把应力限制在额定值的一个固定比例以内，可以免去逐件做可靠性建模， 同时给容差、浪涌和老化留出余量。

| 参数 | 判据 | 备注 |
|---|---|---|
| `capacitor_voltage_stress_max` | <= 0.6 额定电压的比例 | NASA GSFC PD-ED-1201 Table 1：电容 |
| `resistor_power_stress_max` | <= 0.6 额定功率的比例 | NASA PD-ED-1201：电阻 |
| `semiconductor_power_stress_max` | <= 0.5 额定功率的比例 | NASA PD-ED-1201：分立半导体 |
| `semiconductor_voltage_stress_max` | <= 0.75 额定电压的比例 | NASA PD-ED-1201：分立半导体 |
| `semiconductor_junction_temp_max` | <= 110 degC | NASA PD-ED-1201：分立半导体 |
| `microcircuit_supply_voltage_stress_max` | <= 0.8 额定电压的比例 | NASA PD-ED-1201：集成电路电源电压 |
| `microcircuit_power_stress_max` | <= 0.75 额定功率的比例 | NASA PD-ED-1201：集成电路 |
| `microcircuit_junction_temp_max` | <= 100 degC | NASA PD-ED-1201：集成电路 |
| `inductive_device_voltage_stress_max` | <= 0.5 额定电压的比例 | NASA PD-ED-1201：电感类器件 |
| `relay_connector_current_stress_max` | <= 0.5 额定电流的比例 | NASA PD-ED-1201：继电器与连接器 |
| `inductor_saturation_current_derating` | 30 … 40 % | TI SLYP673 幻灯片给出的经验值：Isat 降额 30-40% |

**验证**
- `bom_check`（partial）· BOM + 工作点表的校验脚本 — 对每个元件取仿真 .op / .tran 的最大电压、电流、功耗（或手算），除以数据手册额定值（功率按环境温度折算后的额定值）， 得到应力比；与策略表逐项比较，超限项列出。结温用 Tj = Tamb + P x theta_JA 估算后与 Tj_max 比较。
- `bench`（manual）· 热像仪 / 电流探头 / 示波器 — 最坏负载（电机堵转、Wi-Fi 发射、输入电压上限）下测元件壳温与电压峰值，换算应力比并与策略比较。

**来源分歧** NASA 表是飞行项目策略，商用板常取更宽的比例；行业博客给出的数字各不相同（陶瓷电容 50-60%、钽 50% 甚至 30%、 铝电解 80% 等，未核对到原始标准）；ECSS-Q-ST-30-11C 按器件族另有更细的表格（未逐条核对）。 取舍：把 NASA 表当作可复现的上限基线，产品等级更低时在项目的降额策略文件里明确写出放宽后的数值，不在单个器件上临时放宽。

**来源**
- [PD-ED-1201 EEE Parts Derating (Preferred Reliability Practices)](https://extapps.ksc.nasa.gov/Reliability/Documents/Preferred_Practices/1201.pdf) — NASA GSFC, standard, Table 1 Typical Part Derating Guidelines
- [How to avoid design problems by using worst case analysis calculations (SLYP673)](https://www.ti.com/lit/pdf/slyp673) — Texas Instruments, app_note, inductance rolloff example 幻灯片

<a id="GEN-ARC-003"></a>
#### GEN-ARC-003 · 陶瓷电容按直流偏压后的有效容值取值
`should` · 可信度 `high` · 适用: mlcc, ldo, decoupling, filter · 标签: cat-feeder

**规则** 对用于稳压器稳定性、保持时间、滤波或定时的 Class II（X5R / X7R / Y5V）MLCC，以工作偏压、温度和公差下的有效容值参与计算， 而不是标称值；需要容值稳定的位置优先用 C0G，或加大额定电压 / 封装。

**依据** 高介电常数 MLCC 的容值随直流偏压下降，Murata 的例子是 6.3 V 100 uF 的 X5R 在 1.8 V 偏压下掉约 10%，Y5V 约掉 40%； 同样标称、同样尺寸的不同厂商料偏压曲线差别很大，二次供货时尤其要重新核对。

| 参数 | 判据 | 备注 |
|---|---|---|
| `murata_example_x5r_loss_at_1v8` | == 10 % | Murata 示例：6.3 V 100 uF X5R 在 1.8 V 直流偏压下的容值下降；仅作量级参考，具体以料号曲线为准 |
| `murata_example_y5v_loss_at_1v8` | == 40 % | 同上，Y5V |
| `x7r_tolerance_bol` | == 10 % | TI SLYP673 示例里 X7R 的初始容差；EOL 21%，温度 15%（示例值，EOL 数据应取自厂商） |

**验证**
- `bom_check`（partial）· 厂商偏压曲线工具（Murata SimSurfing、TDK 等）+ 脚本 — 对每个关键 MLCC 取工作偏压下的有效容值，乘以温度与公差余量后，与数据手册要求的最小容值（如 LDO 输出电容）比较， 不足则换料、加并联或换更大额定电压。
- `bench`（manual）· LCR 表（带直流偏置） — 按 Murata 建议，在实际供电线路的直流电压下测电容，对比计算值。

**来源**
- [The voltage characteristics of electrostatic capacitance](https://article.murata.com/en-global/article/voltage-characteristics-of-electrostatic-capacitance) — Murata, vendor_guide
- [How to avoid design problems by using worst case analysis calculations (SLYP673)](https://www.ti.com/lit/pdf/slyp673) — Texas Instruments, app_note, Capacitor Tolerances 幻灯片
- [pcb-checklist: schematic checklist（Decoupling: Derate ceramic capacitors for their C/V curve）](https://github.com/azonenberg/pcb-checklist/blob/master/schematic-checklist.md) — Andrew Zonenberg, blog

<a id="GEN-ARC-004"></a>
#### GEN-ARC-004 · 选型时核对生命周期并为关键件备好替代料
`should` · 可信度 `medium` · 适用: bom, mcu, ldo, mosfet · 标签: cat-feeder

**规则** 冻结 BOM 之前，确认每个料处于量产状态（不是 NRND / EOL / 停产），所选渠道有足够库存；对关键件（MCU 或模块、稳压器、功率开关、 模拟前端）至少登记一个引脚和封装兼容的替代料，必要时让封装能兼容替代料。同一料号有多家制造商时，分别核对各家数据手册。

**依据** 停产或缺货会把一次选型问题变成改板；不同厂商的同名料数据手册要求可能不同（例如稳压器输出电容要求）， 所以替代料不能只看型号相同。生命周期管理有专门的标准框架（IEC 62402）。

**验证**
- `bom_check`（partial）· 分销商 API（LCSC / JLC 零件库 / Octopart）+ 脚本 — 对 BOM 每行查询生命周期状态和库存，状态不是 Active、库存低于一次订单数量的行输出告警； 关键件的 AVL（合格供应商列表）里替代料字段为空则失败。
- `review`（manual）· 评审清单 — 逐个关键件，把原料与替代料的数据手册并排比较（电气参数、稳定性条件、引脚、封装），记录结论。

**来源分歧** 同一型号的二供料数据手册可能不一致。例如 AMS1117 在 UMW 的数据手册里要求 22 uF 钽电容作输出电容以保证稳定性， 其他厂商版本可能给出不同值（未核对）；因此二供替换必须以实际下单料号的数据手册为准。

**来源**
- [Schematic Design Review Checklist（BOM and part checks：active production、库存、一个值一个料号）](https://resources.altium.com/p/schematic-review-checklist) — Altium, vendor_guide
- IEC 62402 Obsolescence management（IEC 62402（淘汰管理框架；未取得正文，仅据二手资料引用）） — IEC, standard

<a id="GEN-ARC-005"></a>
#### GEN-ARC-005 · 封装与器件选择要匹配贴片厂的库和工艺
`should` · 可信度 `high` · 适用: smt, bom · 标签: cat-feeder

**规则** 选型时只用目标贴片厂有料、能贴装的封装；无源件优先用贴片厂的基础库（Basic）料，尽量减少不同料号的扩展库（Extended）料种数； BOM 每一行必须能匹配到厂方料号（LCSC Part #）。

**依据** JLC 对每个不同的扩展库料收一次上料费，BOM 里匹配不到库的料不会被贴装；在选型阶段处理比在下单前改封装代价小得多。

| 参数 | 判据 | 备注 |
|---|---|---|
| `extended_part_loading_fee` | == 3 USD/料种 | JLCPCB PCB Assembly FAQ：每个扩展库料种；Preferred Extended 在 Economic 组装免该费。费用以官网当前页面为准 |

**验证**
- `bom_check`（full）· kicad-cli sch export bom + JLC/LCSC 零件库查询脚本 — BOM 每个非 DNP 行都必须有 LCSC Part #（格式 Cxxxx）且能在库中匹配；统计 Basic / Preferred / Extended 数量， 匹配不到的行为失败；输出唯一扩展库料种数及对应费用。

**来源**
- [PCB Assembly FAQs](https://jlcpcb.com/help/article/pcb-assembly-faqs) — JLCPCB, vendor_guide, Basic vs. Extended components
- [How to generate BOM and Pick and Place file in Sprint-Layout 6（LCSC Part # 写入 Comment，格式 Cxxxx）](https://jlcpcb.com/help/article/how-to-generate-bom-and-pick-and-place-file-in-sprint-layout-6) — JLCPCB, vendor_guide

<a id="GEN-ARC-006"></a>
#### GEN-ARC-006 · MCU / 模块选型前做引脚预算并剔除受限引脚
`should` · 可信度 `high` · 适用: mcu, module, esp32 · 标签: cat-feeder

**规则** 选 MCU 或模块之前，列出全部需要的外设、信号和 ADC 通道，映射到具体引脚形成引脚分配表；把不能自由使用的引脚（strapping、 flash / PSRAM 占用、USB、调试口、上电毛刺、受限的 ADC 通道）标出并排除；给调试口和测试点留出空闲引脚；读器件勘误表。

**依据** 引脚总数不等于可用 GPIO。ESP32-C3 的 GPIO2 / 8 / 9 是 strapping 引脚，部分引脚上电有毛刺，ADC2 在部分版本上不可用； 在布局之后才发现引脚冲突，只能改板或牺牲功能。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esp32c3_strapping_pins` | qualitative | GPIO2、GPIO8、GPIO9（数据手册 Table 3-1） |
| `esp32c3_power_up_low_glitch_duration` | == 5 ns | MTCK、MTDO、GPIO10、U0RXD 上电低电平毛刺（数据手册 Table 2-2） |
| `esp32c3_gpio18_power_up_high_glitch_duration` | == 50000 ns | GPIO18 上电高电平毛刺约 50 us（数据手册 Table 2-2） |

**验证**
- `review`（partial）· 引脚分配表（YAML / CSV）+ 自写校验脚本 — 脚本读取分配表和器件受限引脚清单（strapping、flash、USB、JTAG、毛刺引脚），任何功能落在受限引脚上必须有书面豁免； 再与 kicad-cli 导出的网表比对，保证表中引脚和原理图一致。

**来源**
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, Table 2-1 Pin Overview、Table 2-2 Power-Up Glitches on Pins、Table 3-1
- [Schematic Checklist - ESP32-C3（GPIO、ADC 两节）](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide

<a id="GEN-ARC-008"></a>
#### GEN-ARC-008 · 先定上电时序与复位释放条件
`should` · 可信度 `high` · 适用: mcu, multi_rail, supervisor · 标签: cat-feeder

**规则** 在架构阶段写明各电源轨的上电 / 掉电顺序和复位释放条件，并满足器件手册的时序（ESP32-C3 的具体数值见 GEN-SCH-007 与 GEN-SCH-006）； 轨电压上升慢或不稳（电池充电、光伏等）时加电源监控器。 多电压器件之间若存在反向供电或闩锁风险，要么限定先后顺序，要么用器件手册给出的钳位办法。

**依据** 一条轨有电、另一条轨还没起来时，芯片内部隔离结构可能正偏产生电流，严重时触发闩锁。 复位在电源稳定之前释放，芯片会带着未定义的内部状态启动。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esp32c3_power_monitor_threshold` | == 3.0 V | Espressif 建议的监控器阈值，约 3.0 V，用于慢速 / 不稳定供电 |

**验证**
- `spice`（partial）· ngspice / LTspice（电源斜坡 + 复位 RC 的瞬态仿真） — 用实际电源上升时间（最慢和最快各一个）仿真：CHIP_EN 上升越过 VIL_nRST（0.25 x VDD，数据手册 Figure 2-4 中 tSTBL 的终点）的时刻必须晚于各电源轨达到 2.8 V（Figure 2-4 的标注点）至少 50 us， 且 EN 随后要升过 VIH_nRST（0.75 x VDD）；掉电再上电的最短间隔下 EN 也必须低于 VIL_nRST 至少 50 us（tRST）。
- `bench`（manual）· 示波器（多通道） — 同时抓取 5 V、3V3、EN、strapping 引脚，确认顺序和时间间隔满足上述参数，覆盖冷启动、热复位和欠压恢复。

**来源**
- [Power Supply Sequencing Solutions for Dual Supply Voltage DSPs (SLVA073A)](https://www.ti.com/lit/an/slva073a/slva073a.pdf) — Texas Instruments, app_note, 1.1 Core and I/O Sequencing Requirements
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, 2.5.3 Chip Power-up and Reset, Table 2-11, Table 3-2
- [Schematic Checklist - ESP32-C3](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, Chip Power-up and Reset

<a id="GEN-ARC-010"></a>
#### GEN-ARC-010 · 连接器按触点数与温度折算电流并防插错
`should` · 可信度 `medium` · 适用: connector, power_input, motor_output · 标签: cat-feeder

**规则** 选连接器时，用厂家的降额曲线按同时通电的触点数和最高环境温度折算每触点电流；没有曲线时按额定电流的 50% 使用； 同时选带防呆（极性定位）的型号，并核对线缆是直连还是镜像接线。

**依据** 连接器发热正比于 I^2R，电流翻倍发热变成四倍；多触点同时通电会互相加热，每触点可用电流比单触点额定值小。 环境温度升高时接触电阻上升，温升更大。线缆接反在原型阶段很常见。

| 参数 | 判据 | 备注 |
|---|---|---|
| `connector_current_stress_max` | <= 0.5 额定电流的比例 | NASA PD-ED-1201：继电器与连接器；无降额曲线时的保守默认 |
| `samtec_per_contact_fraction_50pct_energized` | == 0.75 单触点额定电流的比例 | Samtec 博客的经验值：50% 触点通电；仅 Samtec 系列，具体以所选系列曲线为准 |
| `samtec_per_contact_fraction_100pct_energized` | == 0.6 单触点额定电流的比例 | 同上，100% 触点通电 |
| `connector_temp_rise_max` | <= 30 K | Wurth 为 UL1059 取的最大温升，各厂商 / 标准取值不同 |

**验证**
- `bom_check`（partial）· 电源预算表 + 连接器降额数据 — 每个电源连接器：I_per_contact = I_rail_peak / 并联触点数，必须 <= 曲线给出的 (额定电流 x 通电触点折算系数) 在最高环境温度下的值； 曲线缺失时 I_per_contact <= 0.5 x 额定。
- `bench`（manual）· 热电偶 / 热像仪 — 在最坏电流下测连接器温升，与厂家规定的最大温升（如 30 K）比较。
- `review`（manual）· 接口表 — 逐个连接器核对引脚定义、是否防呆、对端线缆是直连还是镜像。

**来源分歧** NASA 的 50% 是通用上限，Samtec 的触点折算系数和 Wurth 的温升判据是连接器系列相关的方法，数值不能互相替代。 取舍：有厂商降额曲线时用曲线，没有曲线时用 50% 作为保守默认。

**来源**
- [Derating of Connectors (ANE006a)](https://www.digikey.com/Site/Global/Layouts/DownloadPdf.ashx?pdfUrl=4032FAAF37CF46A1A3088C1458463D5C) — Wurth Elektronik, app_note, 2.1 Temperature rise theory, 3.1 Derating
- [Connector Voltage and Power Rating 101](https://blog.samtec.com/post/connector-voltage-and-power-rating-101/) — Samtec, vendor_guide
- [PD-ED-1201 EEE Parts Derating](https://extapps.ksc.nasa.gov/Reliability/Documents/Preferred_Practices/1201.pdf) — NASA GSFC, standard, Table 1
- [pcb-checklist: schematic checklist（Verify pinout of cables to other boards）](https://github.com/azonenberg/pcb-checklist/blob/master/schematic-checklist.md) — Andrew Zonenberg, blog

## 符号封装库（library）

<a id="GEN-LIB-001"></a>
#### GEN-LIB-001 · 符号的引脚号、名称和电气类型逐脚对照数据手册
`must` · 可信度 `high` · 适用: symbol, ic, module, connector · 标签: cat-feeder

**规则** 新建或引入的每个符号，在首次使用前把每个引脚的编号、名称和电气类型（输入 / 输出 / 电源输入 / 无连接）逐脚对照数据手册或厂商引脚表核对， 即使符号来自可信库或你以前用过。电源输入脚不得隐藏，不接的脚设为 Not Connected 并隐藏。

**依据** 库错误能通过所有 ERC 和 DRC，直到板子回来才暴露。ERC 的判断依赖符号里正确的电气类型， 类型填错会让它漏报或误报；隐藏的电源脚会产生看不见的隐式连接。

**验证**
- `review`（partial）· 两人互查 + 自写脚本（符号引脚表 vs 数据手册引脚表 CSV） — 脚本解析 .kicad_sym 中每个 pin 的 number、name、electrical type，与从数据手册提取的引脚表逐行比对， 数量、编号、名称不一致即失败；另检查 power_in 类型的脚没有 hide 属性。 数据手册引脚表需由第二人确认提取无误。
- `erc`（full）· KiCad Symbol Editor 的符号检查器 + ERC — 符号检查器对该符号无错误；原理图 ERC 在 pin_to_pin、pin_not_driven 类别上无异常。

**来源**
- [Schematic Design Review Checklist](https://resources.altium.com/p/schematic-review-checklist) — Altium, vendor_guide, Pin verification
- [pcb-checklist: schematic checklist](https://github.com/azonenberg/pcb-checklist/blob/master/schematic-checklist.md) — Andrew Zonenberg, blog, Datasheet verification
- [KiCad 10 Schematic Editor manual（pin electrical types、symbol checker、ERC）](https://docs.kicad.org/10.0/en/eeschema/eeschema.html) — KiCad, tool_doc, Electrical rules checking / Symbol editor
- [KLC S4.1 General pin requirements / S4.6 Hidden pins](https://klc.kicad.org/symbol/s4/s4.6/) — KiCad, tool_doc

<a id="GEN-LIB-002"></a>
#### GEN-LIB-002 · 焊盘图形取自厂商推荐或 IPC-7351 并1:1核对
`must` · 可信度 `medium` · 适用: footprint, smd, qfn · 标签: cat-feeder

**规则** 封装焊盘优先采用器件厂商数据手册里的推荐焊盘图形；没有时用 IPC-7351 的生成规则，回流焊量产取 Nominal（N）密度等级， 手工焊 / 原型取 Most（M），高密度取 Least（L），并把等级写进封装名或描述。新封装必须与数据手册机械图的尺寸做 1:1 对照。

**依据** 焊盘尺寸决定焊点形态（趾部、跟部、侧向焊脚）与桥连风险。TI 对 0.5 mm 间距的 QFN 要求焊盘宽度缩到 0.28 mm 以下以免桥连， 说明通用规则不能代替具体封装的推荐值。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ipc7351_default_density_level` | qualitative | 回流焊量产用 Nominal（N）；M 为手工焊 / 原型，L 为高密度 |
| `qfn_pad_width_0p5mm_pitch` | <= 0.28 mm | TI SLUA271：0.5 mm 间距 QFN/SON 避免桥连的焊盘宽度，以具体器件手册为准 |

**验证**
- `geometry_script`（partial）· 解析 .kicad_mod 的 Python 脚本 — 从数据手册推荐焊盘图形整理成 YAML（焊盘中心坐标、尺寸），脚本逐焊盘比对 .kicad_mod， 中心偏差和尺寸偏差都不得超过项目设定的容差（建议 0.05 mm，属项目选择）；焊盘数不一致即失败。
- `review`（manual）· 1:1 打印纸样 / STEP 叠图 — 把封装按 1:1 打印，放上实物器件，或把 STEP 模型叠在焊盘上，确认引脚落在焊盘中并留有焊脚空间。

**来源**
- [QFN and SON PCB Attachment (SLUA271C)](https://www.ti.com/lit/slua271) — Texas Instruments, app_note, 3.1 Land Pad Styles, 3.2 Land Pad Design, 3.3 Lead Finger Pad PCB Design
- [PCB Land Pattern Design — IPC-7351B 密度等级与命名](https://www.atlaspcb.com/blog/pcb-land-pattern-design-ipc-7351b-footprint-standards/) — AtlasPCB, blog
- IPC-7351B Generic Requirements for Surface Mount Design and Land Pattern Standard（IPC-7351B（付费标准，未取得正文）） — IPC, standard

<a id="GEN-LIB-005"></a>
#### GEN-LIB-005 · 自动核对符号引脚与封装焊盘一致
`must` · 可信度 `high` · 适用: symbol, footprint · 标签: cat-feeder

**规则** 对每个库器件自动检查：符号的每个引脚号都能在所选封装里找到同号焊盘（刻意省略的 NC 脚除外），封装里每个有电气意义的焊盘号都对应一个符号引脚； 重复焊盘号只允许出现在刻意的多焊盘连接（散热焊盘、并联大电流焊盘）。

**依据** 符号与封装由不同人在不同时间做，引脚号错位是最常见的库缺陷。KiCad 的相关 DRC 项默认只是警告或被忽略， 只看 DRC 的 error 数会漏掉。

**验证**
- `erc`（full）· 自写脚本：kicad-cli sch export netlist --format kicadsexpr + 解析 .kicad_mod — 遍历网表中每个 (位号, 引脚号)，在对应封装文件里查同号焊盘；再反向查封装里未被引用的焊盘号。 两个方向的差集都必须为空，或在白名单（NC、散热焊盘）内。
- `netlist_diff`（full）· kicad-cli pcb drc --schematic-parity --severity-all --exit-code-violations — 报告中不得出现 Pad net doesn't match schematic（默认 Warning）、Footprint doesn't match symbol's footprint filters（默认 Ignore， 需手动打开）、Footprint component type doesn't match footprint pads（默认 Ignore，需手动打开）。

**来源**
- [KiCad 10 PCB Editor manual — List of DRC checks（Schematic parity 表）](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Design rules checking / Schematic parity

<a id="GEN-LIB-003"></a>
#### GEN-LIB-003 · 每个封装画闭合的 courtyard 并满足外扩量
`should` · 可信度 `medium` · 适用: footprint, courtyard

**规则** 每个封装在 F.CrtYd（需要时 B.CrtYd）画闭合的 courtyard，外扩量不小于项目规定值：KLC 默认 0.25 mm，部件任一边小于 1.5 mm 时 0.15 mm， 连接器、罐形电容、晶体 0.5 mm，BGA 1.0 mm；线宽 0.05 mm，坐标落在 0.01 mm 网格上。

**依据** courtyard 是贴片机吸嘴、返修和装配公差需要的最小净空，DRC 靠它检查相邻元件是否重叠。 没有 courtyard 的封装等于不参与间距检查。

| 参数 | 判据 | 备注 |
|---|---|---|
| `courtyard_clearance_default` | >= 0.25 mm | KLC F5.3 默认；IPC-7351 的 Nominal 等级同为 0.25 mm |
| `courtyard_clearance_small_part` | >= 0.15 mm | KLC F5.3：部件小于 1.5 mm 时 |
| `courtyard_clearance_connector_canned_cap_crystal` | >= 0.5 mm | KLC F5.3；连接器另需加上插拔所需空间 |
| `courtyard_clearance_bga` | >= 1.0 mm | KLC F5.3；含 WLCSP 等 |
| `courtyard_line_width` | == 0.05 mm | KLC F5.3 |
| `courtyard_grid` | == 0.01 mm | KLC F5.3 |
| `ipc7351_courtyard_excess_most_nominal_least` | 0.1 … 0.5 mm | IPC-7351B 按密度等级：Most 0.5、Nominal 0.25、Least 0.1（每边） |

**验证**
- `drc`（full）· KiCad DRC（kicad-cli pcb drc --severity-all） — DRC 不得有 courtyard 重叠违规；重叠被 DRC 作为违规报告，不要在 DRC 设置里把该项设为忽略。
- `geometry_script`（full）· 解析 .kicad_mod 的脚本 — 对每个封装，计算焊盘与 F.Fab 本体外框的包络，courtyard 外框到包络的最小距离必须 >= 对应分类的外扩量； 缺少 F.CrtYd 图形的封装直接失败。

**来源分歧** IPC 体系内数值不统一：PCB Libraries 论坛转引的 IPC-7352 表按焊盘边 / 本体边分列（SMD：焊盘边 0.50 / 0.25 / 0.20 mm，本体边 1.00 / 0.50 / 0.25 mm）， 同一帖子里另一位用户说 IPC-7352 只给每个等级一个值；该厂商自己的偏好又是 0.10 / 0.20 / 0.40 mm； 各来源对 A/B/C 与 M/N/L 的对应也不一致。取舍：以 KiCad KLC 的 0.25 mm 默认值作为可复现基线， 项目有更紧凑的需求时在项目策略里明确放宽并让贴片厂确认。

**来源**
- [KLC F5.3 Courtyard layer requirements](https://klc.kicad.org/footprint/f5/f5.3.html) — KiCad, tool_doc
- [KiCad 10 PCB Editor manual（Footprint properties：courtyard 重叠产生 DRC 违规）](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Footprint properties
- [PCB Land Pattern Design — IPC-7351B](https://www.atlaspcb.com/blog/pcb-land-pattern-design-ipc-7351b-footprint-standards/) — AtlasPCB, blog

<a id="GEN-LIB-004"></a>
#### GEN-LIB-004 · 带散热焊盘的封装补全焊盘编号、过孔与钢网开窗
`should` · 可信度 `high` · 适用: qfn, son, sot223, module_gnd_pad · 标签: cat-feeder

**规则** 带裸露焊盘 / 散热片的封装（QFN、SON、SOT-223 的散热片、模块底部地焊盘）在符号里有对应编号的引脚，在封装里有同编号的焊盘， 尺寸与器件裸露焊盘一致；散热过孔与焊盘同编号；锡膏开窗做成约 50-70% 覆盖的分块，而不是 1:1 全开。

**依据** 裸露焊盘既是散热路径也是机械固定。1:1 开窗焊料体积过大会让器件浮起造成开路；过孔会吸走焊料，需要控制孔径和是否塞孔。 焊盘编号缺失会让这块铜在网表里没有网络，ERC 和 DRC 都不报。

| 参数 | 判据 | 备注 |
|---|---|---|
| `thermal_pad_pcb_size_vs_package` | == 1 x 器件裸露焊盘 | SLUA271 3.4：PCB 散热焊盘尺寸与器件裸露焊盘相等 |
| `thermal_pad_to_lead_pad_clearance_min` | >= 0.2 mm | SLUA271 3.4：防桥连的最小间隙，对多数设计足够 |
| `thermal_via_pitch` | == 1.0 mm | SLUA271 3.4.1：热要求高时过孔间距约 1.0 mm |
| `thermal_via_drill_start` | == 0.3 mm | SLUA271：起始孔径；更小孔径焊料流失风险更小。KLC F4.4 给 0.2-0.3 mm |
| `exposed_pad_paste_coverage` | 50 … 70 % | SLUA271C 4.4：锡膏覆盖约为焊盘面积的 50-70% |
| `thermal_pad_voiding_max` | <= 50 % | SLUA271C 4.4：大功率应用回流后空洞率，需 X 光确认 |
| `klc_back_copper_pad_margin_min` | >= 0.5 mm | KLC F4.4：热过孔连到背面铜焊盘时，背面焊盘需包住过孔并留的边距 |

**验证**
- `geometry_script`（partial）· 解析 .kicad_mod 与 .kicad_sym 的脚本 — 对含裸露焊盘的器件：符号中存在对应编号的引脚（如 EP / 末位编号）；封装中该编号的焊盘尺寸与数据手册一致； 锡膏层开口总面积 / 铜焊盘面积 在 [0.5, 0.7]；过孔孔径 0.2-0.3 mm 且与焊盘同编号。
- `bench`（manual）· X 光 — 首件回流后拍散热焊盘，空洞面积占比 <= 50%（大功率应用）。

**来源分歧** SLUA271 的 2018 年修订版 B 与 2023 年修订版 C 都写锡膏覆盖约 50-70%（C 版修订历史只改了编号格式；2002 年原版未取得原文）； 其他厂商的 QFN 指南可能给出不同的覆盖范围（未核对）。 取舍：按所用器件的厂商指南为准，没有时用 TI 最新修订版的 50-70%，并以首件 X 光结果修正。

**来源**
- [QFN and SON PCB Attachment (SLUA271C)](https://www.ti.com/lit/slua271) — Texas Instruments, app_note, 3.4 Exposed Pad PCB Design, 3.4.1 Thermal Pad Via Design, 4.4 Exposed-Pad Stencil Design
- [KLC F4.4 Thermal pads](https://klc.kicad.org/footprint/f4/f4.4.html) — KiCad, tool_doc

<a id="GEN-LIB-006"></a>
#### GEN-LIB-006 · 3D 模型对准焊盘并核对与贴片厂的旋转约定
`should` · 可信度 `medium` · 适用: footprint, 3d_model, smt_assembly · 标签: cat-feeder

**规则** 每个非虚拟封装引用一个 STEP 3D 模型，偏移 (0,0,0)、缩放 1、旋转 0，模型已在三维软件中对准封装； 下单前在贴片厂的贴装预览里逐个核对 1 脚方向和极性，需要时在封装或 CPL 里记录旋转偏移。

**依据** KiCad 封装的 0 度方向和贴片厂器件库的约定不一定相同，旋转错误不会触发 DRC，只会造成整批元件贴反。 模型偏移不为零说明模型和焊盘实际不对齐，3D 干涉检查结果也不可信。

| 参数 | 判据 | 备注 |
|---|---|---|
| `model_offset_xyz` | == 0 mm | KLC M2.2 / F9.3：模型偏移必须为 (0,0,0) |
| `model_scale` | == 1 倍 | KLC：缩放 1:1:1，STEP 自带绝对尺寸 |
| `model_rotation` | == 0 deg | KLC：旋转 0 |

**验证**
- `geometry_script`（partial）· 解析 .kicad_mod 的 model 块的脚本；kicad-cli pcb export glb/pos — 所有非虚拟封装都有 model 引用；offset、scale、rotate 均为零 / 1；导出位置文件后，对每个封装检查模型包络中心与焊盘包络中心的偏差。
- `review`（manual）· 贴片厂订单预览（JLCPCB 贴装预览） — 逐个有极性或 1 脚的器件（IC、二极管、LED、钽电容、连接器）核对预览里的朝向，不一致则调整 CPL 的 Rotation 后重新上传。

**来源**
- [KLC F9.3 Footprint 3D model requirements](https://klc.kicad.org/footprint/f9/f9.3/) — KiCad, tool_doc
- [KLC M2.2 Model alignment and scaling](https://klc.kicad.org/model/m2/m2.2.html) — KiCad, tool_doc
- [How to generate BOM and Pick and Place file in Sprint-Layout 6（预览中发现朝向错误，修改 CPL 的 Rotation）](https://jlcpcb.com/help/article/how-to-generate-bom-and-pick-and-place-file-in-sprint-layout-6) — JLCPCB, vendor_guide

<a id="GEN-LIB-007"></a>
#### GEN-LIB-007 · 库只有一个来源：项目内库表且纳入版本控制
`should` · 可信度 `high` · 适用: library, version_control · 标签: cat-feeder

**规则** 进入板子的符号和封装只来自项目目录内、受版本控制的库，库表用 ${KIPRJMOD} 相对路径引用；不依赖个人全局库表。 同一个料号和封装只允许有一份权威定义，改库后必须把改动更新到原理图副本和 PCB 并重新跑 ERC / DRC。

**依据** KiCad 的原理图里放的是符号的副本，改库不会自动更新副本；项目库表优先于全局库表， 换一台机器或换一个人打开可能得到不同的符号或封装，导致输出文件不可复现。

**验证**
- `erc`（full）· 自写脚本 + kicad-cli sch erc — 解析项目 sym-lib-table 与 fp-lib-table：每个条目的 URI 必须在项目目录内（${KIPRJMOD} 展开后）且文件已被 git 跟踪； ERC 中 lib_symbol_mismatch、lib_symbol_issues、footprint_link_issues 必须为 0。
- `drc`（full）· kicad-cli pcb drc --schematic-parity --severity-all — 不得出现 Footprint doesn't match copy in library、Footprint not found in libraries（二者默认都只是 Warning）。

**来源**
- [KiCad 10 Schematic Editor manual — Symbol library tables](https://docs.kicad.org/10.0/en/eeschema/eeschema.html) — KiCad, tool_doc, Symbols and Symbol Libraries
- [KiCad 10 PCB Editor manual — DRC 杂项检查（Footprint doesn't match copy in library）](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, List of DRC checks
- [Version control for KiCad projects（提交项目本地库与库表）](https://boardrepo.com/guides/kicad-version-control) — BoardRepo, blog

<a id="GEN-LIB-008"></a>
#### GEN-LIB-008 · 库器件携带制造商、型号、数据手册和厂方料号
`should` · 可信度 `high` · 适用: library, bom · 标签: cat-feeder

**规则** 每个库器件填写制造商、制造商型号（MPN）、数据手册链接、贴片厂料号（LCSC Part #，格式 Cxxxx）和封装字段； 同一个值加同一封装只保留一个料号。BOM 导出包含这些字段，字段为空的非 DNP 行视为未完成。

**依据** 贴片厂按料号匹配 BOM，匹配不到的行不会被贴装；字段缺失还会让生命周期核查和二次采购无法自动化。

**验证**
- `bom_check`（full）· kicad-cli sch export bom --fields Reference,Value,Footprint,${QUANTITY},${DNP},MPN,LCSC — 导出 CSV 后脚本检查：非 DNP 行的 MPN、LCSC、Datasheet 非空；LCSC 匹配 ^C[0-9]+$；同 (Value, Footprint) 只对应一个 LCSC 号。

**来源**
- [Schematic Design Review Checklist（每个符号指定制造商和料号；一个值一个料号）](https://resources.altium.com/p/schematic-review-checklist) — Altium, vendor_guide, BOM and part checks
- [PCB Assembly FAQs](https://jlcpcb.com/help/article/pcb-assembly-faqs) — JLCPCB, vendor_guide
- [KiCad Command-Line Interface — sch export bom](https://docs.kicad.org/8.0/en/cli/cli.html) — KiCad, tool_doc

## 原理图（schematic）

<a id="GEN-SCH-004"></a>
#### GEN-SCH-004 · 为每个输入定义确定电平，不允许悬空
`must` · 可信度 `high` · 适用: digital_io, cmos, mcu · 标签: cat-feeder

**规则** 每个输入、使能、模式选择和开漏 / 三态线在所有状态（上电、复位、线缆拔出）下都有确定电平：外部上拉 / 下拉； 未使用的 CMOS 逻辑输入接电源或地；MCU 内部上下拉只有在该引脚复位状态允许时才可依赖。电阻取值不得使输入跳变时间超出器件限制。

**依据** CMOS 输入悬空或缓慢穿越阈值区时，P 管 N 管同时导通，电源电流可达毫安级，还可能引起输出振荡与可靠性问题。 MCU 复位期间多数 GPIO 只是输入使能、没有上下拉，表现为高阻。

| 参数 | 判据 | 备注 |
|---|---|---|
| `bus_pullup_pulldown_resistance` | 1000 … 10000 ohm | TI SCBA004E 第 5 节：用于保持总线确定状态，通常 1-10 kOhm；还要满足最大输入跳变时间 |
| `esp32c3_internal_pullup_typ` | == 45 kohm | 数据手册 Table 5-4 的内部弱上拉典型值；复位期间多数 GPIO 无上拉（Table 2-1） |
| `esp32c3_input_leakage_max` | <= 50 nA | Table 5-4 的 IIH / IIL |

**验证**
- `erc`（partial）· KiCad ERC + 自写网表脚本 — ERC 中 pin_not_driven、pin_not_connected 为 0；脚本另检查：只连接输入类引脚、没有驱动脚也没有电阻上下拉的网络（悬空输入）必须为 0。
- `bench`（manual）· 万用表 / 示波器 — 断开外部连接线后，逐个测量这些输入端的静态电平，必须处于确定的高或低；上电瞬间用示波器看有无中间电平。

**来源**
- [Implications of Slow or Floating CMOS Inputs (SCBA004E)](https://www.ti.com/lit/an/scba004e/scba004e.pdf) — Texas Instruments, app_note, 1 Characteristics of Slow or Floating CMOS Inputs, 5 Pull-up or Pull-down Resistors
- [Schematic Checklist - ESP32-C3](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, GPIO
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, Table 2-1, Table 5-4
- [Schematic Design Review Checklist（Pull-ups and pull-downs）](https://resources.altium.com/p/schematic-review-checklist) — Altium, vendor_guide

<a id="GEN-SCH-005"></a>
#### GEN-SCH-005 · 执行器驱动脚在上电和复位期间必须保持关断
`must` · 可信度 `high` · 适用: mosfet_gate, motor_driver, relay_driver · 标签: cat-feeder

**规则** 驱动 MOSFET 栅极、继电器、电机驱动使能的每个 MCU 引脚，必须有外部下拉（或拉向关断态）电阻，使引脚高阻或有毛刺期间栅极电压始终低于 Vgs(th) 最小值； 优先选没有已知上电毛刺的引脚，固件启动最早期把该引脚设成关断态输出。

**依据** ESP32-C3 复位期间大部分 GPIO 只是输入使能、没有上下拉，栅极悬空会随机导通；个别引脚上电还有 5 ns 低电平毛刺，GPIO18 有约 50 us 的高电平毛刺。 引脚漏电流上限 50 nA，100 kOhm 下拉只产生 5 mV，对栅极阈值没有影响。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esp32c3_input_leakage_max` | <= 50 nA | 数据手册 Table 5-4：IIH / IIL，用来估算下拉电阻的上限 |
| `esp32c3_gpio18_high_glitch` | == 50000 ns | Table 2-2：GPIO18 上电高电平毛刺约 50 us，不要用它直接驱动执行器 |
| `esp32c3_low_glitch_pins` | == 5 ns | Table 2-2：MTCK、MTDO、GPIO10、U0RXD 上电低电平毛刺 |

**验证**
- `erc`（full）· 自写脚本：kicad-cli sch export netlist — 对每个 MOSFET 栅极（或驱动器使能）网络：必须存在一个电阻接到源极 / 地，阻值 <= 项目设定上限（示例板取 100 kOhm）；栅极网络不得直接连到 GPIO18。
- `spice`（partial）· ngspice / LTspice — 栅极 RC（含栅极电容）接高阻 MCU 引脚模型，再注入 50 us 的高电平毛刺：栅极峰值电压必须 < MOSFET 的 Vgs(th) 最小值，并留出余量。
- `bench`（manual）· 示波器 + 电流探头 — 多次冷启动、按复位键、切 EN，监视栅极和电机电流，不得出现非预期的动作或电流。

**来源**
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, Table 2-1 Pin Overview, Table 2-2 Power-Up Glitches on Pins, Table 5-4
- [Schematic Design Review Checklist（power-up-critical pins such as MOSFET and transistor gates）](https://resources.altium.com/p/schematic-review-checklist) — Altium, vendor_guide, Pull-ups and pull-downs
- [Schematic Checklist - ESP32-C3（GPIO 上电毛刺）](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, GPIO

<a id="GEN-SCH-006"></a>
#### GEN-SCH-006 · strapping / boot 引脚按手册配置且不加冲突负载
`must` · 可信度 `high` · 适用: esp32, mcu_boot · 标签: cat-feeder

**规则** 对 MCU 的 strapping 和 boot 引脚，在原理图里写明复位释放时需要的电平，并保证外部电路（上拉、下拉、按键、模块）满足该电平和保持时间， 不在这些引脚上挂会改变电平或延时的负载。ESP32-C3：GPIO9 加上拉（按键拉低进入下载模式），GPIO2 也建议上拉，GPIO8 在 ROM 打印控制中有作用；GPIO9 不加大电容。

**依据** strapping 引脚在复位释放时被锁存，电平错误会让芯片进入下载模式或不同的启动配置； GPIO9 加大电容会拖慢上升沿而被误判成低电平。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esp32c3_spi_boot_levels` | qualitative | GPIO2=1，GPIO8=任意，GPIO9=1（Table 3-3） |
| `esp32c3_download_boot_levels` | qualitative | GPIO2=1，GPIO8=1，GPIO9=0（Table 3-3） |
| `esp32c3_strapping_setup_time` | >= 0 ms | tSU（Table 3-2） |
| `esp32c3_strapping_hold_time` | >= 3 ms | tH：CHIP_EN 变高之后需保持的时间（Table 3-2） |

**验证**
- `erc`（partial）· 自写脚本：kicad-cli sch export netlist — GPIO2、GPIO8、GPIO9 网络上：存在到 3V3 的上拉电阻（GPIO9、GPIO2 必须），没有对地的大电容，没有其他输出驱动或有源负载。
- `bench`（manual）· 示波器 + UART 启动日志 — 抓 CHIP_EN 上升沿和 GPIO9 电平，确认 tH >= 3 ms 内电平稳定；不按 BOOT 时串口显示正常启动，按住 BOOT 复位后进入下载模式。

**来源**
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, 3 Boot Configurations, Table 3-1, 3-2, 3-3
- [Schematic Checklist - ESP32-C3](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, Strapping Pins

<a id="GEN-SCH-007"></a>
#### GEN-SCH-007 · 复位 / 使能引脚不得悬空并满足上电时序
`must` · 可信度 `high` · 适用: esp32, mcu_reset · 标签: cat-feeder

**规则** 复位 / 使能引脚（ESP32-C3 的 CHIP_EN）必须有确定电平，不得悬空；用 RC 延时使它在电源稳定之后才释放，建议 10 kOhm + 1 uF， 再按实际电源上升时间调整；上升慢或不稳的供电加监控器；复位走线要短；手动复位键与电容之间加串联电阻限制放电电流。

**依据** 复位过早释放，芯片会在电压不足时启动；走线长会耦合干扰导致误复位。 电容直接被开关短路时，放电电流只受接触电阻限制，开关抖动还会产生尖峰。

| 参数 | 判据 | 备注 |
|---|---|---|
| `chip_en_pullup_resistance` | == 10 kohm | Espressif 建议的起始值，按实际电源时序调整 |
| `chip_en_capacitance` | == 1 uF | 同上 |
| `esp32c3_rail_stable_before_chip_en` | >= 50 us | tSTBL（Table 2-11） |
| `esp32c3_chip_en_low_to_reset` | >= 50 us | tRST（Table 2-11） |
| `esp32c3_vil_nrst_max` | <= 0.25 x VDD | 复位阈值 VIL_nRST（Table 5-4） |
| `esp32c3_vih_nrst_min` | >= 0.75 x VDD | 释放阈值 VIH_nRST（Table 5-4） |

**验证**
- `spice`（partial）· ngspice / LTspice — 用最慢和最快的电源上升时间仿真 RC 与上拉：EN 上升越过 0.25 x VDD（VIL_nRST，数据手册 Figure 2-4 中 tSTBL 的终点）的时刻晚于各电源轨达到 2.8 V（Figure 2-4 的标注点）至少 50 us， 且 EN 随后升过 0.75 x VDD（VIH_nRST）；掉电后再上电时 EN 低于 0.25 x VDD 的持续时间 >= 50 us。
- `erc`（partial）· 自写脚本：kicad-cli sch export netlist — CHIP_EN 网络上必须同时存在上拉电阻和到地电容；复位按键支路中电容与按键之间有串联电阻。
- `bench`（manual）· 示波器 — 测量 3V3 与 EN 的时序，并连续做 20 次以上冷启动与掉电重启，不得出现启动失败或需要手动复位。

**来源分歧** 不同 MCU 的复位网络值不同：Microchip AVR 手册示例是 4.7 kOhm 上拉加 100 nF，ST 对 NRST 的建议也是 100 nF 量级（未取得原文）， 而 ESP32-C3 的 CHIP_EN 建议 10 kOhm 加 1 uF。取舍：按所用器件的手册取值，不套用其他系列的 RC。

**来源**
- [Schematic Checklist - ESP32-C3](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, Chip Power-up and Reset
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, 2.5.3 Chip Power-up and Reset, Table 2-11, Table 5-4
- [AN2519 AVR Microcontroller Hardware Design Considerations（外接复位开关需串联电阻）](https://ww1.microchip.com/downloads/en/Appnotes/AN2519-AVR-Microcontroller-Hardware-Design-Considerations-00002519B.pdf) — Microchip, app_note, Reset

<a id="GEN-SCH-015"></a>
#### GEN-SCH-015 · 从数据手册典型电路出发并遵守元件限制说明
`must` · 可信度 `high` · 适用: ldo, regulator, datasheet_review · 标签: cat-feeder

**规则** 以数据手册的典型应用电路为起点，逐条读「元件限制」类说明（稳压器输出电容类型 / ESR / 最小值、反馈电阻范围、使能时序）， 偏离典型电路处在原理图注明理由。采购料号的数据手册才是准，不同厂商的同名料可能要求不同。

**依据** 线性稳压器的稳定性依赖输出电容的容值与 ESR，用错类型会振荡；偏离典型电路又未记录，评审和后续维护都无法判断是有意还是失误。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ams1117_umw_output_capacitor` | == 22 uF | UMW 版 AMS1117 手册：22 uF 钽电容可覆盖所有旁路情况；该手册未给出 ESR 范围。其他厂商版本可能要求不同，以实际料号手册为准 |

**验证**
- `review`（manual）· 对照表：原理图元件 vs 数据手册 Typical Application / Component Selection — 每个 IC 列出手册中所有带 must / require / recommended 字样的元件要求，并逐条标记「满足」「偏离（理由）」。
- `spice`（partial）· 厂商 SPICE 模型（ngspice / LTspice） — 对稳压器输出网络做 AC 回路增益或负载阶跃仿真，电容使用有效容值（含直流偏压降低）和 ESR；相位裕度或负载阶跃的稳定性满足厂商判据。
- `bench`（manual）· 示波器 — 负载阶跃和最大 / 最小负载下观察输出，不得有持续振荡。

**来源分歧** 不同厂商的 AMS1117 兼容料数据手册对输出电容要求不一致（有的写 22 uF 钽，有的写 10 uF 钽或 MLCC；后者来自搜索结果摘要，未打开原文）。 取舍：以实际下单料号对应厂商的手册为准，并避免把 MLCC 直接当作 22 uF 钽的替代，除非该手册明确允许。

**来源**
- [AMS1117 1A LDO Voltage Regulator datasheet (UMW)](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/5011/AMS1117.pdf) — UMW, datasheet, FUNCTION DESCRIPTION
- [pcb-checklist: schematic checklist（Confirm linear regulators and references are stable with the selected output cap ESR）](https://github.com/azonenberg/pcb-checklist/blob/master/schematic-checklist.md) — Andrew Zonenberg, blog, Power
- [Schematic Design Review Checklist（Power）](https://resources.altium.com/p/schematic-review-checklist) — Altium, vendor_guide

<a id="GEN-SCH-001"></a>
#### GEN-SCH-001 · 按功能块组织原理图，页间只用层次标签连接
`should` · 可信度 `medium` · 适用: schematic, multi_sheet

**规则** 把原理图分成带标题的功能块（电源输入、每个连接器及其保护、MCU、每个传感器 / 执行器），信号从左到右、电源在上、地在下； 元件多时拆成层次化多页，页间连接只用层次标签（hierarchical label）与图纸引脚；单页内用网络标签代替长连线。

**依据** 评审者靠功能块定位问题；跨页用全局标签乱连会让信号走向无法追踪。层次标签和图纸引脚名不一致时 KiCad 会报错， 便于发现漏接。

**验证**
- `erc`（full）· kicad-cli sch erc --severity-all --exit-code-violations — hier_label_mismatch、duplicate_sheet_names（均为默认 Error）和 label_dangling 必须为 0。
- `review`（manual）· 评审清单 — 每页有标题和功能块边框；每个子页的接口在父页可见；没有为省事而用全局标签跨页的信号（电源轨除外）。

**来源**
- [Creating high quality electronics schematics](https://blog.poly.nomial.co.uk/2025-08-10-creating-high-quality-electronics-schematics.html) — Graham Sutherland, blog, Hierarchy and sheet organisation
- [KiCad 10 Schematic Editor manual — Labels](https://docs.kicad.org/10.0/en/eeschema/eeschema.html) — KiCad, tool_doc, Labels / hierarchical sheets
- [KiCad ERC Error Reference](https://pcbkit.com/tools/kicad-erc-reference/) — pcbkit, blog

<a id="GEN-SCH-002"></a>
#### GEN-SCH-002 · 电源轨用统一的电源符号并规范命名
`should` · 可信度 `medium` · 适用: schematic, power_rail

**规则** 每条电源轨使用唯一的电源符号名；名字里体现电压，用 V 代替小数点（3V3、1V8），大小写固定；电源符号朝上、地符号朝下； 不要对电源网络使用信号标签，也不要让同一条轨出现两种写法。

**依据** KiCad 把仅大小写不同的标签当成不同网络，两种写法的电源轨会悄悄断开；网络只能有一个名字，同网络上出现两个不同标签时只保留一个。 名字里带小数点还可能被部分工具拒绝。

**验证**
- `erc`（full）· kicad-cli sch erc --severity-all --exit-code-violations — similar_power、similar_labels、similar_label_and_power、multiple_net_names、same_local_global_label 全部为 0（默认 Warning）。
- `erc`（full）· 自写脚本：kicad-cli sch export netlist 后用正则检查网络名 — 电源轨网络名匹配 ^[+]?[0-9]+V[0-9]*$|^(VIN|VBUS|VBAT|GND)$ 等项目白名单，含小数点或非白名单的电源轨名失败。

**来源**
- [KiCad 10 Schematic Editor manual — Net name assignment / Labels](https://docs.kicad.org/10.0/en/eeschema/eeschema.html) — KiCad, tool_doc
- [KiCad ERC Error Reference](https://pcbkit.com/tools/kicad-erc-reference/) — pcbkit, blog
- [Creating high quality electronics schematics](https://blog.poly.nomial.co.uk/2025-08-10-creating-high-quality-electronics-schematics.html) — Graham Sutherland, blog, Net labels and naming / Power symbols

<a id="GEN-SCH-003"></a>
#### GEN-SCH-003 · 每个电源引脚（对）都画出规定值的去耦电容
`should` · 可信度 `high` · 适用: mcu, ic, connector · 标签: cat-feeder

**规则** 每个 IC 电源脚（或相邻的电源 / 地脚对）在原理图中都有数据手册规定值的去耦电容，靠近该 IC 符号并写明容值、介质和耐压； 模拟电源脚（AVCC / VDDA / AREF）单独去耦；每个电源轨的入口有大电容；连接器上的电源脚也有去耦。

**依据** 数字电路在时钟沿上以纳秒级脉冲取电，脉冲电流靠去耦电容就近供给；电容遗漏或值不对，到布局阶段无法弥补。 原理图里写清每个电容服务哪个引脚，布局时才能按引脚就近放置。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esp32c3_vdd3p3_cpu_decoupling` | == 0.1 uF | Espressif：VDD3P3_CPU 靠近引脚 0.1 uF |
| `esp32c3_vdd3p3_bulk` | >= 10 uF | Espressif：VDD3P3 轨 10 uF 外加 0.1 uF；主电源入口至少 10 uF 加 ESD 二极管 |
| `esp32c3_vdd_spi_decoupling` | == 1 uF | Espressif：VDD_SPI 向外部器件供 3.3 V 时靠近引脚 1 uF |
| `mcu_analog_supply_decoupling_typ` | == 100 nF | Microchip AN2519：AVCC / AREF 的典型去耦值 |
| `tantalum_voltage_rating_margin` | >= 20 % | Altium 检查表：钽电容额定电压至少比最大预期电压高 20% |

**验证**
- `erc`（partial）· 自写脚本：kicad-cli sch export netlist --format kicadsexpr — 对每个 IC 的每个电源脚 / 引脚对：该脚所在网络上存在电容，且其另一端接地网络；容值与 IC 的去耦要求表（YAML）一致； 电源网络上电容的数量 >= IC 电源引脚对数。
- `review`（manual）· 评审清单 — 对照数据手册 Power Supply / Decoupling 章节逐脚核对，模拟电源、参考电压脚、连接器电源脚是否遗漏。

**来源分歧** Microchip 要求多电源脚器件的每对电源 / 地脚都要有去耦电容；Sutherland 的文章认为同电压的多个脚可以接到同一个电源端口， 把电容并排画在器件旁边，不必每个电容单独连线，只要用途清楚。 取舍：原理图层面要求「数量和值可追溯到引脚」，不强制逐脚连线的画法；邻近关系由布局阶段的规则检查。

**来源**
- [Schematic Checklist - ESP32-C3](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, Power Supply
- [AN2519 AVR Microcontroller Hardware Design Considerations](https://ww1.microchip.com/downloads/en/Appnotes/AN2519-AVR-Microcontroller-Hardware-Design-Considerations-00002519B.pdf) — Microchip, app_note, 2.1 Digital Supply, 2.2 Analog Supply
- [Schematic Design Review Checklist](https://resources.altium.com/p/schematic-review-checklist) — Altium, vendor_guide, Power / Decoupling

<a id="GEN-SCH-008"></a>
#### GEN-SCH-008 · 未用引脚按手册处理并显式标注
`should` · 可信度 `high` · 适用: mcu, logic_ic, module · 标签: cat-feeder

**规则** 每个未用引脚都有明确处理：未用的 CMOS 逻辑输入接电源或地；未用的 XTAL 引脚接地；未用的 MCU GPIO 配成确定状态 （固件设输出低 / 启用内部上下拉，或预留不贴的外部上下拉焊盘）；数据手册标注 NC 的引脚按手册要求处理； 完全不连的引脚打 No-Connect 标记，使 ERC 保持干净。

**依据** 悬空的 CMOS 输入会引起额外电流和振荡；未连接也未打 NC 标记的引脚在 ERC 里是 Error， 如果被批量静音，真正漏接的引脚也会被一起掩盖。

**验证**
- `erc`（full）· kicad-cli sch erc --severity-all --exit-code-violations — pin_not_connected（默认 Error）、no_connect_connected、no_connect_dangling 均为 0；每个 NC 标记都在引脚上。
- `review`（manual）· 未用引脚表 — 逐个未用引脚核对：手册要求（接地 / 接电源 / 悬空 / 配置输出）、实际处理、固件配置三者一致。

**来源**
- [Implications of Slow or Floating CMOS Inputs (SCBA004E)](https://www.ti.com/lit/an/scba004e/scba004e.pdf) — Texas Instruments, app_note, 5 Pull-up or Pull-down Resistors
- [AN2519 AVR Microcontroller Hardware Design Considerations](https://ww1.microchip.com/downloads/en/Appnotes/AN2519-AVR-Microcontroller-Hardware-Design-Considerations-00002519B.pdf) — Microchip, app_note, 6 Unused XTAL Pins
- [Schematic Checklist - ESP32-C3](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, GPIO / Clock Source
- [KiCad ERC Error Reference](https://pcbkit.com/tools/kicad-erc-reference/) — pcbkit, blog

<a id="GEN-SCH-009"></a>
#### GEN-SCH-009 · 晶体负载电容按公式计算并留出杂散电容
`should` · 可信度 `high` · 适用: crystal, chip_down_mcu

**规则** 芯片级晶体电路：先从晶体数据手册取 CL，估算总杂散电容 Cs（芯片引脚电容加 PCB），按 CL = C1 x C2 / (C1 + C2) + Cs 计算外部电容， 对称时 C1 = C2 = 2 x (CL - Cs)；取标准值后复核增益裕度和驱动功率，样板上用实测频偏微调。

**依据** 振荡频率取决于晶体看到的总负载电容；忽略杂散电容的「两倍 CL」做法会偏大。 增益裕度不足时可能在实验室起振、在高低温下不起振；驱动功率过大会损坏晶体。

| 参数 | 判据 | 备注 |
|---|---|---|
| `stray_capacitance_per_pin_estimate` | 2 … 5 pF | Microchip AN2519 第 5 节：单脚杂散电容 CS 的估计范围（对称布局），其公式写作 Ce + Ci = 2CL - CS；实际取决于布局与芯片引脚电容 |
| `oscillator_gain_margin_min` | >= 5 倍 | ST AN2867 3.4：gm / gm_crit >= 5 才能保证可靠起振 |
| `esp32c3_xtal_frequency_error_after_tuning` | <= 10 ppm | Espressif：在 TX tone 模式下测频偏并调整 C1/C2，需在 +-10 ppm 内；40 MHz 晶体精度 +-10 ppm |
| `esp32c3_xtal_amplitude_min` | > 500 mV | Espressif 建议晶体振幅大于 500 mV |

**验证**
- `tline_calc`（full）· Python 计算脚本 — 输入 CL、Cs、ESR、C0、ppm 预算和 IC 的 gm_crit 参数：输出 C1 = C2、实际 CL、增益裕度 gm / gm_crit（>= 5）、驱动功率 DL（<= 晶体额定）。 公式：CL = C1*C2/(C1+C2)+Cs；gm_crit = 4*ESR*(2*pi*F)^2*(C0+CL)^2。
- `bench`（manual）· 频率计 / 频谱仪（高阻探头） — 在最终板上测振荡频率或射频输出频偏（ESP32-C3 用 TX tone），偏差在晶体和系统的 ppm 预算内；探头电容会改变负载，按手册方法修正。

**来源分歧** Cs 的定义在资料间不同：ST AN2867 与 Espressif 的 Cs 是整个振荡回路的总杂散电容（公式 CL = C1*C2/(C1+C2) + Cs）， Microchip AN2519 的 CS 是单脚杂散电容（公式 Ce + Ci = 2CL - CS）。两种写法等价但数值不能混用； 取舍：沿用所用 MCU 数据手册 / 应用笔记的定义，并在原理图注释里写明 Cs 的取值和定义。

**来源**
- [AN2867 Oscillator design guide for STM8AF/AL/S, STM32 MCUs and MPUs (Rev 13)](https://ecsxtal.com/store/pdf/stm32-microcontroller-application-note-09232021.pdf) — STMicroelectronics, app_note, 3.3 Load capacitance, 3.4 Oscillator transconductance, 3.5 Drive level
- [AN2519 AVR Microcontroller Hardware Design Considerations](https://ww1.microchip.com/downloads/en/Appnotes/AN2519-AVR-Microcontroller-Hardware-Design-Considerations-00002519B.pdf) — Microchip, app_note, 5 Using Crystal and Ceramic Resonators, Equation 2
- [Schematic Checklist - ESP32-C3](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, Clock Source

<a id="GEN-SCH-010"></a>
#### GEN-SCH-010 · 为每个可编程器件引出调试 / 烧录接口
`should` · 可信度 `medium` · 适用: programming, debug, swd, uart · 标签: cat-feeder

**规则** 每个可编程器件都要引出烧录和调试接口，信号齐全：Cortex-M 用 Arm 10 针 1.27 mm 接口（VCC 目标参考电压、SWDIO / TMS、SWDCLK / TCK、GND、nRESET，SWO 视需要）； ESP32-C3 至少引出 UART0 的 TX / RX、GND、CHIP_EN 和 GPIO9（BOOT）。接口线上加保护，睡眠模式下不要对调试口断电。

**依据** 没有可达的烧录口，一次固件问题就变成返工；nRESET 缺失时调试器无法做复位后停机，参考电压脚缺失时调试器无法检测目标电压（必需 / 可选的划分是常见做法，Arm 文档只给出接口定义）。 ESP32 的下载模式靠 GPIO9 与 EN 的组合进入，接口里漏掉其中一个就必须手动短接。

| 参数 | 判据 | 备注 |
|---|---|---|
| `cortex_debug_connector_pitch` | == 1.27 mm | Arm Cortex Debug Connector（10 针）基于 Samtec 0.05 英寸微型插座 |
| `esp32c3_u0txd_series_resistor` | == 499 ohm | Espressif UART 节：U0TXD 串联电阻 |

**验证**
- `erc`（partial）· 自写脚本：kicad-cli sch export netlist — 每个可编程器件对应的接口连接器上能追到：烧录所需全部信号（见规则）和 GND；接口网络上有 ESD 保护器件的连接。
- `bench`（manual）· 烧录器 / esptool — 新板用该接口完成烧录和读回校验，并能进入下载模式。

**来源**
- [Cortex-M Debug Connectors](https://documentation-service.arm.com/static/5fce6c49e167456a35b36af1) — Arm, datasheet, Cortex Debug Connector (10-pin)
- [Schematic Checklist - ESP32-C3](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, UART
- [pcb-checklist: schematic checklist（Debug header）](https://github.com/azonenberg/pcb-checklist/blob/master/schematic-checklist.md) — Andrew Zonenberg, blog

<a id="GEN-SCH-011"></a>
#### GEN-SCH-011 · 在原理图中为电源轨和关键信号预留测试点
`should` · 可信度 `medium` · 适用: test_point, bring_up · 标签: cat-feeder

**规则** 原理图中为每个电源轨放测试点，至少放两个地测试点（探头接地用），并为复位 / 使能、烧录线、时钟和关键模拟节点放测试点； 测试点符号带封装，进入 BOM 与布局检查。测试点集中在板的一面。

**依据** 首板调试靠测试点定位问题；没有测试点时只能飞线或刮绿油。夹具测试时测试点还决定能否使用针床。

| 参数 | 判据 | 备注 |
|---|---|---|
| `test_pad_diameter_preferred` | >= 1.0 mm | FixturFab：贴片测试焊盘首选；最小 0.8 mm |
| `test_pad_diameter_min` | >= 0.8 mm | FixturFab |
| `test_point_pitch_preferred` | >= 1.9 mm | 中心距首选 1.9 mm（75 mil），最小 1.27 mm |
| `test_point_to_board_edge_preferred` | >= 5 mm | FixturFab：首选 5 mm，最小 3.175 mm |
| `test_point_to_nearest_component_preferred` | >= 1.5 mm | FixturFab：首选 1.5 mm，最小 1.0 mm |

**验证**
- `erc`（full）· 自写脚本：kicad-cli sch export netlist — 网表中每条电源轨网络至少有一个 TP 类元件；GND 网络至少有两个；复位 / 使能 / 烧录信号网络各至少一个。
- `geometry_script`（full）· pcbnew Python（参见 ee-pcb-verify 的 geometry 检查器） — 每个 TP 焊盘直径 >= 0.8 mm（首选 1.0 mm），与最近的其他测试点中心距 >= 1.27 mm（首选 1.9 mm），与板边 >= 3.175 mm（首选 5 mm），与最近元件 >= 1.0 mm（首选 1.5 mm），全部在同一面。夹具数值以实际测试厂要求为准。

**来源分歧** 各资料给的焊盘与间距数值略有出入（有的最小 0.9 mm，推荐 1.27 mm），且依赖具体测试夹具。 取舍：以夹具厂文档的 1.0 / 0.8 mm 为基线，下单前以实际测试方的规则为准。DFM 领域的规则可能给出更细的几何要求，这里只管原理图层面的存在性。

**来源**
- [SMD Test Points and Design-for-Test Guidelines for PCBAs](https://fixturfab.com/resources/how-to-test/design-for-test) — FixturFab, vendor_guide
- [pcb-checklist: schematic checklist（Test points）](https://github.com/azonenberg/pcb-checklist/blob/master/schematic-checklist.md) — Andrew Zonenberg, blog
- [Schematic Design Review Checklist（Test points and indicators）](https://resources.altium.com/p/schematic-review-checklist) — Altium, vendor_guide

<a id="GEN-SCH-012"></a>
#### GEN-SCH-012 · 全部元件完成标注，位号唯一且稳定
`should` · 可信度 `high` · 适用: schematic, bom

**规则** 所有元件都已标注（无 ? 号），位号唯一；一旦 PCB 已开始布局， 不得随意重新标注，必须重标时通过「从原理图更新 PCB」传递，并检查网表对比。

**依据** 位号是原理图、BOM、PCB、坐标文件之间的关联键；重复位号或未标注元件会让 BOM 与贴装文件错位， 重新标注又会让已布局的位号与丝印整体对不上。

**验证**
- `erc`（full）· kicad-cli sch erc --severity-all --exit-code-violations — unannotated、duplicate_reference 为 0（两者均默认 Error）。
- `netlist_diff`（full）· kicad-cli pcb drc --schematic-parity --severity-all — 不得出现 Duplicate footprints、Missing footprint、Extra footprint（默认均为 Warning）。

**来源**
- [KiCad 10 Schematic Editor manual — Reference designators and annotation](https://docs.kicad.org/10.0/en/eeschema/eeschema.html) — KiCad, tool_doc, Annotation
- [KiCad 10 PCB Editor manual — Schematic parity checks](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, List of DRC checks
- [KiCad ERC Error Reference](https://pcbkit.com/tools/kicad-erc-reference/) — pcbkit, blog

<a id="GEN-SCH-013"></a>
#### GEN-SCH-013 · 可选件和调试件标记 DNP 并保证属性两边一致
`should` · 可信度 `high` · 适用: bom, variants · 标签: cat-feeder

**规则** 可选电路（预留的上下拉焊盘、0 欧姆跳线、调试接口、保护件）在原理图里照常画出并标 DNP，注明启用条件； BOM 导出必须区分 DNP 行；原理图符号的 DNP / 不进 BOM / 不进板属性与 PCB 封装的属性必须一致。

**依据** KiCad 的 DNP 元件封装仍会出现在板上，但不贴装；属性两边不一致会让贴片厂把不该贴的件贴上， 或漏贴必须的件。预留 0 欧姆比把 strapping 引脚硬接更便于后期调整。

**验证**
- `bom_check`（full）· kicad-cli sch export bom --fields Reference,Value,Footprint,${QUANTITY},${DNP} — DNP 行有明确的启用条件说明；贴装用的 BOM（--exclude-dnp）不含 DNP 行；设计 BOM 与贴装 BOM 的差集正好等于 DNP 清单。
- `netlist_diff`（full）· kicad-cli pcb drc --schematic-parity --severity-all — 不得出现 Footprint attributes don't match symbol（Value、DNP、Exclude from BOM 不一致，默认 Warning）。

**来源**
- [KiCad 10 Schematic Editor manual — DNP and BOM / Variants](https://docs.kicad.org/10.0/en/eeschema/eeschema.html) — KiCad, tool_doc, Symbol attributes: Do not populate, Exclude from BOM
- [KiCad Command-Line Interface — sch export bom](https://docs.kicad.org/8.0/en/cli/cli.html) — KiCad, tool_doc
- [Schematic Checklist - ESP32-C3（SPI 线串联 0 欧姆预留）](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, Flash
- [pcb-checklist: schematic checklist（用 0 欧姆代替硬接 strapping）](https://github.com/azonenberg/pcb-checklist/blob/master/schematic-checklist.md) — Andrew Zonenberg, blog

<a id="GEN-SCH-014"></a>
#### GEN-SCH-014 · 每个对外连接器线路都要有保护决策
`should` · 可信度 `medium` · 适用: connector, power_input, usb, uart · 标签: cat-feeder

**规则** 每个引出板外的连接器引脚都有一个明确的保护决策并画在原理图里：电源输入有保险丝 / PPTC、反接保护和 TVS；信号线有 ESD 二极管阵列。 TVS 的反向工作电压高于线路最大工作电压，钳位电压低于被保护 IC 的绝对最大值；预留不贴的保护焊盘也要画出来。

**依据** 连接器是 ESD 和浪涌的入口。保护器件在原理图里缺失，到布局阶段才补就没有合适位置； TVS 离连接器越近、对地电感越小，钳位效果越好。

**验证**
- `erc`（partial）· 自写脚本：kicad-cli sch export netlist — 对每个对外连接器的每个信号 / 电源引脚，网络上存在保护类元件（TVS、ESD 阵列、PPTC / 保险丝）或在白名单里有书面豁免。
- `emc_precompliance`（manual）· ESD 枪（IEC 61000-4-2 接触 / 空气放电） — 对每个对外连接器按产品要求的等级放电，板子不得损坏、不得复位或死机（按产品的判据等级）。

**来源分歧** 保险丝与 TVS 的先后顺序在各资料中并不统一（TVS 在保险丝之前能先泄放能量但可能烧保险丝；在之后则保护下游）。 这里不规定顺序，只要求存在保护决策；顺序与器件选型归 emc_esd 领域的规则。

**来源**
- [ESD Protection Layout Guide (SLVA680)](https://www.ti.com/lit/pdf/slva680) — Texas Instruments, app_note, TVS placement guidelines
- [pcb-checklist: schematic checklist（Power: fuse / reverse-protect + TVS）](https://github.com/azonenberg/pcb-checklist/blob/master/schematic-checklist.md) — Andrew Zonenberg, blog
- [Schematic Checklist - ESP32-C3（电源入口 ESD 二极管 + 10 uF）](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif, vendor_guide, Power Supply

<a id="GEN-SCH-016"></a>
#### GEN-SCH-016 · 关键位置标注容差、耐压和取值依据
`should` · 可信度 `medium` · 适用: feedback_divider, current_sense, filter, reference · 标签: cat-feeder

**规则** 决定精度或稳定性的元件（反馈分压、增益电阻、检流电阻、基准、滤波器 RC、LDO 电容）在原理图字段里写明容差、耐压或额定功率、电容介质， 极性元件标极性；在图上用注释记录取值依据（公式、仿真文件名、各轨最大电流和主要器件耗散）。

**依据** 容差是误差预算的输入，不写出来就无法复核；取值依据丢失后，后续改版没人知道哪个值能动。 TI 的最坏情况分析把初始容差、温漂与老化分开累加，说明标称值不是设计值。

| 参数 | 判据 | 备注 |
|---|---|---|
| `monte_carlo_runs` | 1000 … 100000 次 | TI SLYP673：蒙特卡洛分析的典型运行次数 |
| `x7r_tolerance_stack_example` | qualitative | TI SLYP673 示例：X7R 初始 10%、温度 15%、寿命末期 21%；EOL 值应取自厂商 |

**验证**
- `bom_check`（partial）· kicad-cli sch export bom 带 Tolerance、Voltage、Dielectric 字段 — 项目维护关键位号清单（反馈分压、检流、基准、滤波 RC、稳压器电容）；清单内元件的容差、耐压、介质字段必须非空，且容差不大于误差预算要求。
- `spice`（partial）· ngspice / LTspice（STEP + Monte Carlo） — 对该功能块做极值（EVA）或蒙特卡洛分析：用初始容差、温漂和老化范围，输出误差落在需求给定的范围内。

**来源**
- [Creating high quality electronics schematics](https://blog.poly.nomial.co.uk/2025-08-10-creating-high-quality-electronics-schematics.html) — Graham Sutherland, blog, Annotation of values, ratings, and limits
- [How to avoid design problems by using worst case analysis calculations (SLYP673)](https://www.ti.com/lit/pdf/slyp673) — Texas Instruments, app_note, Worst case analysis definition / method types / component tolerances
- [pcb-checklist: schematic checklist（Specify voltage, power, and tolerance ratings for passives；标记极性元件）](https://github.com/azonenberg/pcb-checklist/blob/master/schematic-checklist.md) — Andrew Zonenberg, blog

<a id="GEN-SCH-017"></a>
#### GEN-SCH-017 · I2C 上拉电阻按上升时间和灌电流计算
`should` · 可信度 `high` · 适用: i2c

**规则** I2C 上拉电阻满足 Rp(min) = (VCC - VOL(max)) / IOL 和 Rp(max) = tr / (0.8473 x Cb)，其中 tr 是所用速率模式的最大上升时间（30% 到 70%）， Cb 是总线电容；总线电容不得超出规范上限。在速度和功耗之间选值。

**依据** 上拉太强，器件下拉不到有效低电平；上拉太弱，RC 时间常数使线路在被拉低之前来不及升到高电平。

| 参数 | 判据 | 备注 |
|---|---|---|
| `i2c_rise_time_max_standard_mode` | <= 1000 ns | SLVA689A Table 2-1；Fast mode 300 ns，Fast mode plus 120 ns |
| `i2c_rise_time_max_fast_mode` | <= 300 ns | SLVA689A Table 2-1 |
| `i2c_bus_capacitance_max_standard_fast` | <= 400 pF | SLVA689A Table 2-1；Fast mode plus 为 550 pF |
| `i2c_vol_max` | <= 0.4 V | VCC > 2 V，灌 3 mA 时 |

**验证**
- `tline_calc`（full）· Python 计算脚本 — 输入 VCC、IOL、tr 上限、估算 Cb（元件引脚电容加走线电容）：计算 Rp(min) 和 Rp(max)，所选电阻必须落在区间内。 例：Cb = 200 pF、VCC = 3.3 V、Fast mode：Rp 在 0.97 到 1.77 kOhm 之间。
- `bench`（manual）· 示波器 — 测 SDA / SCL 的 30%-70% 上升时间 <= 所用模式的 tr 上限，低电平 <= VOL(max)。

**来源**
- [I2C Bus Pullup Resistor Calculation (SLVA689A)](https://www.ti.com/lit/pdf/slva689) — Texas Instruments, app_note, 2 Pullup Resistor Calculation, 4 Example

## 网表与约束（netlist）

<a id="GEN-NET-003"></a>
#### GEN-NET-003 · 差分对的两个网络同名并用一致的 _P/_N 后缀
`must` · 可信度 `high` · 适用: differential_pair, usb

**规则** 差分对的两个网络使用相同的基础名和一致的后缀对：_P / _N 或 + / -，不得混用（USB+ 配 USB_N 不构成一对）； 在原理图里命名，不在 PCB 里改。

**依据** KiCad 靠基础名加正负后缀识别差分对，识别不了就无法用差分对布线器，长度和间距规则也无法按对应用。

**验证**
- `erc`（full）· 自写脚本：网表中配对检查 — 每个以 _P 或 + 结尾的网络都存在同基础名、同风格的 _N 或 - 网络，反之亦然；同一设计里不出现两种后缀风格混用的配对。
- `drc`（partial）· 自定义规则 .kicad_dru 中的 inDiffPair() 条件 + kicad-cli pcb drc — 对差分对写间距 / 长度偏差规则后，DRC 能对该对给出结果（规则被命中），而不是被忽略。

**来源**
- [KiCad 10 PCB Editor manual — Routing differential pairs](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Routing differential pairs

<a id="GEN-NET-004"></a>
#### GEN-NET-004 · 网络只在原理图里改，PCB 变更要反向标注
`must` · 可信度 `high` · 适用: annotation, schematic_pcb_sync · 标签: cat-feeder

**规则** 连接关系只在原理图中修改，用「从原理图更新 PCB」传递；PCB 侧发生的变更（引脚交换、门交换、位号重排、封装更换） 必须用「从 PCB 更新原理图」同步回去并审阅预览，再重新做一次正向更新，直到两侧无差异。

**依据** 正向和反向标注是原理图与 PCB 保持一致的唯一通道；在 PCB 里手改网络会在下次正向更新时被覆盖或产生冲突。 更新默认按符号的唯一标识（UUID）而不是位号匹配，「按位号重新关联」选项通常应保持关闭。

**验证**
- `netlist_diff`（full）· kicad-cli pcb drc --schematic-parity --severity-all --exit-code-violations — 每次 PCB 变更之后，在更新原理图并完成正向更新后重新运行，退出码为 0（无任何严重级别的奇偶性差异）。
- `review`（manual）· KiCad 更新预览窗口（Changes To Be Applied） — 更新前逐项审阅预览：只有预期的位号、网络、字段变化；不勾选「按位号重新关联」，除非有明确原因。

**来源**
- [KiCad 10 PCB Editor manual — Update PCB from Schematic / Update Schematic from PCB](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Forward and back annotation
- [KiCad 10 PCB Editor manual — Pin and gate swapping](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Pin and gate swapping

<a id="GEN-NET-005"></a>
#### GEN-NET-005 · 原理图与 PCB 奇偶性检查要连警告一起设为门禁
`must` · 可信度 `high` · 适用: kicad, gate · 标签: cat-feeder

**规则** 签核门禁必须运行 kicad-cli pcb drc --schematic-parity --severity-all --exit-code-violations（退出码 0 才通过）； 不能只数 Error。重复 / 缺失 / 多余封装、焊盘网络不一致、属性不一致都必须为 0。

**依据** KiCad 把大多数奇偶性检查的默认严重级别设为 Warning（只有「元件间缺少连接」是 Error，封装过滤器检查默认被忽略）， 只看 Error 数的门禁会放过原理图与 PCB 不一致的板子。CLI 没加 --exit-code-violations 时，有违规也可能返回成功。

| 参数 | 判据 | 备注 |
|---|---|---|
| `kicad_cli_exit_code_no_violations` | == 0 退出码 | kicad-cli --exit-code-violations |
| `kicad_cli_exit_code_violations` | == 5 退出码 | 存在违规时的退出码 |

**验证**
- `netlist_diff`（full）· kicad-cli pcb drc --schematic-parity --severity-all --exit-code-violations --format json — 退出码为 0；JSON 报告中奇偶性类的违规数为 0（JSON 键名随 KiCad 版本核对）。固定 KiCad 主版本，因为不同版本的检查项和默认严重级别会变。

**来源**
- [KiCad 10 PCB Editor manual — List of DRC checks（Schematic parity 表）](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Design rules checking
- [KiCad Command-Line Interface — pcb drc](https://docs.kicad.org/8.0/en/cli/cli.html) — KiCad, tool_doc, pcb drc
- [How to run ERC in KiCad from the command line reliably](https://www.makeirl.com/blog/run-erc-kicad-command-line) — MakeIRL, blog

<a id="GEN-NET-001"></a>
#### GEN-NET-001 · 信号网络显式命名并统一命名风格
`should` · 可信度 `medium` · 适用: net_naming

**规则** 信号网络用描述用途的名字，全设计统一一套风格（大小写、分隔符、低有效后缀）；名字只含字母、数字和下划线； 凡是出现在多页、网络类、测试点或固件引脚映射里的网络必须显式命名，不得依赖 Net-(R1-Pad1) 之类的自动名。

**依据** 没有标签的网络，KiCad 用所连的符号引脚生成名字，连接的引脚一变名字就变，按名字匹配的网络类、测试点和固件引脚表会失效； 同一网络上有两个不同的标签时 KiCad 只保留其中一个并给出警告，容易被当成噪声忽略。

**验证**
- `erc`（full）· 自写脚本：kicad-cli sch export netlist --format kicadsexpr + kicad-cli sch erc — 正则检查所有网络名 ^[A-Za-z0-9_+\-/]+$；属于以下集合的网络名不得以 Net-( 开头：网络类模式匹配到的网络、含测试点的网络、 固件引脚映射中的网络。ERC 的 multiple_net_names 为 0。

**来源分歧** 低有效信号的写法在各资料中并不统一（_N / _B 后缀、前缀 /、前缀 n 等）。取舍：选定一种写进项目约定并全局一致，不强求某一种。

**来源**
- [KiCad 10 Schematic Editor manual — Net name assignment / Labels](https://docs.kicad.org/10.0/en/eeschema/eeschema.html) — KiCad, tool_doc
- [Creating high quality electronics schematics](https://blog.poly.nomial.co.uk/2025-08-10-creating-high-quality-electronics-schematics.html) — Graham Sutherland, blog, Net labels and naming
- [KiCad ERC Error Reference](https://pcbkit.com/tools/kicad-erc-reference/) — pcbkit, blog

<a id="GEN-NET-002"></a>
#### GEN-NET-002 · 网络类承载约束并保证每个网络都有归属
`should` · 可信度 `high` · 适用: netclass, constraints · 标签: cat-feeder

**规则** 在原理图 / 板级设置里定义网络类（至少 Default、大电流电源、差分对等），每个类写明线宽、间距、过孔尺寸、差分对宽度和间距； 按网络名模式或原理图网络类指令把每个网络分配到类；板级设置里的约束是不可被网络类突破的最小值。

**依据** 约束写在网络类里，布线与 DRC 才能自动执行，不靠人记；未分配的网络落入 Default，大电流网络落入 Default 就会按信号线宽布线。 网络类里的线宽 / 过孔是首选值而不是上下限，真正的下限在板级设置。

**验证**
- `erc`（full）· kicad-cli sch erc --severity-all — undefined_netclass（默认 Error）为 0。
- `drc`（partial）· 解析 .kicad_pro 的 net_settings + kicad-cli pcb drc — 脚本读出每个网络所属的类，对电源 / 电机大电流网络必须分配到大电流类（线宽满足载流计算）； DRC 在对应约束下无线宽 / 间距违规。

**来源**
- [KiCad 10 PCB Editor manual — Net Classes](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Net Classes
- [KiCad ERC Error Reference](https://pcbkit.com/tools/kicad-erc-reference/) — pcbkit, blog

<a id="GEN-NET-006"></a>
#### GEN-NET-006 · 出图前做网表差异对比并附 IPC-D-356
`should` · 可信度 `medium` · 适用: release, fabrication_package · 标签: cat-feeder

**规则** 出图前对比三份网表：原理图导出的网表、PCB 提取的网表、上一个已下单版本的网表，所有差异都要能对应到变更记录； 出图包里附 IPC-D-356 网表，让板厂能用它核对 Gerber 提取出的连接关系。

**依据** Gerber 只有几何，没有连接信息；板厂可以用客户给的网表对照自己从 Gerber 提取的网络，发现开路、短路和输出错误。 与上一版对比能把非预期改动（例如自动更新带来的）在下单前暴露出来。

**验证**
- `netlist_diff`（full）· kicad-cli sch export netlist + 解析 .kicad_pcb 的脚本 — 分别提取 (位号, 引脚号, 网络名) 三元组的集合，计算三组之间的差集；原理图 vs PCB 差集必须为空； 当前 vs 上一版的差集必须全部能在变更记录里找到对应条目。
- `review`（partial）· 出图包检查清单 — 出图目录含 IPC-D-356 文件；记录它由哪个版本的 EDA 生成；板厂是否使用它由板厂确认（本条未核实 JLCPCB 的做法）。

**来源**
- [Do You Need an IPC-D-356 Netlist?](https://resources.altium.com/p/do-you-need-ipc-d-356-netlist) — Altium, vendor_guide
- [KiCad Command-Line Interface — sch export netlist](https://docs.kicad.org/8.0/en/cli/cli.html) — KiCad, tool_doc, sch export netlist
- [KiCad 10 PCB Editor manual — Fabrication outputs（IPC-D-356 与其他制造输出）](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc

<a id="GEN-NET-007"></a>
#### GEN-NET-007 · 排查孤立标签、单引脚网络和意外短接
`should` · 可信度 `high` · 适用: netlist, labels

**规则** 除测试点和已登记的刻意情形外，每个网络至少连两个引脚；标签只出现一次的全局标签视为拼写错误嫌疑； 刻意短接两个网络要用 net tie，不要靠导线；DRC 中「元件间缺少连接」与「两网络被短接」必须为 0。

**依据** 标签拼错会产生没有任何其他引脚的孤立网络，对 ERC 来说「标签只有一个」默认还是被忽略的检查； DRC 只能发现铜皮上的缺失连接和短路，发现不了「根本没有被画进网络」的问题。

**验证**
- `erc`（full）· 自写脚本：网表中统计每个网络的引脚数 + kicad-cli sch erc — 引脚数为 1 的网络必须在白名单（测试点、预留）中；ERC 中 label_dangling（Error）、isolated_pin_label（KiCad 10 Warning）、global_label_dangling（KiCad 9 Warning）为 0，并启用 single_global_label。
- `drc`（full）· kicad-cli pcb drc --severity-all — Missing connection between items（默认 Error）与 Items shorting two nets（默认 Error）为 0；刻意短接处使用 net tie 并且不触发短路违规。

**来源**
- [KiCad ERC Error Reference](https://pcbkit.com/tools/kicad-erc-reference/) — pcbkit, blog
- [KiCad 10 PCB Editor manual — DRC checks（Items shorting two nets 建议用 net tie）](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, List of DRC checks

<a id="GEN-NET-008"></a>
#### GEN-NET-008 · 引脚 / 门交换只在功能等价的引脚间进行
`should` · 可信度 `high` · 适用: pin_swap, gate_swap, mcu

**规则** 引脚交换和门交换只用于功能完全等价的引脚（同一封装里完全相同的逻辑门；MCU 上在 IO MUX 与模拟功能表里都具备所需功能的普通 GPIO）， 不碰 strapping、专用模拟、USB、flash 占用脚；交换后必须同步回原理图，并同步更新固件引脚映射。

**依据** KiCad 的交换不检查电气等价性，由设计者负责；交换在 PCB 上立即生效，原理图要等「从 PCB 更新原理图」才改变， 忘了同步会让原理图、固件与板子三者不一致。

**验证**
- `netlist_diff`（partial）· kicad-cli pcb drc --schematic-parity + 固件引脚映射文件比对脚本 — 交换并更新原理图之后，奇偶性检查为 0；固件引脚映射（YAML / 头文件）与网表中 MCU 引脚的网络名逐项一致。
- `review`（manual）· 评审清单 — 对每次交换的引脚，在数据手册的引脚功能表里确认被交换的两个引脚都具备所需功能，且不在受限引脚清单里。

**来源**
- [KiCad 10 PCB Editor manual — Pin and gate swapping](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Pin and gate swapping
- [ESP32-C3 Series Datasheet v2.4](https://documentation.espressif.com/esp32-c3_datasheet_en.pdf) — Espressif, datasheet, 2.2 Pin Overview, Table 2-4 IO MUX Pin Functions, Table 2-6 Analog Functions

## 叠层与规则（stackup）

<a id="GEN-STK-005"></a>
#### GEN-STK-005 · 按板厂能力设板级约束，不贴着极限设计
`must` · 可信度 `high` · 适用: jlc, 2_layer · 标签: cat-feeder

**规则** 在 Board Setup 里把最小线宽 / 线距 / 过孔 / 环宽 / 铜到板边设成板厂可制造的值，并通用网络用高于最小值的推荐值；JLC 2 层 1 oz：线宽 / 线距 ≥ 0.10 / 0.10 mm，过孔孔径 ≥ 0.15 mm 且过孔外径 ≥ 0.25 mm，铜到铣边 ≥ 0.2 mm。

**依据** 低于板厂能力的设计会被拒收或加价；设计规则一旦与板厂能力对齐，DRC 才等于“可投板”的判据。

| 参数 | 判据 | 备注 |
|---|---|---|
| `min_track_width_1oz_2layer` | >= 0.1 mm | JLC 1-2 层 1 oz；4-6 层为 0.09 mm；2 oz 2 层为 0.16 mm |
| `min_clearance_1oz_2layer` | >= 0.1 mm | JLC 1-2 层 1 oz；2 oz 为 0.16 mm |
| `min_via_hole` | >= 0.15 mm | JLC 页面写明 0.1 mm 仅限板厚 ≤1 mm 且 ENIG/OSP；常规按 0.15 mm |
| `min_via_outer_diameter` | >= 0.25 mm | JLC；同上条件可 0.2 mm |
| `min_pth_annular_ring_2layer_1oz` | >= 0.18 mm | JLC 绝对最小；推荐 0.25 mm |
| `copper_to_routed_edge` | >= 0.2 mm | JLC 铣边；V-cut 边为 0.4 mm |

**验证**
- `drc`（full）· kicad-cli pcb drc --format json（项目 .kicad_pro 的 board_setup 约束） — 确认 .kicad_pro 中 min_track_width ≥ 0.10 mm、min_clearance ≥ 0.10 mm（2 层 1 oz）、min_via_diameter ≥ 0.25 mm、min_through_hole_diameter ≥ 0.15 mm、min_copper_edge_clearance ≥ 0.2 mm；DRC 0 error
- `review`（manual）· 板厂在线 DFM / 报价页 — 上传 Gerber 看板厂 DFM 报告无 trace / space / annular ring 违规

**来源**
- [JLCPCB PCB Manufacturing & Assembly Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide, 1-2 layer 与 multilayer 列
- [KiCad 9.0 PCB Editor — Board Setup constraints and DRC](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Board Setup > Constraints; Design for manufacturing DRC checks

<a id="GEN-STK-001"></a>
#### GEN-STK-001 · 按最高频率与辐射风险选层数，2 层板要补偿
`should` · 可信度 `medium` · 适用: mcu_board, 2_layer, 4_layer · 标签: cat-feeder

**规则** 板上有 ≥10~15 MHz 的时钟 / 快边沿、RF 或敏感模拟时优先 4 层（信号-地-电源-信号）；只有成本迫使用 2 层时，必须用整面地铺铜 / 地网格、电源与地并行走线来替代平面。

**依据** 完整平面给每条走线一个紧贴正下方的低电感回流路径并降低地阻抗；2 层板要靠布局手段（地网格、回流贴着信号线）才能逼近这个效果。

| 参数 | 判据 | 备注 |
|---|---|---|
| `multilayer_consider_above_clock` | >= 10 MHz | Ott：约 10~15 MHz 以上通常应考虑多层板；2 层板在 20~25 MHz、无屏蔽外壳下也有成功先例（属例外） |
| `four_vs_two_layer_radiation_reduction` | == 15 dB | Ott 经验值：其他条件相同，4 层板辐射比 2 层低约 15 dB（非实测数据） |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python)，参见 ee-pcb-verify 的 geometry 检查器 — 读 board.GetCopperLayerCount()；若为 2，统计底层 GND 铜覆盖率（填充区面积 / 板面积）与顶层信号线正下方底层有 GND 铜的线长占比；覆盖率 < 70% 或占比 < 90% 报警（70% / 90% 为经验阈值，需按板调整）
- `emc_precompliance`（manual）· 近场探头 + 频谱仪 / 示波器 — 2 层样板在主时钟及其谐波、电机 PWM 边沿处做近场扫描，与整改前对比；任何频点超过项目 EMC 目标限值（或余量不足 6 dB，6 dB 为经验余量）则考虑升 4 层

**来源分歧** TI SZZA009 §2.1.2 称 2 层板模仿 4 层板的做法（地在电源下方、电源地网格化、回流在信号线正下方、MCU 下方实心地）可达到 4 层板约 95% 的效果；Ott 则给出 4 层比 2 层低约 15 dB 的经验值并建议 10~15 MHz 以上用多层。两者不矛盾于方向，分歧在 2 层板的上限。取舍：默认 4 层；2 层板必须满足 TI 列出的四条补偿做法并过预兼容扫描。

**来源**
- [PCB Stack-Up, Part 1 (Henry Ott Consultants)](https://hott.shielddigitaldesign.com/techtips/pcb-stack-up-1.html) — Henry Ott Consultants, paper, two-layer vs. multi-layer
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.1.2 Two-Layer vs Four-Layer Boards
- [Hardware design with RP2040](https://pip.raspberrypi.com/documents/RP-008279-DS-hardware-design-with-rp2040.pdf) — Raspberry Pi, vendor_guide, §2 minimal design (2 layer) vs §3 VGA/SD/audio demo board (4 layer)

<a id="GEN-STK-002"></a>
#### GEN-STK-002 · 4 层板信号层贴近邻接平面，两平面间用厚芯板
`should` · 可信度 `high` · 适用: 4_layer

**规则** 4 层板（信号-GND-PWR-信号）里，外层信号到其邻接平面的介质厚度 < 0.254 mm（10 mil），中间两个平面之间的芯板 > 1.016 mm（40 mil）。

**依据** 信号与回流平面越近，回流环路面积越小、辐射越低（Ott 称 0.005 in 间距可比等间距叠层减少 10 dB 以上的环路辐射）；电源 / 地平面间距大时电容耦合弱，但换来信号-平面紧耦合，是 4 层板的折中。

| 参数 | 判据 | 备注 |
|---|---|---|
| `signal_to_plane_dielectric` | < 0.254 mm | Ott：<0.010 in |
| `plane_to_plane_core` | > 1.016 mm | Ott：>0.040 in。JLC04161H-7628：prepreg 0.2104 mm，芯板 1.065 mm，满足该判据 |

**验证**
- `geometry_script`（full）· pcbnew：board.GetDesignSettings().GetStackupDescriptor() 遍历介质层 — 取 F.Cu 与 In1.Cu 之间介质厚度 d1、B.Cu 与 In2.Cu 之间 d3、In1 与 In2 之间 d2；通过判据 d1 < 0.254 mm 且 d3 < 0.254 mm 且 d2 > 1.016 mm
- `tline_calc`（partial）· 2D 场求解器 / 阻抗计算器 — 用上述叠层计算 50 Ω 微带线宽度；确认在板厂可做的线宽范围内（JLC04161H-7628 外层到 L2 介质 0.2104 mm）

**来源分歧** TI SCAA082A 表 3 把 SIG-GND-PWR-SIG（其 Model 2）的 EMC 评为 Bad、去耦评为 Good，与 Ott 把它视为 4 层板的改进方案不同；Ott 的前提是外层贴近平面并拉大中间芯板。本条按 Ott；若需要更好 EMC，Ott 的 Fig. 3b（两外层为地、电源走线）是 4 层板能做到的最好方案，但元件焊盘会割裂外层地。

**来源**
- [PCB Stack-Up, Part 2 (Henry Ott Consultants)](https://hott.shielddigitaldesign.com/techtips/pcb-stack-up-2.html) — Henry Ott Consultants, paper, Fig. 2 four-layer stack-up
- [JLCPCB impedance control stackups (JLC04161H-7628)](https://jlcpcb.com/impedance) — JLCPCB, vendor_guide, 4-layer JLC04161H-7628

<a id="GEN-STK-003"></a>
#### GEN-STK-003 · 每个走线层邻接参考平面，高频线埋在两平面之间
`should` · 可信度 `high` · 适用: 4_layer, 6_layer

**规则** 凡布高频 / 开关信号的层，紧邻必须有完整的 GND（或 PWR）平面；6 层板避免 SIG-SIG-GND-PWR-SIG-SIG，优先 SIG-GND-SIG-SIG-PWR-SIG（Ott Fig. 6，最常见）或 GND-SIG-GND-PWR-SIG-GND（Ott Fig. 8，仅 2 个走线层）这类让高频层夹在平面之间的叠层。

**依据** 回流电流走阻抗最低的路径，也就是信号正下方 / 正上方的相邻平面；没有相邻平面的走线层回流只能绕远路，环路面积大。两平面夹住的埋层还能屏蔽辐射。

**验证**
- `geometry_script`（full）· pcbnew 读叠层 + 各层 zone 填充 — 遍历叠层，对每个含 ≥1 条走线的铜层，判断上或下相邻铜层是否为 GND / PWR 平面层；对 6 层板判断是否出现相邻两信号层且外侧无平面（SIG-SIG-PLANE-PLANE-SIG-SIG 模式）
- `review`（manual）· 叠层评审清单 — 对照 Ott 五条目标逐条打勾：①信号层邻平面 ②信号与平面紧耦合 ③电源地平面紧耦合 ④高速线埋层 ⑤多地平面；记录哪几条被牺牲

**来源分歧** TI SCAA082A 表 4 把 6 层 Model 1（SIG-SIG-VCC-GND-SIG-SIG）EMC 评为 Bad，与 Ott 的 Fig. 5 结论一致；对 3 号 / 4 号模型的评分与 Ott 的排序略有差异，但都支持“高频信号层夹在平面之间”。无冲突，仅评分细节不同。

**来源**
- [PCB Stack-Up, Part 1 (Henry Ott Consultants)](https://hott.shielddigitaldesign.com/techtips/pcb-stack-up-1.html) — Henry Ott Consultants, paper, five EMC objectives
- [PCB Stack-Up, Part 3 (Henry Ott Consultants)](https://hott.shielddigitaldesign.com/techtips/pcb-stack-up-3.html) — Henry Ott Consultants, paper, six-layer, Fig. 5 (avoid) and Fig. 6-8
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.2 Board Stackup, Table 4

<a id="GEN-STK-004"></a>
#### GEN-STK-004 · 2 层板：底层做地参考，元件只放顶层
`should` · 可信度 `high` · 适用: 2_layer, mcu_board · 标签: cat-feeder

**规则** 2 层 MCU 板把底层几乎整面留给 GND 铺铜，底层不放元件、尽量不走线；重要信号（时钟、高速 IO、射频）下方的底层必须是连续地，不被其他走线切断。

**依据** 2 层板没有内层平面，把底层当地平面是能提供“紧贴正下方的回流路径”的最接近做法；单面贴装也降低装配成本。

**验证**
- `geometry_script`（full）· pcbnew — 统计 B.Cu 上非 GND 网络的走线总长与焊盘数（应接近 0，仅允许少量必要跳线）；对每条顶层高速 / 时钟网络采样（每 1 mm 一点），检查该点正下方 B.Cu 是否落在 GND 填充区内，通过判据 ≥ 95% 的采样点在 GND 铜内（95% 为经验阈值）
- `drc`（full）· KiCad 自定义规则 .kicad_dru — (rule "no_bottom_parts" (layer B.Cu) (constraint disallow footprint)) 禁止底层元件；底层走线统计用 geometry_script

**来源**
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, General Principles of PCB Layout for the Chip: Two-layer
- [Hardware design with RP2040](https://pip.raspberrypi.com/documents/RP-008279-DS-hardware-design-with-rp2040.pdf) — Raspberry Pi, vendor_guide, §2 Minimal design example; §2.4.1 USB
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.1.2, §2.2.3

<a id="GEN-STK-006"></a>
#### GEN-STK-006 · 网络类宽度只是默认值，必须用自定义规则落成 DRC
`should` · 可信度 `high` · 适用: kicad · 标签: cat-feeder

**规则** 为 Power / Signal / Clock 等网络类定义线宽、间距、过孔尺寸后，再用 .kicad_dru 里的 track_width / clearance / via_diameter 约束把它们变成可检查的下限；否则手动改线宽不会触发 DRC。

**依据** KiCad 的网络类线宽只是布线器默认值；文档明确说除非用自定义规则设最小 / 最大值，否则不会报告违规。

**验证**
- `drc`（full）· KiCad 自定义规则 .kicad_dru + kicad-cli pcb drc — 加入 (version 1) (rule power_width (layer outer) (condition "A.hasNetclass('Power')") (constraint track_width (min 0.5mm))) 与 (rule power_via (condition "A.hasNetclass('Power') && A.Type == 'Via'") (constraint via_diameter (min 0.6mm)))；DRC 0 error。数值按 GEN-STK-007 的电流计算替换

**来源**
- [KiCad 9.0 PCB Editor — Custom design rules; Track width violation](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Advanced topics > Custom design rules; DRC > Track width

<a id="GEN-STK-007"></a>
#### GEN-STK-007 · 按电流和温升算线宽，IPC-2221 作保守下限
`should` · 可信度 `medium` · 适用: power_nets, motor_driver · 标签: cat-feeder

**规则** 载流线宽用 IPC-2221 公式 I = k·ΔT^0.44·A^0.725 估算（A 单位 mil²，外层 k=0.048，内层 k=0.024），ΔT 取 10 °C；有明确叠层且走线邻近铜平面时可用 IPC-2152 放宽，但同一块板不要混用两套标准。

**依据** 线宽太窄会过热、压降大；IPC-2221 图表来自 1950 年代的有限数据，偏保守，IPC-2152（2009）用较新的测试并引入平面等修正，但各二手资料对其外 / 内层结论不一致。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ipc2221_k_external` | == 0.048 - | I = k·ΔT^0.44·A^0.725，A 为 mil² |
| `ipc2221_k_internal` | == 0.024 - | 同上；内层 k 减半，同电流下所需截面积约为外层的 2.6 倍（因 0.725 指数） |
| `design_temp_rise` | <= 10 degC | 常用基线；semiconductor.tools：10 °C 最常见、高可靠 5 °C 更好、非关键应用 20 °C 可接受（并非上限）；Wevolver 称 10 °C→20 °C 约可减窄 25~30%（二手数字，其自身示例 110→70 mil 约 36%，前后不一致，仅供参考） |

**验证**
- `tline_calc`（full）· Python 按公式计算（1 oz = 1.378 mil 厚） — 对每条载流网络取峰值 / RMS 电流 I，反解 A=(I/(k·ΔT^0.44))^(1/0.725)，宽度=A/铜厚；板上该网络最窄处宽度 ≥ 计算值。例（本调研按公式算出）：1 oz 外层 ΔT=10 °C：1 A→0.30 mm，3 A→1.37 mm，5 A→2.77 mm；同条件内层 k=0.024：1 A→0.78 mm，3 A→3.56 mm
- `geometry_script`（full）· pcbnew：遍历 PCB_TRACK，按网络取 GetWidth() 最小值；铜皮用 zone 填充最窄颈宽 — 对每个电源 / 电机网络，最窄走线宽度 ≥ 上一条算出的宽度；过窄处报警
- `bench`（manual）· 热电偶或热像仪 + 可调电流源 — 对最窄的载流段通额定峰值电流（稳态）10 分钟，测相对环境温升，通过判据 ≤ 设计 ΔT（10 °C）；同时四线法测压降

**来源分歧** 二手资料对 IPC-2221 与 IPC-2152 的差异说法不一：Sierra Circuits、semiconductor.tools 等称 IPC-2221 整体偏保守、内层尤甚（内层 k 减半），IPC-2152 显示内外层相差不大；AtlasPCB 却称 IPC-2221 对外层偏保守、对内层常不保守，IPC-2152 对外层允许更大电流、对内层更小。另有博客给出的 IPC-2221 示例宽度（3 A 外层 46 mil）与按公式实算的 54 mil 不符。取舍：公式常数以 Sierra 页面为准并已自行验算；设计时 IPC-2221 当保守下限，只有叠层已知且邻近平面时才用 IPC-2152 缩窄，并用热测量验证。没有读到 IPC 标准原文，故置信度 medium。

**来源**
- [Optimize your PCB trace using IPC-2152 standard](https://www.protoexpress.com/blog/how-to-optimize-your-pcb-trace-using-ipc-2152-standard/) — Sierra Circuits, blog
- [IPC-2221 vs IPC-2152: Which PCB Trace Standard Should You Use?](https://semiconductor.tools/blogs/07-ipc-2221-vs-ipc-2152) — semiconductor.tools, blog
- [PCB Trace Width and Current Capacity](https://www.atlaspcb.com/blog/pcb-trace-width-current-capacity/) — AtlasPCB, blog
- IPC-2221B 与 IPC-2152（IPC-2221B §6（导体载流图表）；IPC-2152（2009）） — standard

<a id="GEN-STK-008"></a>
#### GEN-STK-008 · 载流层间过孔至少两个，并按孔壁截面估算电流
`should` · 可信度 `medium` · 适用: power_nets, motor_driver · 标签: cat-feeder

**规则** 电源 / 地 / 电机电流跨层时至少打 2 个过孔并联；单个过孔载流按孔壁铜截面（π·(D+t)·t）代入 IPC-2221 估算，并留余量，大电流网络用过孔阵列。

**依据** 过孔桶壁铜很薄（常见 25 µm），单个过孔的载流和电感都有限；并联过孔降低电阻与电感，也避免单点失效。

| 参数 | 判据 | 备注 |
|---|---|---|
| `min_parallel_vias_power_transition` | >= 2 count | Espressif：主电源走线跨层至少两个过孔 |

**验证**
- `geometry_script`（partial）· pcbnew：遍历电源 / 地网络的 PCB_VIA，按“连接同一对铜区域的过孔数”分组 — 每个电源 / 地 / 电机网络的每个跨层连接点，并联过孔数 ≥ 2；大电流网络用 I / I_via_max 向上取整得到所需数量，I_via_max 取 0.5 A / 过孔的保守值（见 conflicts：Wevolver 约 0.5 A，AtlasPCB 0.3 mm 孔约 1.2 A）
- `drc`（partial）· KiCad 自定义规则 via_count — (rule min_two_vias (condition "A.hasNetclass('Power')") (constraint via_count (min 2))) —— 注意 via_count 统计的是整网过孔总数，只能粗筛；逐连接点检查用 geometry_script
- `bench`（manual）· 毫欧表 / 四线法 + 热像仪 — 对最大电流路径通额定电流测过孔段压降与温升，温升 ≤ 设计 ΔT

**来源分歧** 单个过孔的载流数字各来源差异大：Wevolver 称“典型过孔约 0.5 A”、5 A 网络要 5~10 个过孔，AtlasPCB 按 0.3 mm 孔、25 µm 镀铜的桶壁截面估算给 ≈1.2 A（10 °C 温升）；按 IPC-2221 常数自行算同一过孔桶壁截面（≈39.6 mil²）：外层 k 得 ≈1.9 A，内层 k 得 ≈0.95 A。取舍：没有标准原文，不把任何单一数字写进 parameters；设计取 ≤0.5 A / 过孔的保守值并用热测量验证，且最少 2 个。

**来源**
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, Power Supply（四层板：主电源跨层至少两个过孔）
- [Trace Width vs Current in PCB Design](https://www.wevolver.com/article/trace-width-vs-current-in-pcb-design) — Wevolver, blog, via current capacity
- [PCB Trace Width and Current Capacity](https://www.atlaspcb.com/blog/pcb-trace-width-current-capacity/) — AtlasPCB, blog, via current estimate from barrel area

## 分区规划（floorplan）

<a id="GEN-FLR-007"></a>
#### GEN-FLR-007 · 板框闭合，铜到板边满足板厂最小间距
`must` · 可信度 `high` · 适用: jlc · 标签: cat-feeder

**规则** Edge.Cuts 板框必须是闭合不自交的轮廓；铜（线、焊盘、铺铜）到铣边 ≥ 0.2 mm、到 V-cut 边 ≥ 0.4 mm（JLC）。

**依据** 板框不闭合板厂无法加工；铜离板边太近会被铣刀切到而短路或露铜。

| 参数 | 判据 | 备注 |
|---|---|---|
| `copper_to_routed_edge` | >= 0.2 mm | JLC 铣边 |
| `copper_to_vcut_edge` | >= 0.4 mm | JLC V-cut |

**验证**
- `drc`（full）· kicad-cli pcb drc --format json — 项目设 min_copper_edge_clearance=0.2 mm（V-cut 板 0.4 mm）；DRC 里“Board has malformed outline”和“Board edge clearance violation”必须为 0；自定义规则 (rule edge_all (constraint edge_clearance (min 0.3mm))) 可给余量
- `geometry_script`（full）· pcbnew — 对 Edge.Cuts 取闭合多边形，计算所有铜对象（线、焊盘、铺铜填充）到其最小距离，通过判据 ≥ 0.2 mm

**来源**
- [JLCPCB PCB Manufacturing & Assembly Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide
- [KiCad 9.0 PCB Editor — Design for manufacturing DRC checks](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Board edge clearance violation; Board has malformed outline

<a id="GEN-FLR-001"></a>
#### GEN-FLR-001 · 按功能和噪声等级分区，快逻辑靠近电源、模拟最远
`should` · 可信度 `high` · 适用: mcu_board, mixed_signal · 标签: cat-feeder

**规则** 布局前先画功能分区图（电源入口、稳压、数字 / MCU、慢速 IO、模拟、RF、连接器），同一功能的器件及走线放在一起；高速逻辑靠近电源，慢速器件更远，模拟器件最远。

**依据** 噪声源靠近供电点可缩短高频电流环路，同时给敏感电路留出隔离距离；分区后各子系统的走线不需要穿过彼此的区域，也就不需要分割地平面。

**验证**
- `review`（manual）· 分区图评审清单 — 检查：每个功能块有明确矩形区域；MCU / 时钟在靠近稳压器一侧；模拟前端、称重 / 采样输入远离电机驱动与开关节点；分区图随 PCB 评审一起存档
- `geometry_script`（partial）· pcbnew：按元件 sheet / 组分类取质心 — 给每个功能块定义元件集合，计算块间质心距离与块外包矩形重叠；通过判据：任意两个块的外包矩形重叠面积 = 0，且噪声块（电机驱动、稳压器）与敏感块（采样输入、晶振）的最小间距 ≥ 设计设定值（项目自定，例如 10 mm）

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.3 Board Zoning
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2 Practical PCB Design Rules（功能框图）
- [Partitioning and Layout of a Mixed-Signal PCB (H. Ott)](https://www.edn.com/partitioning-and-layout-of-a-mixed-signal-pcb-3/) — EDN / Printed Circuit Design, paper

<a id="GEN-FLR-002"></a>
#### GEN-FLR-002 · 电源入口、稳压器、MCU 依次相邻，地在三者间单点汇合
`should` · 可信度 `medium` · 适用: mcu_board, ldo · 标签: cat-feeder

**规则** 把 MCU 放在稳压器旁边、稳压器放在电源入口旁边，三者之间用实心（或网格化）地连成一个单点地参考，外壳 / 屏蔽也接在这一点。

**依据** 电源路径越短、越像单点连接，共阻抗耦合越小；MCU 的高频电流应当来自它身边的去耦电容，而不是长长的电源线。

**验证**
- `geometry_script`（partial）· pcbnew，参见 ee-pcb-verify 的 geometry 检查器 — 计算 电源入口连接器焊盘→稳压器输入电容→稳压器→MCU 供电引脚 的走线总长与折线长度，通过判据：稳压器到 MCU 的直线距离不超过板对角线的 1/3（经验阈值，按板调整），且这条路径上无其他功能块的元件插入
- `bench`（manual）· 示波器（20 MHz 带宽限制关闭，短地弹簧） — 在 MCU 供电引脚处测 VDD 纹波与 IO 翻转时的瞬态跌落，通过判据：跌落 < 芯片数据手册允许的 VDD 容差的一半

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.3 Board Zoning; §2.2.1 Single-Point vs Multipoint Distribution

<a id="GEN-FLR-003"></a>
#### GEN-FLR-003 · 各子系统的走线只在自己的分区内，跨区只走指定通道
`should` · 可信度 `high` · 适用: mixed_signal · 标签: cat-feeder

**规则** 模拟信号只在模拟区、数字信号只在数字区布线（所有层）；确需跨区的信号（如 ADC 的数字接口）走预先指定的一条通道，ADC / 带 ADC 的器件跨在分区边界上。

**依据** 分区的目的是让数字回流电流不进入模拟区。只要有一条数字线布进模拟区，下方的回流路径就会穿过模拟区，破坏分区。

**验证**
- `geometry_script`（full）· pcbnew：按网络类 / 网络名分类 — 为每个分区定义矩形；对每条网络类为 Analog 的走线与过孔，检查是否落在数字区矩形内，对 Digital 网络反之；通过判据：违规线段数 = 0（指定通道内的跨区信号列入白名单）
- `drc`（full）· KiCad 规则区域 + 自定义规则 — 在数字区画规则区域 'dig_zone'，加 (rule no_analog_in_digital (condition "A.intersectsArea('dig_zone') && A.hasNetclass('Analog')") (constraint disallow track via))，反向再建一条 'ana_zone' 规则

**来源**
- [Partitioning and Layout of a Mixed-Signal PCB (H. Ott)](https://www.edn.com/partitioning-and-layout-of-a-mixed-signal-pcb-3/) — EDN / Printed Circuit Design, paper
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.3, Figure 9

<a id="GEN-FLR-004"></a>
#### GEN-FLR-004 · 大电流路径和开关环路远离敏感小信号
`should` · 可信度 `medium` · 适用: motor_driver, mixed_signal · 标签: cat-feeder

**规则** 电机驱动 / MOSFET、分流电阻回路等大电流和快边沿路径及其地回流，布在与称重 / 采样输入、复位、晶振分开的区域；大功率地与数字 / 模拟地只在单点汇合。

**依据** 数字地和大功率地承载需要被限制的射频电流，且高 di/dt 会通过公共地阻抗耦合进敏感电路；不相关的低噪声线靠近继电器 / 电机驱动器等会拾取噪声。

**验证**
- `geometry_script`（partial）· pcbnew — 取大电流网络（网络类 Power / Motor）的所有走线与焊盘，对敏感网络（采样输入、晶振、复位、EN）的每条走线计算两者最小间距，通过判据 ≥ 项目设定值（建议 ≥ 5 mm，经验阈值）；同时检查电机回流电流路径是否经过模拟区
- `bench`（manual）· 示波器 + 称重 / 采样通道静态读数 — 电机 PWM 运行与停转两种状态下，记录采样通道读数的噪声（峰峰值 / 标准差）；通过判据：运行时噪声增量 < 采样分辨率的 1 LSB RMS 或项目指定值

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.1.5 Analog vs Digital vs High Power; §2.4.1 Capacitive and Inductive Crosstalk
- [Grounding Analog-Digital Converters (J. Bryant, ADI lecture, mirror)](http://www.hit.bme.hu/~papay/edu/Acrobat/GndADCs.pdf) — Analog Devices, app_note

<a id="GEN-FLR-005"></a>
#### GEN-FLR-005 · 连接器集中在板边，噪声源与晶振远离连接器
`should` · 可信度 `medium` · 适用: mcu_board · 标签: cat-feeder

**规则** 外部连接器（电源、电机、传感器、调试口）成组放在板边同一区域，I/O 的滤波 / ESD 器件放在连接器附近；晶振回路、开关器件、时钟线远离连接器和电缆走向，不设计会折叠到振荡器 / MCU 上方的线缆。

**依据** 电缆是主要辐射体和注入通道；噪声线靠近连接器会被耦合到电缆上，外部电缆干扰也更容易进入时钟、复位。

**验证**
- `geometry_script`（partial）· pcbnew — 取所有连接器 footprint 的外包框到最近板边距离（应 ≤ 5 mm，经验阈值）与连接器所在边集合（≤ 2 条边）；取晶振 / 时钟网络走线到最近连接器焊盘的距离，通过判据 ≥ 项目设定值（建议 ≥ 15 mm）
- `emc_precompliance`（manual）· 电流探头 / 近场探头 — 连接电缆后，用共模电流探头测电缆上的共模电流谱，对比拔掉电缆的基线

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.3 Board Zoning; §2.4.1; §2.5 Cables and Connectors
- [7 PCB Design Guidelines for EMI and EMC](https://www.protoexpress.com/blog/7-pcb-design-tips-solve-emi-emc-issues/) — Sierra Circuits, blog, connectors and I/O

<a id="GEN-FLR-006"></a>
#### GEN-FLR-006 · 带板载天线的模块放在板边，天线区空出
`should` · 可信度 `high` · 适用: wifi_module, esp32 · 标签: cat-feeder

**规则** 带 PCB 天线的 Wi-Fi / BLE 模块把天线端放在板边外侧或贴边，馈点尽量靠近板边；天线下方和周围所有层不放铜与器件，不要让模块四周都被挖空；外壳内天线周围各方向至少留 15 mm。

**依据** 天线周围的铜和器件会失谐并降低增益；贴边放置是让天线辐射区远离主板铜的最简单办法。

| 参数 | 判据 | 备注 |
|---|---|---|
| `antenna_clearance_in_housing` | >= 15 mm | Espressif：外壳内天线周围各方向 |

**验证**
- `geometry_script`（partial）· pcbnew，参见 ee-pcb-verify 的 geometry 检查器 的天线区检查 — 取模块 footprint 天线端的外包框，通过判据：天线禁布区内（所有铜层）元件数 = 0，且天线端到最近板边距离 ≤ 馈点到板边距离的 +2 mm（+2 mm 为经验阈值，Espressif 未给数值）；板边外侧悬出时检查机械可行性
- `bench`（manual）· 路由器 / 手机 RSSI 或吞吐量测试 — 在最终外壳里测同一距离、同一环境下的 RSSI 与吞吐量，对比模块官方开发板；通过判据：RSSI 差 ≤ 3 dB

**来源分歧** “RSSI 差 ≤ 3 dB” 是本条验证的经验通过判据，不是 Espressif 数值；RF 领域细节由 RF 文件负责。

**来源**
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, General Principles of PCB Layout for Modules

<a id="GEN-FLR-008"></a>
#### GEN-FLR-008 · 安装孔预先定位，孔径和孔距满足板厂，并留地回流接点
`consider` · 可信度 `medium` · 适用: mcu_board, jlc · 标签: cat-feeder

**规则** 在布局初期定好安装孔位置；非镀铜孔（NPTH）孔径 ≥ 0.5 mm，孔与孔边到边 ≥ 0.45 mm；靠近 I/O 连接器的安装孔需要做机壳地回流时用镀铜孔接 GND，并尽量靠近连接器外壳地和 ESD 器件地。

**依据** 机壳螺钉紧邻 TVS 地和连接器屏蔽地，是为 ESD 电流提供低阻抗回流的做法；孔位晚定会反过来推翻布局。

| 参数 | 判据 | 备注 |
|---|---|---|
| `min_npth_hole` | >= 0.5 mm | JLC 最小 NPTH 孔 |
| `min_hole_to_hole` | >= 0.45 mm | JLC 焊盘孔到孔最小间距 |

**验证**
- `drc`（full）· kicad-cli pcb drc；自定义规则 — (rule mount_hole_size (condition "A.Type == 'Pad' && A.Pad_Type == 'NPTH, mechanical'") (constraint hole_size (min 0.5mm))) 与 (rule hole2hole (constraint hole_to_hole (min 0.45mm)))；DRC 0 error
- `review`（manual）· 机械装配核对 — 与外壳 3D / 图纸叠合，检查螺钉头、塑料柱与元件、走线的干涉；螺钉头禁布半径按实际螺钉定，不在本库给数值

**来源**
- [JLCPCB PCB Manufacturing & Assembly Capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide
- [ESD Protection Layout Guide (SLVA680A)](https://www.ti.com/lit/an/slva680/slva680.pdf) — Texas Instruments, app_note, §1, §2.4

## 器件布局（placement）

<a id="GEN-PLC-002"></a>
#### GEN-PLC-002 · 每个电源引脚一个去耦电容，小容值最近
`should` · 可信度 `high` · 适用: mcu, qfn, module · 标签: cat-feeder

**规则** 每个 IC 电源引脚配一个 100 nF 去耦电容（共用引脚的情况可例外），把容值最小的电容放在最靠近该引脚的位置；电容与引脚之间的走线长宽比 ≤ 3:1。

**依据** 去耦电容要在时钟沿提供瞬时电流，回路电感越小越有效；小容值电容自谐振频率高但对走线电感最敏感，必须最近。ADI 的 ADC 讲义甚至给出某款 ADC 去耦电容必须在 2.5 mm 以内否则丢码的实例。

| 参数 | 判据 | 备注 |
|---|---|---|
| `decap_per_power_pin` | == 1 count | RP2040 指南：每个电源引脚 100 nF，个别空间受限引脚可共用 |
| `decap_loop_trace_length_to_width` | <= 3 ratio | TI SZZA009：旁路回路中的走线长宽比 |
| `decap_value_nearest_pin` | minimize nF | TI SCAA082A：容值最小的电容离引脚最近 |

**验证**
- `geometry_script`（full）· pcbnew，参见 ee-pcb-verify 的 geometry 检查器 — 对每个 IC 的每个电源引脚，找同网络、值为 100 nF（或最小容值）的电容，量引脚焊盘中心到电容电源焊盘中心的距离 d，及两者间走线的长度 / 宽度比；通过判据：d ≤ 项目设定值（建议 ≤ 3 mm，经验阈值，按封装调整）且长宽比 ≤ 3；每个电源引脚都存在这样的电容，共用的需在 note 登记
- `spice`（partial）· ngspice：PDN 简化模型 — 用 ESL（含走线电感）扫描去耦电容到引脚的电感（0.5 / 1 / 2 / 4 nH），看 100 MHz 处 PDN 阻抗 vs 目标阻抗，确认目标距离下仍满足
- `bench`（manual）· 示波器（带宽 ≥ 200 MHz，短地弹簧） — 在 MCU 电源引脚旁测 IO 全速翻转时的 VDD 跌落 / 尖峰，通过判据：尖峰峰峰值 < 芯片 VDD 容差的 1/2 或项目设定值

**来源**
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.4 Decoupling Capacitors
- [Hardware design with RP2040](https://pip.raspberrypi.com/documents/RP-008279-DS-hardware-design-with-rp2040.pdf) — Raspberry Pi, vendor_guide, §2.1.2 Decoupling capacitors
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.2.4 Bypassing and Ferrite Beads
- [Grounding Analog-Digital Converters (J. Bryant, ADI lecture, mirror)](http://www.hit.bme.hu/~papay/edu/Acrobat/GndADCs.pdf) — Analog Devices, app_note, SUPPLY DECOUPLING

<a id="GEN-PLC-003"></a>
#### GEN-PLC-003 · 去耦电容地焊盘就近接地，用过孔或直连地铜
`should` · 可信度 `high` · 适用: 2_layer, 4_layer · 标签: cat-feeder

**规则** 去耦电容的地焊盘直接连到地平面 / 地铺铜——通过紧贴焊盘的过孔（多层板可用 2~3 个），或在离 IC 地引脚足够近时直接连到地引脚；不通过一段细线再去找地。

**依据** 电容的接地端电感和电源端一样重要；一段细线会把电容的有效频带拉低。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ground_vias_per_decap` | 1 … 3 count | TI 对多层板写“2~3 个过孔”；2 层 0402 空间不足时 1 个紧贴焊盘的过孔或直连地铜 |

**验证**
- `geometry_script`（full）· pcbnew — 对每个去耦电容的 GND 焊盘，找最近的 GND 过孔或 GND 铺铜连接，量焊盘边缘到过孔边缘距离和连接线长；通过判据：连接线长 ≤ 焊盘宽度的 1 倍（经验阈值）或焊盘与 GND 铜直连（thermal relief 的辐条数 ≥ 2，见 GEN-PLN-008）
- `drc`（partial）· KiCad 自定义规则 — (rule decap_gnd_direct (condition "A.Type == 'Pad' && A.Reference == 'C*' && A.NetName == 'GND'") (constraint connection_width (min 0.3mm))) —— 检查与地铜连接足够宽；距离判据用 geometry_script

**来源**
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.4 Decoupling Capacitors
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, Power Supply（去耦电容地焊盘旁要有接地过孔）

<a id="GEN-PLC-004"></a>
#### GEN-PLC-004 · 电源电流必须穿过去耦电容焊盘再到引脚
`should` · 可信度 `medium` · 适用: mcu, qfn · 标签: cat-feeder

**规则** 电源走线先到电容的电源焊盘、再从该焊盘出到 IC 引脚，不允许从电源线上 T 形分支出一条带电容的短桩；电容与引脚之间不加过孔。

**依据** 电容挂在分支末端时，高频电流仍可经主电源线流向引脚，电容起不到应有的旁路作用，分支也增加回路面积。

**验证**
- `geometry_script`（partial）· pcbnew：按网络建铜连通图 — 对每个去耦电容的电源焊盘和对应 IC 电源引脚，检查电源网络从稳压器 / 入口到该引脚的最短铜路径是否经过该电容焊盘（或与电容焊盘距离 ≤ 焊盘宽度）；该电容与引脚之间的连接中过孔数应为 0；违规则报告
- `review`（manual）· 布局评审 — 对照 SCAA082A 图 12（Poor / Good Bypassing）逐个电源引脚检查

**来源**
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.4 Decoupling Capacitors, Figure 12

<a id="GEN-PLC-005"></a>
#### GEN-PLC-005 · 电源入口和稳压器处放大电容，模块进线前放 10 µF
`should` · 可信度 `medium` · 适用: mcu_board, ldo · 标签: cat-feeder

**规则** 外部电源进入板子的连接器引脚旁放大容量电容（含一个 10 µF 级电容并联 100 nF）；稳压器输入输出各放其数据手册要求的电容；电源走线进入 MCU / 模块前再放一个 10 µF；入口离模块电源脚较远时，两处都要放 10 µF。

**依据** 大电容吸收电缆上的瞬变和负载阶跃，防止电源线上的电流瞬变沿线传导；入口与芯片之间走线的电感使远端的小电容不足以应付芯片的瞬时需求。

| 参数 | 判据 | 备注 |
|---|---|---|
| `entry_bulk_capacitor` | >= 10 uF | Espressif：芯片电源入口前 10 µF，可并联 0.1 或 1 µF |

**验证**
- `geometry_script`（full）· pcbnew — 取电源入口连接器电源焊盘，找同网络最近的 ≥ 10 µF 电容，量焊盘间距离，通过判据 ≤ 项目设定值（建议 ≤ 10 mm，经验阈值）；对模块 / MCU 的电源引脚同样检查是否有 10 µF 在其入口
- `bench`（manual）· 示波器 + 电子负载 / 电机启动 — 在电机堵转 / 启动或 Wi-Fi 发射峰值时测 3V3 与 VIN 的最低值，通过判据：3V3 最低值 ≥ MCU / 模块数据手册规定的最低供电电压 + 余量

**来源**
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, Power Supply: 10 µF before the power trace enters the chip
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.2.4; §2.3 Board Zoning

<a id="GEN-PLC-006"></a>
#### GEN-PLC-006 · 晶振贴近 MCU，走线短且对称，周围有地环
`should` · 可信度 `high` · 适用: crystal, mcu

**规则** 晶振和负载电容尽量贴近 MCU 的 OSC 引脚，两条走线短而对称（两个负载电容相对称），晶振及其走线周围用接地保护环（guard ring）包围；金属壳晶振外壳不接振荡器地。

**依据** 长走线既是天线又增加杂散电容，影响起振与频率稳定；保护环减少外来噪声耦合；这是 EMC 测试里常见的失败点。

**验证**
- `geometry_script`（full）· pcbnew — 取 OSC_IN / OSC_OUT 两条网络的走线长度 L1、L2 与过孔数；通过判据：L1、L2 ≤ 项目设定值（建议 ≤ 10 mm，经验阈值）且 |L1−L2| ≤ 20%（经验阈值），过孔数 = 0；检查 CL1 / CL2 到晶振的距离对称
- `bench`（manual）· 示波器 + 低电容探头（10 MΩ / <1 pF）或频率计 — 测上电到振荡稳定的启动时间与输出频率偏差，通过判据：启动时间 ≤ 数据手册典型值，频率偏差在晶振 ppm 容差内；探头不要直接挂振荡引脚，用时钟输出引脚代替

**来源分歧** 本板用 ESP32-C3 模块，晶振在模块内，板上没有 OSC 走线；本条为板上有分立晶振时的基线。ST 的“保护环”与 Espressif 的“时钟走线周围密地过孔 / 地铜”是同一思路。另：Espressif Crystal 节写有“crystal should be placed far from the clock pin … gap at least 2.0 mm”（原文未说明 clock pin 具体指哪个引脚），与 ST 的“as close as possible to the microcontroller”看似相反；本条按 ST 取贴近，不引入 2.0 mm 数值，板上有分立晶振时按所用芯片的指南核对。

**来源**
- [AN2867 Oscillator design guide for STM8AF/AL/S, STM32 MCUs and MPUs](https://www.st.com/resource/en/application_note/an2867-guidelines-for-oscillator-design-on-stm8afals-and-stm32-mcusmpus-stmicroelectronics.pdf) — STMicroelectronics, app_note, §7.1 PCB design guidelines（读的是 Rev 13；该节针对 32 kHz 振荡器，同样适用于一般晶振）
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, Crystal
- [Hardware design with RP2040](https://pip.raspberrypi.com/documents/RP-008279-DS-hardware-design-with-rp2040.pdf) — Raspberry Pi, vendor_guide, §2.3 Crystal oscillator

<a id="GEN-PLC-009"></a>
#### GEN-PLC-009 · ESD / TVS 器件紧靠连接器，保护对象放得更远
`should` · 可信度 `high` · 适用: connector, tvs, esd · 标签: cat-feeder

**规则** TVS / ESD 阵列放在设计规则允许的最靠近连接器处，被保护的 IC 离 TVS 比 TVS 离连接器远得多；信号线先到 TVS 保护引脚、再去 IC。

**依据** ESD 电流 di/dt 极大（8 kV 接触放电约 30 A / 0.8 ns），每 0.25 nH 电感就多出约 10 V；让连接器到 TVS 的电感远小于 TVS 到 IC 的电感，电流自然被引向 TVS，也把辐射限制在连接器附近。

| 参数 | 判据 | 备注 |
|---|---|---|
| `tvs_to_connector_distance` | minimize mm | SLVA680A：尽可能近；0.25 nH 约 10 V（8 kV IEC 61000-4-2：30 A / 0.8 ns） |

**验证**
- `geometry_script`（full）· pcbnew — 对每个被 TVS 保护的连接器信号，量 d1 = 连接器焊盘到 TVS 信号焊盘距离，d2 = TVS 信号焊盘到被保护 IC 引脚距离；通过判据：d1 ≤ 项目设定值（建议 ≤ 5 mm，经验阈值）且 d2 ≥ 3×d1（比例为经验阈值，SLVA680 只要求 d2 远大于 d1）
- `emc_precompliance`（manual）· ESD 模拟枪（IEC 61000-4-2），示波器 / 电流靶 — 对连接器接触放电 ±4 kV 起逐级测试，观察受保护引脚的钳位波形与系统是否复位 / 损坏；通过判据：系统无损坏，钳位尖峰 < IC 引脚绝对最大额定值

**来源分歧** EMC / ESD 文件会写更详细的规则；本条只覆盖通用 MCU 板的布局基线。

**来源**
- [ESD Protection Layout Guide (SLVA680A)](https://www.ti.com/lit/an/slva680/slva680.pdf) — Texas Instruments, app_note, §2.1 Optimizing Impedance for Dissipating ESD

<a id="GEN-PLC-001"></a>
#### GEN-PLC-001 · 先放固定件，再放 MCU 链，最后放去耦与外围
`consider` · 可信度 `low` · 适用: mcu_board · 标签: cat-feeder

**规则** 布局顺序：①位置被机械固定的件（连接器、安装孔、天线模块、按键）→ ②电源入口→稳压器→MCU 这条链（见 GEN-FLR-002）→ ③紧贴 IC 引脚的去耦电容、晶振及负载电容 → ④其余外围；每一步完成后再进下一步，后一步不得推翻前一步的位置。

**依据** 去耦、晶振等对距离最敏感的件必须贴着 IC，所以要在 IC 位置定下后立刻放，而不是留到最后见缝插针。

**验证**
- `review`（manual）· 布局评审清单 — 检查：连接器和安装孔位置与外壳一致；MCU 周围每个电源引脚都有去耦电容在最近位置；没有因后加外围而把去耦电容挤远（对照 GEN-PLC-002 的距离检查）

**来源分歧** 只有 TI 给出了一条优先级清单（MCU 靠近稳压器、稳压器靠近电源入口），“固定件 → 大 IC → 外围”的完整顺序是通用经验，本次调研没有找到一份权威来源逐条规定，因此置信度 low。

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.3 Board Zoning (prioritizing component placement)
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, General Principles of PCB Layout for Modules

<a id="GEN-PLC-007"></a>
#### GEN-PLC-007 · 晶振周围留出隔离区，不放无关元件
`consider` · 可信度 `medium` · 适用: crystal

**规则** 晶振 / 振荡回路周围不放无关元件（尤其电感、磁珠、开关器件、高速信号），晶振下方不走任何信号；EMI 关键的 2 层板上，无关元件离晶振至少 25.4 mm（1 英寸）。

**依据** 多数晶振相关的 EMI 串扰问题出在受扰线离晶振太近；晶振谐波可以耦合到附近的电感和其他元件上并传播出去。

| 参数 | 判据 | 备注 |
|---|---|---|
| `unrelated_component_to_crystal` | >= 25.4 mm | TI SZZA009 §2.4.1，针对 EMI 严格的 2 层板；紧凑板难以满足，需评估后放宽 |

**验证**
- `geometry_script`（full）· pcbnew — 对每个晶振，枚举所有与它无电气关联的元件，量晶振外包框到其外包框最短距离，并检查晶振 courtyard 内是否有他网络的走线 / 过孔；通过判据：没有他网络走线 / 过孔进入晶振 courtyard，无关元件间距 ≥ 项目设定值（TI 给 25.4 mm，紧凑板按评估放宽）
- `drc`（full）· KiCad 自定义规则 — (rule xtal_keepout (condition "A.intersectsCourtyard('Y1') && !A.hasNetclass('Clock')") (constraint disallow track via zone)) —— Y1 为晶振位号；Clock 网络类包含 OSC 网络

**来源分歧** TI 的 1 英寸（25.4 mm）距离出自 1999 年的 2 层板指南，现代小板几乎做不到；Espressif 与 ST 只要求走线短、周围地铜、下方无信号，不给无关元件的最小距离。取舍：禁布线 / 过孔进入晶振区按 should 严执行，25.4 mm 作为可放宽的目标。

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §1.1 RF Sources; §2.4.1
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, Crystal

<a id="GEN-PLC-008"></a>
#### GEN-PLC-008 · 串联电阻靠近驱动端放置
`consider` · 可信度 `medium` · 适用: mcu_board · 标签: cat-feeder

**规则** 为抑制振铃或降低边沿速率加的串联电阻（SPI 时钟、UART TX、MCU 输出口），放在驱动端 IC 引脚旁，尽量压在 MCU 地铜上；通向电缆或超过 1 英尺的走线、出现振铃的信号必须有串联端接。

**依据** 串联端接要在源端起作用，电阻离驱动越远，电阻前面那段走线就越长地承载未衰减的快边沿；放在远端则起不到阻尼作用。

| 参数 | 判据 | 备注 |
|---|---|---|
| `output_series_resistance` | 50 … 100 ohm | TI SZZA009 §2.2.5：每个输出脚串 50~100 Ω，输入脚 35~50 Ω；该节明确不要用于振荡器引脚；会增加元件数，按需选择 |
| `termination_required_trace_length` | > 304.8 mm | TI SZZA009 §2.4.3：走线超过 1 英尺、通向屏蔽外壳外的电缆、或出现振铃时要端接 |

**验证**
- `geometry_script`（full）· pcbnew — 对每个标记为串联端接的电阻（值 22~100 Ω，位于 MCU 输出网络上；此为识别用的宽范围，宽于 parameters 中 TI 建议的输出脚 50~100 Ω），量它的 MCU 侧焊盘到驱动引脚焊盘的距离，通过判据 ≤ 项目设定值（建议 ≤ 5 mm，经验阈值）；该电阻 MCU 侧不得再分叉出其他负载
- `si_sim`（partial）· IBIS 或 ngspice：驱动 + 走线 + 输入电容 — 对 > 1 英尺的走线或通向电缆的信号做瞬态仿真，过冲 / 下冲 ≤ 器件绝对最大额定值裕量

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.2.5 Keeping Noise Close to the Chip; §2.4.3 Series Termination
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, Flash; UART（串联电阻靠近芯片）
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §1.3.2 Characteristic Impedance, Reflections, and Termination

## 布线（routing）

<a id="GEN-RTE-002"></a>
#### GEN-RTE-002 · 信号线不得跨越参考平面的分割槽或缝隙
`must` · 可信度 `high` · 适用: 2_layer, 4_layer, mixed_signal · 标签: cat-feeder

**规则** 任何信号线都不得跨越其参考地 / 电源平面上的分割、槽或缺口；无法避免的跨越必须走在桥接位置上方或改用隔离 / 差分方式。跨越分割的电源平面时，走线所在层必须邻接完整地平面。

**依据** 跨槽使回流无法贴着信号走，形成大环路并把噪声注入另一个平面，辐射和串扰急剧增大；槽本身还会成为缝隙天线。

**验证**
- `geometry_script`（full）· pcbnew：参考层 zone 填充 + 走线几何 — 对所有非电源网络的每个走线段，取其中点所在位置在参考层的填充：若不在任何 GND 填充内（或线段穿越填充边界），则标为“跨槽”；通过判据：跨槽线段数 = 0（桥接位置白名单除外）
- `bench`（manual）· 示波器 / 近场探头，对比实验 — Ott 建议的对比：先按“不跨槽”布出分割地板，再用 0 Ω 电阻或跳线（约每 1/2 英寸一个）把两块地连起来，测功能与 EMC，对比分割 / 不分割的结果

**来源**
- [Partitioning and Layout of a Mixed-Signal PCB (H. Ott)](https://www.edn.com/partitioning-and-layout-of-a-mixed-signal-pcb-3/) — EDN / Printed Circuit Design, paper
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §1.6; §2.3 Power and Ground Planes
- [7 PCB Design Guidelines for EMI and EMC](https://www.protoexpress.com/blog/7-pcb-design-tips-solve-emi-emc-issues/) — Sierra Circuits, blog

<a id="GEN-RTE-001"></a>
#### GEN-RTE-001 · 每条信号线下方保持连续的回流参考铜
`should` · 可信度 `medium` · 适用: 2_layer, 4_layer · 标签: cat-feeder

**规则** 对时钟、PWM、SPI、开关节点等快边沿信号，沿整条走线在其正下方（相邻层）保持连续的 GND（或 PWR）铜，参考铜向走线两侧至少延伸 2h、推荐 5h（h 为走线到参考平面的介质厚度；2h / 5h 是本库按 Ott 的回流分布表取的工程取值，Ott 并未规定延伸宽度）。

**依据** 高频回流走阻抗最低路径，即信号线正下方的平面；回流电流分布在走线两侧，约 70% 在 ±2h 内，87% 在 ±5h 内，94% 在 ±10h 内。回流被切断就必须绕行，形成大环路，辐射与串扰随环路面积增大。

| 参数 | 判据 | 备注 |
|---|---|---|
| `return_plane_margin_70pct` | >= 2 multiple of h | 本库取值，非 Ott 明文要求：Ott 表给出 x/h=2 时约 70% 回流在 ±x 内 |
| `return_plane_margin_87pct` | >= 5 multiple of h | 本库取值，非 Ott 明文要求：Ott 表 x/h=5 时约 87%；x/h=10→94%，20→97% |

**验证**
- `geometry_script`（full）· pcbnew：取参考层 zone 填充多边形（zone.GetFilledPolysList） — 对 Clock / PWM / 高速网络的每个走线段每 0.5 mm 取采样点，在其参考层（2 层板为对面铜层；多层板为相邻平面层）查点是否落在 GND 填充内，且以采样点为中心 ±2h 范围的填充覆盖率 ≥ 90%；通过判据：违规采样点占比 ≤ 5%（占比阈值为经验值）。h 取叠层介质厚度（JLC 1.6 mm 2 层板约 1.5 mm）
- `emc_precompliance`（manual）· 近场磁场探头 + 频谱仪 — 沿时钟 / PWM 走线扫描磁场，回流不连续处（跨槽、过孔处）出现的局部强点即问题位置；整改前后对比降低量 ≥ 6 dB 视为有效（经验判据）

**来源**
- [Partitioning and Layout of a Mixed-Signal PCB (H. Ott)](https://www.edn.com/partitioning-and-layout-of-a-mixed-signal-pcb-3/) — EDN / Printed Circuit Design, paper, return-current distribution (x/h table)
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §1.6 Return Current and Loop Areas
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §1.4 Basic Loops; §2.1.4 Signal Return Grounds

<a id="GEN-RTE-003"></a>
#### GEN-RTE-003 · 信号换层时在过孔旁放地过孔提供回流
`should` · 可信度 `medium` · 适用: 4_layer, 2_layer · 标签: cat-feeder

**规则** 信号线换层且参考平面随之改变（或经过孔穿过地铜）时，在该信号过孔旁就近加地过孔（缝合过孔）；若信号过孔穿过的是连续不间断的同一参考平面，则不需要。

**依据** 换层使回流需要在不同平面间跳转，没有紧邻的地过孔就得绕远路，形成环路；地过孔相当于同轴结构的外导体。

**验证**
- `geometry_script`（partial）· pcbnew — 对每个信号类过孔（非 GND、非电源），找最近的 GND 过孔，量中心距；通过判据：距离 ≤ 项目设定值（建议 ≤ 2.5 mm，经验阈值）；若过孔两端参考同一平面（2 层板上底层为 GND 铺铜时，信号过孔打穿地铜形成孔洞，也要在旁补地过孔）则豁免条件另行登记

**来源**
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.5 Traces, Vias, and Other PCB Components（Figure 14）
- [7 PCB Design Guidelines for EMI and EMC](https://www.protoexpress.com/blog/7-pcb-design-tips-solve-emi-emc-issues/) — Sierra Circuits, blog, Stitching vias

<a id="GEN-RTE-004"></a>
#### GEN-RTE-004 · 电源线与地线并行贴近，环路长宽比不超过 3:1
`should` · 可信度 `high` · 适用: 2_layer, mcu_board · 标签: cat-feeder

**规则** 2 层板上电源与地并行布线，让电源走线正好在地线（或地铜）的正上方；IC 到电源之间的电源和地走线，长度与宽度之比不超过 3:1。

**依据** 电感随长度增加、随宽度缓慢减小；电源线的电感在开关电流下产生会传播和辐射的压降。电源与地重叠减小环路面积。

| 参数 | 判据 | 备注 |
|---|---|---|
| `power_ground_trace_length_to_width` | <= 3 ratio | TI：两层板，IC 到电压源之间的电源和地走线 |

**验证**
- `geometry_script`（full）· pcbnew — 对每个 IC 的电源网络，沿从稳压器 / 去耦电容到 IC 电源引脚的连接取每段走线的长度 / 宽度比（宽度取该段最窄处），通过判据 ≤ 3；并检查该段正下方相邻层有无 GND 铜（≥ 90% 长度，经验阈值）

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.1.1 Inductance

<a id="GEN-RTE-005"></a>
#### GEN-RTE-005 · 电源分配单点或星形，别串成菊花链
`should` · 可信度 `high` · 适用: mcu_board, motor_driver · 标签: cat-feeder

**规则** 电源从稳压器 / 入口大电容出发，用各自独立的支路分别供给 MCU、模块与电机等负载，在源头单点汇合；不让一个负载的电源走线串联穿过另一个负载。

**依据** 菊花链（多点）让后级共用前级的走线阻抗，噪声通过共阻抗耦合；单点最佳，星形次之，多点最差（对信号线则星形最优）。

**验证**
- `geometry_script`（partial）· pcbnew：按网络建铜连通图 — 以稳压器输出 / 入口电容为根，构造电源网络的树；对每个负载（MCU 电源、电机驱动、传感器）取从根到它的路径；通过判据：不同负载的路径只在根（入口电容焊盘）处共享，共享走线段长度 ≤ 1 个走线宽度；噪声负载（电机驱动）与敏感负载（MCU、模拟）不共用走线
- `bench`（manual）· 示波器 — 电机启动时测 MCU 3V3 引脚电压跌落，对比星形与链式；通过判据：跌落 < MCU 供电容差的一半

**来源分歧** TI 的 Figure 6 对“电源线”认为单点最佳、星形次之、多点最差，对“信号线”认为星形最佳。本条只讨论电源。实际 2 层小板上完全单点难做到，TI 也建议“产生 RF 的器件单点、其余多点”的折中。

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.2.1 Single-Point vs Multipoint; §2.2.2 Star Distribution, Figure 6

<a id="GEN-RTE-008"></a>
#### GEN-RTE-008 · 快信号避免 T 形分支和长残桩
`should` · 可信度 `high` · 适用: clock, fast_signals

**规则** 时钟和快速信号做成点对点或链式（干线上只有极短的引出），不使用 T 形分支；同一信号经过多层过孔时，不要留下穿过整板的过孔残桩。

**依据** 分支处发生阻抗突变和反射，分支到各器件的延时也不同；过孔穿过的多余部分相当于开路传输线，在 1/4 波长处造成零点。

**验证**
- `geometry_script`（full）· pcbnew：按网络建连通图 — 对 Clock 类网络计算图中度 ≥ 3 的节点（分支点），并量每个引出段长度；通过判据：时钟网络分支点数 = 0，或引出段长度 ≤ 项目设定值（建议 ≤ 2 mm，经验阈值）
- `si_sim`（partial）· ngspice / IBIS 瞬态 — 对多负载时钟仿真，各接收端的过冲和单调性满足输入阈值，且最慢边沿时间满足建立 / 保持

**来源**
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.6 Clock Distribution; §2.5（Figure 16 via stub）
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, RF（走线无分支）

<a id="GEN-RTE-009"></a>
#### GEN-RTE-009 · 敏感信号和时钟尽量不打过孔
`should` · 可信度 `high` · 适用: clock, crystal, sensitive_analog

**规则** 时钟、晶振、复位、射频、模拟小信号等敏感网络尽量全程同层布线、不打过孔；晶振时钟输入 / 输出走线上不放过孔。

**依据** 过孔引入电感和电容、造成阻抗突变和反射，并增加走线长度，还会让回流换层。

| 参数 | 判据 | 备注 |
|---|---|---|
| `vias_on_crystal_clock_traces` | == 0 count | Espressif：Do not place vias on the clock input and output traces |

**验证**
- `drc`（full）· KiCad 自定义规则 via_count — (rule no_via_clock (condition "A.hasNetclass('Clock') || A.hasNetclass('Sensitive')") (constraint via_count (max 0))) —— 个别确需换层的网络在规则里按网络名排除，并配套执行 GEN-RTE-003
- `geometry_script`（full）· pcbnew — 统计各敏感网络的过孔数，晶振 OSC 网络必须为 0

**来源**
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.5 Tips for routing traces and the use of vias
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, Crystal; RF

<a id="GEN-RTE-010"></a>
#### GEN-RTE-010 · 干扰源与敏感线间距至少 3 倍线宽
`should` · 可信度 `medium` · 适用: mcu_board, mixed_signal · 标签: cat-feeder

**规则** 时钟、PWM、开关等干扰线与敏感线（复位、采样输入、模拟小信号）平行走线时，边到边间距 ≥ 3 倍线宽（3W）；平行长度很短或参考平面很近时可小于 3W，但不低于 2 倍线宽。

**依据** 串扰随平行长度、频率、电压摆幅增大，随间距增大而减小；3W 是偏保守的经验值，适合走线与地平面距离较大的板子。

| 参数 | 判据 | 备注 |
|---|---|---|
| `aggressor_victim_spacing` | >= 3 multiple of trace width | Altium / Sierra Circuits 的 3W（两处均未写明按边到边还是中心到中心；本库按较保守的边到边取，中心到中心 3W 仅约 2W 净间距） |
| `absolute_min_spacing` | >= 2 multiple of trace width | TI SCAA082A：至少 2 倍线宽；§2.5 提示取 2~3 倍 |
| `critical_traces_guarded_spacing` | >= 3 multiple of trace width | Sierra：关键线之间 3W~5W（取 3~5）并配合接地保护线 |

**验证**
- `drc`（full）· KiCad 自定义规则 clearance — 按网络类写规则，例如 0.2 mm 线宽的 Clock 网络类：(rule clock_3w (condition "A.hasNetclass('Clock') && !B.hasNetclass('Clock')") (constraint clearance (min 0.6mm)))；DRC 0 error
- `geometry_script`（full）· pcbnew：计算平行段 — 对 Clock / PWM 网络与 Sensitive 网络的每对走线，找平行（夹角 < 10°）且间距 < 3W 的段，累计长度；通过判据：累计长度 ≤ 项目设定值（建议 ≤ 5 mm，经验阈值）
- `bench`（manual）· 示波器 — 让干扰线持续翻转，测受害线上的串扰幅度，通过判据：串扰峰值 < 受害输入的噪声容限的 1/4（经验判据）

**来源分歧** 3W 的度量口径来源未统一说明：本次读到的 Altium / Sierra / TI 均未写明是边到边还是中心到中心，本库按较保守的边到边取；Altium 指出板子参考平面更近（介质更薄）时可以小于 3W，而间距实际取决于走线到平面的距离。取舍：边到边 3W 作保守值，平面很近时可降到不低于 2W（TI），并以仿真 / 实测验证。

**来源**
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §1.4 Crosstalk; §2.5 tips
- [Crosstalk Analysis, Reduction, and Elimination Techniques in PCB Design](https://resources.altium.com/p/crosstalk-elimination-techniques-in-altium-designer) — Altium, blog
- [Handling Crosstalk in High-Speed PCB Design](https://www.protoexpress.com/blog/crosstalk-high-speed-pcb-design/) — Sierra Circuits, blog

<a id="GEN-RTE-013"></a>
#### GEN-RTE-013 · 晶振下方不走信号，时钟走线周围用地包裹
`should` · 可信度 `high` · 适用: crystal

**规则** 晶振下方不走任何信号线（最好完全不走线）；时钟走线两侧和附近用地铜包围并加地过孔，电源过孔离时钟线尽量远；高频信号（USB、UART、SPI 时钟）远离晶振走线；晶振和时钟网络上不挂测试点。

**依据** 晶振信号微弱且杂散电容敏感，旁边的快边沿会耦合进来；测试点和长引线增加杂散电容与天线效应，ST 在其坏例子里就把“测试点太多”列为问题。

**验证**
- `geometry_script`（full）· pcbnew — 取晶振 courtyard 区域，检查所有层中是否存在非 OSC / GND 网络的走线、过孔、铜皮；检查 OSC 网络上的测试点焊盘（Fabrication_Property == 'Test point pad' 或位号 TP*）数量必须为 0；通过判据：违规项 = 0
- `drc`（full）· KiCad 自定义规则 — (rule xtal_no_signals (condition "A.intersectsCourtyard('Y1') && !A.hasNetclass('Clock') && A.NetName != 'GND'") (constraint disallow track via)) —— Y1 为晶振位号

**来源分歧** ST AN2867 §7.1 要求晶振下有专用的局部地平面（与应用板地分开、连到最近的 MCU 地），Espressif 则要求晶振下方是整片完整 GND 平面且周围 clean ground；两者对“下方铺地”一致，差别在是否与大地分开。见 GEN-PLN-010。

**来源**
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, Crystal
- [AN2867 Oscillator design guide for STM8AF/AL/S, STM32 MCUs and MPUs](https://www.st.com/resource/en/application_note/an2867-guidelines-for-oscillator-design-on-stm8afals-and-stm32-mcusmpus-stmicroelectronics.pdf) — STMicroelectronics, app_note, §7.1–7.2（Rev 13）

<a id="GEN-RTE-014"></a>
#### GEN-RTE-014 · 连接器先到 TVS 再到 IC，路径短直无桩无过孔
`should` · 可信度 `high` · 适用: connector, tvs, esd · 标签: cat-feeder

**规则** 受保护信号从连接器直接走到 TVS 保护引脚，再去被保护 IC；连接器到 TVS 之间不打过孔、不接桩线、拐角不超过 45°（优先圆弧），不让未受保护的走线紧邻这段路径；TVS 地焊盘直接接同层地铜，并在紧邻其地引脚处加过孔缝合到相邻地层。

**依据** ESD 脉冲 di/dt 极大，路径上每一点电感都变成钳位电压的一部分；TVS 前的路径是主要辐射源，旁边的未保护线会被感应出电流而损坏器件；先到 TVS 再经过孔才能保证电流先被引向 TVS。

| 参数 | 判据 | 备注 |
|---|---|---|
| `connector_to_tvs_vias` | == 0 count | SLVA680A：尽量避免；必须换层时，先到 TVS 再过孔（Case 1） |
| `connector_to_tvs_max_corner` | <= 45 deg | SLVA680A：优先圆弧，45° 为可接受的最大角 |

**验证**
- `geometry_script`（full）· pcbnew — 对每个 ESD 网络：①连接器焊盘→TVS 焊盘之间过孔数 = 0 且线段无分叉；②其间拐角 ≤ 45°；③距离该路径 2 mm 内无其他网络的走线（未保护网络；2 mm 为经验阈值，SLVA680A 只要求不相邻、未给距离）；④TVS 地焊盘到最近 GND 过孔距离 ≤ 焊盘宽度（经验阈值）；通过判据：四项全满足
- `emc_precompliance`（manual）· ESD 枪 + 示波器 — 接触放电 ±4 kV 起，对比 TVS 前后波形；受保护 IC 引脚钳位峰值 < 其绝对最大额定值

**来源**
- [ESD Protection Layout Guide (SLVA680A)](https://www.ti.com/lit/an/slva680/slva680.pdf) — Texas Instruments, app_note, §2.1–2.4

<a id="GEN-RTE-006"></a>
#### GEN-RTE-006 · MCU 供电走线按厂商给的最小宽度
`consider` · 可信度 `high` · 适用: esp32, wifi_module · 标签: cat-feeder

**规则** 以 ESP32-C3 厂商指南为例：3.3 V 主电源走线宽度 ≥ 25 mil（0.635 mm），VDD3P3 走线 ≥ 20 mil（0.508 mm），其他电源走线推荐 10 mil（0.254 mm）；电源走线跨层至少 2 个过孔。其他 MCU 以各自指南为准，不低于按电流算出的宽度（GEN-STK-007）。

**依据** 无线类芯片的发射瞬间电流大，供电走线阻抗过高会拉低芯片引脚电压，造成复位或射频性能变差。

| 参数 | 判据 | 备注 |
|---|---|---|
| `main_3v3_trace_width` | >= 0.635 mm | Espressif：3.3 V main power traces at least 25 mil（四层板章节；2 层板章节未给宽度） |
| `vdd3p3_trace_width` | >= 0.508 mm | Espressif：20 mil |
| `other_power_trace_width` | >= 0.254 mm | Espressif：推荐 10 mil |

**验证**
- `geometry_script`（full）· pcbnew — 对 3V3 主网络的走线段最窄宽度取 min，应 ≥ 0.635 mm（模块板为 3V3 到模块电源引脚之间的走线）；其它电源网络 ≥ 0.254 mm；跨层处并联过孔 ≥ 2
- `drc`（full）· KiCad 自定义规则 — (rule v3p3_width (condition "A.hasNetclass('Power3V3')") (constraint track_width (min 0.635mm)))

**来源分歧** 这些宽度出自 ESP32-C3 芯片的四层板章节；cat-feeder 板用的是 ESP32-C3-WROOM-02 模块 + 2 层板，模块内部已含芯片供电，板上只需把 3V3 以不低于该宽度送到模块电源脚。

**来源**
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, Power Supply

<a id="GEN-RTE-007"></a>
#### GEN-RTE-007 · 拐角默认用 45° 或圆弧，90° 并非一概有害
`consider` · 可信度 `high` · 适用: routing · 标签: cat-feeder

**规则** 默认用 45° 或圆弧拐角（无额外成本）；对射频、可控阻抗快速线、ESD 保护路径（连接器到 TVS）严格禁用 90° 拐角；对普通低速 MCU 信号，90° 拐角不是信号完整性问题。拐角是否影响信号：线宽（mil）> 5 × 上升时间（ps）时才值得担心。

**依据** 拐角处多出约半个方块的金属，附加约 2 fF/mil × 线宽的电容，产生微小反射；对 4~8 mil 线宽和纳秒级边沿几乎不可见。但在 ESD 这种 ~800 ps 上升沿、数十 A 的路径上，90° 拐角处场强集中，辐射明显更强。

| 参数 | 判据 | 备注 |
|---|---|---|
| `corner_excess_capacitance` | == 2 fF per mil of line width | Bogatin 经验值（推导得 1.6 fF/mil，取整为 2）；60 mil 线的拐角估算约 120 fF，其 TDR 实测约 96 fF |
| `corner_matters_when` | qualitative - | 线宽(mil) > 5 × 上升时间(ps)。例：10 ps 上升时 50 Ω 线宽 > 50 mil 才受影响；100 ps → 500 mil |
| `esd_path_max_corner` | <= 45 deg | TI SLVA680A：连接器到 TVS 路径若必须拐弯，优先圆弧，最大 45° |

**验证**
- `geometry_script`（full）· pcbnew：遍历相连的 PCB_TRACK 对 — 对每对共端点的线段计算方向变化角，转角 ≥ 80° 视为 90° 拐角；通过判据（严格集合：RF / 快速 / ESD 路径网络类）：90° 拐角数 = 0；普通网络仅报告数量不判失败
- `drc`（partial）· KiCad 自定义规则 track_angle 约束 — (rule no_right_angle (condition "A.hasNetclass('ESD_Path') || A.hasNetclass('RF')") (constraint track_angle (min <阈值>deg))) —— KiCad 文档未定义“角度”的取值惯例（直线是 180° 还是 0°），先用含已知 90° 拐角的测试板确认惯例再填阈值
- `bench`（manual）· TDR（上升时间 ≤ 40 ps） — Bogatin 用 40 ps 上升时间的 TDR 在 60 mil 线的拐角上测得附加电容约 96 fF（经验公式估算 120 fF）；在自己板上做同样测量可验证 5×rise 判据

**来源分歧** TI SCAA082A 建议避免直角（至少两个 45° 或圆弧）；Bogatin 和 Altium 指出对普通数字线它们只是约几 fF 的电容，不值得担心；TI SLVA680A 又把 ESD 路径上的 90° 拐角描述为强辐射源（电场在拐角集中，8 kV 下半径小于约 2.6 mm 会电离）。三者前提不同：普通低速线 / 高速可控阻抗线 / ESD 大 di/dt 路径。取舍：默认 45° 或圆弧，仅对后两类严格；不把“90° 一律有害”当规则。

**来源**
- [When to worry about trace corners: Rule of Thumb #24 (E. Bogatin)](https://www.edn.com/when-to-worry-about-trace-corners-rule-of-thumb-24/) — EDN, paper
- [ESD Protection Layout Guide (SLVA680A)](https://www.ti.com/lit/an/slva680/slva680.pdf) — Texas Instruments, app_note, §2.2 Limiting EMI from ESD
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.5（Figure 13）
- [PCB Routing Angle Myths: 45-degree Angle Vs 90-degree Angle](https://resources.altium.com/p/pcb-routing-angle-myths-45-degree-angle-versus-90-degree-angle) — Altium, blog

<a id="GEN-RTE-011"></a>
#### GEN-RTE-011 · 相邻走线层垂直布线，但 2 层板优先保证回流
`consider` · 可信度 `medium` · 适用: 2_layer, 4_layer · 标签: cat-feeder

**规则** 两个相邻走线层之间有或没有平面时分别处理：中间隔着完整平面的相邻层，让走线方向相互垂直以减小层间耦合；没有平面的 2 层板，则以“回流紧贴信号”优先，底层主要做地铜，不为垂直而牺牲地。

**依据** 平行走线在相邻层之间耦合，垂直布线最小；但 2 层板本身没有平面，垂直网格会让返回路径离开信号线正下方。

**验证**
- `geometry_script`（partial）· pcbnew — 仅对双面都走信号的板：统计顶层与底层平行（夹角 < 10°）且重叠（正投影重叠宽度 > 0）的信号段长度，通过判据：重叠长度 ≤ 项目设定值；同时对高速 / 时钟线保留回流检查（GEN-RTE-001）

**来源分歧** SCAA082A 建议相邻层垂直布线以减少串扰；SZZA009 §2.2.3 却指出：顶层走线多为竖向、底层多为横向，这本来就与“让回流直接在信号线正下方”相悖。前者面向有平面的高速板，后者面向 2 层板。取舍：有平面时垂直，2 层板以回流为先。

**来源**
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.5 Tips for routing traces and the use of vias
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.2.3 Gridding to Create Planes

<a id="GEN-RTE-012"></a>
#### GEN-RTE-012 · 噪声走线不放在板子最外沿
`consider` · 可信度 `medium` · 适用: mcu_board

**规则** 时钟、PWM 等噪声大的走线不走在板子最外沿，离板边留出距离；可能成为受害者的线远离连接器、晶振、继电器 / 电机驱动。

**依据** 板边的走线更容易向外辐射、边缘处回流平面也不完整；靠近连接器的线最容易拾取或传出噪声。

**验证**
- `geometry_script`（full）· pcbnew — 取 Clock / PWM / Switching 网络走线到 Edge.Cuts 的最短距离，通过判据 ≥ 项目设定值（建议 ≥ 3 mm，经验阈值）；回流平面（GND 铜）应延伸到走线外至少 2h（见 GEN-RTE-001）

**来源分歧** 只有 TI 的定性表述（“绝不让噪声线跑在板子外沿”），没有给距离；板边距离是本库的经验阈值。20H 一类规则属 EMC 文件范围。

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.4.1 Capacitive and Inductive Crosstalk
- [7 PCB Design Guidelines for EMI and EMC](https://www.protoexpress.com/blog/7-pcb-design-tips-solve-emi-emc-issues/) — Sierra Circuits, blog

<a id="GEN-RTE-015"></a>
#### GEN-RTE-015 · 快速信号走线长度限制在约 1/50 波长以内
`consider` · 可信度 `high` · 适用: mcu_board, 2_layer

**规则** 无屏蔽的消费 / 汽车类 2 层板上，时钟及其他快边沿线的走线长度应小于约 1/50 波长（例如超过 4 英寸 ≈ 100 mm 的线对 FM 频段噪声就可能成为问题）；超长时缩短或加串联端接。

**依据** 走线和环路的辐射效率随长度增大，直到 1/4 波长；对商用限值走线长于 λ/10 开始重要，对更严的车规和无屏蔽 2 层板，λ/50 就开始重要。

| 参数 | 判据 | 备注 |
|---|---|---|
| `fast_trace_max_length` | <= 101.6 mm | TI：消费 / 汽车类 2 层板 λ/50 起重要，对应 FM 频段超过 4 英寸的线 |

**验证**
- `geometry_script`（full）· pcbnew — 取 Clock / PWM / 快边沿网络的走线总长，通过判据 ≤ 101.6 mm；超出的网络需登记串联端接（见 GEN-PLC-008）或豁免理由
- `emc_precompliance`（manual）· 近场探头 + 频谱仪 — 对超长线在 FM 频段（88~108 MHz）及其谐波做扫描，通过判据：低于目标限值

**来源分歧** TI 的阈值来自 1999 年的 2 层板指南并以 FM 频段为例；FCC 用 λ/10、军标 λ/20~λ/30。不同产品应以实际 EMC 目标频段重算。

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §1.4.1 Proportionality of Loops and Dipoles; §2.4.2 Antenna Factor Length Rules

## 平面与铺铜（plane_pour）

<a id="GEN-PLN-009"></a>
#### GEN-PLN-009 · 天线下方和周围所有铜层禁布，铺铜前先画禁布区
`must` · 可信度 `high` · 适用: wifi_module, esp32, antenna · 标签: cat-feeder

**规则** 模块的 PCB 天线下方和周围在所有铜层都不放铜（线、过孔、铺铜），先画好禁布区（keep-out / 规则区域）再铺铜，避免地铺铜填进去；天线下方有底板时要挖空；靠近天线的底板地铜加密集地过孔。

**依据** 天线周围的铜会使天线失谐、降低增益；铺铜忘记避让是常见的“发射正常、接收灵敏度差”原因。

| 参数 | 判据 | 备注 |
|---|---|---|
| `antenna_keepout_layers` | qualitative - | Espressif：天线下方和周围任何层都没有铜；具体禁布尺寸以所用模块数据手册为准，本库不给数值 |

**验证**
- `drc`（full）· KiCad 规则区域（禁布：铜、过孔、走线）+ DRC — 天线区建规则区域，勾选禁止 tracks / vias / copper fill；DRC 的“Items not allowed”数 = 0
- `geometry_script`（full）· pcbnew，参见 ee-pcb-verify 的 geometry 检查器 的天线禁布检查 — 取所有铜层的走线、过孔、焊盘与区域填充多边形，检查是否有任何顶点 / 线段落入天线禁布矩形；通过判据：数量 = 0
- `bench`（manual）· 路由器 RSSI / 吞吐量测试，VNA（若有天线测试口） — 在最终外壳内测同一位置的 RSSI 与吞吐量，对比官方开发板；通过判据：RSSI 差 ≤ 3 dB（经验判据）

**来源**
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, General Principles of PCB Layout for Modules
- [PCB Editor — rule areas (keepout) and Items not allowed](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Miscellaneous DRC checks: Items not allowed

<a id="GEN-PLN-001"></a>
#### GEN-PLN-001 · 先保证完整地平面，地层不走线、不被过孔排切成槽
`should` · 可信度 `high` · 适用: 4_layer, 2_layer · 标签: cat-feeder

**规则** 地参考层（4 层板的 L2，2 层板的底层）除不可避免的极短跳线外不走信号线；平面上的孔、反焊盘、引脚排不得连成长槽——相邻孔 / 反焊盘之间保留铜桥，必须埋线时绕板周边走或放在电源平面里。

**依据** 平面上的缺口增大回流环路面积；一排 100 mil 间距的通孔会把平面割成槽，既增加环路又聚焦槽缝辐射。

**验证**
- `geometry_script`（full）· pcbnew — ①在地参考层统计非 GND 网络的走线长度，4 层板通过判据 = 0，2 层板 ≤ 项目登记的跳线总长；②对该层所有过孔 / 通孔焊盘，计算相邻两个反焊盘（孔径 + 2×间隙）之间的铜桥宽度，通过判据 ≥ 0.3 mm（经验阈值），并检查 GND 填充多边形的最窄颈宽
- `drc`（full）· KiCad 区域设置 + 自定义规则 — GND 区域的 Minimum width 设 ≥ 0.2 mm 以去掉窄颈；加 (rule no_sig_in_gnd_layer (layer In1.Cu) (condition "A.NetName != 'GND'") (constraint disallow track)) —— In1.Cu 为 4 层板的地层

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.1.7 Power Plane Do's and Don'ts for Four-Layer Boards, Figure 5
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.5（Figure 15）

<a id="GEN-PLN-002"></a>
#### GEN-PLN-002 · 默认用一整块地平面，靠分区而不是分割隔离模拟数字
`should` · 可信度 `high` · 适用: mixed_signal, mcu_board · 标签: cat-feeder

**规则** 数模混合 MCU 板默认只用一个连续的地平面（GND），通过 GEN-FLR-003 的分区让数字回流不进模拟区；只有低漏电医疗设备、带大功率噪声输出的工业设备，或已经布得很差的板子才考虑分割。

**依据** 数字回流本来就停留在数字走线正下方，不会自己跑进模拟区；分割地平面本身并不阻止回流，反而在有信号跨越时造成大环路。

**验证**
- `geometry_script`（full）· pcbnew — 统计每个铜层上名为 GND / AGND / DGND 的区域数量与是否互相断开，通过判据：每层地区域只有 1 块连通体（允许因为走线造成的次要岛状碎片，另见 GEN-PLN-007）
- `bench`（manual）· 示波器 + 近场探头 — Ott 的对比实验：先留出连接两块地的位置（约每 1/2 英寸一个 0 Ω 电阻），先断开后连接，比较 ADC 噪声与 EMC，预期连接后更好

**来源分歧** 分歧：Ott 认为“几乎总是只用单一参考平面更好”，仅在三种场合考虑分割；TI SCAA082A 说数据转换器厂商常建议分开模拟地和数字地，但自己倾向连续平面（分割时要满足 GEN-PLN-003）；ADI Bryant 讲义写道混合信号系统常有分开的模拟 / 数字地平面，在靠近电源处的星形点汇合，但转换器的 AGND 和 DGND 引脚应一起接到模拟地平面（耗流小于 30 mA 或不含大计算的器件），大 DSP 带编解码器是例外（DGND 瞬态 > 100 mA）。三者并不矛盾：关键是不让数字回流进模拟区。本板的 MCU + HX711 模块 + 电机，采用单一地平面 + 分区 + 大电流回流单点（GEN-FLR-004）。

**来源**
- [Partitioning and Layout of a Mixed-Signal PCB (H. Ott)](https://www.edn.com/partitioning-and-layout-of-a-mixed-signal-pcb-3/) — EDN / Printed Circuit Design, paper
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.3 Power and Ground Planes, Figure 9
- [Grounding Analog-Digital Converters (J. Bryant, ADI lecture, mirror)](http://www.hit.bme.hu/~papay/edu/Acrobat/GndADCs.pdf) — Analog Devices, app_note

<a id="GEN-PLN-003"></a>
#### GEN-PLN-003 · 必须分割地时，只在一点连接，信号只能走桥
`should` · 可信度 `high` · 适用: mixed_signal, split_ground

**规则** 确需分割地时：两块地只在一个位置连接（桥），所有跨区信号都从桥上方经过，使每条线下方都有回流；每个子系统的回流不流经另一个子系统；电源平面只参考自己的地，不与别的地重叠；不在电源平面与无关的地之间接旁路电容。

**依据** 多点连接形成地环路并增加辐射；信号越过缺口则回流绕远路，形成大环路并把噪声串入另一个地。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ground_connection_points` | == 1 count | TI：Connect split ground planes only at one point；Ott：桥宽与单个 ADC 同宽，置于 ADC 下方 |
| `jumper_interval_in_comparison_test` | == 12.7 mm | Ott 对比实验的 0 Ω 跳线间距（1/2 英寸）；仅用于实验，不是设计值 |

**验证**
- `geometry_script`（partial）· pcbnew — ①两地之间的连接点（0 Ω / 磁珠 / 铜桥）数 = 1；②所有跨越两地边界的信号走线段的中点都落在桥的 ±(桥宽/2) 范围内；③每个电源平面的投影与其他地平面的重叠面积 = 0；④检查旁路电容两端是否在同一地域内。通过判据：①~④全部满足
- `erc`（partial）· KiCad ERC 与网络类检查 — 原理图中 AGND / DGND 之间只有一个连接元件（0 Ω 或磁珠或网络标签）；旁路电容的 GND 引脚与其所在电源同域

**来源**
- [Partitioning and Layout of a Mixed-Signal PCB (H. Ott)](https://www.edn.com/partitioning-and-layout-of-a-mixed-signal-pcb-3/) — EDN / Printed Circuit Design, paper
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.3 Power and Ground Planes（If split ground planes are essential）

<a id="GEN-PLN-004"></a>
#### GEN-PLN-004 · 2 层板用地网格 / 整面地铺铜并多打缝合过孔
`should` · 可信度 `high` · 适用: 2_layer · 标签: cat-feeder

**规则** 2 层板把两层所有空白处都铺 GND 铜并连成网格，在顶层走线与底层走线交叉处、地铜的连接处尽量多打地过孔；每块地铜至少两处与其他地铜连接，避免只有一端连的地线或铺铜。

**依据** 网格化让每条信号线下方都有地回流，近似 4 层板的地平面；只在一点连接的铺铜只是一个屏蔽层，连接在两点以上才成为导体，成为地网格的一部分。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ground_fill_connection_points` | >= 2 count | TI SZZA009：地铜连接在两处以上才算网格的一部分 |

**验证**
- `geometry_script`（full）· pcbnew — 取每层所有 GND 填充连通区，统计每个连通区被过孔 / 其他层 GND 铜连接的点数；通过判据：每个面积大于项目设定值的 GND 区域连接点数 ≥ 2；另检查顶层信号线与底层信号线交叉点旁 3 mm 内是否有 GND 过孔（经验阈值）
- `drc`（full）· KiCad DRC — “Isolated copper fill”类（孤岛）违规数 = 0；“Via is not connected or is connected on only one layer” = 0

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.2.3 Gridding to Create Planes
- [Hardware design with RP2040](https://pip.raspberrypi.com/documents/RP-008279-DS-hardware-design-with-rp2040.pdf) — Raspberry Pi, vendor_guide, §2.4.1 USB（底层几乎整层是地）

<a id="GEN-PLN-005"></a>
#### GEN-PLN-005 · MCU 下方做地岛，去耦和晶振的地接在上面
`should` · 可信度 `medium` · 适用: 2_layer, mcu · 标签: cat-feeder

**规则** 2 层板在 MCU 下方的底层做一块与 MCU 地连接的地岛，范围超出器件外轮廓约 1/4 英寸（≈6.35 mm）；去耦电容、电源滤波和晶振电容的地都接到这块地岛，使环路面积（俯视）最小。

**依据** MCU 的噪声电流集中在其电源 / 地引脚与旁路电容之间；让这些回路在同一块地上闭合，噪声不会外泄到更大的地网络。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ground_island_margin_beyond_device` | >= 6.35 mm | TI：about 1/4 inch outside the outline of the device |

**验证**
- `geometry_script`（full）· pcbnew — 取 MCU（或模块 GND 焊盘区）外包框向外扩 6.35 mm 形成矩形，计算其内底层 GND 填充面积占比，通过判据 ≥ 90%（占比阈值为经验值）；检查去耦电容 GND 焊盘是否位于该矩形内

**来源分歧** 模块板的天线端下方必须无铜（见 GEN-PLN-009），地岛只覆盖模块的接地焊盘区而不覆盖天线区。

**来源**
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.1.2–2.1.3 Microcomputer Grounds in One- and Two-Layer Designs

<a id="GEN-PLN-006"></a>
#### GEN-PLN-006 · 地铜用缝合过孔连接，间距不超过 λ/20
`should` · 可信度 `medium` · 适用: 2_layer, 4_layer, rf · 标签: cat-feeder

**规则** 顶底层（及内层）地铜之间用地缝合过孔连接，沿板周边、射频 / 天线地周围、信号过孔旁和 TVS 地引脚旁布置；过孔间距小于所关心最高频率的 λ/20。

**依据** 地铜之间距离过孔太远，铜皮本身会在高频下成为谐振结构或缝隙；板周边的缝合过孔与两个地平面一起能构成法拉第笼，TVS 旁的缝合过孔降低 ESD 回流电感。

| 参数 | 判据 | 备注 |
|---|---|---|
| `via_fence_spacing_wavelength_fraction` | < 0.05 wavelength | Sierra：小于 λ/20（示例：1 GHz 时小于 9 mm）。λ/20 是经验公式，非标准；2.45 GHz 的 3.7 mm 为本库按同一 εeff 推算 |

**验证**
- `geometry_script`（full）· pcbnew — 取 GND 过孔坐标，对射频区域和板周边路径（沿板边内缩 1 mm 的多边形）上相邻 GND 过孔的最大间距，通过判据 ≤ λ_eff/20（λ_eff = c / (f·√εeff)，εeff 取 2.8，f 取最高关注频率；2.45 GHz 时约 3.7 mm）。该 εeff 与 Sierra 示例（1 GHz→9 mm）反推一致，为推导值
- `emc_precompliance`（manual）· 近场探头 + 频谱仪 — 对比加缝合过孔前后的板边近场强度，通过判据：关注频点下降 ≥ 3 dB（经验判据）

**来源分歧** λ/20 来自二手博客并无标准出处；Ott 只说两个地平面可以沿板边缝合形成法拉第笼，没有给间距；TI SLVA680A 的例子是在 TVS 地焊盘旁放 1~4 个缝合过孔。RF 领域的天线地缝合细节归 RF 文件。

**来源**
- [7 PCB Design Guidelines for EMI and EMC](https://www.protoexpress.com/blog/7-pcb-design-tips-solve-emi-emc-issues/) — Sierra Circuits, blog, stitching vias; via fence
- [PCB Stack-Up, Part 2 (Henry Ott Consultants)](https://hott.shielddigitaldesign.com/techtips/pcb-stack-up-2.html) — Henry Ott Consultants, paper, Fig. 3b
- [ESD Protection Layout Guide (SLVA680A)](https://www.ti.com/lit/an/slva680/slva680.pdf) — Texas Instruments, app_note, §2.4

<a id="GEN-PLN-007"></a>
#### GEN-PLN-007 · 去掉死铜和孤岛，不让铺铜悬空
`should` · 可信度 `medium` · 适用: kicad · 标签: cat-feeder

**规则** 铺铜区设置“移除孤岛（Remove islands）”为 Always（或设最小面积阈值），DRC 中“Isolated copper fill”类违规数为 0；确需保留的悬空铜必须接地。

**依据** 没有连到任何同网络铜的孤岛是悬空导体，可成为耦合 / 辐射的“天线”，也可能是铜渣；地铺铜只有一端连时只相当于屏蔽层而不是导体。

**验证**
- `drc`（full）· kicad-cli pcb drc --format json — 违规类型“Isolated copper fill”（孤岛）数 = 0，“Copper sliver”数 = 0；注意 KiCad 只对至少有一处电气连接的区域去孤岛，完全未连接的区域不会被去掉
- `geometry_script`（full）· pcbnew：zone.GetFilledPolysList() 取连通块 — 对每个 zone 的每个填充连通块，检查是否至少含一个同网络焊盘 / 过孔 / 走线；通过判据：无孤块

**来源分歧** “悬空铜是天线”的说法是常见经验；本次调研读到的是 KiCad 对孤岛的处理方式和 TI 对只有一点连接的铺铜的说明，没有找到孤岛辐射的量化来源，所以置信度 medium。

**来源**
- [KiCad 9.0 PCB Editor — Zone properties; Miscellaneous DRC checks](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Remove islands; Isolated copper fill; Copper sliver
- [PCB Design Guidelines For Reduced EMI (SZZA009)](https://www.ti.com/lit/an/szza009/szza009.pdf) — Texas Instruments, app_note, §2.2.3 Gridding to Create Planes

<a id="GEN-PLN-008"></a>
#### GEN-PLN-008 · 通孔焊盘用热焊盘，SMD 地焊盘和去耦地直接连
`should` · 可信度 `medium` · 适用: kicad, smd, tht · 标签: cat-feeder

**规则** 铺铜与焊盘的连接：通孔焊盘（便于手工焊接）用热焊盘（thermal relief），SMD 地焊盘（去耦电容、EPAD 等）与地铜实心连接而不是经细线；每个热焊盘至少保留 2 条辐条。

**依据** 热焊盘增大焊盘到铜皮的热阻，便于焊接但增大了连接电感；去耦地焊盘需要最短的回流，Espressif 要求地焊盘直接接触地铜而不是经走线。

| 参数 | 判据 | 备注 |
|---|---|---|
| `min_thermal_spokes` | >= 2 count | KiCad 文档示例规则要求 4（全部辐条）；2 为本库取的下限（经验值） |

**验证**
- `drc`（full）· KiCad 自定义规则 + DRC — (rule smd_gnd_solid (condition "A.Pad_Type == 'SMD' && A.NetName == 'GND'") (constraint zone_connection solid)) 与 (rule pth_gnd_relief (condition "A.Pad_Type == 'Through-hole' && A.NetName == 'GND'") (constraint zone_connection thermal_reliefs)) 与 (rule min_spokes (constraint min_resolved_spokes 2))；DRC 里“Thermal relief connection to zone incomplete”数 = 0
- `bench`（manual）· 手工焊接试焊 / 回流后目检 — 通孔地焊盘能被普通烙铁正常焊透、不出现冷焊；小型 SMD 地焊盘回流后无立碑（墓碑）

**来源分歧** 热焊盘与“最低电感”矛盾：KiCad 的 Reliefs for PTH 选项让通孔用热焊盘、SMD 用实心；对大电流焊盘（电机、功率 MOSFET 源极）改用实心以提高载流是常见经验做法（无来源，需结合热设计）。

**来源**
- [KiCad 9.0 PCB Editor — Zone properties (Pad connection) and custom rules](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Pad connection; Thermal relief connection to zone incomplete; min_resolved_spokes
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, Power Supply（Ground pads should contact the ground copper directly）

<a id="GEN-PLN-010"></a>
#### GEN-PLN-010 · 晶振下方做完整地参考，区域内不放其他网络的铜
`should` · 可信度 `high` · 适用: crystal

**规则** 晶振及其时钟走线下方的相邻层是完整的地平面（或连到最近 MCU 地的局部地平面），区域内不放别的网络的铜、不开孔；金属壳晶振的外壳不接振荡器地。

**依据** 完整的地给振荡回路一个紧贴的低阻回流并屏蔽相邻信号的耦合，同时没有别的网络的铜进入杂散电容敏感区。

**验证**
- `geometry_script`（full）· pcbnew — 取晶振 courtyard 外扩 1 mm（外扩量为经验取值），检查相邻层 GND 填充覆盖率 ≥ 100%（无反焊盘 / 槽 / 他网络铜），且各层中无非 GND 非 OSC 网络的铜；通过判据：违规 = 0
- `bench`（manual）· 频率计 / 示波器（时钟输出引脚） — 冷启动 50 次（次数为经验取值），振荡启动成功率 100%，启动时间 ≤ 数据手册最大值；改动地参考前后对比

**来源分歧** ST：晶振下用专用局部地平面（与应用板地分开，仅连到最近 MCU 地，且仅在晶振附近需要）；Espressif：整个芯片 / RF / 晶振下是完整的 GND 平面。两者都要求紧邻的完整地，差别是否与大地分开。取舍：多层板按 Espressif（整块地），2 层板在地岛（GEN-PLN-005）内满足 ST 的局部地即可。

**来源**
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, Crystal; General Principles for the Chip
- [AN2867 Oscillator design guide for STM8AF/AL/S, STM32 MCUs and MPUs](https://www.st.com/resource/en/application_note/an2867-guidelines-for-oscillator-design-on-stm8afals-and-stm32-mcusmpus-stmicroelectronics.pdf) — STMicroelectronics, app_note, §7.1（Rev 13）

<a id="GEN-PLN-011"></a>
#### GEN-PLN-011 · 芯片底部接地焊盘用多个过孔接地平面
`should` · 可信度 `high` · 适用: qfn, esp32, module · 标签: cat-feeder

**规则** ESP32-C3 这类带底部接地焊盘（EPAD）的 QFN 芯片：EPAD 通过至少 9 个地过孔接地平面（9 为 Espressif 对该芯片的要求，其他芯片以各自数据手册为准）；模块 EPAD 用方格网分割焊盘、锡膏印在方格间隙内，过孔打在间隙里。

**依据** 底部焊盘是芯片唯一（或主要）的地连接，同时承担散热；过孔数不足会增大地电感和热阻。

| 参数 | 判据 | 备注 |
|---|---|---|
| `epad_ground_vias_chip` | >= 9 count | Espressif：ESP32-C3 芯片底部地焊盘至少 9 个地过孔（芯片专用数值，不可套用到其他 QFN；该条出现在四层板章节，两层板章节未重复） |

**验证**
- `geometry_script`（full）· pcbnew — 取每个 EPAD 焊盘的外包框，统计落在其中的 GND 过孔数；通过判据：ESP32-C3 芯片 EPAD ≥ 9，其他芯片 / 模块 EPAD 按各自数据手册；另检查 EPAD 与地铜的实心连接（GEN-PLN-008）
- `thermal_sim`（manual）· 热阻网络估算 / 热像仪 — 满载下测芯片壳温，通过判据：结温 ≤ 数据手册最大值 − 20 °C（余量为经验值）

**来源**
- [ESP32-C3 Hardware Design Guidelines — PCB Layout Design](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif, vendor_guide, Power Supply（four-layer）

## 签核验证（verification）

<a id="GEN-VER-001"></a>
#### GEN-VER-001 · ERC 零违规，例外逐条带理由，禁止整类静音
`must` · 可信度 `high` · 适用: erc, sign_off · 标签: cat-feeder

**规则** 原理图 ERC 在所有严重级别上报告 0 个违规；确属误报的单项用「带注释排除」并写明原因，禁止用「忽略全部」或降低整类严重级别来通过。 定期用 --severity-exclusions 复查排除项，清理过期例外。

**依据** ERC 只有在每条违规都被认真对待时才有意义；整类降级会让新出现的真问题一起沉默， 而排除缺失电源脚的标记并不会让这些引脚进入网表，板子上仍然是一个没供电的器件。

| 参数 | 判据 | 备注 |
|---|---|---|
| `kicad_cli_exit_code_no_violations` | == 0 退出码 | kicad-cli sch erc --exit-code-violations |

**验证**
- `erc`（full）· kicad-cli sch erc --severity-all --exit-code-violations --format json — 在干净检出、固定 KiCad 主版本下运行，退出码为 0；JSON 报告解析而不是正则匹配文本。
- `erc`（partial）· 解析 .kicad_pro 的 ERC 设置与排除列表的脚本；kicad-cli sch erc --severity-exclusions — 每个排除项都有非空注释；没有被设为 ignore 的检查项超出项目基线清单；--severity-exclusions 的报告与上次评审保存的例外清单逐项对照。 （.kicad_pro 内的字段名随 KiCad 版本核对）

**来源**
- [KiCad 10 Schematic Editor manual — Electrical rules checking（Excluding violations）](https://docs.kicad.org/10.0/en/eeschema/eeschema.html) — KiCad, tool_doc, Electrical rules checking
- [How to run ERC in KiCad from the command line reliably](https://www.makeirl.com/blog/run-erc-kicad-command-line) — MakeIRL, blog
- [pcb-checklist: schematic checklist（ERC 100% clean，例外逐个检查签字）](https://github.com/azonenberg/pcb-checklist/blob/master/schematic-checklist.md) — Andrew Zonenberg, blog, ERC
- [Symbol has power input pins that are not placed — KiCad ERC](https://pcbkit.com/tools/kicad-erc-reference/missing-power-pin/) — pcbkit, blog

<a id="GEN-VER-008"></a>
#### GEN-VER-008 · 下单前按固定门禁逐项签核
`must` · 可信度 `medium` · 适用: release, order, gate · 标签: cat-feeder

**规则** 生成订单（或把文件发给板厂 / 贴片厂）之前，全部门禁必须通过并有记录：ERC 零违规；含奇偶性的 DRC 零违规（所有严重级别）； BOM 每个非 DNP 行都能匹配厂方料号；贴装预览已核对旋转与极性；网表差异已审阅且附 IPC-D-356；独立评审完成； 当前版本已打标签。涉及付款的步骤另需下单人明确同意。

**依据** 各检查覆盖的范围互不重叠：ERC 不替代 DRC 和奇偶性，DRC 查不出旋转错误，零违规也不验证数据手册限值。 任何一项缺失，错误都会带到板厂。

**验证**
- `erc`（full）· kicad-cli sch erc --severity-all --exit-code-violations — 门禁 1：退出码 0。
- `drc`（full）· kicad-cli pcb drc --schematic-parity --severity-all --exit-code-violations — 门禁 2：退出码 0。
- `bom_check`（full）· kicad-cli sch export bom + 厂方零件库匹配脚本 — 门禁 3：每个非 DNP 行有 MPN 和 LCSC 号且在库中匹配（见 GEN-ARC-005、GEN-LIB-008）。
- `review`（partial）· 门禁运行器（形如 scripts/preflight.py 的脚本）+ 签核清单 — 门禁 4-7：贴装预览旋转核对记录、网表差异记录（GEN-NET-006）、评审记录（GEN-VER-004）、git 标签存在。 运行器汇总所有门禁，任一失败则返回非零退出码并阻止后续下单步骤。

**来源**
- [How to run ERC in KiCad from the command line reliably](https://www.makeirl.com/blog/run-erc-kicad-command-line) — MakeIRL, blog, Limits / CI gating
- [KiCad Command-Line Interface](https://docs.kicad.org/8.0/en/cli/cli.html) — KiCad, tool_doc, sch erc / pcb drc
- [PCB Assembly FAQs（BOM 中匹配不到库的料不会被贴装）](https://jlcpcb.com/help/article/pcb-assembly-faqs) — JLCPCB, vendor_guide
- [Do You Need an IPC-D-356 Netlist?](https://resources.altium.com/p/do-you-need-ipc-d-356-netlist) — Altium, vendor_guide

<a id="GEN-VER-002"></a>
#### GEN-VER-002 · 按类别理解 ERC 违规，PWR_FLAG 只放在真实电源源头
`should` · 可信度 `high` · 适用: erc, power_flag · 标签: cat-feeder

**规则** 处理 ERC 违规时先识别类别再动手：连接类（pin_not_connected、wire_dangling）、电气类型类（pin_to_pin、pin_not_driven、power_pin_not_driven）、 命名类（multiple_net_names、similar_*）、库类（lib_symbol_mismatch）、层次类（hier_label_mismatch）。 「Input Power pin not driven」用 PWR_FLAG 或输出电源脚消除，但 PWR_FLAG 只放在真实的电源源头（连接器输入、电池端、稳压器输出）。

**依据** PWR_FLAG 声明「这个网络有电源」，并不创造电源；散落在每个警告上的 PWR_FLAG 会让真正缺失的供电不再被报告。 ERC 不能穿过无源器件（保险丝、磁珠、跳线）传播供电，下游侧可能需要单独标注。

| 参数 | 判据 | 备注 |
|---|---|---|
| `erc_power_pin_not_driven_default_severity` | qualitative | 默认 Error；常见于电源来自无源连接器时 |

**验证**
- `erc`（partial）· kicad-cli sch erc --severity-all — 报告中 power_pin_not_driven、pin_to_pin、pin_not_driven 为 0；脚本统计 PWR_FLAG 个数与位置，每个 PWR_FLAG 都必须在电源入口 / 稳压器输出等白名单位置。
- `review`（manual）· 评审清单 — 对每个 PWR_FLAG 回答：它代表的真实电源是什么？答不出来的删除并修复根因（符号引脚类型或缺失的供电）。

**来源**
- [KiCad 10 Schematic Editor manual — Electrical rules checking / PWR_FLAG](https://docs.kicad.org/10.0/en/eeschema/eeschema.html) — KiCad, tool_doc, Electrical rules checking
- [KiCad ERC Error Reference](https://pcbkit.com/tools/kicad-erc-reference/) — pcbkit, blog
- [How to run ERC in KiCad from the command line reliably](https://www.makeirl.com/blog/run-erc-kicad-command-line) — MakeIRL, blog, PWR_FLAG

<a id="GEN-VER-003"></a>
#### GEN-VER-003 · 打开默认被忽略的 ERC 检查
`should` · 可信度 `high` · 适用: erc, kicad

**规则** 把默认「忽略」的 ERC 检查改成 Warning 或 Error 并纳入门禁：至少包括 single_global_label（全局标签只出现一次）、 footprint_filter（封装与符号过滤器不符）；四路交叉点 four_way_junction 视图纸风格决定是否开启。

**依据** 全局标签拼错是最常见的静默断线，默认检查是关着的；封装过滤器可以拦住把 0402 电阻误指到电解电容封装之类的错误。

**验证**
- `erc`（full）· 解析 .kicad_pro 的 ERC 严重级别表的脚本 — single_global_label、footprint_filter 的严重级别不是 ignore；kicad-cli sch erc 在启用后无违规。

**来源分歧** KiCad 10 手册的 ERC 表把 footprint_filter（封装与过滤器不符）列为 Warning，pcbkit 的参考表则写默认忽略。实测（2026-10-20，KiCad 10.0.6）：对没有 .kicad_pro 的裸工程跑 kicad-cli sch erc，报告里的 ignored_checks 为 single_global_label、four_way_junction、simulation_model_issue、footprint_filter；所以命令行 / CI 里以报告的 ignored_checks 为准，不要依赖手册表。

**来源**
- [KiCad ERC Error Reference（默认严重级别表）](https://pcbkit.com/tools/kicad-erc-reference/) — pcbkit, blog
- [KiCad 10 Schematic Editor manual — Electrical rules checking（Ignored by default）](https://docs.kicad.org/10.0/en/eeschema/eeschema.html) — KiCad, tool_doc, Electrical rules checking

<a id="GEN-VER-004"></a>
#### GEN-VER-004 · 布局前由第二人对照数据手册做原理图评审
`should` · 可信度 `high` · 适用: design_review

**规则** 布局前，由没画这张图的人用版本化的检查清单评审原理图：逐 IC 逐引脚核对数据手册和勘误，电源树、复位 / 启动、去耦、连接器、BOM 与降额； 记录发现与处理结果并签字。ERC 零违规不等于评审通过。

**依据** ERC 只检查连接的电气类型规则，查不出分压比算错、缺上拉、引脚号对错或热设计； 自检容易重复自己的假设，第二人更容易发现设计假设上的错误。

**验证**
- `review`（manual）· 评审清单（版本化，如 docs 下的 schematic_review.md）+ 评审记录 — 清单至少覆盖：每个 IC 引脚与数据手册逐脚核对、勘误、电源轨预算、上电时序、复位与 strapping、去耦、未用引脚、连接器保护、 降额、BOM 生命周期。每条有「通过 / 不适用 / 发现 + 处理」记录；评审人不是原作者。

**来源**
- [Schematic Design Review Checklist](https://resources.altium.com/p/schematic-review-checklist) — Altium, vendor_guide
- [pcb-checklist: schematic checklist](https://github.com/azonenberg/pcb-checklist/blob/master/schematic-checklist.md) — Andrew Zonenberg, blog
- [How to run ERC in KiCad from the command line reliably（Limits：零违规 ERC 不验证数据手册限值、引脚、稳定性等）](https://www.makeirl.com/blog/run-erc-kicad-command-line) — MakeIRL, blog, Limits

<a id="GEN-VER-006"></a>
#### GEN-VER-006 · 把仿真与实测对照并记录模型的适用范围
`should` · 可信度 `medium` · 适用: simulation, bench_correlation

**规则** 用作签核依据的仿真，必须有同条件下的实测对照，并记录模型的特性、对照结果和局限；厂商模型在对照前只当作假设。 差异超出规定范围时修正模型或加大设计余量，不直接采信仿真。

**依据** EDN 的案例里，厂商 LDO 模型显示带宽约为实测的两倍、相位裕度超过 30 度，而实测只有约 21.7 度，67.3 kHz； 只信仿真会误判稳定。分立元件模型也可能有错误（钽电容软件模型的错误、MOSFET 的米勒电荷与手册不符）。

| 参数 | 判据 | 备注 |
|---|---|---|
| `example_ldo_bench_phase_margin` | == 21.7 deg | EDN/AEi 案例的实测相位裕度（带宽 67.3 kHz）；厂商模型给出超过 30 度。案例值，不是阈值 |

**验证**
- `bench`（manual）· 示波器 / 网络分析仪 / 阶跃负载 — 按相同的负载、电压、温度条件测量被仿真的指标（输出阶跃响应、带宽、相位裕度或建立时间），与仿真结果并列记录差异。
- `spice`（partial）· ngspice / LTspice — 用实测修正后的模型重跑签核仿真；差异超出项目规定的容忍范围（项目自定）时，模型不得用作签核依据。

**来源**
- [SPICE models need correlation to measurements](https://www.edn.com/spice-models-need-correlation-to-measurements/) — EDN, blog

<a id="GEN-VER-007"></a>
#### GEN-VER-007 · 首次上电按步骤逐轨进行并限流
`should` · 可信度 `medium` · 适用: bring_up, first_article · 标签: cat-feeder

**规则** 首板上电前先目检并测量每条电源轨对地电阻（接近 0 欧姆就停止）；用限流可调的台式电源，限流设在略高于预期静态电流处， 电压从零缓升；从输入向内逐轨上电，每个稳压器输出确认无误再启用下一级；上电时用热像仪或手指监测发热。

**依据** 新板最常见的首次上电故障是短路、反向和焊接桥连；限流把故障限制在不烧毁器件的能量内，逐轨上电让故障定位到一个稳压器范围内。

| 参数 | 判据 | 备注 |
|---|---|---|
| `first_power_current_limit_small_board` | 50 … 100 mA | projects-house 对小型板的建议，略高于预期静态电流；示例板含电机和射频，应按各级预期电流单独设 |

**验证**
- `bench`（manual）· 限流台式电源、万用表、热像仪 — 步骤清单：1) 目检（放大 10 倍）；2) 各轨对地电阻并记录；3) 限流上电，缓升电压，监测电流； 4) 出现恒流模式、电流随电压持续上升或发热时停止；5) 逐轨测实际电压并与预期比较；6) 确认上电时序。 每一步记录实际值。

**来源**
- [PCB Bring-Up: Powering On a New Board Without Killing It](https://www.projects-house.com/articles/electronics-development/pcb-bring-up-new-board/) — Projects House, blog

<a id="GEN-VER-009"></a>
#### GEN-VER-009 · EDA 文件进版本控制，忽略缓存并给下单版本打标签
`should` · 可信度 `medium` · 适用: version_control, git

**规则** 项目文件（.kicad_pro、.kicad_sch、.kicad_pcb、项目本地库、库表、被引用的 3D 模型）放进 git；忽略缓存、锁文件、自动备份和可再生输出； 每个下单版本打标签并保存其出图包的清单（文件名与哈希）；评审用渲染出的图而不是原始 s-expression 差异。

**依据** KiCad 的文件是文本，可以进 git，但一个电阻的改动可能触及几百行，原始差异不适合评审； 备份 zip 每次保存都会重写，是仓库膨胀的主因；没有标签就无法复现某个已下单版本。

**验证**
- `review`（full）· git ls-files 与 .gitignore 检查脚本 — git ls-files 中不得出现 fp-info-cache、*-backups/、_autosave-*、~*.lck、*.kicad_prl 等； 项目文件、sym-lib-table、fp-lib-table 和项目库必须已被跟踪；每个已下单版本存在 git 标签，且标签对应的出图包清单文件存在。

**来源分歧** GitHub 的 KiCad.gitignore 忽略备份、自动保存和 fp-info-cache；BoardRepo 的指南认为自动保存和备份默认应保留，因为它们可能含有主文件里没有的恢复内容。 取舍：备份 zip 和自动保存不进 git（体积与噪声），恢复靠频繁提交；缓存与锁文件一律忽略。

**来源**
- [KiCad.gitignore (github/gitignore)](https://github.com/github/gitignore/blob/main/KiCad.gitignore) — GitHub, tool_doc
- [Version control for KiCad projects](https://boardrepo.com/guides/kicad-version-control) — BoardRepo, blog

<a id="GEN-VER-005"></a>
#### GEN-VER-005 · 布局前只仿真数据手册答不了的关键块
`consider` · 可信度 `medium` · 适用: simulation, power_up, ldo, current_sense, gate_drive · 标签: cat-feeder

**规则** 布局前对数据手册无法直接回答的块做仿真：上电 / 复位时序（电源斜坡加 RC）、稳压器稳定性与负载阶跃（用有效电容与 ESR）、 检流放大链的增益 / 限幅 / 滤波、栅极驱动与续流路径、容差最坏情况。数据手册已给出结论的简单电路不必仿真。

**依据** 仿真的成本在建模和验证模型，只有结果会改变设计决策的块才值得做； 这些块的错误在板子回来之后很难靠改值修复，且依赖元件的实际行为（偏压降容、ESR、容差）。

**验证**
- `spice`（partial）· ngspice（kicad-cli sch export netlist --format spice 或 KiCad 内置仿真器） — 对每个入选块写一个带判据的仿真网表（例如 EN 越过阈值的时刻、输出过冲 / 欠冲、ADC 输入最大电压、栅极峰值电压）， 批处理运行并检查判据；容差用 STEP 或蒙特卡洛（TI SLYP673 给出的典型运行次数为 1000-100000 次）。

**来源**
- [Schematic Design Review Checklist（Power：simulate switch-mode regulators for stability, current capability and voltage regulation）](https://resources.altium.com/p/schematic-review-checklist) — Altium, vendor_guide
- [How to avoid design problems by using worst case analysis calculations (SLYP673)](https://www.ti.com/lit/pdf/slyp673) — Texas Instruments, app_note
- [KiCad Command-Line Interface — sch export netlist（spice 格式）](https://docs.kicad.org/8.0/en/cli/cli.html) — KiCad, tool_doc

