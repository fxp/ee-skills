# 高速数字（high_speed）— 规则全文

垂直领域 · 52 条规则 · 由 `catalog/*.yaml` 生成，请改 YAML 不要改本文件。用 `grep -n "<规则ID>" rules.md` 定位单条，不要整份读。

环节分布：架构与选型 5，原理图 11，网表与约束 4，叠层与规则 3，分区规划 2，器件布局 4，布线 14，平面与铺铜 3，出图与制造 1，签核验证 5

## 架构与选型（architecture）

<a id="HSD-ARC-002"></a>
#### HSD-ARC-002 · 按接口确定差分/单端目标阻抗与公差
`must` · 可信度 `high` · 适用: usb2, usb3, pcie, ethernet, lvds, ddr3, mipi_csi

**规则** 每个高速接口在立项时写明目标阻抗和公差并记入设计约束：USB2 90 Ω 差分，USB3 SuperSpeed 90 Ω 差分，PCIe 100 Ω 差分（8/10 层板可取 85 Ω），以太网 MDI 100 Ω 差分，LVDS 100 Ω 差分，MII/RGMII 单端 50 Ω，DDR3 单端 50 Ω（SoC 厂商允许时 40 Ω）、DQS/CK 差分 100 Ω。后续叠层、线宽、间距都由该表推出。

**依据** 链路两端的驱动/端接按标称阻抗设计，走线阻抗偏离会在每个失配点产生反射并降低眼图与回波损耗；各接口的容差由协议和 SoC 厂商规定，不同接口不同。

| 参数 | 判据 | 备注 |
|---|---|---|
| `usb2_diff_impedance_spec` | 76.5 … 103.5 ohm | 90 Ω ±15%（SLLA414A §2.1）；单端 45 Ω ±15% |
| `usb2_diff_impedance_soc_guideline` | 81 … 99 ohm | TI SoC 表 A-1：81/90/99 Ω；Espressif ESP32-C3 指南同为 90 Ω ±10% |
| `usb3_diff_impedance` | 76.5 … 103.5 ohm | 90 Ω ±15%（SLLA414A §2.2）；TI SoC 表 A-1 收紧到 83.7–96.3 Ω，AM65xx 为 90.25–99.75 Ω |
| `pcie_diff_impedance` | 90 … 110 ohm | 100 Ω ±10%（SPRAAR7J 表 A-1）；AN10373：4/6 层板 100 Ω（单端 60 Ω），8/10 层板 85 Ω（单端 55 Ω） |
| `ethernet_mdi_diff_impedance` | 90 … 110 ohm | 100 Ω ±10%（SNLA387）；要与线缆阻抗一致 |
| `ethernet_mii_single_ended_impedance` | 45 … 55 ohm | 50 Ω ±10%（SNLA387） |
| `lvds_diff_impedance` | 95 … 105 ohm | 100 Ω ±5%（SNLA302 §3）；SNLA008A 容许 ±10% |
| `ddr3_single_ended_impedance` | 47.5 … 52.5 ohm | 50 Ω ±5%（SPRABI1D §6.3.1.4/6.3.1.6，TI KeyStone）；Micron TN-41-13 在 DQ 上推荐 40 Ω |
| `ddr3_dqs_ck_diff_impedance` | 95 … 105 ohm | 100 Ω ±5%（SPRABI1D §6.3.1.6/6.3.1.7） |
| `mipi_csi_diff_impedance` | 85 … 115 ohm | SPRAAR7J 表 A-7：85/100/115 Ω，单端 50 Ω，并要求松耦合（因 LP 模式为单端） |

**验证**
- `tline_calc`（partial）· KiCad PCB Calculator（TransLine）或板厂阻抗计算器，或 2D 场求解器 — 对每个接口类的线宽/间距/介质厚度/εr 计算 Zdiff 或 Z0，结果必须落在下表 range 内
- `bench`（manual）· TDR 示波器 + 阻抗测试条/实板 — 实测差分阻抗落在 range 内；连接器和过孔处允许短暂偏离但不超出该接口的反射预算

**来源分歧** 公差口径不一：USB 协议本身 ±15%，但 TI SoC 指南和 Espressif 都收紧到 ±10% 甚至更严；LVDS 的 TI 文档分别写 ±5%（SNLA302）与 ±10%（SNLA008A）。取舍：以目标器件数据手册/参考设计的值为准，没有时取更严的一档，给板厂的公差不要比板厂能做到的标准公差（见 HSD-MFG-001）更严。

