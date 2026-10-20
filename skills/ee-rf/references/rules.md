# 射频与天线（rf）— 规则全文

垂直领域 · 45 条规则 · 由 `catalog/*.yaml` 生成，请改 YAML 不要改本文件。用 `grep -n "<规则ID>" rules.md` 定位单条，不要整份读。

环节分布：架构与选型 6，符号封装库 1，原理图 8，网表与约束 1，叠层与规则 3，分区规划 6，器件布局 2，布线 5，平面与铺铜 5，出图与制造 1，签核验证 7

## 架构与选型（architecture）

<a id="RF-ARC-002"></a>
#### RF-ARC-002 · 按法规限值选功率、天线增益与杂散抑制
`must` · 可信度 `high` · 适用: 2.4ghz, certification, fcc, etsi

**规则** 把目标市场的法规限值当作设计输入：FCC 15.247 数字调制（2400-2483.5 MHz）传导峰值功率 <= 1 W，天线定向增益 <= 6 dBi （超出要按超出的 dB 降功率），带外任意 100 kHz 带宽须比带内最高值低 >= 20 dB（用 RMS 平均测功率时为 30 dB）； ETSI EN 300 328 要求 e.i.r.p. <= 20 dBm，1-12.75 GHz 杂散 <= -30 dBm/1 MHz。

**依据** e.i.r.p. 含天线增益，换更高增益天线或更大功率 PA 会直接越线；谐波和杂散由匹配与滤波决定，必须在选 PA、天线和滤波器之前就确定目标。

| 参数 | 判据 | 备注 |
|---|---|---|
| `fcc_max_conducted_power` | <= 30 dBm | FCC 15.247(b)(3) 数字调制 2400-2483.5 MHz，1 W；前提是天线定向增益 <= 6 dBi（15.247(b)(4)） |
| `fcc_max_antenna_gain_without_derating` | <= 6 dBi |  |
| `fcc_out_of_band_suppression` | >= 20 dB | 15.247(d)，100 kHz 带宽相对带内最高值；若按 (b)(3) 用 RMS 平均测功率则为 30 dB |
| `etsi_max_eirp` | <= 20 dBm | EN 300 328 V2.2.2 §4.3.1.2.3（FHSS）、§4.3.2.2.3（非 FHSS） |
| `etsi_spurious_1_to_12p75ghz` | <= -30 dBm | 每 1 MHz 带宽；Table 4（FHSS）/ Table 12（非 FHSS）。传导口按传导测，一体天线设备按 e.i.r.p. 测 |

**验证**
- `review`（partial）· 法规限值对照表 — 用 Pt（传导）+ 天线增益算 e.i.r.p.，对照目标市场限值；检查天线增益是否超过 6 dBi；确认谐波滤波目标与 15.247(d)/EN 300 328 杂散限值相容。
- `bench`（manual）· 频谱仪 + 传导测试口 — 见 RF-VER-005：实测传导功率、二/三次谐波与杂散，留余量后再送认证实验室。

