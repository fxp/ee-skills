# 高压 / 隔离 / 安规（hv_safety）— 规则全文

横向领域 · 23 条规则 · 由 `catalog/*.yaml` 生成，请改 YAML 不要改本文件。用 `grep -n "<规则ID>" rules.md` 定位单条，不要整份读。

环节分布：架构与选型 6，符号封装库 1，原理图 3，网表与约束 1，叠层与规则 2，分区规划 2，器件布局 1，布线 3，平面与铺铜 1，出图与制造 1，签核验证 2

## 架构与选型（architecture）

<a id="HVS-ARC-001"></a>
#### HVS-ARC-001 · 先划分电压域：ELV/SELV 与危险电压
`must` · 可信度 `medium` · 适用: all-boards · 标签: cat-feeder

**规则** 设计之初给每个网络组标注电压域：交流不超过 50 Vrms、无纹波直流不超过 120 V 的为特低压（ELV，SELV/PELV 沿用此限值）；超过则属低压（LV）范围，须按危险电压处理（绝缘等级、爬电/间隙、熔断、认证）。要把瞬态（电机续流、浪涌）后的最高电压也计入核对。5 V/12 V 板是 ELV，由外部认证电源适配器提供 SELV，板上不接市电。

**依据** ELV 阈值以下，电击危险由电源决定，板上只需要功能性间距；超过后须有基本/加强绝缘，间距按 IEC 62368-1 / IEC 60664-1 查表，加保险丝，做耐压测试，进入 EU 低压指令（2014/35/EU，下限 50 V AC / 75 V DC）的范围。

| 参数 | 判据 | 备注 |
|---|---|---|
| `elv_ac_limit` | <= 50 Vrms | IEC 61140:2016 / IEC 60364-4-41:2017 的 ELV 交流上限（来自 Wikipedia 对标准的转述）；SELV/PELV 使用同一限值 |
| `elv_dc_limit` | <= 120 V | 同上，无纹波直流 |
| `eu_lvd_lower_limit_ac` | >= 50 Vac | EU 低压指令 2014/35/EU 适用范围下限：50 V AC / 75 V DC 至 1000 V AC / 1500 V DC |
| `eu_lvd_lower_limit_dc` | >= 75 Vdc | 同上 |

**验证**
- `review`（manual）· 网络电压表（自建） — 每个电源/信号域列出稳态与瞬态最高电压（含电机续流、TVS 钳位后残压）；任何网络 > 50 Vrms 或 > 120 V DC 触发 HVS 其余规则
- `bom_check`（partial）· BOM 脚本 — 外部适配器规格为认证 SELV/LPS 输出，且额定输出电压 ≤ 板上所有器件额定值