**来源**
- [SPRAAR7J High-Speed Interface Layout Guidelines（附录 A 表 A-1..A-8）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, Appendix A
- [SLLA414A High-Speed Layout Guidelines for Signal Conditioners and USB Hubs（§2 Protocol Specific Layout Guidelines）](https://www.ti.com/lit/pdf/slla414) — Texas Instruments, app_note, §2.1-2.4
- [SNLA387 Ethernet PHY PCB Design Layout Checklist](https://www.ti.com/lit/pdf/snla387) — Texas Instruments, app_note
- [SNLA302 High-Speed Layout Guidelines for Reducing EMI for LVDS SerDes Designs](https://www.ti.com/lit/an/snla302/snla302.pdf) — Texas Instruments, app_note, §3
- [SPRABI1D DDR3 Design Requirements for KeyStone Devices（§6.3.1.4-6.3.1.7）](https://www.ti.com/lit/pdf/sprabi1) — Texas Instruments, app_note
- [AN10373 PCI Express PHY PCB Layout Guideline（§2.2.1）](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/powerquicc/2284/2/philips_PCIe_pcb_routing_guide.pdf) — NXP (Philips Semiconductors), app_note, §2.2.1

<a id="HSD-ARC-001"></a>
#### HSD-ARC-001 · 按边沿长度 1/6 判断走线是否需按传输线处理
`should` · 可信度 `high` · 适用: cmos_io, spi, clock, mii, rmii, ddr

**规则** 点对点走线的长度超过信号边沿（10–90% 上升/下降时间）在板上所占物理长度的 1/6 时，必须按传输线对待（受控阻抗并评估串联/并联端接）；更短的线可视为集总，不加端接。20–80% 边沿时间则用 1/4。

**依据** 走线延时与边沿时间可比时，驱动端与负载端的阻抗失配会在边沿上叠加反射，表现为过冲、振铃和非单调沿；比例越小反射占比越小。

| 参数 | 判据 | 备注 |
|---|---|---|
| `lumped_limit_fraction_of_edge_length` | <= 0.1667 x 边沿物理长度（10–90%） | 即 1/6；20–80% 沿时间用 0.25（SiTime AN10002） |
| `example_critical_length_gmii_500ps_fr4` | == 0.5 inch | AN-1263 算例：tr = 500 ps，传播延时 170 ps/inch → (1/6)*500/170 ≈ 0.5 in |
| `example_critical_length_1ns_fr4` | == 1.1 inch | AN10002 算例：1 ns（10–90%）沿、150 ps/in 的 FR4，超过 1.1 in 即按传输线处理 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python)，参见 ee-pcb-verify 的 geometry 检查器 — 取每条 CMOS 输出网络的驱动器上升时间（数据手册/IBIS，10–90%）和板材延时（FR4 约 150–170 ps/inch，外层微带更快），算 L_crit = tr/(6*tpd)；读板文件得每个网络的总长，凡 长度 > L_crit 的网络必须带串联电阻或受控阻抗声明，否则报错。
- `spice`（partial）· ngspice，T 元件（无损传输线） — 驱动器内阻 + 线 Z0 + 负载电容建模，对 L 取 L_crit 前后各一点做瞬态仿真，看接收端过冲/振铃是否在器件手册输入电压范围内

**来源分歧** 分数在不同资料里不一致：Altium 文章列举了 1/2、1/3、1/4、1/5、1/6、1/8、1/10、1/12、1/20 等引用，并指出真实临界长度取决于允许的阻抗偏差与带宽而非上升时间；TI SNLA008A 在 LVDS 场景写「电气长度达到 1/2 上升时间时可能需要端接」。取舍：对有明确阻抗要求的总线（USB/PCIe/DDR/以太网）不靠此规则，直接按目标阻抗设计；此规则只用于 SPI、时钟、GPIO 等无阻抗指标的单端线，决定是否加串联电阻，取保守的 1/6。

**来源**
- [AN-1263 DP83865 Gig PHYTER V Design Guide（§7.3 Termination Requirement，含 500 ps / 170 ps/in = 0.5 in 算例）](https://www.ti.com/lit/an/snla056d/snla056d.pdf) — Texas Instruments, app_note, §7.3
- [AN10002 Termination Recommendations for Single-ended Oscillator Driving Single or Multiple Loads](https://www.sitime.com/support/resource-library/application-notes/an10002-termination-recommendations-single-ended) — SiTime, app_note
- [Can We All Stop Quoting the Critical Length Rule?](https://resources.altium.com/p/can-we-all-stop-quoting-critical-length-rule) — Altium, vendor_guide

<a id="HSD-ARC-003"></a>
#### HSD-ARC-003 · 高速接口板按速率确定最少层数
`should` · 可信度 `medium` · 适用: usb2, ethernet, lvds, pcie, ddr · 标签: cat-feeder

**规则** 含 USB HS、以太网 PHY、LVDS、PCIe 或 DDR 的板子至少 4 层（外层走线、紧邻完整 GND 参考）；带 DDR/PCIe/USB3 的 SoC 级设计 TI 建议至少 6 层。2 层板只用于 FS USB（12 Mb/s）及低速接口，且信号下方必须是连续的地铜。

**依据** 阻抗控制和低回路电感都依赖信号层紧邻的完整参考面；2 层板没有可控的介质厚度，超出低速范围后无法同时满足阻抗与 EMI。

| 参数 | 判据 | 备注 |
|---|---|---|
| `min_layers_hs_interfaces` | >= 4 layers | SNLA302、Microchip AN2054（所有以太网 LAN 设计至少 4 层） |
| `min_layers_soc_ddr_pcie_usb3` | >= 6 layers | SPRAAR7J §3.12 'TI recommends a PCB of at least six layers' |

**验证**
- `review`（manual）· 设计评审清单 — 列出板上所有接口及其速率；任何 ≥ 480 Mb/s 的差分接口或 ≥ 100 MHz 的单端总线，对应层数必须 ≥ 4（SoC 级 DDR/PCIe/USB3 ≥ 6），否则必须记录例外与风险

**来源分歧** Microchip AN2054 要求以太网至少 4 层，而 SMSC AN18.6 §2.2.2 同时给出了 10/100 PHY 的 2 层叠层（底层整面地 + 电源岛、信号下方连续参考）。取舍：以太网产品板用 4 层；2 层只适合原型或极短走线、底层整面地的低成本方案，需在评审中明确接受风险。

**来源**
- [SNLA302 High-Speed Layout Guidelines for Reducing EMI for LVDS SerDes Designs](https://www.ti.com/lit/an/snla302/snla302.pdf) — Texas Instruments, app_note, §2
- [AN2054 Gigabit Ethernet Design Guide（PCB Layer Strategy）](https://ww1.microchip.com/downloads/en/Appnotes/00002054A.pdf) — Microchip, app_note
- [SPRAAR7J High-Speed Interface Layout Guidelines](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, §3.12
- [AN18.6 SMSC Ethernet Physical Layer Layout Guidelines（§2.2.2 2 Layer Stackup）](https://ww1.microchip.com/downloads/en/AppNotes/en562748.pdf) — Microchip (SMSC), app_note, §2.2
- [Hardware design with RP2040（§2.4.1 USB，1 mm 2 层板跑 FS USB）](https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf) — Raspberry Pi, vendor_guide

<a id="HSD-ARC-004"></a>
#### HSD-ARC-004 · DDR3 点对点驱动、走线、ODT 阻抗三者匹配
`should` · 可信度 `high` · 适用: ddr3

**规则** DDR3 点对点的数据总线按「驱动器阻抗 ≈ 走线阻抗」设计：40 Ω 走线配 34 Ω（或 40 Ω）驱动和 60 Ω ODT 是最优或近最优组合；余量足时走线可取 45/50/60 Ω，此时驱动取 40 Ω、ODT 取 60 Ω。选用 SoC 厂商规定的阻抗时（如 TI KeyStone 的 50 Ω）以厂商值为准，并周期性执行 ZQ 校准。

**依据** 驱动与线阻抗相同，反射不会回到驱动端，边沿更干净、眼图更开；ODT 和驱动阻抗靠 ZQ 校准才能保持在数据手册容差内。

| 参数 | 判据 | 备注 |
|---|---|---|
| `dq_line_impedance_best_margin` | == 40 ohm | Micron：DQ 总线 40 Ω、驱动 34/40 Ω 余量最大 |
| `odt_for_40ohm_line` | == 60 ohm | 34 Ω 驱动 + 40 Ω 线 + 60 Ω 终端 = best or near-best |
| `alternative_line_impedances` | 45 … 60 ohm | 45/50/60 Ω 时驱动 40 Ω、终端 60 Ω |

**验证**
- `si_sim`（partial）· IBIS 或 HSPICE 模型（SDRAM 厂商 + SoC 厂商），含完整叠层 — 读/写两种方向分别仿真 DQ，验证 setup/hold 窗口和 VIH/VIL 裕量；变化驱动强度和 ODT 看裕量最大的组合

**来源分歧** Micron 推荐 DQ 约 40 Ω，TI KeyStone 规定 50 Ω ±5%（单端）、100 Ω 差分。二者遵循同一原则（线阻抗匹配驱动），区别在 SoC 的驱动档位；以 SoC 数据手册为准。

**来源**
- [TN-41-13 DDR3 Point-to-Point Design Support（Drive Strength and Calibration；Terminating Point-to-Point Systems）](https://perso.esiee.fr/~poulichp/CEM/Signal_Integrity/tn4113_ddr3_point_to_point_design.pdf) — Micron Technology（ESIEE 镜像）, app_note
- [SPRABI1D DDR3 Design Requirements for KeyStone Devices（§6.5.2）](https://www.ti.com/lit/pdf/sprabi1) — Texas Instruments, app_note

<a id="HSD-ARC-005"></a>
#### HSD-ARC-005 · 选定 DDR 地址/命令拓扑（树形或 fly-by）并写入约束
`should` · 可信度 `high` · 适用: ddr3

**规则** DDR3 点对点的地址/命令/控制总线只选一种拓扑：树形（各分支长度差 ≤ 1 mm，可不加 VTT 终端，驱动端加串联电阻）或 fly-by（顺序经过各 SDRAM，末端 VTT 终端，产生时钟-数据偏斜，需 write leveling 或手工补偿）。SoC 厂商规定 fly-by 时（如 TI KeyStone）必须 fly-by。

**依据** 两种拓扑的信号质量、电源（VTT）需求和时序偏斜不同；写入约束后才能给出后续的长度匹配、stub 和终端规则。

| 参数 | 判据 | 备注 |
|---|---|---|
| `tree_branch_length_match` | <= 1 mm | Micron：地址总线树形各分支在同一网络内匹配到 1 mm 以内（作者自述该值有任意性） |

**验证**
- `review`（manual）· 原理图/约束评审 — 拓扑、终端方式（串联 R / VTT）和 SoC 厂商要求一致；fly-by 时存在 VTT 电源与去耦（见 HSD-SCH-009）
- `si_sim`（partial）· IBIS — 对选定拓扑仿真 CA 总线 setup/hold，比较树形与 fly-by 的抖动与电压裕量

**来源分歧** Micron 说点对点 DDR3 树形或 fly-by 皆可、树形无需 VTT；TI 要求自己的 KeyStone 对所有 CA/控制/时钟线一律 fly-by。取舍：SoC 厂商文档优先；没有厂商要求时按 Micron，用仿真比较。

**来源**
- [TN-41-13 DDR3 Point-to-Point Design Support（ADDR/CMD/CNTL Bus Termination，Table 8）](https://perso.esiee.fr/~poulichp/CEM/Signal_Integrity/tn4113_ddr3_point_to_point_design.pdf) — Micron Technology（ESIEE 镜像）, app_note
- [SPRABI1D DDR3 Design Requirements for KeyStone Devices（§6.3.1.3 'Follow the fly-by architecture concept'）](https://www.ti.com/lit/pdf/sprabi1) — Texas Instruments, app_note

## 原理图（schematic）

<a id="HSD-SCH-002"></a>
#### HSD-SCH-002 · LVDS 接收端用 100 Ω（±2%）差分端接电阻
`must` · 可信度 `high` · 适用: lvds

**规则** 每对 LVDS 在接收端跨接一个与介质差分阻抗一致的端接电阻，典型 100 Ω，精度在标称差分阻抗的 2% 以内；LVDS 接收器无内置端接时该电阻不可省。

**依据** 端接电阻使接收端反射为零并形成电流环路的 100 Ω 负载；阻值偏差直接转为反射系数和幅度误差，LVDS 输出摆幅只有数百 mV。

| 参数 | 判据 | 备注 |
|---|---|---|
| `lvds_termination_value` | == 100 ohm | 与介质（PCB/线缆）差分阻抗一致 |
| `lvds_termination_tolerance` | <= 2 % | SNLA008A：电阻应选到标称差分阻抗的 2% 以内 |

**验证**
- `bom_check`（full）· BOM + 网表脚本 — 对每对 LVDS 接收网络检查存在一个跨接 P/N 的电阻，阻值 = 介质差分阻抗（典型 100 Ω），容差 ≤ 2%（即 1% 或 0.5% 电阻）

**来源**
- [SNLA008A LVDS SerDes Gen I PCB and Interconnect Design-In Guidelines（§2.4 Termination at the RX Inputs）](https://www.ti.com/lit/pdf/snla008) — Texas Instruments, app_note, §2.4
- [SNLA302 High-Speed Layout Guidelines for Reducing EMI for LVDS SerDes Designs（§3，端接与介质阻抗一致）](https://www.ti.com/lit/an/snla302/snla302.pdf) — Texas Instruments, app_note, §3

<a id="HSD-SCH-004"></a>
#### HSD-SCH-004 · 按协议决定是否串联隔直电容及其值和封装
`must` · 可信度 `high` · 适用: usb2, usb3, pcie, displayport, hdmi

**规则** USB2 和 HDMI 数据对不加隔直电容；USB3 SuperSpeed TX 对和 PCIe TX 对必须串联隔直电容，值 0.1 µF（PCIe 允许 75–200 nF），封装 0402 优先、最大 0603，不用电容排；对内两颗电容同值同封装同位置。DisplayPort 同样必须隔直。

**依据** 链路两端共模电平不同，隔直电容是协议要求；大封装或电容排的焊盘寄生电容/电感会在差分线上形成阻抗不连续，不同值/封装会破坏对称并把差模转成共模。

| 参数 | 判据 | 备注 |
|---|---|---|
| `usb3_pcie_ac_cap_value` | == 0.1 uF | SLLU149：USB3/PCIe TX 0.1 µF |
| `pcie_ac_cap_range` | 0.075 … 0.2 uF | AN10373：75–200 nF，100 nF 最佳 |
| `ac_cap_max_package` | qualitative imperial code | 最大 0603，优先 0402 或更小（SPRAAR7J、AN10373、SLLU149）；电容排（C-pack）不允许 |

**验证**
- `bom_check`（full）· BOM + 网表脚本 — 对每个 TX 差分网络检查串联器件为电容，值在允许范围，封装 ≤ 0603，对内两颗相同；对 USB2 D+/D− 检查没有串联电容

**来源**
- [SLLA414A High-Speed Layout Guidelines for Signal Conditioners and USB Hubs（§2.1-2.4 AC Coupling Capacitors 行）](https://www.ti.com/lit/pdf/slla414) — Texas Instruments, app_note, §2
- [SLLU149E TUSB73x0 Board Design and Layout Guidelines（§5.4 SuperSpeed；§7 PCIe）](https://www.ti.com/lit/pdf/sllu149) — Texas Instruments, app_note, §5.4, §7
- [AN10373 PCI Express PHY PCB Layout Guideline（§2.5）](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/powerquicc/2284/2/philips_PCIe_pcb_routing_guide.pdf) — NXP (Philips Semiconductors), app_note, §2.5
- [SPRAAR7J High-Speed Interface Layout Guidelines（§3.10：最大 0603，强烈建议 0402 或更小）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, §3.10

<a id="HSD-SCH-006"></a>
#### HSD-SCH-006 · USB-C 受电设备在 CC1、CC2 各接 5.1 kΩ 下拉
`must` · 可信度 `high` · 适用: usb_c, sink · 标签: cat-feeder

**规则** 只做 sink（UFP）的 USB-C 接口在 CC1 和 CC2 两个引脚上各接一个 5.1 kΩ 电阻到 GND（Rd），两个引脚不要合用一个电阻；使用 CC 控制器时用手册给的内置 Rd。Rd 精度取 ±10% 或更好，CC 引脚上的 ESD/TVS 的 VRWM ≥ 5 V。

**依据** 电源（DFP）靠检测 CC 上的 Rd 判断连接、插入方向和是否可输出电流；没有 Rd，充电器不会给 VBUS 供电，两个 CC 合用一个电阻会让两个方向无法区分。

| 参数 | 判据 | 备注 |
|---|---|---|
| `cc_rd_value` | == 5100 ohm | CC1、CC2 各一个 |
| `cc_rd_tolerance` | <= 10 % | TUSB320 数据手册图中为 5.1 kΩ ±10%；USB Type-C 规范本身的容差未在本条读取，用 ±10% 偏保守 |

**验证**
- `erc`（full）· KiCad 网表脚本 — USB-C 连接器 A5（CC1）和 B5（CC2）各自经一个 5.1 kΩ 电阻（容差 ≤ 10%）连接到 GND 网络，两个电阻是不同的器件位号

**来源**
- [ESP-IoT-Solution USB Type-C Hardware Design Guide（CC1/CC2 各下拉 5.1 kΩ；A6/B6 并为 D+、A7/B7 并为 D−）](https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_overview/usb_typec_hardware_guide.html) — Espressif Systems, vendor_guide
- [TUSB320 USB Type-C Configuration Channel Logic and Port Control（Rd 5.1 kΩ ±10%，内部 RCC_D 4.6–5.6 kΩ）](https://www.ti.com/lit/gpn/TUSB320) — Texas Instruments, datasheet
- [SLVAF82B ESD and Surge Protection for USB Interfaces（§7.2：CC 引脚 VRWM ≥ 5 V）](https://www.ti.com/lit/pdf/slvaf82) — Texas Instruments, app_note, §7.2

<a id="HSD-SCH-009"></a>
#### HSD-SCH-009 · DDR3 的 Vref 与 VTT 用 1% 分压并就近去耦
`must` · 可信度 `high` · 适用: ddr3

**规则** DDR3 Vref（VrefCA、VrefDQ）由 VDD/2 经 1% 或更好的电阻分压得到，在每个 SDRAM 的 Vref 引脚各放 0.01 µF 与 0.1 µF（0402 或更小）并在源头放 1 个 0.1 µF；Vref 走线宽 ≥ 30 mil、与其他网络间距 ≥ 15 mil、走顶层并用地隔离。VTT 稳压器靠近 SDRAM 的 VTT 引脚，每个 VTT 引脚近处 ≥ 1 个 0.1 µF，VTT 岛上 ≥ 1 个 10–22 µF 低 ESR 陶瓷。

**依据** Vref 是比较器阈值，噪声直接变为时序/电压裕量损失；VTT 要吸收/提供终端电流，需要低阻抗的本地去耦。

| 参数 | 判据 | 备注 |
|---|---|---|
| `vref_divider_tolerance` | <= 1 % | 1% 或更好 |
| `vref_decap_each_pin` | qualitative uF | 每个 Vref 引脚 0.01 µF + 0.1 µF；源头 1 个 0.1 µF |
| `vref_trace_width` | >= 30 mil | 0.762 mm，去耦电容到 Vref 引脚的连线，越短越好 |
| `vref_clearance` | >= 15 mil | 0.381 mm |
| `vtt_bulk_cap` | 10 … 22 uF | VTT 岛上低 ESR 陶瓷，数量按岛面积、拓扑、负载 |
| `vref_vtt_noise_limit` | <= 2 % | TI 原文：pk-to-pk 噪声不得超过 ±2%（原文同句另写 1.5 mV，两者数值不自洽，以器件手册为准） |

**验证**
- `erc`（full）· KiCad 网表脚本 — 每个 Vref 引脚网络上有 0.01 µF 与 0.1 µF 电容各一，分压电阻容差 ≤ 1%；每个 VTT 引脚有 ≥ 0.1 µF；VTT 网络总电容 ≥ 10 µF
- `drc`（full）· KiCad DRC 自定义规则 — Vref 网络 track_width min 30 mil，对其他网络 clearance min 15 mil

**来源**
- [SPRABI1D DDR3 Design Requirements for KeyStone Devices（§6.3.1.8 Routing Rules – Power；§8.1.1-8.1.2）](https://www.ti.com/lit/pdf/sprabi1) — Texas Instruments, app_note, §6.3.1.8, §8.1

<a id="HSD-SCH-010"></a>
#### HSD-SCH-010 · 按总线电容和模式计算 I2C 上拉电阻窗口
`must` · 可信度 `high` · 适用: i2c

**规则** I2C 上拉电阻必须落在 Rp(min) ≤ Rp ≤ Rp(max) 的窗口内：Rp(min) = (VCC − VOL(max))/IOL，Rp(max) = tr/(0.8473 × Cb)。tr 最大值：标准模式 1000 ns、快速模式 300 ns、Fast-mode Plus 120 ns；Cb 最大值：标准/快速 400 pF、Fast-mode Plus 550 pF，Cb 要把器件引脚、走线和线缆电容都算上，长线或多从机超限时降速、分段或加缓冲器。

**依据** 上拉太弱时 RC 上升沿超过规范，太强时器件吸不下电流使低电平抬高；线越长 Cb 越大，窗口越窄。

| 参数 | 判据 | 备注 |
|---|---|---|
| `i2c_tr_max_standard` | <= 1000 ns | 标准模式；快速模式 300 ns；Fast-mode Plus 120 ns |
| `i2c_cb_max_standard_fast` | <= 400 pF | 标准/快速模式；Fast-mode Plus 550 pF |
| `i2c_vol_max` | <= 0.4 V | IOL = 3 mA，VCC > 2 V |
| `rise_time_coefficient` | == 0.8473 tr/(R*C) | VIL=0.3*VCC 到 VIH=0.7*VCC 的 RC 上升时间系数 |

**验证**
- `bom_check`（partial）· 脚本：按 Cb 估算（各器件引脚电容之和 + 走线电容（场求解器或实测）+ 线缆） — 对每条 I2C 总线算 Rp(min)/Rp(max)，实际上拉阻值在窗口内；Cb > 规定上限时报错
- `bench`（manual）· 示波器（上升沿按 30%–70% 量测，不是默认的 10%–90%） — 实测 SDA/SCL 上升时间 ≤ 模式限值，VOL ≤ 0.4 V

**来源**
- [SLVA689A I2C Bus Pullup Resistor Calculation（Table 2-1）](https://www.ti.com/lit/pdf/slva689) — Texas Instruments, app_note, §2

<a id="HSD-SCH-001"></a>
#### HSD-SCH-001 · 单端输出在驱动端串联 Rs = Z0 − Ro
`should` · 可信度 `high` · 适用: clock, spi, mii, rmii, ddr_ca

**规则** 超过临界长度（HSD-ARC-001）的单端点对点输出（时钟、SPI SCK、MII/RMII、DDR 地址/命令）在驱动端串联电阻 Rs = Z0 − Ro，Ro 取驱动器数据手册的输出阻抗；终端并联/AC 端接留给负载端。TI 推荐串联端接，因为它功耗小。

**依据** 驱动端内阻加串联电阻等于线阻抗，负载端高阻抗反射回来的波被驱动端吸收，不会再次反射；放在驱动端是因为电阻与引脚之间的走线本身又是一段未端接的传输线。

| 参数 | 判据 | 备注 |
|---|---|---|
| `series_resistor_formula` | qualitative ohm | Rs = Z0 − Ro；示例：Ro = 27 Ω、Z0 = 50 Ω → 23 Ω（TI）；Ro = 15.3 Ω、Z0 = 60 Ω → 44.7 Ω，取 43 Ω（SiTime） |
| `driver_with_two_lines_60ohm` | == 15 ohm | SiTime：一个驱动带两条 60 Ω 线时 Rs = 15 Ω；两条 50 Ω 线时 Rs = 0 Ω 并加大驱动强度；不建议一个驱动带 3 条以上 |

**验证**
- `erc`（partial）· KiCad ERC + 自定义脚本读网表 — 列出所有标记为高速单端输出且估算长度 > L_crit 的网络，要求驱动器引脚与第一个负载之间串有一个 22–100 Ω 范围内的电阻；缺失则报告
- `spice`（partial）· ngspice（T 元件 + 驱动器输出内阻 + 负载电容） — 对 Rs 在 0、计算值、2 倍计算值三档做瞬态，选过冲 < 10% 且 10–90% 边沿满足接收器 tr 要求的最小 Rs

**来源**
- [AN-1263 DP83865 Gig PHYTER V Design Guide（§7.3：Rs = Zo − Ro，例 50 − 27 = 23 Ω；时钟 Rs 靠近振荡器输出）](https://www.ti.com/lit/an/snla056d/snla056d.pdf) — Texas Instruments, app_note, §3, §7.3
- [AN10002 Termination Recommendations for Single-ended Oscillator Driving Single or Multiple Loads（Rs = 60 − 15.3 = 44.7，取 43 Ω）](https://www.sitime.com/support/resource-library/application-notes/an10002-termination-recommendations-single-ended) — SiTime, app_note
- [AN2054 Gigabit Ethernet Design Guide（Signal Integrity Concerns：串联端接放驱动端，AC 端接放负载端）](https://ww1.microchip.com/downloads/en/Appnotes/00002054A.pdf) — Microchip, app_note

<a id="HSD-SCH-003"></a>
#### HSD-SCH-003 · 原生 USB 数据线预留串联电阻与对地电容位
`should` · 可信度 `high` · 适用: usb2_fs, esp32c3, rp2040 · 标签: cat-feeder

**规则** MCU/SoC 的 FS/HS USB 数据线（ESP32-C3 的 GPIO18=D−、GPIO19=D+）在靠近芯片侧串联电阻并预留对地电容焊盘；ESP32-C3 起始值 22/33 Ω，电容初始不贴；RP2040 的 FS USB 需要 27 Ω 串联电阻并靠近芯片。ESP32-C3 上电时 D+ 会在高低之间浮动，需要稳定初态时外加上拉。

**依据** 串联电阻补足驱动器输出阻抗，使数据线满足 USB 驱动阻抗要求并抑制反射；对地电容位留给调试眼图/EMI 时使用。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esp32c3_usb_series_resistor_initial` | 22 … 33 ohm | Espressif 指南的初始值，电容初始不贴 |
| `rp2040_usb_series_resistor` | == 27 ohm | RP2040 硬件设计文档 |

**验证**
- `erc`（partial）· KiCad 网表脚本 — D+、D− 各自在 USB 连接器（或 ESD 器件）与芯片引脚之间存在一个串联电阻（阻值取芯片手册，ESP32-C3 起始 22 或 33 Ω），且每条线旁有一个未贴的对地电容封装
- `bench`（manual）· 示波器 + USB 眼图/枚举测试 — 原型上枚举成功，必要时调整串联 R 值并测上升时间、过冲

**来源分歧** 22/33 Ω（Espressif）与 27 Ω（RP2040）是各芯片驱动器阻抗不同的结果，不是冲突；以所选芯片的手册为准。

**来源**
- [ESP32-C3 Hardware Design Guidelines（§1.3.12 USB）](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/esp-hardware-design-guidelines-en-master-esp32c3.pdf) — Espressif Systems, vendor_guide, §1.3.12
- [Hardware design with RP2040（§2.4.1：27 Ω 串联端接靠近芯片）](https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf) — Raspberry Pi, vendor_guide

<a id="HSD-SCH-005"></a>
#### HSD-SCH-005 · 按接口速率选择 ESD 器件的电容、工作电压与等级
`should` · 可信度 `high` · 适用: usb, usb_c, esd_diode · 标签: cat-feeder

**规则** 选高速线 ESD 器件时同时满足：结电容低于接口上限（USB 1.1 < 20 pF，USB2 D+/D− < 4 pF，5 Gb/s 的 TX/RX < 0.5 pF，10 Gb/s < 0.3 pF，20 Gb/s < 0.25 pF）；反向工作电压 VRWM ≥ 3.3 V（数据线）、≥ 5 V（VBUS、CC）、≥ 3.6 V（SBU）；IEC 61000-4-2 至少 8 kV 接触/15 kV 空气；钳位电压低于被保护器件的绝对最大值。优先选支持直通布线（flow-through）的封装。

**依据** ESD 管的结电容并联在差分线上，过大会拉低眼图、增加插入损耗；VRWM 低于线上电压会漏电或误导通。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esd_cj_usb11` | < 20 pF | USB 1.0/1.1 D+/D−（12 Mb/s） |
| `esd_cj_usb2_data` | < 4 pF | USB2 D+/D−（480 Mb/s），也适用于带 SuperSpeed 接口的 D+/D− |
| `esd_cj_usb_5gbps_lane` | < 0.5 pF | 5 Gb/s TX/RX 及 5 Gb/s 以内 SBU |
| `esd_cj_usb_10gbps_lane` | < 0.3 pF | 10 Gb/s 每通道 |
| `esd_cj_usb_20gbps_lane` | < 0.25 pF | 20 Gb/s 每通道 |
| `esd_vrwm_data_lines` | >= 3.3 V | 数据线；VBUS、CC ≥ 5 V；SBU ≥ 3.6 V |
| `esd_iec61000_4_2_contact` | >= 8 kV | 接触放电；空气放电 ≥ 15 kV |

**验证**
- `bom_check`（partial）· BOM + 器件参数表 — 对每个连接器信号引脚查表：器件 Cj ≤ 上表对应接口上限，VRWM ≥ 线上最高工作电压，IEC 61000-4-2 ≥ 8/15 kV；缺参数时报告
- `bench`（manual）· 示波器眼图或 TDR — 有/无 ESD 器件各测一次眼图或 TDR，确认 ESD 引入的电容性不连续不超过接口反射预算

**来源**
- [SLVAF82B ESD and Surge Protection for USB Interfaces（§2-7）](https://www.ti.com/lit/pdf/slvaf82) — Texas Instruments, app_note, §2.2, §3.2, §4.2, §5.2, §6.2, §7.2
- [SPRAAR7J High-Speed Interface Layout Guidelines（§3.13 flow-through 布线）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, §3.13

<a id="HSD-SCH-007"></a>
#### HSD-SCH-007 · USB VBUS 加 TVS，钳位电压低于下游耐压并按 PD 电压档选型
`should` · 可信度 `high` · 适用: usb_c, usb_pd, vbus · 标签: cat-feeder

**规则** USB 连接器的 VBUS 对地加 TVS/ESD 器件，VRWM ≥ 5 V（USB-PD 时 ≥ 协商的最高 VBUS 电压），钳位电压低于下游器件的绝对最大值；热插拔时线缆电感振铃可使 20 V 的 VBUS 瞬时到约 50 V。支持 PD 的口，CC/SBU 引脚还要防对 VBUS 短路，所用器件 VRWM 需达 VBUS 电压档（如 24 V）。

**依据** VBUS 带电插拔、线缆电感和 ESD 都会产生远高于标称值的瞬态；CC/SBU 与 VBUS 在连接器上相邻，误插或破损时会被抬到 VBUS 电压。

| 参数 | 判据 | 备注 |
|---|---|---|
| `tvs_vrwm_vbus_5v` | >= 5 V | 5 V VBUS；TI 例：TVS0500 钳位 9 V；9 V 档 TVS1400 → 18 V；15 V 档 TVS1800 → 23 V；20 V 档 TVS2200 → 28 V；28 V 档 TVS3300 → 38 V |
| `unplug_ringing_peak_example` | == 50 V | TI 描述：热插拔电感振铃可使 20 V 线瞬时升至约 50 V |

**验证**
- `bom_check`（partial）· BOM + 器件参数表 — VBUS 网络存在 TVS：VRWM ≥ 最高 VBUS，钳位电压（典型 IPP 下） < 被保护器件 Abs Max；支持 PD 的口 CC/SBU 上器件 VRWM ≥ 最高 VBUS
- `bench`（manual）· 示波器 + 带电热插拔 — 用最大 VBUS 电压的电源热插拔，VBUS 过冲峰值 < 下游 Abs Max

**来源**
- [SLVAF82B ESD and Surge Protection for USB Interfaces（§8 USB-PD Surge Protection）](https://www.ti.com/lit/pdf/slvaf82) — Texas Instruments, app_note, §8.1-8.3

<a id="HSD-SCH-008"></a>
#### HSD-SCH-008 · 以太网磁件侧按规范配置 Bob Smith 端接与 49.9 Ω 上拉
`should` · 可信度 `high` · 适用: ethernet, discrete_magnetics

**规则** 分立磁件的线缆侧中心抽头（含未用对）各经 75 Ω 电阻再经 1000 pF/3 kV（或 1500 pF/2 kV）电容接机壳地；PHY 侧 TX/RX 线对按 PHY 手册上拉 49.9 Ω（1%）；磁件按 PHY 厂商认证/建议清单选，回波损耗、插入损耗、串扰隔离满足 Microchip 给的检查值。

**依据** Bob Smith 端接给共模噪声一个到机壳的受控泄放通道，兼顾 EMI 与 EFT/ESD；磁件规格对 IEEE 802.3 一致性影响很大，参数合格的器件也可能与具体 PHY 不兼容。

| 参数 | 判据 | 备注 |
|---|---|---|
| `bob_smith_resistor` | == 75 ohm | 每个线缆侧中心抽头及未用引脚各一个 |
| `bob_smith_capacitor_3kv` | == 1000 pF | 额定电压 3 kV；或 1500 pF/2 kV（Microchip AN2054） |
| `phy_side_pullup` | == 49.9 ohm | 1% 精度，TXP/TXN、RXP/RXN 各一（按 PHY 手册） |
| `magnetics_return_loss_100base_tx` | >= 19 dB | 2–40 MHz（Microchip 推荐检查值）；80 MHz 处 ≥ 12 dB；1000BASE-T 100 MHz 处 ≥ 10 dB |

**验证**
- `bom_check`（partial）· BOM + 数据手册核对 — 线缆侧每个中心抽头（含未用对）有 75 Ω 电阻 + 电容串联到机壳地，电容额定电压 ≥ 2 kV；PHY 侧 49.9 Ω 电阻 1%；磁件型号在 PHY 厂商推荐/认证清单中
- `bench`（manual）· 网络分析仪或以太网一致性测试 — 磁件回波损耗：2–40 MHz ≥ 19 dB，80 MHz 处 ≥ 12 dB（标准要求 ≥ 10 dB）；100BASE-TX 插入损耗 < 1.0 dB（100 kHz–80 MHz）（Microchip AN2054 推荐检查值）

**来源分歧** Microchip 要求 75 Ω+1000 pF/3 kV；TI AN-1263 同；另一些资料用 1500 pF/2 kV 方案，Microchip 也列为可选。属同一类方案内的可选值，以磁件厂商参考设计为准。

**来源**
- [AN2054 Gigabit Ethernet Design Guide（RJ45 Connector；Magnetics）](https://ww1.microchip.com/downloads/en/Appnotes/00002054A.pdf) — Microchip, app_note
- [AN-1263 DP83865 Gig PHYTER V Design Guide（§8-9：49.9 Ω 1% 与 Bob Smith 75 Ω/1000 pF/3 kV）](https://www.ti.com/lit/an/snla056d/snla056d.pdf) — Texas Instruments, app_note, §8, §9
- [AN18.6 SMSC Ethernet Physical Layer Layout Guidelines（49.9 Ω 上拉）](https://ww1.microchip.com/downloads/en/AppNotes/en562748.pdf) — Microchip (SMSC), app_note, §2.3

<a id="HSD-SCH-011"></a>
#### HSD-SCH-011 · 连接器引脚分配保证差分对相邻同排并配回流地针
`should` · 可信度 `high` · 适用: connector, usb, lvds, hdmi

**规则** 差分对分配在连接器同一排的相邻两针，不要跨排；在每对旁预留近邻 GND 针作共模回流；USB3 SuperSpeed 每对可交换 P/N 极性以避免走线交叉，但 TX 对与 RX 对不得互换；USB2 D+/D− 与 HDMI 不允许极性交换。

**依据** 同排相邻针的物理长度相同，对内偏斜最小；邻近地针给线缆上的共模噪声低阻抗回流，降低 EMI；极性交换在 SuperSpeed 里由接收端恢复，USB2 没有该机制。

**验证**
- `erc`（partial）· KiCad 网表 + 符号引脚坐标脚本 — 对每对差分网络，读连接器符号上两个引脚的位置，要求同一行相邻；其他引脚在对的两侧有 GND 针（至少一侧）
- `review`（manual）· 原理图评审 — USB3 P/N 交换仅出现在 SSTX 或 SSRX 对内，TX 与 RX 没被交换；USB2 D+/D− 未交换

**来源**
- [SNLA008A LVDS SerDes Gen I PCB and Interconnect Design-In Guidelines（§3.1 Connector Pinout）](https://www.ti.com/lit/pdf/snla008) — Texas Instruments, app_note, §3.1
- [SLLU149E TUSB73x0 Board Design and Layout Guidelines（§5.4：允许 P/N 交换，不允许 TX 与 RX 对交换）](https://www.ti.com/lit/pdf/sllu149) — Texas Instruments, app_note, §5.4
- [SLLA414A High-Speed Layout Guidelines for Signal Conditioners and USB Hubs（Polarity Reversal 行）](https://www.ti.com/lit/pdf/slla414) — Texas Instruments, app_note, §2.1-2.3

## 网表与约束（netlist）

<a id="HSD-NET-001"></a>
#### HSD-NET-001 · 差分对网络按同基名加 P/N 或 +/- 后缀命名
`must` · 可信度 `high` · 适用: kicad, differential_pair

**规则** 每对差分信号的两个网络使用相同的基名加一对成对后缀：_P/_N 或 +/-（如 USB_P/USB_N、USB+/USB-），同一对不得混用两种后缀风格（USB+ 与 USB_N 不构成一对）；在原理图里命名，PCB 才能用差分布线器、差分长度/偏斜/间距 DRC。

**依据** KiCad 按基名和成对后缀识别差分对；命名不合规时差分布线器、diff_pair_gap/diff_pair_uncoupled/skew(within_diff_pairs) 规则和 inDiffPair() 条件都不会生效，错误只会在后期以「没报错」的形式出现。

**验证**
- `netlist_diff`（full）· kicad-cli sch export netlist + Python 脚本 — 遍历网络名，匹配 *_P/*_N 与 *+/*-（含层级前缀）；任何网络其对侧同基名网络不存在或后缀风格不一致则报错；对已声明为差分接口的网络列表（USB D+/D−、MDI、DQS、CK、LVDS 对）逐一验证成对

**来源**
- [KiCad 9.0 PCB Editor — Routing differential pairs](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Routing differential pairs；inDiffPair()

<a id="HSD-NET-002"></a>
#### HSD-NET-002 · DDR 信号分网络类与字节通道，限定可交换范围
`should` · 可信度 `high` · 适用: ddr3

**规则** DDR3 信号至少分四个网络类：数据（DQ、DQS、DM）、地址/命令（BA、A、RAS、CAS、WE）、控制（CS、CKE、ODT）、时钟（CK 对）；数据类再按字节通道细分，每组含一对 DQS、DM 和 8 位 DQ。各类带各自的线宽/间距/匹配约束。管脚分配时：地址线不得为了布线方便互换，字节通道内的 DQ 位之间可以互换。

**依据** 时序约束只在同组网络间成立，类划分错会让长度匹配组不对；地址线顺序受 SDRAM 和训练算法约束，DQ 位在字节通道内可由控制器重映射。

**验证**
- `netlist_diff`（full）· KiCad netclass 导出 + Python 脚本 — 每个 DDR 网络属于且仅属于一个网络类；每个字节通道的 DQ[7:0]、DQS_P/N、DM 同组；输出各组成员表供长度匹配规则引用
- `review`（manual）· 管脚映射评审 — 对照 SoC 手册确认地址线序号与 SDRAM 一一对应；仅 DQ 位在同一字节通道内有交换

**来源**
- [SPRABI1D DDR3 Design Requirements for KeyStone Devices（§6.3.1.3 Table 6-1；§6.3.1.4；§6.3.1.6 Table 6-5）](https://www.ti.com/lit/pdf/sprabi1) — Texas Instruments, app_note, §6.3.1.3-6.3.1.6

<a id="HSD-NET-003"></a>
#### HSD-NET-003 · 在 .kicad_dru 中为高速网络类写长度/偏斜/间距规则
`should` · 可信度 `high` · 适用: kicad, drc

**规则** 把本域的数值约束写成 KiCad 自定义规则，使用 hasNetclass()/inDiffPair() 选对象，用 skew（对内加 within_diff_pairs，成组总线不加）、length、diff_pair_gap、diff_pair_uncoupled、via_count 约束，让 DRC 能自动判定。diff_pair_gap 的 opt 值给交互布线器用，min/max 才触发 DRC。

**依据** 网络类里的差分间距只是布线器的目标值，不会产生 DRC；不写自定义规则，长度/偏斜/过孔数全靠肉眼。

| 参数 | 判据 | 备注 |
|---|---|---|
| `skew_constraint_semantics` | qualitative mm | skew 取规则匹配网络中最长者为基准，差值超过 max 报错；差分对内（within_diff_pairs）逐对判；length 同时给长度调谐器设目标 |
| `example_rule_target_length` | qualitative mm | 官方示例：(rule "target length and skew" (condition "A.hasNetclass('high_speed')") (constraint length (min 95mm) (opt 100mm) (max 105mm)) (constraint skew (max 0.1mm))) |

**验证**
- `drc`（full）· kicad-cli pcb drc --format json（读取 .kicad_dru） — 规则文件语法通过；含目标规则的板文件 DRC 输出里没有 'Skew between tracks out of range'、'Track length out of range'、'Differential pair gap out of range'、'Differential uncoupled length too long'、'Too many or too few vias on a connection' 违规

**来源分歧** KiCad 论坛的旧例子写 skew 以平均长度为基准并带 ps 单位；9.0 官方文档写以最长网络为基准、单位为 mm/mil/in。取舍：以所用 KiCad 版本的官方文档为准，并用一块已知长度的测试板验证规则行为。

**来源**
- [KiCad 9.0 PCB Editor — Custom design rules（constraint 子句、skew、length、diff_pair_gap、diff_pair_uncoupled、via_count；Length tuning 示例）](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Custom design rules

<a id="HSD-NET-004"></a>
#### HSD-NET-004 · 把走线失配预算化为时序裕量的 1%
`should` · 可信度 `high` · 适用: ddr3, source_synchronous

**规则** 先把走线失配当作时序预算的一项：取时钟周期（地址/命令）或数据位周期（DQ）的约 1%（±0.5%）分给长度匹配；FR4 内层传播约 6.5 ps/mm，外层约快 10%；单个过孔延时按不超过 20 ps 计，同组过孔数相同则可忽略。例：DDR3-1600 DQ 位周期 625 ps，1% = 6.25 ps，约 ±0.5 mm；地址树形各分支 ±1 mm；10 ps 约合 1.5 mm（60 mil）。把换算结果写成 HSD-NET-003 里的数值。

**依据** 没有预算的「越短越好」无法验收；把失配换成 ps 再换成 mm，才能和 SDRAM/控制器的 setup/hold 表对账。

| 参数 | 判据 | 备注 |
|---|---|---|
| `inner_layer_flight_time` | == 6.5 ps/mm | FR4 内层；外层有效介电常数更低，约快 10% |
| `match_budget_fraction_of_period` | == 1 % | ±0.5%；Micron 自述取值有任意性，无未知量时应更紧 |
| `dq_match_800mhz_clock` | <= 0.5 mm | DDR3-1600 位周期 625 ps 的 1% = 6.25 ps |
| `address_branch_match` | <= 1 mm | 树形拓扑各分支 |
| `via_delay_upper_bound` | <= 20 ps | 含 Z 向延时与 LC 延时的最大值 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) + 叠层传播速度表 — 对每个匹配组，按各段所在层（内层 6.5 ps/mm，外层约 5.9 ps/mm）和过孔数折算延时，组内最大延时差 ≤ 预算（如 DQ 6.25 ps）
- `si_sim`（partial）· IBIS — 把实际失配代入时序预算表，复核 setup/hold 裕量 > 0

**来源**
- [TN-41-13 DDR3 Point-to-Point Design Support（Trace Length Matching；Propagation Delay；Vias）](https://perso.esiee.fr/~poulichp/CEM/Signal_Integrity/tn4113_ddr3_point_to_point_design.pdf) — Micron Technology（ESIEE 镜像）, app_note, DDR3 Layout and Design Considerations

## 叠层与规则（stackup）

<a id="HSD-STK-001"></a>
#### HSD-STK-001 · 高速线紧邻完整 GND 参考面，外层微带优先
`must` · 可信度 `high` · 适用: usb, pcie, ethernet, lvds, ddr

**规则** 每个高速信号层的相邻层必须有连续的 GND 参考面（不用电源面作参考，DDR 地址/控制线若参考 VDDQ 面则需沿面分布去耦电容）。TI 推荐高速差分走外层、下方紧邻 GND，不推荐带状线；整条走线始终参考同一个面。

**依据** 高频回流沿紧贴信号的参考面返回，参考面决定特性阻抗并提供最小回路；换参考面或穿越空洞会增加回路电感、辐射和串扰。

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 对每个高速网络的每一段走线，取相邻内层（叠层表）上投影区域的铜填充：该区域必须完全被同一网络（GND）的铜覆盖；输出被缺铜或被不同网络覆盖的线段长度，通过判据为 0

**来源分歧** 微带还是带状线各家说法相反：TI SPRAAR7J/SLLA414A 不推荐高速差分用带状线；TI SNLA302、SCAA082A、Microchip AN2054 称带状线 EMI/串扰更好；TI SPRABI1 要求 DDR 长走线用带状线（微带只用于 BGA 出线），Micron 指出外层传播约比内层快 10%。取舍：USB/PCIe/以太网等串行对按 TI SoC 指南走外层微带；DDR 并行总线按 SoC 厂商；同一匹配组内不要混用内/外层，不可避免时按 10% 修正等效长度。

**来源**
- [SPRAAR7J High-Speed Interface Layout Guidelines](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, §2.4, §3.2
- [SPRABI1D DDR3 Design Requirements for KeyStone Devices（§6.3.1.2）](https://www.ti.com/lit/pdf/sprabi1) — Texas Instruments, app_note
- [High-Speed Layout Guidelines (SCAA082A)](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.5

<a id="HSD-STK-002"></a>
#### HSD-STK-002 · 用板厂实际叠层参数计算阻抗，写明受控线所在层
`should` · 可信度 `medium` · 适用: jlcpcb, controlled_impedance

**规则** 受控阻抗线宽/间距必须用板厂的真实叠层（介质厚度、εr、铜厚、阻焊 εr 与厚度）在场求解器或板厂计算器里算出，并写明受控线在外层还是内层，因为同一叠层的有效介质厚度不同。以 JLCPCB 为例：JLC7628 系列 εr 4.6、阻焊 εr 3.8，外层受控线介质厚度 7.1 mil、内层 8.1 mil；JLC3313 为外层 3.5 mil、内层 4.5 mil。

**依据** 阻抗对介质厚度近似线性敏感，用标称值而不是压合后厚度，宽度会算偏；外层还要计入阻焊和空气。

| 参数 | 判据 | 备注 |
|---|---|---|
| `jlc7628_outer_dielectric_height` | == 7.1 mil | JLCPCB 阻抗页：JLC7628 受控线在外层时取 7.1 mil，内层 8.1 mil；εr(7628)=4.6，阻焊 εr=3.8 |
| `jlc3313_outer_dielectric_height` | == 3.5 mil | JLC3313 外层 3.5 mil，内层 4.5 mil |

**验证**
- `tline_calc`（partial）· JLCPCB 阻抗计算器 + KiCad PCB Calculator 交叉校验 — 用板厂叠层参数分别算差分阻抗；两个工具结果差 ≤ 5% 视为一致，否则以板厂工具为准并查原因

**来源分歧** KiCad 计算器文档未列出输入输出细节，且其模型来自 Transcalc/Atwater 等解析公式；第三方站点常用 εr 4.4，与 JLCPCB 公布的 4.6 不同。取舍：下单前以板厂自己的计算器和叠层表为准。

**来源**
- [JLCPCB 多层高精度阻抗板叠层页](https://cart.jlcpcb.com/client/template/placeOrder/impedance.html) — JLCPCB, vendor_guide
- [KiCad PCB Calculator（TransLine）](https://docs.kicad.org/9.0/en/pcb_calculator/pcb_calculator.html) — KiCad, tool_doc
- [TN-41-13（外层有效介电常数含阻焊和空气，约比内层传播快 10%）](https://perso.esiee.fr/~poulichp/CEM/Signal_Integrity/tn4113_ddr3_point_to_point_design.pdf) — Micron Technology（ESIEE 镜像）, app_note

<a id="HSD-STK-003"></a>
#### HSD-STK-003 · 长距离高速差分对对抗玻纤编织偏斜
`consider` · 可信度 `high` · 适用: pcie, usb3, sata, hdmi, sgmii, mipi_csi

**规则** 长距离、高速率（多 Gb/s）差分对用以下任一办法抑制玻纤编织造成的对内偏斜：让板厂把整个信号层图形相对玻纤旋转 10°–35°；只把高速差分以 10°–35° 角布线；Z 字形布线。同时在制板说明里选编织更密、含树脂更少的布型（如 1080/2116 优于 7628）。

**依据** 玻纤（εr 约 6）与环氧（εr 约 3）介电常数差异大，差分对两根线若分别沿玻纤束和树脂区走，会产生速度差，表现为对内偏斜、共模噪声和 EMI；该问题板间差异大、难以诊断。

| 参数 | 判据 | 备注 |
|---|---|---|
| `weave_rotation_angle` | 10 … 35 deg | SPRAAR7J §2.1：板厂旋转整层图形或仅差分线以该角度布线 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 对长度 > 3 inch 的高速差分对，统计线段与 X/Y 轴的夹角，要求大部分（按长度加权）线段夹角在 10°–35° 之间或确认板厂做了图形旋转
- `review`（manual）· 制板说明评审 — 制板说明中写明玻纤布型（如 1080 或 2116）或图形旋转要求

**来源**
- [SPRAAR7J High-Speed Interface Layout Guidelines](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, §2.1
- [AN10373 PCI Express PHY PCB Layout Guideline（长距离走线与 X-Y 轴成角度）](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/powerquicc/2284/2/philips_PCIe_pcb_routing_guide.pdf) — NXP (Philips Semiconductors), app_note, §2.2.3

## 分区规划（floorplan）

<a id="HSD-FLR-001"></a>
#### HSD-FLR-001 · 以太网前端分区：PHY、磁件、RJ45 的距离与隔离
`should` · 可信度 `medium` · 适用: ethernet

**规则** 分立磁件到 RJ45 ≤ 25 mm（约 1 inch）；PHY 到磁件的距离在 Microchip 的 ≤ 1 inch（不得超 3 inch）与 SMSC 的 ≥ 25 mm 之间取舍（见 conflicts）；PHY 到磁件的整段差分线总长不超过 4 inch；PHY 与发送线对距板边 ≥ 25 mm；晶体及其电阻电容放在距 PHY 12 mm（约 500 mil）以内；其它高速信号与以太网前端的间距 ≥ 0.3 inch。

**依据** 磁件是隔离屏障和 EMI 滤波点，靠近 RJ45 使未过滤的线对最短；PHY 与磁件间隔太近会耦合噪声，太远则线对损耗与失配加大；晶体对杂散电容敏感。

| 参数 | 判据 | 备注 |
|---|---|---|
| `magnetics_to_rj45_distance` | <= 25 mm | SMSC 称最高优先；Microchip 为 < 1 inch |
| `phy_to_magnetics_distance_microchip` | <= 1 inch | Microchip AN2054：做不到时最大 3 inch |
| `phy_to_magnetics_distance_smsc` | >= 25 mm | SMSC AN18.6：为 EMI 隔离 PHY 与磁件，各厂普遍的做法 |
| `phy_to_rj45_total_length` | < 4 inch | Microchip AN2054；TI SNLA387 对 MDI 总长要求 < 2 inch |
| `crystal_to_phy_distance` | <= 12 mm | SMSC AN18.6，约 500 mil；晶体、负载电容和电阻彼此 ≤ 7 mm |
| `other_hs_traces_to_ethernet_front_end` | >= 0.3 inch | Microchip AN2054 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 量 PHY 焊盘到磁件焊盘、磁件到 RJ45 焊盘、PHY 到板边、晶体到 PHY 振荡器引脚的距离，对照上述数值；量其它高速网络到 MDI 线对的最小距离 ≥ 0.3 inch

**来源分歧** PHY 到磁件的距离：Microchip 要求 < 1 inch（最多 3 inch），SMSC 要求 ≥ 25 mm（约 1 inch）以做 EMI 隔离。取舍：二者重合区间约 25 mm，在此取值；总长再服从 TI 的 MDI < 2 inch（见 HSD-RTE-009）。

**来源**
- [AN18.6 SMSC Ethernet Physical Layer Layout Guidelines（§2.3 Component Placement）](https://ww1.microchip.com/downloads/en/AppNotes/en562748.pdf) — Microchip (SMSC), app_note, §2.3
- [AN2054 Gigabit Ethernet Design Guide（Placement of components for discrete and embedded RJ45 and Magnetic module；Ethernet Differential Pairs）](https://ww1.microchip.com/downloads/en/Appnotes/00002054A.pdf) — Microchip, app_note
- [SNLA387 Ethernet PHY PCB Design Layout Checklist（Clock Source：振荡器靠近 PHY）](https://www.ti.com/lit/pdf/snla387) — Texas Instruments, app_note

<a id="HSD-FLR-002"></a>
#### HSD-FLR-002 · DDR 通道专用走线区，SDRAM 与 SoC 同面
`should` · 可信度 `high` · 适用: ddr3

**规则** 单 rank 的 SDRAM 与 SoC 放在同一面；SoC 到 SDRAM 的走线通道仅留给 DDR，不走其它信号，必须穿越时其间距 ≥ 6W 并且这些线不参考 DDR 的 IO 电源面，或放到另一布线层并以完整地平面隔开；DDR 走线下不得有任何参考面分割。

**依据** 并行总线的边沿快、条数多，外来的走线会与其串扰；参考面分割使回流绕行，引起时序与 EMI 问题。

| 参数 | 判据 | 备注 |
|---|---|---|
| `foreign_signal_spacing_in_ddr_channel` | >= 6 x W | 其它信号与 DDR3 网络的间距 ≥ 6W（W 为线宽） |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 取 DDR 网络的外包围区域，列出区域内属于非 DDR 网络的走线；对 DDR 走线 6W 邻域内的非 DDR 线段报错；检查 DDR 线下方内层参考铜是否连续（同 HSD-STK-001）

**来源**
- [SPRABI1D DDR3 Design Requirements for KeyStone Devices（§6.3.1.2-6.3.1.3 Routing Rules – General Overview）](https://www.ti.com/lit/pdf/sprabi1) — Texas Instruments, app_note, §6.3.1.3

## 器件布局（placement）

<a id="HSD-PLC-001"></a>
#### HSD-PLC-001 · 连接器侧保护链按 ESD、共模滤波、隔直电容的顺序放置
`should` · 可信度 `high` · 适用: usb, usb_c, esd, common_mode_choke · 标签: cat-feeder

**规则** USB 等高速接口从连接器引脚向芯片依次放置：ESD 器件最靠近连接器引脚（比共模扼流圈和 TX 隔直电容更近）、共模滤波器/扼流圈紧随其后、TX 隔直电容放在受保护侧并尽量靠近滤波器；ESD、滤波、隔直整段尽量短并紧挨连接器。共模滤波器位置预留 0 Ω 无贴选项，用 0402 0 Ω。以太网例外见 conflicts。

**依据** ESD 能量要在进入板内之前被钳位，路径上的任何器件在 ESD 到来时都可能被击穿；ESD 到引脚越近，保护器件与连接器之间的引线电感越小，残余电压越低。

| 参数 | 判据 | 备注 |
|---|---|---|
| `esd_flow_through_reference_length` | qualitative mm | SPRAAR7J 图 3-11 的直通布线示例标注 8 mm；未给出文字限值，作为参考 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 对每个 USB 连接器信号焊盘，沿网络顺序列出 ESD、CMC、AC 电容与焊盘的距离，要求 d(ESD) < d(CMC) < d(AC cap)；ESD 与连接器焊盘的距离上限由项目设定（来源只要求「尽量靠近」，TI 图 3-11 的直通示例标注 8 mm）

**来源分歧** 以太网相反：TI SNLA387 说明通用 ESD 指南建议放连接器侧，而以太网专用指南建议放磁件的 PHY 侧，因为连接器侧有高共模电压摆动，非 ESD 的高压会损坏保护器件。取舍：USB 按本条；以太网（磁件隔离）把 TVS 放磁件的 PHY 侧。

**来源**
- [SLLU149E TUSB73x0 Board Design and Layout Guidelines（§5.3-5.4）](https://www.ti.com/lit/pdf/sllu149) — Texas Instruments, app_note, §5.3-5.4
- [SPRAAR7J High-Speed Interface Layout Guidelines（§3.14 ESD/EMI Layout Rules）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, §3.14
- [SLVAF82B ESD and Surge Protection for USB Interfaces（place the diodes as close to the connector as design rules allow）](https://www.ti.com/lit/pdf/slvaf82) — Texas Instruments, app_note, §3.3

<a id="HSD-PLC-002"></a>
#### HSD-PLC-002 · 差分对上的隔直电容和 ESD 焊盘对称放置并挖空参考面
`should` · 可信度 `high` · 适用: usb3, pcie, ethernet, ac_coupling

**规则** 差分线上串联的 SMD（隔直电容、共模滤波器、ESD 器件）两根线上位置对称、封装一致、不得错位；SMD 焊盘下方的参考面 100% 挖空且至少两层深；ESD/EMI 器件信号焊盘下方挖空约 60%；以太网器件（磁件、扼流圈、隔直电容、ESD）下方铜平面挖空至少两层，挖空边缘距器件边缘约 20 mil。

**依据** 焊盘的对地电容在高速信号上是电容性不连续；挖空参考面可降低它，对称放置避免差模转共模。

| 参数 | 判据 | 备注 |
|---|---|---|
| `smd_pad_reference_void` | >= 100 % | 至少两层深（SPRAAR7J §3.10） |
| `esd_emi_pad_reference_void` | >= 60 % | SPRAAR7J §3.14：ESD/EMI 器件信号焊盘下 |
| `ethernet_void_edge_offset` | == 20 mil | SNLA387：器件边缘到挖空边缘；车规为全层挖空，标准应用至少两层 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 每对差分网络上的两个串联器件：封装相同、位置沿对中线镜像对称（误差 < 0.1 mm）；读相邻内层铜填充，焊盘投影区应无铜（ESD 焊盘 60% 面积）；不通过则报错

**来源**
- [SPRAAR7J High-Speed Interface Layout Guidelines（§3.10 SMD Pad Discontinuity Mitigation；§3.14）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, §3.10, §3.14
- [SNLA387 Ethernet PHY PCB Design Layout Checklist（MDI Traces：器件下方挖空，边缘约 20 mil）](https://www.ti.com/lit/pdf/snla387) — Texas Instruments, app_note
- [AN10373 PCI Express PHY PCB Layout Guideline（§2.5：两颗隔直电容值、封装一致，位置对称）](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/powerquicc/2284/2/philips_PCIe_pcb_routing_guide.pdf) — NXP (Philips Semiconductors), app_note, §2.5

<a id="HSD-PLC-003"></a>
#### HSD-PLC-003 · 端接电阻按类型放在驱动端或接收端，stub 尽量短
`should` · 可信度 `high` · 适用: lvds, ethernet, ddr, clock

**规则** 串联端接电阻紧靠驱动引脚；并联/AC 端接放在接收端；LVDS 的 100 Ω 差分端接距接收器输入 ≤ 1/2 inch，必要时用 fly-by 方式使 stub 最短；以太网 PHY 侧 49.9 Ω 上拉距 PHY ≤ 10 mm。DDR 单向地址/命令总线的串联电阻最好靠驱动端，放在总线中间也能得到可接受的结果。

**依据** 驱动与电阻之间的线段不受端接保护而成为一段独立的传输线；接收端电阻离输入引脚越远，中间那段线又产生反射，端接就白费。

| 参数 | 判据 | 备注 |
|---|---|---|
| `lvds_termination_to_rx_distance` | <= 0.5 inch | SNLA008A；超过则中间线段成为传输线，端接失效 |
| `ethernet_pullup_to_phy_distance` | <= 10 mm | SMSC AN18.6，约 400 mil |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 对网表中标记为端接的电阻：量其焊盘到对应 IC 引脚焊盘的走线长度（不是直线距离），串联 R 距离上限由项目设定（来源只要求紧靠驱动引脚）；LVDS 端接 ≤ 12.7 mm；以太网 49.9 Ω ≤ 10 mm

**来源**
- [SNLA008A LVDS SerDes Gen I PCB and Interconnect Design-In Guidelines（§2.4）](https://www.ti.com/lit/pdf/snla008) — Texas Instruments, app_note, §2.4
- [AN18.6 SMSC Ethernet Physical Layer Layout Guidelines（§2.3：49.9 Ω 上拉 ≤ 10 mm）](https://ww1.microchip.com/downloads/en/AppNotes/en562748.pdf) — Microchip (SMSC), app_note, §2.3
- [TN-41-13 DDR3 Point-to-Point Design Support（Bus Termination Overview）](https://perso.esiee.fr/~poulichp/CEM/Signal_Integrity/tn4113_ddr3_point_to_point_design.pdf) — Micron Technology（ESIEE 镜像）, app_note
- [AN2054 Gigabit Ethernet Design Guide（Signal Integrity Concerns）](https://ww1.microchip.com/downloads/en/Appnotes/00002054A.pdf) — Microchip, app_note

<a id="HSD-PLC-004"></a>
#### HSD-PLC-004 · 高速 IC 每个电源脚就近去耦，小电容最近，过孔贴焊盘
`should` · 可信度 `high` · 适用: phy, serdes, ddr, fpga

**规则** 高速接口 IC 的每个电源引脚各配去耦电容，同一电源上交替使用 0.01 µF 与 0.1 µF（可再加 1 µF），最小值电容最靠近引脚，与同层的 IC 在同一面；电容焊盘直接打 2–3 个地过孔，焊盘到过孔连接 < 10 mil，过孔不放在电容与 IC 之间；TI 以太网 PHY 的参考做法是电容距电源引脚 0.010 inch 以内。每个电源平面另放 4.7–10 µF 储能电容。DDR SDRAM 不必每个引脚配一颗：器件每侧 4 颗（核心 0.1/1 µF，I/O 更小值），过孔放在电容的器件一侧。

**依据** 去耦回路电感决定了高频供电阻抗；电容离引脚越远、过孔越长，回路电感越大，把 ESL 从约 1.5–2 nH 推到可高达 15 nH。

| 参数 | 判据 | 备注 |
|---|---|---|
| `decap_pad_to_via` | < 10 mil | Microchip AN2054；TI AN-1263：过孔距焊盘 0.010 inch 以内 |
| `decap_to_power_pin_optimal` | <= 0.01 inch | TI AN-1263「optimal results」；SMSC AN18.6 对 PHY 的容许值为 7 mm（280 mil） |
| `decap_ground_vias` | >= 2 pcs | SNLA302/Microchip：每个电容地端用 2–3 个过孔 |
| `decap_value_ladder` | qualitative uF | 0.1/0.01/0.001 µF 并联（SNLA008A）；交替 0.01 与 0.1 µF 使谐振频率分散（AN-1263）；每个电源平面另加 10 µF（AN-1263）/4.7–10 µF（SNLA008A） |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python)，参见 ee-pcb-verify 的 geometry 检查器 — 对每个电源引脚找最近的去耦电容，量焊盘中心距、电容地焊盘到过孔的距离、过孔数；通过判据：小值电容距离最小，pad-to-via < 10 mil，每个电容 ≥ 2 个地过孔；DDR 器件按每侧 4 颗另行判定
- `pi_sim`（partial）· PDN 阻抗仿真（见 HSD-VER-005） — 放置后的回路电感代入 PDN 模型，阻抗在目标频段低于 Z_target

**来源分歧** 距离数值不一致：TI AN-1263「最优 0.010 inch」是对其 PHY 的建议，SMSC 对 PHY 给 7 mm，Microchip 给 pad-to-via < 10 mil；DDR 器件 Micron 又明确不要每引脚一颗。取舍：以所用器件手册为准，缺省取 TI 的最严值，并用 PDN 仿真（HSD-VER-005）确认。

**来源**
- [AN-1263 DP83865 Gig PHYTER V Design Guide（§4 Power Supply Decoupling）](https://www.ti.com/lit/an/snla056d/snla056d.pdf) — Texas Instruments, app_note, §4
- [SNLA302 High-Speed Layout Guidelines for Reducing EMI for LVDS SerDes Designs（§4 Power and Grounding）](https://www.ti.com/lit/an/snla302/snla302.pdf) — Texas Instruments, app_note, §4
- [SNLA008A LVDS SerDes Gen I PCB and Interconnect Design-In Guidelines（§1.4 Device Bypass：电容在短窄线末端电感可高达 15 nH）](https://www.ti.com/lit/pdf/snla008) — Texas Instruments, app_note, §1.4
- [AN2054 Gigabit Ethernet Design Guide（Device Decoupling）](https://ww1.microchip.com/downloads/en/Appnotes/00002054A.pdf) — Microchip, app_note
- [TN-41-13 DDR3 Point-to-Point Design Support（Decoupling）](https://perso.esiee.fr/~poulichp/CEM/Signal_Integrity/tn4113_ddr3_point_to_point_design.pdf) — Micron Technology（ESIEE 镜像）, app_note, Decoupling
- [SPRAC76H Sitara Processor Power Distribution Networks（§6 Checklist for PDN：引脚与过孔 1:1，不共用）](https://www.ti.com/lit/an/sprac76g/sprac76g.pdf) — Texas Instruments, app_note, §6

## 布线（routing）

<a id="HSD-RTE-002"></a>
#### HSD-RTE-002 · 按接口限定差分对内偏斜
`must` · 可信度 `high` · 适用: usb2, usb3, pcie, ethernet, lvds, sata, hdmi · 标签: cat-feeder

**规则** 差分对 P/N 的长度差不得超过接口限值：USB2 ≤ 50 mil（TI SoC；集线器 TUSB 为 ≤ 150 mil）、USB3/PCIe/SATA/HDMI/SGMII ≤ 5 mil、以太网 MDI 100M/10M ≤ 50 mil 且 1G ≤ 20 mil、LVDS 约 ±30 ps（约 5 mm）；对被过孔、隔直电容、连接器分成的各段，每段单独等长，各段差值累加后仍须满足上限。TX 对与 RX 对之间一般不要求等长。

**依据** 对内偏斜使差模信号的一部分变成共模，降低眼图闭合并增加辐射；速率越高，容许的时间偏斜越小。

| 参数 | 判据 | 备注 |
|---|---|---|
| `usb2_intra_pair_skew_soc` | <= 50 mil | TI SoC 表 A-1..A-8；约 1.27 mm |
| `usb2_intra_pair_skew_hub` | <= 150 mil | TI TUSB73x0 指南 §5.3 |
| `usb3_pcie_sata_intra_pair_skew` | <= 5 mil | TI SPRAAR7J、SLLU149、SLLA414A（TI 推荐约 5 mil）、NXP AN10373；约 0.127 mm |
| `ethernet_mdi_intra_pair_skew_100m` | <= 50 mil | TI SNLA387：100M/10M；Microchip AN2054 对 intra-pair 同为 50 mil |
| `ethernet_mdi_intra_pair_skew_1g` | <= 20 mil | TI SNLA387：1G；MII 同组 RX 与 RX、TX 与 TX 之间也按此 |
| `lvds_intra_pair_skew` | <= 5 mm | SNLA302：约 ±30 ps |
| `ethernet_inter_pair_skew` | <= 600 mil | Microchip AN2054：设备到 RJ45 的对间偏斜 |

**验证**
- `drc`（full）· kicad-cli pcb drc（.kicad_dru） — 为各接口网络类写 (constraint skew (max <limit>) (within_diff_pairs))，limit 取下列 parameters（1 mil = 0.0254 mm）；DRC 无 'Skew between tracks out of range'
- `bench`（manual）· TDR 或示波器（对内延时差） — 实测 P/N 到达时间差 < 限值对应的 ps

**来源分歧** USB2 对内偏斜：TI SoC 指南 50 mil，TI TUSB 集线器指南（SLLU149）150 mil；LVDS：SNLA302 约 5 mm（±30 ps），SNLA008A 只说偏斜与时钟速率相关（66–20 MHz 对应不超过 100–400 ps）。取舍：以目标器件的指南为准，没有时取 50 mil（USB2）和 5 mm（LVDS）这类较严的值，PCIe/USB3 一律 5 mil。

**来源**
- [SPRAAR7J High-Speed Interface Layout Guidelines（附录 A 表 A-1..A-6）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, Appendix A
- [SLLU149E TUSB73x0 Board Design and Layout Guidelines（§5.3 USB2 ≤ 150 mil；§5.4 SuperSpeed ≤ 5 mil；§7 PCIe 各段累加 < 5 mil）](https://www.ti.com/lit/pdf/sllu149) — Texas Instruments, app_note, §5.3, §5.4, §7
- [SNLA387 Ethernet PHY PCB Design Layout Checklist（MDI 与 MII）](https://www.ti.com/lit/pdf/snla387) — Texas Instruments, app_note
- [AN2054 Gigabit Ethernet Design Guide（intra-pair 50 mil、inter-pair 600 mil）](https://ww1.microchip.com/downloads/en/Appnotes/00002054A.pdf) — Microchip, app_note
- [SNLA302 High-Speed Layout Guidelines for Reducing EMI for LVDS SerDes Designs（§3：±30 ps，约 5 mm）](https://www.ti.com/lit/an/snla302/snla302.pdf) — Texas Instruments, app_note, §3
- [AN10373 PCI Express PHY PCB Layout Guideline（§2.2.3：对内 ≤ 5 mil）](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/powerquicc/2284/2/philips_PCIe_pcb_routing_guide.pdf) — NXP (Philips Semiconductors), app_note, §2.2.3

<a id="HSD-RTE-005"></a>
#### HSD-RTE-005 · 高速线全程走在连续参考面上，远离参考面边缘和空洞
`must` · 可信度 `high` · 适用: usb, pcie, ethernet, lvds, ddr · 标签: cat-feeder

**规则** 高速线下的 GND 参考面必须连续：不跨分割、不跨空洞（焊盘挖空除外）；线距参考面边缘 ≥ 90 mil，距参考面空洞 ≥ 1.5W；全程参考同一个 GND 平面。确实必须跨分割或换参考面时，在跨越点旁放缝合电容（≤ 1 µF，越近越好）。DDR 走线下不得有任何平面分割。

**依据** 回流电流沿信号正下方返回；跨分割/空洞使回流绕行，增加环路电感、辐射、串扰和延时；板边处参考面边缘效应使阻抗改变。

| 参数 | 判据 | 备注 |
|---|---|---|
| `distance_to_reference_plane_edge` | >= 90 mil | SPRAAR7J §3.2 |
| `distance_to_reference_plane_void` | >= 1.5 x W | W 为计算得到的线宽；SMD 焊盘处的挖空除外 |
| `stitching_capacitor_max` | <= 1 uF | 无法避免跨分割时，缝合电容靠近跨越点 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python)，读填充后的铜区多边形 — 对每个高速网络的每段走线（外层），取相邻内层/对面层的 GND 铜区：线中心线必须在铜内，且到铜区边缘/空洞边缘的距离 ≥ max(90 mil, 1.5W) （边缘用 90 mil，空洞用 1.5W）；输出违反的线段；换层段检查两层 GND 是否同网络

**来源**
- [SPRAAR7J High-Speed Interface Layout Guidelines（§2.4；§3.2）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, §2.4, §3.2
- [SLLA414A High-Speed Layout Guidelines for Signal Conditioners and USB Hubs（§3.5）](https://www.ti.com/lit/pdf/slla414) — Texas Instruments, app_note, §3.5
- [AN2054 Gigabit Ethernet Design Guide（PCB Layer Strategy）](https://ww1.microchip.com/downloads/en/Appnotes/00002054A.pdf) — Microchip, app_note
- [SPRABI1D DDR3 Design Requirements for KeyStone Devices（§6.3.1.3：DDR3 走线下不允许分割）](https://www.ti.com/lit/pdf/sprabi1) — Texas Instruments, app_note, §6.3.1.3

<a id="HSD-RTE-012"></a>
#### HSD-RTE-012 · DDR3 地址/命令/控制线 fly-by 走线规则
`must` · 可信度 `high` · 适用: ddr3, fly_by

**规则** DDR3 地址/命令/控制按 fly-by：50 Ω（±5%）单端；所有网络沿同一路径依次经过各 SDRAM 再到 VTT 终端；各网络在同一路径上与时钟的长度差 ±20 mil 以内；每个匹配段的过孔数相同；到每个 SDRAM 的 stub < 80 mil，stub 之间长度差 ±10 mil；参考一个连续的 GND 面或有分布式去耦的 DVDD15 面；尽量走相近的层以减小过孔偏斜。

**依据** fly-by 使每个 SDRAM 看到的 CA 延时依次递增，由 write leveling 补偿；各 CA 线必须同路径同长度，否则各 SDRAM 的 CA 到时钟的相对时序散开，超出 leveling 范围。

| 参数 | 判据 | 备注 |
|---|---|---|
| `ca_single_ended_impedance` | 47.5 … 52.5 ohm | 50 Ω ±5% |
| `ca_skew_vs_clock` | <= 20 mil | ±20 mil，沿同一路径逐段 |
| `ca_stub_length` | < 80 mil | 到每个 SDRAM 的支线 |
| `ca_stub_skew` | <= 10 mil | ±10 mil |

**验证**
- `drc`（partial）· kicad-cli pcb drc（.kicad_dru） — CA 与 CK 放进同一 skew 匹配集（(condition) 用 hasNetclass），(constraint skew (max 0.508mm))（±20 mil 对应约 0.508 mm）；stub 另用 length 或脚本检查；via_count 在各 fly-by 段一致
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 从 SoC 引脚到每个 SDRAM 引脚逐段测长度，每个 SDRAM 的各 CA 网络段长差 ≤ ±20 mil（相对时钟）；找出长度 ≥ 80 mil 的支线（stub）
- `si_sim`（partial）· IBIS + 叠层 — 仿真各 SDRAM 处的 CA 眼图与 setup/hold，含 VTT 终端

**来源分歧** Micron TN-41-13 用 1 mm（约 40 mil）作为树形分支匹配，并对 DDR3 点对点说明可不用 fly-by；TI 规定的 ±20 mil 相对时钟与 stub < 80 mil 针对 KeyStone 的 fly-by 拓扑，数值不能跨拓扑通用。

**来源**
- [SPRABI1D DDR3 Design Requirements for KeyStone Devices（§6.3.1.4-6.3.1.5，Table 6-2、6-3）](https://www.ti.com/lit/pdf/sprabi1) — Texas Instruments, app_note, §6.3.1.4-6.3.1.5

<a id="HSD-RTE-013"></a>
#### HSD-RTE-013 · DDR3 数据、DQS 与时钟对的匹配和过孔规则
`must` · 可信度 `high` · 适用: ddr3

**规则** DDR3 数据线按字节通道布线：单端 50 Ω ±5%，同一通道内所有网络在同一层、过孔数相同（最多 2 个）、长度差 ±10 mil；DQS 差分对 100 Ω ±5%，对间长度差 ±1 mil；时钟 CK 差分对 100 Ω ±5%，各 CK 对之间长度差 ±1 mil，到每个 SDRAM 的 stub < 40 mil；数据组为点对点，无 VTT 终端，不得有中途过孔；DQS 与 DQ 的长度在控制器能调 DQS 偏斜时可放宽，否则收紧。

**依据** DQS 是数据采样时钟，DQ 对 DQS 的相对延时直接决定 setup/hold；同层同过孔数使每位的 Z 向延时和阻抗一致。

| 参数 | 判据 | 备注 |
|---|---|---|
| `dq_skew_within_byte_lane` | <= 10 mil | ±10 mil |
| `dqs_pair_skew` | <= 1 mil | TI 表 6-4「Skew between DQS pairs ±1 mil」，原文措辞可理解为 DQS 对间或对内，保守按对内与对间都满足 |
| `ck_pair_skew` | <= 1 mil | TI 表 6-6：各 CK 对之间 ±1 mil |
| `ck_stub_length` | < 40 mil | 到每个 SDRAM 的 CK stub |
| `data_vias_max` | <= 2 pcs | 每网络，同通道内数量一致 |

**验证**
- `drc`（full）· kicad-cli pcb drc（.kicad_dru） — 每个字节通道一个 skew 匹配集 (constraint skew (max 0.254mm))（±10 mil）；DQS/CK 差分对 (constraint skew (max 0.0254mm) (within_diff_pairs))（1 mil）；via_count (max 2)
- `si_sim`（partial）· IBIS + 叠层 — 读/写两个方向的 DQ-DQS 时序裕量（含 ODT），验证 setup/hold

**来源**
- [SPRABI1D DDR3 Design Requirements for KeyStone Devices（§6.3.1.6-6.3.1.7，Table 6-4、6-6）](https://www.ti.com/lit/pdf/sprabi1) — Texas Instruments, app_note, §6.3.1.6-6.3.1.7
- [TN-41-13 DDR3 Point-to-Point Design Support（Terminating Point-to-Point Systems：DQS 时序）](https://perso.esiee.fr/~poulichp/CEM/Signal_Integrity/tn4113_ddr3_point_to_point_design.pdf) — Micron Technology（ESIEE 镜像）, app_note

<a id="HSD-RTE-001"></a>
#### HSD-RTE-001 · 差分对全程对称平行，未耦合段只允许出现在引出和连接器处
`should` · 可信度 `high` · 适用: usb, pcie, ethernet, lvds, ddr_clock

**规则** 差分对的两根线全程平行、间距恒定、形状对称（拐弯、过孔、器件两侧一致）；不平行只允许出现在封装引出和连接器引脚处，并尽量短——封装引出须在离封装 0.25 inch 内完成；对内间距要小于介质到参考面的高度（S < h），使耦合主要发生在对内；BGA 出线后保持线宽不变。

**依据** 对内强耦合使外来噪声表现为共模而被接收器抑制，并使两根线的返回电流互相抵消；不对称会把差模转成共模，增加 EMI 和抖动。

| 参数 | 判据 | 备注 |
|---|---|---|
| `package_breakout_uncoupled_length` | <= 0.25 inch | SPRAAR7J §3.3；KiCad diff_pair_uncoupled 约 6.35 mm |
| `uncoupled_trace_into_pin_multibend` | <= 45 mil | AN10373 §2.3；引脚/焊球入口区的未耦合段 |
| `pair_gap_less_than_dielectric_height` | qualitative mil | SNLA008A：S < h；TI USB 图示例：线宽 6 mil、对内间距 8 mil；PCIe 微带线宽 5 mil、间距 7 mil，带状线 5/5 mil |

**验证**
- `drc`（full）· kicad-cli pcb drc（.kicad_dru） — 对差分网络类设 diff_pair_gap (min,max) 与 diff_pair_uncoupled (max 6.35mm)（0.25 inch）；PCIe 引脚入口处的未耦合段按 AN10373 另设 max 45 mil；DRC 无 'Differential uncoupled length too long' / 'Differential pair gap out of range'
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 对每对差分网络比较两根线上过孔、器件的沿线位置（至信号源的距离差）≤ 1 mm

**来源**
- [SPRAAR7J High-Speed Interface Layout Guidelines（§3.3 Symmetry in the Differential Pairs）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, §3.3
- [SNLA008A LVDS SerDes Gen I PCB and Interconnect Design-In Guidelines（§2.3：S < h，对间 ≥ 2S）](https://www.ti.com/lit/pdf/snla008) — Texas Instruments, app_note, §2.3
- [SNLA302 High-Speed Layout Guidelines for Reducing EMI for LVDS SerDes Designs（§3：同一对内距离全程相同）](https://www.ti.com/lit/an/snla302/snla302.pdf) — Texas Instruments, app_note, §3
- [AN10373 PCI Express PHY PCB Layout Guideline（§2.2.2-2.3：线宽 5 mil、微带间距 7 mil、引脚前未耦合段 ≤ 45 mil）](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/powerquicc/2284/2/philips_PCIe_pcb_routing_guide.pdf) — NXP (Philips Semiconductors), app_note, §2.2.2, §2.3
- [KiCad 9.0 PCB Editor — diff_pair_gap / diff_pair_uncoupled](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc

<a id="HSD-RTE-003"></a>
#### HSD-RTE-003 · 在失配发生处就近做局部蛇形补偿，几何满足间距要求
`should` · 可信度 `high` · 适用: differential_pair, length_matching

**规则** 差分对内长度补偿（蛇形）加在失配产生的那一端、尽量小幅度，不要在对中段集中做大蛇形；蛇形的几何参数：线宽 W = 6 mil、对内间距 A = 8 mil 时，蛇形宽 B ≥ 16 mil，转折段 C ≥ 18 mil（即 C ≥ 3W）；蛇形内两线间距 < 2 倍正常对内间距；蛇形各节之间中心距 ≥ 5W（DDR）；弯折两侧线段 ≥ 1.5W；左右弯折数尽量相等。

**依据** 偏斜在何处产生就在何处修正，才能使对中其余段保持平衡的共模特性；过密的蛇形会使两根线之间、节与节之间产生额外耦合和延时修正失真。

| 参数 | 判据 | 备注 |
|---|---|---|
| `serpentine_width_B` | >= 16 mil | SLLA414A 示例：W = 6 mil、A = 8 mil 对应 B ≥ 16 mil（约 2A） |
| `serpentine_turn_length_C` | >= 18 mil | 同示例 C ≥ 18 mil（= 3W）；AN10373 为 ≥ 3w（5 mil 线宽时 15 mil） |
| `serpentine_gap_ratio` | < 2 x S | AN10373：蛇形内对间距 S1 < 2 倍非蛇形对内间距 S |
| `ddr_serpentine_center_spacing` | >= 5 x W | SPRABI1D：含蛇形在内的中心距 ≥ 5W（W 为线宽） |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 识别蛇形段（连续折返）：测每节间距 ≥ 5W（DDR）或 ≥ 3W（差分）、折返长度 ≥ 3W；补偿段的起点与失配源（过孔、焊盘出口）之间的走线距离 ≤ 项目设定值
- `drc`（partial）· KiCad 长度调谐器 + DRC — 用 KiCad 的「调节差分对偏斜」工具（热键 9）只在较短一侧加蛇形；DRC 偏斜规则通过

**来源分歧** SNLA302 写「不要只在差分对一侧做蛇形，非对称的曲折会增加辐射、缩小眼图」，SPRAAR7J/AN10373 则要求把补偿加到失配处。取舍：二者不矛盾——补偿量应小且位于失配源附近，必须在较短的一根上加时，用小幅、对称布置的局部折返，避免长段大幅度蛇形；有条件时先在布局阶段消除失配，不依赖蛇形。

**来源**
- [SPRAAR7J High-Speed Interface Layout Guidelines（§2.3 Length Matching：添加在靠近失配的一端）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, §2.3
- [SLLA414A High-Speed Layout Guidelines for Signal Conditioners and USB Hubs（§3.3：W=6 mil、A=8 mil 时 B ≥ 16 mil、C ≥ 18 mil）](https://www.ti.com/lit/pdf/slla414) — Texas Instruments, app_note, §3.3
- [AN10373 PCI Express PHY PCB Layout Guideline（§2.2.3-2.2.4：jog ≥ 3w，S1 < 2S，左右弯折数接近）](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/powerquicc/2284/2/philips_PCIe_pcb_routing_guide.pdf) — NXP (Philips Semiconductors), app_note, §2.2.3-2.2.4
- [SNLA387 Ethernet PHY PCB Design Layout Checklist（长度匹配技巧应用在同一端）](https://www.ti.com/lit/pdf/snla387) — Texas Instruments, app_note
- [SPRABI1D DDR3 Design Requirements for KeyStone Devices（§6.3.1.3：含蛇形的中心距 ≥ 5W）](https://www.ti.com/lit/pdf/sprabi1) — Texas Instruments, app_note, §6.3.1.3

<a id="HSD-RTE-004"></a>
#### HSD-RTE-004 · 按接口取线对间距并避开时钟线，相邻层正交布线
`should` · 可信度 `high` · 适用: usb, pcie, ethernet, lvds, ddr

**规则** 差分对之间及对其它信号的间距按接口取值：TI SoC 通用规则为对间 ≥ 5W（W 为线宽），对其它信号 ≥ 30 mil，对时钟/周期信号 ≥ 50 mil；DDR 为中心距 ≥ 5W（≤ 1066 MT/s 可用 4W）；PCIe 为 20 mil 与 4 倍介质高度中的较大者，对电压/边沿更强的信号加到 30 mil；LVDS 对间 ≥ 2S，对 TTL 单端线 ≥ 3S 并放在不同层。相邻两个信号层的走线互相垂直。

**依据** 串扰随耦合长度和边沿速率增长，随线间距相对介质高度指数下降；垂直布线减少相邻层之间的宽边耦合。

| 参数 | 判据 | 备注 |
|---|---|---|
| `pair_to_pair_spacing_ti` | >= 5 x W | SPRAAR7J 的 5W 规则（6 mil 线宽 → 30 mil）；USB 对到其它信号 ≥ 30 mil，到时钟 ≥ 50 mil |
| `pair_to_clock_spacing` | >= 50 mil | SPRAAR7J 附录 A：与时钟或高速周期信号 |
| `pair_to_other_signal_spacing` | >= 30 mil | SPRAAR7J 附录 A；SNLA387 对以太网不同差分对间 ≥ 30 mil |
| `pcie_pair_spacing` | >= 20 mil | AN10373：20 mil 或 4 倍介质高度取大者；干扰源更强时 30 mil |
| `ddr_center_to_center_spacing` | >= 5 x W | SPRABI1D：4W 仅适用于 ≤ 1066 MT/s；其它信号 ≥ 6W |
| `lvds_pair_to_ttl_spacing` | >= 3 x S | SNLA008A：对间 ≥ 2S，TTL 单端线 ≥ 3S（S 为对内间距） |

**验证**
- `drc`（full）· kicad-cli pcb drc（.kicad_dru，按网络类写 clearance） — 为 USB/PCIe/以太网等网络类写 (constraint clearance (min <值>))：对时钟/周期类 ≥ 50 mil，对其它类 ≥ 30 mil，对间 ≥ 5W；DRC 无 clearance 违规
- `si_sim`（partial）· 2D/3D 场求解器或串扰估算 — 对长距离并行段（> 5 inch）估算近端/远端串扰，要求相对信号幅度的串扰低于接收器噪声裕量

**来源分歧** 间距倍数不统一：TI SPRAAR7J 5W，SCAA082A 2–3W，Altium 3W（认为是保守经验值），LVDS 2S/3S，PCIe 4 倍介质高度，以太网 30 mil。取舍：串扰实际取决于间距相对介质高度、并行长度和边沿；取接口所属厂商文档的值，没有时取 5W，空间受限时用场求解器/串扰估算证明更小间距可行。

**来源**
- [SPRAAR7J High-Speed Interface Layout Guidelines（§3.1, §3.4；附录 A）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, §3.1, §3.4
- [SPRABI1D DDR3 Design Requirements for KeyStone Devices（§6.3.1.3：5W/4W，其它信号 6W）](https://www.ti.com/lit/pdf/sprabi1) — Texas Instruments, app_note, §6.3.1.3
- [AN10373 PCI Express PHY PCB Layout Guideline（§2.2.2）](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/powerquicc/2284/2/philips_PCIe_pcb_routing_guide.pdf) — NXP (Philips Semiconductors), app_note, §2.2.2
- [SNLA008A LVDS SerDes Gen I PCB and Interconnect Design-In Guidelines（§2.3）](https://www.ti.com/lit/pdf/snla008) — Texas Instruments, app_note, §2.3
- [High-Speed Layout Guidelines (SCAA082A)（§2.5：2–3 倍线宽；相邻层垂直）](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.5
- [Crosstalk Analysis, Reduction, and Elimination Techniques in PCB Design（3W 规则）](https://resources.altium.com/p/crosstalk-elimination-techniques-in-altium-designer) — Altium, vendor_guide

<a id="HSD-RTE-006"></a>
#### HSD-RTE-006 · 换层过孔旁就近放地缝合过孔，且差分两线过孔对称
`should` · 可信度 `high` · 适用: usb, pcie, ethernet, lvds · 标签: cat-feeder

**规则** 高速信号换层且参考面也换时，在信号过孔旁对称放置地缝合过孔（中心距 ≤ 200 mil，越近越好），每对差分线 1–3 个；差分对两根线的过孔数量相同、位置对称；USB 差分线每个过渡点加一对地回流孔（Espressif）；过孔尽量靠近 SoC。

**依据** 过孔使回流面改变，没有近旁的地孔时回流必须绕过多层，回路面积和阻抗不连续陡增；两线过孔不一致会引入对内延时与阻抗差。

| 参数 | 判据 | 备注 |
|---|---|---|
| `stitching_via_distance` | <= 200 mil | 中心到中心，越近越好；对称放置 |
| `stitching_vias_per_pair` | 1 … 3 pcs | AN10373 |
| `signal_via_pad_diameter_max` | <= 25 mil | AN10373；孔径 ≤ 14 mil |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 对高速网络的每个信号过孔：找 200 mil 内的 GND 过孔数，≥ 1（USB/PCIe 对 ≥ 2 并两侧对称）；每对差分线的过孔数相等，沿线位置差 ≤ 1 mm；不满足则报错

**来源**
- [SPRAAR7J High-Speed Interface Layout Guidelines（§2.4 Stitching Vias 200 mils；§3.9 Equalize Via Count）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, §2.4, §3.9
- [AN10373 PCI Express PHY PCB Layout Guideline（§2.1：每对 1–3 个缝合过孔；§2.4 过孔焊盘 ≤ 25 mil、孔 ≤ 14 mil）](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/powerquicc/2284/2/philips_PCIe_pcb_routing_guide.pdf) — NXP (Philips Semiconductors), app_note, §2.1, §2.4
- [ESP32-C3 Hardware Design Guidelines（§1.4.8 USB：每个过渡点加一对地回流孔）](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/esp-hardware-design-guidelines-en-master-esp32c3.pdf) — Espressif Systems, vendor_guide, §1.4.8
- [High-Speed Layout Guidelines (SCAA082A)（§2.5：信号过孔周围加地孔形成同轴结构）](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.5

<a id="HSD-RTE-007"></a>
#### HSD-RTE-007 · 控制过孔残桩 < 15 mil，反焊盘加大，通孔连接器从底层进线
`should` · 可信度 `high` · 适用: usb3, pcie, sata, hdmi, multilayer

**规则** 高速信号过孔的残桩（stub）长度 < 15 mil，超过的必须背钻；高速过孔的反焊盘直径尽量大（TI 取 30 mil 即有明显收益），各层（含布线层和平面层）都要满足，且不留非功能焊盘；差分线上不留分支 stub；通孔式连接器（如 USB-A）高速线接在底层，使连接器引脚成为信号路径而不是残桩；表贴连接器（如 Micro-B）接在顶层，免去过孔。

**依据** 过孔残桩是开路的四分之一波长谐振器，使插入损耗在其谐振频点附近陡增；反焊盘减小过孔的对地电容。

| 参数 | 判据 | 备注 |
|---|---|---|
| `via_stub_length` | < 15 mil | 更长则背钻 |
| `via_antipad_diameter` | >= 30 mil | TI：30 mil 有显著收益而实施难度不大 |
| `trace_stubs_on_pair` | == 0 pcs | SPRAAR7J 附录 A：Number of stubs allowed on any differential pair trace = 0 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) + 叠层高度表 — 对每个高速信号过孔：stub 长度 = 过孔贯穿端到最后一层被使用层之间的介质与铜厚之和，要求 < 15 mil（0.381 mm）；检查过孔在每个平面层的反焊盘直径 ≥ 30 mil；通孔连接器的高速引脚是否在底层引出

**来源分歧** SPRABI1D 说标准速率的 DDR3 不要求背钻，可用盲/埋/微孔改善；SPRAAR7J 对 > 15 mil 的残桩一律要求背钻（面向 Gb/s 串行链路）。取舍：多 Gb/s 串行链路按 15 mil；DDR3 随速率与 SoC 厂商要求，低速率可放宽。

**来源**
- [SPRAAR7J High-Speed Interface Layout Guidelines（§3.5, §3.6, §3.7, §3.8）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, §3.5-3.8
- [SLLA414A High-Speed Layout Guidelines for Signal Conditioners and USB Hubs（§4.5-4.8 Trace Stubs）](https://www.ti.com/lit/pdf/slla414) — Texas Instruments, app_note, §4.4-4.8
- [High-Speed Layout Guidelines (SCAA082A)（§2.5：过孔 stub 在 1/4 波长处呈短路，需背钻或用盲/埋孔）](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.5

<a id="HSD-RTE-008"></a>
#### HSD-RTE-008 · 限制每条高速线的过孔数，两线保持一致
`should` · 可信度 `high` · 适用: usb2, usb3, pcie, hdmi, ethernet, ddr3, mipi_csi

**规则** 每条高速线的过孔数不超过接口限值：USB2 每线 ≤ 4 个；USB3 每线 ≤ 2 个；PCIe/SATA 在 TI 老 SoC 上为 0（AM65xx/AM64x 为 ≤ 2）；HDMI TMDS 0 个；MIPI CSI ≤ 2 个；NXP PCIe 指南为 TX 对 ≤ 4 个过孔对、RX 对 ≤ 2 个过孔对；Microchip 以太网每线 ≤ 2 个；DDR3 数据线每网 ≤ 2 个且字节通道内一致，数据组不允许中途过孔。其中每个过孔对 PCIe 约占去 0.25 dB 损耗。

**依据** 过孔引入电感/电容不连续并占用链路损耗预算；TI 估算每个过孔使 PCIe 最大走线长度减少约 2 inch。

| 参数 | 判据 | 备注 |
|---|---|---|
| `usb2_vias_per_trace` | <= 4 pcs | TI SoC 表 |
| `usb3_vias_per_trace` | <= 2 pcs | TI SoC 表；AM335x/KeyStone PCIe/SATA 为 0，AM65xx/AM64x 的 PCIe/SGMII 为 2 |
| `ethernet_vias_per_diff_trace` | <= 2 pcs | Microchip AN2054 'reasonable budget' |
| `ddr3_vias_per_data_net` | <= 2 pcs | SPRABI1D；同字节通道内数量一致 |
| `pcie_loss_per_via_pair` | == 0.25 dB | NXP AN10373：某些极端情况下 |

**验证**
- `drc`（full）· kicad-cli pcb drc（.kicad_dru） — 为各接口网络类写 (constraint via_count (max N))，N 取 parameters；DRC 无 'Too many or too few vias on a connection'

**来源分歧** 不同 SoC 的指南给的上限不同（0、2、4），属器件差异；以所用器件为准，缺省取更严者。

**来源**
- [SPRAAR7J High-Speed Interface Layout Guidelines（附录 A：各 SoC 的 vias allowed）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, Appendix A
- [AN10373 PCI Express PHY PCB Layout Guideline（§2.4）](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/powerquicc/2284/2/philips_PCIe_pcb_routing_guide.pdf) — NXP (Philips Semiconductors), app_note, §2.4
- [SLLU149E TUSB73x0 Board Design and Layout Guidelines（§7：每个过孔约使最大长度减 2 inch）](https://www.ti.com/lit/pdf/sllu149) — Texas Instruments, app_note, §7
- [AN2054 Gigabit Ethernet Design Guide（Magnetics：每差分线过孔预算 2 个）](https://ww1.microchip.com/downloads/en/Appnotes/00002054A.pdf) — Microchip, app_note
- [SPRABI1D DDR3 Design Requirements for KeyStone Devices（§6.3.1.3, §6.3.1.6）](https://www.ti.com/lit/pdf/sprabi1) — Texas Instruments, app_note, §6.3.1.6
- [KiCad 9.0 PCB Editor — via_count](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc

<a id="HSD-RTE-009"></a>
#### HSD-RTE-009 · 高速线总长不超过接口与器件的限值
`should` · 可信度 `high` · 适用: usb2, usb3, pcie, ethernet, hdmi, mipi_csi

**规则** 按接口限制从芯片到连接器的总走线长度：TI SoC 的 USB2 典型 4 inch、最大 12 inch；USB3 3.5–5.5 inch；PCIe 4–5.5 inch（NXP：加载卡 4 inch、系统板 12 inch）；HDMI 4 inch；SGMII 7.5 inch；MIPI CSI 10 inch；以太网 MDI 单段 < 2 inch、整条 PHY 到 RJ45 < 4 inch；MII 走线 < 6 inch，GMII/RGMII 理想 ≤ 2 inch，超过时走内层。长度越短越好。

**依据** FR4 上每英寸都带来损耗、抖动（PCIe 每英寸约 0.35–0.5 dB、1–5 ps）和辐射，且占用接收器的损耗预算。

| 参数 | 判据 | 备注 |
|---|---|---|
| `usb2_total_trace_length_typ` | <= 4000 mil | TI SoC 表：典型 4000 mil，最大 12000 mil |
| `usb3_total_trace_length` | <= 3500 mil | AM335x/AM57xx 3500 mil；KeyStone/AM64x 5500 mil；AM65xx 4000 mil |
| `pcie_total_trace_length` | <= 4700 mil | AM57xx；KeyStone 5500，AM65xx 4000；NXP：加载卡 4 inch，系统板 12 inch |
| `ethernet_mdi_length` | < 2000 mil | TI SNLA387；Microchip 整条 < 4 inch |
| `mii_trace_length` | < 6000 mil | TI SNLA387；AN-1263 理想 ≤ 2 inch |
| `csi_total_trace_length` | <= 10 inch | TI AM62x/AM62Ax |

**验证**
- `drc`（full）· kicad-cli pcb drc（.kicad_dru） — 为各接口网络类写 (constraint length (max <限值>))，DRC 无 'Track length out of range'；注意 KiCad 长度调谐器默认把过孔的层间高度计入长度（Board Setup > Constraints），DRC 与 Net Inspector 的口径可能不同，见 HSD-VER-002

**来源分歧** 上限因 SoC 和代际而异（如 PCIe 4–5.5 inch，NXP 老文档系统板 12 inch）；以所用器件指南为准。

**来源**
- [SPRAAR7J High-Speed Interface Layout Guidelines（附录 A）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, Appendix A
- [SNLA387 Ethernet PHY PCB Design Layout Checklist（MDI < 2 inch，MII < 6 inch）](https://www.ti.com/lit/pdf/snla387) — Texas Instruments, app_note
- [AN2054 Gigabit Ethernet Design Guide（差分线总长 < 4 inch）](https://ww1.microchip.com/downloads/en/Appnotes/00002054A.pdf) — Microchip, app_note
- [AN10373 PCI Express PHY PCB Layout Guideline（§2.2.3）](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/powerquicc/2284/2/philips_PCIe_pcb_routing_guide.pdf) — NXP (Philips Semiconductors), app_note, §2.2.3
- [AN-1263 DP83865 Gig PHYTER V Design Guide（§7.4：GMII 理想 ≤ 2 inch，最长 < 6 inch 并走中间层）](https://www.ti.com/lit/an/snla056d/snla056d.pdf) — Texas Instruments, app_note, §7.4

<a id="HSD-RTE-010"></a>
#### HSD-RTE-010 · 高速线少拐弯，拐角不小于 135°
`should` · 可信度 `high` · 适用: usb, pcie, ethernet, lvds

**规则** 高速差分线尽量不引入拐弯；必须拐弯时拐角（相邻线段夹角）≥ 135°（即每处只转 45° 以内），拐弯两侧的线段长度 ≥ 1.5 倍线宽，拐弯处气隙（AN10373 图 4 的 A）≥ 20 mil；避免 90° 拐角，圆弧最好；不要使走线与元件引脚或其它走线成直角相交。

**依据** 拐角处线宽有效值改变，对地电容增加、特性阻抗变化，引起反射并增加辐射；拐弯也会引入共模噪声。

| 参数 | 判据 | 备注 |
|---|---|---|
| `bend_angle_min` | >= 135 deg | 线段夹角；TI SPRAAR7J/NXP AN10373 |
| `bend_flank_segment_length` | >= 1.5 x W | 拐弯两侧线段（AN10373 的 B、C 段） |
| `bend_air_gap` | >= 20 mil | NXP AN10373 §2.2.4 / 图 4 的气隙 A（原文未进一步定义，作者按图理解为拐弯处与邻近走线的间隙） |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 遍历高速网络的相邻线段，计算夹角（直线为 180°）：< 135° 报错；对夹角 < 180° 的拐点检查两侧线段长度 ≥ 1.5W
- `drc`（partial）· kicad-cli pcb drc（track_angle 约束） — 用 (constraint track_angle ...) 约束相邻线段夹角；该约束的角度约定需先用一块带 90°/135° 拐角的测试板确认后再使用

**来源**
- [SPRAAR7J High-Speed Interface Layout Guidelines（§3.11 Signal Bending）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, §3.11
- [AN10373 PCI Express PHY PCB Layout Guideline（§2.2.4 Bends）](https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/powerquicc/2284/2/philips_PCIe_pcb_routing_guide.pdf) — NXP (Philips Semiconductors), app_note, §2.2.4
- [SNLA302 High-Speed Layout Guidelines for Reducing EMI for LVDS SerDes Designs（§3）](https://www.ti.com/lit/an/snla302/snla302.pdf) — Texas Instruments, app_note, §3
- [High-Speed Layout Guidelines (SCAA082A)（§2.5：直角使电容增加、阻抗改变；至少两个 45° 或圆弧）](https://www.ti.com/lit/pdf/scaa082) — Texas Instruments, app_note, §2.5

<a id="HSD-RTE-011"></a>
#### HSD-RTE-011 · 高速差分线不放测试点，远离晶振、开关电源和磁性器件
`should` · 可信度 `high` · 适用: usb, pcie, ethernet, lvds

**规则** 高速差分线上不放探针/测试点（TI SoC 表规定测试点数为 0）；差分线不要从晶体、振荡器、时钟发生器、开关电源、安装孔、磁性器件或使用/复制时钟的 IC 下方或近旁经过，不走板边；不在元件下方走差分线，不让 TX/RX 与其它走线交叉，除非在地平面的另一侧；BGA 出线后高速差分线要远离 SoC。

**依据** 测试点是未端接的 stub，且引入焊盘电容；时钟、开关噪声会耦合进差分线，反过来高速线也会辐射到这些器件上。

| 参数 | 判据 | 备注 |
|---|---|---|
| `test_points_on_hs_pair` | == 0 pcs | TI SoC 表；AN10373 允许对称串联且无 stub 的测试点，见 conflicts |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 列出高速网络上的测试点焊盘（TP 前缀或 testpoint 属性），数量应为 0；对晶体、振荡器、开关稳压器电感、磁件等器件的外框膨胀 N mm（项目设定）后与高速线相交则报错

**来源分歧** NXP AN10373 §2.4 允许测试点/探针焊盘「对称、串联、无 stub」放置，TI 一律为 0。取舍：用 TI 的 0；确需调试访问时用串联式（线穿过焊盘）的对称探针点并在评审中说明。

**来源**
- [SPRAAR7J High-Speed Interface Layout Guidelines（§3.2 High-Speed Differential Signal Rules；附录 A）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, §3.2
- [SNLA302 High-Speed Layout Guidelines for Reducing EMI for LVDS SerDes Designs（§3：不走板边）](https://www.ti.com/lit/an/snla302/snla302.pdf) — Texas Instruments, app_note, §3
- [AN18.6 SMSC Ethernet Physical Layer Layout Guidelines（§3.1 Isolation of TX/RX Traces）](https://ww1.microchip.com/downloads/en/AppNotes/en562748.pdf) — Microchip (SMSC), app_note, §3.1

<a id="HSD-RTE-014"></a>
#### HSD-RTE-014 · 2 层板上的 FS USB 差分线：短、等长、下方整面地
`should` · 可信度 `medium` · 适用: usb2_fs, two_layer_board, esp32c3, usb_c · 标签: cat-feeder

**规则** 在 2 层板上跑 FS USB（如 ESP32-C3 的 GPIO18/19 经 USB-C）时：D+/D− 紧耦合平行等长，尽量短；下方保持连续不间断的地铜（整面地），不被其它走线或过孔切割；按板厚用阻抗计算器算线宽/间距逼近 90 Ω 差分，算不到时在评审中记录偏差；换层处就近放一对地回流过孔；两侧用地铜包围。Type-C 的 A6/B6、A7/B7 各自并接后再接芯片时，汇合点靠近连接器。

**依据** FS USB 对阻抗偏差比较宽容，但仍需要可控的传输线环境以减少反射和 EMI；2 层板没有内层参考面，必须靠底层整面地提供回流。

| 参数 | 判据 | 备注 |
|---|---|---|
| `usb_fs_diff_impedance_target` | == 90 ohm | Espressif：90 Ω ±10%；RP2040 文档：接近 USB 规范的 90 Ω 即可，FS 比较宽容但「不一定合规」 |
| `rp2040_example_geometry` | qualitative mm | 1 mm 厚板：线宽 0.8 mm、间隙 0.15 mm 约 90 Ω；板更厚需重算，文档称可能无法实现 |

**验证**
- `tline_calc`（partial）· KiCad PCB Calculator 或板厂计算器（微带/耦合微带，板厚、εr 取板厂值） — 对 2 层板厚（如 1.0/1.6 mm）和可用最小间距算差分阻抗，记录与 90 Ω 的偏差；偏差超过 ±10% 时在评审单上标明
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — D+/D− 总长、长度差（≤ 50 mil 作内部目标）、下方（对面层）GND 铜覆盖率 = 100%、同层 GND 包围；输出违规段

**来源分歧** Espressif 要求 90 Ω ±10%，RP2040 文档说 FS 较宽容、板厚不合适时可「不管它」并接受不合规。取舍：尽力逼近 90 Ω 并记录偏差；USB-IF 认证级别的产品另按 HS/FS 一致性要求。A6/B6 汇合点靠近连接器是作者出于减小 stub 的推理，来源未给数值。

**来源**
- [Hardware design with RP2040（§2.4.1：1 mm 板 0.8 mm 线宽/0.15 mm 间隙 ≈ 90 Ω；整面地；板更厚时无法同时满足）](https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf) — Raspberry Pi, vendor_guide
- [ESP32-C3 Hardware Design Guidelines（§1.4.8 USB）](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/esp-hardware-design-guidelines-en-master-esp32c3.pdf) — Espressif Systems, vendor_guide, §1.4.8
- [ESP-IoT-Solution USB Type-C Hardware Design Guide（A6/B6→D+，A7/B7→D−）](https://docs.espressif.com/projects/esp-iot-solution/en/latest/usb/usb_overview/usb_typec_hardware_guide.html) — Espressif Systems, vendor_guide

## 平面与铺铜（plane_pour）

<a id="HSD-PLN-001"></a>
#### HSD-PLN-001 · 按目标阻抗法设计高速 IC 的电源分配网络
`should` · 可信度 `high` · 适用: ddr, soc, fpga, phy

**规则** 对高速 IC 的每个电源轨，用 Z_target = (电源电压 × 允许纹波%) / (0.5 × I_max) 作为目标阻抗，使 PDN 阻抗从 DC 到 F_MAX（再增加合理数量电容也无法使阻抗低于目标的频点）都低于它：稳压器覆盖约 1 MHz 以下，板级陶瓷电容（1 nF–100 nF，ESL 0.5–1 nH）覆盖约 1–70 MHz，电源/地平面对电容覆盖更高频率；电源与地平面对紧耦合、介质薄；高优先级电源放在叠层上半部；储能电容靠近电源入口。

**依据** 电源轨噪声 = 瞬态电流 × PDN 阻抗；稳压器在高频呈电感性，去耦网络必须在其失效后接棒。

| 参数 | 判据 | 备注 |
|---|---|---|
| `z_target_formula` | qualitative ohm | Z_TARGET = Voltage Rail × %Ripple / (0.5 × I_Max) |
| `vrm_effective_frequency` | <= 1 MHz | PMIC/SMPS 约在 500 kHz–1 MHz 以下响应；之后呈电感性 |
| `mid_frequency_cap_range` | 1 … 100 nF | 中频电容 1 nF–100 nF，ESR 10–100 mΩ，ESL 0.5–1 nH，覆盖约 1–70 MHz（取决于 ESL/ESR） |
| `loop_inductance_measure_frequency` | 50 … 70 MHz | Leff = Im(Z)/(2πf)，取 Z 参数平坦区 |

**验证**
- `pi_sim`（partial）· PDN 阻抗仿真（见 HSD-VER-005） — 扫频 DC–F_MAX，|Z_PDN(f)| < Z_target
- `review`（manual）· 叠层与电容清单评审 — 每个高速电源轨有 Z_target 计算记录；电源/地面对介质厚度、电容数量与回路电感满足仿真结论

**来源分歧** I_transient 的取法：TI 用 0.5×I_max；其它厂商（如 Intel、Microsemi）也有用 50% 的，也有用实测或仿真的 I_max − I_min。取舍：有仿真/实测瞬态电流时用实值，否则用 TI 的 50% 规则。

**来源**
- [SPRAC76H Sitara Processor Power Distribution Networks: Implementation and Analysis（§5 Dynamic Analysis of PCB PDN，式 3；§6 Checklist for PDN）](https://www.ti.com/lit/an/sprac76g/sprac76g.pdf) — Texas Instruments, app_note, §5, §6

<a id="HSD-PLN-002"></a>
#### HSD-PLN-002 · 以太网磁件下无铜，机壳地与数字地隔离
`should` · 可信度 `high` · 适用: ethernet, discrete_magnetics

**规则** 磁件下方所有层不放金属（集成磁件的 RJ45 下除外）；从磁件中部到 RJ45 之间清除所有平面和非以太网走线（≥ 0.250 inch）形成高压隔离带，该区域的 LED、电容、二极管只能参考机壳地；机壳（earth）地与数字地之间在所有层保持 ≥ 20 mil 隔离，用一个电容并联 ≥ 1 MΩ 电阻连接。

**依据** 隔离带是 IEEE 802.3 隔离耐压和 ESD 的屏障；磁件下方有铜会形成耦合电容旁路隔离、或把共模噪声耦合到板内。

| 参数 | 判据 | 备注 |
|---|---|---|
| `earth_ground_keepout` | >= 20 mil | TI SNLA387：所有层；例外：电容 + ≥ 1 MΩ 电阻连接两种地 |
| `hv_barrier_clear_width` | >= 0.25 inch | Microchip AN2054：从磁件中部到 RJ45 的清空区 |
| `earth_to_digital_ground_resistor` | >= 1 Mohm | TI SNLA387 推荐 |

**验证**
- `geometry_script`（full）· pcbnew (KiCad bundled Python) — 取磁件外框（及到 RJ45 的区域），检查所有铜层在该区域内无非机壳地铜、无非以太网网络的走线/过孔；检查机壳地铜与数字地铜的最小间距 ≥ 20 mil

**来源分歧** MDI 走线下的地平面：TI SNLA387 要求走线层下方连续地，仅在器件处挖空；SMSC AN18.6 称一般情况下 TX/RX 线对、磁件、RJ45 下方都不应有地平面（有共模电容时地平面不得越过电容）。二者对「线对下是否铺地」相反；取舍：磁件与磁件到 RJ45 之间无铜（一致处），PHY 到磁件的线对段按 TI 的连续地走线；如需 SMSC 式无地方案，应以该 PHY 参考设计为准并在评审中说明。

**来源**
- [SNLA387 Ethernet PHY PCB Design Layout Checklist（Magnetic Isolation；Earth Ground Isolation）](https://www.ti.com/lit/pdf/snla387) — Texas Instruments, app_note
- [AN2054 Gigabit Ethernet Design Guide（ESD Considerations；High-Voltage Barrier）](https://ww1.microchip.com/downloads/en/Appnotes/00002054A.pdf) — Microchip, app_note
- [AN18.6 SMSC Ethernet Physical Layer Layout Guidelines（§2.4）](https://ww1.microchip.com/downloads/en/AppNotes/en562748.pdf) — Microchip (SMSC), app_note, §2.4

<a id="HSD-PLN-003"></a>
#### HSD-PLN-003 · 高速线两侧铺地时保持 3–5 倍线宽间隙，缝合需验证
`consider` · 可信度 `medium` · 适用: usb, ethernet, lvds, copper_pour · 标签: cat-feeder

**规则** 与高速线同层的地铜离线边缘 ≥ 3W，优选 5W（避免对地电容拉低阻抗）；USB 等线两侧可用地铜包围（Espressif）；用缝合过孔连接地铜时先用仿真/计算确认没有形成谐振腔；避免在差分对之间插入地线作为串扰对策，除非是两端接地的带状线。

**依据** 太近的同层地铜会增加线对地电容，使阻抗偏低；缝合过孔把地铜与参考面连接可抑制辐射，但间距不当会在耦合线之间形成开放谐振腔而加重串扰。

| 参数 | 判据 | 备注 |
|---|---|---|
| `same_layer_ground_clearance_min` | >= 3 x W | SNLA387：与 MDI 线同层的地至少 3w，优选 5w |
| `same_layer_ground_clearance_preferred` | >= 5 x W | SNLA387 优选值 |

**验证**
- `drc`（full）· kicad-cli pcb drc（.kicad_dru） — 为高速差分网络类与铜区（zone）之间写 clearance 规则，min = 3W（W 取该类线宽；条件用 hasNetclass() 选线，zone 对象的类型条件按 KiCad 文档的 Type 属性写，先在测试板上验证规则生效）；DRC 无违规
- `em_sim`（partial）· 2.5D/3D 场求解（openEMS 等）或阻抗计算器的共面地模型 — 加入地铜后重新计算差分阻抗，仍在目标内；有缝合过孔时扫描 S21/串扰看是否出现谐振峰

**来源分歧** TI SNLA302 与 Espressif 建议在差分线周围铺地/包地，Altium 指出缝合地铜可能形成谐振腔，且只有两端接地的带状线保护线才有效。取舍：铺地可以，但保持 ≥ 3W 间隙，并把「包地+缝合」作为需验证的措施而非默认做法。

**来源**
- [SNLA387 Ethernet PHY PCB Design Layout Checklist（MDI Traces：同层地平面 ≥ 3w，优选 5w）](https://www.ti.com/lit/pdf/snla387) — Texas Instruments, app_note
- [ESP32-C3 Hardware Design Guidelines（§1.4.8 USB：Surround the USB traces with ground copper）](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/esp-hardware-design-guidelines-en-master-esp32c3.pdf) — Espressif Systems, vendor_guide, §1.4.8
- [SNLA302 High-Speed Layout Guidelines for Reducing EMI for LVDS SerDes Designs（§2：对差分线周围均匀铺地）](https://www.ti.com/lit/an/snla302/snla302.pdf) — Texas Instruments, app_note, §2
- [Crosstalk Analysis, Reduction, and Elimination Techniques in PCB Design（缝合过孔可能形成谐振腔；仅带状线两端接地的保护线有效）](https://resources.altium.com/p/crosstalk-elimination-techniques-in-altium-designer) — Altium, vendor_guide

## 出图与制造（manufacturing）

<a id="HSD-MFG-001"></a>
#### HSD-MFG-001 · 下单时声明阻抗控制层、目标值、公差和叠层
`must` · 可信度 `medium` · 适用: jlcpcb, controlled_impedance, multilayer

**规则** 需要阻抗控制的板，下单时在板厂选项中打开阻抗控制，选定板厂叠层（如 JLCPCB 的 JLC7628/JLC3313），在制板说明里写明受控线所在层、目标阻抗（单端/差分）和公差；板厂标准公差 ±10%，±5% 需特殊申请（可能额外验证、需要受控介质和精确叠层），不要把公差写得比这更严；JLCPCB 的阻抗控制列于 4 层及以上的多层板，双层板不提供。布线宽度按板厂计算器给出的值，不自行改动。

**依据** 没有声明的线宽板厂不会按阻抗调整；叠层、玻纤布型和铜厚随板厂批次变化，只有锁定叠层并写明受控层，计算值才有意义。

| 参数 | 判据 | 备注 |
|---|---|---|
| `impedance_tolerance_standard` | <= 10 % | JLCPCB 标准；±5% 需特殊申请，可能多出验证并受叠层限制 |
| `min_trace_space_multilayer_1oz` | >= 0.09 mm | JLCPCB 多层 1 oz 最小线宽/线距 0.09/0.09 mm（3.5/3.5 mil）；线宽公差 ±20% |

**验证**
- `review`（manual）· 制板说明/下单单评审 — 说明中含：受控层、目标 Z（单端/差分）、公差（≤ 板厂标准能力）、所选叠层名称；下单页面阻抗控制选项为 Yes；线宽与板厂计算器输出一致
- `bom_check`（partial）· 脚本比对 Gerber/板文件与说明 — 读板文件中受控网络类的线宽/间距，与说明里的计算值逐类对比，差异 > 0.01 mm 报告

**来源分歧** 板厂文档未明确下单页面里如何勾选阻抗控制、费用与工期（抓取页面未列出），实际流程以下单页为准。

**来源**
- [JLCPCB PCB Manufacturing & Assembly Capabilities（Impedance control：±10% 标准，±5% 特殊申请；多层 3.5/3.5 mil 线宽线距；线宽公差 ±20%）](https://jlcpcb.com/capabilities/pcb-capabilities) — JLCPCB, vendor_guide
- [JLCPCB 多层高精度阻抗板叠层页](https://cart.jlcpcb.com/client/template/placeOrder/impedance.html) — JLCPCB, vendor_guide

## 签核验证（verification）

<a id="HSD-VER-002"></a>
#### HSD-VER-002 · 出板前用自定义规则跑 DRC，并核对长度口径
`must` · 可信度 `high` · 适用: kicad, drc

**规则** 出图前用含 HSD-NET-003 全部高速规则的 .kicad_dru 跑 kicad-cli DRC，结果中长度、偏斜、差分间距、未耦合长度、过孔数五类违规都必须为 0；同时核对长度口径：KiCad 长度调谐器（计入过孔层间高度）与 Net Inspector（仅铜段长度求和）算出的长度不同，叠层高度须配置准确，用同一口径做最终判定。

**依据** 默认 DRC 不含这些约束，规则文件没有语法错误才会生效；长度口径不一致会使「已匹配」的网络在另一工具里显示失配。

| 参数 | 判据 | 备注 |
|---|---|---|
| `hs_rule_violations_allowed` | == 0 pcs | 五类高速违规均为 0 |

**验证**
- `drc`（full）· kicad-cli pcb drc --format json --output out.json board.kicad_pcb — out.json 中 type 为 skew / length / diff_pair_gap / diff_pair_uncoupled / via_count 的违规数量 = 0；规则文件语法检查（Board Setup 的 Check rule syntax）通过
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 用脚本按线段求和并加上过孔层间高度（叠层表）重新计算匹配组长度，与 DRC 报告差异 > 1 mil 时逐网络检查是否有残余分支 stub

**来源**
- [KiCad 9.0 PCB Editor — Custom design rules；Length tuning pitfalls and tips；DRC 违规说明](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) — KiCad, tool_doc, Length tuning；Custom design rules；DRC

<a id="HSD-VER-001"></a>
#### HSD-VER-001 · 布线后按实际线宽间距逐段复算受控线阻抗
`should` · 可信度 `medium` · 适用: controlled_impedance, field_solver

**规则** 布线完成后读出各高速网络每一段实际的线宽、对内间距和所在层，用场求解器/计算器复算阻抗，所有受控段必须落在 HSD-ARC-002 的范围内；BGA 出线后线宽保持不变；颈缩段（引脚入口、过孔附近）单独核查长度和偏差。

**依据** 设计时按标称线宽算出的阻抗，被引脚出线颈缩、蛇形、换层等局部改动抵消；2D 计算器模型有适用范围，需与板厂工具交叉验证。

| 参数 | 判据 | 备注 |
|---|---|---|
| `calculator_cross_check_tolerance` | <= 5 % | 作者设定的工具互校阈值，来源未给数值 |

**验证**
- `geometry_script`（partial）· pcbnew (KiCad bundled Python) — 遍历高速网络的线段，输出（层、线宽、对内间距、长度）；对线宽与规范值不同的线段累计长度，颈缩段总长占网络长度比例报告；线宽变化点处对内间距变化是否同步
- `tline_calc`（partial）· KiCad PCB Calculator（TransLine 的耦合微带模型）+ 板厂阻抗计算器 — 对每个（层, 线宽, 间距）组合算 Zdiff/Z0，两个工具结果均在目标范围内，且两者互差 ≤ 5%

**来源分歧** KiCad 计算器文档未列出各线型的输入/输出，且其公式是解析近似（Atwater、Kirschning & Jansen 引用）而非全波场求解；对密耦合、有阻焊的外层线与板厂实测可能有偏差。取舍：以板厂计算器为准，KiCad 计算器作交叉校验。

**来源**
- [SPRAAR7J High-Speed Interface Layout Guidelines（§3.2：BGA 出线后保持线宽不变）](https://www.ti.com/lit/pdf/spraar7) — Texas Instruments, app_note, §3.2
- [KiCad PCB Calculator（TransLine：耦合微带、带状线等；模型基于 Transcalc，引用 Atwater 1989、Kirschning & Jansen 1984）](https://docs.kicad.org/9.0/en/pcb_calculator/pcb_calculator.html) — KiCad, tool_doc
- [JLCPCB 多层高精度阻抗板叠层页](https://cart.jlcpcb.com/client/template/placeOrder/impedance.html) — JLCPCB, vendor_guide
- [SLLA414A High-Speed Layout Guidelines for Signal Conditioners and USB Hubs（§3.1：板厂常有自己偏好的计算工具）](https://www.ti.com/lit/pdf/slla414) — Texas Instruments, app_note, §3.1

<a id="HSD-VER-003"></a>
#### HSD-VER-003 · 用传输线模型仿真端接，并联合 IBIS 做高速总线 SI 仿真
`should` · 可信度 `high` · 适用: ddr, high_speed_bus, ngspice, ibis

**规则** 单端点对点线的端接值先用 ngspice 的传输线元件（T、O/LTRA、Y/TXL、P/CPL）做瞬态仿真确定；DDR3 等 > 300 MHz 的接口必须用 SoC 与 SDRAM 厂商的 IBIS/SPICE 模型、含完整叠层做 SI 仿真，验证 setup/hold 与电压裕量。2D 板级仿真假设理想回流面，回流路径必须另靠人工检查。

**依据** 反射、串扰、非单调沿在高速接口里直接吞掉时序裕量；仿真是在改板前发现拓扑与端接问题的唯一手段。

| 参数 | 判据 | 备注 |
|---|---|---|
| `must_simulate_above_frequency` | > 300 MHz | TI：所有高性能接口，特别是 300 MHz 以上，都应建模（含完整叠层、SoC 与 SDRAM） |
| `ngspice_cpl_max_lines` | <= 8 lines | ngspice CPL 最多 8 根耦合线，且无趋肤效应/频变介质损耗 |

**验证**
- `spice`（partial）· ngspice：T（无损）、O + .model ltra（有损）、Y + .model txl、P + .model cpl（耦合线，无频变损耗） — 驱动器内阻 + 传输线 + 负载电容，扫 Rs；接收端过冲/下冲在手册范围内，单调性满足（无非单调沿）
- `si_sim`（partial）· IBIS 模型（厂商提供；TI 提供 IBIS 5.0）+ 支持 IBIS 与叠层输入的板级 SI 仿真工具 — 读/写方向各一组：眼高、眼宽、setup/hold 裕量、串扰；与时序预算表（TN-41-13 Table 6 类）对账
- `review`（manual）· 人工检查回流路径 — 目视检查每个换层点和分割处的回流路径（2D 板级仿真器假设相邻平面就是理想回流面）

**来源分歧** TI 说明 HSPICE 昂贵、IBIS 因高频限制曾被回避，但 TI 现提供 IBIS 5.0 模型；Micron 强调 2D 仿真器忽略真实回流路径。二者不冲突：IBIS 做拓扑/终端比较，回流路径与连接器处需 3D 或人工检查。

**来源**
- [ngspice User's Manual — Chapter 6 Transmission Lines](https://ngspice.sourceforge.io/docs/ngspice-manual.pdf) — ngspice, tool_doc, Chapter 6
- [SPRABI1D DDR3 Design Requirements for KeyStone Devices（§7 Simulation and Modeling）](https://www.ti.com/lit/pdf/sprabi1) — Texas Instruments, app_note, §7
- [TN-41-13 DDR3 Point-to-Point Design Support（Return Path；Timing Budgets；Terminating Point-to-Point Systems）](https://perso.esiee.fr/~poulichp/CEM/Signal_Integrity/tn4113_ddr3_point_to_point_design.pdf) — Micron Technology（ESIEE 镜像）, app_note

<a id="HSD-VER-005"></a>
#### HSD-VER-005 · 签核前对高速 IC 电源轨做 PDN 阻抗仿真
`should` · 可信度 `medium` · 适用: pdn, ddr, soc

**规则** 在制板前对每个高速电源轨用 PDN 工具/板级 PI 仿真器扫描 DC 到 F_MAX 的阻抗，所有频点 |Z_PDN| < Z_target（HSD-PLN-001）；从去耦电容焊盘处的 Z 参数用 Leff = Im(Z)/(2πf) 在 50–70 MHz 的平坦区提取回路电感，核对不超过器件文档的上限。

**依据** 厂商给的电容数量和值只是基线，TI 明确要求所有设计在制板前仿真；实际回路电感由叠层、过孔和布局决定，不能凭经验判定。

| 参数 | 判据 | 备注 |
|---|---|---|
| `leff_extraction_frequency` | 50 … 70 MHz | Z 参数平坦区，TI SPRAC76H 式 4 |
| `example_decap_loop_inductance_limit` | <= 2.5 nH | TI AM570x/AM571x 示例表中 DDR 与核心电源的 Dec Cap Max LL 为 2–2.5 nH；其它器件值不同，以其文档为准 |

**验证**
- `pi_sim`（partial）· 板级 PI/PDN 阻抗仿真工具，或 SPICE 里的 RLC 网络模型 — 导入叠层、平面形状、电容位置与模型；扫频，|Z| 曲线低于 Z_target 直到 F_MAX；提取各电容的 Leff

**来源**
- [SPRAC76H Sitara Processor Power Distribution Networks: Implementation and Analysis（§5, §7 注：电容数量不能代替仿真，Leff 提取方法）](https://www.ti.com/lit/an/sprac76g/sprac76g.pdf) — Texas Instruments, app_note, §5, §7

<a id="HSD-VER-004"></a>
#### HSD-VER-004 · 用 TDR/VNA 实测阻抗与 S 参数，脚本化后处理
`consider` · 可信度 `medium` · 适用: tdr, vna, scikit_rf

**规则** 首板上对受控阻抗线用 TDR 实测阻抗（尤其连接器、过孔、AC 电容、ESD 焊盘处的不连续）并与目标范围比较；多 Gb/s 链路用 VNA 测 S 参数，后处理（去嵌、差分/共模转换、时域响应、无源性检查）用 scikit-rf 脚本化，并保存结果。

**依据** 场求解器的假设（理想叠层、无粗糙度）与实板有差异；TDR 直接看到各处阻抗，VNA 给出插入损耗与回波损耗，能对照规范模板。

**验证**
- `bench`（manual）· TDR 示波器；VNA；探针或 SMA 转接 + 测试条 — TDR：沿线阻抗曲线在目标范围内，连接器/过孔处的偏离不超过接口规范的反射预算；VNA：回波损耗/插入损耗满足接口规范
- `em_sim`（partial）· scikit-rf（skrf.network、skrf.time、skrf.calibration.deembedding、Mixed Mode 示例） — 读 Touchstone，做混合模式转换、去嵌、阶跃响应；用 passivity()/reciprocity() 检查数据合理性；脚本输出阻抗与 S21 曲线并与目标比较

**来源分歧** scikit-rf 文档首页和 Network API 页可见 network、time、deembedding、vectorFitting 模块及 subnetwork/passivity/reciprocity 函数，但抓取内容未列出混合模式、时域函数的具体名称；使用前以所装版本的 API 为准。

**来源**
- [SNLA302 High-Speed Layout Guidelines for Reducing EMI for LVDS SerDes Designs（§3：跨连接器处阻抗要匹配，用 TDR 验证）](https://www.ti.com/lit/an/snla302/snla302.pdf) — Texas Instruments, app_note, §3
- [scikit-rf documentation（skrf.network、skrf.time、skrf.calibration.deembedding、skrf.vectorFitting；subnetwork、passivity、reciprocity）](https://scikit-rf.readthedocs.io/en/latest/) — scikit-rf, tool_doc
- IPC-TM-650 Method 2.5.5.7 Characteristic Impedance and Time Delay of Lines on Printed Boards by TDR（IPC-TM-650 §2.5.5.7（标准正文未读，仅按方法名引用）） — IPC, standard