**来源**
- [47 CFR 15.247 Operation within the bands 902-928 MHz, 2400-2483.5 MHz, and 5725-5850 MHz](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C/subject-group-ECFR2f2e5828339709e/section-15.247) — eCFR / US Government, standard, (b)(3), (b)(4), (d)
- [ETSI EN 300 328 V2.2.2 Wideband transmission systems; Data transmission equipment operating in the 2,4 GHz band](https://www.etsi.org/deliver/etsi_en/300300_300399/300328/02.02.02_60/en_300328v020202p.pdf) — ETSI, standard, §4.3.1.2.3, §4.3.1.10.3 Table 4, §4.3.2.2.3, §4.3.2.9.3 Table 12

<a id="RF-ARC-004"></a>
#### RF-ARC-004 · 不要改动预认证模组的天线与匹配配置
`must` · 可信度 `high` · 适用: module, certification, fcc · 标签: cat-feeder

**规则** 使用预认证模组的主板必须保持认证时的天线配置：板载 PCB 天线按集成指南保留禁布区，不另加匹配或放大器； U.FL 变体只用 50 Ω、增益不高于认证天线的天线；更换天线类型或走线设计需重新认证（FCC 属 C2/C3 许可性变更）。

**依据** 模组的授权只覆盖认证时测过的天线与走线配置；天线长度、形状和增益变化会改变辐射发射，监管上被视为不同天线类型。

| 参数 | 判据 | 备注 |
|---|---|---|
| `wroom02u_external_antenna_max_gain_non_fcc` | <= 2.33 dBi | ESP32-C3-WROOM-02U 认证用天线增益；换不同类型或增益的天线可能需额外测试 |
| `wroom02u_external_antenna_max_gain_fcc` | <= 1.57 dBi | FCC 认证用天线增益 |

**验证**
- `review`（manual）· 认证文件核对清单 — 核对：天线型号/增益是否在认证清单内；主板上禁布区、地平面、馈线是否与集成指南一致；模组与天线间的匹配元件料号是否与认证时一致 （如 Murata MBN52832 要求 L1、C2 用指定料号）。
- `bom_check`（partial）· BOM 脚本 — 把模组与天线间的匹配元件料号与集成指南/认证列表逐项比对，不一致即失败。

**来源**
- [FCC KDB 996369 D01 v04r01 / D02 Q&A（DR09-45454）](https://apps.fcc.gov/eas/comments/GetPublishedDocument.html?id=520&tn=690618) — FCC Office of Engineering and Technology, standard, D01 §8.1.1-8.1.3; D02 Question 11
- [ESP32-C3-WROOM-02 & WROOM-02U Datasheet v1.7](https://www.espressif.com/sites/default/files/documentation/esp32-c3-wroom-02_datasheet_en.pdf) — Espressif Systems, datasheet, §10.2 Dimensions of External Antenna Connector
- [MBN52832 BLE Module Layout Guide](https://www.murata.com/-/media/webrenewal/products/connectivitymodule/asset/pub/rfm/data/mbn52832_antenna_layout_guide.ashx?la=en&cvid=20210615064716000000) — Murata, vendor_guide, On-board antenna connection

<a id="RF-ARC-001"></a>
#### RF-ARC-001 · 用 Friis 公式做链路预算并留衰落余量
`should` · 可信度 `medium` · 适用: link_budget, 2.4ghz, ble, wifi

**规则** 选定射频方案前先做链路预算：Pr = Pt + Gt - 路径损耗 + Gr，最大路径损耗 = Pt + Gt + Gr - 接收灵敏度 - 衰落余量。 天线增益取含辐射效率的实测/数据手册值（PCB 与芯片天线常为负 dBi），不要用峰值增益。

**依据** Friis 公式是视距链路的基本模型；天线失配是链路预算里最大的损失项之一，增益、效率和余量取得过于乐观会让实际距离远小于预期。

| 参数 | 判据 | 备注 |
|---|---|---|
| `fade_margin_consumer` | 15 … 20 dB | Hubble 博客称 10 dB 偏乐观、15-20 dB 适合可穿戴/消费类和多变环境；单一博客来源，仅作起点 |
| `fspl_at_1m_2p4ghz` | == 40 dB | 自由空间路径损耗约 40 dB + 20*log10(d/1m)（2.4-2.44 GHz；按 20log10(f)+20log10(d)-147.55 自行核算 2.44 GHz 为 40.2 dB） |

**验证**
- `review`（partial）· Python/电子表格（Friis 公式） — 列出 Pt、Gt、Gr（用 VNA/OTA 实测效率换算，而非峰值增益）、接收灵敏度（数据手册，如 nRF52 1 Mbps 约 -96 dBm）、 衰落余量，算出最大路径损耗 PL_max，再用 d = 10^((PL_max - 40)/20) m 估自由空间距离；该距离须大于需求距离，室内另扣墙体损耗。

**来源**
- [AN058 Antenna Selection Guide (SWRA161B)](https://www.ti.com/lit/pdf/swra161) — Texas Instruments, app_note, §3.4 Maximum Power Transfer (VSWR), §3.6 Friis Transmission Equation
- [How to Calculate BLE Link Budget and Range](https://hubble.com/community/guides/how-to-calculate-ble-link-budget-and-range/) — Hubble Network, blog

<a id="RF-ARC-003"></a>
#### RF-ARC-003 · 优先选预认证射频模组，量大再做分立射频
`should` · 可信度 `medium` · 适用: wifi, ble, module, discrete_rf · 标签: cat-feeder

**规则** 没有射频团队和测试设备时，选带板载天线（或 U.FL）的预认证模组并按集成指南使用；只有体积、成本或性能确有需要才做分立射频， 此时整个射频部分（器件值、封装、布局、叠层）直接复制厂商参考设计。

**依据** 模组已完成匹配、滤波和法规测试，主板只需遵守摆放与禁布；分立射频的匹配对寄生参数很敏感，偏离参考设计会让输出功率下降、灵敏度变差、杂散升高。

**验证**
- `bom_check`（partial）· BOM 审查 — 射频部分为预认证模组则记录其认证编号/集成指南版本；若为分立射频，逐项核对 RF 器件值、封装与厂商参考设计一致。
- `netlist_diff`（partial）· 原理图/参考设计网表对比脚本 — 把 RF 匹配/滤波网络的元件类型与值与参考设计网表对比，列出所有差异并逐条给出理由。

**来源**
- [FCC KDB 996369 D01 Module Certification Guide v04r01 / D02 Module Q&A（Laboratory Division Publications Report DR09-45454）](https://apps.fcc.gov/eas/comments/GetPublishedDocument.html?id=520&tn=690618) — FCC Office of Engineering and Technology, standard, D01 §8.1.1-8.1.2
- [PCB Layout Design Guide (EFR32 Wireless Gecko)](https://github.com/SiliconLabs/IoT-Developer-Boot-Camp/wiki/PCB-Layout-Design-Guide) — Silicon Labs, vendor_guide, §2.2 Layout of RF section
- [Impedance Matched RF Front End Differential Balun-Low Pass Filter for CC253X (2450BM15A0002)](https://www.johansontechnology.com/docs/2962/2450BM15A0002-App-Note-for-the-CC253X-11_7cXYuOj.pdf) — Johanson Technology, app_note, §3 Layout

<a id="RF-ARC-006"></a>
#### RF-ARC-006 · GNSS 无源天线馈线不超过 10 cm，更长用有源天线
`should` · 可信度 `high` · 适用: gnss, gps, patch_antenna

**规则** 无源 GNSS 天线必须经不超过 10 cm 的 50 Ω 微带/带状线接到接收机；走线更长或用线缆时改用带 LNA 的有源天线。 LNA 增益约 15 dB 即足够（线长到 5 m 也够），没必要超过 26 dB；线短而增益 > 35 dB 在部分接收机上会过载。

**依据** GNSS 信号极弱，无源馈线的损耗直接加在系统噪声系数上，并更易耦合干扰；有源天线的 LNA 位于线缆之前，线缆损耗不再影响噪声系数。

| 参数 | 判据 | 备注 |
|---|---|---|
| `passive_antenna_feed_max_length` | <= 100 mm | u-blox Table 1：无源天线经最长 10 cm 的微带/带状线连接接收机 |
| `active_antenna_lna_gain_typical` | == 15 dB | 对可兼容无源天线的接收机，15 dB 即使线长到 5 m 也通常足够 |
| `active_antenna_lna_gain_useful_max` | <= 26 dB | u-blox 接收机 RF 输入处无需超过 26 dB；短线加 > 35 dB 增益可能过载 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 取 GNSS 接收机 RF_IN 网络，累加从天线焊盘/连接器到 RF_IN 引脚的走线长度，<= 100 mm；超过则必须改为有源天线并核对偏置与 DC 隔离。
- `review`（manual）· 有源天线偏置检查 — 有源天线供电经射频扼流圈馈入，RF 路径有隔直电容；LNA 增益 + 线缆损耗不使接收机过载。

**来源**
- [GNSS antennas - RF design considerations for u-blox GNSS receivers (UBX-15030289 R03)](https://content.u-blox.com/sites/default/files/products/documents/GNSS-Antennas_AppNote_(UBX-15030289).pdf) — u-blox, app_note, §2.4 Active and passive antennas, Table 1

<a id="RF-ARC-005"></a>
#### RF-ARC-005 · 按频段、面积、高度和成本选天线类型
`consider` · 可信度 `high` · 适用: antenna_selection, 2.4ghz, sub_ghz

**规则** 2.4 GHz 空间够就用 PCB 倒 F（IFA/MIFA）天线；面积极小才用陶瓷芯片天线；要最好性能且允许高度时用线天线。 低于 433 MHz 的 PCB 天线很难做得小又高效，应改用芯片、线或外置天线。 芯片天线的匹配与性能依赖厂商测试板的地平面尺寸，换板型必须重调。

**依据** PCB 天线成本最低、可调长度，但占面积；芯片天线省面积但增加 BOM 和贴装成本，且不能靠改长度调谐，必须带匹配网络； 频率越低，1/4 波长越长（2.4 GHz 自由空间约 31 mm）。

| 参数 | 判据 | 备注 |
|---|---|---|
| `quarter_wavelength_2p4ghz_free_space` | == 31 mm | TI AN058：2.4 GHz λ/4 约 3.1 cm |
| `mifa_s11_bandwidth_minus10db` | == 230 MHz | Infineon AN91445 Table 5：MIFA 7.2x11.1 mm，增益 1.6 dBi；IFA 4x20.5 mm 带宽 220 MHz、1.1 dBi；芯片天线 3.2x1.6 mm 带宽 200 MHz、0.5 dBi；线天线 6x30 mm 带宽 200 MHz、2 dBi |

**验证**
- `review`（manual）· 天线选型表 — 对照可用面积、高度、成本、带宽（S11 <= -10 dB）和需求距离，选出天线类型并记录选型依据与对应厂商参考设计。
- `bench`（manual）· VNA — 原型上测 S11 与带宽，确认 2.400-2.4835 GHz 满足（见 RF-VER-001）。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §3, §4, §8, §10 Table 5
- [AN058 Antenna Selection Guide (SWRA161B)](https://www.ti.com/lit/pdf/swra161) — Texas Instruments, app_note, §3.3 Table 1 (λ/4 = 3.1 cm at 2.4 GHz); §4 Antenna Types, Table 3; §4.2 Chip Antennas

## 符号封装库（library）

<a id="RF-LIB-001"></a>
#### RF-LIB-001 · 天线/模组封装自带厂商禁布区并保持不改
`should` · 可信度 `high` · 适用: pcb_antenna, chip_antenna, module · 标签: cat-feeder

**规则** 天线或模组封装使用厂商给出的焊盘和禁布区几何，把禁布区做成封装内的 keepout rule area，在所有铜层上禁铜、禁走线、禁过孔、禁元件， 使 DRC 能自动检查；不要自行缩小或修改禁布区。

**依据** 禁布区几何是天线谐振和辐射性能的一部分，必须贯穿多层板所有铜层；偏离厂商定义的几何会使性能变得不可预测且效率降低。

**验证**
- `drc`（full）· KiCad DRC（rule area: 禁铜/走线/过孔/焊盘/封装，全部铜层） — 运行 DRC，keepout 类违例数为 0（天线自身焊盘除外）。
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 读取天线封装内 rule area 的层集合，必须包含全部铜层；并确认其多边形与厂商图纸（含悬出板外的部分）一致。

**来源**
- [Understanding Chip Antennas Handbook](https://www.johansontechnology.com/docs/4469/johanson-understanding-chip-antennas-handbook.pdf) — Johanson Technology, vendor_guide, No-Ground or Keep-Out Areas
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §12
- [ESP32-C3-WROOM-02 & WROOM-02U Datasheet v1.7](https://www.espressif.com/sites/default/files/documentation/esp32-c3-wroom-02_datasheet_en.pdf) — Espressif Systems, datasheet, §3.1 Pin Layout, Note A

## 原理图（schematic）

<a id="RF-SCH-001"></a>
#### RF-SCH-001 · 在天线馈点预留 π/T 匹配焊盘
`should` · 可信度 `high` · 适用: external_antenna, chip_antenna, pcb_antenna, discrete_rf

**规则** 天线阻抗未经实测时，在天线馈点前预留三元件 π（或 T）网络：串联位装 0 Ω（或隔直电容），并联位 DNP，以便日后实现任意拓扑； 匹配网络紧贴馈点，并使用厂商指定的天线到匹配网络的线长。

**依据** 塑料外壳、地平面尺寸、板材差异和周围元件都会改变天线阻抗，失配是链路预算里最大的损失之一；有 π 位就能事后调谐，没有就只能改板。

| 参数 | 判据 | 备注 |
|---|---|---|
| `matching_placeholder_positions` | == 3 count | π：并联-串联-并联；串联位默认 0 Ω，并联位默认不装。带不可访问馈点的板载天线模组不适用 |

**验证**
- `erc`（partial）· KiCad ERC + 自定义网表脚本 — 在天线馈点网络上存在 3 个相连的占位元件（并联、串联、并联），拓扑为 π；串联位已选 0 Ω 电阻，并联位标记 DNP。
- `bench`（manual）· VNA — 原型阶段用 VNA 测复阻抗后，按 RF-VER-003 填入实际值。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §12, §14.2
- [AN058 Antenna Selection Guide (SWRA161B)](https://www.ti.com/lit/pdf/swra161) — Texas Instruments, app_note, §3.4
- [AN-1811 Bluetooth Antenna Design (SNOA519B)](https://www.ti.com/lit/an/snoa519b/snoa519b.pdf) — Texas Instruments, app_note, §4.4 PI-Network Matching

<a id="RF-SCH-002"></a>
#### RF-SCH-002 · 射频器件用 C0G、高 Q、SRF 不低于 2 倍工作频率
`should` · 可信度 `high` · 适用: matching_network, filter, crystal_load, 2.4ghz

**规则** 匹配网络和晶振负载电容只用 C0G/NP0；匹配电感用高 Q 型；电容和电感的自谐振频率（SRF）都不低于工作频率的 2 倍； 2.4 GHz 下优先 0402/0201 以减小寄生，并优先采用厂商参考设计列出的料号。

**依据** 器件在接近 SRF 时电抗已偏离标称值；X7R 等介质随温度和偏压漂移会使匹配随温度变化；低 Q 器件会把射频能量变成热， 还会让 S11 看起来不错而实际传不过去。

| 参数 | 判据 | 备注 |
|---|---|---|
| `component_srf_over_operating_frequency` | >= 2 ratio | AN91445 §14.2：电容的串联谐振频率与电感的自谐振频率都至少是工作频率的 2 倍；2.4835 GHz 下即 >= 4.97 GHz |
| `matching_cap_dielectric` | qualitative | C0G/NP0；去耦电容不需要 C0G，可用 X5R/X7R |
| `esp32_c3_chip_matching_package` | qualitative | 封装为 0201（英制）。Espressif 要求 ESP32-C3 芯片射频匹配元件用 0201 封装（参考料号 GRM0335C1H1RXBA01D、LQP03TN2NXB02D）；JLC 经济档 SMT 下限 0402，用 0201 需标准档 |

**验证**
- `bom_check`（partial）· BOM 脚本 + 厂商 S 参数/SRF 数据 — 对射频网络上每个 C/L：介质为 C0G/NP0（电容），封装 0402/0201，SRF（取数据手册或厂商模型）>= 2 × f_max（f_max=2.4835 GHz 即 4.97 GHz）， 电感在 2.4 GHz 的 Q 值已核对。
- `spice`（partial）· ngspice .ac（元件按 ESL/ESR/并联电容建模）或 scikit-rf — 用元件寄生模型仿真匹配网络，查看 2.4 GHz 附近 S11/插入损耗，确认实际电抗与理想值偏差可接受。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §14.2, §21.1.1, §21.2, §21.2.1
- [ESP32-C3 Schematic Checklist - RF](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif Systems, vendor_guide, RF Tuning

<a id="RF-SCH-003"></a>
#### RF-SCH-003 · 射频线上可能有直流时串联隔直电容
`should` · 可信度 `high` · 适用: rf_switch, active_antenna, bias_tee

**规则** 在可能带直流的位置串联隔直电容：射频开关端口（除非数据手册声明端口可带直流）、有源天线偏置馈线、天线连接器。 已匹配的链路中，隔直电容选 SRF 接近工作频率、ESR 低的型号，使其不改变匹配。

**依据** 典型射频开关要求每个端口隔直或保证无直流；直流进入开关会偏置内部器件。电容在 SRF 处电抗近似为零， 因此 SRF 靠近工作频率的隔直电容对匹配影响最小。

| 参数 | 判据 | 备注 |
|---|---|---|
| `dc_block_cap_srf` | qualitative | SRF 接近工作频率；u-blox 双天线示例（1.575 GHz）用 47 pF 隔直，27 nH 射频扼流圈 + 100 nF 馈偏置（示例值，非通用） |

**验证**
- `erc`（partial）· KiCad ERC + 网表脚本 — 遍历 RF 网络上的开关端口、有源天线偏置点、连接器：每个端口与外部之间存在串联电容，或数据手册标明免隔直（记录在器件属性里）。
- `bom_check`（partial）· BOM 脚本 — 隔直电容的 SRF 取自厂商数据，位于 f_op 附近；ESR 低、C0G/NP0。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §21.1.1
- [GNSS antennas - RF design considerations for u-blox GNSS receivers (UBX-15030289 R03)](https://content.u-blox.com/sites/default/files/products/documents/GNSS-Antennas_AppNote_(UBX-15030289).pdf) — u-blox, app_note, §5.5 Dual antenna systems
- [Application Note 44: Introduction and Operation of the PE42020 True DC RF Switch](https://www.psemi.com/pdf/app_notes/an44.pdf) — pSemi, app_note, Safe DC Operating Range

<a id="RF-SCH-004"></a>
#### RF-SCH-004 · 差分射频口经与芯片匹配的巴伦接天线
`should` · 可信度 `high` · 适用: balun, differential_rf, ble, 802.15.4

**规则** 射频芯片差分口（RF_P/RF_N）必须经巴伦转为单端 50 Ω：优先用厂商参考设计的分立网络，或与该芯片匹配的集成巴伦-低通滤波器，并整体复制其布局； 不能复制时，RF_P、RF_N 到巴伦的走线必须对称、尽量短，宽度与长度尽量与参考设计一致。

**依据** 巴伦完成平衡/不平衡变换；走线不对称会降低输出功率并使谐波升高，布局对射频性能影响很大。

**验证**
- `netlist_diff`（partial）· 网表对比脚本（与厂商参考设计） — 巴伦及其匹配元件的料号、值、连接与参考设计一致。
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 测量 RF_P 与 RF_N 两条网络到巴伦焊盘的走线长度与宽度，两者差值 ≈ 0（容许值取参考设计），并与参考设计的长度/宽度比较。

**来源**
- [Impedance Matched RF Front End Differential Balun-Low Pass Filter for CC253X (2450BM15A0002)](https://www.johansontechnology.com/docs/2962/2450BM15A0002-App-Note-for-the-CC253X-11_7cXYuOj.pdf) — Johanson Technology, app_note, §3 Layout
- [AN058 Antenna Selection Guide (SWRA161B)](https://www.ti.com/lit/pdf/swra161) — Texas Instruments, app_note, §4 (balun for differential RF ports)

<a id="RF-SCH-005"></a>
#### RF-SCH-005 · 发射链路保留谐波滤波并用 S21/谐波实测验收
`should` · 可信度 `high` · 适用: transmitter, harmonic_filter, esp32-c3_chip

**规则** 发射链路里保留匹配网络（如 ESP32-C3 的 CLC、Nordic 的 π 网络）或低通/带通滤波器，用来抑制二、三次谐波，不要为省 BOM 删元件； 以厂商给的目标验收：ESP32-C3 芯片射频匹配调试时 S21 在 4.8 GHz 和 7.2 GHz 低于 -35 dB。

**依据** 发射机会产生基波、谐波和杂散；匹配网络除了阻抗变换，还承担谐波抑制，布局失配会令基波功率下降、杂散升高。 谐波必须满足 FCC 15.247(d) / EN 300 328 杂散限值。

| 参数 | 判据 | 备注 |
|---|---|---|
| `s21_at_4p8ghz` | < -35 dB | Espressif 调试 ESP32-C3 芯片射频匹配（端口 1 在芯片、端口 2 在天线）的目标 |
| `s21_at_7p2ghz` | < -35 dB | 同上；另 S11 应接近芯片共轭点 35+j0 |

**验证**
- `bench`（manual）· VNA（S11/S21 测匹配网络两端）+ 频谱仪 — 把 VNA 两端接匹配网络芯片侧和天线侧，S21 在 4.8/7.2 GHz < -35 dB；整机在传导口测二/三次谐波，低于限值并留余量。
- `spice`（partial）· ngspice .ac / scikit-rf — 仿真匹配网络（含元件寄生）的 S21，在 2×、3× 基频处 < -35 dB（仅适用 ESP32-C3；其他芯片用其目标值）。

**来源**
- [ESP32-C3 Schematic Checklist - RF Tuning](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif Systems, vendor_guide, RF Circuit, RF Tuning
- [PCB Layout Design Guide (EFR32 Wireless Gecko)](https://github.com/SiliconLabs/IoT-Developer-Boot-Camp/wiki/PCB-Layout-Design-Guide) — Silicon Labs, vendor_guide, §2.1.1 Function of RF matching and filtering network
- [AN1406 SKY65111-348LF Amplifier Layout Optimization](https://www.skyworksinc.com/-/media/FD49CA4742354582B6E9F1CB74976A01.pdf) — Skyworks, app_note, 915 MHz Harmonic Filter
- [General PCB design guidelines for nRF52 series](https://devzone.nordicsemi.com/guides/hardware-design-test-and-measuring/b/nrf5x/posts/general-pcb-design-guidelines-for-nrf52-series) — Nordic Semiconductor, vendor_guide, Matching network

<a id="RF-SCH-006"></a>
#### RF-SCH-006 · 射频电源脚分级去耦并串 LC 隔离
`should` · 可信度 `high` · 适用: rf_ic, lna, pa, esp32-c3_chip

**规则** 射频 IC/LNA/PA 的电源脚做分级去耦：小值（高 SRF）电容负责高频，0.1 µF 左右滤时钟杂散，大电容供发射瞬时电流并滤开关电源的低频干扰； 射频电源脚前加 LC/CLC 滤波抑制高频谐波回灌（ESP32-C3 的 VDD3P3：10 µF + 0.1 µF，电感额定电流 >= 500 mA）； PA 偏置经射频扼流圈馈入，多只旁路电容紧贴扼流圈。

**依据** 电源噪声会抬高频率合成器相位噪声、使射频输出不稳并造成杂散，接收时增加误包率；发射瞬间的电流尖峰会拉塌电源轨。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esp32_c3_vdd3p3_bulk_cap` | >= 10 uF | 与 0.1 µF 并用；如电源入口靠近 VDD3P3 可与入口 10 µF 合并 |
| `esp32_c3_vdd3p3_lc_inductor_rated_current` | >= 500 mA | Espressif 建议的 LC 滤波电感额定电流 |
| `inrush_cap_formula` | qualitative | C = I / (dV/dt)；例：20 mA、15 µs、允许跌落 300 mV 需 1 µF（AN91445 §19） |

**验证**
- `bom_check`（partial）· BOM + 原理图脚本 — 每个射频电源脚都有对应的 LC/CLC 滤波与规定值的去耦电容；电感额定电流 >= 厂商要求。
- `pi_sim`（partial）· ngspice AC（电源路径含电容 ESL/ESR/SRF 模型） — 在射频电源脚处看阻抗-频率曲线，关注时钟谐波与开关频率附近无反谐振峰，高频段阻抗足够低。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §19 Power Supply Decoupling, §21.1.1
- [ESP32-C3 Schematic Checklist - Power Supply](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif Systems, vendor_guide, Analog Power Supply
- [AN1406 SKY65111-348LF Amplifier Layout Optimization](https://www.skyworksinc.com/-/media/FD49CA4742354582B6E9F1CB74976A01.pdf) — Skyworks, app_note, VCC1/VCC2/VCC3 pin descriptions
- [PCB Layout Design Guide (EFR32 Wireless Gecko)](https://github.com/SiliconLabs/IoT-Developer-Boot-Camp/wiki/PCB-Layout-Design-Guide) — Silicon Labs, vendor_guide, §2.1.2 Function of VDD filterings

<a id="RF-SCH-007"></a>
#### RF-SCH-007 · 模组 3V3 脚旁放 10 µF + 0.1 µF，扛住发射电流尖峰
`should` · 可信度 `high` · 适用: esp32-c3-wroom-02, ldo_ams1117, wifi_tx · 标签: cat-feeder

**规则** ESP32-C3-WROOM-02 的 3V3 脚旁放 10 µF（C1）和 0.1 µF（C2），LDO 到模组的路径短而宽； Wi-Fi 发射瞬间 3V3 必须保持在 3.0-3.6 V，不得跌出。

**依据** 发射时的电流尖峰会拉塌电源轨，导致射频性能变差或复位；模组 802.11b 1 Mbps、20.5 dBm 时峰值电流 345 mA。

| 参数 | 判据 | 备注 |
|---|---|---|
| `module_supply_bulk_cap` | >= 10 uF | Datasheet Figure 9-1 的 C1 |
| `module_supply_hf_cap` | >= 0.1 uF | Datasheet Figure 9-1 的 C2 |
| `module_supply_range` | 3.0 … 3.6 V | Datasheet Table 6-2 推荐工作条件，典型 3.3 V |
| `wifi_tx_peak_current` | == 345 mA | Datasheet Table 6-4，802.11b 1 Mbps @20.5 dBm，100% 占空比 |

**验证**
- `spice`（partial）· ngspice 瞬态（LDO 模型 + 去耦 + 345 mA 阶跃） — 在模组 3V3 引脚处最小电压 >= 3.0 V（含 LDO 瞬态响应与输出电容 ESR）。
- `bench`（manual）· 示波器（AC 耦合 + 直流电压同测） — Wi-Fi 持续发射时抓模组 3V3 引脚波形，最低电压 >= 3.0 V，无复位。

**来源**
- [ESP32-C3-WROOM-02 & WROOM-02U Datasheet v1.7](https://www.espressif.com/sites/default/files/documentation/esp32-c3-wroom-02_datasheet_en.pdf) — Espressif Systems, datasheet, §6.2, §6.4.1 Table 6-4, §9 Figure 9-1
- [ESP32-C3 Schematic Checklist - Power Supply](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif Systems, vendor_guide, Analog Power Supply

<a id="RF-SCH-008"></a>
#### RF-SCH-008 · 预留传导测试口，射频线上不加探针测试点
`should` · 可信度 `high` · 适用: discrete_rf, certification

**规则** 分立射频设计在射频链路上预留可选的 U.FL/SMA 或 0 Ω 切换点用于传导功率、杂散和匹配测试，量产可不贴； 分支处布线要使断开任一支路时另一支路不成为短截线；不要在射频走线上放探针测试点。

**依据** 射频无法用 ICT 测试；测试点和断开后的分支都是短截线，会影响阻抗匹配。传导测试口可兼用于验证匹配网络。

**验证**
- `review`（manual）· 原理图评审 — 射频链路上有明确的传导测试位置（连接器或 0 Ω），且标明「断开后另一支路无短截线」；没有测试点封装连在射频网络上。
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — RF 网络上不存在 TestPoint 类封装的焊盘；分支段（非链路主线）长度 <= 参考设计允许值。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §16.3, §22 Design for Testability
- [ESP32-C3 Schematic Checklist - RF](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif Systems, vendor_guide, RF Circuit (RF with no antenna)

## 网表与约束（netlist）

<a id="RF-NET-001"></a>
#### RF-NET-001 · 射频网络单独设网络类，线宽恒定、不分支
`should` · 可信度 `medium` · 适用: rf_trace, 50ohm

**规则** 把天线馈线与芯片 RF 引脚到匹配网络的网络设为独立 net class，线宽（CPWG 时还有间隙）取阻抗计算值； 网络只连接匹配、隔直、滤波元件与天线/连接器，不做 T 型分支；用 .kicad_dru 自定义规则锁定线宽。

**依据** 特性阻抗必须全程恒定，分支和宽度变化是不连续点；把约束写进设计规则可让 DRC 自动检出。

| 参数 | 判据 | 备注 |
|---|---|---|
| `rf_trace_target_z0` | == 50 ohm | Espressif、Infineon、Nordic 均要求 50 Ω 射频线 |

**验证**
- `drc`（full）· KiCad DRC + .kicad_dru — 自定义规则：(rule rf_width (condition "A.NetClass == 'RF'") (constraint track_width (min W) (max W)))，W 取 tline_calc 结果； 另加 clearance 规则锁定 CPWG 间隙。DRC 违例数为 0。
- `netlist_diff`（partial）· 网表脚本 — RF 网络上的 pad 数 <= 预期（两端 + 匹配/隔直/滤波元件）；不存在分支到其他网络的连接。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §16.3
- [ESP32-C3 PCB Layout Design - RF Trace](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif Systems, vendor_guide, RF / RF Trace

## 叠层与规则（stackup）

<a id="RF-STK-001"></a>
#### RF-STK-001 · 用板厂实际叠层算 50 Ω 线宽，并接受 Dk 与阻抗公差
`should` · 可信度 `high` · 适用: microstrip, cpwg, fr4, jlcpcb

**规则** 射频线宽必须用板厂提供的实际叠层（线到参考层的介质厚度、Dk、铜厚、阻焊）计算，换板厂或换叠层即重算； FR-4 的 Dk 与阻抗公差不可靠，要靠匹配网络预留位与实测调谐兜底，不要依赖 50 Ω 的绝对精度。 线到参考层越薄，50 Ω 线越窄；双层 > 0.8 mm 的板线很宽，且宽线易激发寄生模式。

**依据** 线宽与介质厚度成正比；板厂的 Dk 是按实际工艺推导的值而非树脂原始数据；JLCPCB 免费标准阻抗测试公差为 ±20%。

| 参数 | 判据 | 备注 |
|---|---|---|
| `jlcpcb_prepreg_7628_dk` | == 4.4 dimensionless | JLCPCB 阻抗页；3313=4.1、1080=3.91、2116=4.16；芯板 4.6；阻焊 3.8（厚度 0.6-1.2 mil） |
| `jlcpcb_core_dk` | == 4.6 dimensionless |  |
| `fr4_dk_used_in_infineon_table` | == 4.3 dimensionless | AN91445 Table 2 使用 4.3，另见 JLCPCB 4.4/4.6；不同来源差 5% 以上，印证必须用板厂值 |
| `jlcpcb_standard_impedance_tolerance` | == 20 % | 免费标准阻抗测试公差 ±20%，精密测试收费 |
| `two_layer_thick_board_threshold` | > 0.8 mm | AN91445 §17.2：双层板超过 0.8 mm 时射频线显著变宽 |

**验证**
- `tline_calc`（partial）· KiCad PCB Calculator（TransLine：Microstrip / Coplanar waveguide with ground plane） — 用板厂 H、εr、铜厚、阻焊输入，求 50 Ω 的 W（和 CPWG 的 G）；与布局线宽一致。 自行核算（Hammerstad-Jensen，不含阻焊与铜厚修正）：双层 1.6 mm（H≈1.5 mm、εr 4.4）微带约 2.9 mm； JLC04161H-7628 四层顶层相对 L2（H=0.2104 mm、εr 4.4）约 0.40 mm；εr ±5% 时 Z0 变化约 ±1.2 Ω。
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 读取 .kicad_pcb 的叠层设置，介质厚度/Dk 与板厂叠层表一致；RF 线宽等于上一步计算值。

**来源分歧** Dk 取值：Infineon 表用 4.3，JLCPCB 公布预浸料 4.4、芯板 4.6，通用资料给 4.0-4.8。取舍：只采用拟投板厂公布的值， 且 JLCPCB 说明其 Dk 是按实际工艺推导的。

**来源**
- [Controlled Impedance PCB Layer Stackup](https://jlcpcb.com/impedance) — JLCPCB, vendor_guide
- [Multi-Layer PCB Standard Laminated Structures](https://jlcpcb.com/help/article/multi-layer-pcb-standard-laminated-structures) — JLCPCB, vendor_guide, impedance tolerance, key reminders
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §7.2 Table 2, §17.1, §17.2

<a id="RF-STK-002"></a>
#### RF-STK-002 · 50 Ω 馈线优先用带地共面波导（CPWG）
`should` · 可信度 `high` · 适用: cpwg, 50ohm, fr4

**规则** 介质较厚（如 1.6 mm 双层板）或线上要并联接地元件时，用带底层地的共面波导而非纯微带：线两侧同层铺地、间隙恒定， 顶层两侧地之间的间距小于介质厚度 H（否则退化为微带），两侧地铜宽度大于该间距，并用接地过孔缝合到底层地。

**依据** CPWG 隔离更好、EMI 更低、串扰更小，也便于并联元件接地；同时线宽和间隙两个自由度可补偿叠层厚度偏差，降低对板厚波动的敏感度。

| 参数 | 判据 | 备注 |
|---|---|---|
| `cpwg_ground_to_ground_spacing_over_height` | < 1 ratio | AN91445 §16.3：顶层两侧地之间的间距须小于介质厚度 H，否则主要表现为微带 |

**验证**
- `tline_calc`（full）· KiCad PCB Calculator（Coplanar waveguide with ground plane）或 AppCAD — 输入板厂叠层，求 50 Ω 的 W、G；检查 (W + 2G) < H。
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 沿射频线逐段测与同层地铜的间隙：全程恒定（无渐变），两侧地铜宽度均大于 (W + 2G)。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §16.1-16.3
- [PCB Layout Design Guide (EFR32 Wireless Gecko)](https://github.com/SiliconLabs/IoT-Developer-Boot-Camp/wiki/PCB-Layout-Design-Guide) — Silicon Labs, vendor_guide, §3.1, §3.5
- [KiCad PCB Calculator](https://docs.kicad.org/5.1/en/pcb_calculator/pcb_calculator.html) — KiCad, tool_doc, TransLine

<a id="RF-STK-003"></a>
#### RF-STK-003 · 分立射频优先 4 层；2 层板底层须为整块实心地
`should` · 可信度 `high` · 适用: discrete_rf, module_baseboard, 2-layer · 标签: cat-feeder

**规则** 分立射频 IC 设计优先 4 层：L1 射频与元件，L2 完整地平面（射频区不走线），L3 电源，L4 非射频； 用 2 层时板尽量薄，射频、元件、电源线都在顶层，底层为整块实心地（至少覆盖整个射频区），底层不放元件、少走线。

**依据** 射频信号的返回电流在线正下方的地平面里；地平面不完整就绕行成环路，增加电感、破坏匹配并加大泄漏。

| 参数 | 判据 | 备注 |
|---|---|---|
| `two_layer_board_max_thickness_preferred` | <= 0.8 mm | AN91445 §17.2：双层板应尽量薄；超过 0.8 mm 线宽显著增大。JLC 常用 1.6 mm 时改用 CPWG（RF-STK-002） |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 双层板：沿每段射频线及射频 IC/匹配网络投影采样，底层同位置必须有 GND 铜（无间断、无信号线）；四层板：L2 在射频区无切割、无走线。
- `review`（manual）· 叠层评审 — 确认叠层与厂商参考设计一致（层数、参考层、板厚）。

**来源分歧** Infineon 称射频设计强烈推荐 4 层，Espressif 同样首推 4 层但给出可行的 2 层方案（底层整块地、无元件、少走线）。 取舍：分立射频 IC 首选 4 层；以模组为主且主板无射频走线的 2 层板（如猫食机）可接受，前提是遵守模组禁布与地平面要求。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §17.1, §17.2, §18
- [ESP32-C3 PCB Layout Design - General Principles of PCB Layout for the Chip](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif Systems, vendor_guide, General Principles of PCB Layout for the Chip

## 分区规划（floorplan）

<a id="RF-FLR-001"></a>
#### RF-FLR-001 · 天线放板边或板角，馈点贴近板边，辐射部分悬出板外
`must` · 可信度 `high` · 适用: module_antenna, pcb_antenna, esp32-c3-wroom-02 · 标签: cat-feeder

**规则** 带板载 PCB 天线的模组，天线部分放在底板之外（悬出板边），馈点尽量贴近板边；天线无法悬出时馈点仍贴近板边， 并把底板在天线两侧和下方挖空形成净空；不要把模组放在板中央、四周都挖空。分立 PCB 天线放在板角，与其余电路保持净空。

**依据** 底板的铜和板材会改变天线的电容负载和辐射；放在板边/角能让辐射区尽量远离底板，并保留馈点附近的地。

| 参数 | 判据 | 备注 |
|---|---|---|
| `module_position` | qualitative | 边缘或角落；Murata 对其模组称角落最佳、边缘中点不推荐 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python)，参见 ee-pcb-verify 的 geometry 检查器 — 取模组天线区（keepout rule area）外包框与 Edge.Cuts 比较：天线区至少一边悬出或贴近板边；天线区中心到最近板边的距离小于到板中心的距离； 天线区其余三侧无底板（cutout）或为 keepout。尺寸以 Espressif 图 "Keepout Zone for ESP32-C3 Module's Antenna" 为准： 天线区高 6 mm（模组宽 18 mm），其左、右、上方的净空区各 >= 15 mm（图中 Min15；即约 48 x 21 mm 的净空区，其内底板挖空）； 猫食机板自己的禁布区取值须按此图核对（其仓库契约中的数值未在本库核实）。
- `review`（manual）· 对照 Espressif 模组放置示意图 — 对照 Hardware Design Guidelines 中「Placement of ESP32-C3 Modules on Base Board」图，确认属于推荐位置。

**来源**
- [ESP32-C3 PCB Layout Design - General Principles of PCB Layout for Modules](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif Systems, vendor_guide, Positioning a Module on a Base Board
- [MBN52832 BLE Module Layout Guide](https://www.murata.com/-/media/webrenewal/products/connectivitymodule/asset/pub/rfm/data/mbn52832_antenna_layout_guide.ashx?la=en&cvid=20210615064716000000) — Murata, vendor_guide, Module location on the PCB
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §12

<a id="RF-FLR-002"></a>
#### RF-FLR-002 · 天线禁布区内所有铜层禁铜、禁线、禁件、禁螺丝
`must` · 可信度 `high` · 适用: pcb_antenna, chip_antenna, module_antenna · 标签: cat-feeder

**规则** 厂商图纸规定的天线禁布区内，所有铜层都不得有地、电源、走线、过孔、焊盘、元件、安装螺丝或其他导体； 禁布区几何必须与天线数据手册一致，不得缩小。

**依据** 近场内的任何导体都会使天线失谐或吸收辐射；偏离数据手册的禁布区会让性能不可预测、效率降低。

| 参数 | 判据 | 备注 |
|---|---|---|
| `keepout_copper_layers` | qualitative | 全部铜层，含内层 |
| `murata_mbn52832_ground_clearance_min` | >= 3.3 mm | 仅 Murata MBN52832 模组：地平面到天线区 >= 3.3 mm；其他天线按其数据手册 |

**验证**
- `drc`（full）· KiCad DRC（天线封装的 keepout rule area） — keepout 违例数为 0。
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 取禁布区多边形（含悬出板外部分），遍历所有层的 track、via、zone 填充、pad、封装 courtyard，与多边形相交的数量为 0（天线自身焊盘除外）； 并检查螺丝孔/定位柱坐标。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §12
- [Chip Antenna Layout Considerations for BLE, 802.11, and 2.4G Zigbee](https://www.johansontechnology.com/tech-notes/chip-antenna-layout-considerations-for-ble-80211-and-24g-zigbee/) — Johanson Technology, app_note
- [MBN52832 BLE Module Layout Guide](https://www.murata.com/-/media/webrenewal/products/connectivitymodule/asset/pub/rfm/data/mbn52832_antenna_layout_guide.ashx?la=en&cvid=20210615064716000000) — Murata, vendor_guide, On-board antenna instruction
- [AN11994 QN908x BLE Antenna Design Guide](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/wireless-connectivity/17607/1/BLE_Antenna_Design_AN11994.pdf) — NXP, app_note, §3.2 Placement and PCB layout

<a id="RF-FLR-003"></a>
#### RF-FLR-003 · 外壳内天线周围留净空，金属件远离天线
`should` · 可信度 `high` · 适用: pcb_antenna, enclosure, esp32-c3-wroom-02 · 标签: cat-feeder

**规则** 产品外壳内，PCB 天线四周各方向至少留 15 mm 净空（Espressif 建议）；塑料外壳、电池、连接器、螺丝、屏蔽罩、电机等越远越好。 塑料外壳会使谐振频率向低端移约 100-200 MHz，因此必须在最终外壳内复测。

**依据** 近场内的塑料（Dk 高于空气）增大天线有效电长度，金属则吸收或反射；二者都使天线失谐、效率下降。

| 参数 | 判据 | 备注 |
|---|---|---|
| `housing_clearance_all_directions` | >= 15 mm | Espressif：外壳内 PCB 天线各方向至少 15 mm |
| `murata_plastic_to_module_distance` | > 3 mm | Murata MBN52832 模组：塑料/金属离模组 > 3 mm |
| `murata_metal_to_antenna_distance` | >= 5 mm | Murata：连接器、电池等金属件离天线区 >= 5 mm |
| `taoglas_pa25_metal_clearance` | >= 20 mm | 仅 Taoglas PA.25 芯片 PIFA：离金属件 20 mm，离外壳 1-2 mm 合理 |
| `plastic_resonance_shift` | -200 … -100 MHz | AN91445 §11.2：塑料外壳使谐振频率下移约 100-200 MHz |

**验证**
- `review`（partial）· 3D 机壳 STEP + 板 STEP 的距离检查 — 在 MCAD 里测天线禁布区到外壳内壁、金属件（电机、螺丝、料盒、称重传感器）的最小距离，>= 15 mm 或天线厂商值。
- `bench`（manual）· VNA — 装入最终外壳后复测 S11（含手持或实际放置），中心频率偏移不超过带宽余量（见 RF-VER-002）。

**来源分歧** 净空数字因天线而异：Espressif 15 mm（板载 PCB 天线）、Murata 金属 >= 5 mm / 塑料 > 3 mm、Taoglas PA.25 金属 >= 20 mm。 取舍：用所选天线厂商的数值；没有厂商值时，对 ESP32-C3 板载天线取 15 mm。

**来源**
- [ESP32-C3 PCB Layout Design - Positioning a Module on a Base Board](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif Systems, vendor_guide
- [MBN52832 BLE Module Layout Guide](https://www.murata.com/-/media/webrenewal/products/connectivitymodule/asset/pub/rfm/data/mbn52832_antenna_layout_guide.ashx?la=en&cvid=20210615064716000000) — Murata, vendor_guide, Other suggestions
- [Application Note for PA.25.A Antenna Integration (APN-11-8-002)](https://www.taoglas.com/assets/application-notes/APN-11-8-002.C.pdf) — Taoglas, app_note, §10 Electromagnetic environment
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §11.2, §12

<a id="RF-FLR-004"></a>
#### RF-FLR-004 · 天线远离晶振、高速时钟、开关电源、电机以及 USB/UART
`should` · 可信度 `medium` · 适用: antenna, uart, usb, clock · 标签: cat-feeder

**规则** PCB 天线远离高频器件（晶振、DDR、高速时钟）；USB 口、USB 转串口芯片和 UART 线（走线、过孔、测试点、排针）尽量远离天线， UART 线周围包地并打地过孔；开关电源电感、电机和显示屏同样要拉开或屏蔽。

**依据** 数字边沿的谐波可达数 GHz，会耦合进天线抬高接收底噪（desense）；UART 走线穿过射频线或靠近天线会影响接收。

| 参数 | 判据 | 备注 |
|---|---|---|
| `distance_to_antenna_keepout` | maximize | Espressif/u-blox 均无具体数值，只要求尽量远；开关电源与电机属按同一机理的外推（medium） |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 列出 UART/USB 连接器与排针、测试点、晶振、DC-DC 电感、电机驱动 MOSFET 到天线禁布区的最近距离；这些元件须位于远离天线的一侧，报告距离供评审。
- `emc_precompliance`（manual）· 近场探头 + 频谱仪 — TX 关闭时在天线附近 2.4 GHz 频段扫描噪声，噪声源开关前后底噪差异应可忽略。
- `bench`（manual）· 接收灵敏度/PER 测试 — 分别在电机、UART、USB 工作与关闭时测 RSSI/误包率，差异应不显著。

**来源**
- [ESP32-C3 PCB Layout Design - RF / UART and USB Near the Antenna](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif Systems, vendor_guide
- [GNSS antennas - RF design considerations for u-blox GNSS receivers (UBX-15030289 R03)](https://content.u-blox.com/sites/default/files/products/documents/GNSS-Antennas_AppNote_(UBX-15030289).pdf) — u-blox, app_note, §6.1-6.2 Eliminating digital noise sources
- [Understanding Chip Antennas Handbook](https://www.johansontechnology.com/docs/4469/johanson-understanding-chip-antennas-handbook.pdf) — Johanson Technology, vendor_guide, Causes of Variation From Spec

<a id="RF-FLR-005"></a>
#### RF-FLR-005 · 单极类天线按厂商参考板提供足够的地平面
`should` · 可信度 `high` · 适用: monopole, mifa, pifa, chip_antenna, esp32-c3-wroom-02 · 标签: cat-feeder

**规则** 1/4 波长单极、IFA/MIFA、PIFA 和芯片天线都把板子的地当作天线的一部分，地平面尺寸/形状要与厂商参考板一致； 地平面太小会改变谐振频率和方向图并降低效率；在天线馈点附近的底板上放足够的地铜和密集接地过孔。

**依据** 更大的地平面增大有效电容并使谐振频率下移；良好的地使回波损耗更接近理论值；地平面形状还改变辐射方向图。

| 参数 | 判据 | 备注 |
|---|---|---|
| `murata_host_pcb_length_min` | > 40 mm | Murata MBN52832：主板长度 > 40 mm 才能得到最佳性能，50x50 mm 以上为佳；仅适用该模组 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 计算连通 GND 铜外包尺寸，达到厂商参考板的尺寸（猫食机板 66x60 mm）；天线馈点附近的地铜有密集接地过孔。
- `em_sim`（partial）· openEMS — 扫描地平面长度/宽度，观察 S11 谐振频率和效率变化。

**来源**
- [AN058 Antenna Selection Guide (SWRA161B)](https://www.ti.com/lit/pdf/swra161) — Texas Instruments, app_note, §5.1.2 Ground Effects
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §11.1
- [MBN52832 BLE Module Layout Guide](https://www.murata.com/-/media/webrenewal/products/connectivitymodule/asset/pub/rfm/data/mbn52832_antenna_layout_guide.ashx?la=en&cvid=20210615064716000000) — Murata, vendor_guide, Size of PCB
- [ESP32-C3 PCB Layout Design - Positioning a Module on a Base Board](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif Systems, vendor_guide

<a id="RF-FLR-006"></a>
#### RF-FLR-006 · 多天线或收发之间拉开距离、正交放置
`consider` · 可信度 `high` · 适用: coexistence, multi_antenna, gnss, ble, wifi

**规则** 同板有多个无线电（BLE + Wi-Fi、GNSS + 蜂窝）时，天线尽量远离；线极化天线使其电正交放置、零点方向共线； 两射频区之间打接地过孔隔离墙。GNSS 与 GSM 天线之间的隔离应 >= 40 dB，手持设备靠摆位只能做到约 20 dB，需另加 SAW 滤波器。

**依据** 发射机会以足以阻塞相邻接收机的功率耦合到另一天线，隔离度不足需靠空间、极化和频率分隔补救。

| 参数 | 判据 | 备注 |
|---|---|---|
| `gnss_gsm_antenna_isolation` | >= 40 dB | u-blox §5.4.1；手持设备靠摆位约 20 dB 不够 |

**验证**
- `em_sim`（partial）· openEMS 或 2.5D 求解器 — 两天线端口间 |S21| 在目标频段内满足隔离要求（GNSS-GSM >= 40 dB）。
- `bench`（manual）· VNA 双端口 — 实测两天线端口间 S21，在整机状态下满足要求。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §24.1 Spatial Isolation
- [GNSS antennas - RF design considerations for u-blox GNSS receivers (UBX-15030289 R03)](https://content.u-blox.com/sites/default/files/products/documents/GNSS-Antennas_AppNote_(UBX-15030289).pdf) — u-blox, app_note, §5.4.1 Isolation between GNSS and GSM antenna

## 器件布局（placement）

<a id="RF-PLC-001"></a>
#### RF-PLC-001 · 匹配网络紧贴芯片 RF 脚和天线馈点，元件相互靠近
`should` · 可信度 `high` · 适用: matching_network, rf_ic, antenna_feed

**规则** 芯片侧匹配网络靠近芯片 RF 引脚，第一个元件离引脚尽量近，网络内元件相互靠近（相邻元件用焊盘宽度连线）； 天线侧匹配网络靠近天线馈点。ESP32-C3 芯片要求 CLC 用 0201、按之字形放置，两个电容不朝同一方向。

**依据** 各自把一端匹配到 50 Ω 后，两个网络之间的 50 Ω 线长不再影响匹配值；元件间距和走线长度引入的寄生电感/电容会使匹配失谐。

| 参数 | 判据 | 备注 |
|---|---|---|
| `first_matching_component_distance_to_rf_pin` | minimize | Silicon Labs：第一个元件尽量靠近 RF 引脚，以降低串联寄生电感 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python)，参见 ee-pcb-verify 的 geometry 检查器 — 对 RF 网络上每个匹配元件，取焊盘中心到 RF 引脚（或天线馈点）的距离，按网络顺序递增； 第一个元件焊盘间隙为封装允许的最小值；距离与厂商参考设计的对应值对比，偏差由评审确认。
- `review`（manual）· 对照厂商参考布局图 — 确认元件朝向（之字形）、与参考布局一致。

**来源**
- [PCB Layout Design Guide (EFR32 Wireless Gecko)](https://github.com/SiliconLabs/IoT-Developer-Boot-Camp/wiki/PCB-Layout-Design-Guide) — Silicon Labs, vendor_guide, §3.1 2.4 GHz matching network
- [ESP32-C3 PCB Layout Design - RF Matching Network](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif Systems, vendor_guide, RF / RF Matching Network
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §14
- [AN11994 QN908x BLE Antenna Design Guide](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/wireless-connectivity/17607/1/BLE_Antenna_Design_AN11994.pdf) — NXP, app_note, §3.2

<a id="RF-PLC-002"></a>
#### RF-PLC-002 · 射频电源脚去耦：小值最近、同层、各自接地过孔
`should` · 可信度 `high` · 适用: rf_ic, lna, pa, decoupling

**规则** 去耦电容与 IC 同层，最小值电容离电源脚最近；供电电流先经电容再进引脚，避免电源过孔夹在电容与引脚之间； 每个去耦电容的接地用独立过孔、不共用；接地脚走线加粗并紧贴过孔。

**依据** 最小值电容的有效频段最高，必须最先看到引脚；过孔和走线的寄生电感会抵消电容的高频效果。

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 对每个射频电源脚找出所有去耦电容：按容值升序，到引脚的距离应不递减；电容与 IC 同层； 每个电容 GND 焊盘最近的 GND 过孔仅连接 1 个元件焊盘（无共用）。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §19.1
- [PCB Layout Design Guide (EFR32 Wireless Gecko)](https://github.com/SiliconLabs/IoT-Developer-Boot-Camp/wiki/PCB-Layout-Design-Guide) — Silicon Labs, vendor_guide, §3.4, §3.5

## 布线（routing）

<a id="RF-RTE-001"></a>
#### RF-RTE-001 · 射频线按 50 Ω 设计，线宽（及间隙）全程恒定
`must` · 可信度 `high` · 适用: rf_trace, microstrip, cpwg

**规则** 射频走线位于外层，50 Ω 特性阻抗，线宽恒定（CPWG 时间隙也恒定），不分支；仅天线馈点前极短一段（约 3 mm）可放宽线宽， 但线宽须与天线馈点一致；约 1 cm 以上的馈线应按传输线（宽度 W）设计（Infineon 的措辞是推荐）。

**依据** 特性阻抗不连续处会产生反射；传输线越长，对阻抗恒定性的要求越高。

| 参数 | 判据 | 备注 |
|---|---|---|
| `rf_trace_z0` | == 50 ohm |  |
| `short_feed_width_exempt_length` | <= 3 mm | AN91445 §7.2：约 3 mm 的天线馈入线宽度要求可放宽，但须与天线馈点宽度一致 |
| `long_feed_must_be_transmission_line` | >= 10 mm | AN91445 §7.2：约 1 cm 的馈线推荐用特定宽度 W 的传输线布局 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 遍历射频网络的 track 段，线宽集合大小为 1（焊盘过渡除外），等于 tline_calc 的 W；CPWG 时测与同层地铜的间隙恒定。
- `drc`（full）· KiCad DRC + .kicad_dru（见 RF-NET-001） — track_width 规则违例数为 0。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §7.2, §16.3
- [ESP32-C3 PCB Layout Design - RF Trace](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif Systems, vendor_guide, RF / RF Trace

<a id="RF-RTE-005"></a>
#### RF-RTE-005 · 射频线下方参考地完整，其他走线不穿越、不并行靠近
`must` · 可信度 `high` · 适用: rf_trace, ground_return

**规则** 射频线正下方（相邻层）的地平面完整无切割，不允许任何信号线从射频线下方穿过；同层不要有高频或其他信号线紧邻并行； 射频线两侧的返回路径要宽。

**依据** 射频返回电流沿线正下方的地平面走；地被打断时电流绕行形成环路，增加电感、破坏匹配并增强泄漏和耦合。

| 参数 | 判据 | 备注 |
|---|---|---|
| `other_signals_under_rf_trace` | == 0 count | 相邻层射频线投影下的非地走线数量 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 沿射频线以固定步长采样：参考层每个采样点下都有 GND 铜；相邻铜层不存在非 GND 的 track/via/pad 穿过射频线投影； 同层最近的非 GND 走线间距报告出来评审（无出处数值，常用经验为线宽的 3 倍以上）。
- `drc`（partial）· KiCad DRC + .kicad_dru — 自定义 clearance 规则：RF 网络与其他网络（非 GND）的间距 >= 评审确定的值。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §16.3, §18
- [ESP32-C3 PCB Layout Design - RF Trace](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif Systems, vendor_guide, RF / RF Trace
- [General PCB design guidelines for nRF52 series](https://devzone.nordicsemi.com/guides/hardware-design-test-and-measuring/b/nrf5x/posts/general-pcb-design-guidelines-for-nrf52-series) — Nordic Semiconductor, vendor_guide, RF trace, Keep-out

<a id="RF-RTE-002"></a>
#### RF-RTE-002 · 射频线尽量短，无短截线、分支和测试点
`should` · 可信度 `high` · 适用: rf_trace, shunt_component, stub

**规则** 射频路径取最短；不留开路短截线、T 型分支或探针测试点；并联元件直接放在射频走线上，不要用长线引出再接， 除非参考设计明确要求（如 ESP32-C3 芯片侧接地电容上用于抑制二次谐波的 15 mil/100 Ω 短截线，0402 及更大封装不需要）。

**依据** 走线和基板对信号的衰减与长度成正比；短截线呈电抗性，破坏匹配；参考设计中的短截线是刻意设计，不可随意添加或删除。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esp32_c3_harmonic_stub_length` | == 15 mil | 仅 ESP32-C3 芯片：芯片侧接地电容焊盘上的短截线，宽度使其 Z0 = 100 Ω ±10%，其下方第二层需清空 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — RF 网络必须是链状拓扑：每个节点只连接链中相邻两个焊盘和至多一个并联元件；分支长度（非主链 track）为 0；无 TestPoint 封装挂在 RF 网络上。
- `review`（manual）· 对照参考设计 — 参考设计里的刻意短截线保留，其他短截线不得存在。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §14.2, §16.3
- [ESP32-C3 PCB Layout Design - RF Matching Network / Stub](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif Systems, vendor_guide, RF

<a id="RF-RTE-003"></a>
#### RF-RTE-003 · 射频线拐弯用圆弧或 135° 折线，不画未切角的直角
`should` · 可信度 `high` · 适用: rf_trace

**规则** 射频线尽量不拐弯；必须拐弯时用圆弧、两个 45°（内角 135°）或按公式切角的直角，保持线宽一致，避免锐角和未切角的 90° 拐角。

**依据** 拐角处局部线宽变化造成阻抗不连续；圆弧和切角保持有效宽度连续。

| 参数 | 判据 | 备注 |
|---|---|---|
| `rf_bend_interior_angle` | >= 135 deg | Espressif：使用 135° 弯折或圆弧；Nordic 论坛回答建议两个 45° 代替 90° |
| `mitre_width_formula` | qualitative | AN91445 Fig.51：M = W*(1.04 + 1.3*exp(-1.35*W/H))，W 为线宽、H 为介质厚度 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 遍历射频 track 相邻线段，转角 <= 45°（内角 >= 135°）；圆弧段用多段近似，每段转角 <= 45°。

**来源分歧** 流传的「90° 拐角一定有害」没有量化出处；三份来源（Espressif、Infineon、Nordic）都只建议用圆弧/135°/切角，未给出 2.4 GHz 下直角的量化影响。 取舍：按「避免未切角直角」作为 should，而不是 must。

**来源**
- [ESP32-C3 PCB Layout Design - RF Trace](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif Systems, vendor_guide, RF / RF Trace
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §16.3, Figure 51
- [nRF52 antenna design review (Nordic DevZone Q&A)](https://devzone.nordicsemi.com/f/nordic-q-a/16740/nrf52-antenna-design-review) — Nordic Semiconductor, forum

<a id="RF-RTE-004"></a>
#### RF-RTE-004 · 射频路径上不打过孔
`should` · 可信度 `high` · 适用: rf_trace

**规则** 射频线全程走在同一外层、不换层；必须换层时，在信号过孔旁成对打接地过孔，并保持换层处参考平面连续。

**依据** 过孔有显著寄生电感，会形成阻抗不连续并使返回路径受阻，天线端尤其敏感。

| 参数 | 判据 | 备注 |
|---|---|---|
| `vias_in_rf_path` | == 0 count | Espressif 与 Infineon 均要求射频线不换层；换层时的接地伴随过孔是通用高速做法（Espressif 对 USB 的建议），非射频专有出处 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — RF 网络上的 via 数量 == 0。

**来源**
- [ESP32-C3 PCB Layout Design - RF Trace](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif Systems, vendor_guide, RF / RF Trace
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §20 Vias

## 平面与铺铜（plane_pour）

<a id="RF-PLN-001"></a>
#### RF-PLN-001 · 射频区地平面整块不分割，芯片底焊盘多打过孔
`must` · 可信度 `high` · 适用: rf_ic, qfn, ground_plane

**规则** 射频 IC、匹配网络与射频走线下方的地平面连续整块（尤其第一内层/底层），不分割、不留孤岛； 射频 IC 底部接地焊盘用与参考设计相同数量的接地过孔接到地平面（ESP32-C3 芯片至少 9 个）； 匹配网络地过孔到芯片焊盘的返回路径不得被其他东西挡住。

**依据** 射频地电流需要低阻抗、无阻挡的回路；分割或孤岛会引入电感和环路，使匹配偏移、杂散增加。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esp32_c3_chip_epad_ground_vias` | >= 9 count | Espressif：ESP32-C3 芯片底部焊盘至少 9 个接地过孔；其他芯片以其参考设计的过孔数为准（Nordic：中心焊盘过孔数与参考设计一致） |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 射频区投影内参考层的 GND zone 填充后无贯穿切口/孤岛；EPAD 过孔数 >= 参考设计数量。
- `drc`（full）· KiCad DRC — 无未连接的 GND 孤岛；zone 最小宽度、连接性规则不报错。

**来源**
- [PCB Layout Design Guide (EFR32 Wireless Gecko)](https://github.com/SiliconLabs/IoT-Developer-Boot-Camp/wiki/PCB-Layout-Design-Guide) — Silicon Labs, vendor_guide, §3.1
- [ESP32-C3 PCB Layout Design - Power Supply](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif Systems, vendor_guide, Power Supply (four-layer)
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §18.1, §20

<a id="RF-PLN-002"></a>
#### RF-PLN-002 · 接地缝合过孔间距不超过 λ/20（按介质内波长）
`should` · 可信度 `high` · 适用: via_stitching, cpwg, rf_trace

**规则** 射频线两侧和射频区的顶层接地铜用接地过孔缝合到内层/底层地，过孔间距不超过工作频率波长的 1/20（FR-4 中 2.4 GHz 约 3 mm）； 大块地铜上至少每 5 mm 一个过孔。

**依据** 过孔间距相对波长足够小才像一堵实心墙，抑制 CPWG 中顶层地与底层地之间的平行板模式和泄漏，并降低接地电感。

| 参数 | 判据 | 备注 |
|---|---|---|
| `via_pitch_max_fraction_of_wavelength` | <= 0.05 wavelength | Infineon §18.1/§20：不超过 1/20 波长，原文未说明是自由空间还是介质内波长（自由空间 λ/20 在 2.4835 GHz 约 6 mm）；AtlasPCB 的表按介质内波长（εr≈3.4）取 λ/20。本条取更严的介质内波长 λg = c/(f·√εeff)：f=2.4835 GHz、εeff≈3.3 时 λg≈66 mm，1/20 约 3.3 mm；用 εr 4.3 则约 2.9 mm（自行核算） |
| `large_ground_area_via_pitch_max` | <= 5 mm | Nordic nRF52 指南：大面积地铜上至少每 5 mm 一个过孔 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 沿射频线两侧及射频区边缘的顶层 GND 铜边界，取相邻 GND 过孔间距，最大值 <= 3 mm（保守取 λg/20 向下取整）；大块地铜内部相邻 GND 过孔的中心距 <= 5 mm（Nordic：至少每 5 mm 一个过孔，是间距而非到最近过孔的距离）。
- `em_sim`（partial）· openEMS 或 2.5D 求解器 — 扫 CPWG 过孔间距，S21 在 2.4 GHz 频段内无谐振陷波。

**来源分歧** 间距说法不一：Infineon 与 AtlasPCB 用 λ/20，部分文章用 λ/10，Nordic 给 5 mm（约为 2.4 GHz 介质内波长的 1/13）。 取舍：射频线两侧取 λg/20（约 3 mm），其他大面积地铜取 5 mm；以更严者为准。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §18.1, §20
- [Grounded Coplanar Waveguide (GCPW) PCB Design](https://www.atlaspcb.com/blog/gcpw-coplanar-waveguide-pcb-design-rf-mmwave/) — AtlasPCB, blog, Via Spacing Rule
- [General PCB design guidelines for nRF52 series](https://devzone.nordicsemi.com/guides/hardware-design-test-and-measuring/b/nrf5x/posts/general-pcb-design-guidelines-for-nrf52-series) — Nordic Semiconductor, vendor_guide, Ground planes and vias

<a id="RF-PLN-003"></a>
#### RF-PLN-003 · 并联接地元件的地脚旁紧贴独立接地过孔
`should` · 可信度 `high` · 适用: shunt_capacitor, matching_network, decoupling

**规则** 每个射频并联元件（接地电容等）的接地焊盘旁紧贴一个独立接地过孔，必要时加粗该焊盘附近的连线；不与其他焊盘共用过孔； QFN 封装里最靠近射频口的并联电容通过最近 ANT 脚的 VSS 脚接地（Nordic）。

**依据** 过孔离并联元件越远，就等于串了一段电感，使元件在射频线上呈现的阻抗偏离设计值，造成失配；共用过孔引入公共阻抗耦合。

| 参数 | 判据 | 备注 |
|---|---|---|
| `via_to_shunt_ground_pad_distance` | minimize | Silicon Labs/Nordic 只要求紧贴，无具体数值 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 对 RF 网络上每个并联接地焊盘：最近 GND 过孔距离报告并与参考设计对比；该过孔只连接 1 个元件焊盘（无共用）。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §20 Vias
- [PCB Layout Design Guide (EFR32 Wireless Gecko)](https://github.com/SiliconLabs/IoT-Developer-Boot-Camp/wiki/PCB-Layout-Design-Guide) — Silicon Labs, vendor_guide, §3.5
- [General PCB design guidelines for nRF52 series](https://devzone.nordicsemi.com/guides/hardware-design-test-and-measuring/b/nrf5x/posts/general-pcb-design-guidelines-for-nrf52-series) — Nordic Semiconductor, vendor_guide, Matching network, Ground planes and vias

<a id="RF-PLN-004"></a>
#### RF-PLN-004 · 匹配区走线和焊盘到邻近地铜至少 0.5 mm
`should` · 可信度 `medium` · 适用: matching_network, copper_pour

**规则** 匹配网络区域内，走线和焊盘到相邻地铜的间距不小于 0.5 mm，以减小对地寄生电容、避免失谐； CPWG 馈线区域则保持由阻抗计算得出的恒定间隙。

**依据** 间距越小对地电容越大，匹配元件值与实际有效值偏差越大；匹配网络对这些寄生很敏感。

| 参数 | 判据 | 备注 |
|---|---|---|
| `matching_area_gnd_clearance` | >= 0.5 mm | Silicon Labs EFR32 指南；单一厂商的数值，其他芯片以其参考设计为准 |

**验证**
- `drc`（full）· KiCad DRC + .kicad_dru（限定在匹配区 rule area） — (rule rf_match_gnd_clearance (condition "A.NetClass == 'RF' && B.Type == 'Zone'") (constraint clearance (min 0.5mm))) 仅对匹配区域生效；CPWG 馈线区另设间隙规则。DRC 违例为 0。

**来源**
- [PCB Layout Design Guide (EFR32 Wireless Gecko)](https://github.com/SiliconLabs/IoT-Developer-Boot-Camp/wiki/PCB-Layout-Design-Guide) — Silicon Labs, vendor_guide, §3.1, §3.2

<a id="RF-PLN-005"></a>
#### RF-PLN-005 · 射频路径下的内层：按厂商参考叠层选实心地或整片禁布
`should` · 可信度 `medium` · 适用: 4-layer, matching_network, rf_trace

**规则** 射频线/匹配网络下方的内层要么是完整地平面（该层即线的参考层），要么按厂商要求整片挖空（线以更远的层为参考，用 CPWG 修正线宽）； 二者不能混用，以所用芯片参考设计的叠层和参考层为准，并据此用对应的阻抗模型计算线宽，同时保证参考层与射频线之间没有其他走线。

**依据** 内层铜与顶层线之间的距离决定对地寄生电容和特性阻抗；不同芯片的参考设计基于不同的参考层。

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 方案 A（实心地）：参考层 GND 铜覆盖射频线与匹配网络投影，该层无其他走线； 方案 B（挖空）：内层在射频线或 RX 匹配网络投影区域无铜（可用 rule area 实现），线宽按更远的参考层重算。
- `tline_calc`（partial）· KiCad PCB Calculator — 按所选方案的参考层高度重新计算 50 Ω 线宽，与布局一致。

**来源分歧** Silicon Labs（2.4 GHz）与 Espressif（L2 完整地）要求射频区下的第一内层铺连续地； Nordic nRF52（多层板射频路径下内层禁布）与 Silicon Labs sub-GHz RX 匹配（内层禁布以降低对地寄生电容）则要求挖空。 取舍：这是芯片参考设计各自假设的参考层不同，不能凭此推翻任一方；采用所用芯片厂商的方案。

**来源**
- [General PCB design guidelines for nRF52 series](https://devzone.nordicsemi.com/guides/hardware-design-test-and-measuring/b/nrf5x/posts/general-pcb-design-guidelines-for-nrf52-series) — Nordic Semiconductor, vendor_guide, Keep-out
- [PCB Layout Design Guide (EFR32 Wireless Gecko)](https://github.com/SiliconLabs/IoT-Developer-Boot-Camp/wiki/PCB-Layout-Design-Guide) — Silicon Labs, vendor_guide, §3.1 (2.4 GHz), §3.2 (sub-GHz)
- [ESP32-C3 PCB Layout Design - Stub in a four-layer PCB](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif Systems, vendor_guide, RF / RF Matching Network

## 出图与制造（manufacturing）

<a id="RF-MFG-001"></a>
#### RF-MFG-001 · 下单前锁定叠层与阻抗要求，换板厂须重算射频线宽
`should` · 可信度 `high` · 适用: fabrication, impedance_control, jlcpcb

**规则** 射频线宽依赖板厂叠层：投板前向板厂确认叠层（层间介质厚度、Dk）并写进制造说明；更换板厂或叠层时按新叠层重算射频线宽并改板； 批量产品要求阻抗测试（JLCPCB 免费标准测试公差 ±20%，精密测试收费）。

**依据** 同样板厚的不同板厂层间距可以不同，线宽与介质厚度成正比，沿用旧线宽会使阻抗偏离。

| 参数 | 判据 | 备注 |
|---|---|---|
| `jlcpcb_standard_impedance_test_tolerance` | == 20 % | JLCPCB 层压结构页：标准免费阻抗测试公差 ±20%；其层压页面面向 4-32 层多层板，2 层板用厂商叠层 + 计算器核算并实测 |

**验证**
- `review`（manual）· 制造说明（fab notes）核对 — 制造说明写明叠层编号/各层厚度、阻抗控制网络及线宽、公差；与 RF-STK-001 的计算输入一致。
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 读取 .kicad_pcb 叠层设置，层厚与 Dk 同板厂叠层表一致；射频线宽等于当前叠层的计算值。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §17.1 Four-Layer PCB
- [Multi-Layer PCB Standard Laminated Structures](https://jlcpcb.com/help/article/multi-layer-pcb-standard-laminated-structures) — JLCPCB, vendor_guide

## 签核验证（verification）

<a id="RF-VER-001"></a>
#### RF-VER-001 · 天线端回波损耗 S11 <= -10 dB 覆盖整个工作频段
`should` · 可信度 `high` · 适用: antenna, s11, vna

**规则** 匹配调好后，从芯片/模组输出口向天线看，S11 在整个工作频段（2.4 GHz ISM 为 2.400-2.4835 GHz，BLE 为 2.402-2.482 GHz）<= -10 dB （反射功率 <= 10%，VSWR 约 1.9）；VSWR 1.5（RL 14 dB）算很好，VSWR > 2（RL < 9.5 dB）要重新检查匹配。

**依据** 回波损耗 > 10 dB 意味着约 90% 的功率进入天线；失配是链路预算中最大的损失来源之一。

| 参数 | 判据 | 备注 |
|---|---|---|
| `s11_in_band` | <= -10 dB | Infineon §15；TI AN058 示例以 S11 < -10 dB 为要求；Taoglas 以带中心 -10 dB、VSWR < 2:1 为目标 |
| `vswr_good_match` | <= 1.5 ratio | TI AN058 §3.4：VSWR 1.5（RL 14 dB）算良好匹配 |
| `vswr_review_threshold` | > 2.0 ratio | VSWR 2.0 即 RL 9.5 dB，通常用作带宽判据；超过需检查匹配 |

**验证**
- `bench`（full）· VNA（一端口校准）+ scikit-rf — 在连接器参考面做一端口校准，扫 2.3-2.6 GHz，导入 touchstone： band = skrf.Network('s11.s1p')['2.4-2.4835ghz']，要求 (band.s_db[:,0,0] <= -10).all()。
- `em_sim`（partial）· openEMS — 仿真结果同样在 2.400-2.4835 GHz 内 S11 <= -10 dB（见 RF-VER-004）。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §15 Antenna Tuning
- [AN058 Antenna Selection Guide (SWRA161B)](https://www.ti.com/lit/pdf/swra161) — Texas Instruments, app_note, §3.4, §6.2.4
- [Application Note for PA.25.A Antenna Integration (APN-11-8-002)](https://www.taoglas.com/assets/application-notes/APN-11-8-002.C.pdf) — Taoglas, app_note, §4 Bandwidth

<a id="RF-VER-002"></a>
#### RF-VER-002 · 用 VNA 测天线：校准到参考面，在最终外壳和手持下复测
`should` · 可信度 `high` · 适用: vna, antenna_tuning, enclosure

**规则** 测量前做一端口校准并把参考面移到测量点，用短于 5 cm 的半刚性电缆、屏蔽层就近接地；电缆固定走向，必要时加铁氧体； 放在不致失谐的支撑（木桌/泡沫）上，手离开。先测裸板，再装进最终外壳、手持（或实际放置）复测，并移开芯片侧（拆掉匹配元件）测天线侧。

**依据** 电缆摆放可使 S11 变化达 3 dB；小地平面板上电缆外皮有电流，使读数不稳；塑料外壳和人手会使谐振频率下移，甚至使带内回损劣于 10 dB。

| 参数 | 判据 | 备注 |
|---|---|---|
| `calibration_cable_max_length` | < 5 cm | TI AN-1811：校准用半刚性电缆短于 5 cm，否则电延迟过长 |
| `cable_placement_induced_s11_variation` | <= 3 dB | Infineon §15.1.1：同轴线摆放可使 S11 变化达 3 dB（说明测量不确定度，不是验收值） |

**验证**
- `bench`（manual）· VNA + 半刚性电缆 + 铁氧体 — 按顺序：①校准（开路/短路/负载）；②裸板测 S11；③装入最终外壳复测；④手持复测； 各状态 2.400-2.4835 GHz 内 S11 均 <= -10 dB，且谐振点偏移在带宽余量之内。

**来源**
- [AN058 Antenna Selection Guide (SWRA161B)](https://www.ti.com/lit/pdf/swra161) — Texas Instruments, app_note, §6.2.1-6.2.4
- [AN-1811 Bluetooth Antenna Design (SNOA519B)](https://www.ti.com/lit/an/snoa519b/snoa519b.pdf) — Texas Instruments, app_note, §4.1 Network Analyzer Calibration, §4.2 Measurement
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §15.1

<a id="RF-VER-003"></a>
#### RF-VER-003 · 板子回来后用 Smith 圆图调 π 匹配网络
`should` · 可信度 `high` · 适用: pi_network, antenna_tuning, smith_chart

**规则** 装好 π 预留位后，在 VNA 上测匹配点处的复阻抗，在 Smith 圆图上选拓扑：串联 L 沿恒电阻圆顺时针、串联 C 逆时针， 并联 L 沿恒电导圆逆时针、并联 C 顺时针；逐元件调到谐振点落在频段中心；再在最终外壳和手持状态下复核；记录最终元件值并写进量产 BOM。

**依据** 实际元件有寄生电阻和电容，理论值不会精确成立，需要试凑；环境（外壳、手）会改变天线阻抗，必须在使用环境下调。

**验证**
- `bench`（manual）· VNA + Smith 圆图 / scikit-rf — 测量点与元件放置点一致；每次只改一个元件，S11 谐振凹点移向 2.44 GHz 附近并达到 RF-VER-001 的指标； BOM 记录最终值，DNP 位与 0 Ω 位在 BOM 中明确。
- `spice`（partial）· scikit-rf（Smith 圆图/匹配）或 ngspice .ac — 用测得的复阻抗做匹配仿真，选取初始元件值，减少试凑次数。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §14.1, §14.2, §15, Appendix A
- [AN-1811 Bluetooth Antenna Design (SNOA519B)](https://www.ti.com/lit/an/snoa519b/snoa519b.pdf) — Texas Instruments, app_note, §4.3 Tuning the Impedance, §4.4 PI-Network Matching
- [Chip Antenna Layout Considerations for BLE, 802.11, and 2.4G Zigbee](https://www.johansontechnology.com/tech-notes/chip-antenna-layout-considerations-for-ble-80211-and-24g-zigbee/) — Johanson Technology, app_note

<a id="RF-VER-004"></a>
#### RF-VER-004 · 定制 PCB 天线先做电磁仿真再投板
`should` · 可信度 `medium` · 适用: em_sim, pcb_antenna, openEMS

**规则** 自行设计或改动 PCB 天线、地平面或禁布区时，先用 3D EM 求解器（如 openEMS）仿真 S11、输入阻抗和方向图，网格取最高频率波长的 1/20 左右， 再制板实测；直接拷贝厂商参考设计时可省仿真，但仍要实测。

**依据** PCB 天线设计并不简单，通常必须用仿真工具才能得到可接受的方案；而地平面、外壳等因素又需要实测修正。

| 参数 | 判据 | 备注 |
|---|---|---|
| `mesh_resolution` | <= 0.05 wavelength | openEMS Simple Patch Antenna 教程取 mesh_res = C0/(f0+fc)/20，即最高频率波长的 1/20；仅为教程设置 |

**验证**
- `em_sim`（partial）· openEMS + CSXCAD（Python），后处理用 scikit-rf — 建模基板 εr、铜、地平面尺寸和禁布区，50 Ω 集总端口，扫 2.3-2.6 GHz；S11 = port.uf_ref/port.uf_inc； 通过：2.400-2.4835 GHz 内 S11 <= -10 dB，并检查方向图/效率。

**来源**
- [Simple Patch Antenna - openEMS tutorial](https://openems.readthedocs.io/en/latest/python/openEMS/Tutorials/Simple_Patch_Antenna.html) — openEMS, tool_doc
- [AN058 Antenna Selection Guide (SWRA161B)](https://www.ti.com/lit/pdf/swra161) — Texas Instruments, app_note, §4.1.1 TI Antenna Reference Designs (PCB antenna design usually needs a simulation tool); §8.2 EM Simulation Tools
- [ESP32-C3 PCB Layout Design - RF Matching Network](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif Systems, vendor_guide, RF

<a id="RF-VER-005"></a>
#### RF-VER-005 · 用传导口预扫发射功率、谐波与杂散
`should` · 可信度 `high` · 适用: conducted_test, harmonics, certification

**规则** 在传导测试口（U.FL 或临时焊出）用频谱仪测最大发射功率、二/三次谐波和带外杂散，对照目标法规限值留余量后再送认证实验室： FCC 15.247(b)(3)/(d)（<= 1 W，带外 >= 20 dBc）与 ETSI EN 300 328（e.i.r.p. <= 20 dBm，1-12.75 GHz 杂散 <= -30 dBm/1 MHz）。

**依据** 谐波与杂散由匹配和滤波决定，布局偏离参考设计时最容易超标；预扫能在认证前发现问题并便于调匹配网络。

| 参数 | 判据 | 备注 |
|---|---|---|
| `fcc_out_of_band_suppression` | >= 20 dB | 15.247(d)，100 kHz 带宽相对带内最高值；RMS 平均测功率时为 30 dB |
| `etsi_spurious_1_to_12p75ghz` | <= -30 dBm | 每 1 MHz 带宽，EN 300 328 Table 4/12 |

**验证**
- `bench`（manual）· 频谱仪 + 传导测试口 + 衰减器 — 按设计的最大功率档发射，测峰值/平均功率、2×/3× 谐波与 30 MHz-12.75 GHz 杂散，扣除线损后均满足限值并留余量。
- `emc_precompliance`（manual）· 近场探头 + 频谱仪（辐射预扫） — 整机状态下做辐射预扫，重点看谐波频点与时钟谐波。

**来源**
- [47 CFR 15.247](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C/subject-group-ECFR2f2e5828339709e/section-15.247) — eCFR / US Government, standard, (b)(3), (d)
- [ETSI EN 300 328 V2.2.2](https://www.etsi.org/deliver/etsi_en/300300_300399/300328/02.02.02_60/en_300328v020202p.pdf) — ETSI, standard, §4.3.1.10.3 Table 4, §4.3.2.9.3 Table 12
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §22 Design for Testability

<a id="RF-VER-006"></a>
#### RF-VER-006 · 在最终产品上实测吞吐量与通信距离
`should` · 可信度 `high` · 适用: range_test, ota, final_product, esp32-c3-wroom-02 · 标签: cat-feeder

**规则** 外壳装好后，在代表性环境中测吞吐量/丢包率与最大通信距离，并与链路预算对比；可用 golden board 在校准衰减下测 PER（双向各测一次）， 或在消声室/OTA 测 TRP；任何影响天线环境的结构改动后重测。

**依据** 天线性能受外壳、手、安装位置等整机因素影响，只有整机实测才能确认射频性能；PER 法在没有 VNA/消声室时也可检验装配正确性。

**验证**
- `bench`（manual）· 路由器/对端设备 + iperf 或 RSSI/PER 统计；golden board — 固定位置与朝向，记录不同距离的吞吐量/PER/RSSI；与 RF-ARC-001 的预算对比； 外壳、料盒、猫食机金属部件在位。

**来源**
- [ESP32-C3 PCB Layout Design - Positioning a Module on a Base Board](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html) — Espressif Systems, vendor_guide
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §22
- [AN058 Antenna Selection Guide (SWRA161B)](https://www.ti.com/lit/pdf/swra161) — Texas Instruments, app_note, §6.3 Over-The-Air Measurements

<a id="RF-VER-007"></a>
#### RF-VER-007 · 用 SPICE/S 参数先仿匹配网络（含元件寄生）
`consider` · 可信度 `medium` · 适用: spice, matching_network, scikit-rf

**规则** 布板前用 ngspice（.ac）或 scikit-rf 把匹配网络按元件的 ESL/ESR/SRF/Q 模型仿真，检查 S11/S21（含谐波频点）和 Smith 圆图； 同时看插入损耗，因为低 Q 元件会让 S11 看着好而能量实际耗在电阻里。

**依据** 理想元件仿真与实际会偏差很大，用寄生参数估算实际可得电抗，能减少试凑次数并早期发现 SRF 或 Q 不够。

**验证**
- `spice`（partial）· ngspice .ac（电阻终接做 S 参数提取）或 scikit-rf 级联网络 — 用厂商 S 参数/SPICE 模型替换理想元件，提取 2.4 GHz 附近 S11 与插入损耗，以及谐波频点（如 4.8/7.2 GHz）的 S21，对照 RF-VER-001 与 RF-SCH-005 的目标。

**来源**
- [AN91445 Antenna Design and RF Layout Guidelines](https://community.infineon.com/gfawx74859/attachments/gfawx74859/cnkbas/2308/1/Infineon-AN91445_Antenna_Design_and_RF_Layout_Guidelines-ApplicationNotes-v09_00-EN.pdf) — Infineon (Cypress), app_note, §14.2, §21.2
- [scikit-rf documentation](https://scikit-rf.readthedocs.io/en/latest/) — scikit-rf, tool_doc
- [ESP32-C3 Schematic Checklist - RF Tuning](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html) — Espressif Systems, vendor_guide, RF Tuning