**来源**
- [Extra-low voltage](https://en.wikipedia.org/wiki/Extra-low_voltage) — Wikipedia, blog
- IEC 61140:2016 Protection against electric shock（IEC 61140:2016; IEC 60364-4-41:2017; Directive 2014/35/EU (未打开原文，限值取自 Wikipedia 转述)） — standard

<a id="HVS-ARC-002"></a>
#### HVS-ARC-002 · 每道隔离边界定义绝缘类型
`must` · 可信度 `medium` · 适用: isolation-barrier, mains-board

**规则** 对板上每道隔离边界写明绝缘类型：功能（仅保证工作）、基本（基本电击防护）、附加、双重（基本 + 附加）或加强（单一系统，防护等效双重）。凡可能让可触及部分出现危险电压的边界（如市电到低压次级）按加强/双重处理，爬电距离取基本绝缘查表值的 2 倍。

**依据** 基本绝缘失效即失去防护，因此对可触及部分要求冗余；加强绝缘用单层结构提供等效双重的防护，在紧凑设计里常用。

| 参数 | 判据 | 备注 |
|---|---|---|
| `reinforced_creepage_multiplier` | == 2 ratio | smps.us 爬电计算器说明：查表值适用于功能、基本、附加绝缘；加强绝缘要加倍。间隙对加强绝缘按更高的脉冲耐压档取值，本研究未读到该表 |

**验证**
- `review`（manual）· 绝缘图（自建） — 画出每道边界的两侧电压、绝缘类型、所用器件（隔离器、变压器、Y 电容）和要求的爬电/间隙；缺项即不通过

**来源**
- [Isolation Glossary (SLLA353A)](https://www.ti.com/lit/pdf/slla353) — Texas Instruments, app_note, Insulation definitions
- [PCB Creepage Calculator](https://pcbdesign.smps.us/creepage.html) — smps.us (Lazar Rozenblat), tool_doc
- [High-voltage reinforced isolation - definitions and test methodologies (SLYY063)](https://www.ti.com/lit/pdf/slyy063) — Texas Instruments, app_note

<a id="HVS-ARC-006"></a>
#### HVS-ARC-006 · 锂电池包必须有电芯级保护 IC
`must` · 可信度 `medium` · 适用: li-ion, li-polymer, battery-pack · 标签: cat-feeder

**规则** 单节锂离子/锂聚合物电芯必须带保护电路，至少覆盖过充、过放、充电过流、放电过流和负载短路；保护 IC 的阈值与恢复时间要与电芯规格对照核对。不允许把裸电芯直接接到负载。

**依据** 锂电池在过充、过放、过流或短路下可能起火；保护 IC（如 TI BQ2970 系列）通过外部背靠背 FET 监测并切断，并带零伏充电等功能。

**验证**
- `bom_check`（partial）· BOM / 原理图评审 — 电池通路上存在保护 IC + 双 FET，且 IC 阈值（OVP、UVP、OCC、OCD、SCP）满足电芯数据手册的充放电限值
- `bench`（manual）· 可编程电源 / 电子负载（限流） — 在带限流的条件下依次验证过压、欠压、过流和短路都能切断且可恢复

**来源**
- [BQ2970/71/72/73 Voltage and Current Protection IC for Single-Cell Li-Ion](https://www.ti.com/lit/ds/symlink/bq2970.pdf) — Texas Instruments, datasheet, §1 Features

<a id="HVS-ARC-003"></a>
#### HVS-ARC-003 · 查表前先确定五个输入参数
`should` · 可信度 `high` · 适用: creepage, clearance

**规则** 在查爬电/间隙表之前，先书面确定工作电压（rms 与峰值）、过压类别（I–IV）、污染等级（1–4）、材料组（由 CTI 定）和最高工作海拔；一般用途室内设备污染等级通常按 2，存在导电污染或可预见的凝露时按 3。

**依据** 爬电距离由工作电压、污染等级和材料组共同决定，间隙由瞬态过压（过压类别与电网电压）和海拔决定；任一输入取错，查表结果都不可信。

| 参数 | 判据 | 备注 |
|---|---|---|
| `pollution_degree_general_use` | == 2 degree | smps.us：污染等级 2 是一般用途设备最常见的类型；3 适用于导电污染或会因凝露而导电的干燥污染 |

**验证**
- `review`（manual）· 设计输入清单（自建） — 工作电压 rms/峰值、OVC、PD、材料组、海拔五项齐全并经评审签字

**来源**
- [Isolation Glossary (SLLA353A)](https://www.ti.com/lit/pdf/slla353) — Texas Instruments, app_note, Pollution degree, Overvoltage categories, Material groups
- [PCB Creepage Calculator](https://pcbdesign.smps.us/creepage.html) — smps.us (Lazar Rozenblat), tool_doc

<a id="HVS-ARC-004"></a>
#### HVS-ARC-004 · 海拔超过 2000 m 时间隙要乘修正系数
`should` · 可信度 `medium` · 适用: clearance, high-altitude

**规则** 默认按不高于 2000 m 设计并在产品上标明；若要用于更高海拔，按所在标准的海拔修正系数放大电气间隙（5000 m 约 1.48 倍），爬电距离不得小于修正后的间隙。

**依据** 空气稀薄使击穿电压下降，所以间隙要放大；爬电距离从不小于间隙。GB 4943.1 假设设备可在 5000 m 工作，除非标注「仅用于 2000 m 以下」，间隙须为 IEC/UL 60950-1 的 1.48 倍。

| 参数 | 判据 | 备注 |
|---|---|---|
| `altitude_baseline` | <= 2000 m | IEC/UL 的基准海拔；高于此需修正（据 smps.us 对 GB 4943.1 的转述） |
| `altitude_clearance_multiplier_5000m` | == 1.48 ratio | 5000 m 的间隙倍数；中间海拔的系数请查 IEC 60664-1 表，本研究未读到该表 |

**验证**
- `review`（manual）· 产品规格 / 标签 — 规格写明最高工作海拔；高于 2000 m 者间隙已放大
- `geometry_script`（full）· pcbnew Python / KiCad 自定义规则 — 把修正后的间隙值写入 HV 网络类的 clearance 与 creepage 规则，DRC 零违规

**来源**
- [PCB Trace Spacing for Voltage Levels (Rozenblat)](https://www.smps.us/pcbtracespacing.html) — smps.us, blog
- [IPC-2221B Table 6-1 clearance (smpspowersupply)](https://www.smpspowersupply.com/ipc2221pcbclearance.html) — smpspowersupply.com, blog

<a id="HVS-ARC-005"></a>
#### HVS-ARC-005 · 隔离器件按额定值、封装爬电与 CTI 综合选型
`should` · 可信度 `high` · 适用: digital-isolator, optocoupler, isolated-dcdc

**规则** 选隔离 IC 时同时核对：VIORM/VIOWM ≥ 系统工作电压并留寿命裕量，VIOTM 与 VIOSM 满足暂态和浪涌要求，封装的外部爬电/间隙（CPG/CLR）满足查表值，封装模塑料 CTI/材料组与表一致。要被称为加强隔离器，元件级浪涌测试须通过大于 10 kV。

**依据** 同一封装的 CTI 不同，允许的工作电压可差一倍：TI 举例，8 mm 爬电的封装用 CTI-I 塑封料可到 1600 Vrms 工作电压，用 CTI-IIIa 仅 800 Vrms。IEC 60747-5-5 / VDE 0884 的浪涌测试对基本绝缘用 1.3 倍、对加强绝缘用 1.6 倍 VIOSM。

| 参数 | 判据 | 备注 |
|---|---|---|
| `reinforced_component_surge_test` | > 10 kV | SLYY063：元件级称为加强隔离，浪涌测试须通过 > 10 kV |
| `viosm_test_factor_reinforced` | == 1.6 ratio | 基本绝缘为 1.3 倍 |
| `wide_body_soic16_external_creepage` | > 8 mm | ISO7741 DW-16 的外部爬电/间隙均大于 8 mm，CTI > 600 V，材料组 I；DUW-16 大于 21.2 mm |
| `production_isolation_test_factor` | == 1.2 ratio | 产线对每个器件施加 1.2×VISO、1 s（型式试验 60 s） |

**验证**
- `bom_check`（partial）· BOM 脚本 + 数据手册表（Insulation Specifications） — 对每个隔离件取 CLR、CPG、CTI、材料组、VIORM、VIOTM、VIOSM，与 HVS-RTE-001 的查表结果和系统要求比较；有证书（VDE 0884-17 / UL 1577）

**来源**
- [High-voltage reinforced isolation - definitions and test methodologies (SLYY063)](https://www.ti.com/lit/pdf/slyy063) — Texas Instruments, app_note
- [ISO7740, ISO7741, ISO7742 datasheet](https://www.ti.com/lit/ds/symlink/iso7741.pdf) — Texas Instruments, datasheet, §5.6 Insulation Specifications
- [Digital Isolator Design Guide (SLLA284)](https://www.ti.com/lit/pdf/slla284) — Texas Instruments, app_note

## 符号封装库（library）

<a id="HVS-LIB-001"></a>
#### HVS-LIB-001 · 高压器件封装库要校核焊盘间距与爬电
`should` · 可信度 `low` · 适用: to-220, wide-body-soic, optocoupler, transformer

**规则** 高压网络上的通孔/贴片功率器件（TO-220、宽体 SOIC、光耦、变压器）的封装库，要核对引脚/焊盘之间及焊盘之间沿封装表面的距离是否满足所用工作电压的间隙与爬电；标准焊盘不够时在库里提供加宽间距、带开槽或带禁布区的变体，而不是在每块板上手工补救。

**依据** 器件本体的爬电由封装厂保证，但板上焊盘和铜皮可能把它缩短；smps.us 举例：400 V 以上的 TO-220 MOSFET，焊盘间距约 30 mil，而按文件要求至少 100 mil，引脚沿封装表面约 50 mil。

**验证**
- `geometry_script`（partial）· pcbnew Python / kiutils 读 .kicad_mod — 对库里每个标记为 HV 的封装，求不同电位焊盘之间的最小边到边距离（含沿封装本体的表面路径），与对应工作电压的查表值（HVS-RTE-001）比较

**来源**
- [PCB Trace Spacing for Voltage Levels (Rozenblat)](https://www.smps.us/pcbtracespacing.html) — smps.us, blog
- [ISO7740, ISO7741, ISO7742 datasheet](https://www.ti.com/lit/ds/symlink/iso7741.pdf) — Texas Instruments, datasheet, §5.6 footnote (1)

## 原理图（schematic）

<a id="HVS-SCH-001"></a>
#### HVS-SCH-001 · 电池输出串联保险丝或自恢复保险丝
`must` · 可信度 `medium` · 适用: battery, fuse, pptc · 标签: cat-feeder

**规则** 电池是低阻抗电源，电池输出通路上必须串联保险丝（或经评估的 PPTC），保险丝的额定电压与分断能力要高于电池可能提供的短路电流，并紧靠电池端放置。

**依据** 电池是低阻抗源，TI 建议始终串联保险丝作防火保护；保险丝的额定电压或分断能力不足会在断开时拉弧、产生等离子体和熔融金属，造成灾难性失效。自恢复保险丝（PPTC）同样会因过压损坏：Littelfuse 演示中最大电压 16 VDC 的 16R 系列用在 60 VDC 短路下失效，应选额定电压不低于该处最高电压的型号。

| 参数 | 判据 | 备注 |
|---|---|---|
| `fuse_interrupt_rating_vs_source` | qualitative | 额定电压与分断能力必须高于故障源（Littelfuse）；来源未给统一裕量 |

**验证**
- `bom_check`（partial）· BOM 脚本 — 保险丝额定电压 ≥ 电池最高电压，分断能力 ≥ 电池最大短路电流（≈ Vmax / 内阻，内阻取电芯数据手册）
- `bench`（manual）· 电池 + 限流保护的短路测试台 — 按 UL/IEC 要求的方法做短路与过载，观察保险丝动作、板子温升与是否起火（需防护措施）

**来源**
- [AN-2162 Simple Success With Conducted EMI From DC-DC Converters (SNVA489C)](https://www.ti.com/lit/pdf/snva489) — Texas Instruments, app_note, §7 battery caution
- [GDTs, MOVs & Fuses: Selecting the Appropriate Circuit Protection Component](https://www.ieee.li/pdf/viewgraphs/selecting_the_appropriate_circuit_protection_component.pdf) — Littelfuse, vendor_guide, Fuse Interrupted

<a id="HVS-SCH-002"></a>
#### HVS-SCH-002 · 市电输入：保险丝必须配额定电压与分断能力，MOV 要受保护
`must` · 可信度 `medium` · 适用: mains-input, mov, fuse

**规则** 市电输入的保险丝，其额定电压和最大分断电流都要高于系统可能出现的故障电压和电流；并联的 MOV 要有热保护（热熔 MOV）或前级保险丝，因为 MOV 多次浪涌后劣化、漏电自热并热失控。GDT 用在带电电源线上须选电源专用型号。

**依据** Littelfuse 称保险丝的最大电压与分断电流是安全关键指标，超出额定（其演示用 250 VAC/1500 A 的保险丝承受 400 VDC/200 A 短路）会拉弧、产生等离子体与熔融金属，造成灾难性失效；MOV 寿命终了时漏电自热、阻抗持续下降直至热失控，带内置热保护的 TMOV 无需外部保险丝即可通过 UL1449 的异常过压测试。

| 参数 | 判据 | 备注 |
|---|---|---|
| `fuse_voltage_rating_vs_fault_voltage` | qualitative | 高于系统故障电压；Littelfuse 示例保险丝 250 VAC / 1500 A，在 400 VDC / 200 A 超额定下失效 |

**验证**
- `bom_check`（partial）· BOM 脚本 — 保险丝额定电压 ≥ 线电压最高值 × 1.0（含容差），分断能力 ≥ 预期短路电流；MOV 或 TMOV 旁有保险丝或自带热保护
- `review`（manual）· 原理图评审 — 输入顺序：连接器 → 保险丝（相线）→ MOV/X 电容 → 后级；N、PE 的处理与目标市场标准一致

**来源**
- [GDTs, MOVs & Fuses: Selecting the Appropriate Circuit Protection Component](https://www.ieee.li/pdf/viewgraphs/selecting_the_appropriate_circuit_protection_component.pdf) — Littelfuse, vendor_guide
- [Failure Modes and Fusing of TVS Devices (AN 88440)](https://www.vishay.com/docs/88440/failurem.pdf) — Vishay, app_note

<a id="HVS-SCH-003"></a>
#### HVS-SCH-003 · 跨隔离栅的电容必须是安规 Y 电容
`must` · 可信度 `low` · 适用: y-capacitor, isolated-dcdc, flyback

**规则** 凡跨越隔离栅（初级—次级，或市电—可触及部分）的电容，必须是带 Y1/Y2 等级的安规电容，额定电压与隔离等级一致；容量按漏电流限值计算；它的焊盘与走线同样要满足对应绝缘等级的爬电/间隙。不得用普通 MLCC 跨接。

**依据** 电容在交流下会有电流流过，不能为了降 EMI 随意增大；安规 Y 电容经认证，失效时不会短路，而普通电容可能失效为短路而使隔离失效。Wikipedia 明确：需要防电击时优先用其他隔离方式，若用电容则其值按安全标准计算，且用于电源隔离的电容有专门的额定值以使它们不会失效为短路。

**验证**
- `bom_check`（full）· BOM 脚本 — 所有一端在初级网络、另一端在次级网络的电容，其料号带 Y1 / Y2 认证标注与 AC 额定电压
- `geometry_script`（full）· pcbnew Python — Y 电容两端焊盘之间距离与焊盘到邻近他网络铜的距离满足 HVS-RTE-001 的加强/基本查表值

**来源**
- [Galvanic isolation](https://en.wikipedia.org/wiki/Galvanic_isolation) — Wikipedia, blog
- IEC 60384-14 Fixed capacitors for use in electronic equipment - Part 14 (EMI suppression, safety)（IEC 60384-14（X/Y 电容等级；本研究未打开原文）） — standard

## 网表与约束（netlist）

<a id="HVS-NET-001"></a>
#### HVS-NET-001 · 隔离两侧用独立网络名和网络类，让 DRC 能识别
`should` · 可信度 `medium` · 适用: isolation-barrier, kicad

**规则** 把初级/危险侧与次级/SELV 侧的地和电源用不同的网络名（如 GND_PRI、GND_SEC），并给危险网络分配专用网络类（如 HV）；除隔离器件、变压器、Y 电容外，网表中不得有任何元件的引脚同时连到两侧。

**依据** 只有网络类和网络名区分开，KiCad 的 clearance/creepage 规则（按网络类和网络对象）才能作用于这些网络；隔离器件的测试也是把一侧所有引脚并为一个端、另一侧并为另一个端。

**验证**
- `netlist_diff`（full）· kicad-cli sch export netlist + 脚本 — 对网表里每个元件，收集其引脚所属的域（PRI/SEC）；除白名单（隔离器、变压器、光耦、Y 电容）外，同时含两域引脚的元件数 = 0
- `drc`（full）· kicad-cli pcb drc — HV 网络类的自定义规则（clearance、creepage）生效，见 HVS-VER-001

**来源**
- [KiCad 9.0 PCB Editor manual - custom design rules](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Custom design rules: hasNetclass(), creepage
- [High-voltage reinforced isolation - definitions and test methodologies (SLYY063)](https://www.ti.com/lit/pdf/slyy063) — Texas Instruments, app_note, Figure 1

## 叠层与规则（stackup）

<a id="HVS-STK-001"></a>
#### HVS-STK-001 · 板材 CTI 按数据手册定材料组
`should` · 可信度 `medium` · 适用: laminate, creepage

**规则** 从层压板数据手册读 CTI（IEC 60112）确定材料组，不要默认 FR-4 属于材料组 I；没有数据时按最差的 IIIb 查表。需要更小爬电时选用 CTI 更高的板材并在制造文件中写明。

**依据** CTI 衡量表面抗电痕化的能力，决定爬电距离表中使用哪一列：相同工作电压和污染等级下，材料组 I 的爬电最小，IIIa/IIIb 最大。

| 参数 | 判据 | 备注 |
|---|---|---|
| `material_group_i_cti` | >= 600 V | 材料组 I：CTI ≥ 600 V；II：400–599；IIIa：175–399；IIIb：100–174（TI 术语表与 SLYY063） |

**验证**
- `review`（manual）· 板材数据手册 / 板厂确认 — 叠层文件注明板材型号与 CTI，查表所用材料组与之对应；无资料时按 IIIb

**来源**
- [Isolation Glossary (SLLA353A)](https://www.ti.com/lit/pdf/slla353) — Texas Instruments, app_note, Material groups
- [High-voltage reinforced isolation - definitions and test methodologies (SLYY063)](https://www.ti.com/lit/pdf/slyy063) — Texas Instruments, app_note, Comparative tracking index
- [PCB Creepage Calculator](https://pcbdesign.smps.us/creepage.html) — smps.us (Lazar Rozenblat), tool_doc

<a id="HVS-STK-002"></a>
#### HVS-STK-002 · 低压（非安规）间距按 IPC-2221B 表设 DRC
`should` · 可信度 `medium` · 适用: clearance, drc, elv · 标签: cat-feeder

**规则** 对 ELV 或不受安规约束的网络，按 IPC-2221B Table 6-1 随峰值工作电压设置最小导体间距：外层未涂覆（B2）、内层（B1）、外层涂覆（B4）；把这些值写入网络类的 clearance 规则，板厂最小线距作为下限。

**依据** IPC-2221B 给出的是通用商用/工业板的推荐间距，随电压分段递增；5 V/12 V 板在 0–30 V 档，外层未涂覆间距只要 0.1 mm，小于板厂的最小线距，所以由板厂能力主导。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ipc2221b_b2_external_uncoated_up_to_30v` | >= 0.1 mm | 0–30 V（峰值）：B1 内层 0.05；B4 外层涂覆 0.05。均为海拔 ≤ 3050 m |
| `ipc2221b_b2_external_uncoated_31_to_100v` | >= 0.6 mm | 31–100 V：B1 0.1；B4 0.13 |
| `ipc2221b_b2_external_uncoated_101_to_150v` | >= 0.6 mm | 101–150 V：B1 0.2；B4 0.4 |
| `ipc2221b_b2_external_uncoated_151_to_300v` | >= 1.25 mm | 151–300 V：B1 0.2；B4 0.4 |
| `ipc2221b_b2_external_uncoated_301_to_500v` | >= 2.5 mm | 301–500 V：B1 0.25；B4 0.8；500 V 以上外层未涂覆按页面公式 2.5 + (V−500)×0.005 mm，B3（海拔 > 3050 m）与 A5–A7 列本研究未读到 |

**验证**
- `drc`（full）· kicad-cli pcb drc + 按网络类的 clearance 规则 — 按各网络组的峰值工作电压分配网络类，clearance 取表值与板厂能力较大者；DRC 零违规

**来源**
- [IPC-2221B Table 6-1 clearance (smpspowersupply)](https://www.smpspowersupply.com/ipc2221pcbclearance.html) — smpspowersupply.com, blog, adapted from columns B1, B2, B4
- IPC-2221B Generic Standard on Printed Board Design（IPC-2221B Table 6-1（本研究读的是第三方转录的 B1/B2/B4 三列，未取得原文）） — standard
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/Capabilities) — JLCPCB, vendor_guide, Traces: 0.10/0.10 mm for 1 oz

## 分区规划（floorplan）

<a id="HVS-FLR-001"></a>
#### HVS-FLR-001 · 定义隔离栅禁布区，任何层都不得有铜跨越
`must` · 可信度 `high` · 适用: isolation-barrier, digital-isolator, mains-board

**规则** 在布局规划时画出隔离栅禁布区：宽度不小于要求的爬电/间隙，危险侧与 SELV 侧的元件分居两侧；在该区内所有层都不允许有走线、过孔、焊盘、铜皮和测试点，只有隔离器件、变压器、Y 电容这类认证元件可以跨越。隔离器下方在所有层上也保持无走线、过孔和焊盘。

**依据** 铜穿过栅会直接缩短爬电/间隙，并给表面电痕化提供路径；TI 要求在所有层上保持隔离器下方的空间无走线、过孔和焊盘以保持最大爬电距离。

| 参数 | 判据 | 备注 |
|---|---|---|
| `barrier_gap` | qualitative mm | 取 HVS-RTE-001 查表所得的爬电（及间隙）值，加强绝缘加倍；在 KiCad 中写成规则区 |

**验证**
- `drc`（full）· KiCad 自定义规则 (.kicad_dru) — (rule "barrier keepout" (constraint disallow track via zone pad) (condition "A.intersectsArea('barrier')")) 并对隔离器件豁免；kicad-cli pcb drc 零违规
- `geometry_script`（full）· pcbnew Python — 枚举所有层上与禁布区相交的铜对象，除白名单跨栅元件焊盘外应为 0

**来源**
- [Digital Isolator Design Guide (SLLA284)](https://www.ti.com/lit/pdf/slla284) — Texas Instruments, app_note, §4.3 Creepage Distance, Figure 4-1
- [ISO7740, ISO7741, ISO7742 datasheet](https://www.ti.com/lit/ds/symlink/iso7741.pdf) — Texas Instruments, datasheet, §8.4 Layout, Figure 8-8
- [KiCad 9.0 PCB Editor manual - custom design rules](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Custom design rules: copper keepout example

<a id="HVS-FLR-002"></a>
#### HVS-FLR-002 · 危险电压铜皮与板边、安装孔、外壳可触及件也要满足间距
`should` · 可信度 `medium` · 适用: mains-board, enclosure, mounting-hole

**规则** 爬电和间隙不仅用于两导体之间，也用于导体与设备边界（板边、外壳表面、可触及的金属件、安装螺丝）之间；危险电压铜皮离板边、安装孔和外壳可触及导电件的距离按同样的表值取。

**依据** 爬电的定义是两导电部分之间，或导电部分与设备外表面之间，沿绝缘表面的最短路径；板边铜与外壳之间的缝隙是常被忽略的击穿路径。

**验证**
- `drc`（full）· KiCad 自定义规则：edge_clearance 约束，条件 A.hasNetclass('HV') — (rule "HV edge" (constraint edge_clearance (min <表值>)) (condition "A.hasNetclass('HV')")) 零违规；安装孔（含镀铜螺丝孔）另用 clearance 规则
- `review`（manual）· 装配图评审 — 把外壳内表面、螺丝、金属支架纳入爬电/间隙测量

**来源**
- [PCB Creepage Calculator](https://pcbdesign.smps.us/creepage.html) — smps.us (Lazar Rozenblat), tool_doc, What is creepage
- [KiCad 9.0 PCB Editor manual - custom design rules](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, edge_clearance constraint

## 器件布局（placement）

<a id="HVS-PLC-001"></a>
#### HVS-PLC-001 · 焊盘不得缩短隔离器件封装的爬电与间隙
`must` · 可信度 `high` · 适用: digital-isolator, optocoupler, transformer

**规则** 隔离器件（数字隔离器、光耦、变压器）在 PCB 上的安装焊盘，以及其周围的铜皮，不得使跨隔离栅的爬电与间隙小于封装规格或系统要求；以焊盘到焊盘、焊盘到铜皮的实际距离核对，而不是只看封装标称值。

**依据** 数据手册明确提醒：要保持板子的爬电与间隙，使器件安装焊盘不降低该距离；在 PCB 上爬电与间隙在某些情况下相等，需要开槽或加筋来增大。

| 参数 | 判据 | 备注 |
|---|---|---|
| `dw16_package_creepage` | > 8 mm | ISO7741 DW-16：CLR 与 CPG 均大于 8 mm；焊盘延长后的实际值须重新测量 |

**验证**
- `geometry_script`（full）· pcbnew Python — 对每个隔离器件，取输入侧焊盘与输出侧焊盘之间的最短距离（含周围铜皮、丝印无关），与要求的爬电值比较
- `drc`（full）· KiCad 的 creepage 约束（见 HVS-VER-001） — 跨栅网络类之间的 creepage ≥ 要求值，零违规

**来源**
- [ISO7740, ISO7741, ISO7742 datasheet](https://www.ti.com/lit/ds/symlink/iso7741.pdf) — Texas Instruments, datasheet, §5.6 footnote (1)
- [ISOW7840...ISOW7844 datasheet](https://www.ti.com/lit/ds/symlink/isow7841.pdf) — Texas Instruments, datasheet, §7.6 Insulation Specifications, footnote (1)

## 布线（routing）

<a id="HVS-RTE-001"></a>
#### HVS-RTE-001 · 按表取爬电距离，加强绝缘加倍
`must` · 可信度 `medium` · 适用: mains-board, isolation-barrier, creepage · 标签: cat-feeder

**规则** 危险电压网络之间及与其他网络之间的爬电距离，按「工作电压（rms）× 污染等级 × 材料组」查表，加强绝缘取表值的 2 倍；表值是下限，爬电距离不得小于对应的电气间隙；工作电压介于表中两档时取较高档（保守）或在标准允许时线性内插。

**依据** 爬电对应表面电痕化风险，随电压、污染和材料 CTI 增大。下表值源自 UL 60950-1 Table 2N（IEC 62368-1 Table 17 对 30 kHz 以下相同），用于功能、基本、附加绝缘。可与 TI 的例子交叉验证：PD2 材料组 IIIa 在 800 Vrms 对应 8 mm，与 SLYY063 所述 8 mm 爬电封装在 CTI-IIIa 下 800 Vrms 一致。

| 参数 | 判据 | 备注 |
|---|---|---|
| `creepage_table_basic_insulation` | qualitative | 单位 mm。Vrms 档位 = 10, 12.5, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 320, 400, 500, 630, 800, 1000。PD1（所有材料组）= 0.08, 0.09, 0.1, 0.11, 0.125, 0.14, 0.16, 0.18, 0.2, 0.22, 0.25, 0.28, 0.32, 0.42, 0.56, 0.75, 1.0, 1.3, 1.8, 2.4, 3.2。PD2 材料组 I = 0.4, 0.42, 0.45, 0.48, 0.5, 0.53, 0.56, 0.6, 0.63, 0.67, 0.71, 0.75, 0.8, 1.0, 1.25, 1.6, 2.0, 2.5, 3.2, 4.0, 5.0。PD2 材料组 II = 0.4, 0.42, 0.45, 0.48, 0.5, 0.53, 0.8, 0.85, 0.9, 0.9, 1.0, 1.05, 1.1, 1.4, 1.8, 2.2, 2.8, 3.6, 4.5, 5.6, 7.1。PD2 材料组 III = 0.4, 0.42, 0.45, 0.48, 0.5, 0.53, 1.1, 1.2, 1.25, 1.3, 1.4, 1.5, 1.6, 2.0, 2.5, 3.2, 4.0, 5.0, 6.3, 8.0, 10。PD3 材料组 I = 1.0, 1.05, 1.1, 1.2, 1.25, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.5, 3.2, 4.0, 5.0, 6.3, 8.0, 10, 12.5。PD3 材料组 II = 1.0, 1.05, 1.1, 1.2, 1.25, 1.3, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.8, 3.6, 4.5, 5.6, 7.1, 9.0, 11, 14。PD3 材料组 III = 1.0, 1.05, 1.1, 1.2, 1.25, 1.3, 1.8, 1.9, 2.0, 2.1, 2.2, 2.4, 2.5, 3.2, 4.0, 5.0, 6.3, 8.0, 10, 12.5, 16。取自 smps.us 计算器的脚本数据，未取得标准原文 |
| `creepage_pd2_mg3_250vrms` | >= 2.5 mm | 典型 230 V 市电（污染等级 2，材料组 IIIa/IIIb）基本绝缘；加强绝缘 5.0 mm |
| `creepage_pd2_mg1_250vrms` | >= 1.25 mm | 同上，材料组 I；材料组 II 为 1.8 mm；污染等级 3 材料组 III 为 4.0 mm |
| `creepage_pd2_any_group_12v5` | >= 0.42 mm | ELV 12 V 功能绝缘的参考值（污染等级 2）；对 5–12 V 板，板厂最小间距已大于此值 |
| `reinforced_creepage_multiplier` | == 2 ratio | 加强绝缘对表值加倍 |

**验证**
- `drc`（full）· kicad-cli pcb drc + 自定义规则 (constraint creepage (min X)) — 按网络类写规则：(rule "HV creepage" (condition "A.hasNetclass('HV')") (constraint creepage (min <表值>)))，DRC 无 Creepage violation
- `geometry_script`（partial）· pcbnew Python + 表查询脚本 — 对每对危险网络，沿板面最短路径（穿过 Edge.Cuts 开槽时按槽绕行）测爬电距离并与表值比较

**来源分歧** 表值是基本/功能绝缘值，IEC 62368-1 的 Table 17 与 UL 60950-1 Table 2N 对 30 kHz 以上频率可能要求更严（据 smps.us 提示，将来可能引入基于 IEC 60664-1/-4 的更严规则）。本研究未读到标准原文，认证项目必须以适用标准版本为准。

**来源**
- [PCB Creepage Calculator (UL 60950-1 Table 2N / IEC 62368-1 Table 17 数据)](https://pcbdesign.smps.us/creepage.html) — smps.us (Lazar Rozenblat), tool_doc
- [High-voltage reinforced isolation - definitions and test methodologies (SLYY063)](https://www.ti.com/lit/pdf/slyy063) — Texas Instruments, app_note, Comparative tracking index
- IEC 62368-1 / UL 62368-1 clauses 5.4.2, 5.4.3, Table 17（IEC 62368-1 §5.4.2 clearances、§5.4.3 creepage、Table 17；IEC 60664-1（本研究未取得原文）） — standard

<a id="HVS-RTE-002"></a>
#### HVS-RTE-002 · 开槽延长爬电距离，槽宽大于 1 mm 且不削弱板子
`should` · 可信度 `high` · 适用: isolation-barrier, creepage, slot

**规则** 空间不够时可在危险侧与 SELV 侧之间铣槽或开沟来延长爬电路径：槽宽大于 1 mm；有效爬电 = 原爬电 + 槽宽 + 2 × 槽深（沟槽对爬电路径的增量按此计）；槽不得使板子在机械测试中失效。间隙（空气直线距离）不会因开槽而增加。

**依据** 宽度不足的窄槽会被污物桥接，所以标准对沟槽宽度有最小要求；槽只改变沿表面的路径，不改变空气中的直线距离。

| 参数 | 判据 | 备注 |
|---|---|---|
| `slot_width_for_creepage` | > 1 mm | TI SLLA284 §4.3 对「groove」的要求；smps.us 同样称宽于 1 mm 的槽可增加爬电。JLCPCB 非金属化槽最小宽度 1.0 mm，正好在边界上，设计时取更大值（如 1.2–1.5 mm 为本研究的建议，来源未给） |

**验证**
- `geometry_script`（partial）· pcbnew Python（读 Edge.Cuts 的槽轮廓） — 槽宽 > 1 mm；沿板面的最短路径绕槽计算爬电：原路径 + 槽宽 + 2×槽深 ≥ 要求值；槽两端离铜的距离满足间隙要求
- `drc`（partial）· KiCad creepage 约束（见 HVS-VER-001） — 加了槽后重新跑 DRC，确认 KiCad 是否把槽计入爬电路径；若未计入，用上面的脚本结果作为准绳

**来源**
- [Digital Isolator Design Guide (SLLA284)](https://www.ti.com/lit/pdf/slla284) — Texas Instruments, app_note, §4.3, Figure 4-2
- [PCB Creepage Calculator](https://pcbdesign.smps.us/creepage.html) — smps.us (Lazar Rozenblat), tool_doc
- [JLCPCB PCB Capabilities](https://jlcpcb.com/capabilities/Capabilities) — JLCPCB, vendor_guide, Drilling: Min. Non-Plated Slots 1.0 mm

<a id="HVS-RTE-003"></a>
#### HVS-RTE-003 · 电气间隙由瞬态过压定，单独核对，爬电不得小于间隙
`should` · 可信度 `low` · 适用: clearance, mains-board

**规则** 电气间隙（空气直线距离）要按过压类别决定的暂态脉冲耐压和海拔单独查表，不由工作电压直接推出；最终取间隙和爬电两者中较大的值作为最小距离，因为爬电总是大于等于间隙。

**依据** 间隙防止空气击穿，决定于瞬态过压（过压类别 I–IV 与电网电压）和海拔；爬电防止表面电痕化，决定于工作电压、污染和 CTI。TI 术语表把过压类别定义为不同等级的暂态过压环境（I 信号级、II 本地级等）；因此同一工作电压在不同过压类别下的间隙要求不同。

| 参数 | 判据 | 备注 |
|---|---|---|
| `clearance_table_source` | qualitative | 间隙应查 IEC 60664-1 的脉冲耐压—间隙表或 IEC 62368-1 对应表；本研究未取得这些表。常见的 230 Vac、过压类别 II 数值（基本绝缘间隙约 1.5 mm，加强约 3 mm）来自经验，未经核实，认证前必须核对标准 |

**验证**
- `review`（manual）· 绝缘图 + 标准查表 — 对每道边界写出过压类别、电网电压、脉冲耐压、间隙查表值和海拔修正，最后取 max(间隙, 爬电)
- `drc`（full）· KiCad physical_clearance 约束 — (constraint physical_clearance (min X)) 对 HV 网络类，检查不同电位对象的空气直线距离，零违规

**来源**
- [Isolation Glossary (SLLA353A)](https://www.ti.com/lit/pdf/slla353) — Texas Instruments, app_note, Overvoltage categories
- [High-voltage reinforced isolation - definitions and test methodologies (SLYY063)](https://www.ti.com/lit/pdf/slyy063) — Texas Instruments, app_note
- [PCB Creepage Calculator](https://pcbdesign.smps.us/creepage.html) — smps.us (Lazar Rozenblat), tool_doc
- [KiCad 9.0 PCB Editor manual - custom design rules](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, physical_clearance

## 平面与铺铜（plane_pour）

<a id="HVS-PLN-001"></a>
#### HVS-PLN-001 · 铺铜、热焊盘也受 HV 网络类间距约束
`should` · 可信度 `medium` · 适用: copper-pour, kicad, drc

**规则** 危险电压网络周围的铺铜和填充区要和其他网络保持该网络类的间距；给危险网络专用网络类，并使地铜、屏蔽铜远离危险电压网络同样的距离，避免铺铜在填充后把间距缩到查表值以下。

**依据** 铺铜按网络类的 clearance 避让，若 HV 网络类没有单独的更大间距，铜皮会贴到默认最小间距；爬电计算同样包含铺铜。

**验证**
- `drc`（full）· kicad-cli pcb drc（填充后） — 先重新填充所有 zone 再跑 DRC；HV 网络类的 clearance 与 creepage 规则零违规

**来源**
- [KiCad 9.0 PCB Editor manual - custom design rules](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Custom design rules

## 出图与制造（manufacturing）

<a id="HVS-MFG-001"></a>
#### HVS-MFG-001 · 涂覆或阻焊能否缩小间距要按标准确认
`consider` · 可信度 `low` · 适用: conformal-coating, solder-mask, creepage

**规则** IPC-2221B 的「外层涂覆」列允许比「外层未涂覆」更小的间距，但对安规绝缘（IEC 62368-1 / IEC 60664-1）不要默认可以因阻焊或三防漆而缩小爬电/间隙；若要利用涂覆，须明确涂覆材料、覆盖范围和工艺，并按标准的涂覆条款（如 IEC 60664-3）做型式验证。

**依据** IPC 间距表对 B2（未涂覆）与 B4（涂覆）的差距很大，例如 151–300 V 档 1.25 mm 对 0.4 mm、301–500 V 档 2.5 mm 对 0.8 mm；但安规认证看的是被认可的涂覆工艺，而不是 IPC 通用表。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ipc2221b_uncoated_vs_coated_151_300v` | qualitative | B2 外层未涂覆 1.25 mm；B4 外层涂覆 0.4 mm；31–100 V 档为 0.6 mm 对 0.13 mm；301–500 V 档为 2.5 mm 对 0.8 mm |

**验证**
- `review`（manual）· 认证策略评审 — 凡依靠涂覆缩小间距的位置列清单，附涂覆规格与验证报告；无报告者按未涂覆处理

**来源**
- [IPC-2221B Table 6-1 clearance (smpspowersupply)](https://www.smpspowersupply.com/ipc2221pcbclearance.html) — smpspowersupply.com, blog
- [PCB Trace Spacing for Voltage Levels (Rozenblat)](https://www.smps.us/pcbtracespacing.html) — smps.us, blog
- IEC 60664-3 Use of coating, potting or moulding for protection against pollution（IEC 60664-3（本研究未取得原文，仅作线索）） — standard

## 签核验证（verification）

<a id="HVS-VER-001"></a>
#### HVS-VER-001 · 用 KiCad 的 creepage 与 clearance 规则做 DRC
`must` · 可信度 `medium` · 适用: kicad, drc, creepage

**规则** 给危险网络分配 HV 网络类，写入 .kicad_dru 的 creepage 约束（及 clearance、physical_clearance、edge_clearance 约束），每次布局修改后运行 kicad-cli pcb drc，要求没有 Creepage violation 和 Clearance violation；DRC 之外再用独立脚本核对开槽、Edge.Cuts 和层间路径。

**依据** KiCad 9 起内置 creepage 约束：检查不同网络的铜对象之间的爬电距离是否小于配置值，并在画布上显示路径；该检查按网络类设置。其对槽、外形开口、元件本体的处理和层间路径的处理本研究未验证。

| 参数 | 判据 | 备注 |
|---|---|---|
| `creepage_rule_example` | qualitative | 官方示例：(rule "minimum creepage distance for high voltage nets" (condition "A.hasNetclass('HV')") (constraint creepage (min 5mm))) |

**验证**
- `drc`（full）· kicad-cli pcb drc --format json --output out.json board.kicad_pcb（本机 KiCad 10.0.6） — 解析 JSON，Creepage violation、Clearance violation、Edge clearance violation 计数均为 0
- `geometry_script`（partial）· pcbnew Python — 对 DRC 不覆盖的路径（开槽、板边、元件本体、跨层），用脚本独立计算最短爬电并与表值比较

**来源**
- [KiCad 9.0 PCB Editor manual - custom design rules](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, DRC violations: Creepage violation; constraints: creepage; custom rule examples

<a id="HVS-VER-002"></a>
#### HVS-VER-002 · 耐压测试：型式试验与出厂试验分开，夹具把两侧引脚各并联
`should` · 可信度 `medium` · 适用: isolation-barrier, production-test

**规则** 对隔离栅做耐压（hipot）测试时，把一侧所有引脚并为一端、另一侧所有引脚并为另一端后施加测试电压；整机的测试电压、持续时间、泄漏电流跳闸门限按产品标准定；器件级做法是型式试验与产线试验分开（见参数）。功能绝缘处可用电气强度测试证明较小间距，但须有明确判据。

**依据** 隔离器件的型式试验用 VISO 持续 60 s，产线对每颗器件用 1.2×VISO 持续 1 s；整机 hipot 同样靠泄漏电流超限判失败，典型跳闸设置 0.1–20 mA，持续时间通常最长 5 min，并要控制升压速率以避免电容充电电流造成误跳。smps.us 以 UL796 的 40 V/mil（约 1.6 kV/mm）估算功能绝缘的电气强度，例如 500 V 次级需承受 1740 Vrms。

| 参数 | 判据 | 备注 |
|---|---|---|
| `component_production_test_voltage_factor` | == 1.2 ratio | TI SLYY063：产线对每颗隔离器 1.2×VISO、1 s；型式试验 VISO、60 s |
| `hipot_leakage_trip_range` | 0.1 … 20 mA | Wikipedia Hipot：典型跳闸设置；实际值由产品标准和被测物电容决定 |
| `functional_insulation_dielectric_strength` | == 1.6 kV/mm | smps.us 借用 UL796 的 40 V/mil；仅用于功能绝缘的估算，不得用于基本/加强绝缘的认证 |

**验证**
- `bench`（manual）· 耐压测试仪（带泄漏电流判据）+ 绝缘电阻表 — 夹具把两侧引脚各自并联；按计划电压、时间测试；泄漏电流小于门限、无击穿、无电弧；测试后复测隔离电阻无退化

**来源**
- [High-voltage reinforced isolation - definitions and test methodologies (SLYY063)](https://www.ti.com/lit/pdf/slyy063) — Texas Instruments, app_note, VIOTM and VISO; Figure 1
- [Hipot](https://en.wikipedia.org/wiki/Hipot) — Wikipedia, blog
- [PCB Trace Spacing for Voltage Levels (Rozenblat)](https://www.smps.us/pcbtracespacing.html) — smps.us, blog, Functional insulation (HiPot)

